__all__ = ["ManualSleepSubjectiveInput", "ManualSleepObjectiveInput", "ManualSleepInput", "ManualSleepServiceResponse"]

from typing import Any, Dict, Literal, Optional, Union

from pydantic import BaseModel, Field, model_validator


class ManualSleepSubjectiveInput(BaseModel):
    subjective_rating: int = Field(..., ge=1, le=100, description="User subjective rating (1-100)")


class ManualSleepObjectiveInput(BaseModel):
    time_in_bed_minutes: Optional[int] = Field(None, ge=0, description="Total time in bed (minutes)")
    time_awake_minutes: Optional[int] = Field(None, ge=0, description="Time awake in bed (minutes)")
    rem_sleep_minutes: Optional[int] = Field(None, ge=0, description="REM sleep duration (minutes)")
    core_sleep_minutes: Optional[int] = Field(None, ge=0, description="Core/light sleep duration (minutes)")
    deep_sleep_minutes: Optional[int] = Field(None, ge=0, description="Deep sleep duration (minutes)")
    recovery_percent: Optional[float] = Field(None, ge=0, le=100, description="Recovery percentage (0-100)")
    sleep_score_percent: Optional[float] = Field(None, ge=0, le=100, description="Overall sleep score (0-100)")

    @model_validator(mode="after")
    def validate_sleep_minutes(self):
        """Validate that sleep component minutes sum to time_in_bed_minutes."""
        time_in_bed = self.time_in_bed_minutes
        time_awake = self.time_awake_minutes or 0
        rem_sleep = self.rem_sleep_minutes or 0
        core_sleep = self.core_sleep_minutes or 0
        deep_sleep = self.deep_sleep_minutes or 0

        # Only validate if time_in_bed is provided
        if time_in_bed is not None:
            total_minutes = time_awake + rem_sleep + core_sleep + deep_sleep

            if total_minutes != time_in_bed:
                raise ValueError(
                    f"Sum of time_awake_minutes, rem_sleep_minutes, core_sleep_minutes, "
                    f"and deep_sleep_minutes ({total_minutes}) must equal "
                    f"time_in_bed_minutes ({time_in_bed})"
                )

        if not any(
            [
                self.time_in_bed_minutes,
                self.time_awake_minutes,
                self.rem_sleep_minutes,
                self.core_sleep_minutes,
                self.deep_sleep_minutes,
                self.recovery_percent,
                self.sleep_score_percent,
            ]
        ):
            raise ValueError("At least one objective sleep metric must be provided.")

        return self

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "time_in_bed_minutes": 480,
                    "time_awake_minutes": 30,
                    "rem_sleep_minutes": 120,
                    "core_sleep_minutes": 240,
                    "deep_sleep_minutes": 90,
                    "recovery_percent": 85.5,
                    "sleep_score_percent": 82.0,
                }
            ]
        }


class ManualSleepServiceResponse(BaseModel):
    """Response model for ManualSleepService.record_sleep method."""

    score: Optional[float] = Field(None, description="Calculated sleep score (0-100) or subjective rating")
    method: Literal["subjective_rating", "manual_metrics", "invalid"] = Field(
        ..., description="Method used for calculation"
    )
    warning: Optional[str] = Field(None, description="Warning message about data quality or limitations")
    details: Optional[Dict[str, Any]] = Field(
        None, description="Additional sleep metrics details (only for objective data)"
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "score": 75.0,
                    "method": "subjective_rating",
                    "warning": "Score is based only on subjective rating. Accuracy may be limited.",
                    "details": None,
                },
                {
                    "score": 82.5,
                    "method": "manual_metrics",
                    "warning": None,
                    "details": {"time_in_bed_minutes": 480, "deep_sleep_minutes": 90, "rem_sleep_minutes": 120},
                },
                {
                    "score": None,
                    "method": "invalid",
                    "warning": "No valid sleep input provided. Scores may not be accurate.",
                    "details": None,
                },
            ]
        }


ManualSleepInput = Union[ManualSleepSubjectiveInput, ManualSleepObjectiveInput]
