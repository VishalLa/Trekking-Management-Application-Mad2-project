from datetime import datetime
from celery_app import app 
from database.session import db_session as db
from database.model import Booking, BookingArchive


@app.task(bind=True, max_retries=3)
def archive_trek_bookings_task(self, trek_id: str, old_start_date: str, old_end_date: str):
    print(f"Starting background archive for trek {trek_id}...")
    
    try:
        old_bookings = db.query(Booking).filter_by(trek_id=trek_id).all()
        
        if not old_bookings:
            return "No bookings to archive."

        archives_to_insert = []
        parsed_start = datetime.strptime(old_start_date, '%Y-%m-%d').date()
        parsed_end = datetime.strptime(old_end_date, '%Y-%m-%d').date()

        for b in old_bookings:
            archive = BookingArchive(
                original_booking_id=b.booking_id,
                user_id=b.user_id,
                trek_id=b.trek_id,
                booking_date=b.booking_date,
                status=b.status,
                number_of_booking=b.number_of_booking,
                payment_status=b.payment_status,
                historical_start_date=parsed_start, 
                historical_end_date=parsed_end      
            )
            archives_to_insert.append(archive)

        db.add_all(archives_to_insert)
        db.query(Booking).filter_by(trek_id=trek_id).delete()
        
        db.commit()
        
        print(f"✅ Successfully archived {len(archives_to_insert)} bookings.")
        return f"Archived {len(archives_to_insert)} records"

    except Exception as exc:
        db.rollback() 
        print(f"❌ Archive failed for trek {trek_id}: {exc}")
        raise self.retry(exc=exc, countdown=60)
    