from pydantic import BaseModel, Field
from datetime import datetime


class ModelRunCreate(BaseModel):
    model_name: str = Field(..., example="readmission_classifier_v2")
    accuracy: float = Field(..., ge=0.0, le=1.0, example=0.91)
    f1_score: float = Field(..., ge=0.0, le=1.0, example=0.88)


class ModelRunResponse(BaseModel):
    id: int
    model_name: str
    accuracy: float
    f1_score: float
    created_at: datetime

    class Config:
        from_attributes = True
