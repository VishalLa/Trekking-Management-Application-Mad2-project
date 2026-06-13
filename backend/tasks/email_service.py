import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from celery_app import app 
from core.helper import load_env

from database.session import db_session  as db
from database.model import Booking, Trek, BookingStatus

from datetime import date, timedelta

basedir = os.path.abspath(os.path.dirname(__file__))
env_path = os.path.join(basedir, "../.env")
load_env(env_path)

@app.task(bind=True, max_retries=3)
def send_suspension_email(self, user_email: str, user_name: str):
    subject = "Important: Account Suspension and Booking Cancellation"
    body = f"Hello {user_name},\n\nYour account has been suspended. Any active trek bookings have been cancelled and refunded as per our policy."
    
    try:
        sender_email = os.environ.get("EMAIL_USER")
        sender_password = os.environ.get("EMAIL_PASS")

        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = user_email
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)

        print(f"EMAIL SENT TO: {user_email} | SUBJECT: {subject}")
        return "Activation Email Sent"

    except Exception as exc:
        print(f"Failed to send email to {user_email}: {exc}")
        raise self.retry(exc=exc, countdown=60)


@app.task(bind=True, max_retries=3)
def send_active_email(self, user_email: str, user_name: str):
    subject = "Important: Account Activation"
    body = f"Hello {user_name},\n\nYour account has been suspended. Any active trek bookings have been cancelled and refunded as per our policy."
    
    try:
        sender_email = os.environ.get("EMAIL_USER")
        sender_password = os.environ.get("EMAIL_PASS")

        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = user_email
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)

        print(f"EMAIL SENT TO: {user_email} | SUBJECT: {subject}")
        return "Activation Email Sent"

    except Exception as exc:
        print(f"Failed to send email to {user_email}: {exc}")
        raise self.retry(exc=exc, countdown=60)


@app.task(bind=True, max_retries=3)
def send_trek_cancellation_email(self, user_email: str, user_name: str, trek_name: str, refund_amount: str):
    subject = f"Urgent: {trek_name} has been cancelled"
    body = f"Hello {user_name},\n\nWe regret to inform you that {trek_name} has been cancelled. A full refund of ₹{refund_amount} has been initiated to your original payment method."
    
    try:
        sender_email = os.environ.get("EMAIL_USER")
        sender_password = os.environ.get("EMAIL_PASS")

        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = user_email
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)

        print(f"EMAIL SENT TO: {user_email} | SUBJECT: {subject}")
        return "Activation Email Sent"

    except Exception as exc:
        print(f"Failed to send email to {user_email}: {exc}")
        raise self.retry(exc=exc, countdown=60)


@app.task
def queue_daily_trek_reminder():
    today = date.today()
    five_days_from_now = today + timedelta(days=30)

    try:
        upcomming_bookings = db.query(Booking).join(Trek).filter(
            Booking.status == BookingStatus.BOOKED,
            Trek.start_date > today,
            Trek.start_date <= five_days_from_now
        ).all()

        count = 0
        for booking in upcomming_bookings:
            days_left = (booking.trek.start_date - today).days

            send_countdown_email.delay(
                user_email=booking.user.email,
                user_name=booking.user.first_name,
                trek_name=booking.trek.trek_name,
                days_left=days_left,
                location=booking.trek.location,
                start_date=booking.trek.start_date.strftime('%d %B %Y'), # e.g., 15 June 2026
                end_date=booking.trek.end_date.strftime('%d %B %Y'),
                duration=booking.trek.duration,
                trek_details=booking.trek.description
            )
            count += 1

        print(f"Scan complete! {count} countdown emails queued for delivery.")
        return f"Queued {count} reminders."

    except Exception as e:
        print(f"Database error during daily reminder scan: {e}")
        return "Scan Failed"


@app.task(bind=True, max_retries=3)
def send_countdown_email(self, user_email: str, user_name: str, trek_name: str, days_left: int, location: str, start_date: str, end_date: str, duration: int, trek_details: str):

    day_word = "day" if days_left == 1 else "days"
    subject = f"Countdown: Only {days_left} {day_word} until {trek_name}! 🏔️"

    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
        <h2 style="color: #1a6b42;">The countdown continues, {user_name}!</h2>
        <p>Your adventure to <strong>{trek_name}</strong> begins in exactly <strong>{days_left} {day_word}</strong>. It's time to finalize your packing!</p>
        
        <div style="background-color: #e7f5ee; padding: 15px; border-radius: 8px; border: 1px solid #1a6b42; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #1a6b42; border-bottom: 1px solid #a7f3d0; padding-bottom: 8px;">Trek Itinerary</h3>
            <ul style="list-style-type: none; padding: 0; margin: 0; font-size: 15px;">
                <li style="margin-bottom: 8px;">📍 <strong>Location:</strong> {location}</li>
                <li style="margin-bottom: 8px;">📅 <strong>Dates:</strong> {start_date} to {end_date}</li>
                <li style="margin-bottom: 8px;">⏳ <strong>Duration:</strong> {duration} Days</li>
            </ul>
        </div>

        <div style="background-color: #f3f4f6; padding: 15px; border-left: 4px solid #1a6b42; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #111827;">Trek Briefing:</h3>
            <p style="white-space: pre-line; margin-bottom: 0;">{trek_details}</p>
        </div>

        <p>See you on the trail very soon,<br>
        <strong>Trek Management Team</strong></p>
    </body>
    </html>
    """

    try:
        sender_email = os.environ.get("EMAIL_USER")
        sender_password = os.environ.get("EMAIL_PASS")

        msg = MIMEMultipart("alternative")
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = user_email
        msg.attach(MIMEText(html_body, 'html'))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)

        print(f"[{days_left} DAYS LEFT] EMAILED TO: {user_email} | TREK: {trek_name}")
        return "Success"

    except Exception as exc:
        print(f"Failed to send reminder to {user_email}: {exc}")
        raise self.retry(exc=exc, countdown=60)


@app.task(bind=True, max_retries=3)
def info_about_new_trek(self, user_email: str, user_name: str, trek_name: str, location: str, start_date: str, end_date: str, duration: int, trek_details: str):
    print(f"⏳ Preparing to send new trek alert to {user_email}...")
    
    subject = f"New Trek Alert! {trek_name} is now OPEN for booking 🏔️"
    
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
        <h2 style="color: #1a6b42;">Adventure awaits, {user_name}!</h2>
        <p>We are thrilled to announce that our newest trek, <strong>{trek_name}</strong>, is officially open for bookings.</p>
        
        <div style="background-color: #e7f5ee; padding: 15px; border-radius: 8px; border: 1px solid #1a6b42; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #1a6b42; border-bottom: 1px solid #a7f3d0; padding-bottom: 8px;">Trek Itinerary</h3>
            <ul style="list-style-type: none; padding: 0; margin: 0; font-size: 15px;">
                <li style="margin-bottom: 8px;">📍 <strong>Location:</strong> {location}</li>
                <li style="margin-bottom: 8px;">📅 <strong>Dates:</strong> {start_date} to {end_date}</li>
                <li style="margin-bottom: 8px;">⏳ <strong>Duration:</strong> {duration} Days</li>
            </ul>
        </div>
        
        <div style="background-color: #f3f4f6; padding: 15px; border-left: 4px solid #1a6b42; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #111827;">About the Trek:</h3>
            <p style="white-space: pre-line; margin-bottom: 0;">{trek_details}</p>
        </div>

        <p>Spots fill up quickly! Log into your dashboard now to secure your booking and start planning your next great adventure.</p>
        
        <p>Happy Trekking,<br>
        <strong>Trek Management Team</strong></p>
    </body>
    </html>
    """
    
    try:
        sender_email = os.environ.get("EMAIL_USER")
        sender_password = os.environ.get("EMAIL_PASS")

        msg = MIMEMultipart("alternative")
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = user_email
        msg.attach(MIMEText(html_body, 'html'))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)

        print(f"✅ NEW TREK ALERT EMAILED TO: {user_email} | TREK: {trek_name}")
        return "Success"

    except Exception as exc:
        print(f"❌ Failed to send new trek alert to {user_email}: {exc}")
        raise self.retry(exc=exc, countdown=60)
    