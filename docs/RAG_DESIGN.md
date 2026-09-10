# BIS Sahayak RAG Design

## Grounding Contract

The language model is an explanation component, not the source of truth. It receives retrieved evidence with stable identifiers and may only make claims supported by that evidence. Unsupported or conflicting claims become warnings, clarification requests, or a safe insufficiency response.

## Offline Ingestion Pipeline

1. Register an approved source URL and source policy.
2. Validate scheme, hostname, redirect target, content type, and request limits.
3. Respect robots.txt and applicable BIS website policies.
4. Fetch with bounded timeouts, retries, rate limits, and a descriptive user agent.
5. Detect HTML/PDF content and compute a content hash.
6. Skip unchanged content while recording the observation time.
7. Extract HTML or PDF text while preserving page numbers for PDFs.
8. Apply OCR only when extracted text is absent or below a configured quality threshold.
9. Extract known metadata without guessing; unknown values remain NULL.
10. Detect clauses/sections and retain headings with nearby content.
11. Clean encoding and layout noise without removing technical identifiers.
12. Chunk by document/page/clause context with overlap where needed.
13. Generate embeddings through the provider interface.
14. Store documents, pages, clauses, chunks, provenance, and ingestion events.
15. Validate required links, hashes, page references, and embedding dimensions.
16. Produce a report containing counts, warnings, failures, and source URLs.

## Query Pipeline

1. Validate request size and language options.
2. Detect language and identify intent: standard lookup, product mapping, certification, testing, laboratory, hallmarking, clause lookup, or general information.
3. Extract product, attributes, standard numbers, certification terms, tests, location, and language.
4. Mark each extracted item as explicit, inferred, or unknown.
5. Build metadata filters only from reliable extracted values.
6. Run PostgreSQL full-text search and pgvector search in parallel.
7. Fuse candidates using a documented weighted method; preserve both scores.
8. Rerank candidates using a configurable reranker or deterministic fallback.
9. Apply source, freshness, and evidence-quality filters.
10. Evaluate evidence sufficiency. Missing or contradictory evidence stops generation or requests clarification.
11. Generate a structured answer from bounded evidence excerpts and metadata.
12. Validate every cited document, page, clause, excerpt, and URL against stored evidence.
13. Return answer, confidence, citations, related standards, warnings, unknowns, and source documents.

## Hybrid Retrieval

Keyword search is essential for exact IS numbers, abbreviations, clause numbers, and test names. Semantic search handles paraphrases and natural product descriptions. Neither channel alone is sufficient. The fusion function and thresholds must be configurable and evaluated against a labelled dataset rather than presented as an unmeasured accuracy claim.

Initial metadata filters may include standard number, document type, source domain, language, product category, and document version. Filters must not silently discard evidence when extracted entities are uncertain.

The PostgreSQL adapter now supports weighted hybrid SQL retrieval with a strict `VECTOR(1024)` query-embedding check. The public assistant currently uses keyword retrieval until an approved embedding provider is configured; the hybrid path must not be enabled with fabricated or placeholder vectors.

Reranking uses a deterministic fused-score fallback while no provider is configured. Any future provider must return the exact retrieved evidence identity set; otherwise the result is rejected before answer generation.

## Evidence Sufficiency

Sufficiency is an explicit decision, not an implied LLM confidence. Signals include:

- minimum number and quality of independent relevant chunks
- source authority and document status
- similarity/relevance thresholds
- agreement or conflict between retrieved evidence
- presence of required fields for the requested claim
- citation coverage for answer claims

The result should be `sufficient`, `insufficient`, or `conflicting`, with machine-readable reasons. Low confidence is not permission to guess.

## Structured Answer Contract

```json
{
  "answer": "...",
  "confidence": "high|medium|low",
  "evidence_sufficient": true,
  "citations": [],
  "related_standards": [],
  "unknowns": [],
  "warnings": [],
  "source_documents": []
}
```

The final schema is owned by Pydantic models. Citation objects must use stored evidence IDs and may include document title, standard number, clause, page, excerpt, version, and official source URL only when those values are present in the database.

## Multilingual Strategy

Use one evidence base. Query understanding and answer generation may support English, Hindi, and Telugu. Source evidence remains in its original language unless an official translated source exists. Standard numbers, clause identifiers, quoted excerpts, and official terminology must remain exact. Any machine translation is labelled as explanation, not authoritative evidence.

## Evaluation Plan

Create a labelled dataset for standard identification, product mapping, certification, testing, laboratory, hallmarking, clause lookup, multilingual, ambiguous, unsupported, and adversarial questions. The initial synthetic cases live in `evaluation/questions.jsonl` and contain no official facts. Measure retrieval recall/precision, citation support, refusal quality, answer usefulness, language fidelity, and latency. Publish only measured results with dataset version and test configuration.

## Failure Handling

- No relevant evidence: explain that the current official knowledge base could not verify the answer and request useful missing details.
- Conflicting documents: show the conflict, document versions/dates, and avoid selecting a winner without an authority rule.
- Citation mismatch: suppress the citation or answer claim and log a validation failure.
- Provider failure: return a controlled service error or evidence-only result; never fall back to unsupported model memory.
