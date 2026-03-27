from pydantic import BaseModel, Field


class DriftLogCreate(BaseModel):
    feature_name: str = Field(..., example="bmi")
    psi_score: float = Field(..., ge=0.0, example=0.23)
    ks_statistic: float = Field(..., ge=0.0, le=1.0, example=0.18)
    drift_detected: bool = Field(..., example=True)


class DriftLogResponse(BaseModel):
    id: int
    feature_name: str
    psi_score: float
    ks_statistic: float
    drift_detected: bool

    class Config:
        from_attributes = True
