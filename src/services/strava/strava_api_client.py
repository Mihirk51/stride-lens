__all__ = [
    "StravaAPIClient",
    "ActivityType",
]

from enum import Enum
from typing import Any, Dict, List, Union

from src.core import constants
from src.core.clients.base_api_client import BaseAPIClient
from src.core.exceptions import APIException
from src.core.loggers import logger
from src.interfaces.strava import StravaService
from src.schemas.strava_activity_response import StravaActivity, StravaServiceResponse
from src.services.strava.utils import refresh_strava_token

log = logger


class Constants(constants.Constants):
    STRAVA_API_BASE_URL = "https://www.strava.com/api/v3"
    STRAVA_ATHLETE_ENDPOINT = "/athlete"
    STRAVA_ACTIVITIES_ENDPOINT = "/athlete/activities"
    STRAVA_ACTIVITY_LIMIT = 10
    pass


class ActivityType(str, Enum):
    RECENT_RUNS = "recent_runs"
    RECENT_ACTIVITIES = "recent_activities"
    ATHLETE_PROFILE = "athlete_profile"


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

    def get_recent_activities(self, limit: int = Constants.STRAVA_ACTIVITY_LIMIT) -> list[dict]:
        url = Constants.STRAVA_ACTIVITIES_ENDPOINT
        params = {"per_page": limit, "page": 1}
        response = self.api_client.get(url, headers=self._headers(), params=params)
        activities = response.get_json()
        return activities

    def get_recent_runs(self, limit: int = Constants.STRAVA_ACTIVITY_LIMIT) -> list[dict]:
        activities = self.get_recent_activities(limit=limit)
        return [a for a in activities if a["type"] == "Run"]

    def _load_access_token(self) -> str:
        import os

        from dotenv import load_dotenv

        load_dotenv(Constants.ENV_FILE, override=True)
        access_token = os.getenv("STRAVA_ACCESS_TOKEN")
        if not access_token:
            raise ValueError("STRAVA_ACCESS_TOKEN not found in .env file")
        return access_token

    def _get_data_by_type(
        self, activity_type: ActivityType, limit: int = None
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Get different types of Strava data with proper retry logic.

        Args:
            activity_type: Type of data to retrieve
            limit: Optional limit for activities (ignored for athlete profile)

        Returns:
            Dictionary for athlete profile, List for activities

        Raises:
            APIException: If all retry attempts fail
        """
        method_mapping = {
            ActivityType.RECENT_RUNS: lambda: self.get_recent_runs(limit or Constants.STRAVA_ACTIVITY_LIMIT),
            ActivityType.RECENT_ACTIVITIES: lambda: self.get_recent_activities(
                limit or Constants.STRAVA_ACTIVITY_LIMIT
            ),
            ActivityType.ATHLETE_PROFILE: lambda: self.get_athlete_profile(),
        }

        method = method_mapping.get(activity_type)
        if not method:
            raise ValueError(f"Unsupported activity type: {activity_type}")

        retry_count = 0
        max_retries = 3
        last_exception = None

        while retry_count < max_retries:
            try:
                return method()
            except APIException as e:
                log.warning(f"API call failed (attempt {retry_count + 1}/{max_retries}): {str(e)}")
                last_exception = e
                retry_count += 1

        raise APIException(f"Failed to retrieve data after {max_retries} attempts") from last_exception

    def get_activities(self, activity_type: ActivityType, limit: int = None) -> StravaServiceResponse:
        """
        Get activities as parsed Pydantic models.

        Returns:
            List of StravaActivity models
        """
        raw_data = self._get_data_by_type(activity_type, limit)

        if activity_type == ActivityType.ATHLETE_PROFILE:
            return []

        if not isinstance(raw_data, list):
            raise ValueError(f"Expected list for {activity_type}, got {type(raw_data)}")

        activities = []
        for item in raw_data:
            try:
                activity = StravaActivity(**item)
                activities.append(activity)
            except Exception as e:
                log.warning(f"Failed to parse activity: {str(e)}")
                continue

        return StravaServiceResponse(activities=activities)


def main():
    strava_api_client = StravaAPIClient()
    runs_models = strava_api_client.get_activities(ActivityType.RECENT_RUNS, limit=5)

    for run in runs_models:
        print(run.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
