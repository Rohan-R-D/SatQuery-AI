import logging
from fastapi import APIRouter
from config import settings
from schemas.responses import HealthResponse

logger = logging.getLogger("satquery.api.health")
router = APIRouter(tags=["System"])


@router.get("/health", response_model=HealthResponse)
async def get_health():
    """Health check endpoint to verify backend operational status."""
    logger.debug("Health check ping received.")
    return HealthResponse(
        status="healthy",
        service=settings.SERVICE_NAME,
        version=settings.VERSION
    )
