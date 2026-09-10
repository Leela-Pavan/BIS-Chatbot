# BIS Sahayak Data Policy

## Authority and Provenance

Official BIS sources are the primary authority for BIS standards, certification, hallmarking, testing, laboratory, and service claims. Every ingested resource must retain source URL, source domain, title, document type, retrieval time, last-seen time, content hash, and available version/publication metadata.

Metadata is extracted, not invented. If a field cannot be verified, store NULL or an explicit unknown state. A user-provided product description is not an official BIS fact.

## Approved Source Registry

Sources are added through a reviewed registry rather than an unrestricted crawler. Each entry should define URL, approved hostname, content type, purpose, crawl priority, refresh policy, and policy notes. The fetcher must reject unapproved domains and unsafe redirect targets, enforce HTTPS where applicable, limit response size, and respect robots.txt and applicable website policies.

The initial registry contains no live URLs or records. A source may be enabled only after it is confirmed as an official BIS resource and its usage policy is understood. Phase 2 provides typed registry loading and a controlled fetcher, but it deliberately does not activate any source. Phase 3 adds the persistence schema and extraction interfaces without inserting BIS records.

## Core Data Model

The planned normalized entities are:

- `sources`: approved source and crawl policy
- `documents`: title, type, URL, domain, hash, retrieval/freshness metadata, version, publication date
- `document_pages`: document, page number, extracted text
- `clauses`: document/page, clause number, section title, text
- `chunks`: document/page/clause context, content, embedding, search metadata
- `standards`: standard number, title, status, dates, source document
- `products` and `product_attributes`: user or curated descriptions with provenance
- `standard_product_relationships`: relationship type and supporting evidence
- `certification_schemes`: verified scheme details and evidence
- `testing_requirements`: test, description, applicability, evidence
- `laboratories`: verified name, location, address, capability, contact, and source
- `provenance`: source record, locator, extraction method, confidence, and timestamps
- `ingestion_runs` and `ingestion_events`: operational status, errors, counts, and hashes

Foreign keys must prevent evidence records from outliving their source documents. Soft retirement is preferred when a document is superseded so historical citations remain auditable.

## Freshness and Deduplication

Store `content_hash`, `retrieved_at`, and `last_seen`. A fetch with the same hash updates observation metadata without creating a duplicate document. A changed hash creates a new document version or revision according to the configured identity rule, reprocesses affected pages/chunks, and records the relationship to the prior version.

## Structured Claims

A structured claim is usable in an answer only when it has a provenance link. Certification status must distinguish `mandatory`, `voluntary`, `conditional`, and `not_verified`; mandatory status requires authoritative supporting evidence such as an applicable government notification or official BIS source. Laboratory records must not be displayed unless the current record supports the requested standard/test/location.

## Personal and User Data

The first version should minimize personal data. Store only what is needed for an active session, feedback, rate limiting, and operational debugging. Do not send unnecessary user identifiers or conversation history to model providers. Define retention, deletion, access control, and production logging rules before enabling persistent accounts.

## Sample and Demo Data

Development fixtures must be clearly labelled `DEMO DATA` or `SAMPLE DATA - NOT OFFICIAL`. They must not use plausible fabricated BIS standard numbers, laboratories, certifications, or citations. Tests should use synthetic identifiers that cannot be mistaken for live official records.

## Data Quality Checks

Ingestion validation should check approved domains, URL reachability, hashes, content type, page numbering, clause links, required provenance, duplicate identity, embedding dimensions, and parse errors. Reports must surface failures; they must not silently create partial authoritative records.
