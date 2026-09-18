import logging
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, status, Query, Depends
from schemas.execution import ExecutionRecord
from orchestration.execution_manager import execution_manager
from services.audit_service import audit_service
from api.deps import verify_admin_key

logger = logging.getLogger("satquery.api.audit")
router = APIRouter(tags=["Audit & Execution"], dependencies=[Depends(verify_admin_key)])


@router.get("/executions/{execution_id}", response_model=ExecutionRecord)
async def get_execution_trace(execution_id: str):
    """Retrieve full execution lifecycle trace and result for a specific execution ID."""
    logger.debug(f"GET /api/executions/{execution_id}")
    record = execution_manager.get_execution(execution_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution record '{execution_id}' not found."
        )
    return record


@router.get("/audit")
async def get_audit_overview(
    limit: int = Query(default=50, ge=1, le=200, description="Max records to return"),
    task: Optional[str] = Query(default=None, description="Filter by task")
) -> Dict[str, Any]:
    """Retrieve system execution history and aggregated performance metrics."""
    logger.debug(f"GET /api/audit (limit={limit}, task={task})")
    records = audit_service.list_executions(limit=limit, task=task)
    metrics = audit_service.get_metrics_summary()

    return {
        "metrics": metrics,
        "total_returned": len(records),
        "records": records
    }
