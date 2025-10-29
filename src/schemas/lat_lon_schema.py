__all__ = [
    "LatLonServiceResponse",
]

from pydantic import BaseModel, Field


class LatLonServiceResponse(BaseModel):
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
