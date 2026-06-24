from flask import Blueprint, request, jsonify, Response

from service.admin_service import (
    ManageStaff, 
    ManageUser, 
    ListData,
    GlobalSearchService,
    LocalSearchService,
    AssignedTrekService,
    ManageTrek as AdminManageTrek,
    Duplicate,
    InvalidInput
)
from service.trek_service import (
    ManageTrek,
    BookingService
)
from service.report_service import ReportService

from auth.auth import role_required 

from database.session import db_session as db 
from database.model import BookingArchive

from tasks.admin_tasks import generate_csv_task
from celery_app import app
from cache import cache

admin_bp = Blueprint("admin_routes", __name__)


@admin_bp.route("/user/<string:user_id>/blacklist", methods=["PUT"])
@role_required("ADMIN")
def blacklist_user(user_id):
    try:
        ManageUser.change_status(user_id=user_id, is_active=False)

        cache.delete('all_staff')

        return jsonify({
            "message": f"user with: {user_id} blacklisted"
        }), 200
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e: 
        return jsonify({"error": f"Internal Server Error"}), 500


@admin_bp.route("/user/<string:user_id>/unblacklist", methods=["PUT"])
@role_required("ADMIN")
def unblacklist_user(user_id):
    try:
        ManageUser.change_status(user_id=user_id, is_active=True)
        
        cache.delete('all_staff')
        cache.delete('all_trekker')

        return jsonify({
            "message": f"user with: {user_id} unblacklisted"
        }), 200
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e: 
        return jsonify({"error": "Internal Server Error"}), 500


@admin_bp.route("/staff/<string:user_id>/trek/<string:trek_id>/assign", methods=["PUT"])
@role_required("ADMIN")
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
@role_required("ADMIN")
def delete_staff(user_id):
    try:
        ManageStaff.delete_staff(staff_id=user_id)

        cache.delete('all_staff')
        cache.delete('all_trekker')

        return jsonify({
            "message": f"staff with: {user_id} deleted"
        }), 200
    
    except ValueError as e: 
        return jsonify({"error": str(e)}), 404
    except Exception as e: 
        return jsonify({"error": "Internal Server Error"}), 500
    

@admin_bp.route("/trek/create", methods=["POST"])
@role_required("ADMIN")
def create_trek():
    data = request.get_json()

    if not all(k in data for k in ("trek_name", "location", "available_slots", "difficulty", "start_date", "end_date")):
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        trek = AdminManageTrek.create_trek(data=data)

        cache.delete('all_available_treks')
        
        return jsonify({
            "message": "Trek created successfuly",
            "trek_id": trek.trek_id,
            "trek_name": trek.trek_name
        }), 201
    
    except Duplicate as e:
        return jsonify({"error": str(e)}), 409
    except InvalidInput as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e: 
        return jsonify({"error": "Internal Server Error"}), 500
    

@admin_bp.route("/trek/update/<string:trek_id>", methods=["POST"])
@role_required("ADMIN")
def update_trek(trek_id: str):
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No update data provided"}), 400

        AdminManageTrek.update_trek_details(data=data, trek_id=trek_id)
        
        cache.delete('all_available_treks')

        return jsonify({"message": "Trek updated successfully!"}), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
        
    except Exception as e:
        print(f"Error updating trek {trek_id}: {e}")
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/trek/<string:trek_id>/delete", methods=["DELETE"])
@role_required("ADMIN")
def delete_trek(trek_id):
    try:
        AdminManageTrek.delete_trek(trek_id=trek_id)

        cache.delete('all_available_treks')

        return jsonify({
            "message": f"trek with: {trek_id} deleted"
        }), 200
    
    except ValueError as e: 
        return jsonify({"error": str(e)}), 404
    except Exception as e: 
        return jsonify({"error": "Internal Server Error"}), 500
    

@admin_bp.route("/trek/<string:trek_id>/<string:status>", methods=["PUT"])
@role_required("ADMIN")
def change_status(trek_id, status):
    try:
        ManageTrek.change_status(trek_id=trek_id, status=status)

        cache.delete('all_available_treks')

        return jsonify({
            "message": f"trek with: {trek_id} change status: {status}"
        }), 200
    
    except ValueError as e: 
        return jsonify({"error": str(e)}), 404
    except Exception as e: 
        return jsonify({"error": "Internal Server Error"}), 500
    

@admin_bp.route("/list-staff", methods=["GET"])
@role_required("ADMIN")
@cache.cached(timeout=600, key_prefix='all_staff')
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
        return jsonify({"error": f"Internal server error"}), 500


@admin_bp.route("/list-user", methods=["GET"])
@role_required("ADMIN")
@cache.cached(timeout=600, key_prefix='all_trekker')
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
                "date_created": user.date_created,
                "role": user.role.name
            } for user in raw_user_list
        ]

        return jsonify(formatted_users), 200

    except ValueError as e:
        return jsonify([]), 200
    except Exception as e:
        print(e)
        return jsonify({"error": "Internal server error"}), 500


@admin_bp.route("/list-trek", methods=["GET"])
@role_required("ADMIN")
@cache.cached(timeout=600, key_prefix='all_available_treks')
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
                "status": trek.status.name,
                "difficulty": trek.difficulty.name,
                "start_date": trek.start_date,
                "end_date": trek.end_date,
                "price": trek.price
            } for trek in raw_trek_list
        ]

        return jsonify(formatted_treks), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 200
    except Exception as e:
        print(e)
        return jsonify({"error": "Internal server error"}), 500
            

@admin_bp.route("/search", methods=["GET"])
@role_required("ADMIN")
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
@role_required("ADMIN")
def search_trekker():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({"error": "Please provide a search term using the '?q=' parameter."}), 400
    
    try:
        results = LocalSearchService.search_user(query=query, role="trekker")
        
        if not any(results.values()):
            return jsonify({"message": "No results found."}), 404
                    
        return jsonify(results), 200
            
    except Exception as e:
        return jsonify({"error": "An error occurred while searching."}), 500
            

@admin_bp.route("/search-staff", methods=["GET"])
@role_required("ADMIN")
def search_staff():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({"error": "Please provide a search term using the '?q=' parameter."}), 400
    
    try:
        results = LocalSearchService.search_user(query=query, role="staff")
        
        if not any(results.values()):
            return jsonify({"message": "No results found."}), 404
                    
        return jsonify(results), 200
            
    except Exception as e:
        return jsonify({"error": "An error occurred while searching."}), 500
            
    
@admin_bp.route("/search-booking", methods=["GET"])
@role_required("ADMIN")
def search_booking():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({"error": "Please provide a search term using the '?q=' parameter."}), 400
    
    try:
        results = LocalSearchService.search_booking(query=query)
        
        if not any(results.values()):
            return jsonify({"message": "No results found."}), 404
                    
        return jsonify(results), 200
            
    except Exception as e:
        return jsonify({"error": "An error occurred while searching."}), 500
            

@admin_bp.route("/search-trek", methods=["GET"])
@role_required("ADMIN")
def search_trek():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({"error": "Please provide a search term using the '?q=' parameter."}), 400
    
    try:
        results = LocalSearchService.search_trek(query=query)
        
        if not any(results.values()):
            return jsonify({"message": "No results found."}), 404
                    
        return jsonify(results), 200
    
    except Exception as e:
        return jsonify({"error": "An error occurred while searching."}), 500


@admin_bp.route("/reports/dashboard", methods=["GET"])
@role_required("ADMIN")
@cache.cached(timeout=600, key_prefix='admin_report')
def get_dashboard_reports():
    try:
        report_data = ReportService.get_dashboard_stats()
        return jsonify(report_data), 200
        
    except Exception as e:
        print(f"Report Generation Error: {e}")
        return jsonify({"error": "Failed to generate reports."}), 500
    

@admin_bp.route("/reports/historical", methods=["GET"])
@cache.cached(timeout=600, key_prefix='historical_report')
@role_required("ADMIN")
def get_historical_report():
    try:
        data = ReportService.generate_historical_report_data()
        return jsonify(data), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@admin_bp.route("/booking/<string:trek_id>", methods=["GET"])
@role_required("ADMIN")
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
    

@admin_bp.route("/staff/<string:user_id>/treks", methods=["GET"])
@role_required("ADMIN")
def get_assigned_trek(user_id):
    try:
        assigned_trek_list = AssignedTrekService.get_assigned_trek(staff_id=user_id)

        formated_trek_list = [
            {
                "trek_name": trek.trek_name,
                "location": trek.location,
                "duration": trek.duration,
                "difficulty": trek.difficulty.name,
                "start_date": trek.start_date,
                "end_date": trek.end_date
            }
            for trek in assigned_trek_list
        ]

        return formated_trek_list, 200

    except Exception as e:
        return jsonify({"error": f"An error occured while fetching assigned treks for staff: {user_id}"}), 500


@admin_bp.route("/trek/<string:trek_id>/staff", methods=["GET"])
@role_required("ADMIN")
def trek_assigned_staff(trek_id):
    try:
        assigned_staff_list = AssignedTrekService.get_assigned_staff(trek_id=trek_id)

        formated_staff = [
            {
                "user_id": staff.user_id,
                "first_name": staff.user_account.first_name,
                "last_name": staff.user_account.last_name,
                "email": staff.user_account.email,
                "phone_no": staff.user_account.phone_no,
                "experience": staff.experience,
                "status": staff.user_account.status.value
            }
            for staff in assigned_staff_list
        ]

        return jsonify(formated_staff), 200

    except Exception as e:
        print(e)
        return jsonify({"error": f"An error occured while fetching assigned staff for trek: {trek_id}"}), 500


@admin_bp.route("/export/bookings/trigger", methods=["POST"])
@role_required("ADMIN")
def trigger_export():
    task = generate_csv_task.delay()
    return jsonify({"task_id": task.id}), 202


@admin_bp.route("/export/bookings/status/<task_id>", methods=["GET"])
@role_required("ADMIN")
def export_status(task_id):
    # Ask Celery/Redis how this specific task is doing
    task_result = app.AsyncResult(task_id)

    if task_result.state == 'PENDING' or task_result.state == 'STARTED':
        return jsonify({"status": "Processing..."}), 202
    
    elif task_result.state == "SUCCESS":
        csv_data = task_result.result

        if csv_data is None:
             return jsonify({"status": "Finalizing..."}), 202
        
        output = Response(csv_data, mimetype="text/csv")
        output.headers["Content-Disposition"] = "attachment; filename=Master_Booking_Report.csv"

        return output
    
    else:
        return jsonify({"error": "Task failed"}), 500


@admin_bp.route("/bookings/archive", methods=["GET"])
@role_required("ADMIN")
@cache.cached(timeout=600, key_prefix='archive_booking')
def get_archived_bookings():
    try: 
        archives = db.query(BookingArchive).order_by(BookingArchive.archived_at.desc()).all()

        data = []
        for archive in archives:
            user_name = f"{archive.user.first_name} {archive.user.last_name or ''}".strip() if archive.user else "Deleted User"
            trek_name = archive.trek.trek_name if archive.trek else "Deleted Trek"

            data.append({
                "archive_id": archive.archive_id,
                "user_name": user_name,
                "user_email": archive.user.email if archive.user else "N/A",
                "trek_name": trek_name,
                "historical_start_date": archive.historical_start_date.strftime('%d %b %Y'),
                "historical_end_date": archive.historical_end_date.strftime('%d %b %Y'),
                "booking_date": archive.booking_date.strftime('%d %b %Y'),
                "status": archive.status.name,
                "seats": archive.number_of_booking,
                "payment_status": "Paid" if archive.payment_status else "Pending"
            })

        return jsonify({"data": data}), 200
            
    except Exception as e:
        return jsonify({"error": "Failed to fetch archive history"}), 500
