from typing import Iterable

from app.rag.schemas import AssistantResponse, Citation, EvidenceCandidate, QueryUnderstanding


def response_from_evidence(
    evidence: Iterable[EvidenceCandidate], understanding: QueryUnderstanding
) -> AssistantResponse:
    candidates = list(evidence)
    if not candidates:
        return AssistantResponse(
            answer="I could not verify this request from the current official BIS knowledge base.",
            confidence="low",
            evidence_sufficient=False,
            unknowns=understanding.unknowns,
            warnings=[
                "No official evidence was retrieved; this response does not make a BIS claim."
            ],
        )

    citations = [
        Citation(
            evidence_id=candidate.evidence_id,
            document_id=candidate.document_id,
            document_title=candidate.document_title,
            standard_number=candidate.standard_number,
            clause_number=candidate.clause_number,
            page_number=candidate.page_number,
            excerpt=candidate.content,
            version=candidate.version,
            source_url=candidate.source_url,
        )
        for candidate in candidates
    ]
    standards = sorted(
        {candidate.standard_number for candidate in candidates if candidate.standard_number}
    )
    documents = sorted({candidate.document_id for candidate in candidates})
    return AssistantResponse(
        answer=(
            "The current official BIS knowledge base returned evidence for this query. "
            "Review the cited clauses and pages before acting."
        ),
        confidence="medium",
        evidence_sufficient=True,
        citations=citations,
        related_standards=standards,
        unknowns=understanding.unknowns,
        source_documents=documents,
    )
