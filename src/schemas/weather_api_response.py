__all__ = [
    "ForecastWeatherAPIResponse",
    "CurrentWeatherAPIResponse",
]

from typing import Dict, Optional, Union

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
    wind_direction_10m: str
    wind_gusts_10m: str


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
    wind_direction_10m: int
    wind_gusts_10m: float


class CurrentWeatherAPIResponse(BaseModel):
    latitude: float
    longitude: float
    generationtime_ms: float
    utc_offset_seconds: int
    timezone: str
    timezone_abbreviation: str
    elevation: float
    current_units: CurrentUnits
    current: Current

    class Config:
        extra = "ignore"


class HourlyUnits(BaseModel):
    time: str
    temperature_2m: str
    precipitation: str
    precipitation_probability: str
    wind_speed_10m: str
    wind_direction_10m: str
    relative_humidity_2m: str
    wind_gusts_10m: str
    is_day: str


class Hourly(BaseModel):
    time: list[str]
    temperature_2m: list[float]
    precipitation: list[float]
    precipitation_probability: list[int]
    wind_speed_10m: list[float]
    wind_direction_10m: list[int]
    wind_gusts_10m: list[float]
    relative_humidity_2m: list[int]
    is_day: list[int]


class HourlyWeatherData(BaseModel):
    """Individual hourly weather data point."""

    temperature_2m: float
    precipitation: float
    precipitation_probability: int
    wind_speed_10m: float
    wind_direction_10m: int
    wind_gusts_10m: float
    relative_humidity_2m: int
    is_day: int


class ForecastWeatherAPIResponse(BaseModel):
    latitude: float
    longitude: float
    generationtime_ms: float
    utc_offset_seconds: int
    timezone: str
    timezone_abbreviation: str
    elevation: float
    hourly_units: Optional[HourlyUnits] = None  # Optional since it gets removed
    hourly: Union[Hourly, Dict[str, HourlyWeatherData]]  # Support both formats

    class Config:
        extra = "ignore"
