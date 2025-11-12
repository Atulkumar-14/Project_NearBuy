from fastapi.testclient import TestClient
from backend.main import app


client = TestClient(app)


def test_admin_stats_requires_auth():
    r = client.get('/api/admin/stats')
    assert r.status_code == 401


def test_admin_stats_rejects_non_admin_role():
    # Login as user
    r = client.post('/api/auth/login', json={'email': 'user.demo@example.com', 'password': 'Password@123'})
    assert r.status_code == 200
    token = r.json()['access_token']
    r2 = client.get('/api/admin/stats', headers={'Authorization': f'Bearer {token}'})
    assert r2.status_code == 403


def test_admin_stats_allows_admin():
    # Login as admin (env defaults)
    r = client.post('/api/auth/admin/login', json={'userId': 'nearbuy-admin', 'password': 'Admin@123'})
    assert r.status_code == 200, r.text
    token = r.json()['access_token']
    r2 = client.get('/api/admin/stats', headers={'Authorization': f'Bearer {token}'})
    assert r2.status_code == 200, r2.text