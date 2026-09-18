import pytest
from fastapi.testclient import TestClient
from main import app
from config import settings

client = TestClient(app)


def test_audit_auth_protection(monkeypatch):
    test_key = "isro-sac-secret-key-2026"
    monkeypatch.setattr(settings, "ADMIN_API_KEY", test_key)

    # 1. Access without credentials -> 401
    resp_no_auth = client.get("/api/audit")
    assert resp_no_auth.status_code == 401
    assert "Invalid or missing API key" in resp_no_auth.json()["detail"]

    # 2. Access with invalid key -> 401
    resp_bad_key = client.get("/api/audit", headers={"X-API-Key": "wrong-key"})
    assert resp_bad_key.status_code == 401

    # 3. Access with valid X-API-Key -> 200
    resp_valid_header = client.get("/api/audit", headers={"X-API-Key": test_key})
    assert resp_valid_header.status_code == 200
    assert "metrics" in resp_valid_header.json()

    # 4. Access with valid Bearer token -> 200
    resp_valid_bearer = client.get("/api/audit", headers={"Authorization": f"Bearer {test_key}"})
    assert resp_valid_bearer.status_code == 200

    # 5. Access execution detail endpoint with valid Bearer token -> 404 (not 401)
    resp_exec_bearer = client.get("/api/executions/non-existent-id", headers={"Authorization": f"Bearer {test_key}"})
    assert resp_exec_bearer.status_code == 404
