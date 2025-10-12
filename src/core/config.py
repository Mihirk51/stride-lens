__all__ = ["OpenMeteoCurrentWeatherConfig", "OpenMeteoForecastConfig"]


from pydantic import BaseModel, Field


class OpenMeteoCurrentWeatherConfig(BaseModel):
    latitude: float
    longitude: float
    timezone: str = Field(default="auto")
    wind_speed_unit: str = Field(default="mph")
    current: list | str = Field(
        default=[
            "temperature_2m",
            "relative_humidity_2m",
            "is_day",
            "precipitation",
            "rain",
            "snowfall",
            "showers",
            "wind_speed_10m",
            "wind_direction_10m",
            "wind_gusts_10m",
            "apparent_temperature",
        ]
    )

    @property
    def current_weather_params(self) -> str:
        return ",".join(self.current)


class OpenMeteoForecastConfig(BaseModel):
    latitude: float
    longitude: float
    timezone: str = Field(default="auto")
    wind_speed_unit: str = Field(default="mph")
    forecast_days: int = Field(default=3, description="Number of days to forecast")
    hourly: list | str = Field(
        default=[
            "temperature_2m",
            "precipitation",
            "precipitation_probability",
            "wind_speed_10m",
            "wind_direction_10m",
            "relative_humidity_2m",
            "wind_gusts_10m",
            "is_day",
        ]
    )

    @property
    def forecast_weather_params(self) -> str:
        return ",".join(self.hourly)
