from fastapi import APIRouter, HTTPException
from app.models.location_request import LocationRequest
from app.utils.fare_calculation import fetch_fare
from app.delivery import convert_to_delivery_format
from typing import Dict, Any
import logging

router = APIRouter()
logging.basicConfig(level=logging.DEBUG)

@router.post("/get_fares")
async def get_fares(request: LocationRequest) -> dict:
    """
    Calculate estimated fare for a given route.
    Example Route:
    ```
        {
            "pickup_lat": 12.949294,
            "pickup_long": 77.694598,
            "drop_lat": 12.950044,
            "drop_long": 77.711044,
            "country_code": "IN",
            "city": "",
            "route_type": ""
        }
    ```
    """
    try:
        fare_details: Dict[str, Any] = fetch_fare(
            request.pickup_lat,
            request.pickup_long,
            request.drop_lat,
            request.drop_long,
            request.country_code,
            route_type=request.route_type
        )
        modified_fare_details = convert_to_delivery_format(fare_details)  
        return modified_fare_details

    except Exception as e:
        logging.error(f"Error in get_fares: {e}\nStacktrace:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))
