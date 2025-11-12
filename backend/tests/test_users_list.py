from fastapi.testclient import TestClient
from backend.main import app


client = TestClient(app)


def test_users_list_returns_array_of_users():
    r = client.get('/api/users')
    assert r.status_code == 200, r.text
    data = r.json()
    assert isinstance(data, list)
    if data:
        u = data[0]
        assert 'user_id' in u
        assert 'email' in u
        assert 'created_at' in u