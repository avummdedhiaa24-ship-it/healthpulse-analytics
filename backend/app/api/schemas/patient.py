from pydantic import BaseModel


class PatientCreate(BaseModel):
    patient_id: str
    age: int
    gender: str
    bmi: float
    condition: str
