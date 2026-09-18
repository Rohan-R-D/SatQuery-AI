import io
import pytest
from PIL import Image
from fastapi.testclient import TestClient
from main import app
from utils.rate_limiter import analyze_rate_limiter

client = TestClient(app)


def create_synthetic_image(width=120, height=120, color=(100, 150, 200)):
    buf = io.BytesIO()
    img = Image.new("RGB", (width, height), color=color)
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_bitemporal_two_lane_analysis():
    analyze_rate_limiter.reset()
    t1_bytes = create_synthetic_image(150, 150, (50, 100, 150))
    t2_bytes = create_synthetic_image(150, 150, (60, 110, 160))

    files = {
        "image": ("before.png", t1_bytes, "image/png"),
        "second_image": ("after.png", t2_bytes, "image/png")
    }
    data = {
        "input_type": "bi_temporal",
        "query": "What changed between these two satellite observations?"
    }

    response = client.post("/api/analyze", files=files, data=data)
    assert response.status_code == 200
    res_json = response.json()

    assert res_json["success"] is True
    assert res_json["task"] == "change_vqa"
    assert res_json["confidence"] >= 15.0
    assert len(res_json["execution_trace"]) == 8
    assert len(res_json["evidence"]) >= 1
    assert "artifacts" in res_json
    assert res_json["processing_time"] > 0


def test_optical_sar_two_lane_analysis():
    analyze_rate_limiter.reset()
    opt_bytes = create_synthetic_image(120, 120, (120, 180, 80))
    sar_bytes = create_synthetic_image(120, 120, (80, 80, 80))

    files = {
        "image": ("optical.png", opt_bytes, "image/png"),
        "second_image": ("sar.png", sar_bytes, "image/png")
    }
    data = {
        "input_type": "optical_sar",
        "query": "Use optical and SAR channels to identify urban built-up and water bodies."
    }

    response = client.post("/api/analyze", files=files, data=data)
    assert response.status_code == 200
    res_json = response.json()

    assert res_json["success"] is True
    assert res_json["task"] == "optical_sar_fusion"
    assert "Refined Lee" in res_json["model_used"] or "SAR" in res_json["model_used"]
    assert len(res_json["execution_trace"]) == 8
