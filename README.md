# FinVault

FinVault is an anonymized benchmark release for evaluating financial agent safety in execution-grounded sandbox environments. It contains the experiment code, scenario environments, attack and normal datasets, synthesized attack datasets, and local integrity/privacy checks needed to inspect and reproduce the benchmark workflow.

This repository intentionally excludes private working notes, paper source files, generated logs, model outputs, API keys, `.env` files, and original non-anonymized data.

## Repository Layout

```text
sandbox/
  attack_datasets/               # anonymized attack cases
  normal_datasets/               # anonymized normal business cases
  attack_datasets_synthesis/     # anonymized synthesized attack cases
  sandbox_00 ... sandbox_30/     # execution-grounded financial environments
  base/                          # shared agent, environment, and tool abstractions
  defense/                       # safety detector integrations
  attack_testing/                # LLM-agent test harness
  config/                        # public placeholder configuration
  prompts/                       # scenario prompt templates
  run_attack_test.py             # main attack evaluation entrypoint
  run_llama_guard3_test.py       # Llama Guard 3 evaluation
  run_llama_guard4_test.py       # Llama Guard 4 evaluation
  run_gpt_oss_safeguard_test.py  # GPT-OSS-Safeguard evaluation
  defense_evaluation.py          # defense comparison utilities
finvault_dataset/                # dataset loading, validation, and privacy helpers
scripts/check_release.py         # local release integrity and privacy scan
tests/test_release_integrity.py  # unittest-based release checks
```

## Installation

```bash
pip install -r requirements.txt
```

The evaluation scripts use API-compatible model providers. Configure keys through environment variables or local untracked config files only. Do not commit `.env` files.

## Quick Checks

Run these checks before using or redistributing the release:

```bash
python scripts/check_release.py
python -m unittest discover -s tests
python -m py_compile sandbox/run_attack_test.py sandbox/run_llama_guard3_test.py sandbox/run_llama_guard4_test.py sandbox/run_gpt_oss_safeguard_test.py sandbox/defense_evaluation.py
```

## Running Evaluations

From the repository root:

```bash
cd sandbox
python run_attack_test.py --scenario 00
python run_attack_test.py --all --concurrency 8
python run_llama_guard3_test.py --scenario 00
python run_llama_guard4_test.py --scenario 00
python run_gpt_oss_safeguard_test.py --scenario 00
```

Configuration lives in `sandbox/config/agents_config.yaml`. Public configuration values are placeholders; provide real credentials through local environment variables or ignored files.

## Dataset Access

```python
from finvault_dataset.loader import load_scenario

attack_scenario = load_scenario("00", dataset="attack_datasets")
normal_scenario = load_scenario("00", dataset="normal_datasets")
synth_scenario = load_scenario(
    "00",
    dataset="attack_datasets_synthesis",
    attack_type="authority_impersonation",
)
```

See `DATASET_CARD.md` for the anonymization and release scope.
