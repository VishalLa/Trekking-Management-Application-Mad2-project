from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity

from service.staff_service import (
    StaffDashboardService,
    StaffProfileService
)
from service.trek_service import (
    ManageTrek, 
    BookingService
)

from auth.auth import role_required

staff_bp = Blueprint("staff_route", __name__, url_prefix="/staff")


@staff_bp.route("/assigned-trek-list/<string:user_id>", methods=["GET"])
@role_required("STAFF")
def get_assigned_trek(user_id: str):
    try: 
        trek_list = StaffDashboardService.get_assigned_treks(user_id=user_id)

        format_trek_list = [
            {
                "trek_id": trek.trek_id,
                "trek_name": trek.trek_name,
                "location": trek.location,
                "duration": trek.duration,
                "available_slots": trek.available_slots,
                "status": trek.status.name,
                "difficulty": trek.difficulty.name,
                "start_date": trek.start_date,
                "end_date": trek.end_date,
            } for trek in trek_list
        ]

        return jsonify(format_trek_list), 200

    except ValueError as e:
        return jsonify({"error": f"{e}"}), 404
    except Exception as e:
        return jsonify({"error": f"Internal Server error"}), 500
    

@staff_bp.route("/trek/<string:trek_id>/<string:status>", methods=["PUT"])
@role_required("STAFF")
def change_status(trek_id, status):
    try:
        ManageTrek.change_status(trek_id=trek_id, status=status)

        return jsonify({
            "message": f"trek with: {trek_id} change status: {status}"
        }), 200
    
    except ValueError as e: 
        return jsonify({"error": str(e)}), 404
    except Exception as e: 
        return jsonify({"error": "Internal Server Error"}), 500
    

@staff_bp.route("/trek/<string:trek_id>/slots/<int:slots>", methods=["PUT"])
@role_required("STAFF")
def update_trek_slots(trek_id: str, slots: int):
    try: 
        StaffDashboardService.update_trek_slots(trek_id=trek_id, slots=int(slots))

        return jsonify({
            "message": f"trek with: {trek_id} change slots: {int(slots)}"
        }), 200

    except ValueError as e: 
        return jsonify({"error": str(e)}), 404
    except Exception as e: 
        return jsonify({"error": "Internal Server Error"}), 500
    

@staff_bp.route("/booking/<string:trek_id>", methods=["GET"])
@role_required("STAFF")
def get_trek_specific_booking(trek_id: str):
    try:
        booking_list = BookingService.get_trek_specific_booking(trek_id=trek_id)

        formated_booking_data = [
            {
                "booking_id": booking.booking_id,
                "user_name": f"{booking.user.first_name} {booking.user.last_name}",
                "email": booking.user.email,
                "booking_date": booking.booking_date.strftime("%Y-%m-%d"), 
                "status": booking.status.value,
                "number_of_booking": booking.number_of_booking,
                "payment_status": booking.payment_status
            }
            for booking in booking_list
        ]

        return jsonify(formated_booking_data), 200

    except Exception as e:
        print(f"Booking Error: {e}")
        return jsonify({"error": f"An error occurred while fetching booking for trek: {trek_id}"}), 500


@staff_bp.route("/profile", methods=["GET", "PUT"])
@role_required("STAFF")
def handle_staff_profile():
    current_user_id = get_jwt_identity()

    if request.method == "GET":
        try: 
            profile_data = StaffProfileService.get_profile(current_user_id)
            return jsonify(profile_data), 200
        
        except ValueError as e: 
            return jsonify({"error": str(e)}), 404
        except Exception as e:
            return jsonify({"error": "Internal Server Error"}), 500
        

    if request.method == "PUT":
        try: 
            update_data = request.get_json()
            if not update_data:
                return jsonify({"error": "No update data provided"}), 400
                
            StaffProfileService.update_profile(current_user_id, update_data)
            return jsonify({"message": "Profile updated successfully!"}), 200
            
        except ValueError as e:
            return jsonify({"error": str(e)}), 404
        except Exception as e:
            print(f"Error updating profile: {e}")
            return jsonify({"error": "Failed to update profile"}), 500
