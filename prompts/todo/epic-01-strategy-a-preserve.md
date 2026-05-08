# Epic 01 — Normalisation Strategy A: Preserve

## What you need to provide

Nothing. Strategy A requires no data files, no downloads, and no lookup tables from you. It is a pure code change — a field type list and a function. Copilot builds it entirely.

---

# Answers to questions:
2. Financial values conflict — needs a decision now.
Copilot spotted a real ambiguity in the epic. The resolution is:

PRESERVE_FIELDS = identifiers that must never be touched at all (passport numbers, registration numbers, email). Period.
Financial numeric fields (number_of_shares, total_assets etc.) should be removed from PRESERVE_FIELDS and placed in a separate FINANCIAL_NUMERIC_FIELDS list. Strategy B handles them — format normalisation only (digit scripts, separators), value never changes.

The distinction matters because Strategy B's apply_numeric_rules() needs to receive them explicitly, not have them silently bypass the router via Preserve.
3. Processing method labels as stable contract — agreed. Once defined in Epic 01 they must not be renamed. Audit log and dashboard depend on them.
4. Backward compatibility — important. The src/ pipeline must keep working until Epic 04 (router) migrates everything. The new app/ modules run in parallel, not as replacements, until the cutover.
5. LLM label forward-compatibility — already handled by LLM_ENABLED=false in .env. The label exists in code, the switch controls whether it is ever reached at runtime.

---------------------

## What exists in the current codebase

`src/config/rules.py` contains `PRESERVE_FIELDS` with three entries: `passport_no`, `id_no`, `email`.

`src/pipeline/rules_engine.py` contains `apply_rules()` which checks if a field type is in `PRESERVE_FIELDS` and returns it verbatim.

Both are correct and working. This epic extends them to cover the full KYC field set and moves them into the new Flask app structure.

---

## What this epic does

Extends the preserve list to cover all structured identifiers in the full KYC field set, moves the code into the new app structure, and adds the `ProcessingMethod` constants class used by all subsequent epics.

---

## Files to create or modify

### 1. `app/pipeline/normalisation/field_types.py` — NEW FILE

This file is the single source of truth for all field type classifications used by the normalisation router. Every subsequent epic (B through I) imports from here.

```python
"""
Field type classifications for the KYC normalisation pipeline.

Every field extracted from a document is assigned a field_type string.
This module maps those strings to the normalisation strategy that should
be applied. The router in Epic 4 reads these constants to make routing
decisions.

Add new field types here as new document types are supported. Never
hardcode field type strings anywhere else in the codebase.
"""


# ---------------------------------------------------------------------------
# Strategy A — Preserve
# Returned exactly as extracted. Never sent to any API or library.
# Never altered, uppercased, or modified in any way.
# ---------------------------------------------------------------------------

PRESERVE_FIELDS: list[str] = [
    # Identity document identifiers
    "passport_no",
    "id_no",
    "id_number",
    "licence_no",
    "document_number",

    # Company identifiers
    "registration_no",
    "company_no",
    "commercial_registration_no",

    # Financial identifiers
    "reference_no",
    "tax_id",
    "vat_number",

    # Contact
    "email",

    # Financial values — preserve the numeric value, only format is normalised (Strategy B)
    # These are listed here so the router knows not to transliterate or translate them.
    # The numeric normalisation (digit script conversion, separator format) is
    # handled by Strategy B. The value itself is never changed.
    "number_of_shares",
    "voting_rights",
    "ownership_percentage",
    "share_capital",
    "number_of_issued_shares",
    "total_assets",
    "total_liabilities",
    "net_assets",
    "revenue",
    "expenses",
]


# ---------------------------------------------------------------------------
# Strategy B — Calendar and numeric rules
# Dates converted to ISO 8601. Numeric scripts normalised to ASCII.
# ---------------------------------------------------------------------------

NUMERIC_FIELDS: list[str] = [
    "date_of_birth",
    "birth_date",
    "date",
    "issue_date",
    "expiry_date",
    "incorporation_date",
    "document_date",
    "registry_date",
    "financial_period",
]


# ---------------------------------------------------------------------------
# Strategy C — Vocabulary lookup
# Matched against pre-built JSON dictionaries.
# ---------------------------------------------------------------------------

VOCABULARY_FIELDS: list[str] = [
    "legal_form",
    "status",
    "role",
    "designation",
    "share_class",
    "capital_change_type",
    "relationship_classification",
    "industry_code",
    "document_type",
]


# ---------------------------------------------------------------------------
# Strategy D — Geographic lookup
# Resolved against ISO databases and GeoNames.
# ---------------------------------------------------------------------------

GEOGRAPHIC_FIELDS: list[str] = [
    "nationality",
    "country",
    "country_of_residence",
    "place_of_birth",
    "city",
]


# ---------------------------------------------------------------------------
# Strategy E — Verified repository
# Checked against human-confirmed translation store.
# Applies to all name and address fields before transliteration is attempted.
# ---------------------------------------------------------------------------

REPOSITORY_CHECKED_FIELDS: list[str] = [
    "full_name",
    "person_name",
    "alias",
    "director_name",
    "officer_name",
    "shareholder_name",
    "parent_name_father",
    "parent_name_mother",
    "entity_name",
    "company_name",
    "issuing_authority",
    "address",
    "registered_address",
    "mailing_address",
    "shareholder_address",
    "office_address",
    "locality_information",
]


# ---------------------------------------------------------------------------
# Strategy F — Transliteration libraries
# Non-Latin scripts converted to Latin using international standards.
# Applies to name fields after repository check.
# ---------------------------------------------------------------------------

NAME_FIELDS: list[str] = [
    "full_name",
    "person_name",
    "alias",
    "director_name",
    "officer_name",
    "shareholder_name",
    "parent_name_father",
    "parent_name_mother",
    "entity_name",
    "company_name",
    "issuing_authority",
]


# ---------------------------------------------------------------------------
# Strategy G — Character mapping tables
# Latin-script special characters substituted using fixed tables.
# Applies to name fields when language is a Latin-script language.
# ---------------------------------------------------------------------------

ADDRESS_FIELDS: list[str] = [
    "address",
    "registered_address",
    "mailing_address",
    "shareholder_address",
    "office_address",
]


# ---------------------------------------------------------------------------
# Strategy H — Azure Translator NMT
# Prose fields translated to readable English.
# Never applied to names, identifiers, or structured fields.
# ---------------------------------------------------------------------------

PROSE_FIELDS: list[str] = [
    "nature_of_business",
    "business_purpose",
    "accounting_policies",
    "locality_information",
    "capital_changes_narrative",
    "unstructured_text",
]


# ---------------------------------------------------------------------------
# Processing method labels
# Written to every result dict and to the audit log.
# Used by the admin dashboard to show processing method statistics.
# ---------------------------------------------------------------------------

class ProcessingMethod:
    PRESERVE        = "PRESERVE"
    CALENDAR        = "CALENDAR"
    NUMERIC         = "NUMERIC"
    VOCABULARY      = "VOCABULARY"
    GEOGRAPHIC      = "GEOGRAPHIC"
    REPOSITORY      = "REPOSITORY"
    TRANSLITERATION = "TRANSLITERATION"
    CHARACTER_MAP   = "CHARACTER_MAP"
    NMT             = "NMT"
    NATIVE_SPEAKER  = "NATIVE_SPEAKER"
    LLM             = "LLM"        # Phase 2 only — requires LLM_ENABLED=true in .env
    UNRESOLVED      = "UNRESOLVED"
    FALLBACK        = "FALLBACK"


# ---------------------------------------------------------------------------
# Confidence thresholds
# ---------------------------------------------------------------------------

# Minimum Document Intelligence confidence below which a field is flagged
# review_required=True regardless of which strategy resolved it.
# Configured via OCR_CONFIDENCE_THRESHOLD in .env — this is the default.
DEFAULT_OCR_CONFIDENCE_THRESHOLD: float = 0.85

# Confidence assigned to results from each strategy.
# Human-verified results (PRESERVE, REPOSITORY, VOCABULARY, GEOGRAPHIC) are 1.0.
# Algorithmic results (TRANSLITERATION, CHARACTER_MAP, CALENDAR) are 0.95.
# NMT prose translation is 0.80 — readable but not KYC-formatted.
STRATEGY_CONFIDENCE: dict[str, float] = {
    ProcessingMethod.PRESERVE:        1.0,
    ProcessingMethod.CALENDAR:        0.95,
    ProcessingMethod.NUMERIC:         0.95,
    ProcessingMethod.VOCABULARY:      1.0,
    ProcessingMethod.GEOGRAPHIC:      1.0,
    ProcessingMethod.REPOSITORY:      1.0,
    ProcessingMethod.TRANSLITERATION: 0.90,
    ProcessingMethod.CHARACTER_MAP:   0.95,
    ProcessingMethod.NMT:             0.80,
    ProcessingMethod.NATIVE_SPEAKER:  1.0,
    ProcessingMethod.LLM:             0.75,
    ProcessingMethod.UNRESOLVED:      0.0,
    ProcessingMethod.FALLBACK:        0.50,
}
```

---

### 2. `app/pipeline/normalisation/preserve.py` — NEW FILE

Replaces `src/pipeline/rules_engine.py` for the preserve logic only. The numeric/calendar logic from `rules_engine.py` moves to Epic 02 (Strategy B).

```python
"""
Strategy A — Preserve.

Returns structured identifiers exactly as extracted from the source document.
No normalisation, no transliteration, no translation, no API calls.

This is the first strategy checked by the normalisation router. If a field
type is in PRESERVE_FIELDS, the router returns immediately with this result
and no further strategies are attempted.
"""

from app.pipeline.normalisation.field_types import PRESERVE_FIELDS, ProcessingMethod, STRATEGY_CONFIDENCE


def apply_preserve(field_type: str, text: str) -> dict | None:
    """
    Return the field value verbatim if the field type is a structured identifier.

    Args:
        field_type: The KYC field type string (e.g. "passport_no", "registration_no").
        text: The raw extracted text value.

    Returns:
        A complete result dict if field_type is in PRESERVE_FIELDS, else None.
        Returning None signals the router to try the next strategy.
    """
    if field_type not in PRESERVE_FIELDS:
        return None

    return {
        "original_text":            text,
        "normalised_form":          text,
        "allowed_variants":         [],
        "processing_method":        ProcessingMethod.PRESERVE,
        "confidence":               STRATEGY_CONFIDENCE[ProcessingMethod.PRESERVE],
        "review_required":          False,
        "review_reason":            None,
        "should_use_in_screening":  True,
    }
```

---

### 3. Update `requirements.txt`

No new dependencies required for this epic.

---

## Tests

`tests/test_strategy_a_preserve.py` — NEW FILE

```python
"""Tests for Strategy A — Preserve."""
import pytest
from app.pipeline.normalisation.preserve import apply_preserve
from app.pipeline.normalisation.field_types import PRESERVE_FIELDS, ProcessingMethod


# --- Returns verbatim for all preserve field types ---

@pytest.mark.parametrize("field_type", PRESERVE_FIELDS)
def test_preserve_returns_result_for_all_preserve_fields(field_type):
    result = apply_preserve(field_type, "ABC123")
    assert result is not None

@pytest.mark.parametrize("field_type", PRESERVE_FIELDS)
def test_preserve_normalised_form_equals_input(field_type):
    value = "X1234567"
    result = apply_preserve(field_type, value)
    assert result["normalised_form"] == value

@pytest.mark.parametrize("field_type", PRESERVE_FIELDS)
def test_preserve_never_alters_value(field_type):
    # Lowercase, spaces, hyphens — all must be returned exactly
    value = "abc-123 / xyz"
    result = apply_preserve(field_type, value)
    assert result["normalised_form"] == value

def test_preserve_confidence_is_1():
    result = apply_preserve("passport_no", "TK1234567")
    assert result["confidence"] == 1.0

def test_preserve_review_not_required():
    result = apply_preserve("passport_no", "TK1234567")
    assert result["review_required"] is False

def test_preserve_no_variants():
    result = apply_preserve("passport_no", "TK1234567")
    assert result["allowed_variants"] == []

def test_preserve_processing_method_label():
    result = apply_preserve("passport_no", "TK1234567")
    assert result["processing_method"] == ProcessingMethod.PRESERVE

def test_preserve_should_use_in_screening():
    result = apply_preserve("passport_no", "TK1234567")
    assert result["should_use_in_screening"] is True


# --- Returns None for non-preserve field types ---

@pytest.mark.parametrize("field_type", [
    "person_name", "company_name", "address", "legal_form",
    "status", "nationality", "date_of_birth", "business_purpose",
])
def test_preserve_returns_none_for_non_preserve_fields(field_type):
    result = apply_preserve(field_type, "some value")
    assert result is None


# --- Edge cases ---

def test_preserve_empty_string():
    result = apply_preserve("passport_no", "")
    assert result is not None
    assert result["normalised_form"] == ""

def test_preserve_arabic_indic_digits_not_converted():
    # Identifiers are returned as-is — digit conversion is Strategy B's job
    value = "١٢٣٤٥٦٧"
    result = apply_preserve("id_no", value)
    assert result["normalised_form"] == value

def test_preserve_unicode_not_normalised():
    # No NFKC or other normalisation applied
    value = "Ａ１２３"   # full-width characters
    result = apply_preserve("registration_no", value)
    assert result["normalised_form"] == value

def test_preserve_financial_field_value_unchanged():
    # Financial fields are in PRESERVE_FIELDS — value must not be altered
    result = apply_preserve("total_assets", "1.234.567,89")
    assert result["normalised_form"] == "1.234.567,89"
```

---

## Acceptance criteria

- `apply_preserve()` returns a result dict for every field type in `PRESERVE_FIELDS`.
- `apply_preserve()` returns `None` for every field type not in `PRESERVE_FIELDS`.
- The `normalised_form` in the result is byte-for-byte identical to the input `text` for all inputs including empty string, non-ASCII characters, full-width digits, and Arabic-Indic numerals.
- `confidence` is `1.0`, `review_required` is `False`, `allowed_variants` is `[]` for all preserve results.
- All tests in `tests/test_strategy_a_preserve.py` pass.
- `field_types.py` is importable with no errors and all constants are accessible.
- No existing tests from the golden dataset regression gate are broken.
