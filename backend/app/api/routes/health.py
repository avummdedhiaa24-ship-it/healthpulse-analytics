from fastapi import APIRouter

# Create router
router = APIRouter()

# Health check endpoint


@router.get("/health")
def health_check():
    return {"status": "ok"}
