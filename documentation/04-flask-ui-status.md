# Flask UI Status (Epic 00)

## Summary

The project now includes a Flask UI skeleton under `app/` with an application factory (`create_app`) and placeholder blueprints for:

- `/upload/`
- `/paste/`
- `/review/`
- `/admin/`
- `/export/`

Root (`/`) redirects to `/upload/`.

## Active UI Direction

Flask is now the active UI direction for ongoing epics.

Streamlit is considered **off for forward development** and is no longer the primary UI path for new features. The legacy `app.py` file remains in the repository temporarily for rollback/reference during migration, but new work should target the Flask app structure in `app/`.

## How to run Flask locally

1. Install dependencies:
   - `python -m pip install -r requirements.txt`
2. Ensure environment values are available (at minimum `SECRET_KEY` for non-testing mode).
3. Start Flask:
   - `python run.py`
   - or `flask run`

## Validation completed in this epic

- Unit tests for app factory/config passed.
- Integration tests for placeholder routes passed.
- Data contract/import tests for `app.pipeline.normalisation.*` modules passed.
- Deterministic legacy `src/` tests (`test_rules.py`, `test_transliteration.py`) still pass.
