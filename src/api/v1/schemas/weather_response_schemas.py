__all__ = [
    "CurrentWeatherSummary",
    "CurrentWeatherResponse",
    "ForecastWeatherResponse",
]

from typing import Dict, Optional

from pydantic import BaseModel, Field, validator

from src.schemas.weather_api_response import CurrentWeatherAPIResponse, ForecastWeatherAPIResponse, HourlyWeatherData


class CurrentWeatherSummary(BaseModel):
    """Subset of weather data with essential fields for API responses."""

    timezone: str = Field(..., description="Timezone identifier")
    current_units: Optional[dict] = Field(None, description="Units of the current weather data")

    time: str = Field(..., description="Timestamp of the current weather data")
    temperature_2m: float = Field(..., description="Temperature at 2 meters in °C")
    relative_humidity_2m: int = Field(..., description="Relative humidity at 2 meters in %")
    is_day: int = Field(..., description="Is daytime (1) or nighttime (0)")
    precipitation: float = Field(..., description="Precipitation in mm")
    rain: float = Field(..., description="Rain in mm")
    snowfall: Optional[float] = Field(None, description="Snowfall in mm")
    showers: Optional[float] = Field(None, description="Showers in mm")
    wind_speed_10m: float = Field(..., description="Wind speed at 10 meters in km/h")
    wind_direction_10m: Optional[int] = Field(None, description="Wind direction at 10 meters in degrees")
    wind_gusts_10m: Optional[float] = Field(None, description="Wind gusts at 10 meters in km/h")

    @classmethod
    def from_weather_api_response(cls, weather: CurrentWeatherAPIResponse) -> "CurrentWeatherSummary":
        """Create CurrentWeatherSummary from full CurrentWeatherAPIResponse model."""
        return cls(
            timezone=weather.timezone,
            current_units=weather.current_units.model_dump(),
            time=weather.current.time,
            temperature_2m=weather.current.temperature_2m,
            relative_humidity_2m=weather.current.relative_humidity_2m,
            is_day=weather.current.is_day,
            precipitation=weather.current.precipitation,
            rain=weather.current.rain,
            snowfall=weather.current.snowfall,
            showers=weather.current.showers,
            wind_speed_10m=weather.current.wind_speed_10m,
            wind_direction_10m=weather.current.wind_direction_10m,
            wind_gusts_10m=weather.current.wind_gusts_10m,
        )

    class Config:
        schema_extra = {
            "timezone": "America/Chicago",
            "current_units": {
                "time": "iso8601",
                "interval": "seconds",
                "temperature_2m": "°C",
                "relative_humidity_2m": "%",
                "is_day": "",
                "precipitation": "mm",
                "rain": "mm",
                "snowfall": "cm",
                "showers": "mm",
                "wind_speed_10m": "mp/h",
                "wind_direction_10m": "°",
                "wind_gusts_10m": "mp/h",
            },
            "time": "2025-10-11T14:15",
            "temperature_2m": 17.3,
            "relative_humidity_2m": 68,
            "is_day": 1,
            "precipitation": 0,
            "rain": 0,
            "snowfall": 0,
            "showers": 0,
            "wind_speed_10m": 10.8,
            "wind_direction_10m": 30,
            "wind_gusts_10m": 14.1,
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
            "success": True,
            "message": "Current weather retrieved successfully",
            "weather_data": {
                "timezone": "America/Chicago",
                "current_units": {
                    "time": "iso8601",
                    "interval": "seconds",
                    "temperature_2m": "°C",
                    "relative_humidity_2m": "%",
                    "is_day": "",
                    "precipitation": "mm",
                    "rain": "mm",
                    "snowfall": "cm",
                    "showers": "mm",
                    "wind_speed_10m": "mp/h",
                    "wind_direction_10m": "°",
                    "wind_gusts_10m": "mp/h",
                },
                "time": "2025-10-11T14:15",
                "temperature_2m": 17.3,
                "relative_humidity_2m": 68,
                "is_day": 1,
                "precipitation": 0,
                "rain": 0,
                "snowfall": 0,
                "showers": 0,
                "wind_speed_10m": 10.8,
                "wind_direction_10m": 30,
                "wind_gusts_10m": 14.1,
            },
        }


class ForecastWeatherSummary(BaseModel):
    """Subset of forecast weather data with essential fields for API responses."""

    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    timezone: str = Field(..., description="Timezone identifier")
    timezone_abbreviation: str = Field(..., description="Timezone abbreviation")
    elevation: float = Field(..., description="Elevation in meters")
    generationtime_ms: float = Field(..., description="API generation time in milliseconds")
    utc_offset_seconds: int = Field(..., description="UTC offset in seconds")
    hourly_units: Optional[dict] = Field(None, description="Units of the hourly weather data")
    hourly: Dict[str, HourlyWeatherData] = Field(..., description="Hourly weather data indexed by timestamp")

    @classmethod
    def from_forecast_api_response(cls, forecast: ForecastWeatherAPIResponse) -> "ForecastWeatherSummary":
        """Create ForecastWeatherSummary from ForecastWeatherAPIResponse."""
        if isinstance(forecast.hourly, dict):
            hourly_data = {
                timestamp: HourlyWeatherData(**data) if isinstance(data, dict) else data
                for timestamp, data in forecast.hourly.items()
            }
        else:
            raise ValueError("Expected transformed hourly data as dictionary, got array format")

        return cls(
            latitude=forecast.latitude,
            longitude=forecast.longitude,
            timezone=forecast.timezone,
            timezone_abbreviation=forecast.timezone_abbreviation,
            elevation=forecast.elevation,
            generationtime_ms=forecast.generationtime_ms,
            utc_offset_seconds=forecast.utc_offset_seconds,
            hourly_units=forecast.hourly_units.model_dump(),
            hourly=hourly_data,
        )

    class Config:
        schema_extra = {
            "example": {
                "latitude": 41.85271,
                "longitude": -87.65361,
                "timezone": "America/Chicago",
                "timezone_abbreviation": "GMT-5",
                "elevation": 179.0,
                "generationtime_ms": 0.2415180206298828,
                "utc_offset_seconds": -18000,
                "hourly": {
                    "2025-10-10T00:00": {
                        "temperature_2m": 10.0,
                        "precipitation": 0.0,
                        "precipitation_probability": 0,
                        "wind_speed_10m": 4.3,
                        "wind_direction_10m": 141,
                        "relative_humidity_2m": 77,
                        "wind_gusts_10m": 13.4,
                        "is_day": 0,
                    },
                    "2025-10-10T01:00": {
                        "temperature_2m": 9.5,
                        "precipitation": 0.0,
                        "precipitation_probability": 0,
                        "wind_speed_10m": 5.8,
                        "wind_direction_10m": 157,
                        "relative_humidity_2m": 75,
                        "wind_gusts_10m": 17.2,
                        "is_day": 0,
                    },
                },
            }
        }


class ForecastWeatherResponse(BaseModel):
    success: bool = Field(True, description="Whether the operation was successful")
    message: str = Field(..., description="Status message")
    weather_data: Optional[ForecastWeatherSummary] = Field(None, description="Forecast weather data")

    @validator("weather_data", pre=True)
    def convert_weather_data(cls, v):
        if v is None:
            return v

        if isinstance(v, ForecastWeatherAPIResponse):
            return ForecastWeatherSummary.from_forecast_api_response(v)
        elif isinstance(v, dict):
            try:
                forecast_response = ForecastWeatherAPIResponse(**v)
                return ForecastWeatherSummary.from_forecast_api_response(forecast_response)
            except Exception:
                # If conversion fails, return original data
                return v
        return v

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Weather forecast retrieved successfully",
                "weather_data": {
                    "latitude": 41.85271,
                    "longitude": -87.65361,
                    "timezone": "America/Chicago",
                    "timezone_abbreviation": "GMT-5",
                    "elevation": 179.0,
                    "generationtime_ms": 0.2415180206298828,
                    "utc_offset_seconds": -18000,
                    "hourly": {
                        "2025-10-10T00:00": {
                            "temperature_2m": 10.0,
                            "precipitation": 0.0,
                            "precipitation_probability": 0,
                            "wind_speed_10m": 4.3,
                            "wind_direction_10m": 141,
                            "relative_humidity_2m": 77,
                            "wind_gusts_10m": 13.4,
                            "is_day": 0,
                        }
                    },
                },
            }
        }
