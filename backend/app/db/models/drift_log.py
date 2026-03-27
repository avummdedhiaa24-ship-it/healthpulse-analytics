from sqlalchemy import Column, Integer, String, Float, Boolean
from app.db.base import Base


class DriftLog(Base):
    __tablename__ = "drift_logs"

    id = Column(Integer, primary_key=True, index=True)
    feature_name = Column(String)
    psi_score = Column(Float)
    ks_statistic = Column(Float)
    drift_detected = Column(Boolean)
