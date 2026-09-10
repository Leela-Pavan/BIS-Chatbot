import json
from pathlib import Path
from typing import List, Union

from app.evaluation.models import EvaluationCase


def load_evaluation_cases(path: Union[str, Path]) -> List[EvaluationCase]:
    cases: List[EvaluationCase] = []
    with Path(path).open("r", encoding="utf-8") as dataset_file:
        for line_number, line in enumerate(dataset_file, start=1):
            if not line.strip():
                continue
            try:
                cases.append(EvaluationCase.model_validate(json.loads(line)))
            except (json.JSONDecodeError, ValueError) as error:
                raise ValueError(f"invalid evaluation case on line {line_number}") from error
    if not cases:
        raise ValueError("evaluation dataset must contain at least one case")
    return cases
