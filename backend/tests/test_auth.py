import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.database import Base, engine, SessionLocal
from app.models.user import User

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_signup_user():
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "full_name": "Test User",
            "email": "test@example.com",
            "phone": "+919999999999",
            "password": "SecretPassword123!",
            "role": "tourist"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"
    assert "id" in data
    assert "password" not in data
    assert "hashed_password" not in data

def test_signup_duplicate_email():
    client.post(
        "/api/v1/auth/signup",
        json={
            "full_name": "User One",
            "email": "dup@example.com",
            "password": "Password123!"
        }
    )
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "full_name": "User Two",
            "email": "dup@example.com",
            "password": "Password456!"
        }
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_login_success():
    client.post(
        "/api/v1/auth/signup",
        json={
            "full_name": "Login User",
            "email": "login@example.com",
            "password": "CorrectPassword123!"
        }
    )
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "login@example.com",
            "password": "CorrectPassword123!"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "login@example.com"

def test_login_wrong_password():
    client.post(
        "/api/v1/auth/signup",
        json={
            "full_name": "Login User",
            "email": "login2@example.com",
            "password": "CorrectPassword123!"
        }
    )
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "login2@example.com",
            "password": "WrongPassword123!"
        }
    )
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]

def test_get_me_profile():
    signup_res = client.post(
        "/api/v1/auth/signup",
        json={
            "full_name": "Profile User",
            "email": "profile@example.com",
            "password": "MySecretPassword123!"
        }
    )
    login_res = client.post(
        "/api/v1/auth/login",
        json={
            "email": "profile@example.com",
            "password": "MySecretPassword123!"
        }
    )
    token = login_res.json()["access_token"]

    me_res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["email"] == "profile@example.com"
    assert me_data["full_name"] == "Profile User"

def test_get_me_unauthorized():
    res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalidtoken123"}
    )
    assert res.status_code == 401
