__all__ = [
    "ManualSleepSubjectiveInput",
    "ManualSleepObjectiveInput",
    "ManualSleepInput",
]

from typing import Optional, Union

from pydantic import BaseModel, Field


class ManualSleepSubjectiveInput(BaseModel):
    subjective_rating: int = Field(..., ge=1, le=100, description="User subjective rating (1–100)")


class ManualSleepObjectiveInput(BaseModel):
    time_in_bed_minutes: Optional[int] = Field(None, ge=0, description="Total time in bed (minutes)")
    time_awake_minutes: Optional[int] = Field(None, ge=0, description="Time awake in bed (minutes)")
    rem_sleep_minutes: Optional[int] = Field(None, ge=0, description="REM sleep duration (minutes)")
    core_sleep_minutes: Optional[int] = Field(None, ge=0, description="Core/light sleep duration (minutes)")
    deep_sleep_minutes: Optional[int] = Field(None, ge=0, description="Deep sleep duration (minutes)")
    recovery_percent: Optional[float] = Field(None, ge=0, le=100, description="Recovery percentage (0–100)")
    sleep_score_percent: Optional[float] = Field(None, ge=0, le=100, description="Overall sleep score (0–100)")

    class Config:
        @staticmethod
        def validate_model(values):
            if not any(values.values()):
                raise ValueError("At least one objective sleep metric must be provided.")
            return values


ManualSleepInput = Union[ManualSleepSubjectiveInput, ManualSleepObjectiveInput]
