from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import get_jwt_identity

from service.trekker_service import (
    TrekkerDashboard,
    TrekkerProfile,
    BookingService,
    TrekAssignedStaff,
    Duplicate,
    NotFound,
    PaymentFailed,
    PaymentCompleted
)

from auth.auth import role_required
from tasks.trekker_tasks import generate_booking_csv
from celery_app import app
from cache import cache

trekker_bp = Blueprint("trekker_routes", __name__)


@trekker_bp.route("/profile", methods=["GET", "PUT"])
@role_required("TREKKER")
def handle_trekker_profile():
    current_user_id = get_jwt_identity()

    if request.method == "GET":
        try: 
            user_data = TrekkerProfile.get_trekker_data(user_id=current_user_id)
            return jsonify(user_data), 200
        
        except ValueError as e:
            return jsonify({"error": {e}}), 404
        except Exception as e:
            return jsonify({"error": "Internal Server Error"}), 500
        
    if request.method == "PUT":
        try:
            update_data = request.get_json()
            if not update_data:
                return jsonify({"error": "No update data provided"}), 400
            
            TrekkerProfile.update_profile(user_id=current_user_id, profile_data=update_data)
            cache.delete('all_trekker')
            return jsonify({"message": "Profile updated successfully!"}), 200

        except ValueError as e:
            return jsonify({"error": str(e)}), 404
        except Exception as e:
            print(f"Error updating profile: {e}")
            return jsonify({"error": "Failed to update profile"}), 500
        

@trekker_bp.route("/trek-list", methods=["GET"])
@role_required("TREKKER")
@cache.cached(timeout=600, key_prefix='all_available_treks')
def get_trek_list():
    try:
        trek_data = TrekkerDashboard.get_open_and_approved_trek()
        return jsonify(trek_data), 200
    
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500
    

@trekker_bp.route("/search-trek", methods=["GET"])
@role_required("TREKKER")
def search_trek():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({"error": "Please provide a search term using the '?q=' parameter."}), 400
    
    try:
        results = TrekkerDashboard.search_trek(query=query)

        if not any(results.values()):
            return jsonify({"message": "No results found."}), 404
                    
        return jsonify(results), 200
    
    except Exception as e:
        return jsonify({"error": "An error occurred while searching."}), 500  


@trekker_bp.route("/booked-trek/<string:user_id>", methods=["GET"])
@role_required("TREKKER")
def get_booked_trek(user_id: str):
    try:
        booked_trek = TrekkerDashboard.get_booked_treks(user_id=user_id)
        return jsonify(booked_trek), 200
    
    except Exception as e:
        return jsonify({"error": "Internal Server Error"}), 500
    

@trekker_bp.route("/<string:user_id>/book-trek/<string:trek_id>", methods=["POST"])
@role_required("TREKKER")
def book_trek(user_id: str, trek_id: str):
    data = request.get_json()

    if not data or "number_of_booking" not in data:
        return jsonify({"error": "Missing 'number_of_booking' in request."}), 400
    
    try:
        number_of_booking = int(data["number_of_booking"])
        if number_of_booking <= 0:
            return jsonify({"error": "You must book at least 1 ticket."}), 400
        
        booking = BookingService.book_trek(
            user_id=user_id, 
            trek_id=trek_id, 
            number_of_booking=number_of_booking
        )

        return jsonify({
            "message": "Trek successfully booked! Pending payment.",
            "booking_id": booking.booking_id
        }), 201
    
    except Duplicate as e:
        return jsonify({"error": f"{e}"}), 409
    except NotFound as e:
        return jsonify({"error": f"{e}"}), 404
    except ValueError as e:
        return jsonify({"error": f"{e}"}), 400
    except Exception as e:
        return jsonify({"error": f"Internal Server Error"}), 500
    

@trekker_bp.route("/<string:user_id>/complete-booking/<string:booking_id>", methods=["POST"])
@role_required("TREKKER")
def complete_booking(user_id: str, booking_id: str):
    try: 
        card_data = request.get_json()
        if not card_data:
            return jsonify({"error": "No update data provided"}), 400

        BookingService.complete_booking(
            user_id=user_id, 
            booking_id=booking_id,
            card_data=card_data
        )

        return jsonify({
            "message": "Booking complete",
            "booking_id": booking_id
        }), 200
    
    except NotFound as e:
        return jsonify({"error": f"{e}"}), 404
    except PaymentCompleted as e:
        return jsonify({"error": f"{e}"}), 409
    except PaymentFailed as e:
        return jsonify({"error": str(e)}), 402
    except Exception as e:
        return jsonify({"error": "Internal Server Error"}), 500


@trekker_bp.route("/<string:user_id>/cancel-booking/<string:booking_id>", methods=["POST"])
@role_required("TREKKER")
def cancel_booking(user_id: str, booking_id: str):
    try: 
        BookingService.cancel_booking(user_id=user_id, booking_id=booking_id)
        return jsonify({"message": "booking canceled"}), 200
    
    except NotFound as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Internal Server Error"}), 500
    

@trekker_bp.route("/trigger/download-bookings/<string:user_id>", methods=["POST"])
@role_required("TREKKER")
def trigger_export(user_id: str):
    task = generate_booking_csv.delay(user_id=user_id)
    return jsonify({"task_id": task.id}), 202


@trekker_bp.route("/download-bookings/<task_id>", methods=["GET"])
@role_required("TREKKER")
def downlaod_bookings(task_id):
    task_result = app.AsyncResult(task_id)

    if task_result.state == 'PENDING' or task_result.state == 'STARTED':
        return jsonify({"status": "Processing..."}), 202
    elif task_result.state == 'SUCCESS': 
        csv_data = task_result.result

        if csv_data is None:
             return jsonify({"status": "Finalizing..."}), 202
        
        output = Response(csv_data, mimetype="text/csv")
        output.headers["Content-Disposition"] = "attachment; filename=Booking_Data.csv"

        return output
    
    else:
        error_message = str(task_result.info)
        print(f"CELERY TASK FAILED: {error_message}") 
        
        return jsonify({"error": f"Background task failed: {error_message}"}), 500

    

@trekker_bp.route("/assigned-staff/<string:trek_id>", methods=["GET"])
@role_required("TREKKER")
def trek_specific_staff(trek_id: str):
    try: 
        assigned_staff = TrekAssignedStaff.get_trek_specific_staff(trek_id=trek_id)

        return jsonify(assigned_staff), 200
    
    except NotFound as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        print(e)
        return jsonify({"error": "Internal Server Error"}), 500
