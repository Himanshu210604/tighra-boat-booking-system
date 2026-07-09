from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from app.database import get_db
from app.models.user import User
from app.models.booking import Boat, Booking, Payment
from app.schemas.user import UserResponse
from app.schemas.booking import BoatResponse, BookingResponse
from app.api.auth import get_current_user

router = APIRouter(prefix="/admin", tags=["Admin Management"])

def verify_admin_role(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ADMIN ACCESS REQUIRED: Only administrators can access this portal."
        )
    return current_user

@router.get("/stats")
def get_admin_dashboard_stats(
    admin: User = Depends(verify_admin_role),
    db: Session = Depends(get_db)
):
    total_users = db.query(User).count()
    total_bookings = db.query(Booking).count()
    total_boats = db.query(Boat).count()
    
    total_revenue = db.query(func.sum(Booking.total_amount)).filter(
        Booking.payment_status == "SUCCESS"
    ).scalar() or 0.0

    valid_bookings = db.query(Booking).filter(Booking.booking_status == "VALID").count()
    used_bookings = db.query(Booking).filter(Booking.booking_status == "USED").count()

    return {
        "total_revenue": round(total_revenue, 2),
        "total_bookings": total_bookings,
        "total_users": total_users,
        "total_boats": total_boats,
        "valid_bookings": valid_bookings,
        "used_bookings": used_bookings
    }

@router.get("/bookings", response_model=List[BookingResponse])
def get_all_bookings(
    admin: User = Depends(verify_admin_role),
    db: Session = Depends(get_db)
):
    bookings = db.query(Booking).order_by(Booking.id.desc()).all()
    return bookings

@router.get("/users", response_model=List[UserResponse])
def get_all_users(
    admin: User = Depends(verify_admin_role),
    db: Session = Depends(get_db)
):
    users = db.query(User).order_by(User.id.desc()).all()
    return users

@router.post("/boats", response_model=BoatResponse)
def add_new_boat(
    name: str,
    boat_type: str,
    capacity: int,
    price_per_seat: float,
    admin: User = Depends(verify_admin_role),
    db: Session = Depends(get_db)
):
    new_boat = Boat(
        name=name,
        boat_type=boat_type,
        capacity=capacity,
        price_per_seat=price_per_seat,
        image_url="assets/speed_boat.png"
    )
    db.add(new_boat)
    db.commit()
    db.refresh(new_boat)
    return new_boat

@router.put("/bookings/{ticket_number}/status")
def update_booking_status(
    ticket_number: str,
    new_status: str,
    admin: User = Depends(verify_admin_role),
    db: Session = Depends(get_db)
):
    booking = db.query(Booking).filter(Booking.ticket_number == ticket_number).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking ticket not found")
    
    booking.booking_status = new_status
    db.commit()
    return {"status": "success", "ticket_number": ticket_number, "new_status": new_status}
