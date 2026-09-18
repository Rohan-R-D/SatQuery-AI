import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_cors_allowed_origin():
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET"
        }
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"
    assert response.headers.get("access-control-allow-credentials") == "true"

def test_cors_disallowed_origin():
    response = client.options(
        "/health",
        headers={
            "Origin": "https://malicious.com",
            "Access-Control-Request-Method": "GET"
        }
    )
    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers
