__all__ = [
    "OpenMeteoWeatherAPIClient",
]
from src.core import constants
from src.core.clients.base_api_client import BaseAPIClient
from src.core.config import OpenMeteoCurrentWeatherConfig, OpenMeteoForecastConfig
from src.interfaces.weather import WeatherService
from src.schemas.weather_api_schema import (
    CurrentWeatherAPIResponse,
    CurrentWeatherRequestParams,
    ForecastWeatherAPIResponse,
    WeatherForecastRequestParams,
)
from src.services.lat_lon import lat_lon_service


class Constants(constants.Constants):
    WEATHER_ENDPOINT = "/forecast"
    pass


class OpenMeteoWeatherAPIClient(WeatherService):
    def __init__(self, api_client: BaseAPIClient):
        self.client = api_client

    def get_current_weather(self, current_weather_params: CurrentWeatherRequestParams) -> CurrentWeatherAPIResponse:
        lat = current_weather_params.latitude
        lon = current_weather_params.longitude

        weather_config = OpenMeteoCurrentWeatherConfig(latitude=lat, longitude=lon)

        current_weather_params = weather_config.current_weather_params
        weather_config.current = current_weather_params

        params = weather_config.model_dump()
        reponse_data = (self.client.get(endpoint=Constants.WEATHER_ENDPOINT, params=params)).get_dict()

        return CurrentWeatherAPIResponse(**reponse_data)

    def get_weather_forecast(self, forecast_params: WeatherForecastRequestParams) -> ForecastWeatherAPIResponse:
        lat = forecast_params.latitude
        lon = forecast_params.longitude
        days = forecast_params.forecast_days

        weather_config = OpenMeteoForecastConfig(latitude=lat, longitude=lon, forecast_days=days)

        forecast_weather_params = weather_config.forecast_weather_params
        weather_config.hourly = forecast_weather_params

        params = weather_config.model_dump()
        reponse_data = (self.client.get(endpoint=Constants.WEATHER_ENDPOINT, params=params)).get_dict()

        transformed_data = self._transform_hourly_data(reponse_data)

        return ForecastWeatherAPIResponse(**transformed_data)

    def _transform_hourly_data(self, response_data: dict) -> dict:
        """
        Transform hourly data from array format to time-indexed dictionary format.
        """
        if "hourly" not in response_data.keys():
            return response_data

        hourly_data = response_data["hourly"]

        time_array = hourly_data.get("time", [])
        transformed_hourly = {}

        for i, timestamp in enumerate(time_array):
            transformed_hourly[timestamp] = {}

            for param_name, param_values in hourly_data.items():
                if param_name != "time" and isinstance(param_values, list):
                    if i < len(param_values):
                        transformed_hourly[timestamp][param_name] = param_values[i]

        transformed_response = response_data.copy()
        transformed_response["hourly"] = transformed_hourly

        return transformed_response


if __name__ == "__main__":
    api_client = BaseAPIClient(base_url=Constants.OPEN_METEO_BASE_URL)
    weather_api_client = OpenMeteoWeatherAPIClient(api_client)

    lat_lon = lat_lon_service.get_lat_lon()
    lat = lat_lon.latitude
    lon = lat_lon.longitude
    result = weather_api_client.get_current_weather(lat, lon)
