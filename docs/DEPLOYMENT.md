# Deployment Checklist

## Local Compose

Run `docker compose up --build` for local development. The default database values are development-only fallbacks. The frontend is exposed on port 3000 and the API on port 8000. PostgreSQL is intentionally internal to the Compose network by default.

## Required Production Changes

- Set a strong `POSTGRES_PASSWORD` through the deployment secret manager.
- Use a managed PostgreSQL instance with pgvector or a protected database network.
- Set `ENVIRONMENT=production`.
- Set `CORS_ORIGINS` to the exact frontend origin; do not use a wildcard.
- Set `ALLOWED_HOSTS` to the exact API hostnames.
- Set `DATABASE_URL` through a secret, not a committed file.
- Keep `EMBEDDING_PROVIDER=disabled` until a reviewed provider and data-processing policy are approved.
- Terminate TLS at the platform edge and enforce HTTPS for public traffic.
- Store raw documents outside the application image when enabled.
- Run migrations as a controlled release step and verify `/api/v1/ready` afterward.
- Configure log redaction, backups, retention, rate limits, and alerting before public use.

## Health Checks

- `/api/v1/health` checks process liveness.
- `/api/v1/ready` checks PostgreSQL connectivity and the knowledge-layer migration marker.

A healthy process is not sufficient for traffic; production routing should use readiness.
