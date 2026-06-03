from database.session import db_session as db 
from database.model import User, Role
from core.security import (
    generate_stateless_otp_token, 
    generate_6_digit_otp, 
    generate_password_reset_token, 
    verify_stateless_otp_token, 
    verify_password,
    verify_password_reset_token
)


class PasswordResetService:

    @staticmethod
    def request_reset_via_email(email: str):
        user = db.query(User).filter_by(email=email).first()
        if not user:
            raise ValueError("If this email exists, a reset link has been sent.")
        
        # only trekker can reset via email
        if user.role != Role.TREKKER:
            raise ValueError("Staff member must reset their password via Phone Number.")
        
        token = generate_password_reset_token(user.email)
        reset_url = f"http://localhost:8080/reset-password?token={token}"

        # TODO: Send actual email via celery
        print(f"📧 EMAIL SENT TO {user.email}: Click to reset password: {reset_url}")
        return True
    

    @staticmethod
    def reset_with_email_token(token: str, new_password: str):
        email = verify_password_reset_token(token)
        
        if not email:
            raise ValueError("Invalid or expired reset token.")
            
        user = db.query(User).filter_by(email=email).first()
        if not user:
            raise ValueError("User not found.")
            
        user.set_password(new_password)
        try:
            db.commit()
        except Exception:
            db.rollback()
            raise Exception("Failed to reset password")
            
        return True
    

    @staticmethod
    def request_reset_via_phone(phone_no: str):
        user = db.query(User).filter_by(phone_no=phone_no).first()
        if not user:
            raise ValueError("Phone number not found.")
        
        otp = generate_6_digit_otp()
        reset_token = generate_stateless_otp_token(user.phone_no, otp)

        # TODO: Send the raw `otp` via SMS here
        print(f"📱 SMS SENT TO {user.phone_no}: Your password reset OTP is {otp}")

        return reset_token
    

    @staticmethod
    def reset_with_phone_otp(reset_token: str, user_typed_otp: str, new_password: str):
        payload = verify_stateless_otp_token(reset_token)
        if not payload:
            raise ValueError("OTP session has expired or is invalid. Please request a new one.")
        
        phone_no = payload.get("phone_no")
        saved_otp_hash = payload.get("otp_hash")

        if not verify_password(hashed_password=saved_otp_hash, plain_password=user_typed_otp):
            raise ValueError("Invalid OTP.")
        
        user = db.query(User).filter_by(phone_no=phone_no).first()

        if not user:
            raise ValueError("User not found.")
            
        user.set_password(new_password)
        try:
            db.commit()
        except Exception:
            db.rollback()
            raise Exception("Failed to reset password")
            
        return True
        
