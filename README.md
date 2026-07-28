# ⛵ Tighra Smart Boat Booking System

> A modern, automated boat ticket booking and fleet management web application built for Tighra Dam & Reservoir. Powered by **FastAPI**, **SQLite**, and modern **JavaScript / HTML5 / CSS3**.

---

## 🌟 Key Features

- 🎟️ **Online Ticket Reservation**: Seamless ticket booking for Speed Boats, Motor Boats, Paddle Boats, and Water Scooters.
- 📱 **QR Code Ticket Verification**: Instant digital ticket generation with encrypted QR codes for hassle-free entry and validation.
- 🛡️ **User Authentication**: Secure JWT-based authentication system with user registration, login, and session persistence.
- 📊 **Admin Dashboard**: Comprehensive analytics, real-time boat status monitoring, ticket sales reporting, and revenue tracking.
- 🚤 **Operator Validation Portal**: Specialized interface for dock operators to scan and validate passenger QR passes in real time.
- 📱 **Fully Responsive UI**: Stunning, modern, mobile-friendly interface styled with CSS glassmorphism, smooth animations, and curated color palettes.
- ⚡ **Vercel Serverless Ready**: Configured for instant deployment on Vercel with optimized serverless routing.

---

## 🛠️ Technology Stack

| Layer | Technology |
| :--- | :--- |
| **Backend API** | Python 3.12+, FastAPI, Uvicorn |
| **Database** | SQLite, SQLAlchemy / Raw SQL |
| **Security** | Passlib (Bcrypt password hashing), PyJWT / Jose |
| **Frontend** | Vanilla JS (ES6+), HTML5, Custom CSS3 Design System |
| **QR Engine** | Python `qrcode` library, HTML5 QR Scanner |
| **Deployment** | Vercel Serverless Functions (`vercel.json`) |

---

## 📁 Repository Directory Structure

```
project1/
├── app/                      # Main FastAPI application & route controllers
│   ├── main.py               # Application entrypoint & middleware
│   ├── database.py           # DB connection & session initializer
│   ├── auth.py               # Authentication helper functions
│   ├── models.py             # Data models
│   ├── seed.py               # Initial database seed script
│   └── routers/              # Modular API router controllers
│       ├── auth_router.py    # Login / Register endpoints
│       ├── boats_router.py   # Boat catalog & availability APIs
│       ├── bookings_router.py# Ticket booking management
│       ├── admin_router.py   # Admin management endpoints
│       └── qr_router.py      # QR code generation & scanning
├── backend/                  # Alternative backend service structure & unit tests
│   ├── app/                  # Modular architecture (api, core, models, schemas)
│   ├── tests/                # Automated API test suite
│   └── run_tests.py          # Test suite executor
├── static/                   # Production frontend assets
│   ├── index.html            # Main booking landing page
│   ├── login.html            # User login portal
│   ├── register.html         # Account registration page
│   ├── admin.html            # Administrative dashboard
│   ├── operator.html         # Dock operator verification portal
│   ├── css/style.css         # UI stylesheet
│   └── js/                   # Frontend scripts (app.js, admin.js, scanner.js)
├── frontend/                 # Standalone web app assets & images
├── api/
│   └── index.py              # Vercel serverless entrypoint
├── run.py                    # Local server runner
├── vercel.json               # Vercel deployment configuration
└── requirements.txt          # Python dependencies
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+** installed on your system.
- Git for version control.

### Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Himanshu210604/tighra-boat-booking-system.git
   cd tighra-boat-booking-system
   ```

2. **Create & activate a virtual environment**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Seed the database** *(Optional, populates sample boats & admin credentials)*:
   ```bash
   python app/seed.py
   ```

5. **Run the local development server**:
   ```bash
   python run.py
   ```
   Open your browser and navigate to `http://127.0.0.1:8000`.

---

## 📖 API Documentation

FastAPI automatically generates interactive API documentation. Once the app is running, visit:

- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🧪 Running Automated Tests

To run the automated backend test suite:

```bash
python backend/run_tests.py
```

---

## 🤝 Author & License

Developed by **[Himanshu210604](https://github.com/Himanshu210604)**.

*This project is open-source under the MIT License.*
