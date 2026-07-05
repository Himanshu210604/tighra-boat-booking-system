from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Boat(Base):
    __tablename__ = "boats"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    boat_type = Column(String(50), nullable=False)
    capacity = Column(Integer, nullable=False)
    price_per_seat = Column(Float, nullable=False)
    image_url = Column(String(255), nullable=True)

class TimeSlot(Base):
    __tablename__ = "time_slots"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    boat_id = Column(Integer, ForeignKey("boats.id"), nullable=False)
    start_time = Column(String(20), nullable=False)
    end_time = Column(String(20), nullable=False)
    max_capacity = Column(Integer, nullable=False)

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ticket_number = Column(String(50), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    boat_name = Column(String(100), nullable=False)
    booking_date = Column(String(20), nullable=False)
    time_slot = Column(String(50), nullable=False)
    passengers = Column(Integer, nullable=False, default=1)
    total_amount = Column(Float, nullable=False)
    payment_status = Column(String(20), default="SUCCESS")  # PENDING, SUCCESS, FAILED
    booking_status = Column(String(20), default="VALID")   # VALID, USED, CANCELLED
    qr_code_base64 = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    transaction_id = Column(String(100), unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=False)  # UPI, Razorpay, Card, NetBanking
    payment_status = Column(String(20), default="SUCCESS")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
