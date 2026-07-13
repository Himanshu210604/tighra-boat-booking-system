import uvicorn
import os
import sys

# Reconfigure stdout for utf-8 on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Ensure backend directory is in python search path
base_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(base_dir, "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

if __name__ == "__main__":
    print("==========================================================================")
    print("🚀 Starting Tighra Smart Boat Booking System Server...")
    print("🌊 Tourist Web App Portal:     http://localhost:8000/")
    print("🔑 Login Page:                 http://localhost:8000/login")
    print("🛡️ Gate Operator QR Scanner:  http://localhost:8000/operator")
    print("⚡ Admin Control Console:      http://localhost:8000/admin")
    print("📚 API Documentation:          http://localhost:8000/docs")
    print("==========================================================================")

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
