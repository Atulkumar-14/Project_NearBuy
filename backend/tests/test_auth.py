from fastapi.testclient import TestClient
from backend.main import app


client = TestClient(app)


def test_owner_login_requires_both_fields():
    # Missing owner_id
    r = client.post('/api/auth/owner/login', json={'password': 'x'})
    assert r.status_code == 422 or r.status_code == 400
    # Missing password
    r2 = client.post('/api/auth/owner/login', json={'owner_id': 1})
    assert r2.status_code == 422 or r2.status_code == 400


def test_owner_login_invalid_credentials():
    r = client.post('/api/auth/owner/login', json={'owner_id': 999999, 'password': 'bad'})
    assert r.status_code in (401, 404)


def test_user_login_and_me_endpoint():
    # Use seeded demo user
    r = client.post('/api/auth/login', json={'email': 'user.demo@example.com', 'password': 'Password@123'})
    assert r.status_code == 200, r.text
    token = r.json()['access_token']
    me = client.get('/api/users/me', headers={'Authorization': f'Bearer {token}'})
    assert me.status_code == 200, me.text