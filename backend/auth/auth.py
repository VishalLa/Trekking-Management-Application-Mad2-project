from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt, verify_jwt_in_request, jwt_required

from database.session import db_session as db
from database.model import User, Role, Status
from core.security import verify_token, generate_verification_token
from service.register_service import AuthService
from service.password_service import PasswordResetService
from tasks.email_service import send_account_verification_mail
from cache import cache

from functools import wraps 

from datetime import timedelta

auth_bp = Blueprint("auth", __name__)


# Manages login session
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']

    user = db.query(User).filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid email or password"}), 401

    if user.status == Status.SUSPENDED:
        return jsonify({"message": "Account has been suspended please contact admin"}), 401
    
    if user.role == Role.TREKKER:
        if user.trekker_profile and not user.trekker_profile.email_verified:
            token = generate_verification_token(user.email) 
            verification_link = f"http://localhost:5173/verify-email?token={token}"
            send_account_verification_mail(
                user_email=data["email"],
                user_name=f"{user.first_name} {user.last_name}",
                verification_link=verification_link
            )
            return jsonify({"message": "Please check your email to verify your account before logging in."}), 403
    
    additional_claims = {"role": user.role.name}

    # admin only have small expration time user and staff will have a 24 hour of expration time
    custom_expiration = None
    if user.role == Role.ADMIN:
        custom_expiration = timedelta(hours=2)
    else:
        custom_expiration = timedelta(hours=24)

    access_token = create_access_token(
        identity=user.id,
        additional_claims=additional_claims,
        expires_delta=custom_expiration
    )

    return jsonify({
        "access_token": access_token,
        "user_id": user.id,
        "role": user.role.name
    }), 200


# custome decorator 
def role_required(required_role):
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            
            # print(f"Token contains role -> {claims.get('role')}")
            # print(f"Route requires role -> {required_role}")
            
            if claims.get("role") != required_role:
                return jsonify({"message": "Forbidden access"}), 403
                
            return fn(*args, **kwargs)
        return wrapper
    return decorator


@auth_bp.route("/register/trekker", methods=["POST"])
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
@auth_bp.route("/register/staff", methods=["POST"])
@role_required("ADMIN")
def register_staff():
    data = request.get_json()

    if not all(k in data for k in ("email", "password", "first_name", "phone_no")):
        return jsonify({"error": "Missing required fields"}), 400 
    
    try: 
        user = AuthService.register(
            data=data,
            role="Staff"
        )

        cache.delete('all_staff')

        return jsonify({
            "message": "Registration successful", 
            "user_id": user.id
        }), 201
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 409
    except Exception as e: 
        return jsonify({"error": "Internal Server Error"}), 500


@auth_bp.route("/verify-email", methods=["POST"])
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
    

@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json()
    # method = data.get("method")
    
    try:
        # # Email Request
        # if method == "email":
        #     email = data.get("email")
        #     if not email:
        #         return jsonify({"error": "Email is required for this method"}), 400
                
        #     PasswordResetService.request_reset_via_email(email)
        #     return jsonify({"message": "If the email exists, a reset link has been sent."}), 200
            
        # # Phone Request
        # elif method == "phone":
        #     phone_no = data.get("phone_no")
        #     if not phone_no:
        #         return jsonify({"error": "Phone number is required for this method"}), 400
                
        #     token = PasswordResetService.request_reset_via_phone(phone_no)
        #     return jsonify({
        #         "message": "An OTP has been sent to your phone.",
        #         "reset_token": token 
        #     }), 200
            
        # else:
        #     return jsonify({"error": "Invalid or missing reset method. Must be 'email' or 'phone'."}), 400
        
        email = data.get("email")
        if not email:
            return jsonify({"error": "Email is required for this method"}), 400
                
        PasswordResetService.request_reset_via_email(email)
        return jsonify({"message": "If the email exists, a reset link has been sent."}), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500
    

@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json()
    # method = data.get("method")
    new_password = data.get("new_password")
    
    if not new_password:
        return jsonify({"error": "new_password is required"}), 400

    try:
        # # Execute Email Reset
        # if method == "email":
        #     token = data.get("token")
        #     if not token:
        #         return jsonify({"error": "Email verification token is missing"}), 400
                
        #     PasswordResetService.reset_with_email_token(token, new_password)
        #     return jsonify({"message": "Password reset successfully. You can now log in."}), 200
            
        # # Execute Phone Reset
        # elif method == "phone":
        #     reset_token = data.get("reset_token")
        #     otp = data.get("otp")
            
        #     if not reset_token or not otp:
        #         return jsonify({"error": "Both reset_token and otp are required for phone resets"}), 400
                
        #     PasswordResetService.reset_with_phone_otp(reset_token, otp, new_password)
        #     return jsonify({"message": "Password reset successfully. You can now log in."}), 200
            
        # else:
        #     return jsonify({"error": "Invalid or missing reset method. Must be 'email' or 'phone'."}), 400

        token = data.get("token")
        if not token:
            return jsonify({"error": "Email verification token is missing"}), 400
                
        PasswordResetService.reset_with_email_token(token, new_password)
        return jsonify({"message": "Password reset successfully. You can now log in."}), 200
            
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500
    