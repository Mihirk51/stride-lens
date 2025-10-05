__all__ = [
    "StravaService",
]
from abc import ABC, abstractmethod
from typing import Any, List

from src.schemas.strava_activity_response import StravaActivity


class StravaService(ABC):
    @abstractmethod
    def get_athlete_profile(self) -> dict:
        """Fetch athlete profile info."""
        pass

    @abstractmethod
    def get_recent_runs(self, limit: int = 10) -> List[Any]:
        """Fetch recent run activities."""
        pass

    @abstractmethod
    def get_recent_activities(self, limit: int = 10) -> List[Any]:
        """Fetch recent activities."""
        pass

    @abstractmethod
    def get_activities(self, activity_type, limit: int = None) -> List[StravaActivity]:
        """Fetch activities based on type."""
        pass
