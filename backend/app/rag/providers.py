from typing import List, Optional, Protocol, Sequence

from app.rag.schemas import EvidenceCandidate


class ProviderConfigurationError(ValueError):
    pass


class EmbeddingProvider(Protocol):
    model_name: str
    dimensions: int

    def embed(self, texts: Sequence[str]) -> List[List[float]]:
        """Return one vector per input without changing document metadata."""


class RerankerProvider(Protocol):
    model_name: str

    def rerank(
        self, query: str, candidates: Sequence[EvidenceCandidate]
    ) -> List[EvidenceCandidate]:
        """Return candidates ordered by provider relevance without inventing evidence."""


class GenerationProvider(Protocol):
    model_name: str

    def answer(self, question: str, evidence: Sequence[EvidenceCandidate]) -> str:
        """Generate only from supplied evidence; provider policy is enforced by the caller."""


class SentenceTransformerEmbeddingProvider:
    """Optional local provider for a configured multilingual sentence-transformer model."""

    def __init__(self, model_name: str = "BAAI/bge-m3", dimensions: int = 1024) -> None:
        self.model_name = model_name
        self.dimensions = dimensions
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as error:
            raise ProviderConfigurationError(
                "install the optional 'ml' dependencies before enabling local embeddings"
            ) from error
        self._model = SentenceTransformer(model_name)

    def embed(self, texts: Sequence[str]) -> List[List[float]]:
        vectors = self._model.encode(
            list(texts), normalize_embeddings=True, convert_to_numpy=True
        )
        result = vectors.tolist()
        if any(len(vector) != self.dimensions for vector in result):
            raise ProviderConfigurationError(
                "embedding model returned vectors outside the configured "
                f"{self.dimensions} dimensions"
            )
        return result


def create_embedding_provider(
    provider_name: str, model_name: str = "BAAI/bge-m3", dimensions: int = 1024
) -> Optional[EmbeddingProvider]:
    if provider_name == "disabled":
        return None
    if provider_name == "sentence_transformers":
        return SentenceTransformerEmbeddingProvider(model_name, dimensions)
    raise ProviderConfigurationError(f"unsupported embedding provider: {provider_name}")
