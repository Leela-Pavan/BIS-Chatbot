import re
from typing import Iterable, List, Optional

from bs4 import BeautifulSoup

from app.knowledge.models import ExtractedClause, ExtractedDocument, ExtractedPage

CLAUSE_PATTERN = re.compile(r"(?m)^\s*(\d+(?:\.\d+)*)(?:\s+|$)(.*)$")


def normalize_text(value: str) -> str:
    return "\n".join(line.strip() for line in value.splitlines() if line.strip())


def extract_html(content: bytes) -> ExtractedDocument:
    soup = BeautifulSoup(content, "html.parser")
    for element in soup(["script", "style", "noscript"]):
        element.decompose()
    text = normalize_text(soup.get_text("\n"))
    page = ExtractedPage(page_number=1, text=text)
    return ExtractedDocument(pages=[page], clauses=_extract_clauses([page]))


def extract_pdf(content: bytes) -> ExtractedDocument:
    try:
        import fitz
    except ImportError as error:
        raise RuntimeError("PDF extraction requires PyMuPDF") from error

    with fitz.open(stream=content, filetype="pdf") as document:
        pages = [
            ExtractedPage(page_number=index + 1, text=normalize_text(page.get_text()))
            for index, page in enumerate(document)
        ]
    return ExtractedDocument(pages=pages, clauses=_extract_clauses(pages))


def _extract_clauses(pages: Iterable[ExtractedPage]) -> List[ExtractedClause]:
    clauses: List[ExtractedClause] = []
    for page in pages:
        matches = list(CLAUSE_PATTERN.finditer(page.text))
        for index, match in enumerate(matches):
            start = match.start()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(page.text)
            text = normalize_text(page.text[start:end])
            title = match.group(2).strip() or None
            clauses.append(
                ExtractedClause(
                    page_number=page.page_number,
                    clause_number=match.group(1),
                    section_title=title,
                    text=text,
                )
            )
    return clauses
