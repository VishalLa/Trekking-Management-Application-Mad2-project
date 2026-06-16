from database.session import db_session as db
from database.model import User, TrekkerProfile, StaffProfile, Role
from .helper import validate_credential
from core.security import generate_verification_token

from tasks.email_service import send_account_verification_mail


class AuthService:
    
    @staticmethod
    def register(data: dict, role: str):

        """
        for trekker data fromat 
        {
            "email": str,
            "password": str, 
            "first_name": str, 
            "last_name": str, 
            "phone_no": str, 
        }

        for staff 
        {
            "email": str,
            "password": str, 
            "first_name": str, 
            "last_name": str, 
            "phone_no": str, 
            "experience": int
        }
        """
        
        existing_user = db.query(User).filter_by(email=data["email"]).first()
        if existing_user:
            raise ValueError(f"A user with this email already exists.")
        
        try:
            enum_role = Role[role.upper()]
        except KeyError:
            raise ValueError("Invalid role provided.")
        
        try:
            validate_credential(
                data={
                    "email": data["email"],
                    "password": data["password"],
                    "phone_no": data["phone_no"]
                }
            )

        except ValueError as e:
            raise ValueError(f"{e}")

        new_user = User(
            email=data["email"],
            role=enum_role,
            first_name=data["first_name"],
            last_name=data["last_name"],
            phone_no=data["phone_no"],
            password=data["password"]
        )

        if enum_role == Role.TREKKER:
            new_user.trekker_profile = TrekkerProfile()
            token = generate_verification_token(new_user.email) 
            verification_link = f"http://localhost:5173/verify-email?token={token}"
            send_account_verification_mail(
                user_email=data["email"],
                user_name=f"{data['first_name']} {data['last_name']}",
                verification_link=verification_link
            )

        elif enum_role == Role.STAFF:
            new_user.staff_profile = StaffProfile(experience=str(data["experience"]))

        try:
            db.add(new_user)
            db.commit()
        except Exception as e:
            db.rollback()
            raise Exception("Database transaction failed")

        return new_user
    