# Epic — Strategy D: GeoNames Upgrade

## Save to: `prompts/todo/epic-strategy-d-geonames-upgrade.md`

---

## Implementation Checklist

- [x] 1. Write todos at top of epic file
- [x] 2. Rewrite `geographic_lookup.py` — module-level singleton pattern
      - `_ALIAS_INDEX`, `_CANONICAL_INDEX`, `_COUNTRY_BY_CODE`, `_ADMIN1_INDEX` dicts
      - `_ensure_index()` + `_BUILD_LOCK` thread-safe guard
      - `_build_country_data()` from `countryInfo.txt` + pycountry fallback
      - `_build_index()`: cities15000.txt → canonical, babel → country aliases, alternateNamesV2.txt → multilingual aliases, admin1CodesASCII.txt → admin1
      - `_load_or_build_index()` with pickle cache at `app/data/geo_cache/geo_index_v2_full.pkl`
      - `lookup_geographic(text, field_type, language, country)` public API
      - `_resolve_demonym_to_country(english_name, country_code)` via pycountry
      - `_normalise_text(text)` helper
      - `_build_result(original, normalised, confidence)` helper
      - `validate_hierarchy(city, region, country)` using CANONICAL + ADMIN1 indexes
      - `GeographicLookupService` thin shim for backwards-compat with app/__init__.py
      - `_SUPPLEMENTARY_NATIONALITY_ALIASES` dict for Arabic/Turkish adjectival forms
- [x] 3. Update `router.py` `_try_strategy_d()` — call `lookup_geographic()` directly
- [x] 4. Add `中国`, `ألمانيا`, `سعودي` examples to `field_type_detector.py`
- [x] 5. Create `tests/test_strategy_d_geographic.py`
      - D.7 expected form updated from `SAUDI ARABIAN` → `SAUDI ARABIA`
      - Fixed `run_integration_diagnostic.py` D.7 expected value to match
- [x] 6. Run integration diagnostic
      - D.5 ✅ now passes (中国 → CHINA)
      - D.7 ✅ lookup returns SAUDI ARABIA correctly; diagnostic expectation corrected
      - Score: 41/74 reported (42/74 effective after D.7 expectation fix)

---

## Context

Strategy D (geographic lookup) is implemented and wired. The diagnostic shows it
IS being called and IS returning results — but with two problems:

1. It returns demonyms instead of country names (`GERMAN` instead of `GERMANY`,
   `JAPANESE` instead of `JAPAN`)
2. It does not use `alternateNamesV2.txt` which contains the multilingual alias
   data needed to resolve `ألمانيا`, `Германия`, `日本` etc. reliably

Additionally, the current implementation is slow. Every lookup must be instant —
results must return in under 100ms. This is achieved by building a pre-computed
index at app startup (or on first request) and caching it in memory for the
lifetime of the process.

---

## New data file

```
data/geonames/alternateNamesV2.txt   ← already downloaded, ~1.5GB
data/geonames/allCountries.txt       ← already exists
data/geonames/admin1CodesASCII.txt   ← download from geonames.org if not present
data/geonames/countryInfo.txt        ← download from geonames.org if not present
```

Download URLs (if files are missing):
- `https://download.geonames.org/export/dump/admin1CodesASCII.txt`
- `https://download.geonames.org/export/dump/countryInfo.txt`

---

## What to build

### `app/pipeline/normalisation/geographic_lookup.py` — REPLACE existing implementation

The new implementation has three components:

---

### Component 1 — Index builder

Runs once at startup. Reads the GeoNames files and builds two in-memory dicts:

```python
# Dict 1: native/alternate name → canonical English name + metadata
# Key: lowercase normalised native name
# Value: {"english_name": str, "feature_class": str, "country_code": str,
#          "admin1": str, "geonameid": int}
ALIAS_INDEX: dict[str, dict] = {}

# Dict 2: geonameid → canonical English name
# Used for resolving after alias lookup
CANONICAL_INDEX: dict[int, dict] = {}
```

Build logic:

```python
def _build_index() -> tuple[dict, dict]:
    """
    Build ALIAS_INDEX and CANONICAL_INDEX from GeoNames data files.

    Steps:
    1. Read allCountries.txt → populate CANONICAL_INDEX with geonameid→record
       Filter to feature classes: A (administrative), P (populated place)
       Keep: geonameid, name, ascii_name, country_code, feature_class,
             feature_code, admin1_code, population

    2. Read alternateNamesV2.txt → populate ALIAS_INDEX
       For each row:
         - Skip if isolanguage is not in TARGET_LANGUAGES (see below)
         - Skip if geonameid not in CANONICAL_INDEX (not a place we care about)
         - Add: ALIAS_INDEX[normalise(alternate_name)] = CANONICAL_INDEX[geonameid]

    3. Read countryInfo.txt → build COUNTRY_BY_CODE: ISO2→{name, iso3, ...}

    4. Read admin1CodesASCII.txt → build ADMIN1_INDEX: "CC.A1"→english_name

    Return (ALIAS_INDEX, CANONICAL_INDEX)
    """
```

Target languages to index from alternateNamesV2.txt:
```python
TARGET_LANGUAGES = {
    "ar", "be", "bg", "da", "de", "el", "en", "es", "fa",
    "fr", "he", "it", "ja", "ko", "nl", "no", "pl", "pt",
    "ru", "sv", "th", "tr", "uk", "zh",
    "abbr",    # abbreviations (useful for country codes)
    "iata",    # airport codes (useful for city matching)
    "",        # unlabelled entries (often transliterations)
}
```

Performance requirement: the index must be built once and cached. Use a module-level
singleton pattern:

```python
_INDEX_BUILT = False
_ALIAS_INDEX: dict = {}
_CANONICAL_INDEX: dict = {}
_COUNTRY_BY_CODE: dict = {}
_ADMIN1_INDEX: dict = {}

def _ensure_index() -> None:
    """Build the index if not already built. Thread-safe via a lock."""
    global _INDEX_BUILT, _ALIAS_INDEX, _CANONICAL_INDEX
    if _INDEX_BUILT:
        return
    import threading
    with _BUILD_LOCK:
        if _INDEX_BUILT:  # double-check after acquiring lock
            return
        _ALIAS_INDEX, _CANONICAL_INDEX = _build_index()
        _INDEX_BUILT = True

_BUILD_LOCK = __import__("threading").Lock()
```

The index is also persisted to a pickle file in `app/data/geo_cache/` so that
subsequent app restarts load from cache (milliseconds) rather than rebuilding
from the raw text files (30–60 seconds).

Cache file: `app/data/geo_cache/geo_index_v2_full.pkl`

Cache invalidation: if the pkl file is older than any of the source txt files,
rebuild from scratch and overwrite the pkl.

```python
def _load_or_build_index() -> tuple[dict, dict, dict, dict]:
    """
    Load from pickle cache if fresh, otherwise build and save.
    Returns (alias_index, canonical_index, country_by_code, admin1_index)
    """
    import pickle
    from pathlib import Path

    cache_path = Path("app/data/geo_cache/geo_index_v2_full.pkl")
    source_files = [
        Path("data/geonames/allCountries.txt"),
        Path("data/geonames/alternateNamesV2.txt"),
        Path("data/geonames/countryInfo.txt"),
        Path("data/geonames/admin1CodesASCII.txt"),
    ]

    # Check if cache exists and is newer than all source files
    if cache_path.exists():
        cache_mtime = cache_path.stat().st_mtime
        sources_exist = all(p.exists() for p in source_files)
        if sources_exist:
            all_fresh = all(cache_mtime > p.stat().st_mtime for p in source_files
                           if p.exists())
        else:
            all_fresh = True  # missing sources, use whatever cache we have
        if all_fresh:
            with open(cache_path, "rb") as f:
                return pickle.load(f)

    # Build from scratch
    result = _build_index()
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_path, "wb") as f:
        pickle.dump(result, f, protocol=pickle.HIGHEST_PROTOCOL)
    return result
```

---

### Component 2 — Lookup function

```python
def lookup_geographic(
    text: str,
    field_type: str,
    language: str = "",
    country: str = "",
) -> dict | None:
    """
    Look up a geographic term and return its canonical English form.

    Supported field types:
        nationality, country_of_birth, country_of_residence,
        country_of_incorporation, country_of_registration,
        address, registered_address, business_address,
        place_of_birth, city, region

    Returns None if no match found (router falls through to next strategy).

    Lookup order:
        1. Exact match on normalised text in ALIAS_INDEX
        2. If field_type is nationality/* and result looks like a demonym,
           resolve to canonical country name (see Component 3)
        3. Partial/prefix match for longer strings (address fields)
        4. Return None if no confident match

    Confidence:
        - Exact alias match: 0.92
        - Demonym resolved to country: 0.88
        - Partial match: 0.75
    """
    _ensure_index()

    normalised = _normalise_text(text)
    if not normalised:
        return None

    # Step 1: exact alias lookup
    match = _ALIAS_INDEX.get(normalised)
    if match:
        english_name = match["english_name"]
        confidence = 0.92

        # Step 2: demonym resolution for nationality fields
        if field_type in NATIONALITY_FIELDS:
            resolved = _resolve_demonym_to_country(
                english_name, match.get("country_code", "")
            )
            if resolved:
                english_name = resolved
                confidence = 0.88

        return _build_result(text, english_name.upper(), confidence)

    # Step 3: for address fields, try component matching
    if field_type in ADDRESS_FIELDS and len(normalised) > 5:
        match = _partial_match(normalised)
        if match:
            return _build_result(text, match["english_name"].upper(), 0.75)

    return None


NATIONALITY_FIELDS = {
    "nationality", "country_of_birth", "country_of_residence",
    "country_of_incorporation", "country_of_registration",
}

ADDRESS_FIELDS = {
    "address", "registered_address", "business_address",
    "place_of_birth", "city", "region",
}
```

---

### Component 3 — Demonym resolver

```python
def _resolve_demonym_to_country(english_name: str, country_code: str) -> str | None:
    """
    Convert a demonym or adjectival form to the canonical country name.

    Uses pycountry as primary resolver, falls back to COUNTRY_BY_CODE.

    Examples:
        "GERMAN"    → "GERMANY"
        "JAPANESE"  → "JAPAN"
        "FRENCH"    → "FRANCE"
        "EMIRATI"   → "UNITED ARAB EMIRATES"
        "SAUDI"     → "SAUDI ARABIA"
        "RUSSIAN"   → "RUSSIA"

    If country_code is known (from the GeoNames record), use it directly
    to look up the canonical name — this is more reliable than fuzzy matching.

    Args:
        english_name: The English name returned by the alias lookup.
        country_code: ISO 3166-1 alpha-2 country code from the GeoNames record.

    Returns:
        Canonical country name string, or None if cannot resolve.
    """
    # Primary: use country_code from GeoNames record if available
    if country_code and len(country_code) == 2:
        try:
            import pycountry
            country = pycountry.countries.get(alpha_2=country_code.upper())
            if country:
                return country.name.upper()
        except Exception:
            pass

    # Fallback: fuzzy match the english_name against pycountry
    try:
        import pycountry
        results = pycountry.countries.search_fuzzy(english_name)
        if results:
            return results[0].name.upper()
    except Exception:
        pass

    return None
```

---

### Component 4 — Text normalisation helper

```python
def _normalise_text(text: str) -> str:
    """
    Normalise text for index lookup.
    - Strip leading/trailing whitespace
    - Lowercase
    - Normalise unicode (NFC)
    - Remove diacritics from Latin text (for fuzzy matching)
    - Do NOT strip non-Latin characters (Arabic, CJK, Cyrillic must be preserved)
    """
    import unicodedata
    text = text.strip().lower()
    text = unicodedata.normalize("NFC", text)
    return text
```

---

### Component 5 — Result builder

```python
def _build_result(original: str, normalised: str, confidence: float) -> dict:
    from app.pipeline.normalisation.field_types import ProcessingMethod, STRATEGY_CONFIDENCE
    return {
        "original_text":           original,
        "normalised_form":         normalised,
        "allowed_variants":        [],
        "processing_method":       ProcessingMethod.GEOGRAPHIC,
        "confidence":              confidence,
        "review_required":         confidence < 0.85,
        "review_reason":           None if confidence >= 0.85 else "Low confidence geographic match — verify",
        "should_use_in_screening": True,
    }
```

---

### Component 6 — Hierarchy validation

```python
def validate_hierarchy(city: str, region: str, country: str) -> tuple[bool, str | None]:
    """
    Validate that a city belongs to the stated region and country.
    Used by the document pipeline to flag inconsistent addresses.

    Returns (is_valid, reason).
    reason is None if valid, a string explanation if invalid.

    Example:
        validate_hierarchy("Tokyo", "Osaka", "Japan") →
        (False, "Tokyo is in Tokyo Prefecture, not Osaka Prefecture")

        validate_hierarchy("Tokyo", "Tokyo", "Japan") →
        (True, None)
    """
    _ensure_index()
    # Look up city in alias index
    city_norm = _normalise_text(city)
    city_record = _ALIAS_INDEX.get(city_norm)
    if not city_record:
        return (True, None)  # cannot validate — pass through

    # Check country
    record_country = _COUNTRY_BY_CODE.get(city_record.get("country_code", ""), {})
    record_country_name = record_country.get("name", "").upper()
    if country.upper() not in (record_country_name, city_record.get("country_code", "")):
        return (False, f"{city} is in {record_country_name}, not {country}")

    # Check admin1 (region/prefecture/province)
    admin1_key = f"{city_record['country_code']}.{city_record.get('admin1_code', '')}"
    admin1_english = _ADMIN1_INDEX.get(admin1_key, "")
    if admin1_english and region.upper() not in admin1_english.upper():
        return (False, f"{city} is in {admin1_english}, not {region}")

    return (True, None)
```

---

### Router wiring — `app/pipeline/normalisation/router.py`

Replace `_try_strategy_d()` stub with:

```python
def _try_strategy_d(text: str, field_type: str, language: str,
                    country: str) -> dict | None:
    """Strategy D — GeoNames geographic lookup."""
    try:
        from app.pipeline.normalisation.geographic_lookup import lookup_geographic
        return lookup_geographic(text, field_type, language, country)
    except Exception:
        return None
```

Ensure `_try_strategy_d` is called for these field types (add to the router's
field-type routing logic if not already present):

```python
GEOGRAPHIC_FIELDS = {
    "nationality", "country_of_birth", "country_of_residence",
    "country_of_incorporation", "country_of_registration",
    "address", "registered_address", "business_address",
    "place_of_birth", "city", "region",
}
```

---

## Performance requirements

- First lookup after cold start: index loads from pickle cache in < 2 seconds
- Subsequent lookups: < 50ms (in-memory dict lookup)
- Index rebuild from raw text files: acceptable to take 60–120 seconds, but this
  only happens when source files change (rare)
- On app startup, log: `"Geographic index loaded: {N} aliases, {M} canonical entries"`

---

## Tests — `tests/test_strategy_d_geographic.py`

All tests use real lookup — no mocks. The index must be loaded.

```python
from app.pipeline.normalisation.geographic_lookup import lookup_geographic, validate_hierarchy
from app import create_app

import pytest

@pytest.fixture(scope="module")
def app_context():
    app = create_app("testing")
    ctx = app.app_context()
    ctx.push()
    yield
    ctx.pop()

# ── Country name resolution ────────────────────────────────────────────────────

def test_arabic_germany(app_context):
    r = lookup_geographic("ألمانيا", "nationality", "ar")
    assert r is not None
    assert r["normalised_form"] == "GERMANY"
    assert r["processing_method"] == "GEOGRAPHIC"

def test_japanese_japan(app_context):
    r = lookup_geographic("日本", "nationality", "ja")
    assert r is not None
    assert r["normalised_form"] == "JAPAN"

def test_russian_germany(app_context):
    r = lookup_geographic("Германия", "nationality", "ru")
    assert r is not None
    assert r["normalised_form"] == "GERMANY"

def test_greek_germany(app_context):
    r = lookup_geographic("Γερμανία", "nationality", "el")
    assert r is not None
    assert r["normalised_form"] == "GERMANY"

def test_chinese_china(app_context):
    r = lookup_geographic("中国", "nationality", "zh")
    assert r is not None
    assert r["normalised_form"] == "CHINA"

def test_arabic_cairo(app_context):
    r = lookup_geographic("القاهرة", "city", "ar")
    assert r is not None
    assert r["normalised_form"] == "CAIRO"

def test_japanese_tokyo(app_context):
    r = lookup_geographic("東京", "city", "ja")
    assert r is not None
    assert r["normalised_form"] == "TOKYO"

def test_russian_moscow(app_context):
    r = lookup_geographic("Москва", "city", "ru")
    assert r is not None
    assert r["normalised_form"] == "MOSCOW"

def test_german_munich(app_context):
    r = lookup_geographic("München", "city", "de")
    assert r is not None
    assert r["normalised_form"] == "MUNICH"

# ── Demonym resolution ─────────────────────────────────────────────────────────

def test_demonym_german_resolves_to_germany(app_context):
    # If lookup returns GERMAN, it must resolve to GERMANY for nationality fields
    r = lookup_geographic("ألمانيا", "nationality", "ar")
    assert r["normalised_form"] == "GERMANY"
    assert "GERMAN" not in r["normalised_form"]  # must not return adjectival form

def test_demonym_japanese_resolves_to_japan(app_context):
    r = lookup_geographic("日本", "nationality", "ja")
    assert r["normalised_form"] == "JAPAN"
    assert "JAPANESE" not in r["normalised_form"]

# ── Returns None for non-geographic text ──────────────────────────────────────

def test_returns_none_for_person_name(app_context):
    assert lookup_geographic("田中", "person_name", "ja") is None

def test_returns_none_for_legal_form(app_context):
    assert lookup_geographic("GmbH", "legal_form", "de") is None

def test_returns_none_for_unknown_text(app_context):
    assert lookup_geographic("xyzxyzxyz", "nationality", "en") is None

# ── Hierarchy validation ───────────────────────────────────────────────────────

def test_valid_hierarchy_tokyo_japan(app_context):
    valid, reason = validate_hierarchy("Tokyo", "Tokyo", "Japan")
    assert valid is True
    assert reason is None

def test_invalid_hierarchy_tokyo_osaka(app_context):
    valid, reason = validate_hierarchy("Tokyo", "Osaka", "Japan")
    assert valid is False
    assert reason is not None
    assert "Tokyo" in reason

def test_invalid_country(app_context):
    valid, reason = validate_hierarchy("Paris", "Île-de-France", "Germany")
    assert valid is False

# ── Performance ────────────────────────────────────────────────────────────────

def test_lookup_is_fast(app_context):
    import time
    # Warm up (index already loaded by previous tests)
    start = time.time()
    for _ in range(100):
        lookup_geographic("日本", "nationality", "ja")
    elapsed = time.time() - start
    assert elapsed < 1.0, f"100 lookups took {elapsed:.2f}s — must be under 1s total"
```

---

## Acceptance criteria

- `lookup_geographic("ألمانيا", "nationality", "ar")` returns `GERMANY` not `GERMAN`
- `lookup_geographic("日本", "nationality", "ja")` returns `JAPAN` not `JAPANESE`
- `lookup_geographic("東京", "city", "ja")` returns `TOKYO`
- `lookup_geographic("Москва", "city", "ru")` returns `MOSCOW`
- `lookup_geographic("München", "city", "de")` returns `MUNICH`
- 100 consecutive lookups complete in under 1 second (in-memory index)
- App startup logs the index size: `"Geographic index loaded: N aliases, M canonical entries"`
- Cache pickle is written to `app/data/geo_cache/geo_index_v2_full.pkl` on first build
- Subsequent app restarts load from pickle — no 60-second rebuild
- `validate_hierarchy("Tokyo", "Osaka", "Japan")` returns `(False, <reason>)`
- All tests in `tests/test_strategy_d_geographic.py` pass
- No imports from `src/` at runtime
