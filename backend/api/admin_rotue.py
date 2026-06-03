from flask import Blueprint, request, jsonify
from service.admin_service import (
    ManageStaff,
    ManageTrek, 
    ManageUser, 
    ListData,
    GlobalSearchService,
    LocalService
)
from service.report_service import ReportService
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
    

@admin_bp.route("/list-staff", methods=["GET"])
@role_required("Admin")
def get_all_staff():
    try:
        raw_staff_list = ListData.list_staffs()

        formatted_staff = [
            {
                "user_id": staff.id,
                "first_name": staff.first_name,
                "last_name": staff.last_name,
                "email": staff.email,
                "phone_no": staff.phone_no,
                "status": staff.status.name,
                "experience": staff.staff_profile.experience if staff.staff_profile else 0,
                "date_created": staff.date_created
            }
            for staff in raw_staff_list
        ]

        return jsonify(formatted_staff), 200
    
    except ValueError as e:
        return jsonify({"message": str(e)}), 200
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


@admin_bp.route("/list-user", methods=["GET"])
@role_required("Admin")
def get_all_user():
    try: 
        raw_user_list = ListData.list_users()

        formatted_users = [
            {
                "user_id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone_no": user.phone_no,
                "status": user.status.name,
                "date_created": user.date_created
            } for user in raw_user_list
        ]

        return jsonify(formatted_users), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 200
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


@admin_bp.route("/list-trek", methods=["GET"])
@role_required("Admin")
def get_all_trek():
    try: 
        raw_trek_list = ListData.list_trek()

        formatted_treks = [
            {
                "trek_id": trek.trek_id,
                "trek_name": trek.trek_name,
                "location": trek.location,
                "duration": trek.duration,
                "available_slots": trek.available_slots,
                "status": trek.status,
                "difficulty": trek.difficulty,
                "start_date": trek.start_date,
                "end_date": trek.end_date
            } for trek in raw_trek_list
        ]

        return jsonify(formatted_treks), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 200
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500
            

@admin_bp.route("/search", methods=["GET"])
@role_required("Admin")
def global_search():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({"error": "Please provide a search term using the '?q=' parameter."}), 400
    
    try:
        results = GlobalSearchService.global_search(query=query)

        if not any(results.values()):
            return jsonify({"message": "No results found."}), 404
            
        return jsonify(results), 200
    
    except Exception as e:
        return jsonify({"error": "An error occurred while searching."}), 500
    

@admin_bp.route("/search-trekker", methods=["GET"])
@role_required("Admin")
def search_trekker():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({"error": "Please provide a search term using the '?q=' parameter."}), 400
    
    try:
        results = LocalService.search_user(query=query, role="trekker")
        
        if not any(results.values()):
            return jsonify({"message": "No results found."}), 404
                    
        return jsonify(results), 200
            
    except Exception as e:
        return jsonify({"error": "An error occurred while searching."}), 500
            

@admin_bp.route("/search-staff", methods=["GET"])
@role_required("Admin")
def search_staff():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({"error": "Please provide a search term using the '?q=' parameter."}), 400
    
    try:
        results = LocalService.search_user(query=query, role="staff")
        
        if not any(results.values()):
            return jsonify({"message": "No results found."}), 404
                    
        return jsonify(results), 200
            
    except Exception as e:
        return jsonify({"error": "An error occurred while searching."}), 500
            
    
@admin_bp.route("/search-booking", methods=["GET"])
@role_required("Admin")
def search_booking():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({"error": "Please provide a search term using the '?q=' parameter."}), 400
    
    try:
        results = LocalService.search_booking(query=query)
        
        if not any(results.values()):
            return jsonify({"message": "No results found."}), 404
                    
        return jsonify(results), 200
            
    except Exception as e:
        return jsonify({"error": "An error occurred while searching."}), 500
            

@admin_bp.route("/search-trek", methods=["GET"])
@role_required("Admin")
def search_trek():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({"error": "Please provide a search term using the '?q=' parameter."}), 400
    
    try:
        results = LocalService.search_trek(query=query)
        
        if not any(results.values()):
            return jsonify({"message": "No results found."}), 404
                    
        return jsonify(results), 200
    
    except Exception as e:
        return jsonify({"error": "An error occurred while searching."}), 500


@admin_bp.route("/reports/dashboard", methods=["GET"])
@role_required("Admin")
def get_dashboard_reports():
    try:
        report_data = ReportService.get_dashboard_stats()
        return jsonify(report_data), 200
        
    except Exception as e:
        print(f"Report Generation Error: {e}")
        return jsonify({"error": "Failed to generate reports."}), 500
