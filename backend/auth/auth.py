from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt, verify_jwt_in_request

from database.session import db_session as db
from database.model import User, Role
from core.security import verify_token
from service.register_service import AuthService
from service.password_service import PasswordResetService

from functools import wraps 

from datetime import timedelta

auth_bp = Blueprint("login_controller", __name__)


# Manages login session
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']

    user = db.query(User).filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid email or password"}), 401
    
    if user.role == Role.TREKKER:
        if user.trekker_profile and not user.trekker_profile.email_verified:
            return jsonify({"message": "Please check your email to verify your account before logging in."}), 403
    
    additional_claims = {"role": user.role.name}

    # admin only have small expration time user and staff will have a 24 hour of expration time
    if user.role == Role.ADMIN:
        custom_expiration = timedelta(hours=2)
    else:
        custom_expiration = timedelta(hours=24)

    access_token = create_access_token(
        identity=user.id,
        additional_claims=additional_claims,
        custom_expiration=custom_expiration
    )

    return jsonify({
        "access_token": access_token,
        "user_id": user.id,
        "role": user.role.name
    }), 200


# custome decorator 
def role_required(required_role):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            # ensure a valid jwt is present in the request header
            verify_jwt_in_request()
            # extract the data (claims)
            claims = get_jwt()

            if claims.get("role") != required_role:
                return jsonify(
                    {"message": f"Access forbidden: {required_role}role required."}
                ), 403
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper


@auth_bp.route("/auth/register/trekker", methods=["POST"])
def register_trekker():
    data = request.get_json()

    if not all(k in data for k in ("email", "password", "first_name", "phone_no")):
        return jsonify({"error": "Missing required fields"}), 400 
    
    try: 
        user = AuthService.register(
            data=data,
            role="Trekker"
        )

        return jsonify({
            "message": "Registration successful. Please check your email to verify your account.", 
            "user_id": user.id
        }), 201
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 409
    except Exception as e: 
        return jsonify({"error": "Internal Server Error"}), 500


# only admin can create staff
@auth_bp.route("/auth/register/staff", methods=["POST"])
@role_required("Admin")
def register_staff():
    data = request.get_json()

    if not all(k in data for k in ("email", "password", "first_name", "phone_no")):
        return jsonify({"error": "Missing required fields"}), 400 
    
    try: 
        user = AuthService.register(
            data=data,
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


@auth_bp.route("/auth/verify-email", methods=["POST"])
def verify_email():
    data = request.get_json()
    token = data.get("token")

    if not token:
        return jsonify({"error": "No token provided"}), 400
    
    email = verify_token(token, expiration_seconds=3600)
    if not email:
        return jsonify({"error": "The verification link is invalid or has expired."}), 400
    
    user = db.query(User).filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if user.role != Role.TREKKER:
        return jsonify({"message": "This account type does not require email verification."}), 200
    
    if user.trekker_profile.email_verified:
        return jsonify({"message": "Account is already verified."}), 200
    
    user.trekker_profile.email_verified = True

    try:
        db.commit()
        return jsonify({"message": "Email verified successfully! You can now log in."}), 200
    except Exception:
        db.rollback()
        return jsonify({"error": "Database error"}), 500
    

@auth_bp.route("/auth/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json()
    new_password = data.get("new_password")
    
    if not new_password:
        return jsonify({"error": "new_password is required"}), 400

    try:
        # Reset via Email Token
        if "token" in data:
            PasswordResetService.reset_with_email_token(data["token"], new_password)
            
            return jsonify({"message": "Password reset successfully. You can now log in."}), 200
            
        # Reset via Phone OTP
        elif "phone_no" in data and "otp" in data:
            PasswordResetService.reset_with_phone_otp(data["phone_no"], data["otp"], new_password)

            return jsonify({"message": "Password reset successfully. You can now log in."}), 200
            
        else:
            return jsonify({"error": "Please provide a valid token OR phone_no and otp."}), 400
            
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500
    