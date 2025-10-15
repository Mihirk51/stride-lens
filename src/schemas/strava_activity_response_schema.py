__all__ = [
    "StravaActivity",
    "StravaServiceResponse",
    "StravaAthleteProfile",
]

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel


class StravaActivityUnits(BaseModel):
    distance: Literal["meters", "kilometers", "miles"] = "meters"
    moving_time: Literal["seconds", "minutes", "hhmmss"] = "seconds"
    total_elevation_gain: Literal["meters", "feet"] = "meters"

    average_speed: Optional[Literal["m/s", "km/h", "m/h", "mins/km"]] = "m/s"
    max_speed: Optional[Literal["m/s", "km/h", "m/h", "mins/km"]] = "m/s"
    average_heartrate: Optional[Literal["bpm"]] = "bpm"
    max_heartrate: Optional[Literal["bpm"]] = "bpm"

    elev_high: Literal["meters", "feet"] = "meters"
    elev_low: Literal["meters", "feet"] = "meters"


class StravaActivity(BaseModel):
    id: int
    name: str
    distance: float  # meters
    moving_time: int  # seconds
    total_elevation_gain: float  # meters
    start_date_local: datetime
    timezone: str

    average_speed: Optional[float] = None  # m/s
    max_speed: Optional[float] = None  # m/s
    average_heartrate: Optional[float] = None
    max_heartrate: Optional[float] = None

    elev_high: Optional[float] = None
    elev_low: Optional[float] = None

    trainer: bool
    commute: bool
    sport_type: str
    gear_id: Optional[str] = None

    start_latlng: Optional[List[float]] = None
    end_latlng: Optional[List[float]] = None


class StravaAthleteProfile(BaseModel):
    """Athlete profile information from Strava."""

    id: int
    username: Optional[str] = None
    firstname: str
    lastname: str
    bio: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    sex: Optional[str] = None
    premium: bool = False
    weight: Optional[float] = None
    profile_medium: Optional[str] = None
    profile: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class StravaServiceResponse(BaseModel):
    activity_units: StravaActivityUnits = StravaActivityUnits()
    activities: List[StravaActivity]
    athlete_profile: Optional[StravaAthleteProfile] = None
