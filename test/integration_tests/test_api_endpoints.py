import pytest
from fastapi.testclient import TestClient
from app.api.v1 import app


client = TestClient(app)


def test_get_fares_valid_coordinates():
    """
    Test getting fares with valid coordinates.
    """
    data = {
        "pickup_lat": 34.0522,
        "pickup_long": -118.2437,
        "drop_lat": 33.9517,
        "drop_long": -118.3683
    }
    response = client.post("/get_fares", json=data)
    assert response.status_code == 200
    assert response.json()['estimated_fare'] > 0


def test_get_fares_invalid_coordinates():
    """
    Test getting fares with invalid coordinates.
    """
    data = {
        "pickup_lat": 100,
        "pickup_long": -100,
        "drop_lat": -100,
        "drop_long": 100
    }
    response = client.post("/get_fares", json=data)
    assert response.status_code == 400
    assert response.json()['detail'] == 'Invalid coordinates. Latitude must be between -90 and 90, Longitude between -180 and 180'