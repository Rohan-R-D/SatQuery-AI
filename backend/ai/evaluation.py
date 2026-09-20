"""
SatQuery AI - Evaluation Foundation for Phase 5 Integration.

Provides structured evaluation records, metric computation functions, and
in-memory evaluation benchmarking utilities for VQA and scene captioning responses.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid


def compute_exact_match(prediction: str, reference: str) -> float:
    """Computes exact string match ratio (0.0 or 1.0) after basic normalization."""
    if not prediction or not reference:
        return 0.0
    norm_pred = prediction.strip().lower()
    norm_ref = reference.strip().lower()
    return 1.0 if norm_pred == norm_ref else 0.0


def compute_token_similarity(prediction: str, reference: str) -> float:
    """Computes Jaccard word token overlap similarity (0.0 to 1.0)."""
    if not prediction or not reference:
        return 0.0
    pred_tokens = set(prediction.strip().lower().split())
    ref_tokens = set(reference.strip().lower().split())
    if not pred_tokens or not ref_tokens:
        return 0.0
    intersection = pred_tokens.intersection(ref_tokens)
    union = pred_tokens.union(ref_tokens)
    return len(intersection) / len(union)


def compute_evidence_consistency(prediction: str, evidence: List[str]) -> float:
    """Computes ratio of scientific evidence keywords mentioned in generated prediction."""
    if not prediction or not evidence:
        return 1.0  # Neutral consistency when no evidence required
    pred_lower = prediction.lower()
    matches = 0
    for ev in evidence:
        ev_words = [w.lower() for w in str(ev).split() if len(w) > 3]
        if any(w in pred_lower for w in ev_words):
            matches += 1
    return matches / len(evidence) if evidence else 1.0


@dataclass
class EvaluationRecord:
    """
    Structured evaluation record for logging and benchmarking VQA predictions.
    """
    record_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    model_id: str = "gemini-vlm"
    model_version: str = "1.5-flash"
    provider: str = "gemini"
    dataset_name: str = "rsvqa_synthetic_test"
    dataset_split: str = "test"
    sample_id: str = "sample_001"
    prompt: str = ""
    generated_answer: str = ""
    reference_answer: Optional[str] = None
    metrics: Dict[str, float] = field(default_factory=dict)
    runtime_ms: float = 0.0
    gpu_info: Optional[str] = None
    is_error: bool = False
    failure_reason: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    is_synthetic: bool = True
    is_mock: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "record_id": self.record_id,
            "model_id": self.model_id,
            "model_version": self.model_version,
            "provider": self.provider,
            "dataset_name": self.dataset_name,
            "dataset_split": self.dataset_split,
            "sample_id": self.sample_id,
            "prompt": self.prompt,
            "generated_answer": self.generated_answer,
            "reference_answer": self.reference_answer,
            "metrics": self.metrics,
            "runtime_ms": self.runtime_ms,
            "gpu_info": self.gpu_info,
            "is_error": self.is_error,
            "failure_reason": self.failure_reason,
            "timestamp": self.timestamp,
            "is_synthetic": self.is_synthetic,
            "is_mock": self.is_mock,
        }


class EvaluationEngine:
    """
    Lightweight benchmark engine to evaluate model outputs and compute aggregate metrics.
    Explicitly separates mock/offline evaluation runs from real model benchmark runs.
    """

    def __init__(self):
        self.records: List[EvaluationRecord] = []

    def evaluate_sample(
        self,
        prediction_response: Dict[str, Any],
        prompt: str,
        sample_id: str = "sample_0",
        reference_answer: Optional[str] = None,
        dataset_name: str = "synthetic_fixture",
        dataset_split: str = "val",
        runtime_ms: float = 0.0,
        is_synthetic: bool = True,
        is_mock: bool = True,
    ) -> EvaluationRecord:
        """
        Evaluates a single prediction response dictionary against optional reference ground truth.
        """
        answer = prediction_response.get("answer", "")
        model_id = prediction_response.get("model", "gemini-vlm")
        model_version = prediction_response.get("model_version", "default")
        provider = prediction_response.get("provider", "gemini")
        evidence = prediction_response.get("evidence", [])
        is_err = prediction_response.get("is_error", False)
        err_code = prediction_response.get("error_code")
        
        # Override is_mock if prediction_response specifies it explicitly
        sample_is_mock = prediction_response.get("is_mock", is_mock)

        metrics = {}
        if reference_answer:
            metrics["exact_match"] = compute_exact_match(answer, reference_answer)
            metrics["token_similarity"] = compute_token_similarity(answer, reference_answer)

        metrics["evidence_consistency"] = compute_evidence_consistency(answer, evidence)

        record = EvaluationRecord(
            model_id=model_id,
            model_version=model_version,
            provider=provider,
            dataset_name=dataset_name,
            dataset_split=dataset_split,
            sample_id=sample_id,
            prompt=prompt,
            generated_answer=answer,
            reference_answer=reference_answer,
            metrics=metrics,
            runtime_ms=runtime_ms,
            is_error=is_err,
            failure_reason=err_code if is_err else None,
            is_synthetic=is_synthetic,
            is_mock=sample_is_mock,
        )

        self.records.append(record)
        return record

    def compute_summary_statistics(self) -> Dict[str, Any]:
        """
        Computes summary statistics across all evaluated records in engine.
        Separates mock evaluation counts from real evaluation counts.
        """
        if not self.records:
            return {
                "total_records": 0,
                "mock_records": 0,
                "real_records": 0,
                "eval_mode": "EMPTY",
                "error_rate": 0.0,
                "avg_runtime_ms": 0.0,
                "mean_metrics": {},
                "is_synthetic": True,
                "is_mock": True,
            }

        total = len(self.records)
        mock_count = sum(1 for r in self.records if r.is_mock)
        real_count = total - mock_count
        errors = sum(1 for r in self.records if r.is_error)
        avg_runtime = sum(r.runtime_ms for r in self.records) / total

        if mock_count == total:
            eval_mode = "MOCK_OFFLINE"
        elif real_count == total:
            eval_mode = "REAL_BENCHMARK"
        else:
            eval_mode = "HYBRID"

        # Aggregate metric means
        metric_sums: Dict[str, float] = {}
        metric_counts: Dict[str, int] = {}

        for r in self.records:
            for k, v in r.metrics.items():
                metric_sums[k] = metric_sums.get(k, 0.0) + v
                metric_counts[k] = metric_counts.get(k, 0) + 1

        mean_metrics = {k: round(metric_sums[k] / metric_counts[k], 4) for k in metric_sums}

        return {
            "total_records": total,
            "mock_records": mock_count,
            "real_records": real_count,
            "eval_mode": eval_mode,
            "error_rate": round(errors / total, 4),
            "avg_runtime_ms": round(avg_runtime, 2),
            "mean_metrics": mean_metrics,
            "is_synthetic": any(r.is_synthetic for r in self.records),
            "is_mock": mock_count > 0,
        }
