from typing import Optional

from app.rag.demo import response_from_evidence
from app.rag.embedding import embed_texts
from app.rag.postgres import search_hybrid_evidence, search_keyword_evidence
from app.rag.providers import EmbeddingProvider, RerankerProvider
from app.rag.query import understand_query
from app.rag.rerank import rerank_candidates
from app.rag.retrieval import fuse_scores
from app.rag.safety import assess_sufficiency
from app.rag.schemas import AssistantResponse, QueryRequest, RetrievalFilters


def answer_with_rag(
    request: QueryRequest,
    database_url: str,
    *,
    embedding_provider: Optional[EmbeddingProvider] = None,
    reranker_provider: Optional[RerankerProvider] = None,
) -> AssistantResponse:
    understanding = understand_query(request.question, request.language)
    filters = RetrievalFilters(
        standard_number=understanding.standard_numbers[0]
        if understanding.standard_numbers
        else None
    )

    if embedding_provider is None:
        candidates = search_keyword_evidence(request.question, filters, database_url)
    else:
        query_vector = embed_texts(embedding_provider, [request.question])[0]
        candidates = search_hybrid_evidence(
            request.question,
            query_vector,
            filters,
            database_url,
        )

    fused = fuse_scores(
        candidates,
        keyword_weight=1.0 if embedding_provider is None else 0.5,
        semantic_weight=0.0 if embedding_provider is None else 0.5,
    )
    ranked = rerank_candidates(request.question, fused, reranker_provider)
    decision = assess_sufficiency(ranked)
    if decision.state != "sufficient":
        return AssistantResponse(
            answer=(
                "I could not verify this request from the available official BIS evidence. "
                "Please provide more product details or consult the referenced BIS authority."
            ),
            confidence="low",
            evidence_sufficient=False,
            unknowns=understanding.unknowns,
            warnings=decision.reasons,
        )
    return response_from_evidence(ranked, understanding)
