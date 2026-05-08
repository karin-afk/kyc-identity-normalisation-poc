# Frontend UI (Epic 00-1)

## Scope delivered

- Replaced placeholder templates with a three-tab interface: Document, Sentence, and Review.
- Added HTMX-driven inline result rendering for upload and paste workflows.
- Added graceful fallback partial rendering for not-yet-implemented backend pipeline steps.
- Added review queue/detail/submit/escalation endpoints with fallback behavior while review models are pending.
- Added CSV and email export fallback endpoints to support UI controls.
- Added context processor flag wiring for conditional Review tab visibility.

## Routes added or updated

- `POST /upload/process`
- `POST /paste/translate`
- `GET /review/`
- `GET /review/<task_id>`
- `POST /review/<task_id>/submit`
- `POST /review/escalate-paste`
- `GET /export/csv`
- `POST /export/email`

## Frontend behavior notes

- All POST handlers use the same graceful degradation pattern:
  - Try pipeline/model call.
  - Return `partials/not_implemented.html` with HTTP 200 for ImportError/NotImplementedError.
  - Return inline HTTP 400 error for unexpected exceptions.
- Sentence tab includes live character counting up to 2,000 characters.
- Original-script values are rendered with `dir="auto"` for RTL/LTR compatibility.

## Test coverage

Added frontend integration tests in `tests/test_frontend_ui_epic.py` that verify:

- tab pages return HTTP 200
- active tab classes render correctly
- Review tab can be hidden when `current_user_is_native_speaker` is false
- upload/paste/review/export HTMX endpoints return non-500 fallback responses

## Validation command

```bash
pytest -q tests/test_frontend_ui_epic.py tests/test_epic00_integration_flask_routes.py
```

Latest result: `15 passed`.
