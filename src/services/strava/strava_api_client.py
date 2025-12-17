__all__ = [
    "StravaAPIClient",
    "ActivityType",
]

from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from src.core import constants
from src.core.clients.base_api_client import BaseAPIClient
from src.core.exceptions import APIException
from src.core.loggers import logger
from src.interfaces.strava import StravaService
from src.schemas.strava_activity_schema import StravaActivity, StravaServiceResponse
from src.services.strava.utils import refresh_strava_token

AFTER_TIMESTAMP = int((datetime.now(timezone.utc) - timedelta(days=30)).timestamp())  # 28 days ago

log = logger
EpochTimestamp = int


class Constants(constants.Constants):
    STRAVA_ATHLETE_ENDPOINT = "/athlete"
    STRAVA_ACTIVITIES_ENDPOINT = "/athlete/activities"
    STRAVA_ACTIVITY_LIMIT = 100


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
    def __init__(self, api_client: BaseAPIClient):
        self.access_token, self.token_expiry = refresh_strava_token(target_obj=self)
        self.api_client = api_client

    def _headers(self):
        return {"Authorization": f"Bearer {self.access_token}"}

    def _get_athlete_profile(self) -> dict:
        url = Constants.STRAVA_ATHLETE_ENDPOINT
        response = self.api_client.get(url, headers=self._headers())
        return response.get_json()

    def _get_recent_activities(
        self,
        limit: int = Constants.STRAVA_ACTIVITY_LIMIT,
        before: Optional[EpochTimestamp] = None,
        after: Optional[EpochTimestamp] = None,
    ) -> list[dict]:
        url = Constants.STRAVA_ACTIVITIES_ENDPOINT
        params = {
            "per_page": limit,
            "page": 1,
            "before": before,
            "after": after,
        }
        response = self.api_client.get(url, headers=self._headers(), params=params)
        activities = response.get_json()
        return activities

    def _get_recent_runs(
        self,
        limit: int = Constants.STRAVA_ACTIVITY_LIMIT,
        before: Optional[EpochTimestamp] = None,
        after: Optional[EpochTimestamp] = None,
    ) -> list[dict]:
        activities = self._get_recent_activities(limit=limit, before=before, after=after)
        return [a for a in activities if a["type"] == "Run"]

    def _get_data_by_type(
        self,
        activity_type: ActivityType,
        limit: int = None,
        before: Optional[EpochTimestamp] = None,
        after: Optional[EpochTimestamp] = None,
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
            ActivityType.RECENT_RUNS: lambda: self._get_recent_runs(
                limit or Constants.STRAVA_ACTIVITY_LIMIT, before, after
            ),
            ActivityType.RECENT_ACTIVITIES: lambda: self._get_recent_activities(
                limit or Constants.STRAVA_ACTIVITY_LIMIT, before, after
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

    @staticmethod
    def _meters_to_kilometers(meters: float) -> float:
        """Convert meters to kilometers."""
        return round(meters / 1000, 2)

    @staticmethod
    def _seconds_to_mmss(seconds: int) -> str:
        """Convert seconds to MM:SS format."""
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"

    @staticmethod
    def _speed_ms_to_pace_per_km(speed_ms: float) -> str:
        """
        Convert speed in m/s to pace in MM:SS/km format.

        Args:
            speed_ms: Speed in meters per second

        Returns:
            Pace string in MM:SS/km format (e.g., "05:30")
        """
        if speed_ms == 0:
            return "00:00"

        seconds_per_km = 1000 / speed_ms

        minutes = int(seconds_per_km // 60)
        seconds = int(seconds_per_km % 60)

        return f"{minutes:02d}:{seconds:02d}"

    def _convert_units(self, activity_data: dict) -> dict:
        """
        Convert activity units from Strava API raw data to desired format.

        This method transforms the raw API response dictionary before creating
        a StravaActivity object.

        Conversions:
        - Distance: meters → kilometers
        - Moving time: seconds (int) → MM:SS (string)
        - Average speed: m/s (float) → MM:SS/km (string)
        - Max speed: m/s (float) → MM:SS/km (string)

        Args:
            activity_data: Raw activity data dictionary from Strava API

        Returns:
            Converted activity data dictionary
        """
        converted = activity_data.copy()

        if "distance" in converted:
            converted["distance"] = self._meters_to_kilometers(converted["distance"])

        if "moving_time" in converted:
            converted["moving_time"] = self._seconds_to_mmss(converted["moving_time"])

        if converted.get("average_speed") is not None:
            converted["average_speed"] = self._speed_ms_to_pace_per_km(converted["average_speed"])

        if converted.get("max_speed") is not None:
            converted["max_speed"] = self._speed_ms_to_pace_per_km(converted["max_speed"])

        return converted

    @ensure_token
    def get_activities(
        self,
        activity_type: ActivityType,
        limit: int = None,
        before: Optional[EpochTimestamp] = None,
        after: Optional[EpochTimestamp] = None,
    ) -> StravaServiceResponse:
        """
        Get activities as parsed Pydantic models.

        Returns:
            List of StravaActivity models
        """
        athlete_profile = self._get_athlete_profile()

        if activity_type == ActivityType.ATHLETE_PROFILE:
            return StravaServiceResponse(activities=[], athlete_profile=athlete_profile)

        raw_data = self._get_data_by_type(activity_type, limit, before, after)

        if not isinstance(raw_data, list):
            raise ValueError(f"Expected list for {activity_type}, got {type(raw_data)}")

        activities = []
        for item in raw_data:
            try:
                converted_activity = self._convert_units(item)
                activity = StravaActivity(**converted_activity)
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
    api_client = BaseAPIClient(base_url=Constants.STRAVA_API_BASE_URL)
    strava_api_client = StravaAPIClient(api_client)
    runs_models = strava_api_client.get_activities(ActivityType.RECENT_RUNS, after=AFTER_TIMESTAMP).activities
    for run in runs_models:
        print(run.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
