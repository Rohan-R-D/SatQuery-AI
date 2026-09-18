import datetime
import threading
import logging
from typing import Dict, List, Optional, Any
from schemas.execution import ExecutionRecord, TraceStep, StepStatusEnum
from orchestration.workflow_manager import workflow_manager

logger = logging.getLogger("satquery.orchestration.execution_manager")


class ExecutionManager:
    def __init__(self, max_records: int = 500):
        self._records: Dict[str, ExecutionRecord] = {}
        self._order: List[str] = []
        self._max_records = max_records
        self._lock = threading.Lock()

    def create_execution(
        self,
        execution_id: str,
        task: str,
        query: str,
        input_type: str,
        workflow_name: Optional[str] = None
    ) -> ExecutionRecord:
        """Initialize and store a new execution record with initial trace steps."""
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        # Build initial trace steps from workflow definition if available
        trace_steps: List[TraceStep] = []
        wf = workflow_manager.get_workflow(workflow_name) if workflow_name else None
        if wf:
            for s in wf.steps:
                trace_steps.append(
                    TraceStep(
                        id=s.id,
                        title=s.title,
                        description=s.description,
                        status=StepStatusEnum.PENDING
                    )
                )
        else:
            default_step_titles = [
                "Query Understanding",
                "Input Validation",
                "Task Classification",
                "Model Selection",
                "Analysis Execution",
                "Evidence Generation",
                "Confidence Calculation",
                "Response Generation",
            ]
            for idx, title in enumerate(default_step_titles, 1):
                trace_steps.append(
                    TraceStep(
                        id=idx,
                        title=title,
                        description=f"Operational step {idx}: {title}",
                        status=StepStatusEnum.PENDING
                    )
                )

        record = ExecutionRecord(
            execution_id=execution_id,
            task=task,
            status="RUNNING",
            query=query,
            input_type=input_type,
            started_at=now_str,
            trace_steps=trace_steps
        )

        with self._lock:
            self._records[execution_id] = record
            self._order.append(execution_id)
            while len(self._order) > self._max_records:
                oldest_id = self._order.pop(0)
                self._records.pop(oldest_id, None)

        return record

    def update_step(
        self,
        execution_id: str,
        step_id: int,
        status: StepStatusEnum,
        description: Optional[str] = None
    ) -> None:
        """Update the status of a specific step in an execution trace."""
        with self._lock:
            rec = self._records.get(execution_id)
            if not rec:
                return
            for step in rec.trace_steps:
                if step.id == step_id:
                    step.status = status
                    if description:
                        step.description = description
                    step.timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
                    break

    def complete_execution(
        self,
        execution_id: str,
        result: Optional[Dict[str, Any]] = None,
        duration_sec: float = 0.0,
        status: str = "COMPLETED"
    ) -> Optional[ExecutionRecord]:
        """Mark an execution as completed and store summary result."""
        with self._lock:
            rec = self._records.get(execution_id)
            if not rec:
                return None
            rec.status = status
            rec.completed_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
            rec.duration_sec = duration_sec
            rec.result = result

            # Mark remaining pending steps as completed
            for step in rec.trace_steps:
                if step.status == StepStatusEnum.PENDING or step.status == StepStatusEnum.RUNNING:
                    step.status = StepStatusEnum.COMPLETED
            return rec

    def fail_execution(
        self,
        execution_id: str,
        error_message: str,
        duration_sec: float = 0.0
    ) -> Optional[ExecutionRecord]:
        """Mark an execution as failed."""
        with self._lock:
            rec = self._records.get(execution_id)
            if not rec:
                return None
            rec.status = "FAILED"
            rec.completed_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
            rec.duration_sec = duration_sec
            rec.result = {"error": error_message}
            return rec

    def get_execution(self, execution_id: str) -> Optional[ExecutionRecord]:
        """Retrieve execution record by UUID."""
        with self._lock:
            return self._records.get(execution_id)

    def list_executions(self, limit: int = 50) -> List[ExecutionRecord]:
        """List execution records newest first."""
        with self._lock:
            results = []
            for exec_id in reversed(self._order):
                rec = self._records.get(exec_id)
                if rec:
                    results.append(rec)
                if len(results) >= limit:
                    break
            return results


execution_manager = ExecutionManager()
