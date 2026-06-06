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
from sqlalchemy import or_, cast, String

class ManageTrek:

    @staticmethod
    def change_status(trek_id: str, status: str):
        trek = db.query(Trek).filter_by(trek_id=trek_id).first()

        if not trek:
            raise ValueError(f"Trek with id: {trek_id} not found!")
        
        try:
            new_status = TrekStatus[status.upper()]
            
        except KeyError:
            raise ValueError(f"Invalid trek status provided: '{status}'. Must be one of: PENDING, APPROVED, OPEN, CLOSED, COMPLETE.")
        
        trek.status = new_status

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise Exception("Database transaction failed")
        