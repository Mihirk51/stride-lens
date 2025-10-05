__all__ = [
    "refresh_strava_token",
]

import os

from dotenv import load_dotenv

from src.core import constants, logger
from src.core.clients.base_api_client import BaseAPIClient

log = logger


class Constants(constants.Constants):
    pass


ENV_FILE = Constants.ENV_FILE
api_client = BaseAPIClient(base_url=Constants.STRAVA_BASE_URL)


def refresh_strava_token():
    """Refresh the Strava access token using the refresh token and update the .env file."""
    load_dotenv(ENV_FILE, override=True)

    client_id = os.getenv("STRAVA_CLIENT_ID")
    client_secret = os.getenv("STRAVA_CLIENT_SECRET")
    refresh_token = os.getenv("STRAVA_REFRESH_TOKEN")

    if not all([client_id, client_secret, refresh_token]):
        raise ValueError("Missing STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, or STRAVA_REFRESH_TOKEN in .env")

    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }

    response = api_client.post(endpoint=Constants.STRAVA_TOKEN_ENDPOINT, data=data)

    if not response.is_success:
        raise RuntimeError(f"Failed to refresh token: {response.status_code}, {response.text}")

    tokens = response.get_json()
    access_token = tokens["access_token"]
    new_refresh_token = tokens["refresh_token"]
    expiry_time = tokens["expires_at"]

    log.info("Successfully refreshed Strava token!")
    log.info(f"New access_token: {access_token[:10]}... (truncated)")
    log.info(f"New refresh_token: {new_refresh_token[:10]}... (truncated)")

    # Update the .env file
    update_env_file("STRAVA_ACCESS_TOKEN", access_token)
    update_env_file("STRAVA_REFRESH_TOKEN", new_refresh_token)
    update_env_file("STRAVA_ACCESS_TOKEN_EXPIRY", expiry_time)


def update_env_file(key, value):
    """Update or insert a key=value in the .env file"""
    lines = []
    found = False

    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r") as f:
            lines = f.readlines()

    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = f"{key}={value}\n"
            found = True
            break

    if not found:
        lines.append(f"{key}={value}\n")

    with open(ENV_FILE, "w") as f:
        f.writelines(lines)
    log.info(f"Updated {key} in {ENV_FILE}")

if __name__ == "__main__":
    refresh_strava_token()
