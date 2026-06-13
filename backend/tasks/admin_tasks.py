import os
import smtplib # simple mail transfer protocol 

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date

from celery_app import app 
from service.report_service import ReportService
from core.helper import load_env

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

