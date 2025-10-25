__all__ = [
    "TrainingLoadService",
]

from datetime import datetime, timedelta, timezone

from src.core import constants
from src.core.loggers import logger
from src.schemas.strava_activity_response_schema import StravaActivity
from src.services.strava.strava_api_client import ActivityType, StravaAPIClient

log = logger


class Constants(constants.Constants):
    TRAINING_LOAD_ACTIVITIES_LIMIT = 100
    TRAINING_LOAD_DEFAULT_WEEKS = 4


class TrainingLoadService:
    def __init__(self, strava_client: StravaAPIClient):
        self.strava_client = strava_client
        self.activities: list[StravaActivity] = list()

    def get_baseline_weekly_mileage(self, weeks: int) -> float:
        """
        Calculate average weekly mileage over the past N weeks.

        Args:
            weeks: Number of weeks to analyze for baseline (default: 4)

        Returns:
            Average weekly mileage in kilometers
        """
        self.activities = self.strava_client.get_activities(
            ActivityType.RECENT_RUNS, limit=Constants.TRAINING_LOAD_ACTIVITIES_LIMIT
        ).activities

        if not self.activities:
            return 0.0

        cutoff_date = datetime.now(timezone.utc) - timedelta(weeks=weeks)
        baseline_activities = [activity for activity in self.activities if activity.start_date_local >= cutoff_date]
        earliest_activity_date = min(activity.start_date_local for activity in baseline_activities)
        data_history_weeks = (datetime.now(timezone.utc) - earliest_activity_date).days / 7

        if not baseline_activities:
            return 0.0

        total_distance = sum(activity.distance for activity in baseline_activities)

        if data_history_weeks < (weeks - 1):
            log.warning(
                f"Requested {weeks} weeks but only {data_history_weeks:.1f} weeks of data available. "
                f"Using available data for baseline calculation."
            )
            actual_weeks = max(1, data_history_weeks)
            return round(total_distance / actual_weeks, 2)

        return round(total_distance / weeks, 2)


if __name__ == "__main__":
    strava_client = StravaAPIClient()
    training_load_service = TrainingLoadService(strava_client=strava_client)
    baseline_mileage = training_load_service.get_baseline_weekly_mileage(weeks=Constants.TRAINING_LOAD_DEFAULT_WEEKS)
    log.info(f"Baseline Weekly Mileage over last {Constants.TRAINING_LOAD_DEFAULT_WEEKS} weeks: {baseline_mileage} km")
