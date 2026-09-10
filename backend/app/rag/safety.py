from typing import Iterable, List

from app.rag.schemas import Citation, EvidenceCandidate, SufficiencyDecision


def assess_sufficiency(
    candidates: Iterable[EvidenceCandidate], *, minimum_score: float = 0.55
) -> SufficiencyDecision:
    ranked = list(candidates)
    if not ranked:
        return SufficiencyDecision(
            state="insufficient", reasons=["no relevant official evidence was retrieved"]
        )
    usable = [candidate for candidate in ranked if candidate.fused_score >= minimum_score]
    if not usable:
        return SufficiencyDecision(
            state="insufficient",
            reasons=["retrieved evidence did not meet the relevance threshold"],
        )
    documents = {candidate.document_id for candidate in usable}
    if len(documents) > 1 and len({candidate.version for candidate in usable}) > 1:
        return SufficiencyDecision(
            state="conflicting",
            reasons=["retrieved evidence contains multiple document versions"],
        )
    return SufficiencyDecision(state="sufficient", reasons=[])


def validate_citations(
    citations: Iterable[Citation], evidence: Iterable[EvidenceCandidate]
) -> List[Citation]:
    evidence_by_id = {candidate.evidence_id: candidate for candidate in evidence}
    valid: List[Citation] = []
    for citation in citations:
        candidate = evidence_by_id.get(citation.evidence_id)
        if not candidate or citation.document_id != candidate.document_id:
            continue
        if citation.excerpt not in candidate.content:
            continue
        valid.append(citation)
    return valid
