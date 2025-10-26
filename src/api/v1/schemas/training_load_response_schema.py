__all__ = [
    "TrainingLoadAPIResponse",
    "ACWRAPIResponse",
]

from pydantic import BaseModel, Field

from src.schemas.training_load_response_schema import ACWRResponse, TrainingLoadRatioResponse


class TrainingLoadAPIResponse(BaseModel):
    success: bool = Field(True, description="Whether the operation was successful")
    message: str = Field(..., description="Status message")
    data: TrainingLoadRatioResponse = Field(..., description="Training load analysis data")


class ACWRAPIResponse(BaseModel):
    success: bool = Field(True, description="Whether the operation was successful")
    message: str = Field(..., description="Status message")
    data: ACWRResponse = Field(..., description="ACWR analysis data")
