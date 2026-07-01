import os

def get_db_url():
    env_db = os.getenv("DATABASE_URL")
    if env_db:
        return env_db
    if os.getenv("VERCEL") or not os.access(os.getcwd(), os.W_OK):
        return "sqlite:////tmp/tighra_booking.db"
    return "sqlite:///./tighra_booking.db"

class Settings:
    PROJECT_NAME: str = "Tighra Smart Boat Booking System"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "tighra_secret_key_super_secure_jwt_token_2026_change_in_production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    DATABASE_URL: str = get_db_url()

settings = Settings()
