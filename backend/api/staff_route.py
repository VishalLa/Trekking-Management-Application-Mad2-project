from flask import Blueprint, request, jsonify

from service.staff_service import (
    StaffDashboardService
)
from service.trek_service import (
    ManageTrek
)

from auth.auth import role_required

staff_bp = Blueprint("staff_route", __name__, url_prefix="/staff")


@staff_bp.route("/assigned-trek-list/<string:user_id>", methods=["GET"])
@role_required("STAFF")
def get_assigned_trek(user_id: str):
    try: 
        trek_list = StaffDashboardService.get_assigned_treks(user_id=user_id, complete=False)

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

    except ValueError as e:
        return jsonify({"error": f"{e}"}), 404
    except Exception as e:
        return jsonify({"error": f"Internal Server error"}), 500
    

@staff_bp.route("/completed-trek-list/<string:user_id>")
@role_required("STAFF")
def get_completed_trek(user_id: str):
    try: 
        trek_list = StaffDashboardService.get_assigned_treks(user_id=user_id, complete=False)

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

