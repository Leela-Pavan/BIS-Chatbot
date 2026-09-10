from pathlib import Path

from app.evaluation.loader import load_evaluation_cases

DATASET = Path(__file__).parents[2] / "evaluation" / "questions.jsonl"


def test_synthetic_evaluation_dataset_is_valid() -> None:
    cases = load_evaluation_cases(DATASET)

    assert len(cases) == 8
    assert {case.category for case in cases} == {
        "standard_identification",
        "product_mapping",
        "certification",
        "testing",
        "laboratory",
        "hallmarking",
        "clause_lookup",
        "unsupported",
    }
    assert all(case.requires_official_evidence for case in cases)
