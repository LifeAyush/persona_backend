# from pydantic import BaseModel
# from typing import List, Optional
# from app.config import ENABLED_APPS 

# class RivalResponse(BaseModel):
#     vehicle_category: str
#     price: float
#     eta: Optional[str] = None 

# class FareResponse(BaseModel):
#     """Dynamically adds fields based on ENABLED_APPS"""
#     def __init_subclass__(cls, **kwargs):
#         for app in ENABLED_APPS:
#             field_name = f"{app.upper()}_DATA"
#             cls.__annotations__[field_name] = List[RivalResponse]  
#             setattr(cls, field_name, [])  

# __all__ =[
#     "FareResponse",
#     "RivalResponse",
# ]