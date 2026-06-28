#!/bin/bash

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Starting Celery worker in the background..."
celery -A celery_app worker --loglevel=info

echo "Starting main application..."
python app.py

echo "Done!"
