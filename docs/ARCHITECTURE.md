# BIS Sahayak Architecture

## Scope

This document defines the initial system boundaries for PS26107. It is a modular application, not a microservice fleet. The first delivery optimizes for traceability, testability, and a demonstrable end-to-end evidence path.

## System Flow

```text
User
  -> Next.js application
  -> FastAPI API
  -> Query understanding
  -> Intent and entity extraction
  -> Metadata filters
  -> PostgreSQL keyword search + pgvector search
  -> Result fusion and reranking
  -> Evidence sufficiency check
  -> RAG answer generation
  -> Citation validation
  -> Structured response
  -> Evidence-aware UI
```

The ingestion path is separate from online queries:

```text
Approved BIS source registry
  -> URL and policy validation
  -> Controlled fetcher
  -> HTML/PDF extraction with page preservation
  -> Metadata and clause detection
  -> Cleaning and context-aware chunking
  -> Embeddings
  -> PostgreSQL documents, evidence, and indexes
```

## Major Components

### Frontend

- Dashboard with assistant entry points and recent questions
- Assistant conversation with suggested prompts, confidence, warnings, and feedback
- Smart Standard Finder for natural product descriptions
- Certification Navigator
- Laboratory Finder
- Hallmarking Assistant
- Browse Standards and Evidence Viewer

The frontend receives structured evidence and does not call model providers directly.

### API and Application Services

FastAPI owns request validation, authentication/session boundaries if introduced, rate limits, CORS, error mapping, and response contracts. Application services own the use cases:

- `query_understanding`: intent, entities, language, explicit/inferred/unknown attributes
- `retrieval`: keyword search, vector search, metadata filters, fusion, reranking
- `answering`: prompt assembly, generation-provider abstraction, safe response handling
- `citation`: citation extraction and verification against retrieved evidence
- `domains`: standard finder, certification, laboratory, and hallmarking workflows
- `ingestion`: source registry, fetching, extraction, chunking, embedding, reports

### Data Layer

PostgreSQL is the system of record. PostgreSQL full-text search handles exact terms such as IS numbers and clauses. pgvector stores embeddings in the same database, allowing evidence metadata and retrieval results to remain transactionally connected.

## Domain Boundaries

- `Source` and `Document` describe where information came from.
- `Page`, `Clause`, and `Chunk` preserve the evidence hierarchy.
- `Standard`, `CertificationScheme`, `TestingRequirement`, and `Laboratory` represent structured knowledge only when provenance exists.
- `Product` and product attributes represent user-provided or extracted descriptions; they are not authoritative BIS facts by default.
- `Provenance` is required for AI-relevant records and structured claims.

## API Boundaries

Initial versioned routes should remain small:

- `GET /api/v1/health`
- `POST /api/v1/assistant/query`
- `POST /api/v1/standards/search`
- `GET /api/v1/evidence/{evidence_id}`
- `POST /api/v1/certification/assess`
- `POST /api/v1/laboratories/search`
- `POST /api/v1/hallmarking/query`

Administrative ingestion routes should be protected and may initially be CLI-only. Public API responses use Pydantic models and include `evidence_sufficient`, citations, warnings, and source documents.

## First Demonstration Journey

A manufacturer describes a 20-litre electric storage water heater for domestic use. The system extracts product attributes, retrieves candidate evidence, explains why a standard is relevant, reports missing attributes, and links to the exact source evidence. Certification, testing, and laboratory guidance are shown only where current verified evidence supports them.

## Deployment Shape

- Frontend: deployable to Vercel or an equivalent static/server-rendered host
- Backend: deployable to Render, Railway, or an equivalent container host
- Database: managed PostgreSQL with pgvector, or local Docker for development
- Ingestion: controlled worker/CLI scheduled separately from public request handling
- CI: GitHub Actions for formatting, type checks, tests, migration checks, and build checks

Provider-specific code must be isolated in configuration and adapters so deployment can change without changing domain logic.

## Non-Goals for the First Phase

- No Kubernetes, Kafka, microservices, or separate vector database
- No broad internet crawler
- No automatic claim that certification is mandatory
- No fake or placeholder BIS standards, laboratories, citations, or evaluation scores
- No advanced RAG pipeline until the foundation and data policies are approved
