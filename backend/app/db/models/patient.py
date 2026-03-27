from sqlalchemy import Column, Integer, String, Float
from app.db.base import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, unique=True, index=True)
    age = Column(Integer)
    gender = Column(String)
    bmi = Column(Float)
    condition = Column(String)
