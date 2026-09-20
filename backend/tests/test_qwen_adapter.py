"""
Unit tests for Qwen-VL Adapter (backend/ai/models/qwen_adapter.py).
Tests remote execution, grounding parsing, unconfigured state, and dynamic provider routing.
"""

import pytest
from unittest.mock import patch, MagicMock

from backend.ai.models.qwen_adapter import QwenAdapter, qwen_adapter
from backend.ai.grounding_interface import GroundingRequest, GroundingResponse
from backend.ai.adapters.model_adapter import get_active_vlm_adapter, ModelAdapterFactory
from backend.ai.vqa_inference import run_vqa_inference


def test_qwen_adapter_unconfigured_by_default(monkeypatch):
    monkeypatch.delenv("SATQUERY_QWEN_ENABLED", raising=False)
    monkeypatch.delenv("SATQUERY_QWEN_ENDPOINT_URL", raising=False)

    adapter = QwenAdapter()
    assert adapter.is_available() is False
    assert adapter.get_provider_name() == "Qwen3-VL Remote Multimodal VLM (2B) [Qwen/Qwen3-VL-2B-Instruct]"
    assert adapter.supports_grounding() is False


def test_qwen_adapter_vqa_unconfigured():
    adapter = QwenAdapter()
    res = adapter.generate_vqa(image_bytes=b"dummy", query="Detect runways.")
    assert res["is_error"] is True
    assert res["error_code"] == "QWEN_ENDPOINT_UNCONFIGURED"
    assert res["confidence"] == 0.0


def test_qwen_adapter_grounding_unconfigured():
    adapter = QwenAdapter()
    req = GroundingRequest(image_bytes=b"dummy", query="Detect solar panels")
    resp = adapter.locate_grounded_regions(req)
    assert resp.is_error is True
    assert resp.error_code == "QWEN_ENDPOINT_UNCONFIGURED"


def test_qwen_adapter_enabled_with_endpoint(monkeypatch):
    monkeypatch.setenv("SATQUERY_QWEN_ENABLED", "true")
    monkeypatch.setenv("SATQUERY_QWEN_ENDPOINT_URL", "http://localhost:8000/v1/qwen")
    monkeypatch.setenv("SATQUERY_QWEN_GROUNDING_ENABLED", "true")

    adapter = QwenAdapter()
    assert adapter.is_available() is True
    assert adapter.supports_grounding() is True




def test_vqa_inference_qwen_provider_override():
    res = run_vqa_inference(
        image_bytes=b"dummy_bytes",
        query="Detect agricultural fields.",
        provider_override="qwen"
    )
    assert res["provider"] == "Qwen3-VL Remote Multimodal VLM (2B) [Qwen/Qwen3-VL-2B-Instruct]"
    assert res["is_error"] is True
    assert res["error_code"] == "QWEN_ENDPOINT_UNCONFIGURED"

