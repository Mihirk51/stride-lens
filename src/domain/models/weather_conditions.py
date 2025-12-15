"""Domain model for weather conditions."""

from datetime import datetime

from pydantic import BaseModel, Field


class WeatherConditions(BaseModel):
    """Current weather for running."""

    timestamp: datetime

    # Core metrics
    temperature_c: float
    humidity_percent: int = Field(..., ge=0, le=100)
    wind_speed_mph: float = Field(..., ge=0)
    wind_gusts_mph: float | None = None
    precipitation_mm: float = Field(default=0.0, ge=0)

    # Context
    is_day: bool
    timezone: str
