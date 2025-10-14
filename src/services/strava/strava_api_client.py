__all__ = [
    "StravaAPIClient",
    "ActivityType",
]

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Union

from src.core import constants
from src.core.clients.base_api_client import BaseAPIClient
from src.core.exceptions import APIException
from src.core.loggers import logger
from src.interfaces.strava import StravaService
from src.schemas.strava_activity_response_schema import StravaActivity, StravaServiceResponse
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


def ensure_token(func):
    def wrapper(self, *args, **kwargs):
        self._update_token()
        return func(self, *args, **kwargs)

    return wrapper


class StravaAPIClient(StravaService):
    def __init__(self):
        self.access_token, self.token_expiry = refresh_strava_token(target_obj=self)
        self.api_client = BaseAPIClient(base_url=Constants.STRAVA_API_BASE_URL)

    def _headers(self):
        return {"Authorization": f"Bearer {self.access_token}"}

    def _get_athlete_profile(self) -> dict:
        url = Constants.STRAVA_ATHLETE_ENDPOINT
        response = self.api_client.get(url, headers=self._headers())
        return response.get_json()

    def _get_recent_activities(self, limit: int = Constants.STRAVA_ACTIVITY_LIMIT) -> list[dict]:
        url = Constants.STRAVA_ACTIVITIES_ENDPOINT
        params = {"per_page": limit, "page": 1}
        response = self.api_client.get(url, headers=self._headers(), params=params)
        activities = response.get_json()
        return activities

    def _get_recent_runs(self, limit: int = Constants.STRAVA_ACTIVITY_LIMIT) -> list[dict]:
        activities = self._get_recent_activities(limit=limit)
        return [a for a in activities if a["type"] == "Run"]

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
            ActivityType.RECENT_RUNS: lambda: self._get_recent_runs(limit or Constants.STRAVA_ACTIVITY_LIMIT),
            ActivityType.RECENT_ACTIVITIES: lambda: self._get_recent_activities(
                limit or Constants.STRAVA_ACTIVITY_LIMIT
            ),
            ActivityType.ATHLETE_PROFILE: lambda: self._get_athlete_profile(),
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

    @ensure_token
    def get_activities(self, activity_type: ActivityType, limit: int = None) -> StravaServiceResponse:
        """
        Get activities as parsed Pydantic models.

        Returns:
            List of StravaActivity models
        """
        athlete_profile = self._get_athlete_profile()

        if activity_type == ActivityType.ATHLETE_PROFILE:
            return StravaServiceResponse(activities=[], athlete_profile=athlete_profile)

        raw_data = self._get_data_by_type(activity_type, limit)

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

        return StravaServiceResponse(activities=activities, athlete_profile=athlete_profile)

    def _update_token(self):
        if self.token_expiry < datetime.now().isoformat():
            log.info("Strava token expired or about to expire, refreshing...")
            self.access_token, self.token_expiry = refresh_strava_token(target_obj=self)
        else:
            log.info("Strava token still valid.")


def main():
    strava_api_client = StravaAPIClient()
    runs_models = strava_api_client.get_activities(ActivityType.RECENT_RUNS, limit=5)

    for run in runs_models:
        print(run.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
