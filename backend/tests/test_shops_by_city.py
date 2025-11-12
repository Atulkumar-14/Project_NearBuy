import asyncio
import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_shops_by_city_bhopal():
    r = client.get("/api/shops/by_city", params={"city": "Bhopal"})
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    # Should return either real shops or empty; but structure must be correct
    for it in data:
        assert "shop_id" in it and "shop_name" in it
        assert it.get("city") and it["city"].lower() == "bhopal"

def test_shops_by_city_unknown():
    r = client.get("/api/shops/by_city", params={"city": "Atlantis"})
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) == 0

def test_shops_by_city_special_chars():
    # Edge case: extra spaces and case variations
    r = client.get("/api/shops/by_city", params={"city": "  bhOpAl  "})
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    for it in data:
        assert it.get("city", "").lower().strip() == "bhopal"
