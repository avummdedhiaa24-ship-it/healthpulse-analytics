from fastapi import FastAPI

from app.db.session import engine
from app.db.base import Base

# ── Import models so SQLAlchemy registers them before create_all ──────────
from app.db.models import patient, model_run, drift_log  # noqa: F401

# ── Import routers ────────────────────────────────────────────────────────
from app.api.routes import health
from app.api.routes import patients
from app.api.routes import model_run as model_run_router
from app.api.routes import drift_log as drift_log_router

# ── App factory ───────────────────────────────────────────────────────────
app = FastAPI(
    title="HealthPulse API",
    description="Clinical data pipeline · ML monitoring · Real-world evidence analytics",
    version="0.1.0",
)

# ── Create all DB tables ──────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ── Register routers ──────────────────────────────────────────────────────
app.include_router(health.router)
app.include_router(patients.router)
app.include_router(model_run_router.router)
app.include_router(drift_log_router.router)


# ── Root ──────────────────────────────────────────────────────────────────
@app.get("/", tags=["Root"])
def root():
    return {"message": "HealthPulse API is running 🚀"}
