import io
import pytest
from unittest.mock import AsyncMock, patch
from PIL import Image
from fastapi.testclient import TestClient
from main import app
from utils.rate_limiter import analyze_rate_limiter, upload_rate_limiter
from schemas.responses import AnalysisResponse

client = TestClient(app)

def create_dummy_image_bytes():
    buf = io.BytesIO()
    img = Image.new("RGB", (64, 64), color="red")
    img.save(buf, format="PNG")
    return buf.getvalue()

def test_rate_limiter_blocks_burst_on_analyze(monkeypatch):
    analyze_rate_limiter.reset()
    image_bytes = create_dummy_image_bytes()

    mock_resp = AnalysisResponse(
        success=True,
        task="single_image_vqa",
        input_type="single",
        answer="Mock answer",
        confidence=90.0,
        confidence_explanation="Mock confidence",
        model_used="Mock Model",
        evidence=[],
        execution_trace=[],
        processing_time=0.01
    )

    with patch("agents.supervisor_agent.supervisor_agent.run_pipeline", new=AsyncMock(return_value=mock_resp)):
        # The limit is 10 requests per minute
        # We send 10 requests which should pass rate limiting
        for i in range(10):
            files = {"image": ("test.png", image_bytes, "image/png")}
            data = {"input_type": "single", "query": f"Test query {i}"}
            response = client.post("/api/analyze", files=files, data=data, headers={"X-Forwarded-For": "192.168.1.100"})
            assert response.status_code == 200

        # The 11th request from the same IP MUST receive HTTP 429
        files = {"image": ("test.png", image_bytes, "image/png")}
        data = {"input_type": "single", "query": "Over limit query"}
        response = client.post("/api/analyze", files=files, data=data, headers={"X-Forwarded-For": "192.168.1.100"})
        assert response.status_code == 429
        assert "Rate limit exceeded" in response.json()["detail"]
        assert "retry-after" in response.headers
        assert int(response.headers["retry-after"]) > 0

        # A different IP address should NOT be blocked
        response_other_ip = client.post("/api/analyze", files=files, data=data, headers={"X-Forwarded-For": "192.168.1.101"})
        assert response_other_ip.status_code == 200

    # Reset limiter for other tests
    analyze_rate_limiter.reset()

def test_upload_rate_limiter_reset():
    upload_rate_limiter.reset()
    image_bytes = create_dummy_image_bytes()

    # Upload limit is 30 req/min
    for _ in range(30):
        files = {"file": ("test.png", image_bytes, "image/png")}
        resp = client.post("/api/upload", files=files, headers={"X-Forwarded-For": "10.0.0.50"})
        assert resp.status_code == 200

    # 31st request receives 429
    files = {"file": ("test.png", image_bytes, "image/png")}
    resp = client.post("/api/upload", files=files, headers={"X-Forwarded-For": "10.0.0.50"})
    assert resp.status_code == 429
    assert "retry-after" in resp.headers

    upload_rate_limiter.reset()
