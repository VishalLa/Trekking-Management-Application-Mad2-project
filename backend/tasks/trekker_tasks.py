import io 
import csv 

from celery_app import app 
from database.model import (
    BookingArchive, 
    Booking
)
from database.session import db_session as db


@app.task(bind=True, max_retries=3)
def generate_booking_csv(self, user_id: str): 
    print(f"Background Worker: Generating Booking CSV: {user_id}...")

    try: 
        si = io.StringIO()
        csv_writer = csv.writer(si)

        csv_writer.writerow([
            "Record Type", 
            "Trek Name",
            "Location",
            "Start Date",
            "End Date"
            "Booking Date",
            "Number of Booking",
            "Payment Status"
        ])

        current_bookings = db.query(Booking).filter_by(user_id=user_id).all()
        for booking in current_bookings:
            csv_writer.writerow([
                "CURRENT",
                booking.trek.trek_name,
                booking.trek.location,
                booking.trek.start_date,
                booking.trek.end_date,
                booking.booking_date,
                booking.number_of_booking,
                booking.payment_status
            ])

        archived_bookings = db.query(BookingArchive).filter_by(user_id=user_id).all()
        for booking in archived_bookings:
            csv_writer.writerow([
                "ARCHIVED",
                booking.trek.trek_name,
                booking.trek.location,
                booking.historical_start_date,
                booking.historical_end_date,
                booking.booking_date,
                booking.number_of_booking,
                booking.payment_status
            ])

        return si.getvalue()

    except Exception as e: 
        raise ValueError(f"error: {e}")
    
    finally: 
        db.remove()

