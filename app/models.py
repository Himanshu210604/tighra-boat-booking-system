from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="tourist")  # tourist, operator, admin
    created_at = Column(DateTime, default=datetime.utcnow)

    bookings = relationship("Booking", back_populates="user", foreign_keys="Booking.user_id")

class Boat(Base):
    __tablename__ = "boats"

    id = Column(Integer, primary_key=True, index=True)
    boat_name = Column(String, nullable=False)
    boat_type = Column(String, nullable=False)  # Motor Boat, Speed Boat, Shikara, Paddle Boat
    capacity = Column(Integer, nullable=False)
    price_per_person = Column(Float, nullable=False)
    status = Column(String, default="active")  # active, maintenance
    description = Column(String, nullable=True)
    image_url = Column(String, nullable=True)

    bookings = relationship("Booking", back_populates="boat")

class TimeSlot(Base):
    __tablename__ = "time_slots"

    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(String, nullable=False)  # "09:00 AM"
    end_time = Column(String, nullable=False)    # "10:00 AM"
    max_capacity = Column(Integer, default=50)
    is_active = Column(Boolean, default=True)

    bookings = relationship("Booking", back_populates="slot")

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    booking_ref = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    boat_id = Column(Integer, ForeignKey("boats.id"), nullable=False)
    slot_id = Column(Integer, ForeignKey("time_slots.id"), nullable=False)
    booking_date = Column(String, nullable=False)  # YYYY-MM-DD
    passenger_count = Column(Integer, nullable=False, default=1)
    total_amount = Column(Float, nullable=False)
    payment_status = Column(String, default="PAID")  # PENDING, PAID, REFUNDED
    booking_status = Column(String, default="CONFIRMED")  # CONFIRMED, CANCELLED, USED
    qr_token = Column(String, unique=True, index=True, nullable=False)
    scanned_at = Column(DateTime, nullable=True)
    scanned_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="bookings", foreign_keys=[user_id])
    boat = relationship("Boat", back_populates="bookings")
    slot = relationship("TimeSlot", back_populates="bookings")
    payments = relationship("Payment", back_populates="booking")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    transaction_id = Column(String, unique=True, nullable=False)
    gateway = Column(String, default="Razorpay Test Sandbox")
    amount = Column(Float, nullable=False)
    payment_status = Column(String, default="SUCCESS")
    created_at = Column(DateTime, default=datetime.utcnow)

    booking = relationship("Booking", back_populates="payments")
