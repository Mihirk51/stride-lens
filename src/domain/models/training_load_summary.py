"""Domain model for training load."""

__all__ = [
    "TrainingLoadSummary",
    "TrainingLoadScore",
]

from datetime import datetime

from pydantic import BaseModel, Field


class TrainingLoadSummary(BaseModel):
    """Training load and fatigue state."""

    calculated_at: datetime

    # Distance metrics (km)
    acute_load_km: float = Field(..., ge=0)
    chronic_load_km: float = Field(..., ge=0)

    # Key ratios
    acwr: float = Field(..., ge=0, description="Acute:Chronic Workload Ratio")
    load_ratio: float = Field(..., ge=0, description="Current week / baseline ratio")

    # Context
    days_since_last_run: int = Field(..., ge=0)
    consecutive_training_days: int = Field(default=0, ge=0)


class TrainingLoadScore(BaseModel):
    """Result of training load scoring."""

    score: float = Field(..., ge=0, le=100, description="Training load score (0-100)")
    fatigue_level: str = Field(..., description="Human-readable fatigue level")
    interpretation: str = Field(..., description="Detailed interpretation of current state")
    warnings: list[str] = Field(default_factory=list, description="Actionable warnings")

    summary: TrainingLoadSummary = Field(..., description="Underlying training load data")
