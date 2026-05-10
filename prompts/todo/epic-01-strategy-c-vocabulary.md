# Epic 03 — Normalisation Strategy C: Vocabulary Lookup

## Execution Todo Checklist (this run)

- [x] Complete and validate lookup data files in `data/lookup_tables/`:
  - [x] `legal_forms.json` (verify required country coverage)
  - [x] `status_terms.json` (verify canonical status values only)
  - [x] `role_titles.json`
  - [x] `street_types.json`
  - [x] `industry_codes.json` (populate starter NACE/SIC_UK/ISIC mappings)
  - [x] `issuing_authorities.json` (create and populate starter country mappings)
  - [x] `share_classes.json`
  - [x] `capital_change_types.json` (populate canonical change labels)
  - [x] `document_type_labels.json` (create and populate internal labels)
- [x] Implement `app/pipeline/normalisation/vocabulary_lookup.py` service:
  - [x] table loading with startup validation
  - [x] case-insensitive lookup helpers
  - [x] standard result dict builder
  - [x] language/country fallback behavior
- [x] Plug Strategy C into router and orchestrator flow:
  - [x] call vocabulary service after Strategy B and before unresolved fallback
  - [x] wire service instantiation in app startup (`app/__init__.py`)
  - [x] make router consume shared singleton service
- [x] Add and update tests:
  - [x] add `tests/test_strategy_c_vocabulary.py`
  - [x] update `tests/test_router.py` for Strategy C routing expectations
  - [x] add data validation tests for canonical status/document values
- [x] Run targeted tests and fix regressions
- [x] Run Flask on `127.0.0.1:5001` for manual verification
- [x] Provide copy/paste examples for Strategy C checks in Sentence tab

## Assessment and open data notes

- Current repo state is close but not complete for this epic:
  - `capital_change_types.json` is empty
  - `industry_codes.json` is empty
  - `issuing_authorities.json` does not exist under `data/lookup_tables/`
  - `document_type_labels.json` does not exist under `data/lookup_tables/`
- Execution below will create/complete these files with a validated starter dataset and keep all canonical value constraints enforced by tests.

## What you need to provide

Nine JSON files containing the lookup dictionaries. Copilot builds the service class that loads and queries them — you provide the data.

All files save to `app/data/lookup_tables/`.

---

### `legal_forms.json`

Maps company legal form suffixes to their English canonical abbreviation, keyed by ISO 3166-1 alpha-2 country code.

**Format:**
```json
{
  "JP": {
    "株式会社": "KK",
    "合同会社": "GK"
  },
  "DE": {
    "GmbH": "GMBH",
    "AG": "AG"
  }
}
```

- Top-level key: ISO 3166-1 alpha-2 country code
- Inner key: the legal form exactly as it appears in source documents, in original script
- Value: uppercase English abbreviation as used in KYC screening databases

Coverage required: JP, CN, HK, KR, AE, SA, EG, IL, TR, RU, UA, GR, DE, FR, IT, ES, PT, NL, BE, SG, IN, TH, GB, IE.

---

### `status_terms.json`

Maps company status terms to one of these canonical English values exactly: `ACTIVE`, `INACTIVE`, `DISSOLVED`, `SUSPENDED`, `IN_LIQUIDATION`, `STRUCK_OFF`, `DORMANT`.

**Format:**
```json
{
  "ja": {
    "現役": "ACTIVE",
    "解散": "DISSOLVED"
  },
  "ar": {
    "نشط": "ACTIVE",
    "تصفية": "IN_LIQUIDATION"
  }
}
```

- Top-level key: ISO 639-1 language code
- Inner key: status term exactly as it appears in source documents
- Value: one of the seven canonical strings above, uppercase

Coverage required: ja, zh, ko, ar, he, tr, ru, uk, el, de, fr, it, es, pt, th, en.

---

### `role_titles.json`

Maps director and officer role titles to their English canonical form.

**Format:**
```json
{
  "ja": {
    "代表取締役": "REPRESENTATIVE DIRECTOR",
    "取締役": "DIRECTOR",
    "監査役": "AUDITOR"
  },
  "ar": {
    "مدير عام": "GENERAL MANAGER",
    "رئيس مجلس الإدارة": "CHAIRMAN"
  }
}
```

- Top-level key: ISO 639-1 language code
- Inner key: role title exactly as it appears in source documents
- Value: uppercase English role title

Coverage required: ja, zh, ko, ar, he, tr, ru, uk, el, de, fr, it, es, pt, en.

---

### `street_types.json`

Maps street type words to their English equivalent. Used during address normalisation to translate the type component while leaving the proper name components for transliteration.

**Format:**
```json
{
  "ar": {
    "شارع": "STREET",
    "طريق": "ROAD",
    "ميدان": "SQUARE"
  },
  "ja": {
    "通り": "STREET",
    "丁目": "CHOME",
    "番地": "BANCHI"
  }
}
```

- Top-level key: ISO 639-1 language code
- Inner key: street type word as it appears in documents
- Value: uppercase English equivalent

Coverage required: ar, ja, zh, ko, ru, uk, el, de, fr, it, es, tr, he, th.

---

### `industry_codes.json`

Maps standard industry classification codes to their English descriptions.

**Format:**
```json
{
  "NACE": {
    "K": "Financial and insurance activities",
    "K64": "Financial service activities, except insurance and pension funding",
    "K64.19": "Other monetary intermediation"
  },
  "SIC_UK": {
    "6120": "Banks"
  },
  "ISIC": {
    "K": "Financial and insurance activities"
  }
}
```

- Top-level key: classification scheme (`NACE`, `SIC_UK`, `ISIC`)
- Inner key: code string exactly as it appears in documents
- Value: English description

Coverage required: NACE Rev.2 top-level sections and key financial services subsections at minimum. Add SIC_UK and ISIC as needed.

---

### `issuing_authorities.json`

Maps government issuing authority names in original script to their English canonical name, keyed by country.

**Format:**
```json
{
  "JP": {
    "法務省": "MINISTRY OF JUSTICE",
    "外務省": "MINISTRY OF FOREIGN AFFAIRS"
  },
  "AE": {
    "وزارة الداخلية": "MINISTRY OF INTERIOR"
  }
}
```

- Top-level key: ISO 3166-1 alpha-2 country code
- Inner key: authority name exactly as it appears in documents
- Value: uppercase English name

Start with the jurisdictions you process most. This file grows incrementally as new documents are processed — can start sparse.

---

### `share_classes.json`

Maps share class names to canonical English values: `ORDINARY`, `PREFERENCE`, `REDEEMABLE`, `NON-VOTING`, `MANAGEMENT`.

**Format:**
```json
{
  "ja": {
    "普通株式": "ORDINARY",
    "優先株式": "PREFERENCE"
  },
  "en": {
    "Ordinary": "ORDINARY",
    "Preference": "PREFERENCE",
    "Redeemable": "REDEEMABLE"
  }
}
```

- Top-level key: ISO 639-1 language code
- Inner key: share class name as it appears in documents
- Value: one of the five canonical values above

---

### `capital_change_types.json`

Maps capital change event descriptions to canonical English values: `INCREASE`, `DECREASE`, `CONVERSION`, `SPLIT`, `CONSOLIDATION`.

**Format:**
```json
{
  "ja": {
    "増資": "INCREASE",
    "減資": "DECREASE",
    "株式分割": "SPLIT"
  },
  "de": {
    "Kapitalerhöhung": "INCREASE",
    "Kapitalherabsetzung": "DECREASE"
  }
}
```

- Top-level key: ISO 639-1 language code
- Inner key: event description as it appears in documents
- Value: one of the five canonical values above

---

### `document_type_labels.json`

Maps document type descriptions in any language to the internal document type labels used by the classifier.

Internal labels: `national_id`, `drivers_licence`, `passport`, `company_registry_local`, `company_registry_foreign`, `business_registration`, `aoa`, `financial_statement`, `shareholder_table`, `unknown`.

**Format:**
```json
{
  "ja": {
    "運転免許証": "drivers_licence",
    "旅券": "passport",
    "登記事項証明書": "company_registry_foreign"
  },
  "ar": {
    "بطاقة هوية وطنية": "national_id",
    "جواز السفر": "passport"
  }
}
```

- Top-level key: ISO 639-1 language code
- Inner key: document type label as it appears in the document itself
- Value: one of the internal label strings above

---

## What exists in the current codebase

Nothing. Strategy C does not exist in any form in the current codebase. Entirely new build.

---

## What this epic builds

### `app/pipeline/normalisation/vocabulary_lookup.py` — NEW FILE

```python
"""
Strategy C — Vocabulary Lookup.

Loads all JSON lookup tables at application startup and holds them in memory.
All lookups are O(1) dict operations — no database queries, no API calls.

The service is instantiated once at startup and injected into the normalisation
router. It is not re-instantiated per request.
"""

from pathlib import Path
import json
from app.pipeline.normalisation.field_types import (
    VOCABULARY_FIELDS, ProcessingMethod, STRATEGY_CONFIDENCE
)


class VocabularyLookupService:

    def __init__(self, tables_dir: Path):
        """
        Load all lookup tables from JSON files at the given directory.
        Raises FileNotFoundError if any required table is missing.
        All keys are normalised to lowercase + stripped on load so matching
        is case-insensitive without per-lookup overhead.
        """
        self.legal_forms        = self._load(tables_dir, "legal_forms.json",         key_level="country")
        self.status_terms       = self._load(tables_dir, "status_terms.json",        key_level="language")
        self.role_titles        = self._load(tables_dir, "role_titles.json",         key_level="language")
        self.street_types       = self._load(tables_dir, "street_types.json",        key_level="language")
        self.industry_codes     = self._load(tables_dir, "industry_codes.json",      key_level="scheme")
        self.issuing_authorities= self._load(tables_dir, "issuing_authorities.json", key_level="country")
        self.share_classes      = self._load(tables_dir, "share_classes.json",       key_level="language")
        self.capital_changes    = self._load(tables_dir, "capital_change_types.json",key_level="language")
        self.document_types     = self._load(tables_dir, "document_type_labels.json",key_level="language")

    def lookup(self, field_type: str, text: str, language: str = "", country: str = "") -> dict | None:
        """
        Main entry point called by the normalisation router.

        Routes to the correct sub-lookup based on field_type.
        Returns None if field_type is not a vocabulary field or no match found.
        """
        if field_type not in VOCABULARY_FIELDS:
            return None

        result = None

        if field_type == "legal_form":
            result = self.lookup_legal_form(text, country)
        elif field_type == "status":
            result = self.lookup_status(text, language)
        elif field_type in ("role", "designation"):
            result = self.lookup_role(text, language)
        elif field_type == "share_class":
            result = self.lookup_share_class(text, language)
        elif field_type == "capital_change_type":
            result = self.lookup_capital_change(text, language)
        elif field_type == "industry_code":
            result = self.lookup_industry_code(text)
        elif field_type == "document_type":
            result = self.lookup_document_type(text, language)

        return result

    def lookup_legal_form(self, text: str, country: str) -> dict | None:
        """
        Match legal form suffix for a given country.

        Matching strategy (tried in order):
        1. Exact suffix match — text ends with the key (e.g. "Mitsubishi GmbH" matches "GmbH")
        2. Whole-string match — text equals the key exactly
        3. If country is empty, try all countries in order

        Returns result dict or None.
        """

    def lookup_status(self, text: str, language: str) -> dict | None:
        """
        Case-insensitive whole-string match for status terms.
        If language not found, try "en" as fallback.
        """

    def lookup_role(self, text: str, language: str) -> dict | None:
        """
        Case-insensitive whole-string match for role titles.
        Also tries after stripping trailing punctuation (periods, commas).
        If language not found, try "en" as fallback.
        """

    def lookup_street_type(self, token: str, language: str) -> str | None:
        """
        Match a single token (word) against street type terms.
        Returns English equivalent string or None.
        Used by the address normalisation step, not directly by the router.
        """

    def lookup_industry_code(self, code: str, scheme: str = "NACE") -> dict | None:
        """
        Exact code match first, then prefix match.
        Prefix match: "K64" matches "K64.1", "K64.19" etc.
        Tries all schemes if scheme not found.
        """

    def lookup_document_type(self, text: str, language: str) -> dict | None:
        """
        Case-insensitive whole-string match for document type labels.
        """

    def lookup_share_class(self, text: str, language: str) -> dict | None:
        """Case-insensitive whole-string match."""

    def lookup_capital_change(self, text: str, language: str) -> dict | None:
        """Case-insensitive whole-string match."""

    @staticmethod
    def _build_result(normalised_form: str) -> dict:
        """Build a standard result dict for a successful vocabulary lookup."""
        return {
            "normalised_form":          normalised_form,
            "allowed_variants":         [],
            "processing_method":        ProcessingMethod.VOCABULARY,
            "confidence":               STRATEGY_CONFIDENCE[ProcessingMethod.VOCABULARY],
            "review_required":          False,
            "review_reason":            None,
            "should_use_in_screening":  True,
        }

    @staticmethod
    def _load(tables_dir: Path, filename: str, key_level: str) -> dict:
        """
        Load a JSON file and normalise all inner keys to lowercase + stripped.
        key_level is informational only — all files are loaded the same way.
        Raises FileNotFoundError with a clear message if the file is missing.
        """
```

### Application startup wiring

The `VocabularyLookupService` instance is created once when the Flask app starts and stored on the app object. Copilot adds this to the app factory in `app/__init__.py` (Epic 12) and makes it accessible via `current_app.vocab_service`. For this epic, instantiation is tested directly without Flask.

---

## Tests

`tests/test_strategy_c_vocabulary.py` — Copilot writes these once the JSON files are provided.

```python
# --- Legal form matching ---
def test_legal_form_exact_suffix_japanese(): ...      # "田中商事株式会社" → "KK"
def test_legal_form_whole_string_german(): ...        # "GmbH" → "GMBH"
def test_legal_form_embedded_russian(): ...           # "Газпром ООО" → "LLC"
def test_legal_form_no_match_returns_none(): ...
def test_legal_form_unknown_country_tries_all(): ...

# --- Status terms ---
def test_status_active_japanese(): ...                # "現役" → "ACTIVE"
def test_status_dissolved_arabic(): ...               # "منتهي" → "DISSOLVED"
def test_status_in_liquidation_german(): ...          # "in Liquidation" → "IN_LIQUIDATION"
def test_status_case_insensitive(): ...               # "AKTIV" matches "aktiv" → "ACTIVE"
def test_status_no_match_returns_none(): ...

# --- Role titles ---
def test_role_director_japanese(): ...                # "取締役" → "DIRECTOR"
def test_role_chairman_arabic(): ...                  # "رئيس مجلس الإدارة" → "CHAIRMAN"
def test_role_with_trailing_punctuation(): ...        # "Director," → "DIRECTOR"
def test_role_no_match_returns_none(): ...

# --- Industry codes ---
def test_industry_code_exact_nace(): ...              # "K64" → description
def test_industry_code_prefix_match(): ...            # "K64.19" found when "K64" exists
def test_industry_code_unknown_scheme(): ...

# --- Street types ---
def test_street_type_arabic(): ...                    # "شارع" → "STREET"
def test_street_type_japanese_chome(): ...            # "丁目" → "CHOME"
def test_street_type_no_match(): ...

# --- Document types ---
def test_document_type_japanese_passport(): ...       # "旅券" → "passport"
def test_document_type_arabic_id(): ...               # "بطاقة هوية وطنية" → "national_id"

# --- Router integration ---
def test_router_returns_none_for_non_vocabulary_field(): ...
def test_router_returns_none_for_preserve_field(): ...

# --- Service loading ---
def test_service_loads_all_tables_without_error(): ...
def test_missing_table_raises_file_not_found(): ...
def test_all_status_canonical_values_are_valid(): ...  # validates your data against allowed set
def test_all_document_type_labels_are_valid(): ...     # validates your data against internal labels
```

---

## Acceptance criteria

- `VocabularyLookupService` loads all nine JSON files without error.
- All tests pass.
- `service.lookup("legal_form", "田中商事株式会社", country="JP")` returns `normalised_form == "KK"`.
- `service.lookup("status", "現役", language="ja")` returns `normalised_form == "ACTIVE"`.
- `service.lookup("role", "取締役", language="ja")` returns `normalised_form == "DIRECTOR"`.
- `service.lookup("person_name", "田中太郎", language="ja")` returns `None` — person names are not a vocabulary field.
- A validation test confirms every value in `status_terms.json` is one of the seven canonical status strings.
- A validation test confirms every value in `document_type_labels.json` is one of the eleven internal label strings.
- No LLM is called at any point in this strategy.
- `convertdate` is not required for this epic.
