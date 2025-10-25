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

    def calculate_7_days_load(self) -> float:
        """Calculate mileage for the past 7 days (rolling window)."""
        activities = (
            self.strava_client.get_activities(
                ActivityType.RECENT_RUNS,
                limit=20,
            ).activities
            if not self.activities
            else self.activities
        )
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)

        recent_activities = [activity for activity in activities if activity.start_date_local >= seven_days_ago]

        return sum(activity.distance for activity in recent_activities)

    def calculate_training_load_ratio(self, weeks_baseline: int = 4) -> dict:
        """
        Calculate training load ratio: current week / baseline average.

        Returns:
            Dictionary with load metrics and interpretation
        """
        baseline = self.get_baseline_weekly_mileage(weeks=weeks_baseline)
        current = self.calculate_7_days_load()

        if not baseline:
            ratio = None
            interpretation = "insufficient_baseline"
        else:
            ratio = round(current / baseline + 1e-6, 2)

            if ratio < 0.7:
                interpretation = "considerably undertraining"
            elif ratio < 0.9:
                interpretation = "lighty undertraining"
            elif ratio <= 1.1:
                interpretation = "normal"
            elif ratio <= 1.3:
                interpretation = "moderately overtraining"
            elif ratio <= 1.5:
                interpretation = "highly overtraining"
            else:
                interpretation = "very highly overtraining"

        return {
            "current_week_km": current,
            "baseline_weekly_km": baseline,
            "load_ratio": ratio,
            "interpretation": interpretation,
            "weeks_analyzed": weeks_baseline,
        }

    def calculate_acute_chronic_ratio(self) -> dict:
        """
        Calculate Acute:Chronic Workload Ratio (ACWR).

        ACWR = ATL (7 days) / CTL (28 days)

        Research shows:
        - 0.8-1.3: Sweet spot (optimal adaptation)
        - 1.3-1.5: Moderate risk
        - >1.5: High injury risk
        - <0.8: Detraining risk
        """
        atl = self.calculate_7_days_load()
        ctl = self.get_baseline_weekly_mileage(weeks=Constants.TRAINING_LOAD_DEFAULT_WEEKS)

        if ctl == 0:
            return {
                "acute_load_km": atl,
                "chronic_load_km": ctl,
                "acwr": None,
                "interpretation": "insufficient_baseline",
            }

        acwr = round(atl / ctl, 2)

        if acwr < 0.8:
            interpretation = "detraining_risk"
        elif acwr <= 1.3:
            interpretation = "optimal"
        elif acwr <= 1.5:
            interpretation = "moderate_risk"
        else:
            interpretation = "high_injury_risk"

        return {
            "acute_load_km": atl,
            "chronic_load_km": ctl,
            "acwr": acwr,
            "interpretation": interpretation,
        }


if __name__ == "__main__":
    strava_client = StravaAPIClient()
    training_load_service = TrainingLoadService(strava_client=strava_client)
    acute_chronic_ratio = training_load_service.calculate_acute_chronic_ratio()
