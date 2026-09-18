import logging
from typing import Optional
from fastapi import APIRouter, Query
from schemas.responses import ModelListResponse, ModelStatusEnum
from orchestration.model_registry import model_registry

logger = logging.getLogger("satquery.api.models")
router = APIRouter(tags=["Registry"])


@router.get("/models", response_model=ModelListResponse)
async def list_models(
    task: Optional[str] = Query(default=None, description="Filter models by supported task identifier"),
    status: Optional[ModelStatusEnum] = Query(default=None, description="Filter models by operational status")
):
    """List registered remote-sensing models, tools, and future candidate pipelines."""
    logger.debug(f"GET /api/models query (task={task}, status={status})")
    return model_registry.get_registered_models(task=task, status_filter=status)
