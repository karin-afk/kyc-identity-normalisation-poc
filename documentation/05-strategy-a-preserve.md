# Strategy A Preserve (Epic 1-A)

## Scope

Strategy A preserves strict identifier fields exactly as extracted.

No transliteration, translation, Unicode normalisation, or format conversion is applied.

## Included field types

The preserve list is defined in [app/pipeline/normalisation/field_types.py](app/pipeline/normalisation/field_types.py).

Included identifiers:
- Identity: passport_no, id_no, id_number, licence_no, document_number
- Company: registration_no, company_no, commercial_registration_no
- Financial identifiers: reference_no, tax_id, vat_number
- Contact: email

## Important decision

Financial numeric values are not preserved in Strategy A.

They are explicitly separated into FINANCIAL_NUMERIC_FIELDS and are intended for Strategy B numeric formatting, where representation can be normalised while preserving numeric value.

## How to test

1. Run Strategy A tests:
- `pytest -q tests/test_strategy_a_preserve.py`

2. Optional full Epic tests:
- `pytest -q tests/test_epic00_unit_flask_skeleton.py tests/test_epic00_integration_flask_routes.py tests/test_epic00_data_contracts.py`

## UI status

The Flask UI currently provides scaffold pages. Strategy routing is not yet wired to a user-facing form.

You can still launch and verify UI availability:
- `set SECRET_KEY=dev-secret` (PowerShell: `$env:SECRET_KEY='dev-secret'`)
- `set PORT=50001` (PowerShell: `$env:PORT='50001'`)
- `python run.py`

Then open http://localhost:50001
