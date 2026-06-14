import os
import multiprocessing

import logging 
import logging.handlers 

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from core.config import LocalDevelopmentConfig, Config
from database.model import User, Role
from database.base import Base

from api import admin_rotue
from auth import auth

from celery_app import app as celery_app

LOG_FORMAT = Config.LOG_FORMAT
LOG_FILE = Config.LOG_FILE

formatter = logging.Formatter(LOG_FORMAT)

handler = logging.handlers.TimedRotatingFileHandler(
    LOG_FILE, 
    when='D',
    interval=1,
    backupCount=2
)

handler.setFormatter(formatter)

# logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)
# logger.addHandler(handler)


def init_db():
    engine = create_engine(
        Config.SQLALCHEMY_DATABASE_URI,
        echo=True
    )

    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

    with Session(engine) as session:
        admin_exists = session.query(User).filter_by(role=Role.ADMIN).first()

        if not admin_exists:
            print("No admin found. Creating default admin...")

            default_admin = User(
                role=Role.ADMIN,
                email="admin@tma.com",
                first_name="Super",
                last_name="Admin",
                phone_no="0000000000",
                password="Admin@1234"
            )
            
            session.add(default_admin)
            session.commit()
            print("Default Admin created successfully!")
        else:
            print("Admin account already exists. Skipping creation.")


def run_celery_worker():
    worker_args = ["worker", "--loglevel=info"]

    if os.name == "nt":
        worker_args.append("--pool=solo")
        print("WARNING: Running on Windows. You must start Celery Beat in a separate terminal!")
    else:
        worker_args.append("-B")
    
    celery_app.worker_main(worker_args)

def create_app():
    app = Flask(__name__)
    CORS(app, expose_headers=["Content-Disposition"])
    app.config.from_object(LocalDevelopmentConfig)

    app.register_blueprint(auth.auth_bp)
    app.register_blueprint(admin_rotue.admin_bp)

    app.config["JWT_SECRET_KEY"] = Config.JWT_SECRET_KEY
    _ = JWTManager(app)

    with app.app_context():
        init_db()
        
    return app

if __name__ == '__main__':

    celery_process = multiprocessing.Process(target=run_celery_worker)
    celery_process.daemon = True
    celery_process.start()

    app = create_app()
    app.run(host='0.0.0.0', port=8000, debug=True, use_reloader=False)  
