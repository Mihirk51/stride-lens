import os

from src.services.open_meteo_weather import OpenMeteoWeatherAPIClient


def main():
    lat = float(os.getenv("LATITUDE", "37.7749"))  # Default to San Francisco
    lon = float(os.getenv("LONGITUDE", "-122.4194"))

    weather_client = OpenMeteoWeatherAPIClient()
    current_weather = weather_client.get_current_weather(lat=lat, lon=lon)
    print(current_weather)


if __name__ == "__main__":
    main()
