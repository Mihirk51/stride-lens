from fastapi import APIRouter, Depends, Query

from src.api.v1.schemas.training_load_response_schema import ACWRAPIResponse, TrainingLoadAPIResponse
from src.core import constants
from src.core.clients.base_api_client import BaseAPIClient
from src.services.strava.strava_api_client import StravaAPIClient
from src.services.training_load.training_load_service import TrainingLoadService

router = APIRouter(tags=["training_load"])


class Constants(constants.Constants):
    pass


def get_training_load_service() -> TrainingLoadService:
    """Dependency that provides a TrainingLoadService instance."""
    api_client = BaseAPIClient(base_url=Constants.STRAVA_API_BASE_URL)
    strava_client = StravaAPIClient(api_client)
    return TrainingLoadService(strava_client=strava_client)


@router.get(
    "/training-load",
    response_model=TrainingLoadAPIResponse,
    summary="Get Training Load Analysis",
    operation_id="get_training_load",
    description="""
    Compare your recent 7-day running volume to your personal baseline average.
    
    This helps determine if you're training appropriately for your fitness level:
    - **0.9-1.1**: Normal range (within 10% of baseline)
    - **1.1-1.3**: Moderate increase (monitor fatigue)
    - **>1.3**: High increase (elevated injury risk)
    - **<0.9**: Below baseline (recovery/taper)
    """,
)
def get_training_load(
    weeks_baseline: int = Query(
        default=4,
        ge=1,
        le=12,
        description="Number of weeks to use for baseline calculation",
    ),
    training_load_service: TrainingLoadService = Depends(get_training_load_service),
):
    """Analyze current training load relative to athlete's baseline."""
    result = training_load_service.calculate_training_load_ratio(weeks_baseline=weeks_baseline)

    return TrainingLoadAPIResponse(
        success=True,
        message="Training load analysis retrieved successfully",
        data=result,
    )


@router.get(
    "/acwr",
    response_model=ACWRAPIResponse,
    summary="Get Acute:Chronic Workload Ratio (ACWR)",
    operation_id="get_acwr",
    description="""
    Calculate injury risk by comparing recent training (7 days) to long-term fitness (4 weeks).
    
    **Research-backed thresholds:**
    - **0.8-1.3**: Sweet spot (optimal adaptation, low injury risk)
    - **1.3-1.5**: Moderate injury risk
    - **>1.5**: High injury risk
    - **<0.8**: Detraining risk
    """,
)
def get_acwr(
    training_load_service: TrainingLoadService = Depends(get_training_load_service),
):
    """Calculate Acute:Chronic Workload Ratio for injury risk assessment."""
    result = training_load_service.calculate_acute_chronic_ratio()

    return ACWRAPIResponse(
        success=True,
        message="ACWR analysis retrieved successfully",
        data=result,
    )
