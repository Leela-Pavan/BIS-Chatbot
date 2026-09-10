import math
from typing import List, Optional, Sequence

from app.rag.providers import EmbeddingProvider


class EmbeddingUnavailable(RuntimeError):
    pass


def embed_texts(
    provider: Optional[EmbeddingProvider],
    texts: Sequence[str],
    *,
    expected_dimensions: int = 1024,
) -> List[List[float]]:
    if provider is None:
        raise EmbeddingUnavailable("embedding provider is disabled")
    if not texts:
        return []
    if provider.dimensions != expected_dimensions:
        raise ValueError("embedding provider dimensions do not match the knowledge schema")

    vectors = provider.embed(texts)
    if len(vectors) != len(texts):
        raise ValueError("embedding provider returned an unexpected vector count")
    for vector in vectors:
        if len(vector) != expected_dimensions or not all(math.isfinite(value) for value in vector):
            raise ValueError("embedding provider returned an invalid vector")
    return vectors
