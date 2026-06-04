"""Tests for the anonymized FinVault release."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from finvault_dataset.loader import DATA_ROOT, iter_dataset_files, list_scenarios
from finvault_dataset.privacy import scan_text
from finvault_dataset.validation import validate_dataset_file


ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".json", ".md", ".py", ".toml", ".txt", ".yaml", ".yml", ".sh"}
EXCLUDED_DIR_NAMES = {".git", "__pycache__", "logs", "results"}


class ReleaseIntegrityTests(unittest.TestCase):
    def test_dataset_file_counts(self) -> None:
        self.assertEqual(len(list((DATA_ROOT / "attack_datasets").glob("*.json"))), 31)
        self.assertEqual(len(list((DATA_ROOT / "normal_datasets").glob("*.json"))), 31)
        synthesis_files = list((DATA_ROOT / "attack_datasets_synthesis").rglob("*.json"))
        self.assertEqual(len(synthesis_files), 248)
        self.assertEqual(len(list(iter_dataset_files())), 310)

    def test_scenarios_are_complete(self) -> None:
        expected = [f"{i:02d}" for i in range(31)]
        self.assertEqual(list_scenarios("attack_datasets"), expected)
        self.assertEqual(list_scenarios("normal_datasets"), expected)

    def test_json_files_are_structurally_valid(self) -> None:
        for path in iter_dataset_files():
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertEqual(validate_dataset_file(path), [])

    def test_packaged_text_has_no_common_secret_or_pii_patterns(self) -> None:
        for path in sorted(ROOT.rglob("*")):
            if (
                not path.is_file()
                or path.suffix.lower() not in TEXT_SUFFIXES
                or any(part in EXCLUDED_DIR_NAMES for part in path.parts)
            ):
                continue
            with self.subTest(path=path.relative_to(ROOT)):
                text = path.read_text(encoding="utf-8")
                self.assertEqual(scan_text(text), [])

    def test_anonymization_summary_does_not_store_source_values(self) -> None:
        summary_path = ROOT / "anonymization_summary.json"
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        self.assertEqual(summary["exported_json_files"], 310)
        self.assertIn("anonymization_replacement_counts", summary)
        self.assertNotIn("mapping", json.dumps(summary).lower())


if __name__ == "__main__":
    unittest.main()
