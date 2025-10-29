__all__ = [
    "TrainingLoadInterpretation",
    "TrainingLoadRatioResponse",
    "ACWRInterpretation",
    "ACWRResponse",
]

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class TrainingLoadInterpretation(str, Enum):
    """Interpretation categories for training load ratio."""

    CONSIDERABLY_UNDERTRAINING = "considerably_undertraining"
    LIGHTLY_UNDERTRAINING = "lightly_undertraining"
    NORMAL = "normal"
    MODERATELY_OVERTRAINING = "moderately_overtraining"
    HIGHLY_OVERTRAINING = "highly_overtraining"
    VERY_HIGHLY_OVERTRAINING = "very_highly_overtraining"
    INSUFFICIENT_BASELINE = "insufficient_baseline"


class ACWRInterpretation(str, Enum):
    """Interpretation categories for Acute:Chronic Workload Ratio."""

    DETRAINING_RISK = "detraining_risk"
    OPTIMAL = "optimal"
    MODERATE_RISK = "moderate_risk"
    HIGH_INJURY_RISK = "high_injury_risk"
    INSUFFICIENT_BASELINE = "insufficient_baseline"


class TrainingLoadRatioResponse(BaseModel):
    """Response for training load ratio analysis comparing recent 7-day load to baseline."""

    current_week_km: float = Field(..., ge=0, description="Total distance in the past 7 days (km)")
    baseline_weekly_km: float = Field(..., ge=0, description="Average weekly distance over baseline period (km)")
    load_ratio: Optional[float] = Field(None, ge=0, description="Ratio of current to baseline load")
    interpretation: TrainingLoadInterpretation = Field(..., description="Load interpretation category")
    weeks_analyzed: int = Field(..., gt=0, description="Number of weeks used for baseline calculation")

    class Config:
        json_schema_extra = {
            "example": {
                "current_week_km": 48.5,
                "baseline_weekly_km": 42.0,
                "load_ratio": 1.15,
                "interpretation": "moderately_overtraining",
                "weeks_analyzed": 4,
            }
        }


class ACWRResponse(BaseModel):
    """
    Acute:Chronic Workload Ratio (ACWR) response.

    Compares recent 7-day load to 4-week average to assess injury risk.
    Optimal range: 0.8-1.3
    """

    acute_load_km: float = Field(..., ge=0, description="Total distance in last 7 days (km)")
    chronic_load_km: float = Field(..., ge=0, description="Average weekly distance over last 4 weeks (km)")
    acwr: Optional[float] = Field(None, ge=0, description="Acute:Chronic Workload Ratio")
    interpretation: ACWRInterpretation = Field(..., description="ACWR interpretation category")

    class Config:
        json_schema_extra = {
            "example": {
                "acute_load_km": 45.0,
                "chronic_load_km": 40.0,
                "acwr": 1.13,
                "interpretation": "optimal",
            }
        }
