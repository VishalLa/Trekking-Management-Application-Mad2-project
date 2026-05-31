import logging 
import logging.handlers 

from flask import Flask
from flask_jwt_extended import JWTManager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from core.config import LocalDevelopmentConfig, Config
from database.model import User 
from database.base import Base

from api import admin_rotue
from auth import register, auth

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

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)


def init_db():
    engine = create_engine(
        Config.SQLALCHEMY_DATABASE_URI,
        echo=True
    )

    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

    with Session(engine) as session:
        admin_exists = session.query(User).filter_by(role="Admin").first()

        if not admin_exists:
            print("No admin found. Creating default admin...")
            
            default_admin = User(
                role="Admin",
                email="admin@tma.com"
            )
            default_admin.set_password("Admin@1234")
            
            session.add(default_admin)
            session.commit()
            print("Default Admin created successfully!")
        else:
            print("Admin account already exists. Skipping creation.")


def create_app():
    app = Flask(__name__)
    app.config.from_object(LocalDevelopmentConfig)

    app.register_blueprint(auth.login_bp)
    app.register_blueprint(register.auth_bp)
    app.register_blueprint(admin_rotue.admin_bp)

    app.config["JWT_SECRET_KEY"] = "your-super-secret-capstone-key"
    jwt = JWTManager(app)

    with app.app_context():
        init_db()
        
    return app

if __name__ == '__main__':
    app = create_app()
    @app.route("/")
    def home(): 
        return "Hello"
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=True)  
