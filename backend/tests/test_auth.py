from fastapi.testclient import TestClient
from backend.main import app


client = TestClient(app)


def test_owner_login_requires_email():
    r = client.post('/api/auth/owner/login', json={})
    assert r.status_code in (422, 400)


def test_owner_login_invalid_email():
    r = client.post('/api/auth/owner/login', json={'email': 'noone@example.com'})
    assert r.status_code in (401, 404)


def test_user_login_and_me_endpoint():
    # Use seeded demo user
    r = client.post('/api/auth/login', json={'email': 'user.demo@example.com', 'password': 'Password@123'})
    assert r.status_code == 200, r.text
    token = r.json()['access_token']
    me = client.get('/api/users/me', headers={'Authorization': f'Bearer {token}'})
    assert me.status_code == 200, me.text
