__all__ = [
    "TrainingLoadService",
]

from datetime import datetime, timedelta, timezone

from src.core import constants
from src.core.clients.base_api_client import BaseAPIClient
from src.core.loggers import logger
from src.interfaces.training_load import ITrainingLoadService
from src.schemas.strava_activity_schema import StravaActivity
from src.schemas.training_load_schema import (
    ACWRInterpretation,
    ACWRResponse,
    TrainingLoadInterpretation,
    TrainingLoadRatioResponse,
)
from src.services.strava.strava_api_client import ActivityType, StravaAPIClient

log = logger


class Constants(constants.Constants):
    TRAINING_LOAD_ACTIVITIES_LIMIT = 100
    TRAINING_LOAD_DEFAULT_WEEKS = 4


class TrainingLoadService(ITrainingLoadService):
    def __init__(self, strava_client: StravaAPIClient):
        self.strava_client = strava_client
        self.activities: list[StravaActivity] = list()

    def _load_activities(self, lookback_days: int = 28) -> None:
        """Fetch activities explicitly before calculations."""
        after_timestamp = int((datetime.now(timezone.utc) - timedelta(days=lookback_days)).timestamp())
        self.activities = self.strava_client.get_activities(ActivityType.RECENT_RUNS, after=after_timestamp).activities

        return self.activities

    def get_baseline_weekly_mileage(self, weeks: int) -> float:
        """
        Calculate average weekly mileage over the past N weeks.

        Args:
            weeks: Number of weeks to analyze for baseline (default: 4)

        Returns:
            Average weekly mileage in kilometers
        """
        if not self.activities:
            self._load_activities(lookback_days=weeks * 7)

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
        activities = self._load_activities() if not self.activities else self.activities
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)

        recent_activities = [activity for activity in activities if activity.start_date_local >= seven_days_ago]

        return sum(activity.distance for activity in recent_activities)

    def calculate_training_load_ratio(self, weeks_baseline: int = 4) -> TrainingLoadRatioResponse:
        """
        Calculate training load ratio: current week / baseline average.

        Returns:
            TrainingLoadRatioResponse with load metrics and interpretation
        """
        baseline = self.get_baseline_weekly_mileage(weeks=weeks_baseline)
        current = self.calculate_7_days_load()

        if not baseline:
            return TrainingLoadRatioResponse(
                current_week_km=round(current, 2),
                baseline_weekly_km=0.0,
                load_ratio=None,
                interpretation=TrainingLoadInterpretation.INSUFFICIENT_BASELINE,
                weeks_analyzed=weeks_baseline,
            )

        ratio = round(current / baseline, 2)

        if ratio < 0.7:
            interpretation = TrainingLoadInterpretation.CONSIDERABLY_UNDERTRAINING
        elif ratio < 0.9:
            interpretation = TrainingLoadInterpretation.LIGHTLY_UNDERTRAINING
        elif ratio <= 1.1:
            interpretation = TrainingLoadInterpretation.NORMAL
        elif ratio <= 1.3:
            interpretation = TrainingLoadInterpretation.MODERATELY_OVERTRAINING
        elif ratio <= 1.5:
            interpretation = TrainingLoadInterpretation.HIGHLY_OVERTRAINING
        else:
            interpretation = TrainingLoadInterpretation.VERY_HIGHLY_OVERTRAINING

        return TrainingLoadRatioResponse(
            current_week_km=round(current, 2),
            baseline_weekly_km=round(baseline, 2),
            load_ratio=ratio,
            interpretation=interpretation,
            weeks_analyzed=weeks_baseline,
        )

    def calculate_acute_chronic_ratio(self) -> ACWRResponse:
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
            return ACWRResponse(
                acute_load_km=round(atl, 2),
                chronic_load_km=0.0,
                acwr=None,
                interpretation=ACWRInterpretation.INSUFFICIENT_BASELINE,
            )

        acwr = round(atl / ctl, 2)

        if acwr < 0.8:
            interpretation = ACWRInterpretation.DETRAINING_RISK
        elif acwr <= 1.3:
            interpretation = ACWRInterpretation.OPTIMAL
        elif acwr <= 1.5:
            interpretation = ACWRInterpretation.MODERATE_RISK
        else:
            interpretation = ACWRInterpretation.HIGH_INJURY_RISK

        return ACWRResponse(
            acute_load_km=round(atl, 2),
            chronic_load_km=round(ctl, 2),
            acwr=acwr,
            interpretation=interpretation,
        )


if __name__ == "__main__":
    api_client = BaseAPIClient(base_url=Constants.STRAVA_API_BASE_URL)
    strava_client = StravaAPIClient(api_client)
    training_load_service = TrainingLoadService(strava_client=strava_client)
    acute_chronic_ratio = training_load_service.calculate_acute_chronic_ratio()
    training_load_ratio = training_load_service.calculate_training_load_ratio()
