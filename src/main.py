import json

from src.core.clients.base_api_client import BaseAPIClient


class StravaService:
    BASE_URL = "https://www.strava.com/api/v3"

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.api_client = BaseAPIClient(base_url=self.BASE_URL)

    def _headers(self):
        return {"Authorization": f"Bearer {self.access_token}"}

    def get_athlete_profile(self) -> dict:
        url = "/athlete"
        response = self.api_client.get(url, headers=self._headers())
        return response.get_json()

    def get_recent_runs(self, limit: int = 10) -> list[dict]:
        url = "/athlete/activities"
        params = {"per_page": limit, "page": 1}
        response = self.api_client.get(url, headers=self._headers(), params=params)
        activities = response.get_dict()
        # Filter only runs
        return [a for a in activities if a["type"] == "Run"]


def main():
    strava = StravaService(access_token="3eb581261d39f19b8e8e44f0261837a1755cbb73")

    profile = strava.get_athlete_profile()
    print("Athlete:", profile["firstname"], profile["lastname"])

    runs = strava.get_recent_runs(limit=5)
    print(json.dumps(runs[0]))


if __name__ == "__main__":
    main()
