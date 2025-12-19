__all__ = [
    "get_base_api_client",
    "get_strava_client",
    "get_weather_client",
    "get_training_load_service",
    "get_sleep_service",
    "get_lat_lon_service",
]

from functools import lru_cache

import geocoder

from src.core import constants
from src.core.clients.base_api_client import BaseAPIClient
from src.services.lat_lon import LatLonService
from src.services.sleep_and_recovery.manual_sleep_service import ManualSleepService
from src.services.strava.strava_api_client import StravaAPIClient
from src.services.training_load.training_load_service import TrainingLoadService
from src.services.weather import OpenMeteoWeatherAPIClient


class Constants(constants.Constants):
    pass


@lru_cache()
def get_base_api_client(base_url: str) -> BaseAPIClient:
    """Get or create a cached BaseAPIClient instance for a given base URL."""
    return BaseAPIClient(base_url=base_url)


@lru_cache()
def get_strava_api_client() -> BaseAPIClient:
    """Get or create a cached BaseAPIClient instance for Strava API."""
    return get_base_api_client(Constants.STRAVA_API_BASE_URL)


@lru_cache()
def get_open_meteo_api_client() -> BaseAPIClient:
    """Get or create a cached BaseAPIClient instance for Open Meteo API."""
    return get_base_api_client(Constants.OPEN_METEO_BASE_URL)


@lru_cache()
def get_strava_client() -> StravaAPIClient:
    """Dependency that provides a singleton StravaAPIClient instance."""
    base_api_client = get_strava_api_client()
    return StravaAPIClient(base_api_client)


@lru_cache()
def get_weather_client() -> OpenMeteoWeatherAPIClient:
    """Dependency that provides a singleton OpenMeteoWeatherAPIClient instance."""
    api_client = get_open_meteo_api_client()
    return OpenMeteoWeatherAPIClient(api_client)


@lru_cache()
def get_training_load_service() -> TrainingLoadService:
    """Dependency that provides a TrainingLoadService instance with shared StravaAPIClient."""
    strava_client = get_strava_client()
    return TrainingLoadService(strava_client=strava_client)


@lru_cache()
def get_sleep_service() -> ManualSleepService:
    """Dependency that provides a singleton ManualSleepService instance."""
    return ManualSleepService()


@lru_cache()
def get_lat_lon_service() -> LatLonService:
    """Dependency that provides a singleton LatLonService instance."""
    return LatLonService(geocoder_instance=geocoder)
