from fastapi import FastAPI

from src.api.v1.routers import sleep_and_recovery, strava

app = FastAPI(
    title="Stride Lens API", version="0.1.0", description="AI-powered tool that predicts how your run will feel"
)

app.include_router(sleep_and_recovery.router, prefix="/v1")
app.include_router(strava.router, prefix="/v1")