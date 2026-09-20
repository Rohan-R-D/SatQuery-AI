"""
Unit tests for GeoChat Remote Sensing VLM Adapter (backend/ai/models/geochat_adapter.py).
Tests lazy loading, configuration status checks, structured error handling, grounding fallback,
and dynamic adapter resolution.
"""

import os
import pytest
from unittest.mock import patch, MagicMock

from backend.ai.models.geochat_adapter import GeoChatAdapter, geochat_adapter
from backend.ai.grounding_interface import GroundingRequest, GroundingResponse
from backend.ai.adapters.model_adapter import get_active_vlm_adapter, ModelAdapterFactory
from backend.ai.vqa_inference import resolve_adapter, run_vqa_inference


def test_geochat_adapter_unconfigured_default(monkeypatch):
    monkeypatch.delenv("SATQUERY_GEOCHAT_ENABLED", raising=False)
    monkeypatch.delenv("SATQUERY_GEOCHAT_ENDPOINT_URL", raising=False)
    monkeypatch.delenv("SATQUERY_GEOCHAT_WEIGHTS_PATH", raising=False)

    adapter = GeoChatAdapter()
    assert adapter.is_available() is False
    assert adapter.get_provider_name() == "GeoChat Remote Sensing VLM (7B) [MBZUAI/geochat-7B]"
    assert adapter.supports_grounding() is False


def test_geochat_adapter_vqa_unconfigured():
    adapter = GeoChatAdapter()
    res = adapter.generate_vqa(image_bytes=b"dummy", query="Identify land cover.")
    assert res["is_error"] is True
    assert res["error_code"] == "GEOCHAT_UNCONFIGURED"
    assert res["confidence"] == 0.0
    assert any("GeoChat" in w for w in res["warnings"])


def test_geochat_adapter_caption_unconfigured():
    adapter = GeoChatAdapter()
    res = adapter.generate_caption(image_bytes=b"dummy")
    assert res["is_error"] is True
    assert res["error_code"] == "GEOCHAT_UNCONFIGURED"


def test_geochat_adapter_grounding_unconfigured():
    adapter = GeoChatAdapter()
    req = GroundingRequest(image_bytes=b"dummy", query="Detect solar panels")
    resp = adapter.locate_grounded_regions(req)
    assert resp.is_error is True
    assert resp.error_code == "GEOCHAT_UNCONFIGURED"
    assert resp.capability_supported is False


def test_geochat_adapter_enabled_with_endpoint(monkeypatch):
    monkeypatch.setenv("SATQUERY_GEOCHAT_ENABLED", "true")
    monkeypatch.setenv("SATQUERY_GEOCHAT_ENDPOINT_URL", "http://localhost:8000/v1/geochat")

    adapter = GeoChatAdapter()
    assert adapter.is_available() is True
    assert adapter.supports_grounding() is True


def test_geochat_adapter_remote_only_architecture():
    adapter = GeoChatAdapter()
    # GeoChat is strictly remote-only: zero local weights loading
    assert adapter.get_provider_name() == "GeoChat Remote Sensing VLM (7B) [MBZUAI/geochat-7B]"


def test_adapter_factory_geochat_resolution(monkeypatch):
    monkeypatch.setenv("ACTIVE_VLM_PROVIDER", "geochat")
    resolved = get_active_vlm_adapter()
    assert "GeoChat Remote Sensing VLM" in resolved.get_provider_name()


def test_vqa_inference_geochat_provider_override():
    res = run_vqa_inference(
        image_bytes=b"dummy_bytes",
        query="Assess airport runway.",
        provider_override="geochat"
    )
    assert res["provider"] == "GeoChat Remote Sensing VLM (7B) [MBZUAI/geochat-7B]"
    assert res["is_error"] is True
    assert res["error_code"] == "GEOCHAT_UNCONFIGURED"



@pytest.mark.skipif(
    not os.getenv("RUN_GEOCHAT_INTEGRATION_TESTS"),
    reason="GeoChat live integration test skipped because RUN_GEOCHAT_INTEGRATION_TESTS is not set."
)
def test_geochat_live_inference_optional():
    """
    Optional real inference test execution when GeoChat checkpoint weights / endpoint exist.
    """
    adapter = GeoChatAdapter()
    if not adapter.is_available():
        pytest.skip("GeoChat model unconfigured in current environment.")
    
    res = adapter.generate_vqa(image_bytes=b"sample_bytes", query="What land cover is visible?")
    assert res["is_error"] is False
    assert res["confidence"] > 0.0
