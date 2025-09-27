__all__ = [
    "StravaAPIClient",
]

from src.core import constants
from src.core.clients.base_api_client import BaseAPIClient
from src.interfaces.strava import StravaService
from src.services.strava.utils import refresh_strava_token


class Constants(constants.Constants):
    STRAVA_API_BASE_URL = "https://www.strava.com/api/v3"
    STRAVA_ATHLETE_ENDPOINT = "/athlete"
    STRAVA_ACTIVITIES_ENDPOINT = "/athlete/activities"
    pass


class StravaAPIClient(StravaService):
    def __init__(self):
        refresh_strava_token()
        self.api_client = BaseAPIClient(base_url=Constants.STRAVA_API_BASE_URL)
        self.access_token = self._load_access_token()

    def _headers(self):
        return {"Authorization": f"Bearer {self.access_token}"}

    def get_athlete_profile(self) -> dict:
        url = Constants.STRAVA_ATHLETE_ENDPOINT
        response = self.api_client.get(url, headers=self._headers())
        return response.get_json()

    def get_recent_runs(self, limit: int = 10) -> list[dict]:
        url = Constants.STRAVA_ACTIVITIES_ENDPOINT
        params = {"per_page": limit, "page": 1}
        response = self.api_client.get(url, headers=self._headers(), params=params)
        activities = response.get_json()
        return [a for a in activities if a["type"] == "Run"]

    def _load_access_token(self) -> str:
        import os

        from dotenv import load_dotenv

        load_dotenv(Constants.ENV_FILE)
        access_token = os.getenv("STRAVA_ACCESS_TOKEN")
        if not access_token:
            raise ValueError("STRAVA_ACCESS_TOKEN not found in .env file")
        return access_token


def main():
    strava = StravaAPIClient()

    runs = strava.get_recent_runs(limit=5)
    print(runs[0])


if __name__ == "__main__":
    main()
