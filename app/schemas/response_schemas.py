from pydantic import BaseModel


class FareResponse(BaseModel):
    estimated_fare: float
    distance_km: float
    surge_multiplier: float
    currency: str
    breakdown: dict

__all__ = [
    "FareResponse",
]