# FinVault Dataset Card

## Scope

This release contains anonymized FinVault benchmark data for financial agent safety evaluation:

- 31 attack dataset files
- 31 normal business dataset files
- 248 synthesized attack dataset files
- 31 execution-grounded sandbox environments
- evaluation and defense-testing code used by the benchmark workflow

## Anonymization

The release removes or replaces obvious private values, including person names, organization names, identity numbers, phone numbers, email addresses, customer identifiers, document identifiers, policy identifiers, employee identifiers, user identifiers, and case reference identifiers.

The original-to-placeholder mapping is not included because that mapping is sensitive.

## Excluded Content

This public package excludes original non-anonymized data, API keys, `.env` files, model outputs, execution logs, generated results, paper source files, PDFs, review materials, and private working notes.

## Validation

Run:

```bash
python scripts/check_release.py
python -m unittest discover -s tests
```

The checks validate dataset structure and scan packaged text for common secret and PII patterns.
