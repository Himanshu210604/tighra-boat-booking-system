import uuid
import base64
import io
import qrcode
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.booking import Boat, Booking, Payment
from app.schemas.booking import BoatResponse, BookingCreate, BookingResponse, VerifyQRRequest
from app.api.auth import get_current_user

router = APIRouter(prefix="/bookings", tags=["Bookings & Payments"])

def generate_qr_base64(ticket_data: str) -> str:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )
    qr.add_data(ticket_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="#0f172a", back_color="#ffffff")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_bytes = buffer.getvalue()
    base64_str = base64.b64encode(qr_bytes).decode("utf-8")
    return f"data:image/png;base64,{base64_str}"

@router.get("/boats", response_model=List[BoatResponse])
def get_boats(db: Session = Depends(get_db)):
    boats = db.query(Boat).all()
    if not boats:
        # Initial fallback boats
        default_boats = [
            Boat(name="Speed Boat Express", boat_type="Speed Boat", capacity=6, price_per_seat=400.0, image_url="assets/speed_boat.png"),
            Boat(name="Family Paddle Boat", boat_type="Paddle Boat", capacity=4, price_per_seat=250.0, image_url="assets/real_tighra_lake_boats.jpg"),
            Boat(name="Tighra Dam Scenic Cruise", boat_type="Cruise", capacity=30, price_per_seat=150.0, image_url="assets/real_tighra_dam_wall.jpg")
        ]
        db.add_all(default_boats)
        db.commit()
        boats = db.query(Boat).all()
    return boats

@router.post("/create", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    booking_in: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Lookup boat for price verification
    boat = db.query(Boat).filter(Boat.name == booking_in.boat_name).first()
    price = boat.price_per_seat if boat else 300.0
    total_amount = price * booking_in.passengers

    # Generate unique ticket & transaction ID
    ticket_num = f"TIGH-{uuid.uuid4().hex[:8].upper()}"
    tx_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"

    # Generate Valid Base64 QR Code
    qr_payload = f"TIGHRA_TICKET:{ticket_num}|USER:{current_user.email}|DATE:{booking_in.booking_date}|SLOT:{booking_in.time_slot}|PASSENGERS:{booking_in.passengers}"
    qr_b64 = generate_qr_base64(qr_payload)

    # Save Booking record
    db_booking = Booking(
        ticket_number=ticket_num,
        user_id=current_user.id,
        boat_name=booking_in.boat_name,
        booking_date=booking_in.booking_date,
        time_slot=booking_in.time_slot,
        passengers=booking_in.passengers,
        total_amount=total_amount,
        payment_status="SUCCESS",
        booking_status="VALID",
        qr_code_base64=qr_b64
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)

    # Save Payment record
    db_payment = Payment(
        booking_id=db_booking.id,
        transaction_id=tx_id,
        amount=total_amount,
        payment_method=booking_in.payment_method or "Razorpay (UPI/Card)",
        payment_status="SUCCESS"
    )
    db.add(db_payment)
    db.commit()

    return db_booking

@router.get("/my-tickets", response_model=List[BookingResponse])
def get_my_tickets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tickets = db.query(Booking).filter(Booking.user_id == current_user.id).order_by(Booking.id.desc()).all()
    return tickets

@router.post("/verify-qr")
def verify_qr_code(
    verify_req: VerifyQRRequest,
    db: Session = Depends(get_db)
):
    booking = db.query(Booking).filter(Booking.ticket_number == verify_req.ticket_number).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="INVALID TICKET: Ticket number not found in Tighra Dam system."
        )

    if booking.booking_status == "USED":
        return {
            "status": "REJECTED",
            "message": f"TICKET ALREADY USED: Ticket {booking.ticket_number} was already scanned at entry gate.",
            "ticket": booking
        }

    if booking.booking_status == "CANCELLED":
        return {
            "status": "REJECTED",
            "message": f"CANCELLED TICKET: Ticket {booking.ticket_number} was cancelled.",
            "ticket": booking
        }

    # Mark ticket as USED
    booking.booking_status = "USED"
    db.commit()

    return {
        "status": "VERIFIED",
        "message": f"VALID TICKET: Entry granted for {booking.passengers} passenger(s) on {booking.boat_name}.",
        "ticket": booking
    }
