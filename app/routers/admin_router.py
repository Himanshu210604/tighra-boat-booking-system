from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app.database import get_db
from app.models import Booking, Boat, TimeSlot, User, Payment
from app.schemas import AnalyticsResponse, BookingResponse, UserResponse
from app.auth import require_role

router = APIRouter(prefix="/api/admin", tags=["Admin Dashboard & Analytics"])

@router.get("/analytics", response_model=AnalyticsResponse)
def get_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    total_rev = db.query(func.sum(Booking.total_amount)).filter(
        Booking.payment_status == "PAID",
        Booking.booking_status != "CANCELLED"
    ).scalar() or 0.0

    total_bks = db.query(func.count(Booking.id)).scalar() or 0

    active_bts = db.query(func.count(Boat.id)).filter(Boat.status == "active").scalar() or 0

    today_passengers = db.query(func.sum(Booking.passenger_count)).filter(
        Booking.payment_status == "PAID",
        Booking.booking_status != "CANCELLED"
    ).scalar() or 0

    recent_bookings = db.query(Booking).order_by(Booking.created_at.desc()).limit(10).all()

    return AnalyticsResponse(
        total_revenue=float(total_rev),
        total_bookings=total_bks,
        active_boats=active_bts,
        today_passengers=today_passengers,
        recent_bookings=recent_bookings
    )

@router.get("/bookings", response_model=List[BookingResponse])
def list_all_bookings(
    status: Optional[str] = None,
    boat_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    query = db.query(Booking)
    if status:
        query = query.filter(Booking.booking_status == status)
    if boat_id:
        query = query.filter(Booking.boat_id == boat_id)
    if search:
        query = query.filter(
            (Booking.booking_ref.contains(search)) |
            (Booking.qr_token.contains(search))
        )
    return query.order_by(Booking.created_at.desc()).all()

@router.get("/users", response_model=List[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    return db.query(User).order_by(User.id.asc()).all()

@router.post("/boats/{boat_id}/status")
def toggle_boat_status(
    boat_id: int,
    status_val: str = Query(..., description="active or maintenance"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    boat = db.query(Boat).filter(Boat.id == boat_id).first()
    if not boat:
        raise HTTPException(status_code=404, detail="Boat not found")
    
    boat.status = status_val
    db.commit()
    return {"message": f"Boat '{boat.boat_name}' status updated to {status_val}", "boat_id": boat_id, "new_status": status_val}
