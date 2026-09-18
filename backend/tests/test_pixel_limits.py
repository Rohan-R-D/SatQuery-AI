import io
import pytest
from PIL import Image
from fastapi.testclient import TestClient
from main import app
from scientific.raster_loader import load_raster

client = TestClient(app)

def create_image_bytes(width: int, height: int, color=(100, 100, 100), fmt="PNG") -> bytes:
    buf = io.BytesIO()
    img = Image.new("RGB", (width, height), color=color)
    img.save(buf, format=fmt)
    return buf.getvalue()

def create_synthetic_oversized_png_header(width: int = 10000, height: int = 10000) -> bytes:
    """Create a minimal PNG header with large dimensions that exceed 50 MP (e.g. 10000x10000 = 100 MP)."""
    # 8000 x 8000 = 64,000,000 pixels (> 50,000,000)
    img = Image.new("1", (width, height))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def test_valid_image_upload_within_limits():
    data = create_image_bytes(200, 200)
    files = {"file": ("test.png", data, "image/png")}
    response = client.post("/api/upload", files=files)
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["success"] is True
    assert res_json["dimensions"] == [200, 200]

def test_oversized_image_upload_rejected_413():
    # 8000x8000 = 64 MP > 50 MP limit
    oversized_data = create_synthetic_oversized_png_header(8000, 8000)
    files = {"file": ("oversized.png", oversized_data, "image/png")}
    response = client.post("/api/upload", files=files)
    assert response.status_code == 413
    assert "exceed maximum allowed limit" in response.json()["detail"]

def test_oversized_image_analyze_rejected_413():
    oversized_data = create_synthetic_oversized_png_header(8000, 8000)
    files = {"image": ("oversized.png", oversized_data, "image/png")}
    form_data = {"input_type": "single", "query": "Describe this image"}
    response = client.post("/api/analyze", files=files, data=form_data)
    assert response.status_code == 413
    assert "exceed maximum allowed limit" in response.json()["detail"]

def test_raster_loader_rejects_oversized():
    oversized_data = create_synthetic_oversized_png_header(8000, 8000)
    with pytest.raises(ValueError, match="exceeds sample limit"):
        load_raster(oversized_data, max_pixels=50_000_000)
