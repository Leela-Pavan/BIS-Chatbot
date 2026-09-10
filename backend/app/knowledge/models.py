from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class ExtractedPage:
    page_number: int
    text: str


@dataclass(frozen=True)
class ExtractedClause:
    page_number: int
    clause_number: str
    section_title: Optional[str]
    text: str


@dataclass(frozen=True)
class ExtractedDocument:
    pages: List[ExtractedPage]
    clauses: List[ExtractedClause]
