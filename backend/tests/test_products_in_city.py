import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_in_city_requires_city():
    r = client.get("/api/products/in_city")
    assert r.status_code == 422 or r.status_code == 400

def test_in_city_invalid_city_format():
    r = client.get("/api/products/in_city", params={"city": "123!!"})
    assert r.status_code == 422
    assert r.json()["detail"] == "Invalid city format"

def test_in_city_unknown_city():
    r = client.get("/api/products/in_city", params={"city": "Unknownville"})
    assert r.status_code == 404

def test_in_city_indore_success():
    r = client.get("/api/products/in_city", params={"city": "Indore"})
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 20
    assert "product_id" in data[0]
    assert "product_name" in data[0]

def test_in_city_banaras_success_with_q():
    r = client.get("/api/products/in_city", params={"city": "Banaras", "q": "Product"})
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 20
    # ensure filter behaves
    assert any("product_name" in d for d in data)

