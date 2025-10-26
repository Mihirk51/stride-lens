__all__ = [
    "ITrainingLoadService",
]

from abc import ABC, abstractmethod


class ITrainingLoadService(ABC):
    @abstractmethod
    def get_baseline_weekly_mileage(self, weeks: int) -> float:
        """Calculate baseline weekly mileage over a specified number of weeks."""
        pass

    @abstractmethod
    def calculate_7_days_load(self) -> float:
        """Calculate mileage for the past 7 days (rolling window)."""
        pass

    @abstractmethod
    def calculate_training_load_ratio(self, weeks_baseline: int = 4) -> dict:
        """
        Calculate training load ratio: current week / baseline average.

        Returns:
            Dictionary with load metrics and interpretation
        """
        pass

    @abstractmethod
    def calculate_acute_chronic_ratio(self) -> dict:
        """
        Calculate acute to chronic training load ratio.

        Returns:
            Dictionary with acute load, chronic load, ratio, and interpretation
        """
        pass
