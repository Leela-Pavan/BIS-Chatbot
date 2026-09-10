-- Phase 1 baseline. Domain tables and pgvector indexes arrive with the knowledge-layer phase.
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS schema_migrations (
    version TEXT PRIMARY KEY,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO schema_migrations (version)
VALUES ('001_initial')
ON CONFLICT (version) DO NOTHING;
