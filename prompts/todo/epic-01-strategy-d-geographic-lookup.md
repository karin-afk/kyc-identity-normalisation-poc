# Epic 04 — Strategy D: Geographic Lookup

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
