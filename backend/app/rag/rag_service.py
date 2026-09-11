import json
import re
from pathlib import Path
from typing import List, Optional

from app.rag.demo import response_from_evidence
from app.rag.embedding import embed_texts
from app.rag.postgres import DatabaseUnavailable, search_hybrid_evidence, search_keyword_evidence
from app.rag.providers import EmbeddingProvider, RerankerProvider
from app.rag.query import understand_query
from app.rag.rerank import rerank_candidates
from app.rag.retrieval import fuse_scores
from app.rag.safety import assess_sufficiency
from app.rag.schemas import AssistantResponse, EvidenceCandidate, QueryRequest, RetrievalFilters

FAQ_DATA_PATH = Path(__file__).resolve().parents[3] / "data_sources" / "basic_bis_faqs.jsonl"


def _fallback_faq_candidates(question: str, language: Optional[str]) -> List[EvidenceCandidate]:
    if not FAQ_DATA_PATH.exists():
        raise DatabaseUnavailable("the knowledge database is unavailable")

    records = []
    with FAQ_DATA_PATH.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if not text:
                continue
            try:
                records.append(json.loads(text))
            except json.JSONDecodeError:
                continue

    if not records:
        raise DatabaseUnavailable("the knowledge database is unavailable")

    question_tokens = {
        token.lower()
        for token in re.findall(r"[A-Za-z0-9\u0900-\u097F\u0C00-\u0C7F]+", question)
        if len(token) > 2
    }
    scored = []
    for index, record in enumerate(records):
        record_question = str(record.get("question", ""))
        record_answer = str(record.get("answer", ""))
        record_language = str(record.get("language", "en"))
        text = f"{record_question} {record_answer}".lower()

        score = 0.0
        if language and record_language == language:
            score += 0.25
        elif language is None and record_language == "en":
            score += 0.10

        overlap = len(question_tokens & {token.lower() for token in re.findall(r"[A-Za-z0-9\u0900-\u097F\u0C00-\u0C7F]+", record_question) if len(token) > 2})
        if overlap:
            score += min(0.55, overlap * 0.18)
        if any(token.lower() in text for token in question_tokens):
            score += 0.2
        if "bis" in text:
            score += 0.1

        if score > 0.0:
            scored.append((score, index, record))

    if not scored:
        raise DatabaseUnavailable("the knowledge database is unavailable")

    scored.sort(key=lambda item: item[0], reverse=True)
    candidates = []
    for score, index, record in scored[:5]:
        content = f"Q: {record.get('question', '')}\nA: {record.get('answer', '')}"
        candidates.append(
            EvidenceCandidate(
                evidence_id=f"faq-{index}",
                content=content,
                document_id="bis-demo-faq",
                document_title=record.get("source_title", "BIS Basic FAQ Knowledge Base"),
                standard_number=None,
                clause_number=f"faq-{index}",
                page_number=1,
                version="demo-v1",
                source_url=str(record.get("source_url", "https://www.bis.gov.in/")),
                keyword_score=min(score, 1.0),
                semantic_score=0.0,
                fused_score=min(score, 1.0),
            )
        )
    return candidates


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

    try:
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
    except DatabaseUnavailable:
        candidates = _fallback_faq_candidates(request.question, understanding.language)

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
