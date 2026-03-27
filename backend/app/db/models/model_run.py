from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.db.base import Base


class ModelRun(Base):
    __tablename__ = "model_runs"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String)
    accuracy = Column(Float)
    f1_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
