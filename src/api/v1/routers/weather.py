from fastapi import APIRouter

from src.api.v1.schemas.weather_response_schemas import CurrentWeatherResponse, ForecastWeatherResponse
from src.schemas.weather_api_response_schema import CurrentWeatherRequestParams, WeatherForecastRequestParams
from src.services.lat_lon import lat_lon_service
from src.services.weather import OpenMeteoWeatherAPIClient

router = APIRouter(tags=["weather"])

weather_api_client = OpenMeteoWeatherAPIClient()

lat_lon = lat_lon_service.get_lat_lon()
lat = lat_lon.latitude
lon = lat_lon.longitude


@router.get(
    "/current-weather",
    response_model=CurrentWeatherResponse,
    summary="Get current weather from weather client",
    operation_id="get_current_weather",
)
def get_current_weather():
    request_params = CurrentWeatherRequestParams(latitude=lat, longitude=lon)

    result = weather_api_client.get_current_weather(request_params)

    return CurrentWeatherResponse(success=True, message="Current weather retrieved successfully", weather_data=result)


@router.get(
    "/weather-forecast",
    response_model=ForecastWeatherResponse,
    summary="Get weather forecast from weather client",
    operation_id="get_weather_forecast",
)
def get_weather_forecast(forecast_days: int = 3):
    request_params = WeatherForecastRequestParams(latitude=lat, longitude=lon, forecast_days=forecast_days)

    result = weather_api_client.get_weather_forecast(request_params)

    return ForecastWeatherResponse(success=True, message="Weather forecast retrieved successfully", weather_data=result)
