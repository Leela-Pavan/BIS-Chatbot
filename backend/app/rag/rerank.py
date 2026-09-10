from typing import List, Optional, Sequence

from app.rag.providers import ProviderConfigurationError, RerankerProvider
from app.rag.schemas import EvidenceCandidate


def rerank_candidates(
    query: str,
    candidates: Sequence[EvidenceCandidate],
    provider: Optional[RerankerProvider] = None,
) -> List[EvidenceCandidate]:
    if provider is None:
        return sorted(
            candidates,
            key=lambda candidate: (
                candidate.fused_score,
                candidate.clause_number is not None,
                candidate.page_number is not None,
            ),
            reverse=True,
        )

    reranked = provider.rerank(query, candidates)
    expected_ids = {candidate.evidence_id for candidate in candidates}
    actual_ids = [candidate.evidence_id for candidate in reranked]
    if len(actual_ids) != len(expected_ids) or set(actual_ids) != expected_ids:
        raise ProviderConfigurationError(
            "reranker must return exactly the retrieved evidence candidates"
        )
    return list(reranked)
