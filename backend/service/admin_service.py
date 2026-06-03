from database.session import db_session as db 
from database.model import (
    User, 
    Trek, 
    StaffProfile,  
    Status, 
    TrekStatus, 
    TrekDifficulty,
    Role,
    Booking
)
from sqlalchemy import or_, cast, String
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


class ListData:

    @staticmethod
    def list_staffs():
        staff_list = db.query(User).filter_by(role=Role.STAFF).all()
        
        if not staff_list:
            raise ValueError(f"No Staff found")
        return staff_list
    

    @staticmethod
    def list_users():
        user_list = db.query(User).filter_by(role=Role.TREKKER).all()

        if not user_list:
            raise ValueError(f"No registred user found")
        return user_list
    
    
    @staticmethod
    def list_trek():
        trek_list = db.query(Trek).all()

        if not trek_list:
            raise ValueError(f"No trek are added yet")
        return trek_list


class GlobalSearchService:

    @staticmethod
    def global_search(query: str):
        search_term = f"%{query}%"

        # search treks 
        treks = db.query(Trek).filter(
            or_(
                Trek.trek_name.ilike(search_term),
                Trek.location.ilike(search_term),
                cast(Trek.duration, String).ilike(search_term),
                cast(Trek.status, String).ilike(search_term),
                cast(Trek.difficulty, String).ilike(search_term),
                cast(Trek.start_date, String).ilike(search_term),
                cast(Trek.end_date, String).ilike(search_term)
            )
        ).all()

        # search user 
        users  = db.query(User).filter(
            or_(
                User.email.ilike(search_term),
                User.first_name.ilike(search_term),
                User.last_name.ilike(search_term),
                User.phone_no.ilike(search_term),
            )
        ).all()

        # serach booking
        bookings = db.query(Booking).join(User).join(Trek).filter(
            or_(
                Booking.booking_id.ilike(search_term),
                cast(Booking.booking_date, String).ilike(search_term),
                User.first_name.ilike(search_term),
                User.last_name.ilike(search_term),
                User.email.ilike(search_term),
                Trek.trek_name.ilike(search_term),
            )
        )

        return {
            "treks": [
                {
                    "id": t.trek_id,
                    "name": t.trek_name,
                    "location": t.location,
                    "duration": t.duration,
                    "status": t.status.name,
                    "price": t.price,
                    "difficulty": t.difficulty.name,
                    "start_date": t.start_date,
                    "end_date": t.end_date
                } for t in treks
            ],

            "staff": [
                {
                    "id": u.id,
                    "name": f"{u.first_name} {u.last_name or ''}".strip(),
                    "email": u.email,
                    "phone_no": u.phone_no,
                    "status": u.status.name,
                    "experience": u.staff_profile.experience
                } for u in users if u.role == Role.STAFF
            ],

            "trekkers": [
                {
                    "id": u.id,
                    "name": f"{u.first_name} {u.last_name or ''}".strip(),
                    "email": u.email,
                    "phone_no": u.phone_no,
                    "status": u.status.name
                } for u in users if u.role == Role.TREKKER
            ], 

            "booking": [
                {
                    "id": b.booking_id,
                    "trek_name": b.trek.trek_name,
                    "user_name": f"{b.user.first_name} {b.user.last_name or ''}".strip(),
                    "status": b.status.name
                } for b in bookings
            ]
        }
    

class LocalService:

    @staticmethod
    def search_trek(query: str):
        search_term = f"%{query}%"

        treks = db.query(Trek).filter(
            or_(
                Trek.trek_name.ilike(search_term),
                Trek.location.ilike(search_term),
                cast(Trek.duration, String).ilike(search_term),
                cast(Trek.status, String).ilike(search_term),
                cast(Trek.difficulty, String).ilike(search_term),
                cast(Trek.start_date, String).ilike(search_term),
                cast(Trek.end_date, String).ilike(search_term)
            )
        ).all()

        return {
            "treks": [
                {
                    "id": t.trek_id,
                    "name": t.trek_name,
                    "location": t.location,
                    "duration": t.duration,
                    "status": t.status.name,
                    "price": t.price,
                    "difficulty": t.difficulty.name,
                    "start_date": t.start_date,
                    "end_date": t.end_date
                } for t in treks
            ]
        }
    

    @staticmethod 
    def search_user(query: str, role: str):
        search_term = f"%{query}%"

        try:
            enum_role = Role[role.upper()]
        except KeyError:
            raise ValueError("Invalid role provided. role can only be Staff, Trekker")

        users = db.query(User).filter(
            User.role == enum_role,
            or_(
                User.email.ilike(search_term),
                User.first_name.ilike(search_term),
                User.last_name.ilike(search_term),
                User.phone_no.ilike(search_term),
            )
        ).all()

        return {
            "users": [
                {
                    "id": u.id,
                    "name": f"{u.first_name} {u.last_name or ''}".strip(),
                    "email": u.email,
                    "phone_no": u.phone_no,
                    "status": u.status.name
                } for u in users
            ], 
        }
    

    @staticmethod
    def search_booking(query: str):
        search_term = f"%{query}%"

        bookings = db.query(Booking).join(User).join(Trek).filter(
            or_(
                Booking.booking_id.ilike(search_term),
                cast(Booking.booking_date, String).ilike(search_term), 
                User.first_name.ilike(search_term),
                User.last_name.ilike(search_term),
                User.email.ilike(search_term),
                Trek.trek_name.ilike(search_term),
            )
        )

        return {
            "booking": [
                {
                    "id": b.booking_id,
                    "trek_name": b.trek.trek_name,
                    "user_name": f"{b.user.first_name} {b.user.last_name or ''}".strip(),
                    "status": b.status.name
                } for b in bookings
            ]
        }
