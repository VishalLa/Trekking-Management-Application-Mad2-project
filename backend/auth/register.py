from flask import Blueprint, request, jsonify
from service.auth_service import AuthService
from .auth import role_required

auth_bp = Blueprint("auth_routes", __name__, url_prefix="/auth/register")

@auth_bp.route("/trekker", methods=["POST"])
def register_trekker():
    data = request.get_json()

    if not all(k in data for k in ("email", "password", "first_name", "phone_no")):
        return jsonify({"error": "Missing required fields"}), 400 
    
    try: 
        user = AuthService.register(
            email=data["email"],
            password=data["password"],
            first_name=data["first_name"],
            last_name=data.get("last_name", ""),
            phone_no=data["phone_no"],
            role="Trekker"
        )

        return jsonify({
            "message": "Registration successful", 
            "user_id": user.id
        }), 201
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 409
    except Exception as e: 
        return jsonify({"error": "Internal Server Error"}), 500


# only admin can create staff
@auth_bp.route("/staff", methods=["POST"])
@role_required("Admin")
def register_staff():
    data = request.get_json()

    if not all(k in data for k in ("email", "password", "first_name", "phone_no")):
        return jsonify({"error": "Missing required fields"}), 400 
    
    try: 
        user = AuthService.register(
            email=data["email"],
            password=data["password"],
            first_name=data["first_name"],
            last_name=data.get("last_name", ""),
            phone_no=data["phone_no"],
            role="Staff"
        )

        return jsonify({
            "message": "Registration successful", 
            "user_id": user.id
        }), 201
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 409
    except Exception as e: 
        return jsonify({"error": "Internal Server Error"}), 500

