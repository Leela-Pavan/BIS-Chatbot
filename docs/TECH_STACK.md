# BIS Sahayak Technology Stack

## Fixed Choices

| Area | Choice | Boundary |
| --- | --- | --- |
| Frontend | Next.js, React, TypeScript | UI, routing, accessibility, structured evidence presentation |
| Styling | Tailwind CSS and shadcn/ui | Consistent, responsive service-platform UI |
| API | Python, FastAPI, Uvicorn | Versioned HTTP API and validation |
| Schemas | Pydantic | Request, response, configuration, and ingestion contracts |
| Database | PostgreSQL | System of record and transactional metadata |
| Keyword retrieval | PostgreSQL full-text search | Exact technical terms, IS numbers, clauses |
| Vector retrieval | pgvector | Semantic similarity in the same database |
| HTTP ingestion | httpx | Timeouts, redirects, headers, and bounded downloads |
| HTML extraction | BeautifulSoup | Controlled HTML parsing |
| PDF extraction | PyMuPDF | Text and page-preserving extraction |
| OCR | PaddleOCR, optional | Only for scanned/image-based documents when needed |
| Crawler | Controlled custom Python fetcher initially | Approved URLs/domains, policy checks, rate limits |
| Testing | Pytest, Vitest, Playwright | Backend, frontend, and browser behavior |
| CI/CD | GitHub Actions | Reproducible checks and build artifacts |
| Packaging | Docker and Docker Compose for local dependencies | Local PostgreSQL/pgvector and repeatable services |

LlamaIndex may be evaluated during implementation, but the initial design uses clean internal retrieval interfaces so that adding it is optional rather than an architectural dependency.

## Provider Abstractions

The following interfaces must be replaceable:

- `EmbeddingProvider`: text to vectors, model name, dimensions, batch behavior
- `GenerationProvider`: grounded prompt to structured answer
- `RerankerProvider`: candidate evidence to relevance scores
- `TranslationProvider`: optional language assistance, never authoritative metadata
- `ObjectStorageProvider`: optional raw-document storage

Provider credentials are server-side environment variables. The frontend never receives them.

## Environment Configuration

Expected configuration categories include:

- `DATABASE_URL`
- `CORS_ORIGINS`
- `API_RATE_LIMIT`
- `EMBEDDING_PROVIDER` and model settings
- `GENERATION_PROVIDER` and model settings
- `RERANKER_PROVIDER` and model settings
- `INGESTION_USER_AGENT`
- approved source registry location
- raw-document storage settings, if enabled

The repository should provide `.env.example` later with non-secret values only. Production secrets belong in the deployment secret manager.

## Local and External Requirements

### Can run locally for free

- Next.js development server
- FastAPI/Uvicorn
- PostgreSQL with pgvector through Docker
- PostgreSQL full-text search
- Pytest, Vitest, Playwright, and static checks
- Deterministic fake embedding/generation providers for tests
- Ingestion against explicitly approved test fixtures

### May require external access or cost

- Hosted PostgreSQL for production
- Hosted embedding, reranking, translation, or generation APIs
- GPU or larger memory for local multilingual models and OCR
- Managed object storage for a large raw-document archive
- Deployment hosting and scheduled ingestion
- Access restrictions, licensing, or policy approval for some BIS resources

No provider is fixed until latency, language quality, data handling, and cost are evaluated.

## Dependency Policy

Keep the initial dependency set small. Add a package only when it removes meaningful implementation risk or is required by the selected stack. Pin compatible versions, audit licenses, and test the package in the target Python/Node versions before adoption. Do not add multiple overlapping RAG frameworks.

## Development Quality Gates

Every phase should include:

- formatting and lint checks
- type checks where applicable
- focused unit tests
- migration/schema checks
- no-secret checks
- frontend build checks when frontend code changes

Live BIS crawling and paid model calls must not be required for ordinary CI.
