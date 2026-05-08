# Flask Application and Frontend UI

**Status: IMPLEMENTED** — Epics 00-0 (Flask skeleton) and 00-1 (Frontend UI). Branches `feature/epic-frontend-ui` (commit `66b193f`).

---

## Flask application structure

The project runs on Flask under `app/` with an application factory pattern (`create_app`). Blueprints registered at startup:

| Blueprint | Prefix | Status |
|-----------|--------|--------|
| `upload`  | `/upload/` | Implemented |
| `paste`   | `/paste/`  | Implemented |
| `review`  | `/review/` | Implemented |
| `admin`   | `/admin/`  | Placeholder |
| `export`  | `/export/` | Fallback stubs |

Root (`/`) redirects to `/upload/`.

Streamlit (`app.py`) is **off for forward development** and retained only for rollback reference. All new work targets the Flask structure in `app/`.

---

## How to run locally

```bash
# From kyc-identity-normalisation-poc/
python -m pip install -r requirements.txt
# Ensure .env contains at minimum: SECRET_KEY=<value>
python run.py
# or: flask --app app:create_app run --port 5001
```

Server starts on `http://127.0.0.1:5001` by default.

---

## Frontend UI — three tabs

### Tab 1 — Document Normalisation (`/upload/`)

- File upload area (drag-and-drop or click). Accepts PDF, JPG, PNG, TIFF, DOCX, TXT, max 50 MB.
- Document type dropdown: Auto-detect, National ID, Driver's Licence, Passport, Company Registry (Local/Foreign), Business Registration, Articles of Association, Financial Statement, Shareholder Table.
- Language hint dropdown: Auto-detect + 24 languages.
- `POST /upload/process` — validates and saves file, calls `process_document_file()`, renders result table or not-implemented notice.
- Results render inline via HTMX into `<div id="upload-results">`. Currently shows not-implemented notice (document pipeline is Epic 11).

### Tab 2 — Sentence Normalisation (`/paste/`)

- Textarea with `dir="auto"` (RTL/LTR aware), 2,000-character limit with live counter.
- Field type dropdown: **Auto-detect** (added in orchestrator epic), Person name, Company/entity name, Address, Date, Nationality/country, Legal form, Company status, Role/designation, Nature of business, Issuing authority, Other.
- Language hint dropdown: Auto-detect + 24 languages.
- `POST /paste/translate` — routes text through normalisation router. Returns result or not-implemented partial.
- Auto-detect mode: calls `field_type_detector.detect_field_type()` before routing; detected type and confidence shown in result.
- Preserve fields (passport numbers, IDs, emails, etc.) return immediately with `PRESERVE` method and 100% confidence.
- Non-preserve fields currently return `UNRESOLVED` with `review_required=True` pending Strategies B–I.

### Tab 3 — Human Review (`/review/`)

- Conditionally visible: only shown when `current_user_is_native_speaker` is `True` (context processor in `app/__init__.py`; defaults to `True` during development).
- Review queue lists pending tasks. `/review/<task_id>` shows detail with original text, reason, and confirmation form.
- `POST /review/<task_id>/submit` — saves confirmed form and variants, updates task status.
- `POST /review/escalate-paste` — creates a review task from the Sentence tab escalation button.
- All review endpoints degrade gracefully while database models are pending.

---

## Design system in use

- **Font**: Helvetica Neue / Arial — no web fonts.
- **Accent colour**: `#DA2128` (active nav underline, primary button, review flags). No red backgrounds.
- **Text**: `#1A1A1A` primary, `#6B6B6B` secondary/metadata.
- **Surface**: `#F7F7F7` table headers, context blocks, method pills.
- **Border**: `#E0E0E0`.
- HTMX for all form submissions — results swap inline, no full page reload.
- No JavaScript frameworks, no CSS frameworks, no icon libraries.

---

## HTMX partials

| Partial | Triggered by |
|---------|-------------|
| `partials/upload_results.html` | `POST /upload/process` success |
| `partials/paste_result.html`   | `POST /paste/translate` success |
| `partials/review_submitted.html` | `POST /review/<id>/submit` success |
| `partials/not_implemented.html` | Any pipeline step not yet built |

---

## Graceful degradation pattern

Every route that calls a pipeline function follows this pattern — no exceptions:

```python
try:
    result = pipeline_function(...)
    return render_template("partials/...", result=result)
except (ImportError, NotImplementedError):
    return render_template("partials/not_implemented.html", feature="..."), 200
except Exception as e:
    return f'<p class="notice notice-flag">Error: {e}</p>', 400
```

The `not_implemented.html` partial always returns HTTP 200 so HTMX swaps it correctly.

---

## Test coverage

| Test file | Covers | Count |
|-----------|--------|-------|
| `tests/test_epic00_integration_flask_routes.py` | Blueprint route smoke tests | — |
| `tests/test_frontend_ui_epic.py` | Tab rendering, HTMX endpoints, graceful degradation | 15 passed |

Validation command:

```bash
pytest -q tests/test_frontend_ui_epic.py tests/test_epic00_integration_flask_routes.py
```
