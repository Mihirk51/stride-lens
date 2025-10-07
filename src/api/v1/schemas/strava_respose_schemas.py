__all__ = [
    "StravaActivityResponse",
]

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator

from src.schemas.strava_activity_response import StravaActivity


class StravaActivitySummary(BaseModel):
    """Subset of StravaActivity with only essential fields for API responses."""

    id: int
    name: str
    distance: float = Field(..., description="Distance in meters")
    moving_time: int = Field(..., description="Moving time in seconds")
    total_elevation_gain: float = Field(..., description="Total elevation gain in meters")
    start_date_local: datetime
    timezone: str
    sport_type: str

    # Optional fields included in summary
    average_speed: Optional[float] = Field(None, description="Average speed in m/s")
    max_speed: Optional[float] = Field(None, description="Max speed in m/s")
    average_heartrate: Optional[float] = None
    max_heartrate: Optional[float] = None

    @classmethod
    def from_strava_activity(cls, activity: StravaActivity) -> "StravaActivitySummary":
        """Create StravaActivitySummary from full StravaActivity model."""
        return cls(**activity.dict())

    class Config:
        schema_extra = {
            "example": {
                "id": 123456789,
                "name": "Morning Run",
                "distance": 5000.0,
                "moving_time": 1800,
                "total_elevation_gain": 50.0,
                "start_date_local": "2025-10-04T07:00:00Z",
                "timezone": "America/New_York",
                "average_speed": 2.78,
                "max_speed": 4.5,
                "average_heartrate": 155.0,
                "max_heartrate": 180.0,
                "sport_type": "Run",
            }
        }


class StravaActivityResponse(BaseModel):
    success: bool = Field(True, description="Whether the operation was successful")
    message: str = Field(..., description="Status message")
    activity: Optional[StravaActivitySummary] = Field(None, description="Single Strava activity data")
    activities: Optional[List[StravaActivitySummary]] = Field(None, description="List of Strava activities")

    @validator("activities", pre=True)
    def convert_activities(cls, v):
        if v is None:
            return v

        # Handle StravaServiceResponse object
        if hasattr(v, "activities"):
            v = v.activities

        converted = []
        for item in v:
            if isinstance(item, StravaActivity):
                converted.append(StravaActivitySummary.from_strava_activity(item))
            elif isinstance(item, dict):
                strava_activity = StravaActivity(**item)
                converted.append(StravaActivitySummary.from_strava_activity(strava_activity))
            else:
                converted.append(item)
        return converted

    @validator("activity", pre=True)
    def convert_activity(cls, v):
        if v is None:
            return v

        if isinstance(v, StravaActivity):
            return StravaActivitySummary.from_strava_activity(v)
        elif isinstance(v, dict):
            strava_activity = StravaActivity(**v)
            return StravaActivitySummary.from_strava_activity(strava_activity)
        return v

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Strava activities retrieved successfully",
                "activity": None,
                "activities": [
                    {
                        "id": 123456789,
                        "name": "Morning Run",
                        "distance": 5000.0,
                        "moving_time": 1800,
                        "total_elevation_gain": 50.0,
                        "start_date_local": "2025-10-04T07:00:00Z",
                        "timezone": "America/New_York",
                        "average_speed": 2.78,
                        "max_speed": 4.5,
                        "average_heartrate": 155.0,
                        "max_heartrate": 180.0,
                        "sport_type": "Run",
                    }
                ],
            }
        }
