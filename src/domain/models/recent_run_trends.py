"""Domain model for recent run trends."""

from datetime import datetime

from pydantic import BaseModel, Field


class SingleRun(BaseModel):
    """Individual run data."""

    id: int
    name: str
    distance_km: float
    moving_time_minutes: int
    elevation_gain_m: float
    date: datetime
    avg_pace_min_per_km: float | None = None
    avg_heartrate: int | None = None
    max_heartrate: int | None = None


class RecentRunTrends(BaseModel):
    """Recent running patterns from last 10 activities."""

    calculated_at: datetime

    recent_runs: list[SingleRun] = Field(default_factory=list)

    runs_last_7_days: int = Field(..., ge=0)
    runs_last_30_days: int = Field(..., ge=0)

    total_distance_last_30_days_km: float = Field(..., ge=0)
    total_distance_last_7_days_km: float = Field(..., ge=0)

    days_since_last_run: int | None = None
