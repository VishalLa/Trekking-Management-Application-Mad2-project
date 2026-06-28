@echo off
echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Starting Celery worker in a separate window...
start celery -A celery_app worker --loglevel=info --pool=solo

echo Starting main application...
python app.py

echo Done!
