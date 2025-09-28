__all__ = ["StravaActivity"]

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


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
