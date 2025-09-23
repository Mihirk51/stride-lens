import geocoder

from src.core import loggers
from src.services.open_meteo_weather import OpenMeteoWeatherAPIClient

log = loggers.logger


def main():
    try:
        g = geocoder.ip("me")  # TODO: When going big, replace with platform specific library to get location
        lat, lon = g.latlng
    except Exception:
        log.exception("Error obtaining geolocation")

    weather_client = OpenMeteoWeatherAPIClient()
    current_weather = weather_client.get_current_weather(lat=lat, lon=lon)
    log.info(f"Current weather: {current_weather.model_dump_json(indent=2)}")


if __name__ == "__main__":
    main()
