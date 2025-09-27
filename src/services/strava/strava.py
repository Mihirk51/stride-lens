__all__ = [
    "StravaAPIClient",
]

from src.interfaces.strava import StravaService
from src.services.strava.utils import refresh_strava_token


class StravaAPIClient(StravaService):
    def __init__(self):
        refresh_strava_token()
