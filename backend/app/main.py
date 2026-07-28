import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

from app.core.config import settings
from app.database import engine, Base
from app.api.auth import router as auth_router
from app.api.bookings import router as booking_router
from app.api.admin import router as admin_router
from seed import seed_database

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    try:
        seed_database()
    except Exception as e:
        print(f"Database seed note: {e}")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for Tighra Smart Boat Booking System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Enable CORS for all clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers under /api/v1 and /api
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(booking_router, prefix=settings.API_V1_STR)
app.include_router(admin_router, prefix=settings.API_V1_STR)

app.include_router(auth_router, prefix="/api")
app.include_router(booking_router, prefix="/api")
app.include_router(admin_router, prefix="/api")

# Directory paths
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
static_dir = os.path.join(base_dir, "static")

if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def read_root():
    return FileResponse(os.path.join(static_dir, "index.html"))

@app.get("/login")
def read_login():
    return FileResponse(os.path.join(static_dir, "login.html"))

@app.get("/register")
def read_register():
    return FileResponse(os.path.join(static_dir, "register.html"))

@app.get("/operator")
def read_operator():
    return FileResponse(os.path.join(static_dir, "operator.html"))

@app.get("/admin")
def read_admin():
    return FileResponse(os.path.join(static_dir, "admin.html"))

@app.get(f"{settings.API_V1_STR}/health")
def health_check():
    return {"status": "ok", "service": settings.PROJECT_NAME}
