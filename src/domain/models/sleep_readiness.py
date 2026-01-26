"""Domain model for sleep readiness."""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class SleepReadiness(BaseModel):
    """Unified sleep data for scoring."""

    date: datetime
    score: float = Field(..., ge=0, le=100, description="Overall sleep/recovery score")

    # Optional detailed metrics
    time_in_bed_minutes: Optional[int] = None
    total_sleep_minutes: Optional[int] = None
    deep_sleep_minutes: Optional[int] = None
    rem_sleep_minutes: Optional[int] = None
    core_sleep_minutes: Optional[int] = None
    time_awake_minutes: Optional[int] = None
    recovery_percent: Optional[float] = None
    sleep_score_percent: Optional[float] = None

    data_source: Literal["manual", "oura", "whoop", "apple_watch"] = "manual"
