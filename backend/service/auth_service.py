from database.session import db_session as db
from database.model import User, TrekkerProfile, StaffProfile


class AuthService:
    @staticmethod
    def register(
        email: str, 
        password: str, 
        first_name: str,
        last_name: str, 
        phone_no: str,
        role: str
    ):
        
        existing_user = db.query(User).filter_by(email=email).first()
        if existing_user:
            raise ValueError(f"A {role} with this email already exists")
        
        new_user = User(
            email=email,
            role=role
        )
        new_user.set_password(password=password)

        if role == "Trekker":
            new_profile = TrekkerProfile(
                first_name=first_name,
                last_name=last_name,
                phone_no=phone_no
            )
            new_user.trekker_profile = new_profile

        if role == "Staff":
            new_profile = StaffProfile(
                first_name=first_name,
                last_name=last_name,
                phone_no=phone_no,
                status=True
            )
            new_user.staff_profile = new_profile

        try:
            db.add(new_user)
            db.commit()
        except Exception as e:
            db.rollback()
            raise Exception("Database transaction failed")

        return new_user
    
    