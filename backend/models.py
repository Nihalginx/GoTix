"""
backend/models.py - SQLAlchemy ORM Models
Defines tables: users, login_logs, trips, bookings.
Includes relationships and serialization helper methods.
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from backend.database import Base


def utcnow():
    """Returns current UTC datetime without deprecation warning."""
    return datetime.now(timezone.utc)


class User(Base):
    """
    Users table storing credentials, display name, and role ('user' or 'admin').
    Passwords are stored as bcrypt hashes; never returned in API responses.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="user", nullable=False)  # 'user' or 'admin'
    created_at = Column(DateTime, default=utcnow, nullable=False)

    # Relationships
    bookings = relationship("Booking", back_populates="user", cascade="all, delete-orphan")
    login_logs = relationship("LoginLog", back_populates="user")

    def to_dict(self):
        """Safe dictionary representation excluding password_hash."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None
        }


class LoginLog(Base):
    """
    Audit log of every authentication attempt (both successful and failed).
    Used directly in the Admin Database Monitor.
    """
    __tablename__ = "login_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    email_tried = Column(String(120), nullable=False, index=True)
    login_time = Column(DateTime, default=utcnow, nullable=False, index=True)
    ip_address = Column(String(45), nullable=False, default="127.0.0.1")
    status = Column(String(20), nullable=False)  # 'success' or 'failed'

    # Relationships
    user = relationship("User", back_populates="login_logs")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "email_tried": self.email_tried,
            "login_time": self.login_time.strftime("%Y-%m-%d %H:%M:%S") if self.login_time else None,
            "ip_address": self.ip_address,
            "status": self.status,
            "user_name": self.user.name if self.user else None
        }


class Trip(Base):
    """
    Trips table supporting 5 transport types: flight, bus, cab, bike, train.
    Tracks real-time seats_available which decrements upon booking and increments on cancellation.
    """
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    transport_type = Column(String(20), nullable=False, index=True)  # flight, bus, cab, bike, train
    operator = Column(String(100), nullable=False)
    origin = Column(String(100), nullable=False, index=True)
    destination = Column(String(100), nullable=False, index=True)
    departure_time = Column(DateTime, nullable=False, index=True)
    arrival_time = Column(DateTime, nullable=False)
    price = Column(Float, nullable=False)
    seats_total = Column(Integer, nullable=False)
    seats_available = Column(Integer, nullable=False)

    # Relationships
    bookings = relationship("Booking", back_populates="trip", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "transport_type": self.transport_type,
            "operator": self.operator,
            "origin": self.origin,
            "destination": self.destination,
            "departure_time": self.departure_time.strftime("%Y-%m-%d %H:%M") if self.departure_time else None,
            "arrival_time": self.arrival_time.strftime("%Y-%m-%d %H:%M") if self.arrival_time else None,
            "price": self.price,
            "seats_total": self.seats_total,
            "seats_available": self.seats_available,
            "occupancy_percent": round(((self.seats_total - self.seats_available) / self.seats_total) * 100, 1) if self.seats_total > 0 else 0
        }


class Booking(Base):
    """
    Bookings table recording ticket purchases.
    Status transitions from 'confirmed' to 'cancelled'.
    """
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, index=True)
    passenger_names = Column(Text, nullable=False)  # JSON or comma-separated names
    seats_booked = Column(Integer, nullable=False, default=1)
    total_price = Column(Float, nullable=False)
    status = Column(String(20), nullable=False, default="confirmed")  # 'confirmed' or 'cancelled'
    booked_at = Column(DateTime, default=utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="bookings")
    trip = relationship("Trip", back_populates="bookings")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "trip_id": self.trip_id,
            "passenger_names": self.passenger_names,
            "seats_booked": self.seats_booked,
            "total_price": self.total_price,
            "status": self.status,
            "booked_at": self.booked_at.strftime("%Y-%m-%d %H:%M:%S") if self.booked_at else None,
            "user_name": self.user.name if self.user else None,
            "user_email": self.user.email if self.user else None,
            "trip": self.trip.to_dict() if self.trip else None
        }
