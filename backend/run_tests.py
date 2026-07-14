import sys
import os
import time
import threading
import requests
import uvicorn

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.main import app
from app.database import Base, engine, SessionLocal
from app.models.user import User

HOST = "127.0.0.1"
PORT = 8009
BASE_URL = f"http://{HOST}:{PORT}/api/v1"

def start_server():
    uvicorn.run(app, host=HOST, port=PORT, log_level="error")

def run_tests():
    # 1. Reset database
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Database reset completed.")

    # 2. Start server in thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(1.5)  # Wait for server to bind

    # 3. Test Health Check
    health_res = requests.get(f"{BASE_URL}/health")
    assert health_res.status_code == 200, f"Health check failed: {health_res.text}"
    print("[PASS] GET /api/v1/health")

    # 4. Test User Signup
    signup_payload = {
        "full_name": "Test Tourist",
        "email": "tourist_test@tighra.com",
        "phone": "+919876543210",
        "password": "Password123!",
        "role": "tourist"
    }
    signup_res = requests.post(f"{BASE_URL}/auth/signup", json=signup_payload)
    assert signup_res.status_code == 201, f"Signup failed: {signup_res.text}"
    user_data = signup_res.json()
    assert user_data["email"] == "tourist_test@tighra.com"
    assert "id" in user_data
    print("[PASS] POST /api/v1/auth/signup")

    # 5. Test Duplicate Email Signup Rejection
    dup_res = requests.post(f"{BASE_URL}/auth/signup", json=signup_payload)
    assert dup_res.status_code == 400, f"Duplicate signup didn't fail as expected: {dup_res.text}"
    print("[PASS] POST /api/v1/auth/signup (Duplicate Email Rejection)")

    # 6. Test Login Success
    login_payload = {
        "email": "tourist_test@tighra.com",
        "password": "Password123!"
    }
    login_res = requests.post(f"{BASE_URL}/auth/login", json=login_payload)
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    login_data = login_res.json()
    assert "access_token" in login_data
    token = login_data["access_token"]
    print("[PASS] POST /api/v1/auth/login")

    # 7. Test Login Wrong Password
    bad_login_res = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "tourist_test@tighra.com",
        "password": "WrongPassword!"
    })
    assert bad_login_res.status_code == 401, f"Wrong password login didn't return 401: {bad_login_res.text}"
    print("[PASS] POST /api/v1/auth/login (Invalid Password Rejection)")

    # 8. Test Protected Profile /me with Valid Token
    me_res = requests.get(
        f"{BASE_URL}/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_res.status_code == 200, f"Profile fetch failed: {me_res.text}"
    me_data = me_res.json()
    assert me_data["email"] == "tourist_test@tighra.com"
    assert me_data["full_name"] == "Test Tourist"
    print("[PASS] GET /api/v1/auth/me (Authenticated Profile)")

    # 9. Test Protected Profile /me with Invalid Token
    bad_me_res = requests.get(
        f"{BASE_URL}/auth/me",
        headers={"Authorization": "Bearer invalidtoken123"}
    )
    assert bad_me_res.status_code == 401, f"Invalid token access didn't return 401: {bad_me_res.text}"
    print("[PASS] GET /api/v1/auth/me (Unauthorized Rejection)")

    print("\nALL BACKEND AUTHENTICATION TESTS PASSED SUCCESSFULLY! 100% VERIFIED.")

if __name__ == "__main__":
    run_tests()
