__all__ = [
    "OpenMeteoWeatherAPIClient",
]

from src.core import constants
from src.core.clients.base_api_client import BaseAPIClient
from src.core.config import OpenMeteoCurrentWeatherConfig, OpenMeteoForecastConfig
from src.interfaces.weather import WeatherService
from src.schemas.weather_api_response import CurrentWeatherAPIResponse, ForecastWeatherAPIResponse
from src.services.lat_lon import lat_lon_service


class Constants(constants.Constants):
    WEATHER_ENDPOINT = "/forecast"
    pass


class OpenMeteoWeatherAPIClient(WeatherService):
    def __init__(self, base_url: str = Constants.OPEN_METEO_BASE_URL):
        self.client = BaseAPIClient(base_url=base_url)

    def get_current_weather(self, lat: float, lon: float) -> CurrentWeatherAPIResponse:
        weather_config = OpenMeteoCurrentWeatherConfig(latitude=lat, longitude=lon)

        current_weather_params = weather_config.current_weather_params
        weather_config.current = current_weather_params

        params = weather_config.model_dump()
        reponse_data = (self.client.get(endpoint=Constants.WEATHER_ENDPOINT, params=params)).get_dict()

        return CurrentWeatherAPIResponse(**reponse_data)

    def get_weather_forecast(self, lat: float, lon: float, days: int) -> ForecastWeatherAPIResponse:
        weather_config = OpenMeteoForecastConfig(latitude=lat, longitude=lon, forecast_days=days)

        forecast_weather_params = weather_config.forecast_weather_params
        weather_config.hourly = forecast_weather_params

        params = weather_config.model_dump()
        reponse_data = (self.client.get(endpoint=Constants.WEATHER_ENDPOINT, params=params)).get_dict()

        # Transform the hourly data structure
        transformed_data = self._transform_hourly_data(reponse_data)

        return ForecastWeatherAPIResponse(**transformed_data)

    def _transform_hourly_data(self, response_data: dict) -> dict:
        """
        Transform hourly data from array format to time-indexed dictionary format.
        """
        if "hourly" not in response_data.keys():
            return response_data

        hourly_data = response_data["weather_data"]["hourly"]

        # Extract time array and other parameter arrays
        time_array = hourly_data.get("time", [])

        # Create the transformed hourly structure
        transformed_hourly = {}

        for i, timestamp in enumerate(time_array):
            transformed_hourly[timestamp] = {}

            # Iterate through all hourly parameters except 'time'
            for param_name, param_values in hourly_data.items():
                if param_name != "time" and isinstance(param_values, list):
                    if i < len(param_values):
                        transformed_hourly[timestamp][param_name] = param_values[i]

        # Create new response structure
        transformed_response = response_data.copy()
        transformed_response["weather_data"] = response_data["weather_data"].copy()
        transformed_response["weather_data"]["hourly"] = transformed_hourly

        # Remove hourly_units as it's no longer needed in this format
        if "hourly_units" in transformed_response["weather_data"]:
            del transformed_response["weather_data"]["hourly_units"]

        return transformed_response


if __name__ == "__main__":
    weather_api_client = OpenMeteoWeatherAPIClient()

    lat_lon = lat_lon_service.get_lat_lon()
    lat = lat_lon.latitude
    lon = lat_lon.longitude
    result = weather_api_client.get_weather_forecast(lat, lon, 2)
