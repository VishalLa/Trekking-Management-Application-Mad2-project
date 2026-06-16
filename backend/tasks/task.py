from celery_app import app
from datetime import date, datetime
from database.session import db_session as db 
from database.model import Trek, TrekStatus

@app.task
def auto_close_past_due_treks():
    today = date.today()
    # today = datetime.now().date()

    overdue_treks = db.query(Trek).filter(
        Trek.status == TrekStatus.OPEN,
        Trek.start_date >= today
    ).all()

    count = 0 
    for trek in overdue_treks:
        trek.status = TrekStatus.COMPLETE
        count += 1

    try:
        if count > 0:
            db.commit()
            print(f"[Celery] Successfully complete {count} overdue treks.")
        else:
            print("[Celery] No overdue treks found today.")
            
    except Exception as e:
        db.rollback()
        print(f"[Celery Error] Failed to complete treks: {e}")
        
    return f"Processed {count} overdue treks."
