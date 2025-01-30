from fastapi import APIRouter, HTTPException
from app.models.location_request import LocationRequest
from app.schemas.response_schemas import FareResponse
from app.utils.fare_calculation import fetch_fare
from app.compiler.generic_compiler import GenericCompiler

router = APIRouter()

# @router.post("/get_fares", response_model=FareResponse)
@router.post("/get_fares", )
async def get_fares(request: LocationRequest):
    """
    Calculate estimated fare for a given route.
    Example:
    {
        "pickup_lat": 12.949294,
        "pickup_long": 77.694598,
        "drop_lat": 12.950044,
        "drop_long":  77.711044,
        "country_code": "IN"
    }
    
    """
    try:
        fare_details = fetch_fare(
            request.pickup_lat,
            request.pickup_long,
            request.drop_lat,
            request.drop_long,
            request.country_code,
            route_type = request.route_type
        )
        return fare_details

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
