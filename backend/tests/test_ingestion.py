import asyncio
from pathlib import Path

import httpx
import pytest

from app.ingestion.fetcher import ControlledFetcher, FetchError
from app.ingestion.models import SourceConfig
from app.ingestion.registry import load_registry


@pytest.fixture
def html_source() -> SourceConfig:
    return SourceConfig(
        source_id="demo-html",
        url="https://example.test/resource",
        approved_domain="example.test",
        content_type="html",
        purpose="synthetic test fixture only",
        refresh_policy="test-only",
        policy_notes="DEMO DATA - NOT OFFICIAL",
        enabled=True,
    )


def test_fetcher_preserves_content_and_hash(html_source: SourceConfig) -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            200,
            headers={"content-type": "text/html; charset=utf-8"},
            content=b"<html>demo</html>",
        )
    )
    fetcher = ControlledFetcher(user_agent="test-agent", transport=transport)
    result = asyncio.run(fetcher.fetch(html_source))

    assert result.status_code == 200
    assert result.content_type == "text/html"
    assert result.sha256 == "79e4491c26eaa628dec4daf289e891595fe3c3985650284554bc568ead4d96c7"
    assert result.body == b"<html>demo</html>"


def test_fetcher_rejects_unapproved_redirect(html_source: SourceConfig) -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(302, headers={"location": "https://unsafe.test/file"})
    )

    with pytest.raises(FetchError, match="unsafe redirect"):
        fetcher = ControlledFetcher(user_agent="test-agent", transport=transport)
        asyncio.run(fetcher.fetch(html_source))


def test_empty_registry_is_explicit() -> None:
    registry_path = Path(__file__).parents[2] / "data_sources" / "sources.yaml"
    registry = load_registry(registry_path)

    assert registry.sources == []
