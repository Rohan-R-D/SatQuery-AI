import re
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

REPORT_FILENAME_REGEX = re.compile(r"^satquery_report_[a-f0-9]{8}_\d{8}\.md$")

def test_report_filename_format_and_security():
    payload = {
        "query": "Detect flood extent in eastern sector\r\nSet-Cookie: admin=true\r\n\r\nMalicious",
        "input_type": "single",
        "task": "single_image_vqa\r\nInjected-Header: 1",
        "answer": "Water observed across agricultural fields.",
        "confidence": 92.5,
        "confidence_explanation": "Clear spectral contrast.",
        "model_used": "Gemini Multimodal VLM",
        "evidence": [
            {
                "id": "ev-1",
                "title": "Water Absorption\r\nBad-Header: true",
                "description": "NIR low reflectance.",
                "type": "metrics"
            }
        ],
        "execution_trace": [
            {
                "id": 1,
                "title": "Query Understanding",
                "description": "Parsed intent.",
                "status": "COMPLETED"
            }
        ],
        "processing_time": 0.55
    }

    response = client.post("/api/report", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/markdown")

    content_disp = response.headers.get("content-disposition", "")
    assert "attachment; filename=\"" in content_disp
    
    # Extract filename from header
    match = re.search(r'filename="([^"]+)"', content_disp)
    assert match is not None
    filename = match.group(1)
    
    # Assert strict regex match ^satquery_report_[a-f0-9]{8}_\d{8}\.md$
    assert REPORT_FILENAME_REGEX.match(filename) is not None

    # Assert no CRLF or injected headers in response headers
    for header_key, header_val in response.headers.items():
        assert "\r" not in header_key
        assert "\n" not in header_key
        assert "\r" not in header_val
        assert "\n" not in header_val

    # Assert report body contains cleaned text
    assert "SATQUERY AI - ANALYSIS REPORT" in response.text
    assert "Detect flood extent in eastern sector" in response.text
