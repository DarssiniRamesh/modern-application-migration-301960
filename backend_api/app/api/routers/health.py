from fastapi import APIRouter

# PUBLIC_INTERFACE
router = APIRouter()

# PUBLIC_INTERFACE
@router.get(
    "/health",
    tags=["Health"],
    summary="Health Check",
    description="Return a simple health status response.",
    response_description="Successful Response",
)
def health_check():
    """Basic readiness/health endpoint for liveness probes and API docs."""
    return {"status": "ok"}
