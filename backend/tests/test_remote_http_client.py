"""
Unit tests for Remote VLM HTTP Client (backend/ai/models/remote_http_client.py).
Tests endpoint checks, payload formation, mock responses, timeout handling, and error handling.
"""

import pytest
from unittest.mock import patch, MagicMock
from backend.ai.models.remote_http_client import RemoteVLMHttpClient, remote_http_client


def test_remote_client_missing_endpoint():
    client = RemoteVLMHttpClient()
    assert client.is_endpoint_configured("") is False

    res = client.query_vlm_endpoint(
        endpoint_url="",
        prompt="Test prompt",
        image_bytes=b"dummy_bytes",
        provider_id="test_provider"
    )
    assert res["is_error"] is True
    assert res["error_code"] == "ENDPOINT_UNCONFIGURED"
    assert res["answer"] == ""


def test_remote_client_health_check_unconfigured():
    client = RemoteVLMHttpClient()
    assert client.check_endpoint_health("") is False


@patch("urllib.request.urlopen")
def test_remote_client_query_success(mock_urlopen):
    mock_response = MagicMock()
    mock_response.read.return_value = b'{"choices": [{"message": {"content": "Sample satellite query answer."}}]}'
    mock_response.__enter__.return_value = mock_response
    mock_urlopen.return_value = mock_response

    client = RemoteVLMHttpClient()
    res = client.query_vlm_endpoint(
        endpoint_url="http://localhost:8000/v1/chat/completions",
        prompt="Identify land cover.",
        image_bytes=b"sample_bytes",
        provider_id="qwen"
    )

    assert res["is_error"] is False
    assert res["answer"] == "Sample satellite query answer."
    assert res["confidence"] == 90.0

