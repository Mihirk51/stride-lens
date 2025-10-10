__all__ = [
    "CurrentWeatherSummary",
    "CurrentWeatherResponse",
    "ForecastWeatherResponse",
]

from typing import Optional

from pydantic import BaseModel, Field, validator

from src.schemas.weather_api_response import CurrentWeatherAPIResponse, ForecastWeatherAPIResponse


class CurrentWeatherSummary(BaseModel):
    """Subset of weather data with essential fields for API responses."""

    timezone: str = Field(..., description="Timezone identifier")

    # Current weather data
    temperature_2m: float = Field(..., description="Temperature at 2 meters in °C")
    relative_humidity_2m: int = Field(..., description="Relative humidity at 2 meters in %")
    is_day: int = Field(..., description="Is daytime (1) or nighttime (0)")
    precipitation: float = Field(..., description="Precipitation in mm")
    rain: float = Field(..., description="Rain in mm")
    wind_speed_10m: float = Field(..., description="Wind speed at 10 meters in km/h")

    # Optional weather data
    snowfall: Optional[float] = Field(None, description="Snowfall in mm")
    showers: Optional[float] = Field(None, description="Showers in mm")

    @classmethod
    def from_weather_api_response(cls, weather: CurrentWeatherAPIResponse) -> "CurrentWeatherSummary":
        """Create CurrentWeatherSummary from full CurrentWeatherAPIResponse model."""
        return cls(
            timezone=weather.timezone,
            temperature_2m=weather.current.temperature_2m,
            relative_humidity_2m=weather.current.relative_humidity_2m,
            is_day=weather.current.is_day,
            precipitation=weather.current.precipitation,
            rain=weather.current.rain,
            wind_speed_10m=weather.current.wind_speed_10m,
            snowfall=weather.current.snowfall,
            showers=weather.current.showers,
        )

    class Config:
        schema_extra = {
            "example": {
                "timezone": "America/New_York",
                "temperature_2m": 22.5,
                "relative_humidity_2m": 65,
                "is_day": 1,
                "precipitation": 0.0,
                "rain": 0.0,
                "wind_speed_10m": 15.2,
                "snowfall": 0.0,
                "showers": 0.0,
            }
        }


class CurrentWeatherResponse(BaseModel):
    success: bool = Field(True, description="Whether the operation was successful")
    message: str = Field(..., description="Status message")
    weather_data: Optional[CurrentWeatherSummary] = Field(None, description="Current weather data")

    @validator("weather_data", pre=True)
    def convert_weather_data(cls, v):
        if v is None:
            return v

        if isinstance(v, CurrentWeatherAPIResponse):
            return CurrentWeatherSummary.from_weather_api_response(v)
        elif isinstance(v, dict):
            try:
                weather_response = CurrentWeatherAPIResponse(**v)
                return CurrentWeatherSummary.from_weather_api_response(weather_response)
            except Exception:
                return v
        return v

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Weather data retrieved successfully",
                "weather_data": {
                    "timezone": "America/New_York",
                    "temperature_2m": 22.5,
                    "relative_humidity_2m": 65,
                    "is_day": 1,
                    "precipitation": 0.0,
                    "rain": 0.0,
                    "wind_speed_10m": 15.2,
                    "snowfall": 0.0,
                    "showers": 0.0,
                },
            }
        }


class ForecastWeatherResponse(BaseModel):
    success: bool = Field(True, description="Whether the operation was successful")
    message: str = Field(..., description="Status message")
    weather_data: Optional[ForecastWeatherAPIResponse] = Field(None, description="Forecast weather data")
