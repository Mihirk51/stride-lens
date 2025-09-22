from abc import ABC, abstractmethod

from src.schemas.weather_api_response import WeatherAPIResponse


class WeatherService(ABC):
    """Contract for any weather service provider."""

    @abstractmethod
    def get_current_weather(self, lat: float, lon: float) -> WeatherAPIResponse:
        """Return validated current weather data for a given lat/lon."""
        pass

    def get_weather_forecast(self, lat: float, lon: float, days: int) -> WeatherAPIResponse:
        """Return validated weather forecast data for a given lat/lon and number of days."""
        pass
