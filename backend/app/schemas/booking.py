from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class BoatResponse(BaseModel):
    id: int
    name: str
    boat_type: str
    capacity: int
    price_per_seat: float
    image_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class BookingCreate(BaseModel):
    boat_name: str
    booking_date: str
    time_slot: str
    passengers: int = 1
    payment_method: str = "Razorpay (Demo)"

class BookingResponse(BaseModel):
    id: int
    ticket_number: str
    user_id: int
    boat_name: str
    booking_date: str
    time_slot: str
    passengers: int
    total_amount: float
    payment_status: str
    booking_status: str
    qr_code_base64: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class VerifyQRRequest(BaseModel):
    ticket_number: str
