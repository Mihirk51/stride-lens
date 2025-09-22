import os

from src.core.clients.base_api_client import BaseAPIClient


def main():
    api_key = os.getenv("OW_API_KEY")
    client = BaseAPIClient("https://api.open-meteo.com/v1")
    params = {
        "latitude": 41.85,
        "longitude": -87.65,
        "current": "temperature_2m,relative_humidity_2m,is_day,precipitation,rain,snowfall,showers,wind_speed_10m,wind_direction_10m,wind_gusts_10m",
    }

    response = client.get("/forecast", params=params)
    print(response.data)


if __name__ == "__main__":
    main()
