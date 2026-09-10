from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, base_url="http://localhost")


def test_assistant_refuses_without_evidence(monkeypatch) -> None:
    monkeypatch.setattr("app.rag.rag_service.search_keyword_evidence", lambda *_args: [])
    response = client.post(
        "/api/v1/assistant/query",
        json={"question": "Which standard applies to my product?"},
    )

    assert response.status_code in (200, 503)
    if response.status_code == 503:
        return
    payload = response.json()
    assert payload["evidence_sufficient"] is False
    assert payload["citations"] == []
    assert "could not verify" in payload["answer"]
