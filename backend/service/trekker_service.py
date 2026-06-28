from database.session import db_session as db
from database.model import (
    User,
    Status,
    Trek, 
    TrekStatus,
    TrekDifficulty,
    Booking,
    BookingStatus,
    TrekkerProfile,
    Role
)
from tasks.payment_service import payment
from tasks.email_service import send_booked_trek_mail, send_cancel_booking_mail
from sqlalchemy import or_, cast, String
from datetime import date


class Duplicate(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class NotFound(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class PaymentFailed(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class PaymentCompleted(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)



class TrekkerProfile:
    @staticmethod
    def update_profile(user_id: str, profile_data: dict):
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            raise NotFound("User not found")
        
        if "first_name" in profile_data: user.first_name = profile_data["first_name"]
        if "last_name" in profile_data: user.last_name = profile_data["last_name"]
        if "phone_no" in profile_data: user.phone_no = profile_data["phone_no"]
        if "address" in profile_data: user.address = profile_data["address"]
        if "bio" in profile_data: user.bio = profile_data["bio"]
        if "dob" in profile_data: user.dob = profile_data["dob"] 

            
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise Exception("Failed to update profile")
    

    @staticmethod 
    def get_trekker_data(user_id: str):
        user = db.query(User).filter(
            User.id == user_id,
            User.role == Role.TREKKER
        ).first()

        if not user:
            raise NotFound(f"User not found")
        
        format_data = {
            "user_id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone_no": user.phone_no,
            "bio": user.bio,
            "address": user.address,
        }

        return format_data
    

class TrekkerDashboard:

    @staticmethod 
    def get_open_and_approved_trek():
        treks = db.query(Trek).all()

        if treks == []:
            raise NotFound("No treks found!")
        
        formated_trek = [
            {
                "trek_id": trek.trek_id,
                "trek_name": trek.trek_name,
                "location": trek.location,
                "duration": trek.duration,
                "available_slots": trek.available_slots,
                "status": trek.status.name, 
                "difficulty": trek.difficulty.name,
                "price": trek.price,
                "start_date": trek.start_date,
                "end_date": trek.end_date,
            }
            for trek in treks 
                if trek.status in [TrekStatus.OPEN, TrekStatus.APPROVED]
        ]

        return formated_trek
    

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
    def get_booked_treks(user_id: str):
        bookings = db.query(Booking).filter(
            Booking.user_id == user_id,
            # Booking.status != BookingStatus.CANCELLED, 
            # Booking.payment_status == True
        ).all()

        result = []
        for booking in bookings:
            trek = booking.trek
            
            if not trek:
                continue 
                
            total_amount = booking.number_of_booking * trek.price

            result.append({
                "booking_id": booking.booking_id,
                "trek_id": trek.trek_id,
                "trek_name": trek.trek_name,
                "location": trek.location,
                "start_date": trek.start_date.strftime("%Y-%m-%d"),
                "end_date": trek.end_date.strftime("%Y-%m-%d"),
                "number_of_tickets": booking.number_of_booking,
                "price_per_ticket": trek.price,
                "total_amount": total_amount,
                "booking_status": booking.status.name,
                "booking_date": booking.booking_date.strftime("%Y-%m-%d %H:%M"),
                "payment_status": booking.payment_status
            })

        return result
    
    
class BookingService:

    @staticmethod
    def book_trek(user_id: str, trek_id: str, number_of_booking: int):
        today = date.today()

        user = db.query(User).filter(
            User.id == user_id, 
            User.role == Role.TREKKER,
            User.status == Status.ACTIVE
        ).first()
        if not user:
            raise NotFound(f"No valid Trekker account found for ID: {user_id}")
        
        trek = db.query(Trek).filter_by(trek_id=trek_id).first()
        if not trek:
            raise NotFound(f"No Trek found for ID: {trek_id}")
        
        existing_booking = db.query(Booking).filter(
            Booking.user_id == user_id, 
            Booking.trek_id == trek_id, 
        ).first()

        if existing_booking:
            raise Duplicate(f"Booking for trek by trekker already exists")

        
        if trek.available_slots < number_of_booking:
            raise ValueError(f"Cannot book {number_of_booking} tickets. Only {trek.available_slots} slots remaining.")
        
        if trek.start_date <= today:
            raise ValueError("This trek has already started and cannot be booked.")
        
        trek.available_slots -= number_of_booking
        
        booking = Booking(
            user_id = user_id, 
            trek_id = trek_id, 
            booking_date = today,
            number_of_booking = number_of_booking,
            status = BookingStatus.BOOKED,
            payment_status = False,
        )

        send_booked_trek_mail(
            user_email=user.email,
            user_name=f"{user.first_name} {user.last_name}",
            trek_name=trek.trek_name,
            location=trek.location,
            start_date=trek.start_date,
            end_date=trek.end_date,
            duration=trek.duration,
            trek_details=trek.description
        )

        try: 
            db.add(booking)
            db.commit()
        except Exception as e:
            db.rollback()
            raise Exception(f"Database Error: {str(e)}")
        
        return booking
        

    @staticmethod
    def complete_booking(user_id: str, booking_id: str, card_data: dict):
        """
        Expected card_data: 
        {
            'card_no': int, 
            'card_cvv': int,
            'price': float,
            'phone_no': int, 
            'expration_date': str, # Expected format 'MM/YY'
            'card_holder_name': str
        }
        """
        booking = db.query(Booking).filter(
            Booking.user_id == user_id,
            Booking.booking_id == booking_id
        ).first()

        if not booking:
            raise NotFound("Booking data not found")
        
        if booking.payment_status:
            raise PaymentCompleted(f"Payment already done for {booking.trek.trek_name}")
        
        payment_status = payment(card_data=card_data)

        if payment_status:
            booking.payment_status = payment_status
        else:
            raise PaymentFailed("Payment Failed If your amount is debited refund will be initiated")
        
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise Exception("Server Error")
        

    def cancel_booking(user_id: str, booking_id: str):
        booking = db.query(Booking).filter(
            Booking.user_id == user_id,
            Booking.booking_id == booking_id
        ).first()

        if not booking:
            raise NotFound(f"No Booking found for user: {user_id}") 
        
        try: 
            trek = booking.trek 
            trek.available_slots += booking.number_of_booking

            send_cancel_booking_mail(
                user_name=f"{booking.user.first_name} {booking.user.last_name}",
                user_email=booking.user.email,
                trek_name=booking.trek.trek_name
            )

            db.delete(booking)
            db.commit()
        except Exception as e:
            db.rollback()
            raise Exception("Internal Server Error")
        

class TrekAssignedStaff:

    @staticmethod
    def get_trek_specific_staff(trek_id: str): 
        trek = db.query(Trek).filter_by(trek_id=trek_id).first()

        if not trek: 
            raise NotFound("Trek Not Found!")
        
        assigned_staff = trek.assigned_staff

        formated_staff = [{
            "name": f"{staff.user_account.first_name} {staff.user_account.last_name}",
            "phone_no": staff.user_account.phone_no,
            "experience": staff.experience

        } for staff in assigned_staff]

        return formated_staff
