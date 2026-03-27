import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models.drift_log import DriftLog
from app.api.schemas.drift_log import DriftLogCreate, DriftLogResponse
from app.services.drift_service import run_drift_detection

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/drift-logs", tags=["ML Monitoring — Drift Logs"])

# PSI threshold: industry standard — >0.2 = significant drift
PSI_THRESHOLD = 0.2
# KS threshold: >0.1 = statistically significant distribution shift
KS_THRESHOLD = 0.1


@router.post("/", response_model=DriftLogResponse, status_code=201)
def log_drift(payload: DriftLogCreate, db: Session = Depends(get_db)):
    """
    Log a drift detection result for a specific feature.
    Stores PSI score, KS statistic, and whether drift was detected.
    """
    entry = DriftLog(
        feature_name=payload.feature_name,
        psi_score=payload.psi_score,
        ks_statistic=payload.ks_statistic,
        drift_detected=payload.drift_detected,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    logger.info(
        "Drift log: feature=%s psi=%.4f ks=%.4f drift=%s",
        entry.feature_name, entry.psi_score, entry.ks_statistic, entry.drift_detected,
    )
    return entry


@router.get("/", response_model=List[DriftLogResponse])
def get_all_drift_logs(db: Session = Depends(get_db)):
    """
    Retrieve all drift log entries.
    """
    return db.query(DriftLog).order_by(DriftLog.id.desc()).all()


@router.get("/alerts", response_model=List[DriftLogResponse])
def get_drift_alerts(db: Session = Depends(get_db)):
    """
    Retrieve only features where drift was detected.
    Use this endpoint for dashboards and alerting pipelines.
    """
    alerts = db.query(DriftLog).filter(DriftLog.drift_detected == True).all()
    if not alerts:
        return []
    return alerts


@router.get("/feature/{feature_name}", response_model=List[DriftLogResponse])
def get_drift_by_feature(feature_name: str, db: Session = Depends(get_db)):
    """
    Retrieve all drift logs for a specific feature (e.g. 'bmi', 'age').
    """
    logs = db.query(DriftLog).filter(
        DriftLog.feature_name == feature_name).all()
    if not logs:
        raise HTTPException(
            status_code=404, detail=f"No drift logs found for feature '{feature_name}'.")
    return logs


@router.get("/summary", response_model=dict)
def get_drift_summary(db: Session = Depends(get_db)):
    """
    Return a high-level drift summary across all features.
    Shows total features tracked, how many have drifted, and which ones.
    """
    all_logs = db.query(DriftLog).all()
    if not all_logs:
        return {"total_features": 0, "drifted": 0, "stable": 0, "drifted_features": []}

    drifted = [log for log in all_logs if log.drift_detected]
    stable = [log for log in all_logs if not log.drift_detected]

    return {
        "total_features": len(all_logs),
        "drifted": len(drifted),
        "stable": len(stable),
        "drifted_features": [log.feature_name for log in drifted],
        "thresholds": {"psi": PSI_THRESHOLD, "ks": KS_THRESHOLD},
    }


@router.delete("/{log_id}", status_code=200)
def delete_drift_log(log_id: int, db: Session = Depends(get_db)):
    """
    Delete a specific drift log entry by ID.
    """
    log = db.query(DriftLog).filter(DriftLog.id == log_id).first()
    if not log:
        raise HTTPException(
            status_code=404, detail=f"Drift log with id={log_id} not found.")
    db.delete(log)
    db.commit()
    logger.info("Deleted drift log id=%d", log_id)
    return {"message": f"Drift log id={log_id} deleted successfully."}


@router.post("/run-detection")
def trigger_drift_detection(db: Session = Depends(get_db)):
    try:
        result = run_drift_detection(db=db)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return result
