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
from datetime import datetime
from .helper import validate_date_format



class StaffDashboardService:

    @staticmethod
    def get_assigned_treks(user_id: str, complete: bool = True):
        staff = db.query(StaffProfile).filter_by(user_id=user_id).first()

        if not staff:
            raise ValueError("Staff Not found in database!")
        
        assigned_trek = staff.assigned_treks


        if complete:
            result = [
                trek for trek in assigned_trek 
                    if trek.status == TrekStatus.COMPLETE
                ]
            
        elif not complete:
            result = [
                trek for trek in assigned_trek 
                    if trek.status != TrekStatus.COMPLETE
                ]
        
        return result
    

    @staticmethod
    def list_booking(trek_id: str):
        booking_list = db.query(Booking).filter_by(trek_id=trek_id).all()
        return booking_list

