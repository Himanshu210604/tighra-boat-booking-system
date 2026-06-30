# Tighra Smart Boat Booking System - Backend & Auth Server

FastAPI backend server providing User Models, Authentication (JWT), Database Models (SQLAlchemy + SQLite), and API routes for the Tighra Smart Boat Booking System.

## Features

- **User Model & Roles**: Support for `tourist`, `admin`, and `operator` roles.
- **Authentication**: JWT access token generation & verification, password hashing using `bcrypt`.
- **API Endpoints**:
  - `POST /api/v1/auth/signup`: User registration
  - `POST /api/v1/auth/login`: User login (JSON payload)
  - `POST /api/v1/auth/login-form`: OAuth2 form login
  - `GET /api/v1/auth/me`: Protected route returning authenticated user profile
  - `GET /api/v1/health`: Server health check
- **Interactive Documentation**: Swagger UI at `http://127.0.0.1:8000/docs`

## Quick Start

### 1. Seed Database with Demo Accounts

```bash
cd backend
python seed.py
```

Default Accounts:
- **Admin**: `admin@tighra.com` / `AdminPassword123!`
- **Tourist**: `tourist@tighra.com` / `TouristPassword123!`
- **Operator**: `operator@tighra.com` / `OperatorPassword123!`

### 2. Run Backend Server

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Run Verification Tests

```bash
python run_tests.py
```
