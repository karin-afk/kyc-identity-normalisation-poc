# Epic — Minimal Normalisation Router and Orchestrator

**Status: IMPLEMENTED** — branch `feature/epic-04-1-orchestrator-minimal`, commit `5f7f595`, 61 tests passed.

## Implementation assessment (this run)

Status: agreed with minor practical adjustments so this integrates cleanly with the current Flask UI.

- Keep `src/` untouched and import Strategy A from `src/pipeline/rules_engine.py`.
- Implement router stubs for B-I that always fall through to `UNRESOLVED`.
- Implement minimal orchestrator with `process_field_row()` and document stub raising `NotImplementedError`.
- Add deterministic field type detector for paste tab when `field_type=auto`.
- Update paste route to support both `original_text` (current UI) and `text` (epic snippet).
- Update paste result partial to read both legacy/new key names (`normalised_form` and `normalized_text`, `confidence` and `confidence_score`).
- Update sentence field type selector to include an explicit `Auto-detect` option.
- Keep upload flow behavior unchanged: `process_document_file()` raises and route renders not-implemented partial.

## Execution todo checklist (this run)

- [x] Replace `app/pipeline/normalisation/router.py` with minimal Strategy A router
- [x] Replace `app/pipeline/orchestrator.py` with minimal orchestrator
- [x] Add `app/pipeline/normalisation/field_type_detector.py`
- [x] Update `app/routes/paste.py` to wire auto-detect and orchestrator
- [x] Update sentence UI selector with `Auto-detect`
- [x] Update paste result partial to display auto-detect metadata and new key mapping
- [x] Add `tests/test_router.py`
- [x] Update frontend tests impacted by non-placeholder paste behavior
- [x] Run pytest for router + impacted frontend tests
- [x] Redeploy Flask app on `http://127.0.0.1:5001`

## Goal

Wire up the router and orchestrator so the paste tab and document tab in the UI can call them and receive real results for Strategy A (Preserve) fields. All other strategies are stubbed — the router falls through to an UNRESOLVED result for anything that isn't a preserve field. This is enough to test the full UI flow end to end.

---

## What exists

**Strategy A is implemented in `src/pipeline/rules_engine.py`** as `apply_rules()`. It handles `passport_no`, `id_no`, and `email` — returning them verbatim with `processing_method: "RULE"` and `confidence: 1.0`.

**The Flask `app/` package exists** with placeholder modules at every path. The paste route (`POST /paste/translate`) and upload route (`POST /upload/process`) are already wired to call `app.pipeline.normalisation.router.route_field()` and `app.pipeline.orchestrator.process_document_file()` respectively — but both modules are currently empty placeholders.

**Do not touch anything in `src/`.** It must keep working.

---

## Files to implement

### 1. `app/pipeline/normalisation/router.py` — REPLACE placeholder

```python
"""
Normalisation router — Strategy A only (Phase 1, minimal implementation).

Routes a field row through the normalisation strategy chain.
Currently only Strategy A (Preserve) is implemented. All other strategies
return None and the field falls through to UNRESOLVED with review_required=True.

As each strategy epic is completed, replace the stub call with a real import.
"""

import sys
import os

# Make src/ importable so Strategy A can reuse the existing rules engine
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))


PRESERVE_FIELDS = [
    "passport_no", "id_no", "id_number", "email",
    "registration_no", "company_no", "commercial_registration_no",
    "reference_no", "tax_id", "vat_number", "document_number",
    "licence_no",
    # Financial numeric values — preserved verbatim, format only normalised by Strategy B
    "number_of_shares", "voting_rights", "ownership_percentage",
    "share_capital", "number_of_issued_shares",
    "total_assets", "total_liabilities", "net_assets", "revenue", "expenses",
]


def route_field(row: dict) -> dict:
    """
    Route a single field through strategies A–I in order.

    Returns the first successful result. If nothing resolves the field,
    returns an UNRESOLVED result with review_required=True.

    Args:
        row: dict containing at minimum:
             - original_text (str)
             - field_type    (str)
             - language      (str, optional)
             - country       (str, optional)

    Returns:
        Result dict with keys: original_text, normalised_form, allowed_variants,
        processing_method, confidence, review_required, review_reason,
        should_use_in_screening.
    """
    text       = row.get("original_text", "")
    field_type = row.get("field_type", "")
    language   = row.get("language", "")
    country    = row.get("country", "")

    if not text or not field_type:
        return _unresolved(text, field_type, language,
                           reason="Missing original_text or field_type")

    # ── Strategy A — Preserve ────────────────────────────────────────────────
    result = _try_strategy_a(text, field_type)
    if result:
        return result

    # ── Strategy B — Calendar / numeric rules ────────────────────────────────
    # Stub — implemented in Epic 02
    result = _try_stub("B", "calendar_rules")
    if result:
        return result

    # ── Strategy C — Vocabulary lookup ───────────────────────────────────────
    # Stub — implemented in Epic 03
    result = _try_stub("C", "vocabulary_lookup")
    if result:
        return result

    # ── Strategy D — Geographic lookup ───────────────────────────────────────
    # Stub — implemented in Epic 04
    result = _try_stub("D", "geographic_lookup")
    if result:
        return result

    # ── Strategy E — Verified repository ─────────────────────────────────────
    # Stub — implemented in Epic 05
    result = _try_stub("E", "repository_lookup")
    if result:
        return result

    # ── Strategy F — Transliteration libraries ───────────────────────────────
    # Stub — implemented in Epic 06
    result = _try_stub("F", "transliteration")
    if result:
        return result

    # ── Strategy G — Character mapping tables ────────────────────────────────
    # Stub — implemented in Epic 07
    result = _try_stub("G", "character_map_normaliser")
    if result:
        return result

    # ── Strategy H — Azure NMT ───────────────────────────────────────────────
    # Stub — implemented in Epic 08
    result = _try_stub("H", "nmt_translator")
    if result:
        return result

    # ── Strategy I — LLM (Phase 2 only) ──────────────────────────────────────
    # Only called when LLM_ENABLED=true — see .env
    llm_enabled = os.environ.get("LLM_ENABLED", "false").lower() == "true"
    if llm_enabled:
        result = _try_stub("I", "llm_normalise")
        if result:
            return result

    # ── Nothing resolved — route to native speaker review ────────────────────
    return _unresolved(text, field_type, language)


# ── Strategy A implementation ─────────────────────────────────────────────────

def _try_strategy_a(text: str, field_type: str) -> dict | None:
    """
    Call Strategy A (Preserve) from the existing src pipeline.
    Returns result dict if field_type is a preserve field, else None.
    """
    if field_type not in PRESERVE_FIELDS:
        return None
    try:
        from pipeline.rules_engine import apply_rules
        result = apply_rules(field_type, text)
        if result:
            # Normalise processing_method label to PRESERVE
            # (src uses "RULE" — the new system uses "PRESERVE")
            result["processing_method"] = "PRESERVE"
            return result
    except Exception:
        pass

    # Direct fallback if src import fails for any reason
    return {
        "original_text":             text,
        "normalised_form":           text,
        "allowed_variants":          [],
        "processing_method":         "PRESERVE",
        "confidence":                1.0,
        "review_required":           False,
        "review_reason":             None,
        "should_use_in_screening":   True,
        "latin_transliteration":     None,
        "analyst_english_rendering": text,
    }


# ── Stub helper ───────────────────────────────────────────────────────────────

def _try_stub(strategy_letter: str, module_name: str) -> None:
    """
    Placeholder for strategies not yet implemented.
    Always returns None so the router falls through to the next strategy.
    When a strategy is implemented, replace this call with a real import.
    """
    return None


# ── Unresolved fallback ───────────────────────────────────────────────────────

def _unresolved(text: str, field_type: str, language: str,
                reason: str | None = None) -> dict:
    """
    Called when no strategy resolves the field.
    The result enters the native speaker review queue.
    """
    return {
        "original_text":             text,
        "normalised_form":           None,
        "allowed_variants":          [],
        "processing_method":         "UNRESOLVED",
        "confidence":                0.0,
        "review_required":           True,
        "review_reason":             reason or (
            f"No strategy resolved field_type='{field_type}' "
            f"language='{language}' — awaiting native speaker review"
        ),
        "should_use_in_screening":   False,
        "latin_transliteration":     None,
        "analyst_english_rendering": None,
    }
```

---

### 2. `app/pipeline/orchestrator.py` — REPLACE placeholder

```python
"""
Pipeline orchestrator — minimal implementation.

Coordinates the full pipeline for a single input.
Currently: receives a row dict, passes it to the router, returns the result.
Document Intelligence ingestion, OCR, and page segmentation are stubbed.
These will be wired in when Epic 11 (document pipeline) is implemented.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


def process_field_row(row: dict) -> dict:
    """
    Process a single pre-extracted field row through the normalisation router.

    This is the entry point for the paste tab, which supplies text, field_type,
    and language directly — no OCR or document extraction needed.

    Args:
        row: dict with original_text, field_type, language, country (optional)

    Returns:
        Result dict from the normalisation router.
    """
    from app.pipeline.normalisation.router import route_field
    return route_field(row)


def process_document_file(file_path: str, doc_type: str, language: str) -> list[dict]:
    """
    Full document pipeline: OCR → field extraction → normalisation.

    Currently a stub — Document Intelligence ingestion is implemented in Epic 11.
    Returns a single placeholder result so the UI renders something meaningful.

    Args:
        file_path: Absolute path to the uploaded file.
        doc_type:  Document type selected by analyst (or "auto").
        language:  Language hint selected by analyst (or "" for auto-detect).

    Returns:
        List of result dicts, one per extracted field.
    """
    raise NotImplementedError(
        "Document processing pipeline not yet implemented (Epic 11). "
        "The UI will show a 'not yet available' notice."
    )
```

---

### 3. `app/pipeline/normalisation/field_type_detector.py` — NEW FILE

```python
"""
Field type auto-detector for the paste tab.

When the analyst selects "Auto-detect" for field type, this module
applies deterministic heuristics to guess the most likely field type
from the text content. No AI involved.

Used only by the paste tab route. The document upload route derives
field types from Document Intelligence output, not from this module.
"""

import re
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))


def detect_field_type(text: str, language: str = "") -> tuple[str, float]:
    """
    Infer the most likely KYC field type from pasted text.

    Applies heuristics in priority order. Returns the first match.
    If nothing matches, returns ("unstructured_text", 0.5).

    Args:
        text:     The pasted text, stripped.
        language: ISO 639-1 language code if known, else "".

    Returns:
        Tuple of (field_type: str, confidence: float).
        confidence is between 0.5 (low, uncertain) and 0.95 (high, clear match).
    """
    text_stripped = text.strip()

    # 1. Looks like an email address
    if re.match(r"^[\w._%+\-]+@[\w.\-]+\.[a-zA-Z]{2,}$", text_stripped):
        return ("email", 0.95)

    # 2. Looks like a document / ID number
    # Alphanumeric, 6–20 chars, may contain hyphens — no spaces
    if re.match(r"^[A-Z0-9][A-Z0-9\-]{5,19}$", text_stripped.upper()) and " " not in text_stripped:
        return ("id_number", 0.85)

    # 3. Looks like a date
    date_patterns = [
        r"\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}",   # DD/MM/YYYY or MM/DD/YYYY
        r"\d{4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2}",       # YYYY-MM-DD
        r"[٠-٩]{1,2}[\/\-\.][٠-٩]{1,2}[\/\-\.][٠-٩]{2,4}",  # Arabic-Indic digits
        r"令和|平成|昭和|大正|明治",                        # Japanese era names
        r"\d{1,2}\s+\w+\s+\d{4}",                      # 12 March 2023
    ]
    for pattern in date_patterns:
        if re.search(pattern, text_stripped):
            return ("date_of_birth", 0.85)

    # 4. Short text (1–4 space-separated tokens), no sentence structure
    # → likely a name or company name
    tokens = text_stripped.split()
    if 1 <= len(tokens) <= 4 and not _has_sentence_structure(text_stripped):
        # If it ends with a known Latin-script legal form suffix → company name
        latin_legal_suffixes = {
            "llc", "ltd", "inc", "corp", "plc", "gmbh", "sarl", "sas", "sa",
            "bv", "nv", "ag", "kg", "oy", "ab", "as", "srl", "spa",
        }
        last_token = tokens[-1].lower().rstrip(".")
        if last_token in latin_legal_suffixes:
            return ("company_name", 0.90)

        # Otherwise likely a person name
        return ("person_name", 0.80)

    # 5. Contains street-type keywords → address
    street_keywords = [
        "street", "road", "avenue", "boulevard", "lane", "drive", "place",
        "rue", "via", "calle", "strasse", "straße", "ulica", "улица",
        "شارع", "طريق", "通り", "路", "街", "로",
    ]
    lower_text = text_stripped.lower()
    if any(kw in lower_text for kw in street_keywords):
        return ("address", 0.85)

    # 6. Longer text with sentence structure → nature of business or unstructured
    if len(tokens) > 8 or _has_sentence_structure(text_stripped):
        return ("nature_of_business", 0.60)

    # 7. Fallback
    return ("unstructured_text", 0.50)


def _has_sentence_structure(text: str) -> bool:
    """
    Returns True if the text appears to be a sentence or clause
    rather than a name or code — based on punctuation and length.
    """
    has_verb_indicators = bool(re.search(r"\b(is|are|was|were|has|have|the|and|of|in)\b", text, re.I))
    has_punctuation = bool(re.search(r"[,;:।。、]", text))
    return has_verb_indicators or has_punctuation
```

---

### 4. Update `app/routes/paste.py` — use field type detector

In the `POST /paste/translate` endpoint, when `field_type == "auto"`, call the detector before routing:

```python
@paste_bp.route("/translate", methods=["POST"])
def translate():
    text       = request.form.get("text", "").strip()
    field_type = request.form.get("field_type", "auto")
    language   = request.form.get("language", "")

    if not text:
        return '<p class="notice notice-flag">Please enter some text.</p>', 400
    if len(text) > 2000:
        return '<p class="notice notice-flag">Text exceeds 2,000 characters. Please upload as a file instead.</p>', 400

    detected_field_type  = None
    field_type_confidence = None

    if field_type == "auto":
        from app.pipeline.normalisation.field_type_detector import detect_field_type
        detected_field_type, field_type_confidence = detect_field_type(text, language)
        field_type = detected_field_type

    try:
        from app.pipeline.orchestrator import process_field_row
        result = process_field_row({
            "original_text": text,
            "field_type":    field_type,
            "language":      language,
        })
        if detected_field_type:
            result["detected_field_type"]    = detected_field_type
            result["field_type_confidence"]  = field_type_confidence

        return render_template("partials/paste_result.html",
                               result=result,
                               original=text,
                               field_type=field_type,
                               detected_field_type=detected_field_type,
                               field_type_confidence=field_type_confidence)

    except (ImportError, NotImplementedError):
        return render_template("partials/not_implemented.html",
                               feature="Normalisation router"), 200
    except Exception as e:
        return f'<p class="notice notice-flag">Error: {e}</p>', 400
```

When `detected_field_type` is set, the `paste_result.html` partial shows a line below the result:
`Field type auto-detected as: Person name (80% confidence) — resubmit with a specific type selected if incorrect.`

---

## Tests

`tests/test_router.py` — NEW FILE

```python
"""Tests for the normalisation router — Strategy A only."""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app.pipeline.normalisation.router import route_field


# ── Strategy A — preserve fields ─────────────────────────────────────────────

@pytest.mark.parametrize("field_type,value", [
    ("passport_no",    "TK1234567"),
    ("id_no",          "987654321"),
    ("email",          "john.doe@example.com"),
    ("registration_no","DE123456789"),
    ("company_no",     "SC123456"),
    ("tax_id",         "GB123456789"),
])
def test_preserve_fields_returned_verbatim(field_type, value):
    result = route_field({"original_text": value, "field_type": field_type})
    assert result["normalised_form"] == value
    assert result["processing_method"] == "PRESERVE"
    assert result["confidence"] == 1.0
    assert result["review_required"] is False
    assert result["allowed_variants"] == []
    assert result["should_use_in_screening"] is True


def test_preserve_arabic_indic_digits_not_converted():
    """Preserve fields must not convert digit scripts — that is Strategy B's job."""
    result = route_field({"original_text": "١٢٣٤٥٦٧", "field_type": "id_no"})
    assert result["normalised_form"] == "١٢٣٤٥٦٧"


def test_preserve_full_width_digits_not_converted():
    result = route_field({"original_text": "Ａ１２３４５", "field_type": "passport_no"})
    assert result["normalised_form"] == "Ａ１２３４５"


def test_preserve_empty_string():
    result = route_field({"original_text": "", "field_type": "passport_no"})
    assert result["normalised_form"] == ""
    assert result["processing_method"] == "PRESERVE"


# ── Non-preserve fields → UNRESOLVED (strategies B–I not yet built) ──────────

@pytest.mark.parametrize("field_type", [
    "person_name", "company_name", "address", "date_of_birth",
    "legal_form", "status", "nationality",
])
def test_unresolved_for_non_preserve_fields(field_type):
    result = route_field({"original_text": "Some text", "field_type": field_type})
    assert result["processing_method"] == "UNRESOLVED"
    assert result["review_required"] is True
    assert result["normalised_form"] is None
    assert result["should_use_in_screening"] is False


# ── Field type detector ───────────────────────────────────────────────────────

from app.pipeline.normalisation.field_type_detector import detect_field_type

def test_detect_email():
    ft, conf = detect_field_type("john.doe@example.com")
    assert ft == "email"
    assert conf >= 0.90

def test_detect_date_iso():
    ft, conf = detect_field_type("1985-03-12")
    assert ft == "date_of_birth"

def test_detect_date_japanese_era():
    ft, conf = detect_field_type("令和5年7月3日")
    assert ft == "date_of_birth"

def test_detect_person_name_short():
    ft, conf = detect_field_type("田中 太郎")
    assert ft == "person_name"

def test_detect_company_with_ltd():
    ft, conf = detect_field_type("Acme Corp Ltd")
    assert ft == "company_name"
    assert conf >= 0.85

def test_detect_address_street_keyword():
    ft, conf = detect_field_type("123 Main Street London")
    assert ft == "address"

def test_detect_fallback():
    ft, conf = detect_field_type("x")
    assert ft in ("person_name", "unstructured_text")


# ── Orchestrator ──────────────────────────────────────────────────────────────

from app.pipeline.orchestrator import process_field_row

def test_orchestrator_preserve():
    result = process_field_row({
        "original_text": "TK1234567",
        "field_type":    "passport_no",
        "language":      "en",
    })
    assert result["normalised_form"] == "TK1234567"
    assert result["processing_method"] == "PRESERVE"

def test_orchestrator_unresolved():
    result = process_field_row({
        "original_text": "محمد",
        "field_type":    "person_name",
        "language":      "ar",
    })
    assert result["processing_method"] == "UNRESOLVED"
    assert result["review_required"] is True

def test_orchestrator_document_file_raises_not_implemented():
    from app.pipeline.orchestrator import process_document_file
    with pytest.raises(NotImplementedError):
        process_document_file("/some/file.pdf", "auto", "")
```

---

## Acceptance criteria

- `pytest tests/test_router.py` passes with zero failures.
- All existing `src/` tests continue to pass — `pytest tests/test_rules.py tests/test_pipeline.py`.
- In the paste tab, entering `TK1234567` with field type `passport_no` shows: normalised form `TK1234567`, method `PRESERVE`, confidence `100%`, no review flag.
- In the paste tab, entering any non-preserve field (e.g. a Japanese name with field type `person_name`) shows the not-yet-available / awaiting review notice — not a 500 error.
- In the paste tab, selecting "Auto-detect" and entering `john.doe@example.com` detects `email` and returns the value preserved.
- `process_document_file()` raises `NotImplementedError`, which the upload route catches and renders the not-implemented partial — not a 500.
- `LLM_ENABLED=false` in `.env` — the LLM stub is never called.
