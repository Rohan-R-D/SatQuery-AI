import threading
import logging
from typing import List, Optional, Dict, Any
from schemas.execution import ExecutionRecord

logger = logging.getLogger("satquery.services.audit")


class AuditService:
    def __init__(self, max_records: int = 500):
        self._records: Dict[str, ExecutionRecord] = {}
        self._order: List[str] = []
        self._max_records = max_records
        self._lock = threading.Lock()

    def record_execution(self, record: ExecutionRecord) -> None:
        """Store or update an execution record thread-safely."""
        with self._lock:
            if record.execution_id not in self._records:
                self._order.append(record.execution_id)
            self._records[record.execution_id] = record

            # Evict oldest if exceeding max capacity
            while len(self._order) > self._max_records:
                oldest_id = self._order.pop(0)
                self._records.pop(oldest_id, None)

        logger.debug(f"Audit record updated: {record.execution_id} ({record.task} - {record.status})")

    def get_execution(self, execution_id: str) -> Optional[ExecutionRecord]:
        """Fetch a specific execution by ID."""
        with self._lock:
            return self._records.get(execution_id)

    def list_executions(
        self,
        limit: int = 50,
        task: Optional[str] = None
    ) -> List[ExecutionRecord]:
        """List execution records sorted newest first."""
        with self._lock:
            results = []
            for exec_id in reversed(self._order):
                rec = self._records.get(exec_id)
                if rec:
                    if task and rec.task != task:
                        continue
                    results.append(rec)
                if len(results) >= limit:
                    break
            return results

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Compute aggregated audit metrics."""
        with self._lock:
            total = len(self._records)
            if total == 0:
                return {
                    "total_queries": 0,
                    "avg_duration_sec": 0.0,
                    "success_rate_pct": 100.0,
                    "task_distribution": {}
                }

            completed = sum(1 for r in self._records.values() if r.status == "COMPLETED")
            total_duration = sum(r.duration_sec for r in self._records.values())
            tasks: Dict[str, int] = {}
            for r in self._records.values():
                tasks[r.task] = tasks.get(r.task, 0) + 1

            return {
                "total_queries": total,
                "avg_duration_sec": round(total_duration / total, 3),
                "success_rate_pct": round((completed / total) * 100, 1),
                "task_distribution": tasks
            }


audit_service = AuditService()
