__all__ = [
    "BaseSleepService",
]

from abc import ABC
from typing import Any, Dict, Optional

from src.interfaces.sleep import SleepService


class BaseSleepService(SleepService, ABC):
    """
    Base class for all sleep services.
    Provides shared helpers for score calculation, normalization, and warnings.
    """

    def _normalize_minutes(self, field: str, value: int) -> float:
        if field == "deep_sleep_minutes":
            return min(value / 120 * 100, 100)
        elif field == "rem_sleep_minutes":
            return min(value / 120 * 100, 100)
        elif field == "core_sleep_minutes":
            return min(value / 270 * 100, 100)
        elif field == "time_in_bed_minutes":
            return min(value / 480 * 100, 100)
        elif field == "time_awake_minutes":
            return max(100 - (value / 60 * 100), 0)
        return float(value)

    def _calculate_score(self, metrics: Dict[str, Any]) -> float:
        """
        Generic weighted scoring algorithm.
        Subclasses can override this for custom provider-specific logic.
        """
        weights = {
            "sleep_score_percent": 0.5,
            "recovery_percent": 0.3,
            "deep_sleep_minutes": 0.2,
            "rem_sleep_minutes": 0.15,
            "core_sleep_minutes": 0.05,
            "time_awake_minutes": -0.2,
            "time_in_bed_minutes": 0.05,
        }

        total_weight, weighted_sum = 0, 0
        for field, weight in weights.items():
            value = metrics.get(field, None)
            if value is not None:
                normalized = self._normalize_minutes(field, value) if "minutes" in field else value
                weighted_sum += normalized * abs(weight)
                total_weight += abs(weight)

        return round(weighted_sum / total_weight, 2) if total_weight > 0 else 50.0

    def _add_warning_if_incomplete(self, metrics: Dict[str, Any]) -> Optional[str]:
        """
        Warn the user if insufficient data was provided.
        """
        if not metrics:
            return "No sleep data provided. Scores may not be accurate."

        warning = None

        avaiable_fields = set(metrics.keys())
        if len(avaiable_fields) < 3:
            warning = "Score may not be accurate due to limited input data."

        return warning
