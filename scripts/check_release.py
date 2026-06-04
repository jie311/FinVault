"""Run local integrity and privacy checks for this release."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from finvault_dataset.loader import iter_dataset_files
from finvault_dataset.privacy import scan_text
from finvault_dataset.validation import validate_dataset_file


TEXT_SUFFIXES = {".json", ".md", ".py", ".toml", ".txt", ".yaml", ".yml", ".sh"}
EXCLUDED_DIR_NAMES = {".git", "__pycache__", "logs", "results"}


def iter_text_files() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*")
        if path.is_file()
        and path.suffix.lower() in TEXT_SUFFIXES
        and not any(part in EXCLUDED_DIR_NAMES for part in path.parts)
    )


def main() -> int:
    errors: list[str] = []
    dataset_files = list(iter_dataset_files())

    if len(dataset_files) != 310:
        errors.append(f"expected 310 dataset JSON files, found {len(dataset_files)}")

    for path in dataset_files:
        for message in validate_dataset_file(path):
            errors.append(f"{path.relative_to(ROOT)}: {message}")

    for path in iter_text_files():
        text = path.read_text(encoding="utf-8")
        issues = scan_text(text)
        for issue in issues:
            errors.append(
                f"{path.relative_to(ROOT)}:{issue.line}: {issue.kind}: {issue.excerpt}"
            )

    if errors:
        print(json.dumps({"status": "failed", "errors": errors[:50]}, indent=2))
        return 1

    print(json.dumps({"status": "ok", "dataset_json_files": len(dataset_files)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
