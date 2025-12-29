from fastapi import APIRouter

router = APIRouter()


@router.get("/health", summary="Health Check", description="Return a simple health status response.")
def health_check():
    """Health check endpoint to verify API is running."""
    return {"status": "ok"}
