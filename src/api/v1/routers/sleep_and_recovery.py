import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import ValidationError

from src.api.v1.schemas.manual_sleep_response_schemas import ManualSleepResponse
from src.core.dependencies import get_sleep_service
from src.domain.models.sleep_readiness import SleepReadiness
from src.domain.scoring.components.sleep_readiness import SleepReadinessComponent
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

    # Create domain model and calculate score
    sleep_data = SleepReadiness(
        date=datetime.now(timezone.utc),
        score=subjective_rating,
        data_source="manual",
    )

    component = SleepReadinessComponent()
    scored_result = component.calculate(sleep_data)

    # Convert 0-1 scale to 0-100 for API response
    score_0_100 = round(scored_result.score * 100, 1)

    return ManualSleepResponse(
        success=True,
        message="Subjective sleep data recorded successfully",
        score=score_0_100,
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

    # Extract score from metrics (use sleep_score_percent if available, otherwise calculate from metrics)
    base_score = result.details.get("sleep_score_percent") or 50.0

    # Create domain model and calculate score
    sleep_data = SleepReadiness(
        date=datetime.now(timezone.utc),
        score=base_score,
        data_source="manual",
        time_in_bed_minutes=result.details.get("time_in_bed_minutes"),
        time_awake_minutes=result.details.get("time_awake_minutes"),
        rem_sleep_minutes=result.details.get("rem_sleep_minutes"),
        core_sleep_minutes=result.details.get("core_sleep_minutes"),
        deep_sleep_minutes=result.details.get("deep_sleep_minutes"),
        recovery_percent=result.details.get("recovery_percent"),
        sleep_score_percent=result.details.get("sleep_score_percent"),
    )

    component = SleepReadinessComponent()
    scored_result = component.calculate(sleep_data)

    # Convert 0-1 scale to 0-100 for API response
    score_0_100 = round(scored_result.score * 100, 1)

    return ManualSleepResponse(
        success=True,
        message="Objective sleep data recorded successfully",
        score=score_0_100,
        method=result.method,
        details=result.details,
        warning=result.warning,
        sleep_id=f"sleep_{uuid.uuid4().hex[:8]}",
    )
