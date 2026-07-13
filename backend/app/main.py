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
    # Create database tables & seed initial users/boats on startup
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

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Auth, Booking & Admin routers under /api/v1 and alias /api/auth, /api/boats, /api/bookings
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(booking_router, prefix=settings.API_V1_STR)
app.include_router(admin_router, prefix=settings.API_V1_STR)

# Aliases for root /api compatibility
app.include_router(auth_router, prefix="/api")
app.include_router(booking_router, prefix="/api")
app.include_router(admin_router, prefix="/api")

# Directory paths
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
frontend_dir = os.path.join(base_dir, "frontend")
static_dir = os.path.join(base_dir, "static")

if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

if os.path.exists(frontend_dir):
    app.mount("/frontend", StaticFiles(directory=frontend_dir, html=True), name="frontend")

@app.get("/")
def read_root():
    if os.path.exists(os.path.join(static_dir, "index.html")):
        return FileResponse(os.path.join(static_dir, "index.html"))
    elif os.path.exists(os.path.join(frontend_dir, "index.html")):
        return FileResponse(os.path.join(frontend_dir, "index.html"))
    return {"message": "Tighra Smart Boat Booking System API Online", "docs": "/docs"}

@app.get("/login")
def read_login():
    login_path = os.path.join(static_dir, "login.html")
    if os.path.exists(login_path):
        return FileResponse(login_path)
    return FileResponse(os.path.join(static_dir, "index.html"))

@app.get("/register")
def read_register():
    reg_path = os.path.join(static_dir, "register.html")
    if os.path.exists(reg_path):
        return FileResponse(reg_path)
    return FileResponse(os.path.join(static_dir, "index.html"))

@app.get("/operator")
def read_operator():
    op_path = os.path.join(static_dir, "operator.html")
    if os.path.exists(op_path):
        return FileResponse(op_path)
    return FileResponse(os.path.join(static_dir, "index.html"))

@app.get("/admin")
def read_admin():
    adm_path = os.path.join(static_dir, "admin.html")
    if os.path.exists(adm_path):
        return FileResponse(adm_path)
    return FileResponse(os.path.join(static_dir, "index.html"))

@app.get(f"{settings.API_V1_STR}/health")
def health_check():
    return {"status": "ok", "service": settings.PROJECT_NAME}
