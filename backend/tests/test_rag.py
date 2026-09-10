from app.rag.demo import response_from_evidence
from app.rag.providers import ProviderConfigurationError, create_embedding_provider
from app.rag.query import understand_query
from app.rag.rag_service import answer_with_rag
from app.rag.rerank import rerank_candidates
from app.rag.retrieval import fuse_scores
from app.rag.safety import assess_sufficiency, validate_citations
from app.rag.schemas import Citation, EvidenceCandidate, QueryRequest


def evidence(evidence_id: str, keyword: float, semantic: float) -> EvidenceCandidate:
    return EvidenceCandidate(
        evidence_id=evidence_id,
        content="Clause 5 applies to the synthetic product.",
        document_id="demo-document",
        document_title="DEMO DATA - NOT OFFICIAL",
        standard_number="IS1234",
        clause_number="5",
        page_number=2,
        keyword_score=keyword,
        semantic_score=semantic,
    )


def test_query_understanding_preserves_standard_and_intent() -> None:
    result = understand_query("Which BIS standard applies to my product, IS 1234:2020?")

    assert result.intent == "product_mapping"
    assert result.standard_numbers == ["IS1234:2020"]
    assert result.language == "en"


def test_hybrid_fusion_and_sufficiency_are_deterministic() -> None:
    ranked = fuse_scores([evidence("a", 0.4, 0.9), evidence("b", 0.8, 0.3)])

    assert ranked[0].evidence_id == "a"
    assert assess_sufficiency(ranked).state == "sufficient"


def test_citation_validator_rejects_unbacked_excerpt() -> None:
    candidate = evidence("a", 0.8, 0.8)
    valid = Citation(evidence_id="a", document_id="demo-document", excerpt="Clause 5 applies")
    invalid = Citation(evidence_id="a", document_id="demo-document", excerpt="Unsupported claim")

    assert validate_citations([valid, invalid], [candidate]) == [valid]


def test_evidence_response_exposes_source_context() -> None:
    candidate = evidence("a", 0.8, 0.0)
    understanding = understand_query("Which standard applies to my product?")

    response = response_from_evidence([candidate], understanding)

    assert response.evidence_sufficient is True
    assert response.citations[0].clause_number == "5"
    assert response.citations[0].page_number == 2


def test_embedding_provider_is_disabled_by_default() -> None:
    assert create_embedding_provider("disabled") is None


def test_unknown_embedding_provider_fails_closed() -> None:
    try:
        create_embedding_provider("unknown")
    except ProviderConfigurationError as error:
        assert "unsupported embedding provider" in str(error)
    else:
        raise AssertionError("unknown providers must not be silently accepted")


def test_deterministic_reranker_preserves_evidence_identity() -> None:
    candidates = fuse_scores([evidence("a", 0.2, 0.2), evidence("b", 0.8, 0.8)])

    reranked = rerank_candidates("synthetic query", candidates)

    assert [candidate.evidence_id for candidate in reranked] == ["b", "a"]


def test_rag_service_returns_grounded_response_from_retrieved_evidence(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.rag.rag_service.search_keyword_evidence",
        lambda *_args: [evidence("grounded", 0.9, 0.0)],
    )

    response = answer_with_rag(
        QueryRequest(question="Which standard applies to my product?"),
        "postgresql://synthetic",
    )

    assert response.evidence_sufficient is True
    assert response.citations[0].evidence_id == "grounded"
