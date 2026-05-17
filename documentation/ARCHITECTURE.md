# KYC Identity Normalisation — Architecture Reference

**Current Status:** Epic 08 (Strategy H — NMT Translation)  
**Diagnostic Baseline:** 138/164 integration tests  
**Entry Point:** `run.py` (Flask production)

---

## 1. Production Entry Point & Bootstrap

### `run.py` — Flask Application Factory

**Location:** Repository root  
**Role:** Production web application entry point  
**Initialization:**

```python
from app import create_app
app = create_app()  # Reads config, initializes extensions
```

**Flow:**
1. Calls `app.create_app()` (in [app/__init__.py](../app/__init__.py))
2. Loads `app/config.py` (Flask config keys, feature flags)
3. Initializes extensions (`app/extensions.py`: SQLAlchemy, logging)
4. Registers route blueprints from `app/routes/`:
   - `paste.py` — POST normalisation requests
   - `upload.py` — File upload & batch processing
   - `review.py` — Data review interface
   - `admin.py` — Admin controls
   - `export.py` — Result export
   - `telemetry.py` — System telemetry
5. Runs on `0.0.0.0:5000` (configurable)

---

## 2. Request Pipeline — Live Normalisation Flow

### Entry Point: `POST /paste/translate` ([app/routes/paste.py](../app/routes/paste.py))

```
Client Request (form POST)
    ↓
paste.py::translate()
    ↓ calls classifier
[app/pipeline/normalisation/field_type_detector.py](../app/pipeline/normalisation/field_type_detector.py)::detect_field_type()
    ↓ calls
[app/pipeline/orchestrator.py](../app/pipeline/orchestrator.py)::process_field_row()
    ↓ calls
[app/pipeline/normalisation/router.py](../app/pipeline/normalisation/router.py)::route_field()
    ↓ dispatches to
Strategy Module (A–I, based on field_type + language + rules)
    ↓ delegates to
src/ Shared Utilities (transliteration, calendar, rules, geographic lookup)
    ↓
Result: normalised_form, processing_method, confidence, review_required
    ↓
Response (JSON) to Client
```

### `router.py` — Central Dispatcher

**Location:** [app/pipeline/normalisation/router.py](../app/pipeline/normalisation/router.py)  
**Responsibility:** Route each field to the correct strategy (A–I) based on:
- `field_type`: 'person_name', 'company_name', 'address', 'nationality', etc.
- `language`: ISO 639-1 code ('ja', 'zh', 'ar', etc.)
- `country`: ISO 3166-1 alpha-2 code (optional)

**Classifier Before Routing:**
- `paste.py` calls `detect_field_type()` from `field_type_detector.py`
- That classifier assigns `field_type`, `classification_confidence`, and `language`
- The router consumes the classified row; it does not call `field_type_detector.py`

**Strategy Dispatch Logic:**
1. **Strategy A (PRESERVE)** — fields requiring literal preservation
    - Implemented in `router.py::_try_strategy_a()`
    - Rules: `from pipeline.rules_engine import apply_rules`
    - `app/pipeline/normalisation/preserve.py` exists but is a placeholder and is not called by the router
   
2. **Strategy B (CALENDAR_NUMERIC)** — date and numeric normalization
   - Detects date formats (MD/DD/YYYY, ISO 8601, etc.)
   - Converts to ISO 8601; normalizes numbers to English numerals
   
3. **Strategy C (VOCABULARY)** — fixed vocabulary lookups
   - State names, titles, honorifics, etc.
   - Multi-language phrase tables
   
4. **Strategy D (GEOGRAPHIC)** — country, city, region detection
   - Geonames integration with local aliases
   - Supports 200+ languages via pycountry + custom aliases
   
5. **Strategy E–I** — Remaining strategy slots / language-specific transformations
    - **E (Repository Lookup)** — placeholder strategy slot represented by `repository_lookup.py`
   - **F (Transliteration)** — Romanization engines (Japanese kanji→romaji, Arabic→Latin, etc.)
   - **G (Character Maps)** — Systematic diacritic normalization
   - **H (NMT Translation)** — Neural Machine Translation via Azure Translator
   - **I (Native Speaker Review)** — Placeholder for future human-in-loop review

### Strategy Modules

All strategy modules are under [app/pipeline/normalisation/](../app/pipeline/normalisation/):

| Strategy | File | Input | Output | Key Dependency |
|----------|------|-------|--------|-----------------|
| A | router.py (`_try_strategy_a`) | field_type, text | Literal text or rules-based fallback | src/config/rules.py, src/pipeline/rules_engine.py |
| B | calendar_rules.py, numeric_rules.py | text, field_type | Normalized ISO dates, English numerals | src/utils/calendar_utils.py |
| C | vocabulary_lookup.py | text, language, field_type | Matched vocabulary entry or None | (internal dicts) |
| D | geographic_lookup.py | text, field_type, language, country | Geographic entity (country, city, region) + confidence | pycountry, geonames data |
| E | repository_lookup.py | text, field_type, language, country | Placeholder | Stub only; not currently routed |
| F | transliteration.py | text, language, target_script | Latin transliteration + confidence | src/pipeline/transliteration_engine.py |
| G | character_map_normaliser.py | text, language | Unicode-normalized text (diacritics) | src/pipeline/transliteration_engine.py, character_maps.py |
| H | nmt_translator.py | text, source_lang, target_lang | Translated text via Azure Translator | Azure Translator API (external service) |
| I | (placeholder) | — | — | — |

**Placeholders / non-routed modules in this directory:**
- `preserve.py` — placeholder from Epic 01; not used by the router
- `repository_lookup.py` — placeholder from Epic 05; not used by the router
- `field_type_detector.py` — classifier used by `paste.py` before routing, not a router strategy

---

## 3. Shared `src/` Modules — Why They Stayed

The following `src/` modules are **ALIVE** (imported transitively at Flask runtime) and **NOT ARCHIVED**:

| Module | Location | Used By | Reason |
|--------|----------|---------|--------|
| **rules_engine.py** | src/pipeline/ | router.py → Strategy A | Applies deterministic preserve & numeric rules |
| **transliteration_engine.py** | src/pipeline/ | Strategy F, G | Core romanization engine (kanji, Arabic, Cyrillic) |
| **calendar_utils.py** | src/utils/ | Strategy B | Date normalization and parsing |
| **script_detection.py** | src/utils/ | transliteration_engine.py | Script-family helpers used by transliteration logic |
| **language_normalisation_tables.py** | src/config/ | transliteration_engine.py, Strategy G | Language-specific character mapping tables |
| **rules.py** | src/config/ | rules_engine.py (transitive) | Preserve/normalize field type definitions |
| **kanji_lookup.py** | src/config/ | transliteration_engine.py | Japanese kanji → romaji lookups (50k+ entries) |
| **cantonese_surname_map.py** | src/config/ | transliteration_engine.py | Cantonese surname variants (family-name preference) |

**CI/CD Entry Points** (used by regression gate, not Flask runtime):
- **src/main.py** — CI test runner
- **src/evaluation/evaluator.py** — Test evaluation harness
- **src/evaluation/metrics.py** — Accuracy & coverage metrics
- **src/evaluation/regression_gate.py** — 138/164 test assertion
- **src/pipeline/matcher.py** — Result matching logic (used by evaluator)
- **src/pipeline/pipeline.py** — Legacy processing surface called by evaluator
- **src/pipeline/analyst_handler.py** — Imported transitively by `src/pipeline/pipeline.py`
- **src/pipeline/field_classifier.py** — Imported transitively by `src/pipeline/pipeline.py`
- **src/pipeline/llm_layer.py** — Imported transitively by `src/pipeline/pipeline.py`

**Note:** These modules are used by the CI regression gate (`src/main.py` → `evaluator.py` → `pipeline.py`). Migrating the regression gate to use the Flask-era `route_field()` pipeline is a future cleanup task that would allow archiving these files.

---

## 4. Test Structure

### Live Tests (Kept)

| Test | Scope | Validates |
|------|-------|-----------|
| test_epic00_* | Unit/Integration | Flask skeleton, routes, app contracts |
| test_router.py | Unit | Router dispatch logic |
| test_strategy_*.py (A–H) | Unit/Integration | Individual strategy modules |
| test_e2e_pipeline.py | Integration | End-to-end request flow |
| test_evaluator.py | Unit | Regression gate evaluation |
| test_data_integrity.py | Integration | Data contract compliance |

**Note:** Task 4 cleanup completed: `test_epic00_data_contracts.py` no longer contains `test_src_pipeline_imports_still_work()`.

### Dead Tests (Archived)

- **test_pipeline.py** — Tests pre-Flask v1 pipeline.py (archived with source)
- **test_ocr_gate.py** — Tests legacy OCR gate (archived with source)
- **test_ocr_pipeline.py** — Tests legacy pipeline + OCR (archived with source)

### Smoke Tests (Kept)

- **test_nmt.py** — Root-level standalone script that verifies Azure Translator credentials and connectivity

---

## 5. Retired Components

### Streamlit Prototype — `app.py` (ARCHIVED)

**Status:** Retired v1 prototype (replaced by Flask production app)  
**Dependencies:**
- `src/pipeline/pipeline.py` (pre-Flask orchestrator) — retained for CI regression gate compatibility
- `src/pipeline/rules_engine.py` (moved to Flask)
- Other legacy v1 pipeline modules

**Why Archived:**
- `run.py` is the active production entry point
- Streamlit prototype was proof-of-concept only
- Flask provides scalability and integration required for production
- All business logic migrated to strategy modules

### Legacy Modules (ARCHIVED)

| Module | Reason |
|--------|--------|
| `src/pipeline/ocr_gate.py` | Pre-Flask OCR system; Epic 05 not yet started |
| `src/utils/logging_utils.py` | Replaced by app/utils/logging_utils.py |
| `src/utils/normalisation.py` | Legacy normalization; split into strategy modules |

**One-Off Diagnostics (ARCHIVED):**
- `run_ocr.py`, `_fix_dataset_a.py`, `_geo_debug.py`, `_geo_smoke_test.py` — development-only scripts
- `evaluate_copilot_output.py` — one-time evaluation; results documented in reports/

**Kept Placeholder Modules (Not Archived):**
- `app/pipeline/normalisation/preserve.py` — retained as the future Epic 01 implementation surface; currently a placeholder and not routed
- `app/pipeline/normalisation/repository_lookup.py` — retained as the future Epic 05 implementation surface; currently a placeholder and not routed

---

## 6. Data & Configuration

### Character Maps & Lookups

**Location:** [app/data/](../app/data/)

| File | Purpose | Loaded By |
|------|---------|-----------|
| character_maps.py | Master character mapping routing dict | Strategy G (character normalizer) |
| character_maps_new.py | New language tables (Turkish, Dutch, Scandinavian, Polish, Portuguese) | character_maps.py (active import) |
| kanji_lookup.py | Japanese kanji → romaji + reading variants | Strategy F (transliteration) |
| cantonese_surname_map.py | Cantonese surname family-name primary forms | Strategy F (transliteration) |

### Geonames Data

**Location:** [data/geonames/](../data/geonames/)  
**Used By:** Strategy D (geographic_lookup.py)  
**Contents:** City/region names in 200+ languages with ISO mappings

---

## 7. CI/CD Integration

### Regression Gate — [.github/workflows/regression.yml](../.github/workflows/regression.yml)

```yaml
runs: python src/main.py --regression-gate
expects: 138/164 tests pass
gates: Pull requests; must pass before merge to main
```

**Entry:** `src/main.py`  
**Pipeline:**
1. Loads golden_dataset.csv + test_dataset.csv
2. Runs strategy module tests for each case
3. Evaluates accuracy metrics (exact, fuzzy, pass/fail)
4. Counts passed tests; asserts >= 138/164
5. Generates integration report

**Diagnostics:**
- `run_integration_diagnostic.py` — Full test run with all strategies (run locally)
- `run_strategy_h_diagnostic.py` — Strategy H (NMT) specific tests

---

## 8. Conventions & Patterns

### Import Path Configuration

**Why:** src/ modules can be imported two ways depending on context.

```python
# In routes & strategies (Flask app context):
from pipeline.rules_engine import apply_rules  # Relative to sys.path.insert(0, 'src')

# In CI tests (regression gate):
from src.pipeline.rules_engine import apply_rules  # Direct import

# Set by app/pipeline/normalisation/router.py at module load:
sys.path.insert(0, os.path.abspath('src'))
```

### Field Type Constants

**Location:** [app/pipeline/normalisation/field_types.py](../app/pipeline/normalisation/field_types.py)

Defines:
- `PERSON_NAME`, `COMPANY_NAME`, `ADDRESS`, `NATIONALITY`, `CITY`, etc.
- Used by router to dispatch to correct strategy

### Result Shape

All strategy modules return a dict with standard keys:

```python
{
    "original_text": str,
    "normalised_form": str,
    "processing_method": str,  # "PRESERVE", "RULE", "VOCAB", "GEO", "SCRIPT", "TRANS", "CHAR", "NMT", etc.
    "confidence": float,  # 0.0–1.0
    "allowed_variants": list[str],  # Alternative acceptable forms
    "latin_transliteration": str | None,
    "analyst_english_rendering": str,
    "review_required": bool,
    "review_reason": str | None,
    "should_use_in_screening": bool,
}
```

### Error Handling

- Strategies **never raise exceptions**; they return None or a fallback result
- Router catches exceptions and escalates to next strategy or returns "REVIEW_REQUIRED"
- Flask routes log errors and return HTTP 500 with structured error JSON

---

## 9. File Structure Summary

```
kyc-identity-normalisation-poc/
├── run.py                          # Flask production entry point (LIVE)
├── app.py                          # Streamlit prototype (ARCHIVED)
│
├── app/
│   ├── __init__.py                # Flask factory
│   ├── config.py                  # Flask configuration
│   ├── extensions.py              # Extension initialization
│   ├── routes/                    # Flask blueprints (ALIVE)
│   │   ├── paste.py, upload.py, review.py, admin.py, export.py, telemetry.py
│   │
│   ├── pipeline/
│   │   ├── orchestrator.py        # Request orchestrator (ALIVE)
│   │   └── normalisation/
│   │       ├── router.py          # Strategy dispatcher (ALIVE)
│   │       ├── field_types.py     # Constants (ALIVE)
│   │       ├── field_type_detector.py # Pre-router classifier (ALIVE)
│   │       ├── preserve.py        # Placeholder; not routed
│   │       ├── calendar_rules.py  # Strategy B (ALIVE)
│   │       ├── numeric_rules.py   # Strategy B variant (ALIVE)
│   │       ├── vocabulary_lookup.py # Strategy C (ALIVE)
│   │       ├── geographic_lookup.py # Strategy D (ALIVE)
│   │       ├── repository_lookup.py # Strategy E placeholder; not routed
│   │       ├── transliteration.py # Strategy F (ALIVE)
│   │       ├── character_map_normaliser.py # Strategy G (ALIVE)
│   │       ├── nmt_translator.py  # Strategy H (ALIVE)
│   │       ├── [native speaker review slot] # Strategy I placeholder
│   │
│   ├── data/                      # Lookup tables (ALIVE)
│   │   └── normalisation/
│   │       ├── character_maps.py
│   │       ├── character_maps_new.py
│   │       ├── kanji_lookup.py
│   │       └── cantonese_surname_map.py
│   │
│   ├── utils/                     # Flask utilities (ALIVE)
│   │   ├── logging_utils.py
│   │   └── session_trace.py
│   │
│   └── models/, tasks/            # Stubs (ALIVE but unused)
│
├── src/
│   ├── main.py                    # CI test runner (CI-LIVE)
│   ├── config/
│   │   ├── rules.py               # PRESERVE/NORMALISE field defs (ALIVE—transitive)
│   │   ├── kanji_lookup.py        # Kanji data (ALIVE)
│   │   ├── cantonese_surname_map.py # Cantonese surname data (ALIVE)
│   │   └── language_normalisation_tables.py (ALIVE)
│   │
│   ├── pipeline/
│   │   ├── rules_engine.py        # Deterministic rules (ALIVE)
│   │   ├── transliteration_engine.py (ALIVE)
│   │   ├── matcher.py             # Result matching (CI-LIVE)
│   │   ├── pipeline.py            # CI-LIVE (used by evaluator)
│   │   ├── analyst_handler.py     # CI-LIVE (transitive via pipeline.py)
│   │   ├── field_classifier.py    # CI-LIVE (transitive via pipeline.py)
│   │   ├── llm_layer.py           # CI-LIVE (transitive via pipeline.py)
│   │   └── [ocr_gate.py, ...] (ARCHIVED)
│   │
│   ├── utils/
│   │   ├── calendar_utils.py      # Date normalization (ALIVE)
│   │   ├── script_detection.py    # Script detection (ALIVE)
│   │   └── [logging_utils.py, normalisation.py, ...] (ARCHIVED)
│   │
│   └── evaluation/                # Evaluation harness (CI-LIVE)
│       ├── evaluator.py
│       ├── metrics.py
│       └── regression_gate.py
│
├── tests/                         # pytest tests
│   ├── test_epic00_*.py           # Flask skeleton (KEEP; CLEAN test_epic00_data_contracts.py)
│   ├── test_router.py             # Router dispatch (KEEP)
│   ├── test_strategy_*.py         # Strategy tests (KEEP all)
│   ├── test_e2e_pipeline.py       # Integration (KEEP)
│   ├── test_evaluator.py          # Evaluation (KEEP)
│   ├── [test_pipeline.py, test_ocr_gate.py, test_ocr_pipeline.py] (ARCHIVE)
│
├── test_nmt.py                    # NMT credential smoke test (KEEP)
│
├── data/
│   ├── golden_dataset.csv         # Hand-verified reference (220 cases)
│   ├── test_dataset.csv           # Test cases (212+ cases)
│   ├── geonames/                  # Geographic data
│   └── images/, output/, seed/    # Data artifacts
│
├── documentation/
│   ├── 01-linguistic-approach.md
│   ├── 02-ai-governance.md
│   ├── 03-evaluation-framework.md
│   ├── 04-strategy-*.md           # Strategy documentation
│   ├── 05-flask-*.md
│   ├── 06-*.md
│   └── ARCHITECTURE.md            # This file
│
├── prompts/
│   ├── prompt_*.txt               # LLM prompts (reference)
│   └── todo/                      # Epic planning docs
│
├── reports/                       # Integration test reports (automated)
│
└── .github/workflows/
    └── regression.yml             # CI/CD gate
```

---

## 10. Migration Notes from Epic 08

### Task 1 — Inventory Complete ✓
- Catalogued all 84 files across src/ (21) + app/ (63)
- Mapped import relationships and runtime chains
- Identified live, CI-live, and dead code

### Task 2 — Archive Prepared ✓
- KEEP: 50+ live files + ci-live (5 files)
- ARCHIVE: 15 source files (13 dead src/ modules + 2 dead root scripts) + 3 dead test files
- CLEAN: 2 live test files (remove dead imports)

### Task 3 — Architecture Documented ✓
- This document: explains production pipeline, strategy dispatch, why src/ modules survived

### Task 4 — File Moves (Complete ✓)
- Move archived files to `_archive/`
- Update test imports in test_epic00_data_contracts.py, test_transliteration.py
- Verify diagnostic remains at 138/164 ✓
- Smoke test Flask routes end-to-end

---

## References

- **Routes:** [app/routes/](../app/routes/)
- **Normalisation Pipeline:** [app/pipeline/normalisation/](../app/pipeline/normalisation/)
- **Shared Modules:** [src/](../src/)
- **CI/CD:** [.github/workflows/regression.yml](../.github/workflows/regression.yml)
- **Diagnostics:** [run_integration_diagnostic.py](../run_integration_diagnostic.py)
- **Evaluation Framework:** [documentation/03-evaluation-framework.md](03-evaluation-framework.md)
