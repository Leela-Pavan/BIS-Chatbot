CREATE TABLE IF NOT EXISTS sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id TEXT NOT NULL UNIQUE,
    url TEXT NOT NULL UNIQUE,
    approved_domain TEXT NOT NULL,
    purpose TEXT NOT NULL,
    policy_notes TEXT NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES sources(id),
    title TEXT,
    document_type TEXT NOT NULL CHECK (document_type IN ('html', 'pdf')),
    source_url TEXT NOT NULL,
    source_domain TEXT NOT NULL,
    content_hash CHAR(64) NOT NULL,
    retrieved_at TIMESTAMPTZ NOT NULL,
    last_seen TIMESTAMPTZ NOT NULL,
    version TEXT,
    publication_date DATE,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'superseded', 'retired')),
    previous_document_id UUID REFERENCES documents(id),
    UNIQUE (source_url, content_hash)
);

CREATE TABLE IF NOT EXISTS document_pages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    page_number INTEGER NOT NULL CHECK (page_number > 0),
    extracted_text TEXT NOT NULL,
    UNIQUE (document_id, page_number)
);

CREATE TABLE IF NOT EXISTS clauses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    page_id UUID NOT NULL REFERENCES document_pages(id) ON DELETE CASCADE,
    clause_number TEXT NOT NULL,
    section_title TEXT,
    text TEXT NOT NULL,
    UNIQUE (document_id, page_id, clause_number)
);

CREATE TABLE IF NOT EXISTS chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    page_number INTEGER NOT NULL CHECK (page_number > 0),
    clause_number TEXT,
    content TEXT NOT NULL,
    search_vector TSVECTOR GENERATED ALWAYS AS (to_tsvector('simple', content)) STORED,
    embedding VECTOR(1024),
    metadata JSONB NOT NULL DEFAULT '{}'::JSONB,
    UNIQUE (document_id, page_number, clause_number, content)
);

CREATE TABLE IF NOT EXISTS standards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    standard_number TEXT NOT NULL UNIQUE,
    title TEXT,
    description TEXT,
    status TEXT,
    version TEXT,
    publication_date DATE,
    revision_date DATE,
    source_document_id UUID REFERENCES documents(id)
);

CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    category TEXT,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS product_attributes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    attribute TEXT NOT NULL,
    value TEXT NOT NULL,
    evidence_chunk_id UUID REFERENCES chunks(id),
    UNIQUE (product_id, attribute, value)
);

CREATE TABLE IF NOT EXISTS standard_product_relationships (
    standard_id UUID NOT NULL REFERENCES standards(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    relationship_type TEXT NOT NULL,
    evidence_chunk_id UUID REFERENCES chunks(id),
    PRIMARY KEY (standard_id, product_id, relationship_type)
);

CREATE TABLE IF NOT EXISTS certification_schemes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('mandatory', 'voluntary', 'conditional', 'not_verified')),
    description TEXT,
    source_document_id UUID REFERENCES documents(id)
);

CREATE TABLE IF NOT EXISTS testing_requirements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    standard_id UUID REFERENCES standards(id),
    test_name TEXT NOT NULL,
    test_description TEXT,
    applicable_product_id UUID REFERENCES products(id),
    evidence_chunk_id UUID REFERENCES chunks(id)
);

CREATE TABLE IF NOT EXISTS laboratories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    location TEXT,
    address TEXT,
    capabilities JSONB NOT NULL DEFAULT '[]'::JSONB,
    contact_information JSONB NOT NULL DEFAULT '{}'::JSONB,
    source_document_id UUID REFERENCES documents(id),
    verified_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS provenance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES sources(id),
    document_id UUID REFERENCES documents(id),
    page_id UUID REFERENCES document_pages(id),
    clause_id UUID REFERENCES clauses(id),
    chunk_id UUID REFERENCES chunks(id),
    locator TEXT,
    extraction_method TEXT NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (document_id IS NOT NULL OR page_id IS NOT NULL OR clause_id IS NOT NULL OR chunk_id IS NOT NULL)
);

CREATE TABLE IF NOT EXISTS ingestion_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    status TEXT NOT NULL CHECK (status IN ('running', 'completed', 'failed')),
    source_count INTEGER NOT NULL DEFAULT 0,
    document_count INTEGER NOT NULL DEFAULT 0,
    error_count INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS ingestion_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES ingestion_runs(id) ON DELETE CASCADE,
    source_id UUID REFERENCES sources(id),
    status TEXT NOT NULL CHECK (status IN ('fetched', 'skipped', 'failed')),
    url TEXT NOT NULL,
    message TEXT NOT NULL,
    content_hash CHAR(64),
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS chunks_search_vector_idx ON chunks USING GIN (search_vector);
CREATE INDEX IF NOT EXISTS chunks_document_idx ON chunks (document_id, page_number);
CREATE INDEX IF NOT EXISTS clauses_document_idx ON clauses (document_id, page_id);
CREATE INDEX IF NOT EXISTS documents_hash_idx ON documents (content_hash);
CREATE INDEX IF NOT EXISTS provenance_chunk_idx ON provenance (chunk_id);

INSERT INTO schema_migrations (version)
VALUES ('002_knowledge_layer')
ON CONFLICT (version) DO NOTHING;
