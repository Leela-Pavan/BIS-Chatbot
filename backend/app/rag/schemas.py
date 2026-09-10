from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Field, HttpUrl

Intent = Literal[
    "standard_lookup",
    "product_mapping",
    "certification",
    "testing",
    "laboratory",
    "hallmarking",
    "clause_lookup",
    "general",
]
Language = Literal["en", "hi", "te", "unknown"]
EvidenceState = Literal["sufficient", "insufficient", "conflicting"]
Confidence = Literal["high", "medium", "low"]


class QueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=4000)
    language: Optional[Language] = None


class QueryUnderstanding(BaseModel):
    intent: Intent
    language: Language
    explicit_terms: List[str] = Field(default_factory=list)
    inferred_terms: List[str] = Field(default_factory=list)
    unknowns: List[str] = Field(default_factory=list)
    standard_numbers: List[str] = Field(default_factory=list)
    location: Optional[str] = None


class RetrievalFilters(BaseModel):
    standard_number: Optional[str] = None
    document_type: Optional[Literal["html", "pdf"]] = None
    source_domain: Optional[str] = None
    language: Optional[Language] = None
    product_category: Optional[str] = None
    document_version: Optional[str] = None


class EvidenceCandidate(BaseModel):
    evidence_id: str
    content: str = Field(min_length=1)
    document_id: str
    document_title: Optional[str] = None
    standard_number: Optional[str] = None
    clause_number: Optional[str] = None
    page_number: Optional[int] = Field(default=None, ge=1)
    version: Optional[str] = None
    source_url: Optional[HttpUrl] = None
    keyword_score: float = Field(default=0.0, ge=0.0, le=1.0)
    semantic_score: float = Field(default=0.0, ge=0.0, le=1.0)
    fused_score: float = Field(default=0.0, ge=0.0, le=1.0)


class SufficiencyDecision(BaseModel):
    state: EvidenceState
    reasons: List[str] = Field(default_factory=list)


class Citation(BaseModel):
    evidence_id: str
    document_id: str
    document_title: Optional[str] = None
    standard_number: Optional[str] = None
    clause_number: Optional[str] = None
    page_number: Optional[int] = Field(default=None, ge=1)
    excerpt: str
    version: Optional[str] = None
    source_url: Optional[HttpUrl] = None


class AssistantResponse(BaseModel):
    answer: str
    confidence: Confidence
    evidence_sufficient: bool
    citations: List[Citation] = Field(default_factory=list)
    related_standards: List[str] = Field(default_factory=list)
    unknowns: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    source_documents: List[str] = Field(default_factory=list)
