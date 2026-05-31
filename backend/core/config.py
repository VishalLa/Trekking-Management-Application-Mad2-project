import os 
from .helper import load_env
basedir = os.path.abspath(os.path.dirname(__file__))

env_path = os.path.join(basedir, "../.env")
load_env(env_path)

class Config():
    DEBUG = False

    SQLITE_DB_DIR = os.path.join(basedir, "../db")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(SQLITE_DB_DIR, "trekking.sqlite3")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")

    os.makedirs(SQLITE_DB_DIR, exist_ok=True)
    API_BASE = None
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SCHEDULER_API_ENABLED = True
    LOG_FILE = 'debug.log'
    LOG_FORMAT = '%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'

class LocalDevelopmentConfig(Config) :
    SQLITE_DB_DIR = os.path.join(basedir, "../db")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(SQLITE_DB_DIR, "test.sqlite3")
    DEBUG = True
    API_BASE = os.environ.get("API_BASE")
    API_SERVER_URL = os.environ.get("API_SERVER_URL")
