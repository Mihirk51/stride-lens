from src.core.clients.base_api_client import BaseAPIClient
from src.interfaces.weather import WeatherService
from src.schemas.weather_api_response import WeatherAPIResponse


class OpenMeteoWeatherAPIClient(WeatherService):
    def __init__(self, base_url: str = "https://api.open-meteo.com/v1"):
        self.client = BaseAPIClient(base_url=base_url)

    def get_current_weather(self, lat: float, lon: float) -> WeatherAPIResponse:
        return self.client.get(f"/weather?lat={lat}&lon={lon}")

    def get_weather_forecast(self, lat: float, lon: float, days: int) -> WeatherAPIResponse:
        return self.client.get(f"/weather/forecast?lat={lat}&lon={lon}&days={days}")
