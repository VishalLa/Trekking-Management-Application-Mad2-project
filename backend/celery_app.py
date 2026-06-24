from celery import Celery
from celery.schedules import crontab

import os 
from core.helper import load_env
# basedir = os.path.abspath(os.path.dirname(__file__))

# env_path = os.path.join(basedir, "../.env")
load_env(".env")

app = Celery(
    'xyz',
    broker=os.environ.get("REDIS_URL"),  # where tasks are stored 
    backend=os.environ.get("REDIS_URL"),  # where results are stored
    include=[
        'tasks.admin_tasks',
        'tasks.email_service',
        'tasks.trek_task',
        "tasks.task",
        "tasks.trekker_tasks"
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
        # "schedule": crontab(minute="*"),
    },

    "daily-trek-auto-close": {
        'task': 'tasks.auto_close_past_due_treks',
        'schedule': crontab(hour=0, minute=1),
        # "schedule": crontab(minute="*")
    }
}
