from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, base_url="http://localhost")


def test_health_endpoint() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "bis-sahayak-api"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"


def test_oversized_request_is_rejected() -> None:
    response = client.get("/api/v1/health", headers={"content-length": "64001"})

    assert response.status_code == 413


def test_ready_endpoint_reports_database_unavailable(monkeypatch) -> None:
    monkeypatch.setattr("app.main.database_is_ready", lambda _database_url: False)

    response = client.get("/api/v1/ready")

    assert response.status_code == 503
