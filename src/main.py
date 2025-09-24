from src.core import loggers
from src.services import OpenMeteoWeatherAPIClient, lat_lon_service

log = loggers.logger


def main():
    try:
        lat, lon = (
            lat_lon_service.get_lat_lon()
        )  # TODO: When going big, replace with platform specific library to get location
    except Exception:
        log.exception("Error obtaining geolocation")

    weather_client = OpenMeteoWeatherAPIClient()
    current_weather = weather_client.get_current_weather(lat=lat, lon=lon)
    log.info(f"Current weather: {current_weather.model_dump_json(indent=2)}")


if __name__ == "__main__":
    main()
