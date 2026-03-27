from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models.patient import Patient
from app.api.schemas.patient import PatientCreate
from app.services.csv_service import process_patient_csv

router = APIRouter(prefix="/patients", tags=["Patients"])


# CREATE PATIENT
@router.post("/")
def create_patient(
    patient: PatientCreate,
    db: Session = Depends(get_db)
):
    new_patient = Patient(
        patient_id=patient.patient_id,
        age=patient.age,
        gender=patient.gender,
        bmi=patient.bmi,
        condition=patient.condition
    )

    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)

    return {
        "message": "Patient created successfully",
        "id": new_patient.id
    }


# GET PATIENTS
@router.get("/")
def get_patients(db: Session = Depends(get_db)):
    return db.query(Patient).all()


# 🔥 NEW: CSV UPLOAD
@router.post("/upload-csv")
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    return await process_patient_csv(file, db)
