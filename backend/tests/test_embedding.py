import pytest

from app.rag.embedding import EmbeddingUnavailable, embed_texts


from typing import List


class FakeEmbeddingProvider:
    dimensions = 3

    def embed(self, texts: List[str]) -> List[List[float]]:
        return [[float(index)] * self.dimensions for index, _ in enumerate(texts)]


def test_disabled_embedding_provider_fails_closed() -> None:
    with pytest.raises(EmbeddingUnavailable):
        embed_texts(None, ["synthetic text"], expected_dimensions=3)


def test_embedding_service_rejects_dimension_mismatch() -> None:
    with pytest.raises(ValueError, match="dimensions"):
        embed_texts(FakeEmbeddingProvider(), ["synthetic text"])


def test_embedding_service_validates_batch_shape() -> None:
    provider = FakeEmbeddingProvider()
    assert embed_texts(provider, ["a", "b"], expected_dimensions=3) == [[0.0] * 3, [1.0] * 3]
