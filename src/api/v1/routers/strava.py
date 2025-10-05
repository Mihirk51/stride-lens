from fastapi import APIRouter

from src.api.v1.schemas.strava_respose_schemas import StravaActivityResponse
from src.services.strava.strava_api_client import ActivityType, StravaAPIClient

router = APIRouter(tags=["strava_activities"])

strava_api_client = StravaAPIClient()


@router.get(
    "/recent-runs",
    response_model=StravaActivityResponse,
    summary="Get Recent Runs from Strava",
    operation_id="get_recent_runs",
)
def get_recent_runs():
    result = strava_api_client.get_activities(ActivityType.RECENT_RUNS)
    return StravaActivityResponse(success=True, message="Recent runs retrieved successfully", activities=result)


@router.get(
    "/recent-activites",
    response_model=StravaActivityResponse,
    summary="Get Recent Activities from Strava",
    operation_id="get_recent_activities",
)
def get_recent_activities():
    result = strava_api_client.get_activities(ActivityType.RECENT_ACTIVITIES)
    return StravaActivityResponse(success=True, message="Recent activities retrieved successfully", activities=result)
