from fastapi import APIRouter, HTTPException
from app.models.location_request import LocationRequest
from app.schemas.response_schemas import FareResponse
from app.utils.fare_calculation import fetch_fare

router = APIRouter()

# @router.post("/get_fares", response_model=FareResponse)
@router.post("/get_fares", )
async def get_fares(request: LocationRequest):
    """
    Calculate estimated fare for a given route.
    """
    try:
        fare_details = fetch_fare(
            request.pickup_lat,
            request.pickup_long,
            request.drop_lat,
            request.drop_long,
            request.country_code,
        )

        return fare_details

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
