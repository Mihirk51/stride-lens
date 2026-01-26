__all__ = [
    "ManualSleepService",
]

from src.schemas.manual_sleep_and_recovery_schema import (
    ManualSleepInput,
    ManualSleepObjectiveInput,
    ManualSleepServiceResponse,
    ManualSleepSubjectiveInput,
)
from src.services.sleep_and_recovery.base_sleep_service import BaseSleepService


class ManualSleepService(BaseSleepService):
    """
    Manual sleep service - returns raw sleep metrics without scoring.
    Scoring is handled by SleepReadinessComponent in the domain layer.
    """

    def record_sleep(self, data: ManualSleepInput) -> ManualSleepServiceResponse:
        """Record sleep data and return raw metrics (no score calculation)."""
        if isinstance(data, ManualSleepSubjectiveInput):
            return ManualSleepServiceResponse(
                method="subjective_rating",
                details={"subjective_rating": data.subjective_rating},
                warning="Score is based only on subjective rating. Use objective metrics for better accuracy.",
            )

        elif isinstance(data, ManualSleepObjectiveInput):
            metrics = data.dict(exclude_none=True)

            return ManualSleepServiceResponse(
                method="manual_metrics",
                details=metrics,
                warning=self._add_warning_if_incomplete(metrics),
            )

        else:
            return ManualSleepServiceResponse(
                method="invalid",
                warning="No valid sleep input provided.",
            )
