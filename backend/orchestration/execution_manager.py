import json
import datetime
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from schemas.execution import ExecutionRecord, TraceStep, StepStatusEnum
from orchestration.workflow_manager import workflow_manager
from database.session import get_db_session, init_db
from database.models import ExecutionModel, TraceStepModel, EvidenceItemModel

logger = logging.getLogger("satquery.orchestration.execution_manager")


class ExecutionManager:
    def __init__(self):
        # Ensure database tables exist
        init_db()

    def _model_to_record(self, model: ExecutionModel) -> ExecutionRecord:
        trace_steps: List[TraceStep] = []
        for s in sorted(model.trace_steps, key=lambda x: x.step_number):
            try:
                status_val = StepStatusEnum(s.status)
            except ValueError:
                status_val = StepStatusEnum.COMPLETED
            trace_steps.append(
                TraceStep(
                    id=s.step_number,
                    title=s.title,
                    description=s.description,
                    status=status_val,
                    timestamp=s.timestamp
                )
            )

        result_dict = None
        if model.result_json:
            try:
                result_dict = json.loads(model.result_json)
            except Exception:
                result_dict = {"raw": model.result_json}

        return ExecutionRecord(
            execution_id=model.id,
            task=model.task,
            status=model.status,
            query=model.query,
            input_type=model.input_type,
            started_at=model.started_at,
            completed_at=model.completed_at,
            duration_sec=model.duration_sec,
            trace_steps=trace_steps,
            result=result_dict
        )

    def create_execution(
        self,
        execution_id: str,
        task: str,
        query: str,
        input_type: str,
        workflow_name: Optional[str] = None
    ) -> ExecutionRecord:
        """Initialize and persist a new execution record with initial trace steps in SQLite."""
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Build initial trace steps from workflow definition if available
        step_definitions: List[Dict[str, Any]] = []
        wf = workflow_manager.get_workflow(workflow_name) if workflow_name else None
        if wf:
            for s in wf.steps:
                step_definitions.append({
                    "step_number": s.id,
                    "title": s.title,
                    "description": s.description
                })
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
                step_definitions.append({
                    "step_number": idx,
                    "title": title,
                    "description": f"Operational step {idx}: {title}"
                })

        with get_db_session() as session:
            exec_model = ExecutionModel(
                id=execution_id,
                task=task,
                status="RUNNING",
                query=query,
                input_type=input_type,
                started_at=now_str
            )
            session.add(exec_model)

            for step_def in step_definitions:
                step_model = TraceStepModel(
                    execution_id=execution_id,
                    step_number=step_def["step_number"],
                    title=step_def["title"],
                    description=step_def["description"],
                    status="PENDING"
                )
                session.add(step_model)

        return self.get_execution(execution_id)

    def update_step(
        self,
        execution_id: str,
        step_id: int,
        status: StepStatusEnum,
        description: Optional[str] = None
    ) -> None:
        """Update the status of a specific step in an execution trace atomically."""
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with get_db_session() as session:
            stmt = select(TraceStepModel).where(
                TraceStepModel.execution_id == execution_id,
                TraceStepModel.step_number == step_id
            )
            step = session.scalars(stmt).first()
            if step:
                step.status = status.value if hasattr(status, "value") else str(status)
                if description:
                    step.description = description
                step.timestamp = now_str

    def complete_execution(
        self,
        execution_id: str,
        result: Optional[Dict[str, Any]] = None,
        duration_sec: float = 0.0,
        status: str = "COMPLETED"
    ) -> Optional[ExecutionRecord]:
        """Mark an execution as completed, persist result payload and evidence."""
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with get_db_session() as session:
            stmt = select(ExecutionModel).where(ExecutionModel.id == execution_id).options(
                selectinload(ExecutionModel.trace_steps)
            )
            exec_model = session.scalars(stmt).first()
            if not exec_model:
                return None

            exec_model.status = status
            exec_model.completed_at = now_str
            exec_model.duration_sec = duration_sec
            if result:
                exec_model.result_json = json.dumps(result)
                exec_model.answer = result.get("answer")
                exec_model.confidence = result.get("confidence")
                exec_model.confidence_explanation = result.get("confidence_explanation")
                exec_model.model_used = result.get("model_used")
                exec_model.change_percentage = result.get("change_percentage")

                # Persist evidence items if present in result
                evidence_list = result.get("evidence", [])
                for ev in evidence_list:
                    ev_id = ev.get("id") or f"ev-{execution_id[:8]}-{len(exec_model.evidence_items)}"
                    ev_model = EvidenceItemModel(
                        id=ev_id,
                        execution_id=execution_id,
                        title=ev.get("title", "Evidence Item"),
                        description=ev.get("description", ""),
                        type=ev.get("type", "metrics"),
                        source=ev.get("source"),
                        limitations_json=json.dumps(ev.get("limitations", [])),
                        url=ev.get("url"),
                        metrics_json=json.dumps(ev.get("metrics")) if ev.get("metrics") else None
                    )
                    session.merge(ev_model)

            # Mark any remaining pending/running steps as completed
            for step in exec_model.trace_steps:
                if step.status in ("PENDING", "RUNNING"):
                    step.status = "COMPLETED"
                    if not step.timestamp:
                        step.timestamp = now_str

        return self.get_execution(execution_id)

    def fail_execution(
        self,
        execution_id: str,
        error_message: str,
        duration_sec: float = 0.0
    ) -> Optional[ExecutionRecord]:
        """Mark an execution as failed and record error message."""
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with get_db_session() as session:
            stmt = select(ExecutionModel).where(ExecutionModel.id == execution_id).options(
                selectinload(ExecutionModel.trace_steps)
            )
            exec_model = session.scalars(stmt).first()
            if not exec_model:
                return None

            exec_model.status = "FAILED"
            exec_model.completed_at = now_str
            exec_model.duration_sec = duration_sec
            exec_model.result_json = json.dumps({"error": error_message})

        return self.get_execution(execution_id)

    def get_execution(self, execution_id: str) -> Optional[ExecutionRecord]:
        """Retrieve execution record by UUID from SQLite database."""
        with get_db_session() as session:
            stmt = select(ExecutionModel).where(ExecutionModel.id == execution_id).options(
                selectinload(ExecutionModel.trace_steps),
                selectinload(ExecutionModel.evidence_items)
            )
            exec_model = session.scalars(stmt).first()
            if not exec_model:
                return None
            return self._model_to_record(exec_model)

    def list_executions(self, limit: int = 50, task: Optional[str] = None) -> List[ExecutionRecord]:
        """List execution records newest first from SQLite database."""
        with get_db_session() as session:
            stmt = select(ExecutionModel).options(
                selectinload(ExecutionModel.trace_steps)
            )
            if task:
                stmt = stmt.where(ExecutionModel.task == task)
            stmt = stmt.order_by(ExecutionModel.created_at.desc()).limit(limit)

            records = session.scalars(stmt).all()
            return [self._model_to_record(r) for r in records]


execution_manager = ExecutionManager()
