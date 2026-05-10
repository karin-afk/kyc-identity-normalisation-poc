# Epic 04 — Strategy D: Geographic Lookup

**Status: ✅ IMPLEMENTED** — committed `44b8edb` on `feat/integration-diagnostic` (2026-05-10)

> This epic was superseded by `epic-04-strategy-d-geonames-upgrade.md`, which documents the actual implementation.
> The module-level singleton approach replaced the class-based design described here.

## Todo list

### 0. Prerequisites — verify what already exists before writing any code

- [ ] Confirm `ProcessingMethod.GEOGRAPHIC` is defined in `app/pipeline/normalisation/field_types.py`. If missing, add it alongside the existing `ProcessingMethod` entries.
- [ ] Confirm `STRATEGY_CONFIDENCE` dict exists in `field_types.py` and has a `"GEOGRAPHIC"` key. If missing, add entry (suggested value: `0.90`).
- [ ] Confirm `GEOGRAPHIC_FIELDS = ["nationality", "country", "country_of_residence", "place_of_birth", "city"]` is defined in `field_types.py`. It is referenced in `epic-01-strategy-a-preserve.md` but verify it is present in the actual file.
- [ ] Confirm `GEONAMES_DATA_PATH` is present in `app/config.py` for all three configs (`development`, `testing`, `production`). The key already exists in `app.config` per `test_epic00_data_contracts.py` — just verify the default value for `testing` is `""` or `None` (not a real path).
- [ ] Confirm `data/geonames/` directory exists or add it to `.gitignore` (the file itself is 1.5 GB and must not be committed).
- [ ] Add four libraries to `requirements.txt`: `pycountry>=24.6.1`, `babel>=2.16.0`, `geonamescache>=1.6.0`, `countryinfo>=0.1.2`.
- [ ] Run `C:\Python314\python.exe -m pip install pycountry babel geonamescache countryinfo` to install them locally.

---

### 1. Implement `app/pipeline/normalisation/geographic_lookup.py`

The file currently contains a 4-line stub. Replace it entirely.

- [ ] Define class `GeographicLookupService` with class attribute `TARGET_LOCALES` (21 locales as specified).
- [ ] Implement `__init__(self, geonames_path=None)`: initialise four empty index dicts, then call all four `_build_*` methods in order.
- [ ] Implement `lookup(field_type, text, language, country)`: gate on `GEOGRAPHIC_FIELDS`; route to `lookup_nationality`, `lookup_country`, or `lookup_place` based on field type; return `None` for unrecognised fields.
- [ ] Implement `lookup_country(text)`: try (1) normalised exact match in `_country_index`, (2) NFKD + ASCII + lowercase match, (3) `pycountry.countries.search_fuzzy()` with confidence >= 0.90 threshold. Return `None` if all three miss.
- [ ] Implement `lookup_nationality(text, language)`: check `_nationality_index`; if miss, fall back to `lookup_country()` and derive demonym from result. Return `None` if both miss.
- [ ] Implement `lookup_place(text)`: try (1) `_city_index` exact match, (2) geonamescache fallback, (3) `_subdivision_index`. Return `None` if all three miss.
- [ ] Implement `_build_country_index()`: for each ISO 3166-1 country, use babel to generate country name in each `TARGET_LOCALE`; index every generated name (lowercased) → `{name_en, iso2, iso3}`. Add hard-coded common English aliases (Russia/Russian Federation, South Korea/Republic of Korea, etc.). Swallow babel errors per locale with a `log.warning`, do not raise.
- [ ] Implement `_build_nationality_index()`: use countryinfo to get demonym per country; index normalised demonym → `{english_nationality, iso2}`.
- [ ] Implement `_build_city_index(geonames_path)`: if file exists, parse `allCountries.txt` (tab-separated, 19 columns, 0-based); index `name` (col 1), `asciiname` (col 2), and each `alternatename` (col 3 comma-split) for rows with `population > 0`; skip rows where name or asciiname is empty. If file is absent, log the specified warning and load `geonamescache.GeonamesCache().get_cities()` instead.
- [ ] Implement `_build_subdivision_index()`: use `pycountry.subdivisions` to index subdivision names → `{name_en, country_code, subdivision_type}`.
- [ ] Implement `@staticmethod _build_result(normalised_form, confidence, **extra)`: return the standard result dict as specified, with `processing_method = ProcessingMethod.GEOGRAPHIC`, `review_required = confidence < 0.90`, `should_use_in_screening = True`.

---

### 2. Wire `GeographicLookupService` into the router

- [ ] In `router.py`, add `_try_strategy_d(text, field_type, language, country)` following the same pattern as `_try_strategy_c` — import the service instance, call `service.lookup()`, handle `None` return.
- [ ] In `route_field()`, call `_try_strategy_d()` after `_try_strategy_c()` and before the existing `_try_stub()` loop.
- [ ] Remove `"D"` / `"geographic_lookup"` from the `_try_stub()` loop (it is currently in the loop at line 81 of `router.py`).
- [ ] Add `log_event("router_selected_strategy", {"strategy": "D", ...})` on successful match, consistent with Strategy B and C logging.

---

### 3. Wire service instantiation into the app factory

- [ ] In `app/__init__.py` / `create_app()`, instantiate `GeographicLookupService` once after the app is configured, reading `geonames_path = app.config.get("GEONAMES_DATA_PATH") or None`.
- [ ] Store the instance on the app (e.g. `app.geo_service = GeographicLookupService(geonames_path)`) so `_try_strategy_d()` can retrieve it via `current_app.geo_service`.
- [ ] For `testing` config, confirm instantiation completes without error when `GEONAMES_DATA_PATH` is empty (geonamescache fallback path).

---

### 4. Write `tests/test_strategy_d_geographic.py` (Category 1 — strategy unit tests)

No mocks. Call `route_field()` or the service directly with real inputs. Assert on exact values.

**Country lookup (9 tests):**
- [ ] `test_country_english_name` — `"Germany"` → `iso2 == "DE"`
- [ ] `test_country_arabic` — `"ألمانيا"` → `normalised_form == "GERMANY"`
- [ ] `test_country_japanese` — `"日本"` → `normalised_form == "JAPAN"`, `iso2 == "JP"`
- [ ] `test_country_korean` — `"대한민국"` → `normalised_form == "SOUTH KOREA"` (or canonical English form from pycountry)
- [ ] `test_country_russian` — `"Германия"` → `normalised_form == "GERMANY"`
- [ ] `test_country_greek` — `"Γερμανία"` → `normalised_form == "GERMANY"`
- [ ] `test_country_common_alias` — `"Russia"` → resolves to Russian Federation entry, `iso2 == "RU"`
- [ ] `test_country_no_match_returns_none` — `"Ruritania"` → `None`
- [ ] `test_country_result_has_iso2_and_iso3` — result dict contains both `iso2` and `iso3` keys

**Nationality lookup (4 tests):**
- [ ] `test_nationality_english` — `"Japanese"` → `normalised_form == "JAPANESE"`
- [ ] `test_nationality_arabic_demonym` — `"ياباني"` → `normalised_form == "JAPANESE"`
- [ ] `test_nationality_fallback_to_country` — `"Japan"` resolves via country → `normalised_form == "JAPANESE"`
- [ ] `test_nationality_no_match_returns_none` — random string → `None`

**Place lookup (5 tests):**
- [ ] `test_city_english` — `"Tokyo"` → `country_code == "JP"`
- [ ] `test_city_japanese` — `"東京"` → `normalised_form == "TOKYO"`
- [ ] `test_city_arabic` — `"القاهرة"` → `normalised_form == "CAIRO"`
- [ ] `test_city_alternate_name` — `"Moskva"` → `normalised_form == "MOSCOW"`
- [ ] `test_city_fallback_without_geonames_file` — service instantiated with `geonames_path=None`, `"Tokyo"` still resolves

**Subdivision lookup (2 tests):**
- [ ] `test_subdivision_japanese_prefecture` — `"東京都"` → `normalised_form == "TOKYO"`
- [ ] `test_subdivision_german_state` — `"Bayern"` → `normalised_form == "BAVARIA"`

**Router integration (2 tests):**
- [ ] `test_returns_none_for_non_geographic_field` — `route_field({"original_text": "GmbH", "field_type": "legal_form", "country": "DE"})` → `processing_method != "GEOGRAPHIC"`
- [ ] `test_returns_none_for_name_field` — `route_field({"original_text": "محمد", "field_type": "person_name"})` → `processing_method != "GEOGRAPHIC"`

**Index building (3 tests):**
- [ ] `test_service_initialises_without_geonames` — `GeographicLookupService(geonames_path=None)` completes without exception
- [ ] `test_service_initialises_with_geonames(tmp_path)` — write a minimal 2-row TSV to `tmp_path / "allCountries.txt"`, confirm service loads it without exception
- [ ] `test_country_index_covers_target_locales` — after init, Arabic `"ألمانيا"`, Japanese `"日本"`, Russian `"Германия"` all resolve (checks the index was actually built)

---

### 5. Extend `tests/test_e2e_pipeline.py` (Category 3 — end-to-end, zero mocks)

- [ ] `test_e2e_country_arabic` — `process_field_row({"original_text": "ألمانيا", "field_type": "country", "language": "ar"})` → `normalised_form == "GERMANY"`, `processing_method == "GEOGRAPHIC"`
- [ ] `test_e2e_country_japanese` — `"日本"` + `field_type="country"` → `normalised_form == "JAPAN"`
- [ ] `test_e2e_nationality_english` — `"Japanese"` + `field_type="nationality"` → `normalised_form == "JAPANESE"`
- [ ] `test_e2e_place_of_birth_japanese` — `"東京"` + `field_type="place_of_birth"` → `normalised_form == "TOKYO"`

---

### 6. Run tests and commit

- [x] Run `& "C:\Python314\python.exe" -m pytest tests/test_strategy_d_geographic.py -v` — all 25 tests must pass.
- [x] Run full suite `& "C:\Python314\python.exe" -m pytest -q` — no regressions against current 162-test baseline.
- [x] `git add` only: `app/pipeline/normalisation/geographic_lookup.py`, `app/pipeline/normalisation/router.py`, `app/__init__.py`, `requirements.txt`, `tests/test_strategy_d_geographic.py`, `tests/test_e2e_pipeline.py`.
- [x] Commit: `feat(strategy-d): implement geographic lookup service with country, nationality, and place indexes`.
- [x] Push to `origin/feat/strategy-d-geographic-lookup` (new branch from `dev`).

---

### 7. Disk cache for geographic indexes ✅ IMPLEMENTED

Avoids the ~30-second index rebuild on every server restart by persisting the four
in-memory dictionaries to a pickle file after the first build.

- [x] Add `import hashlib` and `import pickle` to `geographic_lookup.py`.
- [x] Add `_CACHE_VERSION = "1"` constant — bump this whenever index-building logic changes to force a rebuild.
- [x] Extend `GeographicLookupService.__init__` with `cache_dir: Path | str | None = None` parameter.
- [x] On startup: resolve cache file path → if exists, load and return early; if missing or corrupt, rebuild then save.
- [x] `_resolve_cache_file()` — encodes geonames source (file mtime+size hash, or `"geonamescache"`) and `_CACHE_VERSION` in the filename so stale caches are never silently reused.
- [x] `_load_from_cache()` — deserialises all five dicts (`country`, `nationality`, `city`, `subdivision`, `iso2_to_nationality`) from the pickle file.
- [x] `_save_to_cache()` — creates `data/geo_cache/` if absent, serialises with `pickle.HIGHEST_PROTOCOL`.
- [x] Update `app/__init__.py` `_register_services()` to pass `cache_dir = Path(app.root_path).parent / "data" / "geo_cache"` explicitly.
- [x] Add `data/geo_cache/` to `.gitignore` (cache files are machine-generated and must not be committed).

**Result:** First startup builds indexes and writes `data/geo_cache/geo_index_v1_geonamescache.pkl`.
Every subsequent restart loads from that file in under one second.

---

## What you need to provide

### Download: GeoNames full dataset

**Save to:** `data/geonames/allCountries.txt`

1. Go to https://download.geonames.org/export/dump/
2. Download `allCountries.zip`
3. Unzip — you get `allCountries.txt` (~1.5GB)
4. Run `mkdir -p data/geonames` then save the file there

This is the only item you need to provide. Everything else is built by Copilot using the `pycountry`, `babel`, `geonamescache`, and `countryinfo` Python libraries, which contain their own bundled data.

---

## What exists in the current codebase

Nothing. Strategy D does not exist in any form. Entirely new build.

---

## What this epic builds

### `app/pipeline/normalisation/geographic_lookup.py` — NEW FILE

```python
"""
Strategy D — Geographic Lookup.

Resolves country names, nationality demonyms, and place names from
authoritative reference data. All lookups are in-memory — no database
queries, no API calls at request time.

The service builds three indexes at startup:
  1. Country index — maps country names in any script/language to English
     name and ISO codes. Built from pycountry + babel.
  2. City index — maps city and town names to English form and country.
     Built from GeoNames full dataset if available, geonamescache otherwise.
  3. Subdivision index — maps province, region, and prefecture names to
     English form. Built from pycountry ISO 3166-2 subdivisions.

Startup time is approximately 10–30 seconds on first run while indexes build.
Indexes are held in memory for the lifetime of the process.
"""

from pathlib import Path
from app.pipeline.normalisation.field_types import (
    GEOGRAPHIC_FIELDS, ProcessingMethod, STRATEGY_CONFIDENCE
)


class GeographicLookupService:

    # Target locales for babel country name generation.
    # These are the scripts/languages for which we build the reverse lookup index.
    TARGET_LOCALES: list[str] = [
        "ar", "zh", "zh_TW", "ja", "ko", "ru", "uk", "el",
        "de", "fr", "es", "it", "tr", "he", "th", "pt", "nl",
        "pl", "sv", "no", "da",
    ]

    def __init__(self, geonames_path: str | None = None):
        """
        Build all indexes at startup.

        Args:
            geonames_path: Path to GeoNames allCountries.txt.
                           If None or file missing, falls back to geonamescache
                           and logs a warning. The tool works without this file
                           but place-of-birth lookups are limited to cities
                           above ~15,000 population.
        """
        self._country_index: dict[str, dict] = {}
        self._nationality_index: dict[str, dict] = {}
        self._city_index: dict[str, dict] = {}
        self._subdivision_index: dict[str, dict] = {}

        self._build_country_index()
        self._build_nationality_index()
        self._build_city_index(geonames_path)
        self._build_subdivision_index()

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def lookup(self, field_type: str, text: str, language: str = "", country: str = "") -> dict | None:
        """
        Main entry point called by the normalisation router.

        Routes to the correct sub-lookup based on field_type.
        Returns None if field_type is not a geographic field or no match found.
        """
        if field_type not in GEOGRAPHIC_FIELDS:
            return None

        if field_type in ("nationality",):
            return self.lookup_nationality(text, language)

        if field_type in ("country", "country_of_residence"):
            return self.lookup_country(text)

        if field_type in ("place_of_birth", "city"):
            return self.lookup_place(text)

        return None

    # ------------------------------------------------------------------
    # Country lookup
    # ------------------------------------------------------------------

    def lookup_country(self, text: str) -> dict | None:
        """
        Match a country name in any script or language to its English name
        and ISO codes.

        Matching strategy (tried in order):
        1. Exact match in the country index (normalised key)
        2. Normalised match (NFKD + ASCII + lowercase)
        3. pycountry.countries.search_fuzzy() fallback
           — only used if confidence would be >= 0.90

        Returns:
            {normalised_form, iso2, iso3, confidence, ...} or None
        """

    # ------------------------------------------------------------------
    # Nationality lookup
    # ------------------------------------------------------------------

    def lookup_nationality(self, text: str, language: str = "") -> dict | None:
        """
        Resolve a nationality demonym in any language to its English form.

        Uses the countryinfo library for demonym data.
        Example: "ياباني" (ar) → "JAPANESE"
        Example: "日本人" (ja) → "JAPANESE"

        Falls back to country lookup if demonym not found
        (e.g. "Japan" → country lookup → "JAPANESE" via demonym).
        """

    # ------------------------------------------------------------------
    # Place name lookup
    # ------------------------------------------------------------------

    def lookup_place(self, text: str) -> dict | None:
        """
        Match a city, town, or village name to its English form and country.

        Matching strategy (tried in order):
        1. Exact match in city index (normalised key) from GeoNames
        2. Exact match in geonamescache fallback
        3. Subdivision match (for prefecture/province names)

        GeoNames index includes:
        - Primary name (name column)
        - ASCII name (asciiname column)
        - Alternate names (alternatenames column, pipe-separated)
        All three are indexed for each place entry.

        Returns:
            {normalised_form, country_code, confidence, ...} or None
        """

    # ------------------------------------------------------------------
    # Index builders — called once at startup
    # ------------------------------------------------------------------

    def _build_country_index(self):
        """
        Build the country reverse-lookup index.

        For each ISO 3166-1 country, use babel to generate the country name
        in each of TARGET_LOCALES. Index every generated name (normalised to
        lowercase + stripped) → {name_en, iso2, iso3}.

        Also index English aliases and common variant names:
        - "Russia" and "Russian Federation"
        - "South Korea" and "Republic of Korea"
        - "North Korea" and "Democratic People's Republic of Korea"
        - "Taiwan" and "Republic of China"
        - "Iran" and "Islamic Republic of Iran"
        - "Syria" and "Syrian Arab Republic"
        etc.

        If babel raises an error for a specific locale + country combination,
        log a warning and continue — do not raise.
        """

    def _build_nationality_index(self):
        """
        Build the nationality demonym index using countryinfo.

        For each country, retrieve the demonym (e.g. "German" for DE).
        Also generate demonyms in target languages using babel locale data
        where available.

        Index: normalised demonym → {english_nationality, iso2}
        """

    def _build_city_index(self, geonames_path: str | None):
        """
        Build the city/place name index.

        If geonames_path is provided and the file exists:
        - Parse allCountries.txt (tab-separated, see GeoNames readme)
        - Index columns: name (col 1), asciiname (col 2),
          alternatenames (col 3, comma-separated), countryCode (col 8)
        - Only load rows where population (col 14) > 0
        - For each row, index: name, asciiname, and each alternate name
          → {name_en: asciiname, country_code: countryCode}
        - Skip rows where name or asciiname is empty

        If geonames_path is None or file not found:
        - Log: "GeoNames file not found at {path}. Falling back to
          geonamescache (~25,000 cities). Place-of-birth lookups for
          small towns and villages will not resolve automatically."
        - Load geonamescache.GeonamesCache().get_cities() instead

        GeoNames file format reference:
        https://download.geonames.org/export/dump/readme.txt
        Column indices (0-based): 0=geonameid, 1=name, 2=asciiname,
        3=alternatenames, 4=latitude, 5=longitude, 6=feature_class,
        7=feature_code, 8=country_code, 9=cc2, 10=admin1_code,
        11=admin2_code, 12=admin3_code, 13=admin4_code, 14=population,
        15=elevation, 16=dem, 17=timezone, 18=modification_date
        """

    def _build_subdivision_index(self):
        """
        Build the administrative subdivision index.

        Use pycountry.subdivisions to index province, region, prefecture,
        and state names → {name_en, country_code, subdivision_type}.

        Also generate subdivision names in target languages using babel
        where locale data is available.
        """

    @staticmethod
    def _build_result(normalised_form: str, confidence: float, **extra) -> dict:
        """Build a standard result dict for a successful geographic lookup."""
        return {
            "normalised_form":          normalised_form,
            "allowed_variants":         [],
            "processing_method":        ProcessingMethod.GEOGRAPHIC,
            "confidence":               confidence,
            "review_required":          confidence < 0.90,
            "review_reason":            None if confidence >= 0.90 else "Geographic lookup confidence below threshold",
            "should_use_in_screening":  True,
            **extra,
        }
```

### `requirements.txt` additions

```
pycountry>=24.6.1
babel>=2.16.0
geonamescache>=1.6.0
countryinfo>=0.1.2
```

### Application startup wiring

`GeographicLookupService` is instantiated once at app startup. The `geonames_path` is read from the `GEONAMES_DATA_PATH` environment variable (already in `.env.example`). Copilot adds instantiation to the app factory in Epic 12. For this epic, test directly without Flask.

---

## Tests

`tests/test_strategy_d_geographic.py`

```python
# --- Country lookup ---
def test_country_english_name(): ...                  # "Germany" → iso2="DE"
def test_country_arabic(): ...                        # "ألمانيا" → "Germany"
def test_country_japanese(): ...                      # "日本" → "Japan"
def test_country_korean(): ...                        # "대한민국" → "South Korea"
def test_country_russian(): ...                       # "Германия" → "Germany"
def test_country_greek(): ...                         # "Γερμανία" → "Germany"
def test_country_common_alias(): ...                  # "Russia" → "Russian Federation"
def test_country_no_match_returns_none(): ...         # "Ruritania" → None
def test_country_result_has_iso2_and_iso3(): ...

# --- Nationality lookup ---
def test_nationality_english(): ...                   # "Japanese" → "JAPANESE"
def test_nationality_arabic_demonym(): ...            # "ياباني" → "JAPANESE"
def test_nationality_fallback_to_country(): ...       # "Japan" resolves via country → "JAPANESE"
def test_nationality_no_match_returns_none(): ...

# --- Place lookup ---
def test_city_english(): ...                          # "Tokyo" → country_code="JP"
def test_city_japanese(): ...                         # "東京" → "Tokyo"
def test_city_arabic(): ...                           # "القاهرة" → "Cairo"
def test_city_alternate_name(): ...                   # "Moskva" → "Moscow"
def test_city_fallback_without_geonames_file(): ...   # gracefully uses geonamescache

# --- Subdivision lookup ---
def test_subdivision_japanese_prefecture(): ...       # "東京都" → "Tokyo"
def test_subdivision_german_state(): ...              # "Bayern" → "Bavaria"

# --- Router integration ---
def test_returns_none_for_non_geographic_field(): ... # "legal_form" → None
def test_returns_none_for_name_field(): ...           # "person_name" → None

# --- Index building ---
def test_service_initialises_without_geonames(): ...  # works with geonamescache fallback
def test_service_initialises_with_geonames(tmp_path): ... # works with real file
def test_country_index_covers_target_locales(): ...   # Arabic, Japanese, Russian all indexed
```

---

## Acceptance criteria

- `service.lookup("country", "ألمانيا")` returns `normalised_form == "GERMANY"` and `iso2 == "DE"`.
- `service.lookup("country", "日本")` returns `normalised_form == "JAPAN"` and `iso2 == "JP"`.
- `service.lookup("place_of_birth", "東京")` returns `normalised_form == "TOKYO"` and `country_code == "JP"`.
- `service.lookup("nationality", "Japanese")` returns `normalised_form == "JAPANESE"`.
- `service.lookup("legal_form", "GmbH", country="DE")` returns `None` — legal forms are not a geographic field.
- Service initialises without error when GeoNames file is absent (fallback to geonamescache with logged warning).
- Service initialises without error when GeoNames file is present.
- All tests pass.
- No LLM is called at any point.
- Four new libraries added to `requirements.txt`.
