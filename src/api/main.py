from fastapi import FastAPI

from src.api.v1.endpoints import sleep_and_recovery

app = FastAPI(
    title="Run Feeling API", version="0.1.0", description="AI-powered tool that predicts how your run will feel"
)

# Include with proper v1 prefix
app.include_router(sleep_and_recovery.router, prefix="/v1")
