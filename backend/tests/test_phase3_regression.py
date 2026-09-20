"""
Regression tests for Phase 3 functionality including VLM Adapters, Model Registry,
Scientific Evidence Interface, VQA Inference Engine, and Evaluation Engine.
"""

import pytest
import os
from unittest.mock import MagicMock, patch

from backend.ai.models.gemini_adapter import GeminiAdapter
from backend.ai.models.base_model import BaseVLMAdapter
from backend.orchestration.model_registry import ModelRegistry, model_registry
from backend.schemas.responses import ModelInfo, ModelStatusEnum, AnalysisResponse
from backend.ai.evidence_interface import ScientificEvidence, create_synthetic_evidence_fixture, format_evidence_for_prompt
from backend.ai.vqa_inference import run_vqa_inference, run_caption_inference, normalize_vqa_response
from backend.ai.evaluation import EvaluationEngine, EvaluationRecord, compute_exact_match, compute_token_similarity


def test_gemini_adapter_unconfigured_api_key():
    with patch("backend.ai.models.gemini_adapter.gemini_service.is_available", return_value=False):
        adapter = GeminiAdapter()
        assert adapter.is_available() is False


def test_model_registry_registered_models():
    registry = ModelRegistry()

    # Query registered models
    response = registry.get_registered_models()
    assert len(response.models) >= 1

    gemini_info = registry.get_model("gemini-vlm")
    assert gemini_info is not None
    assert gemini_info.provider == "google-gemini"
    assert gemini_info.status == ModelStatusEnum.TEMPORARY_BASELINE


def test_scientific_evidence_interface():
    evidence = create_synthetic_evidence_fixture(
        ndvi=0.75,
        ndwi=-0.20,
        sar_vv_mean_db=-10.5,
    )

    assert isinstance(evidence, ScientificEvidence)
    assert evidence.is_synthetic is True
    assert evidence.spectral_indices["NDVI"] == 0.75

    dict_repr = evidence.to_dict()
    assert dict_repr["is_synthetic"] is True

    prompt_summary = format_evidence_for_prompt(evidence)
    assert "NDVI=0.750" in prompt_summary


def test_vqa_inference_normalization():
    raw_dict = {
        "answer": "The river shows high turbidity.",
        "confidence": 0.88,
    }
    normalized = normalize_vqa_response(raw_dict, provider="gemini-vlm")
    assert normalized["answer"] == "The river shows high turbidity."
    assert normalized["confidence"] == 0.88
    assert normalized["provider"] == "gemini-vlm"


def test_evaluation_engine_metrics():
    engine = EvaluationEngine()

    pred_res1 = {"answer": "Dense forest area", "model": "gemini-vlm", "provider": "gemini", "evidence": []}
    record1 = engine.evaluate_sample(
        prediction_response=pred_res1,
        prompt="What land cover is visible?",
        reference_answer="Dense forest area",
    )
    assert record1.metrics["exact_match"] == 1.0
    assert record1.metrics["token_similarity"] == 1.0

    pred_res2 = {"answer": "Agricultural land", "model": "gemini-vlm", "provider": "gemini", "evidence": []}
    record2 = engine.evaluate_sample(
        prediction_response=pred_res2,
        prompt="What land cover is visible?",
        reference_answer="Water body",
    )
    assert record2.metrics["exact_match"] == 0.0
    assert record2.metrics["token_similarity"] == 0.0

    summary = engine.compute_summary_statistics()
    assert summary["total_records"] == 2
    assert summary["mean_metrics"]["exact_match"] == 0.5


def test_analysis_response_schema_compatibility():
    resp = AnalysisResponse(
        success=True,
        task="single_image_vqa",
        input_type="single",
        answer="Yes, it shows dense forest.",
        confidence=92.0,
        confidence_explanation="High confidence based on visual features",
        model_used="gemini-vlm",
        processing_time=0.45,
    )

    assert resp.success is True
    assert resp.task == "single_image_vqa"
    assert resp.answer == "Yes, it shows dense forest."
    assert resp.model_used == "gemini-vlm"
