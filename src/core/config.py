__all__ = [
    "OpenMeteoCurrentWeatherConfig",
]

from typing import Literal

from pydantic import BaseModel, Field


class OpenMeteoCurrentWeatherConfig(BaseModel):
    latitude: float
    longitude: float
    timezone: Literal["America%2FChicago", "auto"] = Field(
        default="auto"
    )  # TODO: add logic to set timezone based on lat/lon
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
