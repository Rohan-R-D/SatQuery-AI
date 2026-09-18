import os
import pytest
from fastapi.testclient import TestClient
from main import app
from ai.models.base_model import BaseVLMAdapter
from ai.models.gemini_adapter import gemini_adapter
from ai.models.custom_rs_vlm_adapter import custom_rs_vlm_adapter
from ai.adapters.model_adapter import get_active_vlm_adapter, ModelAdapterFactory
from orchestration.model_registry import model_registry

client = TestClient(app)


def test_base_vlm_adapter_interface():
    """Verify that both Gemini and Custom adapters implement BaseVLMAdapter."""
    assert isinstance(gemini_adapter, BaseVLMAdapter)
    assert isinstance(custom_rs_vlm_adapter, BaseVLMAdapter)

    assert "Gemini" in gemini_adapter.get_provider_name()
    assert "Sovereign" in custom_rs_vlm_adapter.get_provider_name()


def test_model_adapter_factory_resolution(monkeypatch):
    """Verify dynamic switching between Gemini baseline and custom sovereign RS models."""
    # Test default -> Gemini
    monkeypatch.delenv("ACTIVE_VLM_PROVIDER", raising=False)
    adapter = get_active_vlm_adapter()
    assert isinstance(adapter, BaseVLMAdapter)
    assert "Gemini" in adapter.get_provider_name()

    # Test custom setting -> CustomRSVLMAdapter
    monkeypatch.setenv("ACTIVE_VLM_PROVIDER", "custom_rs_vlm")
    custom_adapter = ModelAdapterFactory.get_active_vlm()
    assert "Qwen" in custom_adapter.get_provider_name() or "Sovereign" in custom_adapter.get_provider_name()


def test_models_api_endpoint():
    """Verify GET /api/models returns model capabilities with status filters."""
    resp = client.get("/api/models")
    assert resp.status_code == 200
    res_json = resp.json()
    assert "models" in res_json
    assert len(res_json["models"]) >= 4

    # Check that baseline models exist
    model_ids = [m["id"] for m in res_json["models"]]
    assert "gemini-vlm" in model_ids
    assert "opencv-change" in model_ids
    assert "qwen3-vl-rs" in model_ids
