import hashlib
from datetime import datetime, timezone
from email.message import Message
from typing import Awaitable, Callable, Optional

import httpx

from app.ingestion.models import FetchResult, SourceConfig
from app.ingestion.security import UnsafeUrlError, validate_redirect, validate_source_url


class FetchError(RuntimeError):
    pass


RobotsChecker = Callable[[str, str], Awaitable[bool]]


async def allow_all_robots(_url: str, _user_agent: str) -> bool:
    return True


class ControlledFetcher:
    def __init__(
        self,
        *,
        user_agent: str,
        max_bytes: int = 10 * 1024 * 1024,
        timeout_seconds: float = 20.0,
        max_redirects: int = 3,
        robots_checker: RobotsChecker = allow_all_robots,
        transport: Optional[httpx.AsyncBaseTransport] = None,
    ) -> None:
        self.user_agent = user_agent
        self.max_bytes = max_bytes
        self.timeout = httpx.Timeout(timeout_seconds)
        self.max_redirects = max_redirects
        self.robots_checker = robots_checker
        self.transport = transport

    async def fetch(self, source: SourceConfig) -> FetchResult:
        url = str(source.url)
        try:
            validate_source_url(url, source.approved_domain)
        except UnsafeUrlError as error:
            raise FetchError(str(error)) from error
        if not source.enabled:
            raise FetchError("source is disabled")
        if not await self.robots_checker(url, self.user_agent):
            raise FetchError("robots.txt disallows this source")

        headers = {"User-Agent": self.user_agent, "Accept": "text/html, application/pdf"}
        async with httpx.AsyncClient(
            follow_redirects=False,
            timeout=self.timeout,
            headers=headers,
            transport=self.transport,
        ) as client:
            for _ in range(self.max_redirects + 1):
                response = await client.get(url)
                if response.is_redirect:
                    location = response.headers.get("location")
                    if not location:
                        raise FetchError("redirect response has no location")
                    try:
                        url = validate_redirect(url, location, source.approved_domain)
                    except UnsafeUrlError as error:
                        raise FetchError(f"unsafe redirect: {error}") from error
                    continue
                break
            else:
                raise FetchError("redirect limit exceeded")

        if response.status_code >= 400:
            raise FetchError(f"source returned HTTP {response.status_code}")
        if len(response.content) > self.max_bytes:
            raise FetchError("response exceeds configured size limit")
        content_type = Message()
        content_type["content-type"] = response.headers.get("content-type", "")
        media_type = content_type.get_content_type()
        allowed_types = {
            "html": {"text/html", "application/xhtml+xml"},
            "pdf": {"application/pdf"},
        }
        if media_type not in allowed_types[source.content_type]:
            raise FetchError(f"unexpected content type: {media_type or 'unknown'}")

        body = response.content
        return FetchResult(
            source_id=source.source_id,
            url=source.url,
            final_url=url,
            status_code=response.status_code,
            content_type=media_type,
            content_length=len(body),
            sha256=hashlib.sha256(body).hexdigest(),
            retrieved_at=datetime.now(timezone.utc),
            body=body,
        )
