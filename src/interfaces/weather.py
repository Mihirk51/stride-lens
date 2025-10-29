from abc import ABC, abstractmethod

from src.schemas.weather_api_response_schema import (
    CurrentWeatherAPIResponse,
    CurrentWeatherRequestParams,
    ForecastWeatherAPIResponse,
    WeatherForecastRequestParams,
)


class WeatherService(ABC):
    """Contract for any weather service provider."""

    @abstractmethod
    def get_current_weather(self, current_weather_params: CurrentWeatherRequestParams) -> CurrentWeatherAPIResponse:
        """Return validated current weather data for a given lat/lon."""
        pass

    def get_weather_forecast(self, forecast_params: WeatherForecastRequestParams) -> ForecastWeatherAPIResponse:
        """Return validated weather forecast data for a given lat/lon and number of days."""
        pass
