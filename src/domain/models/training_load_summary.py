"""Domain model for training load."""

from datetime import datetime

from pydantic import BaseModel, Field


class TrainingLoadSummary(BaseModel):
    """Training load and fatigue state."""

    calculated_at: datetime

    # Distance metrics (km)
    last_7_days_km: float = Field(..., ge=0)
    last_28_days_km: float = Field(..., ge=0)
    baseline_weekly_km: float = Field(..., ge=0)

    # Key ratios
    acwr: float = Field(..., ge=0, description="Acute:Chronic Workload Ratio")
    load_ratio: float = Field(..., ge=0, description="Current week / baseline ratio")

    # Context
    days_since_last_run: int = Field(..., ge=0)
    consecutive_training_days: int = Field(default=0, ge=0)
