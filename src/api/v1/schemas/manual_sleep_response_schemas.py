__all__ = [
    "ManualSleepResponse",
]

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ManualSleepResponse(BaseModel):
    success: bool = Field(True, description="Whether the operation was successful")
    message: str = Field(..., description="Status message")
    score: Optional[float] = Field(None, description="Calculated sleep score (0-100)")
    method: str = Field(..., description="Method used for calculation")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional sleep metrics details")
    warning: Optional[str] = Field(None, description="Warning message if data is incomplete")
    sleep_id: Optional[str] = Field(None, description="Unique identifier for the sleep record")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Sleep data recorded successfully",
                "score": 85.5,
                "method": "manual_metrics",
                "details": {"time_in_bed_minutes": 480, "deep_sleep_minutes": 90},
                "warning": None,
                "sleep_id": "sleep_123",
            }
        }
