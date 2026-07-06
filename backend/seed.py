import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.booking import Boat
from app.core.security import get_password_hash
from sqlalchemy import or_

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # 1. Seed Users
        users = [
            {
                "full_name": "Admin User",
                "email": "admin@tighra.com",
                "phone": "+919876543210",
                "password": "AdminPassword123!",
                "role": "admin"
            },
            {
                "full_name": "Demo Tourist",
                "email": "tourist@tighra.com",
                "phone": "+919876543211",
                "password": "TouristPassword123!",
                "role": "tourist"
            },
            {
                "full_name": "Boat Operator Staff",
                "email": "operator@tighra.com",
                "phone": "+919876543212",
                "password": "OperatorPassword123!",
                "role": "operator"
            }
        ]
        
        for user_data in users:
            existing = db.query(User).filter(
                or_(User.email == user_data["email"], User.phone == user_data["phone"])
            ).first()
            if not existing:
                user = User(
                    full_name=user_data["full_name"],
                    email=user_data["email"],
                    phone=user_data["phone"],
                    hashed_password=get_password_hash(user_data["password"]),
                    role=user_data["role"],
                    is_active=True
                )
                db.add(user)
                print(f"Seeded user: {user_data['email']} ({user_data['role']})")
        
        # 2. Seed Boats
        boats = [
            Boat(name="Speed Boat Express", boat_type="Speed Boat", capacity=6, price_per_seat=400.0, image_url="assets/speed_boat.png"),
            Boat(name="Family Paddle Boat", boat_type="Paddle Boat", capacity=4, price_per_seat=250.0, image_url="assets/real_tighra_lake_boats.jpg"),
            Boat(name="Tighra Dam Scenic Cruise", boat_type="Cruise", capacity=30, price_per_seat=150.0, image_url="assets/real_tighra_dam_wall.jpg")
        ]
        for boat in boats:
            existing_boat = db.query(Boat).filter(Boat.name == boat.name).first()
            if not existing_boat:
                db.add(boat)
                print(f"Seeded boat: {boat.name}")

        db.commit()
        print("Database seeding completed successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
