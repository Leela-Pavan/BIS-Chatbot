from pathlib import Path
from typing import Union

import yaml

from app.ingestion.models import SourceRegistry


def load_registry(path: Union[str, Path]) -> SourceRegistry:
    registry_path = Path(path)
    with registry_path.open("r", encoding="utf-8") as registry_file:
        payload = yaml.safe_load(registry_file) or {}
    return SourceRegistry.model_validate(payload)


def get_enabled_sources(registry: SourceRegistry):
    return [source for source in registry.sources if source.enabled]
