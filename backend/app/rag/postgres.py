from typing import Any, Dict, List

from app.database import psycopg_url
from app.rag.schemas import EvidenceCandidate, RetrievalFilters


class DatabaseUnavailable(RuntimeError):
    pass


SEARCH_SQL = """
SELECT
    c.id::text AS evidence_id,
    c.content,
    d.id::text AS document_id,
    d.title AS document_title,
    s.standard_number,
    c.clause_number,
    c.page_number,
    d.version,
    d.source_url,
    LEAST(ts_rank_cd(c.search_vector, plainto_tsquery('simple', %(question)s)), 1.0)
        AS keyword_score
FROM chunks AS c
JOIN documents AS d ON d.id = c.document_id
LEFT JOIN standards AS s ON s.source_document_id = d.id
WHERE d.status = 'active'
  AND c.search_vector @@ plainto_tsquery('simple', %(question)s)
    AND (
            %(standard_number)s IS NULL
            OR REPLACE(s.standard_number, ' ', '') = REPLACE(%(standard_number)s, ' ', '')
    )
  AND (%(document_version)s IS NULL OR d.version = %(document_version)s)
ORDER BY keyword_score DESC, d.retrieved_at DESC
LIMIT %(limit)s
"""

HYBRID_SEARCH_SQL = """
SELECT
    c.id::text AS evidence_id,
    c.content,
    d.id::text AS document_id,
    d.title AS document_title,
    s.standard_number,
    c.clause_number,
    c.page_number,
    d.version,
    d.source_url,
    LEAST(ts_rank_cd(c.search_vector, plainto_tsquery('simple', %(question)s)), 1.0)
        AS keyword_score,
    GREATEST(0.0, LEAST(1.0, 1.0 - (c.embedding <=> %(query_embedding)s::vector)))
        AS semantic_score
FROM chunks AS c
JOIN documents AS d ON d.id = c.document_id
LEFT JOIN standards AS s ON s.source_document_id = d.id
WHERE d.status = 'active'
  AND (c.search_vector @@ plainto_tsquery('simple', %(question)s) OR c.embedding IS NOT NULL)
  AND (
      %(standard_number)s IS NULL
      OR REPLACE(s.standard_number, ' ', '') = REPLACE(%(standard_number)s, ' ', '')
  )
  AND (%(document_version)s IS NULL OR d.version = %(document_version)s)
ORDER BY (keyword_score * %(keyword_weight)s + semantic_score * %(semantic_weight)s) DESC,
         d.retrieved_at DESC
LIMIT %(limit)s
"""


def search_keyword_evidence(
    question: str,
    filters: RetrievalFilters,
    database_url: str,
    *,
    limit: int = 20,
) -> List[EvidenceCandidate]:
    try:
        import psycopg
        from psycopg.rows import dict_row
    except ImportError as error:
        raise DatabaseUnavailable("the PostgreSQL driver is unavailable") from error

    try:
        with psycopg.connect(
            psycopg_url(database_url), row_factory=dict_row, connect_timeout=3
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    SEARCH_SQL,
                    {
                        "question": question,
                        "standard_number": filters.standard_number,
                        "document_version": filters.document_version,
                        "limit": limit,
                    },
                )
                rows = cursor.fetchall()
    except (OSError, psycopg.Error) as error:
        raise DatabaseUnavailable("the knowledge database is unavailable") from error

    return _rows_to_candidates(rows)


def search_hybrid_evidence(
    question: str,
    query_embedding: List[float],
    filters: RetrievalFilters,
    database_url: str,
    *,
    keyword_weight: float = 0.5,
    semantic_weight: float = 0.5,
    limit: int = 20,
) -> List[EvidenceCandidate]:
    if len(query_embedding) != 1024:
        raise ValueError("query embedding must match the configured VECTOR(1024) dimension")
    if keyword_weight < 0 or semantic_weight < 0 or keyword_weight + semantic_weight == 0:
        raise ValueError("retrieval weights must be non-negative and not both zero")

    try:
        import psycopg
        from psycopg.rows import dict_row
    except ImportError as error:
        raise DatabaseUnavailable("the PostgreSQL driver is unavailable") from error

    try:
        with psycopg.connect(
            psycopg_url(database_url), row_factory=dict_row, connect_timeout=3
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    HYBRID_SEARCH_SQL,
                    {
                        "question": question,
                        "query_embedding": "[" + ",".join(map(str, query_embedding)) + "]",
                        "standard_number": filters.standard_number,
                        "document_version": filters.document_version,
                        "keyword_weight": keyword_weight,
                        "semantic_weight": semantic_weight,
                        "limit": limit,
                    },
                )
                rows = cursor.fetchall()
    except (OSError, psycopg.Error) as error:
        raise DatabaseUnavailable("the knowledge database is unavailable") from error

    return _rows_to_candidates(rows)


def _rows_to_candidates(rows: List[Dict[str, Any]]) -> List[EvidenceCandidate]:
    return [
        EvidenceCandidate(
            evidence_id=row["evidence_id"],
            content=row["content"],
            document_id=row["document_id"],
            document_title=row["document_title"],
            standard_number=row["standard_number"],
            clause_number=row["clause_number"],
            page_number=row["page_number"],
            version=row["version"],
            source_url=row["source_url"],
            keyword_score=float(row["keyword_score"] or 0.0),
            semantic_score=float(row.get("semantic_score") or 0.0),
        )
        for row in rows
    ]
