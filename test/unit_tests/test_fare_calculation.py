import pytest
from app.utils import calculate_mock_fare


def test_calculate_mock_fare_valid_coordinates():
    """
    Test fare calculation with valid coordinates.
    """
    pickup_lat = 34.0522
    pickup_long = -118.2437
    drop_lat = 33.9517
    drop_long = -118.3683
    fare_details = calculate_mock_fare(pickup_lat, pickup_long, drop_lat, drop_long)
    assert fare_details['estimated_fare'] > 0
    assert fare_details['distance_km'] > 0


def test_calculate_mock_fare_invalid_coordinates():
    """
    Test fare calculation with invalid coordinates.
    """
    pickup_lat = 100
    pickup_long = -100
    drop_lat = -100
    drop_long = 100
    with pytest.raises(ValueError):
        calculate_mock_fare(pickup_lat, pickup_long, drop_lat, drop_long)