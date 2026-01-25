"""
Adapter layer that bridges service layer and domain layer.
Fetches data from services and transforms into domain models.
"""

__all__ = [
    "DataProvider",
]

from datetime import datetime, timedelta, timezone
from typing import Optional

from src.core import constants
from src.domain.models import (
    RecentRunTrends,
    SingleRun,
    SleepReadiness,
    TrainingLoadSummary,
    WeatherConditions,
)
from src.schemas.weather_api_schema import CurrentWeatherRequestParams
from src.services.lat_lon import LatLonService
from src.services.sleep_and_recovery import ManualSleepService
from src.services.strava import ActivityType, StravaAPIClient
from src.services.training_load import TrainingLoadService
from src.services.weather import OpenMeteoWeatherAPIClient


class Constants(constants.Constants):
    LOAD_RATIO_BASELINE_WEEKS = 8
    AFTER_TIMESTAMP_DAYS = 28


AFTER_TIMESTAMP = int((datetime.now(timezone.utc) - timedelta(days=Constants.AFTER_TIMESTAMP_DAYS)).timestamp())


class DataProvider:
    """
    Adapter that fetches data from services and transforms into domain models.
    This is the bridge between the service layer and domain scoring logic.
    """

    def __init__(
        self,
        strava_client: StravaAPIClient,
        weather_client: OpenMeteoWeatherAPIClient,
        training_load_service: TrainingLoadService,
        lat_lon_service: LatLonService,
        sleep_service: Optional[ManualSleepService] = None,
    ):
        self.strava_client = strava_client
        self.weather_client = weather_client
        self.training_load_service = training_load_service
        self.lat_lon_service = lat_lon_service
        self.sleep_service = sleep_service

    def get_weather_conditions(self) -> WeatherConditions:
        """Fetch current weather and transform to domain model."""
        lat_lon = self.lat_lon_service.get_lat_lon()
        request_params = CurrentWeatherRequestParams(latitude=lat_lon.latitude, longitude=lat_lon.longitude)

        weather_response = self.weather_client.get_current_weather(request_params)

        return WeatherConditions(
            timestamp=datetime.fromisoformat(weather_response.current.time),
            temperature_c=weather_response.current.temperature_2m,
            humidity_percent=weather_response.current.relative_humidity_2m,
            wind_speed_mph=weather_response.current.wind_speed_10m,
            wind_gusts_mph=weather_response.current.wind_gusts_10m,
            precipitation_mm=weather_response.current.precipitation,
            is_day=bool(weather_response.current.is_day),
            timezone=weather_response.timezone,
        )

    def get_training_load_summary(self) -> TrainingLoadSummary:
        """Fetch training load data and transform to domain model."""
        acwr_response = self.training_load_service.calculate_acute_chronic_ratio()
        load_ratio_response = self.training_load_service.calculate_training_load_ratio(
            weeks_baseline=Constants.LOAD_RATIO_BASELINE_WEEKS
        )

        activities = self.strava_client.get_activities(ActivityType.RECENT_RUNS, after=AFTER_TIMESTAMP).activities

        days_since_last_run = 0
        consecutive_days = 0
        if activities:
            last_run_date = activities[-1].start_date_local
            days_since_last_run = (datetime.now(timezone.utc) - last_run_date).days

            consecutive_days = self._calculate_consecutive_days(activities)

        return TrainingLoadSummary(
            calculated_at=datetime.now(timezone.utc),
            acute_load_km=acwr_response.acute_load_km,
            chronic_load_km=acwr_response.chronic_load_km,
            acwr=acwr_response.acwr or 0.0,
            load_ratio=load_ratio_response.load_ratio or 0.0,
            days_since_last_run=days_since_last_run,
            consecutive_training_days=consecutive_days,
        )

    def get_recent_run_trends(self) -> RecentRunTrends:
        """Fetch recent runs and transform to domain model."""
        activities_response = self.strava_client.get_activities(ActivityType.RECENT_RUNS, after=AFTER_TIMESTAMP)

        recent_runs = []
        for activity in activities_response.activities:
            recent_runs.append(
                SingleRun(
                    id=activity.id,
                    name=activity.name,
                    distance_km=activity.distance,
                    moving_time_minutes=self._parse_moving_time_to_minutes(activity.moving_time),
                    elevation_gain_m=activity.total_elevation_gain,
                    date=activity.start_date_local,
                    avg_pace_min_per_km=self._parse_pace_to_minutes(activity.average_speed),
                    avg_heartrate=int(activity.average_heartrate) if activity.average_heartrate else None,
                    max_heartrate=int(activity.max_heartrate) if activity.max_heartrate else None,
                )
            )

        now = datetime.now(timezone.utc)
        runs_7_days = sum(1 for run in recent_runs if (now - run.date).days <= 7)
        runs_28_days = len(recent_runs)

        distance_7_days = sum(run.distance_km for run in recent_runs if (now - run.date).days <= 7)
        distance_28_days = sum(run.distance_km for run in recent_runs)

        days_since_last = (now - recent_runs[-1].date).days if recent_runs else None

        return RecentRunTrends(
            calculated_at=now,
            recent_runs=recent_runs,
            runs_last_7_days=runs_7_days,
            runs_last_30_days=runs_28_days,
            total_distance_last_7_days_km=distance_7_days,
            total_distance_last_30_days_km=distance_28_days,
            days_since_last_run=days_since_last,
        )

    def get_sleep_readiness(self) -> SleepReadiness:
        """
        Get sleep readiness data if available.
        For now, returns manual input if provided, otherwise None.
        """

        manual_sleep = {
            "awake_minutes": 30,
            "rem_sleep_minutes": 53,
            "core_sleep_minutes": 232,
            "deep_sleep_minutes": 79,
            "recovery_percent": 52,
            "sleep_score_percent": 72,
            "score": 61.21,
        }  # add logic to fetch from service if available

        return SleepReadiness(
            date=datetime.now(timezone.utc),
            data_source="manual",
            **manual_sleep,
        )

    @staticmethod
    def _calculate_consecutive_days(activities) -> int:
        """Calculate consecutive training days from activities."""
        if not activities:
            return 0

        activities_sorted = sorted(activities, key=lambda x: x.start_date_local, reverse=True)

        consecutive = 0
        current_date = datetime.now(timezone.utc).date()

        for activity in activities_sorted:
            activity_date = activity.start_date_local.date()

            if activity_date == current_date:
                consecutive += 1
                current_date = current_date.replace(day=current_date.day - 1)
            elif (current_date - activity_date).days == 1:
                consecutive += 1
                current_date = activity_date
            else:
                break

        return consecutive

    @staticmethod
    def _parse_moving_time_to_minutes(time_str: str) -> int:
        """Convert 'HH:MM:SS' or 'MM:SS' format to total minutes."""
        parts = time_str.split(":")
        if len(parts) == 3:
            hours, minutes, seconds = map(int, parts)
            return hours * 60 + minutes + (1 if seconds > 30 else 0)
        elif len(parts) == 2:
            minutes, seconds = map(int, parts)
            return minutes + (1 if seconds > 30 else 0)
        return 0

    @staticmethod
    def _parse_pace_to_minutes(pace_str: Optional[str]) -> Optional[float]:
        """Convert 'MM:SS' pace format to decimal minutes per km."""
        if not pace_str:
            return None

        try:
            parts = pace_str.split(":")
            if len(parts) == 2:
                minutes, seconds = map(int, parts)
                return minutes + seconds / 60
        except (ValueError, AttributeError):
            return None

        return None
