# BIS Sahayak

AI-powered decision support for Indian Standards and BIS services.

## Vision

BIS Sahayak is an evidence-first platform for industries, manufacturers, MSMEs, startups, consumers, students, and researchers. It retrieves information from approved official BIS sources, explains the retrieved evidence, and exposes document, clause, page, version, and source references.

It is not a generic chatbot. Answers must distinguish source-supported facts, AI-generated explanations, and information that could not be verified.

## Current Status

**Phase 7: Evaluation, security, provider, browser-test, database-validation, container, deployment, and RAG orchestration foundations implemented.** The frontend workflow foundation is joined by replaceable embedding/reranking/generation provider interfaces, an opt-in BGE-M3-compatible local adapter, validated embedding batches, a unified RAG service, a validated loader for eight synthetic labelled evaluation cases, trusted-host configuration, request-size limits, security response headers, reproducible npm CI installs, Playwright smoke coverage, a CI pgvector migration job, a Docker Compose application stack, database-aware API readiness checks, and a deployment checklist. Python 3.11 is installed locally; Ruff passes and all 21 backend tests pass. The frontend build reaches successful compilation, lint/type validation, and static page generation. Embeddings remain disabled by default; no evaluation scores are claimed, and live records and production deployment remain pending. No BIS records, standards, laboratories, citations, or evaluation scores are included. Docker Desktop still requires a separate administrator-approved installation.

## Planned Architecture

- Next.js, React, TypeScript, Tailwind CSS, and shadcn/ui frontend
- FastAPI, Python, and Pydantic backend
- PostgreSQL with PostgreSQL full-text search and pgvector
- Controlled ingestion of approved BIS HTML and PDF sources
- Page-preserving extraction, clause-aware chunking, hybrid retrieval, reranking, evidence sufficiency checks, and citation validation
- English, Hindi, and Telugu interaction over one authoritative knowledge base

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), [docs/TECH_STACK.md](docs/TECH_STACK.md), and [docs/RAG_DESIGN.md](docs/RAG_DESIGN.md).

## Fixed Principles

1. Official BIS sources are authoritative for BIS claims.
2. No unsupported standard, clause, page, URL, certification status, or laboratory fact may be invented.
3. Retrieval precedes generation; the model answers only from supplied evidence.
4. Insufficient evidence results in a transparent refusal or clarification request.
5. Sample records, if later needed, must be labelled `DEMO DATA` and must never resemble verified BIS data.
6. PostgreSQL is the initial unified data layer; no separate vector database is planned.

## Roadmap

### Phase 1: Foundation

- Create the frontend/backend repository structure
- Add configuration, health endpoints, database migrations, and local Docker Compose
- Add CI checks without requiring live BIS or model credentials

### Phase 2: Controlled ingestion

- Add an approved-source registry
- Implement URL/domain validation, robots/policy checks, rate limits, hashing, retrieval logs, HTML/PDF extraction, page preservation, and ingestion reports
- Ingest only explicitly approved sources after policy review

### Phase 3: Knowledge layer

- Add normalized provenance, documents, pages, clauses, chunks, standards, and structured BIS entities
- Add PostgreSQL full-text indexes and pgvector migrations
- Add embedding-provider abstraction

### Phase 4: Retrieval and answer safety

- Implement query understanding, metadata filters, keyword/vector retrieval, score fusion, reranking, evidence sufficiency, and citation validation
- Add structured Pydantic response contracts

### Phase 5: First demo journey

- Implement Smart Standard Finder for a manufacturer product description
- Add evidence viewer, confidence, unknown attributes, certification guidance, testing requirements, and verified laboratory results only

### Phase 6: User experience and multilingual support

- Add assistant, standards, certification, laboratory, hallmarking, and evidence views
- Add English, Hindi, and Telugu response handling while preserving technical identifiers

### Phase 7: Evaluation and deployment

- Build retrieval, citation, refusal, multilingual, latency, and end-to-end evaluation datasets
- Add measured reports, security hardening, deployment configuration, and Playwright coverage

## Local Development Expectations

The first implementation should run without paid services using PostgreSQL/pgvector locally and deterministic test doubles. A real embedding provider and answer-generation provider will be configurable later through environment variables. No API keys belong in the frontend or Git.

## Container Stack

Once Docker is installed, run `docker compose up --build` from the repository root. The frontend is available at `http://localhost:3000` and the API at `http://localhost:8000`; PostgreSQL stays internal to the Compose network by default. The API waits for the healthy pgvector database, and the frontend waits for the API health check. See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) before exposing any service publicly.

## Next Recommended Phase

After approval, implement the remaining production-hardening work: connect a reviewed embedding/reranking provider, run measured retrieval and citation evaluations against an approved knowledge snapshot, add multilingual tests, and verify the new container stack in an environment with Docker. Do not add fabricated or unverified BIS data.
