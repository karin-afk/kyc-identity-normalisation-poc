# Strategy B — Calendar and Numeric Rules

Status: IMPLEMENTED

## Scope implemented

Strategy B is now wired into the Flask app pipeline for both:

- Calendar/date normalisation (`processing_method = CALENDAR`)
- Financial numeric normalisation (`processing_method = NUMERIC`)

The integration is active from sentence input (`/paste/translate`) through orchestrator and router.

## Key implementation files

- `app/pipeline/normalisation/calendar_rules.py`
- `app/pipeline/normalisation/router.py`
- `app/pipeline/orchestrator.py`
- `src/pipeline/calendar_solar_hijri.py`
- `src/pipeline/calendar_hebrew.py`
- `src/pipeline/calendar_offset.py`
- `src/pipeline/numeric_rules.py`
- `tests/test_strategy_b_calendar.py`

## Calendar capabilities

Implemented calendar handling includes:

- Hijri/Gregorian continuity from existing `src/utils/calendar_utils.py`
- Japanese era handling (existing logic preserved)
- Solar Hijri conversion (FA/PS/IR/AF contexts)
- Hebrew date conversion (HE context)
- Thai Buddhist Era conversion (TH context)
- Minguo conversion (TW context)

Accepted output is normalised to ISO date format where date precision is available.

## Numeric capabilities

Implemented numeric normalisation includes:

- Full-width digit conversion
- Devanagari digit conversion
- Thai digit conversion
- Arabic-Indic and Eastern Arabic-Indic digit conversion
- Parenthetical/triangle negative handling (`△`, full-width and ASCII parentheses)
- European/Swiss/English numeric separator normalisation
- Currency symbol extraction and ISO code mapping where applicable

## Router and orchestrator wiring

- Router now attempts Strategy B before Strategy A preserve fallback.
- `process_field_row` in orchestrator ensures row keys include `original_text`, `field_type`, `language`, and `country`.
- Non-Strategy-B field types continue to fall through existing routing behavior.

## UI updates relevant to Strategy B testing

Sentence field dropdown now includes Strategy B date and financial numeric field types, including:

- `date_of_birth`, `birth_date`, `issue_date`, `expiry_date`, `incorporation_date`, `document_date`, `registry_date`, `financial_period`
- `number_of_shares`, `voting_rights`, `ownership_percentage`, `share_capital`, `number_of_issued_shares`, `total_assets`, `total_liabilities`, `net_assets`, `revenue`, `expenses`

## Dependencies

`requirements.txt` includes:

- `convertdate>=2.4.0`

## Validation summary

Targeted strategy and regression tests were run:

- `tests/test_strategy_b_calendar.py`
- `tests/test_router.py`
- `tests/test_rules.py`
- `tests/test_transliteration.py`

Result: all passing in the final run.
