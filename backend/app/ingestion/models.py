from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

ContentType = Literal["html", "pdf"]


class SourceConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_id: str = Field(min_length=1, pattern=r"^[a-z0-9][a-z0-9_-]*$")
    url: HttpUrl
    approved_domain: str = Field(min_length=1)
    content_type: ContentType
    purpose: str = Field(min_length=1)
    refresh_policy: str = Field(min_length=1)
    policy_notes: str = Field(min_length=1)
    enabled: bool = False

    @field_validator("approved_domain")
    @classmethod
    def normalize_domain(cls, value: str) -> str:
        return value.lower().strip().rstrip(".")

    @field_validator("url")
    @classmethod
    def require_https(cls, value: HttpUrl) -> HttpUrl:
        if value.scheme != "https":
            raise ValueError("approved sources must use HTTPS")
        return value


class SourceRegistry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sources: List[SourceConfig] = Field(default_factory=list)


class FetchResult(BaseModel):
    source_id: str
    url: HttpUrl
    final_url: HttpUrl
    status_code: int
    content_type: str
    content_length: int
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    retrieved_at: datetime
    body: bytes = Field(repr=False)


class IngestionEvent(BaseModel):
    source_id: str
    status: Literal["fetched", "skipped", "failed"]
    url: str
    message: str
    retrieved_at: datetime
    sha256: Optional[str] = None
