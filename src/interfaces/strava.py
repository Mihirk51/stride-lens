__all__ = [
    "StravaService",
]

from abc import ABC, abstractmethod
from typing import Any, List


class StravaService(ABC):
    @abstractmethod
    def get_athlete_profile(self) -> dict:
        """Fetch athlete profile info."""
        pass

    @abstractmethod
    def get_recent_runs(self, limit: int = 10) -> List[Any]:
        """Fetch recent run activities."""
        pass
