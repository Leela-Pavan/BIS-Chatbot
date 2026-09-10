from typing import Iterable, List

from app.rag.schemas import EvidenceCandidate, RetrievalFilters


def fuse_scores(
    candidates: Iterable[EvidenceCandidate],
    *,
    keyword_weight: float = 0.5,
    semantic_weight: float = 0.5,
) -> List[EvidenceCandidate]:
    if keyword_weight < 0 or semantic_weight < 0 or keyword_weight + semantic_weight == 0:
        raise ValueError("retrieval weights must be non-negative and not both zero")
    total = keyword_weight + semantic_weight
    ranked = [
        candidate.model_copy(
            update={
                "fused_score": (
                    candidate.keyword_score * keyword_weight
                    + candidate.semantic_score * semantic_weight
                )
                / total
            }
        )
        for candidate in candidates
    ]
    return sorted(ranked, key=lambda candidate: candidate.fused_score, reverse=True)


def apply_filters(
    candidates: Iterable[EvidenceCandidate],
    filters: RetrievalFilters,
) -> List[EvidenceCandidate]:
    return [
        candidate
        for candidate in candidates
        if (not filters.standard_number or candidate.standard_number == filters.standard_number)
        and (not filters.document_version or candidate.version == filters.document_version)
    ]
