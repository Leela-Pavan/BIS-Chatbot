import re
from typing import Optional, Tuple, List

from app.rag.schemas import Intent, Language, QueryUnderstanding

STANDARD_NUMBER_PATTERN = re.compile(r"\bIS\s*[-:]?\s*\d{3,6}(?:\s*:\s*\d{4})?\b", re.IGNORECASE)
LOCATION_PATTERN = re.compile(r"\b(?:in|near|at)\s+([A-Za-z][A-Za-z .'-]{2,40})", re.IGNORECASE)


def detect_language(question: str, requested: Optional[Language] = None) -> Language:
    if requested:
        return requested
    if re.search(r"[\u0900-\u097F]", question):
        return "hi"
    if re.search(r"[\u0C00-\u0C7F]", question):
        return "te"
    if re.search(r"[A-Za-z]", question):
        return "en"
    return "unknown"


def detect_intent(question: str) -> Intent:
    normalized = question.lower()
    signals: List[Tuple[Intent, Tuple[str, ...]]] = [
        ("laboratory", ("laboratory", "lab", "test centre", "testing center")),
        ("certification", ("certification", "certify", "mandatory", "qco")),
        ("hallmarking", ("hallmark", "jewellery", "gold")),
        ("testing", ("test requirement", "testing", "test method")),
        ("clause_lookup", ("clause", "section", "page")),
        ("product_mapping", ("manufacture", "manufacturing", "product", "applies to")),
        ("standard_lookup", ("standard", "is number", "indian standard")),
    ]
    for intent, keywords in signals:
        if any(keyword in normalized for keyword in keywords):
            return intent
    return "general"


def understand_query(
    question: str, requested_language: Optional[Language] = None
) -> QueryUnderstanding:
    standard_numbers = [
        match.upper().replace(" ", "") for match in STANDARD_NUMBER_PATTERN.findall(question)
    ]
    location_match = LOCATION_PATTERN.search(question)
    explicit_terms = standard_numbers.copy()
    if location_match:
        explicit_terms.append(location_match.group(1).strip())
    unknowns = []
    if detect_intent(question) == "product_mapping" and len(question.split()) < 8:
        unknowns.append("product attributes and intended use")
    return QueryUnderstanding(
        intent=detect_intent(question),
        language=detect_language(question, requested_language),
        explicit_terms=explicit_terms,
        standard_numbers=standard_numbers,
        location=location_match.group(1).strip() if location_match else None,
        unknowns=unknowns,
    )
