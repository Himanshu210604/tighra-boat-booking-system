import io
import uuid
import qrcode
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.database import get_db
from app.models import Booking, Boat, TimeSlot, Payment, User
from app.schemas import BookingCreate, BookingResponse
from app.auth import get_current_user
from app.config import settings

router = APIRouter(prefix="/api/bookings", tags=["Bookings & Payments"])

@router.post("", response_model=BookingResponse)
def create_booking(booking_data: BookingCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 1. Validate Boat
    boat = db.query(Boat).filter(Boat.id == booking_data.boat_id, Boat.status == "active").first()
    if not boat:
        raise HTTPException(status_code=404, detail="Boat not found or currently under maintenance")

    # 2. Validate Slot
    slot = db.query(TimeSlot).filter(TimeSlot.id == booking_data.slot_id, TimeSlot.is_active == True).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Time slot not found or inactive")

    # 3. Check Capacity
    current_booked = db.query(func.sum(Booking.passenger_count)).filter(
        Booking.boat_id == boat.id,
        Booking.slot_id == slot.id,
        Booking.booking_date == booking_data.booking_date,
        Booking.booking_status != "CANCELLED"
    ).scalar() or 0

    available_seats = min(boat.capacity, slot.max_capacity) - current_booked
    if booking_data.passenger_count > available_seats:
        raise HTTPException(status_code=400, detail=f"Insufficient seats available. Only {available_seats} remaining for this slot.")

    # 4. Calculate Price & Generate Tokens
    total_price = boat.price_per_person * booking_data.passenger_count
    booking_ref = f"TIGHRA-{uuid.uuid4().hex[:8].upper()}"
    qr_token = f"TGH-QR-{uuid.uuid4().hex[:12].upper()}"

    # 5. Create Booking Record
    new_booking = Booking(
        booking_ref=booking_ref,
        user_id=current_user.id,
        boat_id=boat.id,
        slot_id=slot.id,
        booking_date=booking_data.booking_date,
        passenger_count=booking_data.passenger_count,
        total_amount=total_price,
        payment_status="PAID",
        booking_status="CONFIRMED",
        qr_token=qr_token
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    # 6. Record Payment (Razorpay Test Mode simulation)
    payment = Payment(
        booking_id=new_booking.id,
        transaction_id=f"pay_rzp_{uuid.uuid4().hex[:10]}",
        gateway="Razorpay Test Gateway",
        amount=total_price,
        payment_status="SUCCESS"
    )
    db.add(payment)
    db.commit()

    return new_booking

@router.get("/my", response_model=List[BookingResponse])
def get_my_bookings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    bookings = db.query(Booking).filter(Booking.user_id == current_user.id).order_by(Booking.created_at.desc()).all()
    return bookings

@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking_detail(booking_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.user_id != current_user.id and current_user.role not in ["admin", "operator"]:
        raise HTTPException(status_code=403, detail="Unauthorized access to this booking")
    return booking

@router.post("/{booking_id}/cancel", response_model=BookingResponse)
def cancel_booking(booking_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Unauthorized to cancel this booking")
    if booking.booking_status == "USED":
        raise HTTPException(status_code=400, detail="Cannot cancel a ticket that has already been scanned/used")
    if booking.booking_status == "CANCELLED":
        raise HTTPException(status_code=400, detail="Booking is already cancelled")

    booking.booking_status = "CANCELLED"
    booking.payment_status = "REFUNDED"
    db.commit()
    db.refresh(booking)
    return booking

@router.get("/{booking_id}/qr-image")
def get_booking_qr_image(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Generate QR Code PNG
    qr_content = booking.qr_token
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )
    qr.add_data(qr_content)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#0F172A", back_color="#FFFFFF")
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    return Response(content=img_byte_arr.getvalue(), media_type="image/png")
