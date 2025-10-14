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
    return StravaActivityResponse(
        success=True,
        message="Recent runs retrieved successfully",
        athlete_profile=result.athlete_profile,
        activities=result.activities,
    )


@router.get(
    "/recent-activites",
    response_model=StravaActivityResponse,
    summary="Get Recent Activities from Strava",
    operation_id="get_recent_activities",
)
def get_recent_activities():
    result = strava_api_client.get_activities(ActivityType.RECENT_ACTIVITIES)
    return StravaActivityResponse(
        success=True,
        message="Recent activities retrieved successfully",
        athlete_profile=result.athlete_profile,
        activities=result.activities,
    )


@router.get(
    "/athlete-profile",
    response_model=StravaActivityResponse,
    summary="Get Athlete profile from Strava",
    operation_id="get_athlete_profile",
)
def get_athlete_profile():
    result = strava_api_client.get_activities(ActivityType.ATHLETE_PROFILE)
    return StravaActivityResponse(
        success=True,
        message="Athlete Profile retrieved successfully",
        athlete_profile=result.athlete_profile,
        activities=[],
    )
