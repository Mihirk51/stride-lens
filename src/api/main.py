from fastapi import FastAPI
from pydantic import ValidationError

from src.api.v1.exception_handler import validation_exception_handler
from src.api.v1.routers import sleep_and_recovery, strava, training_load, weather

app = FastAPI(
    title="Stride Lens API", version="0.1.0", description="AI-powered tool that predicts how your run will feel"
)

app.include_router(sleep_and_recovery.router, prefix="/v1")
app.include_router(strava.router, prefix="/v1")
app.include_router(weather.router, prefix="/v1")
app.include_router(training_load.router, prefix="/v1")
app.add_exception_handler(ValidationError, validation_exception_handler)
