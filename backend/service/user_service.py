from database.session import db_session as db
from database.model import User

class UserService:
    @staticmethod
    def update_profile(user_id: str, profile_data: dict):
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            raise ValueError("User not found")
        
        if "address" in profile_data:
            user.address = profile_data["address"]
        if "bio" in profile_data:
            user.bio = profile_data["bio"]
        if "gender" in profile_data:
            user.gender = profile_data["gender"]
        if "dob" in profile_data:
            user.dob = profile_data["dob"] 
            
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise Exception("Failed to update profile")
            
        return user
    