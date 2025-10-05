import uuid
from typing import Optional

from fastapi import APIRouter

from src.api.v1.schemas.manual_sleep_response_schemas import RecordManualSleepResponse
from src.schemas.manual_sleep_and_recovery import ManualSleepObjectiveInput, ManualSleepSubjectiveInput
from src.services.sleep_and_recovery.manual_sleep_service import ManualSleepService

router = APIRouter(tags=["sleep_and_recovery"])

sleep_service = ManualSleepService()


@router.post(
    "/manual/subjective",
    response_model=RecordManualSleepResponse,
    summary="Record Subjective Sleep",
    operation_id="record_subjective_sleep",
)
def record_subjective_sleep(subjective_rating: int) -> RecordManualSleepResponse:
    data = ManualSleepSubjectiveInput(subjective_rating=subjective_rating)

    result = sleep_service.record_sleep(data)

    return RecordManualSleepResponse(
        success=True,
        message="Subjective sleep data recorded successfully",
        score=result["score"],
        method=result["method"],
        warning=result.get("warning"),
        sleep_id=f"sleep_{uuid.uuid4().hex[:8]}",
    )


@router.post(
    "/manual/objective",
    response_model=RecordManualSleepResponse,
    summary="Record Objective Sleep",
    operation_id="record_objective_sleep",
)
def record_objective_sleep(
    time_in_bed_minutes: Optional[int] = None,
    time_awake_minutes: Optional[int] = None,
    rem_sleep_minutes: Optional[int] = None,
    core_sleep_minutes: Optional[int] = None,
    deep_sleep_minutes: Optional[int] = None,
    recovery_percent: Optional[float] = None,
    sleep_score_percent: Optional[float] = None,
) -> RecordManualSleepResponse:
    data = ManualSleepObjectiveInput(
        time_in_bed_minutes=time_in_bed_minutes,
        time_awake_minutes=time_awake_minutes,
        rem_sleep_minutes=rem_sleep_minutes,
        core_sleep_minutes=core_sleep_minutes,
        deep_sleep_minutes=deep_sleep_minutes,
        recovery_percent=recovery_percent,
        sleep_score_percent=sleep_score_percent,
    )

    result = sleep_service.record_sleep(data)

    return RecordManualSleepResponse(
        success=True,
        message="Objective sleep data recorded successfully",
        score=result["score"],
        method=result["method"],
        details=result.get("details"),
        warning=result.get("warning"),
        sleep_id=f"sleep_{uuid.uuid4().hex[:8]}",
    )
