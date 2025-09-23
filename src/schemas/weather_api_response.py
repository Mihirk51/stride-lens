__all__ = [
    "WeatherAPIResponse",
]

from pydantic import BaseModel


class CurrentUnits(BaseModel):
    time: str
    interval: str
    temperature_2m: str
    relative_humidity_2m: str
    is_day: str
    precipitation: str
    rain: str
    snowfall: str
    showers: str
    wind_speed_10m: str


class Current(BaseModel):
    time: str
    interval: int
    temperature_2m: float
    relative_humidity_2m: int
    is_day: int
    precipitation: float
    rain: float
    snowfall: float
    showers: float
    wind_speed_10m: float


class WeatherAPIResponse(BaseModel):
    latitude: float
    longitude: float
    generationtime_ms: float
    utc_offset_seconds: int
    timezone: str
    timezone_abbreviation: str
    elevation: float
    current_units: CurrentUnits
    current: Current
