from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker, scoped_session
from core.config import Config 

engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URI,
    echo=False
)

session_factory = sessionmaker(bind=engine)
# Thread-Local "singleton" (The Scoped Session)
db_session = scoped_session(session_factory)
