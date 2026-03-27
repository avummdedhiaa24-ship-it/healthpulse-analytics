import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models.model_run import ModelRun
from app.api.schemas.model_run import ModelRunCreate, ModelRunResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/model-runs", tags=["ML Monitoring — Model Runs"])


@router.post("/", response_model=ModelRunResponse, status_code=201)
def log_model_run(payload: ModelRunCreate, db: Session = Depends(get_db)):
    """
    Log a new ML model evaluation run.
    Records model name, accuracy, and F1 score with a timestamp.
    """
    run = ModelRun(
        model_name=payload.model_name,
        accuracy=payload.accuracy,
        f1_score=payload.f1_score,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    logger.info("Logged model run: model=%s accuracy=%.4f f1=%.4f",
                run.model_name, run.accuracy, run.f1_score)
    return run


@router.get("/", response_model=List[ModelRunResponse])
def get_all_model_runs(db: Session = Depends(get_db)):
    """
    Retrieve all logged model runs, ordered by most recent first.
    """
    runs = db.query(ModelRun).order_by(ModelRun.created_at.desc()).all()
    return runs


@router.get("/{model_name}", response_model=List[ModelRunResponse])
def get_runs_by_model(model_name: str, db: Session = Depends(get_db)):
    """
    Retrieve all runs for a specific model name.
    Useful for tracking performance over time for a single model.
    """
    runs = (
        db.query(ModelRun)
        .filter(ModelRun.model_name == model_name)
        .order_by(ModelRun.created_at.desc())
        .all()
    )
    if not runs:
        raise HTTPException(
            status_code=404, detail=f"No runs found for model '{model_name}'.")
    return runs


@router.get("/{model_name}/latest", response_model=ModelRunResponse)
def get_latest_run(model_name: str, db: Session = Depends(get_db)):
    """
    Retrieve the most recent run for a specific model.
    """
    run = (
        db.query(ModelRun)
        .filter(ModelRun.model_name == model_name)
        .order_by(ModelRun.created_at.desc())
        .first()
    )
    if not run:
        raise HTTPException(
            status_code=404, detail=f"No runs found for model '{model_name}'.")
    return run


@router.delete("/{run_id}", status_code=200)
def delete_model_run(run_id: int, db: Session = Depends(get_db)):
    """
    Delete a specific model run by ID.
    """
    run = db.query(ModelRun).filter(ModelRun.id == run_id).first()
    if not run:
        raise HTTPException(
            status_code=404, detail=f"Model run with id={run_id} not found.")
    db.delete(run)
    db.commit()
    logger.info("Deleted model run id=%d", run_id)
    return {"message": f"Model run id={run_id} deleted successfully."}
