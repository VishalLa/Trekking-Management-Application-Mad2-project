from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import get_jwt_identity

from service.trekker_service import (
    TrekkerDashboard,
    TrekkerProfile,
    BookingService,
    Duplicate,
    NotFound,
    PaymentFailed
)

from auth.auth import role_required

trekker_bp = Blueprint("trekker_routes", __name__, url_prefix="/trekker")


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
            return jsonify({"message": "Profile updated successfully!"}), 200

        except ValueError as e:
            return jsonify({"error": str(e)}), 404
        except Exception as e:
            print(f"Error updating profile: {e}")
            return jsonify({"error": "Failed to update profile"}), 500
        

@trekker_bp.route("/trek-list", methods=["GET"])
@role_required("TREKKER")
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
