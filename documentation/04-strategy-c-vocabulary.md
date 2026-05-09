# 04 - Strategy C Vocabulary Lookup

## Scope

Strategy C introduces deterministic vocabulary lookup for normalising selected KYC field types using curated JSON dictionaries.

Supported field types:

- legal_form
- status
- role
- designation
- share_class
- capital_change_type
- industry_code
- document_type

## Runtime flow

Execution order in router:

1. Strategy B (calendar/numeric)
2. Strategy C (vocabulary lookup)
3. Strategy A (preserve)
4. unresolved fallback

## Service design

Implementation file:

- app/pipeline/normalisation/vocabulary_lookup.py

Key behavior:

- Loads required lookup JSONs once at app startup.
- Raises startup errors if a required lookup table is missing/invalid.
- Uses case-insensitive matching for language/categorical lookups.
- Adds exact/parent/child-prefix matching for industry codes.
- Returns standard normalisation payload with processing_method=VOCABULARY.

## App wiring

Flask startup now registers a singleton service:

- app/__init__.py

`create_app()` now calls `_register_services(app)`, which initializes `VocabularyLookupService` from:

- data/lookup_tables

## Lookup data completed

Completed/added files in data/lookup_tables:

- legal_forms.json
- status_terms.json
- role_titles.json
- street_types.json
- industry_codes.json
- issuing_authorities.json
- share_classes.json
- capital_change_types.json
- document_type_labels.json

Notes:

- `industry_codes.json` and `capital_change_types.json` were previously empty and are now valid JSON objects with starter content.
- `issuing_authorities.json` and `document_type_labels.json` were added.
- `document_type_labels.json` values now align to internal canonical labels:
  - national_id, drivers_licence, passport, company_registry_local, company_registry_foreign, business_registration, aoa, financial_statement, shareholder_table, unknown

## Tests

New/updated tests:

- tests/test_strategy_c_vocabulary.py (new)
- tests/test_router.py (updated with Strategy C routing test)

Additional validation:

- Canonical status values are validated against ALLOWED_STATUS_VALUES.
- Canonical document labels are validated against ALLOWED_DOCUMENT_TYPE_LABELS.

## Verified commands

Targeted tests run:

- pytest tests/test_strategy_c_vocabulary.py tests/test_router.py tests/test_epic00_data_contracts.py -q

Result:

- 41 passed

## Manual verification server

Flask is running on:

- http://127.0.0.1:5001

Terminal session:

- 13be355a-c0c1-45c6-a191-a4331b4ab3f3

Note:

- Startup requires SECRET_KEY in non-testing mode.

## Copy/paste examples for Sentence tab

Use these to verify Strategy C behavior quickly:

1. legal_form
- original_text: GmbH
- field_type: legal_form
- language: de
- country: DE
- expected normalised_form: GMBH
- expected processing_method: VOCABULARY

2. status
- original_text: Good Standing
- field_type: status
- language: en
- expected normalised_form: ACTIVE

3. role
- original_text: Director.
- field_type: role
- language: en
- expected normalised_form: DIRECTOR

4. capital_change_type
- original_text: 増資
- field_type: capital_change_type
- language: ja
- expected normalised_form: INCREASE

5. industry_code
- original_text: K64.19
- field_type: industry_code
- language: en
- expected normalised_form: Other monetary intermediation

6. document_type
- original_text: جواز سفر
- field_type: document_type
- language: ar
- expected normalised_form: passport

## Remaining close-out step

After your manual verification, update epic status in:

- prompts/todo/epic-01-strategy-c-vocabulary.md

from in-progress to IMPLEMENTED.
