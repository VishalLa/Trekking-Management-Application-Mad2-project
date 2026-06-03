import uuid
import enum
from datetime import datetime

from sqlalchemy import (
    Column,
    String, 
    Integer,
    Float, 
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Table,
    UniqueConstraint,
    Text,
    Enum as SQLEnum
)

from sqlalchemy.orm import relationship
from .base import Base
from core.security import hash_password, verify_password
from core.helper import IndiaTimeStampNow


# ASSOCIATION TABLE (StaffProfile <-> Trek)
staff_trek_association = Table(
    "staff_trek",
    Base.metadata,
    Column("staff_id", String(36), ForeignKey("staff_profiles.user_id", ondelete="CASCADE"), primary_key=True),
    Column("trek_id", String(36), ForeignKey("trek.trek_id", ondelete="CASCADE"), primary_key=True)
)

class Status(enum.Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"

class Role(enum.Enum):
    ADMIN = "ADMIN"
    STAFF = "STAFF"
    TREKKER = "TREKKER"

class TrekStatus(enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    COMPLETE = "COMPLETE"

class TrekDifficulty(enum.Enum):
    EASY = "EASY" 
    MEDIUM = "MEDIUM"
    HARD = "HARD"

class BookingStatus(enum.Enum):
    BOOKED = "BOOKED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"


class User(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    role = Column(SQLEnum(Role), nullable=False)   
    email = Column(String(128), nullable=False, unique=True)
    password_hash = Column(String(240), nullable=False)

    first_name = Column(String(36), nullable=False)
    last_name = Column(String(36))

    phone_no = Column(String(15), nullable=False)
    address = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    gender = Column(String(10), nullable=True)
    dob = Column(Date, nullable=True)
    profile_picture = Column(String(255), nullable=True, default="default.jpg")

    status = Column(SQLEnum(Status), nullable=False, default=Status.ACTIVE)

    date_created = Column(DateTime, default=lambda: IndiaTimeStampNow())
    last_login = Column(Integer)

    staff_profile = relationship('StaffProfile', back_populates='user_account', uselist=False, cascade="all, delete-orphan")
    trekker_profile = relationship('TrekkerProfile', back_populates='user_account', uselist=False, cascade="all, delete-orphan")
    bookings = relationship('Booking', back_populates='user', lazy=True)

    def __init__(self, password=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if password:
            self.set_password(password=password)

    def set_password(self, password: str) -> None:
        self.password_hash = hash_password(password)

    def check_password(self, password: str) -> bool:
        return verify_password(hashed_password=self.password_hash, plain_password=password)


class TrekkerProfile(Base):
    __tablename__ = 'trekker_profiles'
    user_id = Column(String(36), ForeignKey('users.id'), primary_key=True, nullable=False) 
    email_verified = Column(Boolean, default=False)
    user_account = relationship("User", back_populates="trekker_profile")


class StaffProfile(Base):
    __tablename__ = 'staff_profiles'
    user_id = Column(String(36), ForeignKey('users.id'), primary_key=True , nullable=False)
    experience = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    user_account = relationship("User", back_populates="staff_profile")
    assigned_treks = relationship('Trek', secondary=staff_trek_association, back_populates='assigned_staff')


class Trek(Base):
    __tablename__ = "trek"
    trek_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    trek_name = Column(String(128), nullable=False, unique=True, index=True)
    location = Column(String(128), nullable=False)
    duration = Column(Integer, nullable=False)
    available_slots = Column(Integer, nullable=False)
    
    status = Column(SQLEnum(TrekStatus), nullable=False, default=TrekStatus.PENDING)    
    difficulty = Column(SQLEnum(TrekDifficulty), nullable=False) 

    price = Column(Float, nullable=False, default=0.0)  

    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    date_created = Column(DateTime, default=lambda: IndiaTimeStampNow())
    description = Column(Text, nullable=True)
    
    assigned_staff = relationship("StaffProfile", secondary=staff_trek_association, back_populates="assigned_treks")
    bookings = relationship('Booking', back_populates='trek', lazy=True)


class Booking(Base):
    __tablename__ = "booking"
    booking_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    user_id = Column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    trek_id = Column(String(36), ForeignKey("trek.trek_id"), index=True, nullable=False)
    
    booking_date = Column(Date, nullable=False)
    status = Column(SQLEnum(BookingStatus), nullable=False)
    number_of_booking = Column(Integer, nullable=False)
    payment_status = Column(Boolean, nullable=False, default=False)

    user = relationship("User", back_populates="bookings")
    trek = relationship("Trek", back_populates="bookings")

    __table_args__ = (
        UniqueConstraint('user_id', 'trek_id', name='_user_trek_uc'),
    )
