import os
import io 
import csv
import smtplib # simple mail transfer protocol 

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date

from celery_app import app 
from service.report_service import ReportService
from core.helper import load_env

from database.session import db_session as db 
from database.model import Booking, BookingArchive

basedir = os.path.abspath(os.path.dirname(__file__))

env_path = os.path.join(basedir, "../.env")
load_env(env_path)

@app.task
def generate_monthly_report(admin_email: str="admin@trek.com"):
    print("starting monthly report generation ...")
    today = date.today()
    month_name = today.strftime('%B %Y')

    try:

        html_content = ReportService.generate_monthly_report()
        sender_email = os.environ.get("EMAIL_USER")
        sender_password = os.environ.get("EMAIL_PASS")

        msg = MIMEMultipart("alternative")
        msg['Subject'] = f"Monthly Performance Report - {month_name}"
        msg['From'] = sender_email
        msg['To'] = admin_email
        msg.attach(MIMEText(html_content, 'html'))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)

        print(f"HTML Report successfully emailed to {admin_email}!")

    except Exception as e:
        print(f"Failed to send HTML email: {e}")

    return "Monthly HTML Report Complete"


@app.task(bind=True)
def generate_csv_task(self):
    print("Background Worker: Generating Master CSV...")

    try:
        si = io.StringIO()
        csv_writer = csv.writer(si)

        csv_writer.writerow([
            "Record Type", 
            "Booking ID", 
            "User Name", 
            "User Email", 
            "Trek Name", 
            "Start Date", 
            "End Date", 
            "Booking Date", 
            "Status", 
            "Seats Booked", 
            "Payment Status"
        ])

        current_bookings = db.query(Booking).all()
        for booking in current_bookings:
            user_name = f"{booking.user.first_name} {booking.user.last_name or ''}".strip() if booking.user else "Unknown User"
            user_email = booking.user.email if booking.user else "Unknown Email"
            trek_name = booking.trek.trek_name if booking.trek else "Unknown Trek"
            start_date = booking.trek.start_date.strftime('%Y-%m-%d') if booking.trek else "N/A"
            end_date = booking.trek.end_date.strftime('%Y-%m-%d') if booking.trek else "N/A"

            csv_writer.writerow([
                "CURRENT",
                booking.booking_id,               
                user_name,
                user_email,
                trek_name,
                start_date,
                end_date,
                booking.booking_date.strftime('%Y-%m-%d'),
                booking.status.name,
                booking.number_of_booking,
                "Paid" if booking.payment_status else "Pending"
            ])

        archived_bookings = db.query(BookingArchive).all()
        for booking in archived_bookings:
            user_name = f"{booking.user.first_name} {booking.user.last_name or ''}".strip() if booking.user else "Unknown User"
            user_email = booking.user.email if booking.user else "Unknown Email"
            trek_name = booking.trek.trek_name if booking.trek else "Unknown Trek"

            csv_writer.writerow([
                "ARCHIVED", 
                booking.archive_id, 
                user_name, 
                booking.user.email if booking.user else "N/A", 
                trek_name,
                booking.historical_start_date.strftime('%Y-%m-%d'),
                booking.historical_end_date.strftime('%Y-%m-%d'),
                booking.booking_date.strftime('%Y-%m-%d'), 
                booking.status.name, 
                booking.number_of_booking,
                "Paid" if booking.payment_status else "Pending"
            ])

        return si.getvalue()

    except Exception as e:
        raise ValueError(f"error: {e}")
