from sqlalchemy.orm import Session
from app.database import engine, SessionLocal, Base
from app.models import User, Boat, TimeSlot
from app.auth import hash_password

def seed_database():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # Seed Admin
        if not db.query(User).filter(User.email == "admin@tighra.gov.in").first():
            admin = User(
                name="Chief Administrator",
                email="admin@tighra.gov.in",
                phone="+91 98765 43210",
                password_hash=hash_password("Admin@123"),
                role="admin"
            )
            db.add(admin)

        # Seed Operator
        if not db.query(User).filter(User.email == "operator@tighra.gov.in").first():
            operator = User(
                name="Gate Operator Ram",
                email="operator@tighra.gov.in",
                phone="+91 98765 11111",
                password_hash=hash_password("Operator@123"),
                role="operator"
            )
            db.add(operator)

        # Seed Tourist
        if not db.query(User).filter(User.email == "tourist@example.com").first():
            tourist = User(
                name="Anand Sharma",
                email="tourist@example.com",
                phone="+91 98765 22222",
                password_hash=hash_password("Tourist@123"),
                role="tourist"
            )
            db.add(tourist)

        # Seed Boats
        boats_data = [
            {
                "boat_name": "Royal Shikara Cruise",
                "boat_type": "Shikara",
                "capacity": 8,
                "price_per_person": 250.0,
                "status": "active",
                "description": "Traditional luxury Kashmiri style Shikara with cushioned seating and canopy shades on Tighra waters.",
                "image_url": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=500&auto=format&fit=crop"
            },
            {
                "boat_name": "Sagar Queen Speedboat",
                "boat_type": "Speed Boat",
                "capacity": 6,
                "price_per_person": 450.0,
                "status": "active",
                "description": "High-speed thrilling water ride equipped with life jackets and expert pilot.",
                "image_url": "https://images.unsplash.com/photo-1567899378494-47b22a2ae96a?w=500&auto=format&fit=crop"
            },
            {
                "boat_name": "Tighra Explorer Motorboat",
                "boat_type": "Motor Boat",
                "capacity": 20,
                "price_per_person": 150.0,
                "status": "active",
                "description": "Spacious family group tour boat offering panoramic sight-seeing of Tighra Dam hills.",
                "image_url": "https://images.unsplash.com/photo-1559136555-9303baea8ebd?w=500&auto=format&fit=crop"
            },
            {
                "boat_name": "Twin Splash Paddle Boat",
                "boat_type": "Paddle Boat",
                "capacity": 4,
                "price_per_person": 200.0,
                "status": "active",
                "description": "Self-driven 4-seater pedal boat ideal for couples and small families.",
                "image_url": "https://images.unsplash.com/photo-1520255870062-bd79d3865de7?w=500&auto=format&fit=crop"
            }
        ]

        for b_data in boats_data:
            if not db.query(Boat).filter(Boat.boat_name == b_data["boat_name"]).first():
                db.add(Boat(**b_data))

        # Seed Time Slots
        slots_data = [
            ("09:00 AM", "10:00 AM"),
            ("10:00 AM", "11:00 AM"),
            ("11:00 AM", "12:00 PM"),
            ("12:00 PM", "01:00 PM"),
            ("02:00 PM", "03:00 PM"),
            ("03:00 PM", "04:00 PM"),
            ("04:00 PM", "05:00 PM"),
            ("05:00 PM", "06:00 PM (Sunset)")
        ]

        for s_start, s_end in slots_data:
            if not db.query(TimeSlot).filter(TimeSlot.start_time == s_start, TimeSlot.end_time == s_end).first():
                db.add(TimeSlot(start_time=s_start, end_time=s_end, max_capacity=50, is_active=True))

        db.commit()
        print("Database seeded successfully with initial Tighra Dam fleet & users!")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
