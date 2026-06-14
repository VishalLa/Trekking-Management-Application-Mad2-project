from celery import Celery
from celery.schedules import crontab


app = Celery(
    'xyz',
    broker='redis://localhost:6379/0',  # where tasks are stored 
    backend='redis://localhost:6379/0',  # where results are stored
    include=[
        'tasks.admin_tasks',
        'tasks.email_service',
        'tasks.trek_task'
    ]
)

app.conf.timezone = 'Asia/Kolkata'

app.conf.beat_schedule = {
    "send-monthly-admin-report": {
        "task": "tasks.admin_tasks.generate_monthly_report", 
        "schedule": crontab(hour=6, minute=0, day_of_month=1), 
        "args": ("vishalladoiya66@gmail.com",) 
    },

    "daily-trek-countdown-scanner": {
        "task": "tasks.queue_daily_trek_reminders","tasks.queue_daily_trek_reminder"
        "schedule": crontab(hour=8, minute=0),
        "schedule": crontab(minute="*"),
    }
}
