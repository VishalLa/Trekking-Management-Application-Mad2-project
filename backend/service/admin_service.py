from database.session import db_session as db 
from database.model import User, Trek, StaffProfile, TrekkerProfile, Status, TrekStatus, TrekDifficulty
from .helper import validate_date_format


class ManageStaff:
        
    @staticmethod
    def assign_trek(
        staff_id: str,
        trek_id: str,
    ):
        staff = db.query(StaffProfile).filter_by(user_id=staff_id).first()
        if not staff:
            raise ValueError(f"Staff with user id: {staff_id} not found!")
        
        trek = db.query(Trek).filter_by(trek_id=trek_id).first()
        if not trek:
            raise ValueError(f"Trek with id: {trek_id} not found!")
        
        if trek in staff.assigned_treks:
            raise ValueError("This trek is already assigned to this staff member.")
        
        staff.assigned_treks.append(trek)

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise Exception("Database transaction failed")
            
        return staff
    

    @staticmethod
    def delete_staff(staff_id: str):
        staff = db.query(StaffProfile).filter_by(user_id=staff_id).first()
        if not staff:
            raise ValueError(f"Staff with user id: {staff_id} not found!")
        
        try:
            db.delete(staff)
            db.commit()
        except Exception:
            db.rollback()
            raise Exception("Database transaction failed")


class ManageTrek:

    @staticmethod
    def create_trek(data: dict):
        existing_trek = db.query(Trek).filter_by(trek_name=data["trek_name"]).first()

        if existing_trek:
            raise ValueError(f"Trek with name: {data['trek_name']} already exists")
        
        try:
            difficulty = TrekDifficulty[data["difficulty"].upper()]
        except KeyError:
            raise ValueError(f"Invalid difficulty provided: {data['difficulty']}, Must be one of these EASY, MEDIUM, HARD")
        
        new_trek = Trek(
            trek_name=data["trek_name"],
            location=data["location"],
            duration=int(data["duration"]),
            available_slots=int(data["available_slots"]),
            status=TrekStatus.PENDING,
            difficulty=difficulty,
            start_date=validate_date_format(data["start_date"]),
            end_date=validate_date_format(data["end_date"]),
            description=data.get("description", "")
        )

        try:
            db.add(new_trek)
            db.commit()
        except Exception:
            db.rollback()
            raise Exception("Database transaction failed")
        
        return new_trek
    

    @staticmethod
    def delete_trek(trek_id: str):
        trek = db.query(Trek).filter_by(trek_id=trek_id).first()

        if not trek:
            raise ValueError(f"Trek with id: {trek_id} not found!")
        
        try:
            db.delete(trek)
            db.commit()
        except Exception:
            db.rollback()
            raise Exception("Database transaction failed")
        

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
        

class ManageUser:
    @staticmethod
    def change_status(
        is_active: bool,
        user_id: str
    ):
        user = db.query(User).filter_by(user_id=user_id).first()
        if not user:
            raise ValueError(f"Trekker / Staff with user id: {user_id} not found!")
        
        new_status = Status.ACTIVE if is_active else Status.SUSPENDED
        user.status = new_status

        try: 
            db.commit()
        except Exception:
            db.rollback()
            raise Exception("Database transaction failed")
