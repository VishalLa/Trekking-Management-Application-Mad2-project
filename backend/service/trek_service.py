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
from tasks.email_service import info_about_new_trek


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

        if new_status == TrekStatus.OPEN and trek.status != TrekStatus.OPEN:
            trek.status = TrekStatus.OPEN
            
            all_trekkers = db.query(User).filter(
                User.role == Role.TREKKER,
                User.status == Status.ACTIVE
            ).all()

            count = 0
            for trekker in all_trekkers:
                info_about_new_trek.delay(
                    user_email=trekker.email,
                    user_name=trekker.first_name,
                    trek_name=trek.trek_name,
                    location=trek.location,
                    start_date=trek.start_date.strftime('%d %B %Y'),
                    end_date=trek.end_date.strftime('%d %B %Y'),
                    duration=trek.duration,
                    trek_details=trek.description
                )

                count += 1
                
            print(f"Queued {count} new trek announcements for {trek.trek_name}!")

        else:
            trek.status = new_status

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise Exception("Database transaction failed")
        