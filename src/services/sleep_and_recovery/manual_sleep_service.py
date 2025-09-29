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

    def _calculate_score(self, data: ManualSleepObjectiveInput) -> tuple[float, str]:
        """Simple heuristic: weighted average of available fields.
        Returns (score, warning).
        """
        weights = {
            "time_in_bed_minutes": 0.1,
            "time_awake_minutes": -0.1,
            "rem_sleep_minutes": 0.2,
            "core_sleep_minutes": 0.2,
            "deep_sleep_minutes": 0.3,
            "recovery_percent": 0.3,
            "sleep_score_percent": 0.5,
        }

        total_weight, weighted_sum = 0, 0
        fields_provided = 0

        for field, weight in weights.items():
            value = getattr(data, field, None)
            if value is not None:
                fields_provided += 1
                if "minutes" in field:
                    normalized = min(value / 480 * 100, 100)
                else:
                    normalized = value
                weighted_sum += normalized * abs(weight)
                total_weight += abs(weight)

        score = round(weighted_sum / total_weight, 2) if total_weight > 0 else 50.0

        warning = None
        if fields_provided < 3:
            warning = "Score may not be accurate due to limited input data."

        return score, warning
