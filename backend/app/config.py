from functools import lru_cache
from typing import List, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _parse_list_value(value: Union[str, List[str], None]) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return [str(item).strip() for item in value if str(item).strip()]


class Settings(BaseSettings):
    environment: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    max_request_bytes: int = 64_000
    cors_origins: Union[str, List[str]] = "http://localhost:3000"
    allowed_hosts: Union[str, List[str]] = "localhost,127.0.0.1"
    database_url: str = "postgresql+psycopg://bis_sahayak:bis_sahayak@localhost:5432/bis_sahayak"
    embedding_provider: str = "disabled"
    embedding_model: str = "BAAI/bge-m3"
    embedding_dimensions: int = 1024
    generation_provider: str = "disabled"
    reranker_provider: str = "disabled"
    ingestion_user_agent: str = "BIS-Sahayak/0.1"
    approved_source_registry: str = "data_sources/sources.yaml"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origins_list(self) -> List[str]:
        return _parse_list_value(self.cors_origins)

    @property
    def allowed_hosts_list(self) -> List[str]:
        return _parse_list_value(self.allowed_hosts)

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Union[str, List[str]]) -> Union[str, List[str]]:
        return value

    @field_validator("allowed_hosts", mode="before")
    @classmethod
    def parse_allowed_hosts(cls, value: Union[str, List[str]]) -> Union[str, List[str]]:
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
