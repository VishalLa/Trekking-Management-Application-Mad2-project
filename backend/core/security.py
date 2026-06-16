import os
import random
import hashlib 
from passlib.context import CryptContext

from itsdangerous import URLSafeTimedSerializer
from flask import current_app

from core.helper import load_env

basedir = os.path.abspath(os.path.dirname(__file__))
env_path = os.path.join(basedir, "../.env")
load_env(env_path)

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def _hash_per_bcrypt(password: str) -> str: 
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def hash_password(password: str) -> str: 
    safe_password = _hash_per_bcrypt(password)
    return pwd_context.hash(safe_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    safe_password = _hash_per_bcrypt(plain_password)
    return pwd_context.verify(safe_password, hashed_password)


def generate_verification_token(email: str) -> str: 
    serializer = URLSafeTimedSerializer(current_app.config["JWT_SECRET_KEY"])
    return serializer.dumps(email, salt=os.environ.get("EMAIL_OTP_SALT"))

def verify_token(token: str, expiration_seconds: int = 3600):
    serializer = URLSafeTimedSerializer(current_app.config["JWT_SECRET_KEY"])

    try:
        email = serializer.loads(token, salt=os.environ.get("EMAIL_OTP_SALT"), max_age=expiration_seconds)
        return email
    except Exception:
         return None
    

def generate_password_reset_token(email: str) -> str:
    serializer = URLSafeTimedSerializer(current_app.config["JWT_SECRET_KEY"])
    return serializer.dumps(email, salt=os.environ.get("EMAIL_OTP_SALT"))

def verify_password_reset_token(token: str, expiration_seconds: int = 900): # 15 minutes
    serializer = URLSafeTimedSerializer(current_app.config["JWT_SECRET_KEY"])
    try:
        email = serializer.loads(token, salt=os.environ.get("EMAIL_OTP_SALT"), max_age=expiration_seconds)
        return email
    except Exception:
        return None
    

# def generate_stateless_otp_token(phone_no: str, raw_otp: str) -> str:
#     serializer = URLSafeTimedSerializer(current_app.config["JWT_SECRET_KEY"])
#     hashed_otp = hash_password(raw_otp)
    
#     payload = {
#         "phone_no": phone_no,
#         "otp_hash": hashed_otp
#     }
#     return serializer.dumps(payload, salt=os.environ.get("PHONE_OTP_SALT"))

# def verify_stateless_otp_token(token: str, expiration_seconds: int = 300): # 5 mins
#     serializer = URLSafeTimedSerializer(current_app.config["JWT_SECRET_KEY"])
#     try:
#         payload = serializer.loads(token, salt=os.environ.get("PHONE_OTP_SALT"), max_age=expiration_seconds)
#         return payload
#     except Exception:
#         return None


# def generate_6_digit_otp() -> str:
#     # Generates a random 6-digit string like "048291"
#     return str(random.randint(100000, 999999))
