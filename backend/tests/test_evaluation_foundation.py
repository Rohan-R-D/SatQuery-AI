import pytest
from ai.evaluation import (
    EvaluationEngine,
    EvaluationRecord,
    compute_exact_match,
    compute_evidence_consistency,
    compute_token_similarity,
)


def test_metric_computation_exact_match():
    assert compute_exact_match("Urban fabric", "urban fabric") == 1.0
    assert compute_exact_match("Forest cover", "water body") == 0.0
    assert compute_exact_match("", "ref") == 0.0


def test_metric_computation_token_similarity():
    sim = compute_token_similarity("dense urban fabric and roads", "urban fabric with roads")
    assert sim >= 0.5
    assert compute_token_similarity("water body", "desert dunes") == 0.0



def test_metric_computation_evidence_consistency():
    evidence = ["NDVI vegetation index 0.75", "Built-up urban structures"]
    consistency = compute_evidence_consistency("High NDVI vegetation with urban structures", evidence)
    assert consistency == 1.0


def test_evaluation_engine_sample_record_creation():
    engine = EvaluationEngine()
    prediction_response = {
        "answer": "Industrial port area with shipping containers.",
        "model": "gemini-vlm",
        "model_version": "1.5-flash",
        "provider": "gemini",
        "evidence": ["Shipping containers", "Port area"],
        "is_error": False,
    }

    record = engine.evaluate_sample(
        prediction_response=prediction_response,
        prompt="Describe port features.",
        sample_id="test_patch_001",
        reference_answer="Industrial port area with shipping containers.",
        dataset_name="rsvqa_synthetic",
        dataset_split="test",
        runtime_ms=125.0,
        is_synthetic=True,
    )

    assert isinstance(record, EvaluationRecord)
    assert record.metrics["exact_match"] == 1.0
    assert record.metrics["token_similarity"] == 1.0
    assert record.is_synthetic is True

    summary = engine.compute_summary_statistics()
    assert summary["total_records"] == 1
    assert summary["error_rate"] == 0.0
    assert summary["avg_runtime_ms"] == 125.0
    assert summary["mean_metrics"]["exact_match"] == 1.0
