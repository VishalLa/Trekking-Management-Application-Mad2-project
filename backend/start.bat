@echo off
echoecho Activating virtual environment...
call myenv\Scripts\activate.bat

echo Starting Celery worker in a separate window...
start celery -A celery_app worker --loglevel=info --pool=solo

echo Starting main application...
python app.py

echo Done!
