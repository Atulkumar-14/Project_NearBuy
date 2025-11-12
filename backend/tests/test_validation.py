from fastapi.testclient import TestClient
from backend.main import app


client = TestClient(app)


def test_signup_rejects_weak_password():
    payload = {
        "name": " Weak User ",
        "email": "weak.user@example.com",
        "password": "weakpass",
        "phone": "90000-00000",
    }
    r = client.post('/api/auth/register', json=payload)
    assert r.status_code == 422, r.text


def test_signup_accepts_strong_password():
    payload = {
        "name": "Strong User",
        "email": "strong.user@example.com",
        "password": "StrongPassw0rd!",
        "phone": "+91 90000 00000",
    }
    r = client.post('/api/auth/register', json=payload)
    # 200 OK with normalized phone and email
    assert r.status_code == 200, r.text
