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


def test_specialist_agents_adapter_routing(monkeypatch):
    """Verify that specialist agents dynamically route through the active VLM adapter."""
    from agents.vqa_agent import vqa_agent
    from agents.grounding_agent import grounding_agent

    # 1. Test when provider is set to custom_rs_vlm
    monkeypatch.setenv("ACTIVE_VLM_PROVIDER", "custom_rs_vlm")
    monkeypatch.setenv("LOCAL_WEIGHTS_PATH", "/mock/path")

    res_vqa = vqa_agent.execute_vqa(b"dummy_bytes", "What is in this image?")
    assert "Qwen3-VL-RS-Adapted" in res_vqa["model_used"] or "Sovereign" in res_vqa["model_used"]
    assert res_vqa["is_error"] is False

    res_caption = vqa_agent.execute_caption(b"dummy_bytes")
    assert "Qwen3-VL-RS-Adapted" in res_caption["model_used"] or "Sovereign" in res_caption["model_used"]

    res_grounding = grounding_agent.execute_grounding(b"dummy_bytes", "water body")
    assert "Grounding Engine" in res_grounding["model_used"]
    assert "Sovereign" in res_grounding["model_used"] or "Qwen3-VL" in res_grounding["model_used"]

    # 2. Test when provider is reset to default (gemini)
    monkeypatch.delenv("ACTIVE_VLM_PROVIDER", raising=False)
    adapter = get_active_vlm_adapter()
    assert "Gemini" in adapter.get_provider_name()


def test_custom_rs_vlm_adapter_unconfigured_fallback(monkeypatch):
    """Verify CustomRSVLMAdapter returns clean fallback and VLM_ENDPOINT_UNCONFIGURED error when unconfigured."""
    monkeypatch.delenv("CUSTOM_VLM_ENDPOINT", raising=False)
    monkeypatch.delenv("LOCAL_WEIGHTS_PATH", raising=False)

    assert custom_rs_vlm_adapter.is_available() is False

    res_vqa = custom_rs_vlm_adapter.generate_vqa(b"dummy", "query")
    assert res_vqa["is_error"] is True
    assert res_vqa["error_code"] == "VLM_ENDPOINT_UNCONFIGURED"
    assert res_vqa["confidence"] == 0

    res_cap = custom_rs_vlm_adapter.generate_caption(b"dummy")
    assert res_cap["is_error"] is True
    assert res_cap["error_code"] == "VLM_ENDPOINT_UNCONFIGURED"

    res_chg = custom_rs_vlm_adapter.generate_change_explanation(b"d1", b"d2", b"d3", "query", 10.5)
    assert res_chg["is_error"] is True
    assert res_chg["error_code"] == "VLM_ENDPOINT_UNCONFIGURED"

    res_sar = custom_rs_vlm_adapter.generate_optical_sar(b"opt", b"sar", "query")
    assert res_sar["is_error"] is True
    assert res_sar["error_code"] == "VLM_ENDPOINT_UNCONFIGURED"

    res_loc = custom_rs_vlm_adapter.locate_regions(b"dummy", "query")
    assert res_loc["is_error"] is True
    assert res_loc["error_code"] == "VLM_ENDPOINT_UNCONFIGURED"

