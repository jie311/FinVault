"""Structural validation for the anonymous dataset files."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .loader import load_json


SCENARIO_ID_RE = re.compile(r"^\d{2}$")


def _require_string(obj: dict[str, Any], key: str, errors: list[str]) -> None:
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"missing or invalid string field: {key}")


def _validate_case_list(dataset: dict[str, Any], errors: list[str]) -> None:
    case_key = (
        "attacks"
        if "attacks" in dataset
        else "queries"
        if "queries" in dataset
        else "scenarios"
        if "scenarios" in dataset
        else "attack_cases"
        if "attack_cases" in dataset
        else None
    )
    if case_key is None:
        errors.append("dataset must include either attacks or queries")
        return

    cases = dataset.get(case_key)
    if not isinstance(cases, list) or not cases:
        errors.append(f"{case_key} must be a non-empty list")
        return

    seen_ids: set[str] = set()
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            errors.append(f"{case_key}[{index}] must be an object")
            continue

        case_id = case.get("id") or case.get("case_id")
        if not isinstance(case_id, str) or not case_id.strip():
            errors.append(f"{case_key}[{index}] must include id or case_id")
        elif case_id in seen_ids:
            errors.append(f"duplicate case id: {case_id}")
        else:
            seen_ids.add(case_id)

        prompt = case.get("attack_prompt") or case.get("query_prompt") or case.get("attack_input")
        if not isinstance(prompt, str) or not prompt.strip():
            errors.append(f"{case_id or case_key + '[' + str(index) + ']'} must include a prompt")


def validate_dataset_object(dataset: dict[str, Any]) -> list[str]:
    """Validate one loaded dataset object and return human-readable errors."""
    errors: list[str] = []
    _require_string(dataset, "scenario_name", errors)

    scenario_id = dataset.get("scenario_id")
    if not isinstance(scenario_id, (str, int)):
        errors.append("missing or invalid scenario_id field")
    elif not SCENARIO_ID_RE.fullmatch(f"{int(scenario_id):02d}" if isinstance(scenario_id, int) else scenario_id):
        errors.append("scenario_id must be a two-digit string or integer in range 00-99")

    vulnerabilities = dataset.get("vulnerabilities")
    if vulnerabilities is not None and not isinstance(vulnerabilities, dict):
        errors.append("vulnerabilities must be an object when present")

    _validate_case_list(dataset, errors)
    return errors


def validate_dataset_file(path: Path) -> list[str]:
    """Validate one dataset file."""
    return validate_dataset_object(load_json(path))
