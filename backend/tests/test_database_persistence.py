import uuid
import pytest
from sqlalchemy import select
from fastapi.testclient import TestClient

from main import app
from database.session import get_db_session, init_db
from database.models import ExecutionModel, TraceStepModel, EvidenceItemModel
from orchestration.execution_manager import ExecutionManager
from services.audit_service import audit_service
from schemas.execution import StepStatusEnum

client = TestClient(app)


def test_database_initialization():
    """Verify SQLite database schema initializes cleanly."""
    init_db()
    with get_db_session() as session:
        # Check that we can query the tables
        count = session.scalar(select(ExecutionModel).limit(1))
        assert count is None or isinstance(count, ExecutionModel)


def test_execution_persistence_lifecycle():
    """Verify full execution lifecycle persists to SQLite and survives across manager instances."""
    exec_id = str(uuid.uuid4())
    mgr1 = ExecutionManager()

    # 1. Create execution
    record = mgr1.create_execution(
        execution_id=exec_id,
        task="bi_temporal_change",
        query="What infrastructure expanded between these dates?",
        input_type="bi_temporal"
    )
    assert record.execution_id == exec_id
    assert record.status == "RUNNING"
    assert len(record.trace_steps) == 8

    # 2. Update specific step
    mgr1.update_step(
        execution_id=exec_id,
        step_id=2,
        status=StepStatusEnum.COMPLETED,
        description="Co-registration verified with RMSE = 0.42px."
    )

    # 3. Complete execution
    result_data = {
        "answer": "Commercial expansion of 4.2 hectares detected.",
        "confidence": 91.0,
        "confidence_explanation": "Co-registration RMSE = 0.42px.",
        "model_used": "OpenCV Difference Engine",
        "change_percentage": 3.85,
        "evidence": [
            {
                "id": f"ev-{exec_id[:8]}-1",
                "title": "Change Mask",
                "description": "Detected 3.85% pixel difference.",
                "type": "mask",
                "source": "opencv_baseline",
                "limitations": ["Seasonal sun angle difference"]
            }
        ]
    }
    mgr1.complete_execution(
        execution_id=exec_id,
        result=result_data,
        duration_sec=1.25,
        status="COMPLETED"
    )

    # 4. Simulate complete server restart / fresh manager instance
    mgr2 = ExecutionManager()
    persisted_record = mgr2.get_execution(exec_id)
    assert persisted_record is not None
    assert persisted_record.execution_id == exec_id
    assert persisted_record.status == "COMPLETED"
    assert persisted_record.duration_sec == 1.25
    assert persisted_record.result["change_percentage"] == 3.85
    assert persisted_record.trace_steps[1].description == "Co-registration verified with RMSE = 0.42px."

    # 5. Verify API endpoints read from persistent storage
    api_resp = client.get(f"/api/executions/{exec_id}")
    assert api_resp.status_code == 200
    api_json = api_resp.json()
    assert api_json["execution_id"] == exec_id
    assert api_json["status"] == "COMPLETED"
    assert len(api_json["trace_steps"]) == 8

    # 6. Verify audit overview aggregates persistent SQLite rows
    audit_resp = client.get("/api/audit")
    assert audit_resp.status_code == 200
    audit_json = audit_resp.json()
    assert audit_json["metrics"]["total_queries"] >= 1
    assert "bi_temporal_change" in audit_json["metrics"]["task_distribution"]


def test_cascade_deletion():
    """Verify that deleting an Execution cascades to its TraceSteps and EvidenceItems."""
    exec_id = str(uuid.uuid4())
    mgr = ExecutionManager()
    mgr.create_execution(
        execution_id=exec_id,
        task="single_image_vqa",
        query="Locate water bodies",
        input_type="single"
    )
    mgr.complete_execution(
        execution_id=exec_id,
        result={
            "answer": "Water detected",
            "evidence": [{"id": f"ev-{exec_id[:8]}-water", "title": "Water", "description": "Lake", "type": "metrics"}]
        }
    )

    with get_db_session() as session:
        exec_row = session.get(ExecutionModel, exec_id)
        assert exec_row is not None
        session.delete(exec_row)

    # After commit, child rows should be deleted
    with get_db_session() as session:
        steps = session.scalars(select(TraceStepModel).where(TraceStepModel.execution_id == exec_id)).all()
        evidence = session.scalars(select(EvidenceItemModel).where(EvidenceItemModel.execution_id == exec_id)).all()
        assert len(steps) == 0
        assert len(evidence) == 0
