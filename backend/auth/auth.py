from flask import Blueprint, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, get_jwt, verify_jwt_in_request

from database.session import db_session
from database.model import User

from functools import wraps 

login_bp = Blueprint("login_controller", __name__)


# Manages login session
@login_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']

    user = db_session.query(User).filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid email or password"}), 401
    
    additional_claims = {"role": user.role}

    access_token = create_access_token(
        identity=user.id,
        additional_claims=additional_claims
    )

    return jsonify({
        "access_token": access_token,
        "user_id": user.id,
        "role": user.role
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

