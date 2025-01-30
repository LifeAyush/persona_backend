from pydantic import BaseModel
from typing import Optional

class LocationRequest(BaseModel):
    pickup_lat: float
    pickup_long: float
    drop_lat: float
    drop_long: float
    country_code: str
    route_type: str
    city: Optional[str]

__all__ = [
    "LocationRequest",
]