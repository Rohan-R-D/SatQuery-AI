import pytest
from unittest.mock import MagicMock, patch

from ai.adapters.model_adapter import get_active_vlm_adapter
from ai.evidence_interface import create_synthetic_evidence_fixture
from ai.vqa_inference import (
    normalize_vqa_response,
    resolve_adapter,
    run_caption_inference,
    run_vqa_inference,
)
from agents.vqa_agent import vqa_agent


def test_default_adapter_resolution(monkeypatch):
    monkeypatch.delenv("ACTIVE_VLM_PROVIDER", raising=False)
    adapter = get_active_vlm_adapter()
    assert adapter.get_provider_name() == "Gemini Multimodal VLM (Baseline)"


def test_custom_provider_override_resolution():
    adapter = resolve_adapter(provider_override="custom")
    assert "Sovereign RS-VLM" in adapter.get_provider_name()


def test_vqa_inference_missing_image():
    res = run_vqa_inference(image_bytes=b"", query="What is in this image?")
    assert res["is_error"] is True
    assert res["error_code"] == "INVALID_INPUT"
    assert "Input image payload was zero bytes." in res["warnings"]


def test_vqa_inference_empty_query():
    res = run_vqa_inference(image_bytes=b"dummy_image_bytes", query="   ")
    assert res["is_error"] is True
    assert res["error_code"] == "INVALID_INPUT"
    assert "VQA query parameter was empty." in res["warnings"]


def test_vqa_inference_unconfigured_custom_provider():
    res = run_vqa_inference(
        image_bytes=b"dummy_bytes",
        query="Identify land cover.",
        provider_override="custom"
    )
    assert res["provider"] == "Qwen3-VL-RS-Adapted (Sovereign RS-VLM)"
    assert res["is_error"] is True
    assert res["error_code"] == "VLM_ENDPOINT_UNCONFIGURED"


def test_vqa_inference_with_synthetic_evidence():
    synth_evidence = create_synthetic_evidence_fixture(ndvi=0.72, ndwi=-0.3, change_pct=14.5)
    
    with patch("ai.models.gemini_adapter.gemini_service.analyze_image") as mock_gemini:
        mock_gemini.return_value = {
            "answer": "Dense vegetation identified with high NDVI value.",
            "evidence": ["NDVI 0.72"],
            "confidence": 95.0,
            "is_error": False
        }
        res = run_vqa_inference(
            image_bytes=b"sample_image_bytes",
            query="Assess vegetation health.",
            scientific_evidence=synth_evidence,
            provider_override="gemini"
        )
        assert res["is_error"] is False
        assert "Dense vegetation" in res["answer"]
        assert any("synthetic test fixture" in w for w in res["warnings"])


def test_caption_inference_execution():
    with patch("ai.models.gemini_adapter.gemini_service.generate_caption") as mock_caption:
        mock_caption.return_value = {
            "caption": "Satellite overview displaying coastal structures and urban fabric.",
            "scene_features": ["Coastal area", "Urban fabric"],
            "confidence": 92.0,
            "is_error": False
        }
        res = run_caption_inference(image_bytes=b"sample_bytes", provider_override="gemini")
        assert res["is_error"] is False
        assert "coastal structures" in res["answer"]
        assert res["confidence"] == 92.0


def test_vqa_agent_integration():
    with patch("ai.models.gemini_adapter.gemini_service.analyze_image") as mock_gemini:
        mock_gemini.return_value = {
            "answer": "Industrial units visible near port facilities.",
            "evidence": ["Port structure"],
            "confidence": 88.0,
            "is_error": False
        }
        res = vqa_agent.execute_vqa(image_bytes=b"sample_bytes", query="Where are industrial units?")
        assert res["is_error"] is False
        assert "Industrial units" in res["answer"]
        assert "model_used" in res
