# Epic — Frontend UI

## Overview

Build the working HTML/CSS frontend for the KYC Identity Normalisation Flask application. Three tabs. Results appear inline below the input area on the same page via HTMX. If a backend feature is not yet implemented, show a clean notice rather than crashing.

This epic touches only frontend files. Do not modify any pipeline, normalisation, or database code.

---

## Implementation Todo Checklist (this run)

- [x] Replace frontend templates and stylesheet with full UI implementation
- [x] Add HTMX partial templates for upload, paste, review, and fallback notices
- [x] Add upload POST handler with graceful degradation
- [x] Add paste POST handler with graceful degradation
- [x] Add review queue/detail/submit/escalate endpoints with graceful degradation
- [x] Add context processor flag for native speaker tab visibility
- [x] Add minimal export endpoints for CSV/email fallback notices used by UI buttons
- [x] Add frontend route/HTMX tests for success and not-implemented paths
- [x] Run tests and confirm pass
- [ ] Run app locally on localhost:5001 for manual testing

---

## Files to create or modify

```
app/static/css/main.css              REPLACE — full CSS implementation
app/templates/base.html              REPLACE — nav + layout
app/templates/upload.html            REPLACE — Document tab
app/templates/paste.html             REPLACE — Sentence tab
app/templates/review.html            REPLACE — Review queue
app/templates/review_task.html       NEW — Single review task page
app/templates/partials/
  upload_results.html                NEW — HTMX partial: document results table
  paste_result.html                  NEW — HTMX partial: sentence result
  review_submitted.html              NEW — HTMX partial: confirmation after submit
  not_implemented.html               NEW — HTMX partial: graceful fallback notice
app/routes/upload.py                 MODIFY — add POST /upload/process endpoint
app/routes/paste.py                  MODIFY — add POST /paste/translate endpoint
app/routes/review.py                 MODIFY — add task list, task detail, submit endpoints
app/__init__.py                      MODIFY — add context processor for native speaker flag
```

---

## Design system

### Font
```css
font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
```
No other fonts. No Google Fonts. No icon libraries.

### Colour palette — strictly observed
| Role | Hex | Use |
|---|---|---|
| Accent / primary action | `#DA2128` | Active nav underline, primary button, review-required flag, form submit |
| Primary text | `#1A1A1A` | All body text, table content, labels |
| Secondary text | `#6B6B6B` | Metadata, method labels, hints, muted copy |
| Border | `#E0E0E0` | Table rules, card outlines, dividers |
| Page background | `#FFFFFF` | Full page |
| Surface | `#F7F7F7` | Table header row, input background, context blocks |

Red is an accent only. It must not appear as a background colour, a large block, or in decorative elements.

### Visual principles
- Generous whitespace. Sections breathe.
- Left-aligned throughout. No centred body content.
- No box shadows, no gradients, no border-radius above 3px.
- No icons, no emoji, no decorative elements of any kind.
- Typography hierarchy: page title (20px, weight 600) → section label (11px, weight 600, uppercase, letter-spacing 0.06em, `#6B6B6B`) → body (14px, weight 400) → metadata (12px, `#6B6B6B`).
- Tables: horizontal rules only. No vertical cell borders. No zebra striping. Header row uses surface background.
- Buttons: flat, no shadow. Primary = `#DA2128` + white text. Secondary = white + `#E0E0E0` border + `#1A1A1A` text.
- Tone: calm, corporate, editorial. Think consulting document, not product landing page.

---

## Navigation — `base.html`

Three tabs in the nav bar:
1. **Document** — always visible
2. **Sentence** — always visible
3. **Review** — visible only when `current_user_is_native_speaker` is `True`

Active tab is indicated by a `#DA2128` underline on the tab text. No background fill on active state.

The brand name on the left: `KYC Normalisation` — plain text, uppercase, small, weight 600.

### Context processor — `app/__init__.py`

Add inside `create_app()` after blueprint registration:

```python
@app.context_processor
def inject_user_flags():
    """
    Injects is_native_speaker flag into all templates.
    Until Entra ID SSO is wired (Epic 12), falls back to True so
    all tabs are visible during development.
    Reads from the users table once that table exists (Epic 06).
    """
    try:
        from app.models.user import User
        # TODO Epic 12: replace with session-based current user lookup
        user = User.query.filter_by(is_native_speaker=True).first()
        return {"current_user_is_native_speaker": user is not None}
    except Exception:
        return {"current_user_is_native_speaker": True}
```

---

## Tab 1 — Document Normalisation (`/upload/`)

### Purpose
Analyst uploads a document, selects document type and optional language hint, receives a table of extracted and normalised KYC fields below.

### `upload.html` — what to build
- Page title: `Document Normalisation`
- Short description (one line): uploaded documents are processed and all KYC fields extracted and normalised to English.
- File input area: a dashed-border rectangular zone the analyst can click or drag a file onto. On file selected, show the filename inside the zone. Accepted: pdf, jpg, jpeg, png, tiff, docx, txt. Max 50 MB enforced server-side.
- Two dropdowns side by side: Document type (options: Auto-detect, National ID, Driver's Licence, Passport, Company Registry — Local, Company Registry — Foreign, Business Registration, Articles of Association, Financial Statement, Shareholder Table) and Language hint (Auto-detect plus all 24 languages listed in the language list below).
- Primary action button: `Extract and Normalise` — full width, `#DA2128`.
- Spinner shown during HTMX request (htmx-indicator pattern).
- Results area `<div id="upload-results">` below the form. Empty on page load. HTMX swaps in `upload_results.html` partial on POST response.

### POST `/upload/process` — `upload.py`

```python
@upload_bp.route("/process", methods=["POST"])
def process():
    """
    Receives uploaded file and form fields.
    Attempts to call the orchestrator. Returns HTMX partial HTML.
    Handles gracefully if orchestrator not yet implemented.
    """
    # 1. Validate file presence and extension
    # 2. Save to UPLOAD_FOLDER with uuid filename
    # 3. Try: from app.pipeline.orchestrator import process_document_file
    #         results = process_document_file(path, doc_type, language)
    #         return render_template("partials/upload_results.html", results=results, ...)
    # 4. Except ImportError / NotImplementedError:
    #         return render_template("partials/not_implemented.html",
    #                                feature="Document processing pipeline (Epic 10)")
    # 5. Except any other Exception as e:
    #         return inline error notice, 400
```

### `partials/upload_results.html` — what to build

Show two lines of document-level metadata above the table:
- `Document type detected:` value
- `Language detected:` value

Then a table with these columns in this order:

| Field | Original | Normalised | Language | Method | Confidence | Status |
|---|---|---|---|---|---|---|

- **Field** — field type label, title-cased, underscores replaced with spaces.
- **Original** — raw extracted text in its original script. Apply `dir="auto"` so Arabic/Hebrew render RTL correctly.
- **Normalised** — the normalised English form. Monospace font. If empty (pending review), show an em dash.
- **Language** — ISO 639-1 code detected for this field.
- **Method** — processing strategy label (PRESERVE, CALENDAR, VOCABULARY, GEOGRAPHIC, REPOSITORY, TRANSLITERATION, CHARACTER_MAP, NMT, NATIVE_SPEAKER). Render as a small pill: `#F7F7F7` background, `#E0E0E0` border, `#6B6B6B` text, 11px.
- **Confidence** — as a percentage, e.g. `95%`. Colour `#6B6B6B`.
- **Status** — if `review_required` is True: show `Awaiting review` in `#DA2128`, 12px. Otherwise: empty cell. No positive indicator — keep visual noise low.

If a result row has `allowed_variants` (non-empty list), show them as a small line directly below the normalised form cell: `Variants: FORM ONE · FORM TWO` — 11px, `#6B6B6B`.

Below the table, two buttons:
- `Download CSV` — secondary button. GET to `/export/csv`. Returns not_implemented partial if not yet built.
- `Email to me` — secondary button. POST via HTMX to `/export/email`. Shows inline confirmation when done.

---

## Tab 2 — Sentence Normalisation (`/paste/`)

### Purpose
Analyst pastes a short piece of text (max 2,000 characters), selects what type of information it is and optionally the language, receives the normalised result below.

### `paste.html` — what to build
- Page title: `Sentence Normalisation`
- Short description: paste a name, address, company name, date, or short phrase. The tool normalises it to English. Maximum 2,000 characters.
- Large textarea with `dir="auto"`. Character counter below right-aligned: `0 / 2,000`. Updates on every keystroke.
- Two dropdowns side by side: Field type (see field type list below) and Language hint (Auto-detect + all 24 languages).
- Primary action button: `Normalise` — full width, `#DA2128`.
- Result area `<div id="paste-result">` below. Empty on page load. HTMX swaps in `paste_result.html` partial.

### Field type dropdown options
```
Person name
Company / entity name
Address
Date
Nationality / country
Legal form
Company status
Role / designation
Nature of business
Issuing authority
Other
```

### POST `/paste/translate` — `paste.py`

```python
@paste_bp.route("/translate", methods=["POST"])
def translate():
    """
    Receives pasted text, field type, language.
    Routes through normalisation router. Returns HTMX partial HTML.
    """
    # 1. Validate: text not empty, len <= 2000
    # 2. Try: from app.pipeline.normalisation.router import route_field
    #         result = route_field({"original_text": text, "field_type": field_type,
    #                               "language": language})
    #         return render_template("partials/paste_result.html",
    #                                result=result, original=text, field_type=field_type)
    # 3. Except ImportError / NotImplementedError:
    #         return render_template("partials/not_implemented.html",
    #                                feature="Normalisation router (Epic 10)")
    # 4. Except Exception as e:
    #         return inline error notice, 400
```

### `partials/paste_result.html` — what to build

A horizontal rule above to visually separate result from input.

Two stacked rows in a two-column layout (label left 120px, value right):

```
Original      [original text — dir="auto", 15px, #6B6B6B]
Normalised    [normalised form — monospace, 15px, weight 600, #1A1A1A]
```

If `allowed_variants` is non-empty, add a third row:
```
Variants      [variant 1 · variant 2 · variant 3 — 12px, #6B6B6B]
```

Below the rows, one line of metadata in 12px `#6B6B6B`:
`Method: [METHOD] · Confidence: [XX%] · Language: [code]`

If `review_required` is True, show below the metadata in `#DA2128`, 13px:
`Awaiting native speaker review`

And a secondary button: `Escalate to review queue` — POSTs to `/review/escalate-paste` with `original_text`, `field_type`, `normalised_suggestion`. On response, swaps a small confirmation into `<div id="escalate-confirm">`.

---

## Tab 3 — Human Review (`/review/`)

Visible only when `current_user_is_native_speaker` is True in the template context.

### `review.html` — task queue

- Page title: `Review Queue`
- Short description: fields that could not be resolved automatically are listed for your review.
- If no tasks: `No pending tasks.` — 14px, `#6B6B6B`.
- If tasks: a flat list, each task as a row with a bottom border:
  - Left: field type (11px, uppercase, `#6B6B6B`) → original text (16px, `dir="auto"`) → date assigned (12px, `#6B6B6B`)
  - Right: `Review` — secondary button → `/review/<task_id>`

### GET `/review/` — `review.py`

```python
@review_bp.route("/", methods=["GET"])
def index():
    try:
        from app.models.review import ReviewTask
        tasks = ReviewTask.query.filter_by(status="pending").order_by(
            ReviewTask.assigned_at.asc()
        ).all()
        return render_template("review.html", tasks=tasks)
    except Exception:
        return render_template("review.html", tasks=[])
```

### `review_task.html` — single task page

- Back link to queue at top.
- Page title: `Review: [field type label, title-cased]`

**Context block** — surface background `#F7F7F7`, 1px border `#E0E0E0`, 1.25rem padding. Two-column grid layout (label 140px, value rest). Rows:

```
Field type      [value]
Language        [ISO code]
Reason          [review_reason text]
Original text   [value — dir="auto", 16px]
Raw text        [full extracted text from document — dir="auto", 13px, #6B6B6B,
                 scrollable if long, max-height 180px, overflow-y: auto]
```

If `suggested_form` exists (Phase 2 only): add row `Suggested form` with the value in monospace.

**Form below the context block:**
- Label: `Confirmed normalised form (uppercase)`
- Text input, monospace, 15px. Pre-filled with `suggested_form` if present, otherwise empty.
- Label: `Allowed variants (comma-separated, optional)`
- Text input, empty.
- Two buttons side by side:
  - `Confirm and save` — primary, `#DA2128`. Submits form via HTMX POST to `/review/<task_id>/submit`.
  - `Approve as suggested` — secondary. Only shown if `suggested_form` exists. Submits with the suggested form pre-filled.
- `<div id="review-confirm">` below buttons. HTMX swaps in `review_submitted.html` on response.

### POST `/review/<int:task_id>/submit` — `review.py`

```python
@review_bp.route("/<int:task_id>/submit", methods=["POST"])
def submit(task_id):
    """
    Save native speaker confirmation. Write to verified repository.
    Returns HTMX partial confirmation.
    """
    # 1. Load ReviewTask by task_id or 404
    # 2. confirmed_form = request.form.get("confirmed_form", "").strip().upper()
    # 3. variants = [v.strip() for v in request.form.get("allowed_variants","").split(",") if v.strip()]
    # 4. task.confirmed_form = confirmed_form
    #    task.confirmed_variants = variants
    #    task.status = "approved" if confirmed_form == (task.suggested_form or "") else "corrected"
    #    task.reviewed_at = datetime.utcnow()
    # 5. Try: from app.pipeline.normalisation.repository_lookup import RepositoryLookupService
    #         repo.store_verified(task.original_text, task.language_code, task.field_type,
    #                             confirmed_form, variants,
    #                             processing_method=task.suggested_form and "LLM" or "UNRESOLVED",
    #                             verified_by_user_id=1)  # TODO Epic 12: real user id
    # 6. db.session.commit()
    # 7. return render_template("partials/review_submitted.html", task=task)
    # 8. Except repository not yet available: commit task status, note repo write pending in response
```

### POST `/review/escalate-paste` — `review.py`

```python
@review_bp.route("/escalate-paste", methods=["POST"])
def escalate_paste():
    """
    Creates a ReviewTask from a paste tab escalation.
    Returns small inline confirmation partial.
    """
    # Try to create ReviewTask. If model not available, return not_implemented partial.
    # Fields: original_text, field_type, language, suggested_form (from form)
    # status = "pending", assigned_to = None (Epic 07 wires assignment)
```

### `partials/review_submitted.html` — what to build

A calm confirmation notice — left border 3px `#E0E0E0`, surface background, no red:

```
Translation confirmed as [confirmed_form in monospace].
Written to verified repository.
← Back to queue   [link to /review/]
```

---

## `partials/not_implemented.html`

Left border 3px `#E0E0E0`. Surface background `#F7F7F7`. 13px, `#6B6B6B`. No red. Calm.

```
This feature is not yet available: {{ feature }}.
It will appear here automatically once the relevant pipeline step is complete.
```

---

## Language list (for both dropdowns)

```
Auto-detect        (empty value "")
Arabic             ar
Belarusian         be
Bulgarian          bg
Chinese            zh
Danish             da
Dutch              nl
English            en
Farsi / Persian    fa
French             fr
German             de
Greek              el
Hebrew             he
Italian            it
Japanese           ja
Korean             ko
Norwegian          no
Polish             pl
Portuguese         pt
Russian            ru
Spanish            es
Swedish            sv
Thai               th
Turkish            tr
Ukrainian          uk
```

---

## Graceful degradation — required on every route

Every route that calls a pipeline function must follow this exact pattern. No exceptions.

```python
try:
    # call pipeline function
    return render_template("partials/...", ...)
except (ImportError, NotImplementedError):
    return render_template("partials/not_implemented.html", feature="..."), 200
except Exception as e:
    return f'<p style="color:#DA2128;font-size:13px">Error: {e}</p>', 400
```

The `not_implemented.html` partial is always returned with HTTP 200 so HTMX swaps it in correctly.

---

## Acceptance criteria

- All three tab pages load with HTTP 200 and real UI — not "Placeholder".
- Active tab shows `#DA2128` underline. Inactive tabs have no underline or highlight.
- Review tab is hidden from the nav when `current_user_is_native_speaker` is False.
- Submitting a file on the Document tab shows either a results table or the not-implemented notice. Never a 500.
- Submitting text on the Sentence tab shows either a result or the not-implemented notice. Never a 500.
- Arabic and Hebrew text in Original cells renders right-to-left correctly via `dir="auto"`.
- Character counter on the Sentence textarea updates on every keystroke.
- The review task form pre-fills the confirmed form input with `suggested_form` if one exists.
- On review submit, the confirmation partial swaps in without a page reload.
- No JavaScript frameworks. No CSS frameworks. No Google Fonts. No icon libraries.
- All CSS custom properties defined in `:root` in `main.css`. No inline styles in templates.
