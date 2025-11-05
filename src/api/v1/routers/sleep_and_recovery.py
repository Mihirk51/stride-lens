import uuid
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import ValidationError

from src.api.dependencies import get_sleep_service
from src.api.v1.schemas.manual_sleep_response_schemas import ManualSleepResponse
from src.schemas.manual_sleep_and_recovery_schema import ManualSleepObjectiveInput, ManualSleepSubjectiveInput
from src.services.sleep_and_recovery.manual_sleep_service import ManualSleepService

router = APIRouter(tags=["sleep_and_recovery"])


@router.post(
    "/manual/subjective",
    response_model=ManualSleepResponse,
    summary="Record Subjective Sleep",
    operation_id="record_subjective_sleep",
)
def record_subjective_sleep(
    subjective_rating: int, sleep_service: ManualSleepService = Depends(get_sleep_service)
) -> ManualSleepResponse:
    data = ManualSleepSubjectiveInput(subjective_rating=subjective_rating)

    result = sleep_service.record_sleep(data)

    return ManualSleepResponse(
        success=True,
        message="Subjective sleep data recorded successfully",
        score=result.score,
        method=result.method,
        warning=result.warning,
        sleep_id=f"sleep_{uuid.uuid4().hex[:8]}",
    )


@router.post(
    "/manual/objective",
    response_model=ManualSleepResponse,
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
    sleep_service: ManualSleepService = Depends(get_sleep_service),
) -> ManualSleepResponse:
    try:
        data = ManualSleepObjectiveInput(
            time_in_bed_minutes=time_in_bed_minutes,
            time_awake_minutes=time_awake_minutes,
            rem_sleep_minutes=rem_sleep_minutes,
            core_sleep_minutes=core_sleep_minutes,
            deep_sleep_minutes=deep_sleep_minutes,
            recovery_percent=recovery_percent,
            sleep_score_percent=sleep_score_percent,
        )
    except ValidationError:
        raise

    result = sleep_service.record_sleep(data)

    return ManualSleepResponse(
        success=True,
        message="Objective sleep data recorded successfully",
        score=result.score,
        method=result.method,
        details=result.details,
        warning=result.warning,
        sleep_id=f"sleep_{uuid.uuid4().hex[:8]}",
    )
