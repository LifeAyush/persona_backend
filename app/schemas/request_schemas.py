from pydantic import BaseModel, Field
from typing import Any, Dict, Optional
from uuid import uuid4

class MessagePayloadModel(BaseModel):
    """
    Model to represent the payload data within the MessageModel.
    """
    country_code: Optional[str] = Field(None, description="Country code for the route")
    route_id: Optional[str] = Field(default_factory=uuid4, description="Identifier for the route, default is random uuid")
    pickup_latitude: Optional[float] = Field(None, description="Pickup latitude")
    pickup_longitude: Optional[float] = Field(None, description="Pickup longitude")
    drop_latitude: Optional[float] = Field(None, description="Drop latitude")
    drop_longitude: Optional[float] = Field(None, description="Drop longitude")
    

class MessageModel(BaseModel):
    """
    Model to represent the message structure passed to the scrape method.
    """
    payload: MessagePayloadModel = Field(..., description="Payload containing route and scraping details")
