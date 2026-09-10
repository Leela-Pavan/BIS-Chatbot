from typing import Literal

from pydantic import BaseModel, Field

EvaluationCategory = Literal[
    "standard_identification",
    "product_mapping",
    "certification",
    "testing",
    "laboratory",
    "hallmarking",
    "clause_lookup",
    "unsupported",
]
EvaluationLanguage = Literal["en", "hi", "te"]


class EvaluationCase(BaseModel):
    case_id: str = Field(min_length=1)
    category: EvaluationCategory
    language: EvaluationLanguage
    question: str = Field(min_length=3)
    expected_behavior: str = Field(min_length=1)
    requires_official_evidence: bool
