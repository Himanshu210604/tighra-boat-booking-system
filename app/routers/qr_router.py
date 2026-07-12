from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Booking, User
from app.schemas import VerifyQRRequest, VerifyQRResponse, BookingResponse
from app.auth import get_current_user, require_role

router = APIRouter(prefix="/api/verify-qr", tags=["QR Verification & Gate Scanner"])

@router.post("", response_model=VerifyQRResponse)
def verify_qr_code(
    payload: VerifyQRRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["operator", "admin"]))
):
    token = payload.qr_token.strip()
    booking = db.query(Booking).filter(Booking.qr_token == token).first()

    if not booking:
        # Try matching booking reference as fallback
        booking = db.query(Booking).filter(Booking.booking_ref == token).first()

    if not booking:
        return VerifyQRResponse(
            success=False,
            message="❌ INVALID TICKET: QR code or Booking Reference not found in database.",
            booking=None
        )

    if booking.payment_status != "PAID":
        return VerifyQRResponse(
            success=False,
            message=f"❌ UNPAID TICKET: Payment status is {booking.payment_status}.",
            booking=booking
        )

    if booking.booking_status == "CANCELLED":
        return VerifyQRResponse(
            success=False,
            message="❌ CANCELLED TICKET: This booking has been cancelled and refunded.",
            booking=booking
        )

    if booking.booking_status == "USED" or booking.scanned_at is not None:
        scanned_time = booking.scanned_at.strftime("%I:%M %p, %d %b %Y") if booking.scanned_at else "Earlier"
        return VerifyQRResponse(
            success=False,
            message=f"⚠️ DUPLICATE TICKET WARNING: Ticket already used/scanned on {scanned_time}.",
            booking=booking
        )

    # Valid ticket! Mark as USED and record scan timestamp
    booking.booking_status = "USED"
    booking.scanned_at = datetime.utcnow()
    booking.scanned_by_id = current_user.id
    db.commit()
    db.refresh(booking)

    return VerifyQRResponse(
        success=True,
        message=f"✅ VERIFIED ENTRY GRANTED! {booking.passenger_count} Passenger(s) - {booking.boat.boat_name} ({booking.slot.start_time} - {booking.slot.end_time})",
        booking=booking
    )

@router.get("/summary")
def get_operator_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["operator", "admin"]))
):
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    
    total_scanned = db.query(func.count(Booking.id)).filter(
        Booking.booking_status == "USED"
    ).scalar() or 0

    passengers_boarded = db.query(func.sum(Booking.passenger_count)).filter(
        Booking.booking_status == "USED"
    ).scalar() or 0

    recent_scans = db.query(Booking).filter(
        Booking.booking_status == "USED"
    ).order_by(Booking.scanned_at.desc()).limit(10).all()

    return {
        "operator_name": current_user.name,
        "total_tickets_scanned": total_scanned,
        "total_passengers_boarded": passengers_boarded,
        "recent_scans": recent_scans
    }
