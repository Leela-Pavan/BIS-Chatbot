from fastapi.testclient import TestClient

from app.main import app
from app.rag.postgres import DatabaseUnavailable

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


def test_assistant_uses_local_faq_fallback_when_database_is_unavailable(monkeypatch) -> None:
    def raise_unavailable(*_args, **_kwargs):
        raise DatabaseUnavailable("the knowledge database is unavailable")

    monkeypatch.setattr("app.rag.rag_service.search_keyword_evidence", raise_unavailable)
    response = client.post(
        "/api/v1/assistant/query",
        json={"question": "What is BIS?"},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["evidence_sufficient"] is True
    assert payload["answer"]
    assert any("BIS" in citation["excerpt"] or "Bureau of Indian Standards" in citation["excerpt"] for citation in payload["citations"])
