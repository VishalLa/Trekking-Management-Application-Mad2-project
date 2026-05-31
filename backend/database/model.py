import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    String, 
    Integer, 
    Boolean,
    Date,
    ForeignKey,
    Table,
    UniqueConstraint 
)

from sqlalchemy.orm import relationship
from .base import Base
from core.security import hash_password, verify_password


# ASSOCIATION TABLE (StaffProfile <-> Trek)
staff_trek_association = Table(
    "staff_trek",
    Base.metadata,
    Column("staff_id", String(36), ForeignKey("staff_profiles.user_id", ondelete="CASCADE"), primary_key=True),
    Column("trek_id", String(36), ForeignKey("trek.trek_id", ondelete="CASCADE"), primary_key=True)
)


class User(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    role = Column(String(20), nullable=False)   # Admin, Trekker, Staff
    email = Column(String(128), nullable=False, unique=True)
    password_hash = Column(String(240), nullable=False)

    staff_profile = relationship('StaffProfile', back_populates='user_account', uselist=False, cascade="all, delete-orphan")
    trekker_profile = relationship('TrekkerProfile', back_populates='user_account', uselist=False, cascade="all, delete-orphan")
    bookings = relationship('Booking', back_populates='user', lazy=True)

    def set_password(self, password: str) -> None:
        self.password_hash = hash_password(password)

    def check_password(self, password: str) -> bool:
        return verify_password(hashed_password=self.password_hash, plain_password=password)


class TrekkerProfile(Base):
    __tablename__ = 'trekker_profiles'
    user_id = Column(String(36), ForeignKey('users.id'), primary_key=True, nullable=False) 
    
    first_name = Column(String(36), nullable=False)
    last_name = Column(String(36))
    phone_no = Column(String(15), nullable=False)

    user_account = relationship("User", back_populates="trekker_profile")


class StaffProfile(Base):
    __tablename__ = 'staff_profiles'
    user_id = Column(String(36), ForeignKey('users.id'), primary_key=True , nullable=False)
    
    first_name = Column(String(36), nullable=False)
    last_name = Column(String(36))
    phone_no = Column(String(15), nullable=False)
    status = Column(Boolean, nullable=False)

    user_account = relationship("User", back_populates="staff_profile")
    assigned_treks = relationship('Trek', secondary=staff_trek_association, back_populates='assigned_staff')


class Trek(Base):
    __tablename__ = "trek"
    trek_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    trek_name = Column(String(128), nullable=False, unique=True, index=True)
    location = Column(String(128), nullable=False)
    duration = Column(Integer, nullable=False)
    available_slots = Column(Integer, nullable=False)
    status = Column(String(15), nullable=False)     # (Pending / Approved / Open / Closed / Completed)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    assigned_staff = relationship("StaffProfile", secondary=staff_trek_association, back_populates="assigned_treks")
    bookings = relationship('Booking', back_populates='trek', lazy=True)


class Booking(Base):
    __tablename__ = "booking"
    booking_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    user_id = Column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    trek_id = Column(String(36), ForeignKey("trek.trek_id"), index=True, nullable=False)
    
    booking_date = Column(Date, nullable=False)
    status = Column(String(20), nullable=False)
    payment_status = Column(Boolean, nullable=False)

    user = relationship("User", back_populates="bookings")
    trek = relationship("Trek", back_populates="bookings")

    __table_args__ = (
        UniqueConstraint('user_id', 'trek_id', name='_user_trek_uc'),
    )
