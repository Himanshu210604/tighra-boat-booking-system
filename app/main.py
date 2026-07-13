from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from app.database import engine, Base
from app.seed import seed_database
from app.routers import auth_router, boats_router, bookings_router, qr_router, admin_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables & seed database
    Base.metadata.create_all(bind=engine)
    seed_database()
    yield

app = FastAPI(
    title="Tighra Smart Boat Booking System",
    description="Digital ticket booking, QR verification, and fleet management system for Tighra Dam, Gwalior.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth_router.router)
app.include_router(boats_router.router)
app.include_router(bookings_router.router)
app.include_router(qr_router.router)
app.include_router(admin_router.router)

# Mount Static Files (HTML, CSS, JS)
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
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
