from flask import Blueprint, request, jsonify
from service.admin_service import ManageStaff, ManageTrek, ManageUser
from auth.auth import role_required 

admin_bp = Blueprint("admin_routes", __name__, url_prefix="/admin")


@admin_bp.route("/user/<string:user_id>/blacklist", methods=["PUT"])
@role_required("Admin")
def blacklist_staff(user_id):
    try:
        ManageUser.change_status(user_id=user_id, is_active=False)

        return jsonify({
            "message": f"user with: {user_id} blacklisted"
        }), 200
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e: 
        return jsonify({"error": "Internal Server Error"}), 500


@admin_bp.route("/user/<string:user_id>/unblacklist", methods=["PUT"])
@role_required("Admin")
def unblacklist_staff(user_id):
    try:
        ManageUser.change_status(user_id=user_id, is_active=True)

        return jsonify({
            "message": f"user with: {user_id} unblacklisted"
        }), 200
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e: 
        return jsonify({"error": "Internal Server Error"}), 500


@admin_bp.route("/staff/<string:user_id>/trek/<string:trek_id>/assign", methods=["PUT"])
@role_required("Admin")
def assign_trek(user_id, trek_id):
    try:
        ManageStaff.assign_trek(staff_id=user_id, trek_id=trek_id)

        return jsonify({
            "message": f"staff with: {user_id} assigned to trek: {trek_id}"
        }), 200 
    
    except ValueError as e: 
        return jsonify({"error": str(e)}), 404
    except Exception as e: 
        return jsonify({"error": "Internal Server Error"}), 500
    

@admin_bp.route("/staff/<string:user_id>/delete", methods=["DELETE"])
@role_required("Admin")
def delete_staff(user_id):
    try:
        ManageStaff.delete_staff(staff_id=user_id)

        return jsonify({
            "message": f"staff with: {user_id} deleted"
        }), 200
    
    except ValueError as e: 
        return jsonify({"error": str(e)}), 404
    except Exception as e: 
        return jsonify({"error": "Internal Server Error"}), 500
    

@admin_bp.route("/trek/create", methods=["POST"])
@role_required("Admin")
def create_trek():
    data = request.get_json()

    if not all(k in data for k in ("trek_name", "location", "duration", "available_slots", "status", "difficulty", "start_date", "end_date")):
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        trek = ManageTrek.create_trek(data=data)
        
        return jsonify({
            "message": "Trek created successfuly",
            "trek_id": trek.trek_id,
            "trek_name": trek.trek_name
        }), 201
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 409
    except Exception as e: 
        return jsonify({"error": "Internal Server Error"}), 500
    

@admin_bp.route("/trek/<string:trek_id>/delete", methods=["DELETE"])
@role_required("Admin")
def delete_trek(trek_id):
    try:
        ManageTrek.delete_trek(trek_id=trek_id)

        return jsonify({
            "message": f"trek with: {trek_id} deleted"
        }), 200
    
    except ValueError as e: 
        return jsonify({"error": str(e)}), 404
    except Exception as e: 
        return jsonify({"error": "Internal Server Error"}), 500
    

@admin_bp.route("/trek/<string:trek_id>/<string:status>", methods=["PUT"])
@role_required("Admin")
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

