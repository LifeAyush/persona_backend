from pydantic import BaseModel


class LocationRequest(BaseModel):
    pickup_lat: float
    pickup_long: float
    drop_lat: float
    drop_long: float
    country_code: str

__all__ = [
    "LocationRequest",
]