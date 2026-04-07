from nlp_utils import extract_entities, compute_similarity
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.db.session import engine
from app.db.base import Base
from app.db.models import patient, model_run, drift_log  # noqa: F401
from app.api.routes import health
from app.api.routes import patients
from app.api.routes import model_run as model_run_router
from app.api.routes import drift_log as drift_log_router

app = FastAPI(
    title="HealthPulse API",
    description="Clinical data pipeline · ML monitoring · Real-world evidence analytics",
    version="0.1.0",
)

Base.metadata.create_all(bind=engine)

app.include_router(health.router)
app.include_router(patients.router)
app.include_router(model_run_router.router)
app.include_router(drift_log_router.router)


@app.get("/", tags=["Root"])
def root():
    return {"message": "HealthPulse API is running 🚀"}

# ── NLP Endpoints ──────────────────────────────────────────────────────────


@app.post("/nlp/entities", tags=["NLP"])
async def get_entities(request: Request):
    data = await request.json()
    text = data.get("text", "")
    entities = extract_entities(text)
    return JSONResponse({"entities": entities})


@app.post("/nlp/similarity", tags=["NLP"])
async def get_similarity(request: Request):
    data = await request.json()
    score = compute_similarity(data["text1"], data["text2"])
    return JSONResponse({"similarity_score": score})
