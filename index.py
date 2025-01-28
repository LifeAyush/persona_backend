from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import math
from typing import Dict

app = FastAPI()

class LocationRequest(BaseModel):
    pickup_lat: float
    pickup_long: float
    drop_lat: float
    drop_long: float

def calculate_mock_fare(pickup_lat: float, pickup_long: float, drop_lat: float, drop_long: float) -> Dict:
    """
    Mock function to calculate fare based on coordinates
    Uses a simplified distance calculation and adds some mock pricing logic
    """
    # Calculate rough distance using Euclidean distance (for mock purposes)
    distance = math.sqrt(
        (pickup_lat - drop_lat) ** 2 + 
        (pickup_long - drop_long) ** 2
    ) * 111  # Rough conversion to kilometers (1 degree ≈ 111 km)
    
    # Mock pricing logic
    base_fare = 50  # Base fare in currency units
    per_km_rate = 10  # Rate per kilometer
    estimated_fare = base_fare + (distance * per_km_rate)
    
    # Add some mock surge pricing based on latitude (just for demonstration)
    surge_multiplier = 1.0
    if abs(pickup_lat) > 30:  # Arbitrary condition for surge pricing
        surge_multiplier = 1.2
    
    final_fare = estimated_fare * surge_multiplier
    
    return {
        "estimated_fare": round(final_fare, 2),
        "distance_km": round(distance, 2),
        "surge_multiplier": surge_multiplier,
        "currency": "USD",
        "breakdown": {
            "base_fare": base_fare,
            "distance_charge": round(distance * per_km_rate, 2),
            "surge_charge": round(final_fare - estimated_fare, 2)
        }
    }

@app.post("/get_fares")
async def get_fares(request: LocationRequest):
    try:
        # Input validation (basic range checks for coordinates)
        if not (-90 <= request.pickup_lat <= 90 and 
                -90 <= request.drop_lat <= 90 and
                -180 <= request.pickup_long <= 180 and
                -180 <= request.drop_long <= 180):
            raise HTTPException(
                status_code=400,
                detail="Invalid coordinates. Latitude must be between -90 and 90, Longitude between -180 and 180"
            )
        
        # Calculate fare using mock function
        fare_details = calculate_mock_fare(
            request.pickup_lat,
            request.pickup_long,
            request.drop_lat,
            request.drop_long
        )
        
        return fare_details
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)