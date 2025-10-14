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
    def __init__(self):
        self.fields_provided = 0

    def record_sleep(self, data: ManualSleepInput) -> ManualSleepServiceResponse:
        if isinstance(data, ManualSleepSubjectiveInput):
            return ManualSleepServiceResponse(
                score=data.subjective_rating,
                method="subjective_rating",
                warning="Score is based only on subjective rating. Accuracy may be limited.",
            )

        elif isinstance(data, ManualSleepObjectiveInput):
            metrics = data.dict(exclude_none=True)
            score = self._calculate_score(metrics)

            return ManualSleepServiceResponse(
                score=score,
                method="manual_metrics",
                details=metrics,
                warning=self._add_warning_if_incomplete(metrics),
            )

        else:
            return ManualSleepServiceResponse(
                score=None,
                method="invalid",
                warning="No valid sleep input provided. Scores may not be accurate.",
            )
