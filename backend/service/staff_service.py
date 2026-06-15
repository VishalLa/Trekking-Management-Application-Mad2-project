from database.session import db_session as db 
from database.model import (
    User, 
    Trek, 
    StaffProfile,  
    Status, 
    TrekStatus, 
    TrekDifficulty,
    Role,
    Booking,
    BookingStatus
)
from .helper import validate_date_format


class StaffDashboardService:

    @staticmethod
    def get_assigned_treks(user_id: str):
        staff = db.query(StaffProfile).filter_by(user_id=user_id).first()

        if not staff:
            return []
        
        assigned_trek = staff.assigned_treks
        return assigned_trek
    

    @staticmethod
    def update_trek_slots(trek_id: str, slots: int):

        trek = db.query(Trek).filter_by(trek_id=trek_id).first()
        if not trek:
            raise ValueError(f"No trek with: {trek_id} found in database")
        
        trek.available_slots = slots
        
        try:
            db.commit()
        except Exception:
            db.rollback()
            raise Exception("Database transaction failed")
        

class StaffProfileService:

    @staticmethod
    def get_profile(user_id: str): 
        user = db.query(User).filter_by(id=user_id, role=Role.STAFF).first()

        if not user: 
            raise ValueError("Staff profile not found.")
        
        staff_data = user.staff_profile

        return {
            "id": user.id, 
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone_no": user.phone_no,
            "address": user.address,
            "bio": user.bio,
            "experience": staff_data.experience if staff_data else 0,
            "description": staff_data.description if staff_data else ""
        }
    

    @staticmethod
    def update_profile(user_id: str, data: dict):
        user = db.query(User).filter_by(id=user_id, role=Role.STAFF).first()
        
        if not user:
            raise ValueError("Staff profile not found.")
        
        if "first_name" in data: user.first_name = data["first_name"]
        if "last_name" in data: user.last_name = data["last_name"]
        if "phone_no" in data: user.phone_no = data["phone_no"]
        if "address" in data: user.address = data["address"]
        if "bio" in data: user.bio = data["bio"]

        staff_data = user.staff_profile
        if staff_data:
            if "experience" in data: staff_data.experience = int(data["experience"])
            if "description" in data: staff_data.description = data["description"]
            
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise Exception(f"Database transaction failed: {e}")

