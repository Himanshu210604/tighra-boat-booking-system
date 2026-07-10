from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app.database import get_db
from app.models import Boat, TimeSlot, Booking, User
from app.schemas import BoatCreate, BoatResponse, SlotCreate, SlotResponse
from app.auth import get_current_user, require_role

router = APIRouter(tags=["Boats & Time Slots"])

@router.get("/api/boats", response_model=List[BoatResponse])
def get_boats(status_filter: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Boat)
    if status_filter:
        query = query.filter(Boat.status == status_filter)
    return query.all()

@router.get("/api/boats/{boat_id}", response_model=BoatResponse)
def get_boat(boat_id: int, db: Session = Depends(get_db)):
    boat = db.query(Boat).filter(Boat.id == boat_id).first()
    if not boat:
        raise HTTPException(status_code=404, detail="Boat not found")
    return boat

@router.post("/api/boats", response_model=BoatResponse)
def create_boat(boat_data: BoatCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role(["admin"]))):
    new_boat = Boat(**boat_data.model_dump())
    db.add(new_boat)
    db.commit()
    db.refresh(new_boat)
    return new_boat

@router.put("/api/boats/{boat_id}", response_model=BoatResponse)
def update_boat(boat_id: int, boat_data: BoatCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role(["admin"]))):
    boat = db.query(Boat).filter(Boat.id == boat_id).first()
    if not boat:
        raise HTTPException(status_code=404, detail="Boat not found")
    
    for key, value in boat_data.model_dump().items():
        setattr(boat, key, value)
    
    db.commit()
    db.refresh(boat)
    return boat

@router.get("/api/slots", response_model=List[SlotResponse])
def get_slots(boat_id: Optional[int] = None, date_str: Optional[str] = None, db: Session = Depends(get_db)):
    slots = db.query(TimeSlot).filter(TimeSlot.is_active == True).all()
    result = []
    
    for slot in slots:
        booked_count = 0
        if boat_id and date_str:
            count = db.query(func.sum(Booking.passenger_count)).filter(
                Booking.boat_id == boat_id,
                Booking.slot_id == slot.id,
                Booking.booking_date == date_str,
                Booking.booking_status != "CANCELLED"
            ).scalar()
            booked_count = count or 0
        
        slot_dict = {
            "id": slot.id,
            "start_time": slot.start_time,
            "end_time": slot.end_time,
            "max_capacity": slot.max_capacity,
            "is_active": slot.is_active,
            "booked_count": booked_count
        }
        result.append(slot_dict)
    return result

@router.post("/api/slots", response_model=SlotResponse)
def create_slot(slot_data: SlotCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role(["admin"]))):
    new_slot = TimeSlot(**slot_data.model_dump())
    db.add(new_slot)
    db.commit()
    db.refresh(new_slot)
    return new_slot
