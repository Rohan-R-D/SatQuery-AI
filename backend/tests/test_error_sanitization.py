import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app, raise_server_exceptions=False)

def test_global_exception_handler_sanitizes_errors():
    # Inject a temporary test route that raises an unhandled exception with sensitive internal details
    @app.get("/api/test-unhandled-exception")
    async def trigger_exception():
        raise RuntimeError("Database connection string postgres://user:secretpassword@10.0.0.5:5432/db failed")

    response = client.get("/api/test-unhandled-exception")
    assert response.status_code == 500
    res_json = response.json()
    assert res_json == {"detail": "An internal server error occurred."}
    assert "secretpassword" not in response.text
    assert "RuntimeError" not in response.text
    assert "10.0.0.5" not in response.text
