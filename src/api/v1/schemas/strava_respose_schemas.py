__all__ = [
    "StravaActivityResponse",
    "StravaAthleteProfileSummary",
]

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator

from src.schemas.strava_activity_schema import StravaActivity, StravaActivityUnits, StravaAthleteProfile


class StravaActivitySummary(BaseModel):
    """Subset of StravaActivity with only essential fields for API responses."""

    id: int
    name: str
    distance: float = Field(..., description="Distance in meters")
    moving_time: str = Field(..., description="Moving time in seconds")
    total_elevation_gain: float = Field(..., description="Total elevation gain in meters")
    start_date_local: datetime
    timezone: str
    sport_type: str

    # Optional fields included in summary
    average_speed: Optional[str] = Field(None, description="Average speed in m/s")
    max_speed: Optional[str] = Field(None, description="Max speed in m/s")
    average_heartrate: Optional[float] = None
    max_heartrate: Optional[float] = None

    @classmethod
    def from_strava_activity(cls, activity: StravaActivity) -> "StravaActivitySummary":
        """Create StravaActivitySummary from full StravaActivity model."""
        return cls(**activity.dict())

    class Config:
        json_schema_extra = {
            "example": {
                "id": 123456789,
                "name": "Morning Run",
                "distance": 5.0,
                "moving_time": "30:00",
                "total_elevation_gain": 50.0,
                "start_date_local": "2025-10-04T07:00:00Z",
                "timezone": "America/New_York",
                "average_speed": "06:00",
                "max_speed": "04:30",
                "average_heartrate": 155.0,
                "max_heartrate": 180.0,
                "sport_type": "Run",
            }
        }


class StravaAthleteProfileSummary(BaseModel):
    """Summary of athlete profile for API responses."""

    id: int
    username: Optional[str] = None
    firstname: str
    lastname: str
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    sex: Optional[str] = None
    premium: bool = False
    weight: Optional[float] = None
    profile_medium: Optional[str] = None

    @classmethod
    def from_athlete_profile(cls, profile: StravaAthleteProfile) -> "StravaAthleteProfileSummary":
        """Create summary from full athlete profile."""
        return cls(**profile.dict())

    class Config:
        json_schema_extra = {
            "example": {
                "id": 39347966,
                "username": "mihir_kadam",
                "firstname": "Mihir",
                "lastname": "Kadam",
                "city": "Chicago",
                "state": "Illinois",
                "country": "United States",
                "sex": "M",
                "premium": False,
                "weight": 69.0,
                "profile_medium": "https://graph.facebook.com/2408439245872989/picture?height=256&width=256",
            }
        }


class StravaActivityResponse(BaseModel):
    success: bool = Field(True, description="Whether the operation was successful")
    message: str = Field(..., description="Status message")
    athlete_profile: Optional[StravaAthleteProfileSummary] = Field(None, description="Athlete profile information")
    activity_units: Optional[StravaActivityUnits] = Field(None, description="Units for activity metrics")
    activity: Optional[StravaActivitySummary] = Field(None, description="Single Strava activity data")
    activities: Optional[List[StravaActivitySummary]] = Field(None, description="List of Strava activities")

    @validator("athlete_profile", pre=True)
    def convert_athlete_profile(cls, v):
        if v is None:
            return v

        if isinstance(v, StravaAthleteProfile):
            return StravaAthleteProfileSummary.from_athlete_profile(v)
        elif isinstance(v, dict):
            profile = StravaAthleteProfile(**v)
            return StravaAthleteProfileSummary.from_athlete_profile(profile)
        return v

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
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Strava activities retrieved successfully",
                "athlete_profile": {
                    "id": 39347966,
                    "username": "mihir_kadam",
                    "firstname": "Mihir",
                    "lastname": "Kadam",
                    "city": "Chicago",
                    "state": "Illinois",
                    "country": "United States",
                    "sex": "M",
                    "premium": False,
                    "weight": 69.0,
                },
                "activity_units": {
                    "distance": "kilometers",
                    "moving_time": "hhmmss",
                    "total_elevation_gain": "meters",
                    "average_speed": "mins/km",
                    "max_speed": "mins/km",
                    "average_heartrate": "bpm",
                    "max_heartrate": "bpm",
                    "elev_high": "meters",
                    "elev_low": "meters",
                },
                "activity": None,
                "activities": [
                    {
                        "id": 123456789,
                        "name": "Morning Run",
                        "distance": 5.0,
                        "moving_time": "30:00",
                        "total_elevation_gain": 50.0,
                        "start_date_local": "2025-10-04T07:00:00Z",
                        "timezone": "America/New_York",
                        "average_speed": "06:00",
                        "max_speed": "04:30",
                        "average_heartrate": 155.0,
                        "max_heartrate": 180.0,
                        "sport_type": "Run",
                    }
                ],
            }
        }
