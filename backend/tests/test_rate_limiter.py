import io
import pytest
from PIL import Image
from fastapi.testclient import TestClient
from main import app
from utils.rate_limiter import analyze_rate_limiter, upload_rate_limiter

client = TestClient(app)

def create_dummy_image_bytes():
    buf = io.BytesIO()
    img = Image.new("RGB", (64, 64), color="red")
    img.save(buf, format="PNG")
    return buf.getvalue()

def test_rate_limiter_blocks_burst_on_analyze():
    analyze_rate_limiter.reset()
    image_bytes = create_dummy_image_bytes()

    # The limit is 10 requests per minute
    # We send 10 requests which should pass rate limiting
    # (they may return 200 or whatever status, but NOT 429)
    for i in range(10):
        files = {"image": ("test.png", image_bytes, "image/png")}
        data = {"input_type": "single", "query": f"Test query {i}"}
        response = client.post("/api/analyze", files=files, data=data, headers={"X-Forwarded-For": "192.168.1.100"})
        assert response.status_code != 429

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
    assert response_other_ip.status_code != 429

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
