__all__ = [
    "StravaService",
]
from abc import ABC, abstractmethod
from typing import List

from src.schemas.strava_activity_response_schema import StravaServiceResponse


class StravaService(ABC):
    @abstractmethod
    def _get_athlete_profile(self) -> dict:
        """Fetch athlete profile info."""
        pass

    @abstractmethod
    def _get_recent_runs(self, limit: int = 10) -> List[dict]:
        """Fetch recent run activities."""
        pass

    @abstractmethod
    def _get_recent_activities(self, limit: int = 10) -> List[dict]:
        """Fetch recent activities."""
        pass

    @abstractmethod
    def get_activities(self, activity_type, limit: int = None) -> StravaServiceResponse:
        """Fetch activities based on type."""
        pass
