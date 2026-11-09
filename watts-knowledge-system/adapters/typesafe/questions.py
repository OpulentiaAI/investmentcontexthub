"""Question constructors and local request validation for TypeSafe."""

from __future__ import annotations

from typing import Any, Mapping


def noul(instructions: str, criteria: Mapping[str, str] | None = None) -> dict[str, Any]:
    question: dict[str, Any] = {"type": "noul", "instructions": instructions}
    if criteria is not None:
        question["criteria"] = dict(criteria)
    return question


def choice(instructions: str, criteria: Mapping[str, str]) -> dict[str, Any]:
    return {"type": "choice", "instructions": instructions, "criteria": dict(criteria)}


def score(instructions: str, criteria: list[str]) -> dict[str, Any]:
    return {"type": "score", "instructions": instructions, "criteria": list(criteria)}


def validate_questions(questions: Mapping[str, Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    """Validate and copy public API questions before they leave this process."""
    if not questions:
        raise ValueError("questions must not be empty")

    validated: dict[str, dict[str, Any]] = {}
    for question_id, question in questions.items():
        if not isinstance(question_id, str) or not question_id.strip():
            raise ValueError("question ids must be non-empty strings")
        if not isinstance(question, Mapping):
            raise ValueError(f"question {question_id!r} must be an object")
        question_type = question.get("type")
        instructions = question.get("instructions")
        if question_type not in {"noul", "choice", "score"}:
            raise ValueError(f"question {question_id!r} has unsupported type")
        if not isinstance(instructions, str) or not instructions.strip():
            raise ValueError(f"question {question_id!r} needs non-empty instructions")

        criteria = question.get("criteria")
        if question_type == "choice":
            if not isinstance(criteria, Mapping) or not criteria:
                raise ValueError(f"choice question {question_id!r} requires a criteria map")
        elif question_type == "score":
            if not isinstance(criteria, list) or len(criteria) < 2:
                raise ValueError(f"score question {question_id!r} requires at least two ordered criteria levels")
        elif criteria is not None:
            if not isinstance(criteria, Mapping) or set(criteria) != {"true", "false"}:
                raise ValueError(f"noul question {question_id!r} criteria must contain true and false")

        validated[question_id] = dict(question)
    return validated
