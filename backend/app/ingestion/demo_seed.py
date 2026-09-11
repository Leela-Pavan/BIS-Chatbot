from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, List

import psycopg

ROOT = Path(__file__).resolve().parents[2]
FAQ_PATH = ROOT.parent / "data_sources" / "basic_bis_faqs.jsonl"
DEFAULT_DB_URL = "postgresql+psycopg://bis_sahayak:bis_sahayak@localhost:5432/bis_sahayak"


def load_faqs(path: Path) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            records.append(record)
    return records


def get_database_url() -> str:
    return os.getenv("DATABASE_URL", DEFAULT_DB_URL)


def upsert_source(conn: psycopg.Connection, source_id: str, url: str, domain: str) -> str:
    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO sources (source_id, url, approved_domain, purpose, policy_notes, enabled)
            VALUES (%s, %s, %s, %s, %s, TRUE)
            ON CONFLICT (source_id) DO UPDATE
                SET url = EXCLUDED.url,
                    approved_domain = EXCLUDED.approved_domain,
                    purpose = EXCLUDED.purpose,
                    policy_notes = EXCLUDED.policy_notes,
                    enabled = TRUE
            RETURNING id
            """,
            (
                source_id,
                url,
                domain,
                "Official BIS FAQ knowledge used for local development and basic retrieval testing.",
                "DEMO DATA ONLY - for local evaluation and development. Not official BIS publication data.",
            ),
        )
        row = cursor.fetchone()
        if row is None:
            cursor.execute("SELECT id FROM sources WHERE source_id = %s", (source_id,))
            row = cursor.fetchone()
        return str(row[0])


def upsert_document(conn: psycopg.Connection, source_id: str, title: str, source_url: str) -> str:
    document_hash = hashlib.sha256(f"demo-faq::{source_id}::{title}".encode("utf-8")).hexdigest()
    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO documents (
                source_id, title, document_type, source_url, source_domain,
                content_hash, retrieved_at, last_seen, status, version
            )
            VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW(), 'active', 'demo-v1')
            ON CONFLICT (source_url, content_hash) DO UPDATE
                SET title = EXCLUDED.title,
                    last_seen = NOW(),
                    status = 'active'
            RETURNING id
            """,
            (
                source_id,
                title,
                "html",
                source_url,
                "bis.gov.in",
                document_hash,
            ),
        )
        row = cursor.fetchone()
        if row is None:
            cursor.execute(
                "SELECT id FROM documents WHERE source_url = %s AND content_hash = %s",
                (source_url, document_hash),
            )
            row = cursor.fetchone()
        return str(row[0])


def insert_page(conn: psycopg.Connection, document_id: str, page_number: int, text: str) -> str:
    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO document_pages (document_id, page_number, extracted_text)
            VALUES (%s, %s, %s)
            ON CONFLICT (document_id, page_number) DO UPDATE
                SET extracted_text = EXCLUDED.extracted_text
            RETURNING id
            """,
            (document_id, page_number, text),
        )
        row = cursor.fetchone()
        if row is None:
            cursor.execute(
                "SELECT id FROM document_pages WHERE document_id = %s AND page_number = %s",
                (document_id, page_number),
            )
            row = cursor.fetchone()
        return str(row[0])


def seed_demo_knowledge() -> None:
    faq_records = load_faqs(FAQ_PATH)
    if not faq_records:
        raise RuntimeError(f"No FAQ data found in {FAQ_PATH}")

    database_url = get_database_url()
    with psycopg.connect(database_url, connect_timeout=5) as conn:
        source_id = upsert_source(
            conn,
            "bis_demo_faq",
            "https://www.bis.gov.in/",
            "bis.gov.in",
        )
        document_id = upsert_document(
            conn,
            source_id,
            "BIS Basic FAQ Knowledge Base",
            "https://www.bis.gov.in/",
        )
        page_id = insert_page(
            conn,
            document_id,
            1,
            "\n\n".join(f"Q: {item['question']}\nA: {item['answer']}" for item in faq_records),
        )

        for idx, item in enumerate(faq_records, start=1):
            question = item["question"]
            answer = item["answer"]
            content = f"Q: {question}\nA: {answer}"
            metadata = {
                "category": item.get("category", "faq"),
                "language": item.get("language", "en"),
                "source_url": item.get("source_url", "https://www.bis.gov.in/"),
                "source_title": item.get("source_title", "BIS Official Website"),
            }
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO chunks (document_id, page_number, clause_number, content, metadata)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (document_id, page_number, clause_number, content) DO NOTHING
                    RETURNING id
                    """,
                    (document_id, 1, f"faq-{idx}", content, json.dumps(metadata)),
                )
                row = cursor.fetchone()
                chunk_id = str(row[0]) if row else None
                if chunk_id is None:
                    cursor.execute(
                        "SELECT id FROM chunks WHERE document_id = %s AND page_number = %s AND clause_number = %s AND content = %s",
                        (document_id, 1, f"faq-{idx}", content),
                    )
                    row = cursor.fetchone()
                    chunk_id = str(row[0]) if row else None
                if chunk_id:
                    cursor.execute(
                        """
                        INSERT INTO provenance (source_id, document_id, page_id, chunk_id, locator, extraction_method)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT DO NOTHING
                        """,
                        (
                            source_id,
                            document_id,
                            page_id,
                            chunk_id,
                            f"faq-{idx}",
                            "demo_seed",
                        ),
                    )


if __name__ == "__main__":
    seed_demo_knowledge()
    print(f"Seeded {len(load_faqs(FAQ_PATH))} BIS FAQ entries into the local knowledge database.")
