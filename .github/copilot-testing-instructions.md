# Testing Instructions for GitHub Copilot

This file defines how tests must be written for the KYC Identity Normalisation project.
Copilot must follow these instructions for every test it writes, modifies, or extends.

---

## The one rule that overrides everything else

**Tests must verify actual behaviour. They must not mock the thing being tested.**

The failure mode to avoid: a test that passes by replacing the real implementation with a
fake return value, then asserting on that fake value. This is not a test. It is a lie that
hides broken code.

If Copilot is uncertain whether a test is real, apply this check:

> If I deleted the production code this test is supposed to cover, would the test still pass?

If yes — the test is wrong. Rewrite it.

---

## The three questions every test must answer before being written

1. What **real input** am I giving the system? A real string in the original script. A real
   HTTP POST with real form field names. A real file path. Not a mock return value.

2. What **exact output** do I expect? A specific normalised form. A specific string in HTML
   that can only be there if the real code ran. Not just HTTP 200.

3. If this test fails, does it mean **something is broken in production**? If no — do not
   write the test.

---

## Test categories

### Category 1 — Strategy unit tests

One file per strategy (A through H). Each file tests the normalisation strategy with real
inputs and asserts on exact outputs. No mocks. No monkeypatching.

**File naming:** `tests/test_strategy_a_preserve.py`, `tests/test_strategy_b_calendar.py`, etc.

**Rules:**
- Call `route_field()` or `process_field_row()` directly with a real input dict.
- Assert on the exact `normalised_form` string, `processing_method` label, and `confidence`.
- If the strategy module raises `NotImplementedError`, the test must **fail** — not skip.
  A failing test on an unbuilt strategy is the correct signal that work remains. A skipped
  or mocked test on an unbuilt strategy is a false certificate of completion.
- Minimum 5 real input/output pairs per language the strategy supports.

**Correct example:**
```python
def test_strategy_a_passport_verbatim():
    result = route_field({"original_text": "TK1234567", "field_type": "passport_no"})
    assert result["normalised_form"] == "TK1234567"
    assert result["processing_method"] == "PRESERVE"
    assert result["confidence"] == 1.0
    assert result["review_required"] is False

def test_strategy_b_thai_buddhist_date():
    result = route_field({"original_text": "2568/5/8", "field_type": "date_of_birth", "language": "th"})
    assert result["normalised_form"] == "2025-05-08"
    assert result["processing_method"] == "CALENDAR"
    assert result["original_calendar"] == "thai_buddhist"

def test_strategy_c_legal_form_japanese_suffix_match():
    result = route_field({"original_text": "三菱商事株式会社", "field_type": "legal_form", "country": "JP"})
    assert result["normalised_form"] == "KK"
    assert result["processing_method"] == "VOCABULARY"

def test_strategy_c_status_active_arabic():
    result = route_field({"original_text": "نشط", "field_type": "status", "language": "ar"})
    assert result["normalised_form"] == "ACTIVE"
    assert result["processing_method"] == "VOCABULARY"
```

**Prohibited example — do not write this:**
```python
# WRONG — mocking the function being tested
@patch("app.pipeline.normalisation.calendar_rules.apply_calendar_rules")
def test_strategy_b_mocked(mock_cal):
    mock_cal.return_value = {"normalised_form": "2025-05-08", "processing_method": "CALENDAR"}
    result = route_field({"original_text": "2568/5/8", "field_type": "date_of_birth"})
    assert result["normalised_form"] == "2025-05-08"
# This test passes even if calendar_rules.py is completely empty.
```

---

### Category 2 — Route integration tests

**File naming:** `tests/test_routes_paste.py`, `tests/test_routes_upload.py`, `tests/test_routes_review.py`

These test the Flask routes with real HTTP requests. External APIs (OpenAI, Azure Document
Intelligence, Azure Translator) may be monkeypatched at the API call boundary only — not at
the business logic level.

**Critical rule on form field names:** Before writing any route test that POSTs data, check
the actual HTML template for the exact `name` attribute of the input element. The form field
name in `data={}` must match the template exactly. A mismatch causes the route to receive
an empty string — the page renders nothing, the test passes because it only checks HTTP 200,
and the bug is invisible.

The paste textarea uses `name="original_text"` (verified in `app/templates/paste_sentence.html`).
The route reads `request.form.get("original_text", ...)`. All paste route tests must POST
`data={"original_text": "..."}` — not `data={"text": "..."}`.  

**Mandatory paste tab tests — these must exist and pass:**

```python
def test_paste_form_field_name_is_original_text(client):
    """
    Verifies the paste template uses name='original_text'.
    If this fails, the form field name has changed and all POST tests must be updated.
    """
    html = client.get("/paste/").get_data(as_text=True)
    assert 'name="original_text"' in html, (
        "Paste textarea must have name='original_text'. "
        "If the template changed, update all route POST tests to match."
    )

def test_paste_translate_preserve_field_real_result(client, monkeypatch):
    """
    Posts a real passport number. Monkeypatches only the OpenAI call.
    The router, preserve strategy, and template rendering are all real.
    Asserts on content that can ONLY appear if the real router ran.
    """
    from app.pipeline.normalisation import field_type_detector
    monkeypatch.setattr(
        field_type_detector, "detect_field_type",
        lambda text, language="": ("passport_no", 0.99, "en")
    )
    response = client.post("/paste/translate", data={"original_text": "TK1234567"})
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "TK1234567" in html, "Normalised form not rendered — router or template broken"
    assert "PRESERVE" in html, "Processing method not rendered — router or template broken"
    assert "Language:" in html
    assert "Field type:" in html

def test_paste_translate_strategy_b_calendar_real_result(client, monkeypatch):
    """Strategy B must actually run and convert the date. Not mocked."""
    from app.pipeline.normalisation import field_type_detector
    monkeypatch.setattr(
        field_type_detector, "detect_field_type",
        lambda text, language="": ("date_of_birth", 0.95, "th")
    )
    response = client.post("/paste/translate", data={"original_text": "2568/5/8"})
    html = response.get_data(as_text=True)
    assert "2025-05-08" in html, "Thai date not converted — Strategy B not wired into router"
    assert "CALENDAR" in html

def test_paste_translate_strategy_c_vocabulary_real_result(client, monkeypatch):
    """Strategy C must actually run and resolve the legal form. Not mocked."""
    from app.pipeline.normalisation import field_type_detector
    monkeypatch.setattr(
        field_type_detector, "detect_field_type",
        lambda text, language="": ("legal_form", 0.97, "de")
    )
    response = client.post("/paste/translate", data={"original_text": "GmbH"})
    html = response.get_data(as_text=True)
    assert "GMBH" in html, "Legal form not resolved — Strategy C not wired or JSON not loaded"
    assert "VOCABULARY" in html

def test_paste_translate_unresolved_shows_review_notice(client, monkeypatch):
    """An Arabic name that cannot be resolved must show 'Awaiting review', not crash."""
    from app.pipeline.normalisation import field_type_detector
    monkeypatch.setattr(
        field_type_detector, "detect_field_type",
        lambda text, language="": ("person_name", 0.90, "ar")
    )
    response = client.post("/paste/translate", data={"original_text": "محمد عبد الله"})
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Awaiting" in html or "review" in html.lower(), (
        "Unresolved field must show review notice, not a blank page or error"
    )
```

**Prohibited — do not write this:**
```python
# WRONG — only checks HTTP status, tells us nothing about the result
def test_paste_works(client):
    response = client.post("/paste/translate", data={"original_text": "anything"})
    assert response.status_code == 200
# This passes even if the route returns a completely blank page.

# WRONG — wrong field name ('text' is not the textarea name attribute)
def test_paste_translate_passport_wrong_name(client):
    response = client.post("/paste/translate", data={"text": "TK1234567"})
    assert response.status_code == 200
# Route receives empty string (original_text not found). Test passes. Bug is invisible.
```

---

### Category 3 — End-to-end pipeline tests (no mocks at all)

**File:** `tests/test_e2e_pipeline.py`

Call `process_field_row()` directly with real data. Assert on exact values. Zero mocks.

**Mandatory tests — must all exist and pass for each implemented strategy:**

```python
# Strategy A
def test_e2e_passport_preserved():
    r = process_field_row({"original_text": "TK1234567", "field_type": "passport_no", "language": "en"})
    assert r["normalised_form"] == "TK1234567" and r["processing_method"] == "PRESERVE"

def test_e2e_arabic_indic_id_not_converted():
    """Arabic-Indic digits in an ID must pass through unchanged — digit conversion is Strategy B."""
    r = process_field_row({"original_text": "١٢٣٤٥٦٧", "field_type": "id_no", "language": "ar"})
    assert r["normalised_form"] == "١٢٣٤٥٦٧"

# Strategy B — calendar
def test_e2e_thai_date_converted():
    r = process_field_row({"original_text": "2568/5/8", "field_type": "date_of_birth", "language": "th"})
    assert r["normalised_form"] == "2025-05-08" and r["processing_method"] == "CALENDAR"

def test_e2e_minguo_date_converted():
    r = process_field_row({"original_text": "114/5/8", "field_type": "date_of_birth", "country": "TW"})
    assert r["normalised_form"] == "2025-05-08" and r["processing_method"] == "CALENDAR"

def test_e2e_reiwa_era_converted():
    r = process_field_row({"original_text": "令和5年7月3日", "field_type": "date_of_birth", "language": "ja"})
    assert r["normalised_form"] == "2023-07-03" and r["processing_method"] == "CALENDAR"

def test_e2e_hijri_date_converted():
    r = process_field_row({"original_text": "١٤٤٥/٠٩/٠١", "field_type": "date_of_birth", "language": "ar"})
    assert r["normalised_form"] == "2024-03-11" and r["processing_method"] == "CALENDAR"

# Strategy B — numeric
def test_e2e_japanese_negative_triangle():
    r = process_field_row({"original_text": "△4,191", "field_type": "total_assets", "language": "ja"})
    assert r["normalised_form"] == "-4191" and r["processing_method"] == "NUMERIC"

def test_e2e_european_number_format():
    r = process_field_row({"original_text": "1.234.567,89", "field_type": "total_assets", "language": "de"})
    assert r["normalised_form"] == "1234567.89" and r["processing_method"] == "NUMERIC"

# Strategy C
def test_e2e_legal_form_de():
    r = process_field_row({"original_text": "GmbH", "field_type": "legal_form", "language": "de", "country": "DE"})
    assert r["normalised_form"] == "GMBH" and r["processing_method"] == "VOCABULARY"

def test_e2e_legal_form_jp():
    r = process_field_row({"original_text": "株式会社", "field_type": "legal_form", "language": "ja", "country": "JP"})
    assert r["normalised_form"] == "KK" and r["processing_method"] == "VOCABULARY"

def test_e2e_legal_form_ru():
    r = process_field_row({"original_text": "ООО", "field_type": "legal_form", "language": "ru", "country": "RU"})
    assert r["normalised_form"] == "LLC" and r["processing_method"] == "VOCABULARY"

def test_e2e_status_active_japanese():
    r = process_field_row({"original_text": "現役", "field_type": "status", "language": "ja"})
    assert r["normalised_form"] == "ACTIVE" and r["processing_method"] == "VOCABULARY"

def test_e2e_status_dissolved_arabic():
    r = process_field_row({"original_text": "منتهي", "field_type": "status", "language": "ar"})
    assert r["normalised_form"] == "DISSOLVED" and r["processing_method"] == "VOCABULARY"

def test_e2e_role_director_japanese():
    r = process_field_row({"original_text": "取締役", "field_type": "role", "language": "ja"})
    assert r["normalised_form"] == "DIRECTOR" and r["processing_method"] == "VOCABULARY"

# Unresolved — must route cleanly to review, not crash
def test_e2e_arabic_name_unresolved_routes_to_review():
    r = process_field_row({"original_text": "محمد عبد الله", "field_type": "person_name", "language": "ar"})
    assert r["processing_method"] == "UNRESOLVED"
    assert r["review_required"] is True
    assert r["normalised_form"] is None
    assert r["should_use_in_screening"] is False
    assert r["review_reason"] is not None
```

---

### Category 4 — Data integrity tests

**File:** `tests/test_data_integrity.py`

Load JSON files from disk and validate every value against its allowed canonical set.
No application code involved. These run even when the Flask app is not importable.

```python
TABLES = Path("data/lookup_tables")  # repo-root data dir — NOT app/data/lookup_tables (that dir does not exist)

STATUS_CANONICAL  = {"ACTIVE","INACTIVE","DISSOLVED","SUSPENDED","IN_LIQUIDATION","STRUCK_OFF","DORMANT"}
SHARE_CANONICAL   = {"ORDINARY","PREFERENCE","REDEEMABLE","NON-VOTING","MANAGEMENT"}
CAPITAL_CANONICAL = {"INCREASE","DECREASE","CONVERSION","SPLIT","CONSOLIDATION"}
DOC_TYPE_CANONICAL = {"national_id","drivers_licence","passport","company_registry_local",
                       "company_registry_foreign","business_registration","aoa",
                       "financial_statement","shareholder_table","unknown"}

def test_all_lookup_tables_exist_and_are_non_empty():
    required = ["legal_forms.json","status_terms.json","role_titles.json",
                "share_classes.json","capital_change_types.json",
                "street_types.json","industry_codes.json"]
    for f in required:
        path = TABLES / f
        assert path.exists(), f"Missing: {f}"
        data = json.loads(path.read_text("utf-8"))
        assert isinstance(data, dict) and len(data) > 1, f"Empty or trivial: {f}"

def test_status_terms_all_values_canonical():
    data = json.loads((TABLES / "status_terms.json").read_text("utf-8"))
    for lang, terms in data.items():
        if lang.startswith("_"): continue
        for term, value in terms.items():
            assert value in STATUS_CANONICAL, f"status_terms.json: '{value}' invalid (lang={lang}, term={term})"

def test_share_classes_all_values_canonical():
    data = json.loads((TABLES / "share_classes.json").read_text("utf-8"))
    for lang, terms in data.items():
        if lang.startswith("_"): continue
        for term, value in terms.items():
            assert value in SHARE_CANONICAL, f"share_classes.json: '{value}' invalid (lang={lang})"

def test_capital_change_types_all_values_canonical():
    data = json.loads((TABLES / "capital_change_types.json").read_text("utf-8"))
    for lang, terms in data.items():
        if lang.startswith("_"): continue
        for term, value in terms.items():
            assert value in CAPITAL_CANONICAL, f"capital_change_types.json: '{value}' invalid (lang={lang})"

def test_legal_forms_country_codes_are_two_chars():
    data = json.loads((TABLES / "legal_forms.json").read_text("utf-8"))
    for code in data:
        if code.startswith("_"): continue
        assert len(code) == 2, f"legal_forms.json: country code '{code}' is not ISO 3166-1 alpha-2"
```

---

### Category 5 — Regression gate

The existing `data/golden_dataset.csv` runs on every commit via CI. No mocks. Accuracy must
not drop below baseline for any strategy or language. CI fails if it does.

---

## Explicitly prohibited patterns

These patterns must never appear in any test file. If Copilot generates them, delete and rewrite.

```python
# 1. Mocking the business logic being tested
@patch("app.pipeline.normalisation.router.route_field")
def test_x(mock): ...

# 2. Posting with the wrong form field name (template uses original_text, not text)
client.post("/paste/translate", data={"text": "value"})
# Must be: data={"original_text": "value"}

# 3. Asserting only on HTTP status
assert response.status_code == 200
# Must also assert on specific content in the response body

# 4. Asserting on string presence without verifying it comes from real data
assert "PRESERVE" in html
# Only acceptable if the test does NOT mock the router or strategy

# 5. Testing that an attribute exists rather than that it works
assert hasattr(module, "apply_calendar_rules")
# This passes even if the function raises NotImplementedError
```

---

## How to handle unbuilt strategies

When a strategy is not yet implemented, its test must **fail**, not skip or pass.
Write the test as if it is built. When the strategy is built, the test will pass.
This is how the test suite communicates what remains to be built.

```python
def test_strategy_f_russian_transliteration():
    """Fails until Strategy F is implemented. That is correct."""
    r = route_field({"original_text": "Наталья", "field_type": "person_name", "language": "ru"})
    assert r["processing_method"] == "TRANSLITERATION", (
        f"Strategy F not yet implemented — got {r['processing_method']}"
    )
    assert "NATALYA" in r["normalised_form"]
```

---

## Test file structure

```
tests/
  conftest.py                        # path bootstrap — do not modify
  test_strategy_a_preserve.py        # real input/output, no mocks
  test_strategy_b_calendar.py        # real input/output, no mocks
  test_strategy_b_numeric.py         # real input/output, no mocks
  test_strategy_c_vocabulary.py      # real input/output, no mocks
  test_data_integrity.py             # JSON files on disk, no app code
  test_e2e_pipeline.py               # process_field_row(), zero mocks
  test_routes_paste.py               # real HTTP POST, real form field names
  test_routes_upload.py              # real HTTP POST, real form field names
  test_routes_review.py              # real HTTP GET/POST
  test_pipeline.py                   # existing src/ tests — do not modify
  test_rules.py                      # existing rules engine — do not modify
  test_transliteration.py            # existing transliteration — do not modify
  test_evaluator.py                  # regression gate — do not modify
```
