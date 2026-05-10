# 04 - Strategy D Geographic Lookup

## Scope

Strategy D introduces deterministic geographic normalisation for KYC field types that carry location or nationality data. All lookups run entirely in-memory with no database queries and no API calls at request time.

Supported field types:

- country
- country_of_residence
- nationality
- place_of_birth
- city

## Runtime flow

Execution order in router:

1. Strategy B (calendar/numeric)
2. Strategy C (vocabulary lookup)
3. Strategy D (geographic lookup)
4. Strategy A (preserve)
5. unresolved fallback

## Service design

Implementation file:

- app/pipeline/normalisation/geographic_lookup.py

Key behaviour:

- Builds four in-memory indexes once at app startup (or loads them from disk cache).
- Returns standard normalisation payload with processing_method=GEOGRAPHIC.
- Returns None for any field type not in the geographic field set, allowing the router to fall through to the next strategy.
- Confidence >= 0.99 for exact index hits, 0.90 for fuzzy pycountry fallback.

## Indexes

### Country index

Built from pycountry ISO 3166-1 + babel territory translations across 21 target locales:

- ar, zh, zh_TW, ja, ko, ru, uk, el, de, fr, es, it, tr, he, th, pt, nl, pl, sv, no, da

Each country is indexed under its English primary name, common name, official name, and the babel-generated name in every target locale. Hard-coded aliases handle common short forms (Russia, South Korea, Taiwan, Iran, etc.).

### Nationality index

Built from countryinfo demonyms. Maps English demonym strings (Japanese, German, Brazilian) to their ISO 2-letter country code. If the input does not match a demonym directly, the service falls back to a country lookup and derives the nationality from that.

### City index

Two data sources, selected at startup:

1. **GeoNames full dataset** (`data/geonames/allCountries.txt`, ~1.5 GB) — indexes ~5 million populated places including alternate names and transliterations. Covers city names in all scripts.
2. **geonamescache fallback** (~25,000 cities) — used automatically when the GeoNames file is absent. Covers major cities in English only. Population-based disambiguation ensures "Moscow" resolves to Russia (not Moscow, Idaho).

### Subdivision index

Built from pycountry ISO 3166-2 subdivisions (provinces, states, prefectures, regions). Also indexed via babel territory data where available.

## Disk cache

Geographic indexes are persisted to disk after the first build to avoid the ~30-second rebuild on every server restart.

Cache location:

- data/geo_cache/geo_index_v1_geonamescache.pkl (when using geonamescache)
- data/geo_cache/geo_index_v1_file_\<hash\>.pkl (when using GeoNames file)

Cache invalidation rules:

- The filename encodes `_CACHE_VERSION` — bump this constant in geographic_lookup.py to force a full rebuild after index logic changes.
- When using the GeoNames file, the filename also encodes the file's mtime and size. Replacing allCountries.txt automatically triggers a rebuild.
- Delete the data/geo_cache/ directory manually to force a rebuild at any time.

The cache directory is excluded from version control via .gitignore.

## App wiring

Flask startup registers the service singleton:

- app/__init__.py

`_register_services(app)` initialises `GeographicLookupService` with:

- `geonames_path` — from `app.config["GEONAMES_DATA_PATH"]` (defaults to data/geonames/allCountries.txt; gracefully absent)
- `cache_dir` — explicitly set to `data/geo_cache/` relative to the project root

The instance is stored on the app object as `app.geo_service` and retrieved inside the router via `current_app.geo_service`.

## GeoNames dataset (optional)

For full multilingual city coverage (Arabic, Japanese, Korean scripts etc.), download the GeoNames dataset:

1. Go to https://download.geonames.org/export/dump/
2. Download allCountries.zip
3. Unzip to data/geonames/allCountries.txt (~1.5 GB)

Without this file the service uses geonamescache and resolves ~25,000 major cities in English only. Country and nationality lookups are unaffected.
