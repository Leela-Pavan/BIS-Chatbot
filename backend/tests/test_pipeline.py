import asyncio

import httpx

from app.ingestion.fetcher import ControlledFetcher
from app.ingestion.models import SourceConfig
from app.ingestion.pipeline import run_ingestion


def source(source_id: str, url: str) -> SourceConfig:
    return SourceConfig(
        source_id=source_id,
        url=url,
        approved_domain="example.test",
        content_type="html",
        purpose="synthetic test fixture only",
        refresh_policy="test-only",
        policy_notes="DEMO DATA - NOT OFFICIAL",
        enabled=True,
    )


def test_ingestion_report_extracts_and_deduplicates() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            200,
            headers={"content-type": "text/html"},
            content=b"<p>1 Scope</p><p>DEMO DATA - NOT OFFICIAL</p>",
        )
    )
    fetcher = ControlledFetcher(user_agent="test-agent", transport=transport)
    sources = [source("one", "https://example.test/one"), source("two", "https://example.test/two")]

    report = asyncio.run(run_ingestion(sources, fetcher))

    assert report.fetched_count == 1
    assert report.skipped_count == 1
    assert report.failed_count == 0
    assert report.items[0].extracted is not None
    assert report.items[1].event.message == "content hash already exists"
