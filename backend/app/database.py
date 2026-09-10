from urllib.parse import urlsplit, urlunsplit


def psycopg_url(database_url: str) -> str:
    parts = urlsplit(database_url)
    scheme = parts.scheme
    if scheme.endswith("+psycopg"):
        scheme = scheme[: -len("+psycopg")]
    return urlunsplit((scheme, parts.netloc, parts.path, parts.query, parts.fragment))


def database_is_ready(database_url: str) -> bool:
    try:
        import psycopg
    except ImportError:
        return False
    try:
        with psycopg.connect(psycopg_url(database_url), connect_timeout=3) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT 1 FROM schema_migrations WHERE version = %s",
                    ("002_knowledge_layer",),
                )
                return cursor.fetchone() is not None
    except (OSError, psycopg.Error):
        return False
