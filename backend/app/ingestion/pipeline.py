from collections.abc import Iterable
from datetime import datetime, timezone
from typing import List, Optional, Set

from app.ingestion.fetcher import ControlledFetcher, FetchError
from app.ingestion.models import FetchResult, IngestionEvent, SourceConfig
from app.knowledge.extractors import extract_html, extract_pdf
from app.knowledge.models import ExtractedDocument


class IngestionItem:
    def __init__(
        self,
        source: SourceConfig,
        event: IngestionEvent,
        fetch_result: Optional[FetchResult] = None,
        extracted: Optional[ExtractedDocument] = None,
    ) -> None:
        self.source = source
        self.event = event
        self.fetch_result = fetch_result
        self.extracted = extracted


class IngestionReport:
    def __init__(self, items: List[IngestionItem], started_at: datetime) -> None:
        self.items = items
        self.started_at = started_at
        self.completed_at = datetime.now(timezone.utc)

    @property
    def fetched_count(self) -> int:
        return sum(item.event.status == "fetched" for item in self.items)

    @property
    def skipped_count(self) -> int:
        return sum(item.event.status == "skipped" for item in self.items)

    @property
    def failed_count(self) -> int:
        return sum(item.event.status == "failed" for item in self.items)


async def run_ingestion(
    sources: Iterable[SourceConfig],
    fetcher: ControlledFetcher,
    *,
    known_hashes: Optional[Set[str]] = None,
) -> IngestionReport:
    started_at = datetime.now(timezone.utc)
    seen_hashes = known_hashes if known_hashes is not None else set()
    items: List[IngestionItem] = []
    for source in sources:
        try:
            result = await fetcher.fetch(source)
            if result.sha256 in seen_hashes:
                event = IngestionEvent(
                    source_id=source.source_id,
                    status="skipped",
                    url=str(result.final_url),
                    message="content hash already exists",
                    retrieved_at=result.retrieved_at,
                    sha256=result.sha256,
                )
                items.append(IngestionItem(source, event, result))
                continue
            extracted = (
                extract_html(result.body)
                if source.content_type == "html"
                else extract_pdf(result.body)
            )
            seen_hashes.add(result.sha256)
            event = IngestionEvent(
                source_id=source.source_id,
                status="fetched",
                url=str(result.final_url),
                message="fetched and extracted",
                retrieved_at=result.retrieved_at,
                sha256=result.sha256,
            )
            items.append(IngestionItem(source, event, result, extracted))
        except (FetchError, RuntimeError, ValueError) as error:
            event = IngestionEvent(
                source_id=source.source_id,
                status="failed",
                url=str(source.url),
                message=str(error),
                retrieved_at=datetime.now(timezone.utc),
            )
            items.append(IngestionItem(source, event))
    return IngestionReport(items, started_at)
