__all__ = [
    "ManualSleepService",
]

from src.interfaces import SleepService
from src.schemas.manual_sleep_and_recovery import (
    ManualSleepInput,
    ManualSleepObjectiveInput,
    ManualSleepSubjectiveInput,
)


class ManualSleepService(SleepService):
    def __init__(self):
        self.fields_provided = 0

    def record_sleep(self, data: ManualSleepInput) -> dict:
        if isinstance(data, ManualSleepSubjectiveInput):
            return {
                "score": data.subjective_rating,
                "method": "subjective_rating",
                "warning": "Score is based only on subjective rating. Accuracy may be limited.",
            }

        elif isinstance(data, ManualSleepObjectiveInput):
            score, warning = self._calculate_score(data)
            return {
                "score": score,
                "method": "manual_metrics",
                "details": data.dict(exclude_none=True),
                "warning": warning,
            }

        else:
            return {
                "score": None,
                "method": "invalid",
                "warning": "No valid sleep input provided. Scores may not be accurate.",
            }

    def _calculate_score(self, data: ManualSleepInput) -> float:
        """Improved heuristic: normalize against healthy ranges + weighted average"""

        weights = {
            "sleep_score_percent": 0.5,
            "recovery_percent": 0.3,
            "deep_sleep_minutes": 0.2,
            "rem_sleep_minutes": 0.15,
            "core_sleep_minutes": 0.05,
            "time_awake_minutes": -0.2,
            "time_in_bed_minutes": 0.05,
        }

        def normalize_minutes(field: str, value: int) -> float:
            if field == "deep_sleep_minutes":
                return min(value / 120 * 100, 100)  # 90–120 is optimal
            elif field == "rem_sleep_minutes":
                return min(value / 120 * 100, 100)
            elif field == "core_sleep_minutes":
                return min(value / 270 * 100, 100)
            elif field == "time_in_bed_minutes":
                return min(value / 480 * 100, 100)  # 8h = 100
            elif field == "time_awake_minutes":
                return max(100 - (value / 60 * 100), 0)  # <=20 min awake is ideal
            return float(value)

        total_weight, weighted_sum = 0, 0
        for field, weight in weights.items():
            value = getattr(data, field, None)
            if value is not None:
                self.fields_provided += 1
                normalized = normalize_minutes(field, value) if "minutes" in field else value
                weighted_sum += normalized * abs(weight)
                total_weight += abs(weight)

        score = round(weighted_sum / total_weight, 2) if total_weight > 0 else 50.0

        warning = None
        if self.fields_provided < 3:
            warning = "Score may not be accurate due to limited input data."

        return score, warning
