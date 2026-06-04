"""Dataset loading helpers for the anonymized FinVault release."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator, Optional


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = PACKAGE_ROOT / "sandbox"

DATASET_NAMES = {
    "attack_datasets",
    "normal_datasets",
    "attack_datasets_synthesis",
}


def iter_dataset_files(dataset: Optional[str] = None) -> Iterator[Path]:
    """Yield JSON dataset files in stable order."""
    if dataset is not None and dataset not in DATASET_NAMES:
        raise ValueError(f"unknown dataset: {dataset}")

    roots = [DATA_ROOT / dataset] if dataset else [DATA_ROOT / name for name in sorted(DATASET_NAMES)]
    for root in roots:
        if root.exists():
            yield from sorted(root.rglob("*.json"))


def load_json(path: Path) -> dict:
    """Load a JSON object from a dataset file."""
    with Path(path).open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def list_scenarios(dataset: str = "attack_datasets", attack_type: Optional[str] = None) -> list[str]:
    """List two-digit scenario identifiers available in a dataset directory."""
    base = DATA_ROOT / dataset
    if attack_type:
        base = base / attack_type
    if not base.exists():
        return []

    scenario_ids: list[str] = []
    for path in sorted(base.glob("scenario_*_*.json")):
        parts = path.stem.split("_")
        if len(parts) >= 2 and parts[1].isdigit():
            scenario_ids.append(parts[1])
    return sorted(set(scenario_ids))


def load_scenario(
    scenario_id: str,
    dataset: str = "attack_datasets",
    attack_type: Optional[str] = None,
) -> dict:
    """Load one scenario from attack, normal, or synthesized datasets."""
    if dataset not in DATASET_NAMES:
        raise ValueError(f"unknown dataset: {dataset}")
    if not scenario_id.isdigit() or len(scenario_id) != 2:
        raise ValueError("scenario_id must be a two-digit string")

    if dataset == "normal_datasets":
        filename = f"scenario_{scenario_id}_normal.json"
        path = DATA_ROOT / dataset / filename
    else:
        filename = f"scenario_{scenario_id}_attacks.json"
        path = DATA_ROOT / dataset / filename
        if dataset == "attack_datasets_synthesis":
            if not attack_type:
                raise ValueError("attack_type is required for synthesized datasets")
            path = DATA_ROOT / dataset / attack_type / filename

    if not path.exists():
        raise FileNotFoundError(path)
    return load_json(path)
