from database.session import db_session as db 
from database.model import User, Trek, StaffProfile, TrekkerProfile
from .helper import validate_date_format


class ManageStaff:
    @staticmethod
    def change_status(
        status: bool,
        staff_id: str
    ):
        staff = db.query(StaffProfile).filter_by(user_id=staff_id).first()
        if not staff:
            raise ValueError(f"Staff with user id: {staff_id} not found!")
        
        staff.status = status 

        try: 
            db.commit()
        except Exception:
            raise Exception("Database transaction failed")
        

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
        """
        data ={
            trek_name: str, 
            location: str, 
            duration: int,
            available_slots: int,
            status: int,
            start_date: date,
            end_date: date
        }
        """
        existing_trek = db.query(Trek).filter_by(trek_name=data["trek_name"]).first()

        if existing_trek:
            raise ValueError(f"Trek with name: {data['trek_name']} already exists")
        
        new_trek = Trek(
            trek_name=data["trek_name"],
            location=data["location"],
            duration=int(data["duration"]),
            available_slots=int(data["available_slots"]),
            status=data["status"],
            start_date=validate_date_format(data["start_date"]),
            end_date=validate_date_format(data["end_date"])
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
        
        trek.status = status

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise Exception("Database transaction failed")
        

class ManageUser:
    @staticmethod
    def change_status(
        status: bool,
        trekker_id: str
    ):
        staff = db.query(TrekkerProfile).filter_by(user_id=trekker_id).first()
        if not staff:
            raise ValueError(f"Trekker with user id: {trekker_id} not found!")
        
        staff.status = status 

        try: 
            db.commit()
        except Exception:
            raise Exception("Database transaction failed")
