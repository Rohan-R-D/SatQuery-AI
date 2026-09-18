import logging
from typing import List, Optional, Dict, Any
from sqlalchemy import select, func

from schemas.execution import ExecutionRecord
from orchestration.execution_manager import execution_manager
from database.session import get_db_session
from database.models import ExecutionModel

logger = logging.getLogger("satquery.services.audit")


class AuditService:
    def record_execution(self, record: ExecutionRecord) -> None:
        """Audit recording is handled automatically via persistent ExecutionManager."""
        logger.debug(f"Audit record noted: {record.execution_id} ({record.task} - {record.status})")

    def get_execution(self, execution_id: str) -> Optional[ExecutionRecord]:
        """Fetch a specific execution by ID from database."""
        return execution_manager.get_execution(execution_id)

    def list_executions(
        self,
        limit: int = 50,
        task: Optional[str] = None
    ) -> List[ExecutionRecord]:
        """List execution records sorted newest first from database."""
        return execution_manager.list_executions(limit=limit, task=task)

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Compute aggregated audit metrics directly from persistent SQLite storage."""
        with get_db_session() as session:
            total_count = session.scalar(select(func.count(ExecutionModel.id))) or 0
            if total_count == 0:
                return {
                    "total_queries": 0,
                    "avg_duration_sec": 0.0,
                    "success_rate_pct": 100.0,
                    "task_distribution": {}
                }

            completed_count = session.scalar(
                select(func.count(ExecutionModel.id)).where(ExecutionModel.status == "COMPLETED")
            ) or 0

            total_duration = session.scalar(select(func.sum(ExecutionModel.duration_sec))) or 0.0

            task_rows = session.execute(
                select(ExecutionModel.task, func.count(ExecutionModel.id)).group_by(ExecutionModel.task)
            ).all()
            task_distribution = {task: count for task, count in task_rows}

            return {
                "total_queries": total_count,
                "avg_duration_sec": round(total_duration / total_count, 3),
                "success_rate_pct": round((completed_count / total_count) * 100, 1),
                "task_distribution": task_distribution
            }


audit_service = AuditService()
