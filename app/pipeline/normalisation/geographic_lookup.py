"""
Strategy D — Geographic Lookup v2 (GeoNames-backed).

Resolves country names, city names, and nationality terms from authoritative
GeoNames data. All lookups are in-memory after index build.

Index build strategy:
  1. Country data    — countryInfo.txt + pycountry fallback
  2. Country aliases — babel localised territory names (all target languages)
  3. City canonical  — cities15000.txt (places with population ≥ 15,000)
  4. City aliases    — alternateNamesV2.txt filtered to cities15000 geoids
  5. Admin1 regions  — admin1CodesASCII.txt

First build: 30–90 seconds (738 MB alternateNamesV2.txt read).
Subsequent starts: pickle cache loads in < 2 seconds.
"""

from __future__ import annotations

import logging
import pickle
import threading
import unicodedata
from pathlib import Path

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

# app/pipeline/normalisation/ → app/pipeline/ → app/ → project root
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_DATA_DIR = _PROJECT_ROOT / "data" / "geonames"
_CACHE_FILE = _PROJECT_ROOT / "app" / "data" / "geo_cache" / "geo_index_v2_full.pkl"

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

TARGET_LANGUAGES: frozenset[str] = frozenset(
    {
        "ar", "be", "bg", "da", "de", "el", "en", "es", "fa",
        "fr", "he", "it", "ja", "ko", "nl", "no", "pl", "pt",
        "ru", "sv", "th", "tr", "uk", "zh",
        "abbr",   # country/airport abbreviations
        "iata",   # IATA airport codes (useful for city matching)
        "",       # unlabelled entries (transliterations etc.)
    }
)

# Locales fed to babel for country name localisation
_BABEL_LOCALES: list[str] = [
    "ar", "zh", "zh_TW", "ja", "ko", "ru", "uk", "el",
    "de", "fr", "es", "it", "tr", "he", "th", "pt", "nl",
    "pl", "sv", "no", "da", "fa", "be", "bg",
]

NATIONALITY_FIELDS: frozenset[str] = frozenset(
    {
        "nationality",
        "country_of_birth",
        "country_of_residence",
        "country_of_incorporation",
        "country_of_registration",
    }
)

ADDRESS_FIELDS: frozenset[str] = frozenset(
    {
        "address",
        "registered_address",
        "business_address",
        "place_of_birth",
        "city",
        "region",
    }
)

GEOGRAPHIC_FIELDS: frozenset[str] = NATIONALITY_FIELDS | ADDRESS_FIELDS

# ---------------------------------------------------------------------------
# Module-level singleton indexes
# ---------------------------------------------------------------------------

_ALIAS_INDEX: dict[str, dict] = {}
"""normalised_text → {english_name, country_code, feature, [geonameid, admin1_code]}"""

_CANONICAL_INDEX: dict[int, dict] = {}
"""geonameid → {name_en, country_code, admin1_code, feature}"""

_COUNTRY_BY_CODE: dict[str, dict] = {}
"""ISO2 → {name, iso3, geonameid}"""

_ADMIN1_INDEX: dict[str, str] = {}
"""'CC.A1' → english_name  (e.g. 'JP.13' → 'Tokyo')"""

_INDEX_BUILT = False
_BUILD_LOCK = threading.Lock()

# ---------------------------------------------------------------------------
# Supplementary nationality adjective aliases
#
# GeoNames stores place *names*, not nationality adjectives/demonyms. Common
# adjectival forms (Arabic: سعودي, Russian: саудовский, etc.) are not in
# babel territory data either. This curated dict covers forms that appear
# regularly in KYC nationality fields.  Key = NFC-lowercased adjective.
# ---------------------------------------------------------------------------

_SUPPLEMENTARY_NATIONALITY_ALIASES: dict[str, str] = {
    # Arabic masculine adjective (nisba) forms
    "سعودي": "SA",     # Saudi → Saudi Arabia
    "ياباني": "JP",    # Japanese → Japan
    "صيني": "CN",      # Chinese → China
    "مصري": "EG",      # Egyptian → Egypt
    "أمريكي": "US",    # American → United States
    "بريطاني": "GB",   # British → United Kingdom
    "فرنسي": "FR",     # French → France
    "ألماني": "DE",    # German → Germany
    "إيطالي": "IT",    # Italian → Italy
    "إسباني": "ES",    # Spanish → Spain
    "تركي": "TR",      # Turkish → Turkey
    "هندي": "IN",      # Indian → India
    "باكستاني": "PK",  # Pakistani → Pakistan
    "إماراتي": "AE",   # Emirati → United Arab Emirates
    "كويتي": "KW",     # Kuwaiti → Kuwait
    "قطري": "QA",      # Qatari → Qatar
    "بحريني": "BH",    # Bahraini → Bahrain
    "عُماني": "OM",    # Omani → Oman
    "عماني": "OM",     # (without hamza above ain) Omani → Oman
    "أردني": "JO",     # Jordanian → Jordan
    "لبناني": "LB",    # Lebanese → Lebanon
    "سوري": "SY",      # Syrian → Syria
    "عراقي": "IQ",     # Iraqi → Iraq
    "إيراني": "IR",    # Iranian → Iran
    "مغربي": "MA",     # Moroccan → Morocco
    "تونسي": "TN",     # Tunisian → Tunisia
    "جزائري": "DZ",    # Algerian → Algeria
    "ليبي": "LY",      # Libyan → Libya
    "يمني": "YE",      # Yemeni → Yemen
    "سوداني": "SD",    # Sudanese → Sudan
    "روسي": "RU",      # Russian → Russia (ar adjective)
    "كوري": "KR",      # Korean → South Korea (ar adjective)
    # Turkish adjectival forms (commonly omit country suffix)
    "suudi": "SA",     # Saudi (tr)
    "japon": "JP",     # Japanese (tr)
    "çinli": "CN",     # Chinese (tr)
    "alman": "DE",     # German (tr)
    "fransız": "FR",   # French (tr)
    "ingiliz": "GB",   # British (tr)
    "amerikalı": "US", # American (tr)
    "rus": "RU",       # Russian (tr)
    "İranlı": "IR",    # Iranian (tr)
    "iranlı": "IR",    # Iranian (tr, normalised)
}

# ---------------------------------------------------------------------------
# Text normalisation
# ---------------------------------------------------------------------------


def _normalise_text(text: str) -> str:
    """
    Lowercase + NFC unicode normalisation.

    NFC is used (not NFKD) to preserve meaningful diacritics and non-Latin
    scripts (Arabic, CJK, Cyrillic). Trailing/leading whitespace is stripped.
    """
    return unicodedata.normalize("NFC", text.strip().lower())


# ---------------------------------------------------------------------------
# Index builders
# ---------------------------------------------------------------------------


def _build_country_data() -> dict[str, dict]:
    """
    Build ISO2 → {name, iso3, geonameid} from countryInfo.txt.
    Falls back to pycountry for any missing entries.
    """
    result: dict[str, dict] = {}

    country_info_path = _DATA_DIR / "countryInfo.txt"
    if country_info_path.exists() and country_info_path.stat().st_size > 100:
        try:
            with country_info_path.open(encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    if line.startswith("#"):
                        continue
                    parts = line.rstrip("\n").split("\t")
                    if len(parts) < 17:
                        continue
                    iso2 = parts[0].strip()
                    iso3 = parts[1].strip()
                    name = parts[4].strip()
                    try:
                        geonameid = int(parts[16].strip())
                    except (ValueError, IndexError):
                        geonameid = 0
                    if iso2 and name:
                        result[iso2] = {"name": name, "iso3": iso3, "geonameid": geonameid}
            log.info("countryInfo.txt: %d countries loaded", len(result))
        except Exception as exc:
            log.warning("countryInfo.txt parse error: %s", exc)

    # Fill gaps (or entire dict if file missing/empty) from pycountry
    try:
        import pycountry

        for c in pycountry.countries:
            if c.alpha_2 not in result:
                result[c.alpha_2] = {
                    "name": c.name,
                    "iso3": getattr(c, "alpha_3", ""),
                    "geonameid": 0,
                }
        log.info("Country data after pycountry fill: %d entries", len(result))
    except ImportError:
        log.warning("pycountry not available — country data may be incomplete")

    return result


def _build_index() -> tuple[dict, dict, dict, dict]:
    """
    Build all four indexes from GeoNames data files.

    Returns:
        (alias_index, canonical_index, country_by_code, admin1_index)
    """
    log.info("Building geographic index from GeoNames data — this may take 30–90 seconds...")

    country_by_code = _build_country_data()
    country_geoid_set: set[int] = {
        v["geonameid"] for v in country_by_code.values() if v.get("geonameid")
    }

    # ── Step 1: Canonical city index from cities15000.txt ──────────────────
    canonical_index: dict[int, dict] = {}
    cities_path = _DATA_DIR / "cities15000.txt"
    if cities_path.exists():
        try:
            with cities_path.open(encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    parts = line.rstrip("\n").split("\t")
                    if len(parts) < 15:
                        continue
                    try:
                        geonameid = int(parts[0])
                    except ValueError:
                        continue
                    ascii_name = parts[2].strip()
                    country_code = parts[8].strip()
                    admin1_code = parts[10].strip()
                    if ascii_name:
                        canonical_index[geonameid] = {
                            "name_en": ascii_name,
                            "country_code": country_code,
                            "admin1_code": admin1_code,
                            "feature": "city",
                        }
            log.info("Canonical city index from cities15000.txt: %d entries", len(canonical_index))
        except Exception as exc:
            log.error("cities15000.txt parse error: %s", exc)
    else:
        log.warning("cities15000.txt not found at %s — city lookups will be empty", cities_path)

    city_geoid_set: set[int] = set(canonical_index.keys())

    # ── Step 2: Country alias index from babel ─────────────────────────────
    alias_index: dict[str, dict] = {}

    try:
        import pycountry
        from babel import Locale
        from babel.core import UnknownLocaleError

        for c in pycountry.countries:
            iso2 = c.alpha_2
            canonical_name = country_by_code.get(iso2, {}).get("name") or c.name
            entry = {
                "english_name": canonical_name,
                "country_code": iso2,
                "feature": "country",
            }
            # English name variants
            for form in (
                c.name,
                getattr(c, "common_name", None),
                getattr(c, "official_name", None),
                iso2,
                getattr(c, "alpha_3", None),
            ):
                if form:
                    alias_index[_normalise_text(form)] = entry

            # Babel localised forms
            for loc_str in _BABEL_LOCALES:
                try:
                    loc = Locale.parse(loc_str)
                    localised = loc.territories.get(iso2)
                    if localised:
                        alias_index[_normalise_text(localised)] = entry
                except (UnknownLocaleError, ValueError, KeyError):
                    pass
                except Exception:
                    pass

        log.info("Country alias index from babel: %d entries", len(alias_index))
    except ImportError as exc:
        log.warning("babel/pycountry not available for country index: %s", exc)

    # ── Supplementary nationality adjective aliases (demonym/adjectival forms) ─
    try:
        import pycountry

        supp_count = 0
        for raw_text, iso2 in _SUPPLEMENTARY_NATIONALITY_ALIASES.items():
            key = _normalise_text(raw_text)
            if key and key not in alias_index:
                c = pycountry.countries.get(alpha_2=iso2)
                canonical_name = country_by_code.get(iso2, {}).get("name") or (c.name if c else iso2)
                alias_index[key] = {
                    "english_name": canonical_name,
                    "country_code": iso2,
                    "feature": "country",
                }
                supp_count += 1
        log.info("Supplementary nationality alias entries added: %d", supp_count)
    except ImportError:
        pass

    # Index canonical city English names (so "Tokyo", "Moscow" etc. resolve directly)
    for geonameid, record in canonical_index.items():
        key = _normalise_text(record["name_en"])
        if key and key not in alias_index:
            alias_index[key] = {
                "english_name": record["name_en"],
                "country_code": record["country_code"],
                "feature": "city",
                "geonameid": geonameid,
                "admin1_code": record.get("admin1_code", ""),
            }

    # ── Step 3: alternateNamesV2.txt — multilingual city aliases ──────────
    alternate_path = _DATA_DIR / "alternateNamesV2.txt"
    known_geoids = city_geoid_set | country_geoid_set
    if alternate_path.exists() and known_geoids:
        # Pre-build country geoid → ISO2 reverse map for fast lookup
        geoid_to_iso2: dict[int, str] = {
            v["geonameid"]: k for k, v in country_by_code.items() if v.get("geonameid")
        }
        try:
            new_alias_count = 0
            with alternate_path.open(encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    parts = line.rstrip("\n").split("\t")
                    if len(parts) < 4:
                        continue
                    try:
                        geonameid = int(parts[1])
                    except ValueError:
                        continue

                    if geonameid not in known_geoids:
                        continue

                    isolanguage = parts[2]
                    if isolanguage not in TARGET_LANGUAGES:
                        continue

                    alternate_name = parts[3].strip()
                    if not alternate_name:
                        continue

                    key = _normalise_text(alternate_name)
                    if not key:
                        continue

                    # Build entry from canonical source
                    if geonameid in canonical_index:
                        record = canonical_index[geonameid]
                        entry = {
                            "english_name": record["name_en"],
                            "country_code": record.get("country_code", ""),
                            "feature": "city",
                            "geonameid": geonameid,
                            "admin1_code": record.get("admin1_code", ""),
                        }
                    elif geonameid in geoid_to_iso2:
                        iso2 = geoid_to_iso2[geonameid]
                        entry = {
                            "english_name": country_by_code[iso2]["name"],
                            "country_code": iso2,
                            "feature": "country",
                        }
                    else:
                        continue

                    if key not in alias_index:
                        alias_index[key] = entry
                        new_alias_count += 1

            log.info(
                "alternateNamesV2.txt: +%d new aliases (total alias index: %d entries)",
                new_alias_count,
                len(alias_index),
            )
        except Exception as exc:
            log.error("alternateNamesV2.txt parse error: %s", exc)
    elif not alternate_path.exists():
        log.warning(
            "alternateNamesV2.txt not found at %s — multilingual city aliases unavailable",
            alternate_path,
        )

    # ── Step 4: admin1CodesASCII.txt ──────────────────────────────────────
    admin1_index: dict[str, str] = {}
    admin1_path = _DATA_DIR / "admin1CodesASCII.txt"
    if admin1_path.exists():
        try:
            with admin1_path.open(encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    parts = line.rstrip("\n").split("\t")
                    if len(parts) < 2:
                        continue
                    code = parts[0].strip()   # e.g. "JP.13"
                    name = parts[1].strip()
                    if code and name:
                        admin1_index[code] = name
            log.info("Admin1 index: %d entries", len(admin1_index))
        except Exception as exc:
            log.warning("admin1CodesASCII.txt parse error: %s", exc)

    log.info(
        "Geographic index ready: %d aliases, %d canonical city entries, %d countries, %d admin1 regions",
        len(alias_index),
        len(canonical_index),
        len(country_by_code),
        len(admin1_index),
    )
    return alias_index, canonical_index, country_by_code, admin1_index


def _load_or_build_index() -> tuple[dict, dict, dict, dict]:
    """Load from pickle if fresh, otherwise build from source files and cache."""
    source_files = [
        _DATA_DIR / "cities15000.txt",
        _DATA_DIR / "alternateNamesV2.txt",
        _DATA_DIR / "countryInfo.txt",
        _DATA_DIR / "admin1CodesASCII.txt",
    ]

    if _CACHE_FILE.exists():
        try:
            cache_mtime = _CACHE_FILE.stat().st_mtime
            all_fresh = all(
                not p.exists() or cache_mtime > p.stat().st_mtime
                for p in source_files
            )
            if all_fresh:
                with _CACHE_FILE.open("rb") as f:
                    data = pickle.load(f)  # noqa: S301 — written by this process only
                if isinstance(data, tuple) and len(data) == 4:
                    log.info(
                        "Geographic index loaded from cache: %d aliases, %d canonical entries",
                        len(data[0]),
                        len(data[1]),
                    )
                    return data  # type: ignore[return-value]
                log.warning("Cache format mismatch — rebuilding")
        except Exception as exc:
            log.warning("Cache load failed (%s) — rebuilding", exc)

    result = _build_index()
    try:
        _CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with _CACHE_FILE.open("wb") as f:
            pickle.dump(result, f, protocol=pickle.HIGHEST_PROTOCOL)
        log.info("Geographic index cached to %s", _CACHE_FILE)
    except Exception as exc:
        log.warning("Cache save failed: %s", exc)

    return result


def _ensure_index() -> None:
    """Build/load the geographic index exactly once. Thread-safe double-check locking."""
    global _INDEX_BUILT, _ALIAS_INDEX, _CANONICAL_INDEX, _COUNTRY_BY_CODE, _ADMIN1_INDEX
    if _INDEX_BUILT:
        return
    with _BUILD_LOCK:
        if _INDEX_BUILT:  # double-check after acquiring lock
            return
        _ALIAS_INDEX, _CANONICAL_INDEX, _COUNTRY_BY_CODE, _ADMIN1_INDEX = (
            _load_or_build_index()
        )
        _INDEX_BUILT = True


# ---------------------------------------------------------------------------
# Demonym resolver
# ---------------------------------------------------------------------------


def _resolve_demonym_to_country(english_name: str, country_code: str) -> str | None:
    """
    Convert a demonym or adjectival English name to the canonical country name.

    Uses the ISO2 country_code from the GeoNames record when available
    (most reliable), then falls back to pycountry fuzzy search.

    Examples:
        "GERMAN"   + "DE" → "GERMANY"
        "JAPANESE" + "JP" → "JAPAN"
        "SAUDI"    + "SA" → "SAUDI ARABIA"
    """
    # Primary: use country_code from the GeoNames record (ISO2 → pycountry)
    if country_code and len(country_code) == 2:
        try:
            import pycountry

            c = pycountry.countries.get(alpha_2=country_code.upper())
            if c:
                return c.name.upper()
        except Exception:
            pass

        # Also check COUNTRY_BY_CODE (from countryInfo.txt)
        entry = _COUNTRY_BY_CODE.get(country_code.upper())
        if entry:
            return entry["name"].upper()

    # Fallback: pycountry fuzzy match on the English name
    try:
        import pycountry

        results = pycountry.countries.search_fuzzy(english_name)
        if results:
            return results[0].name.upper()
    except Exception:
        pass

    return None


# ---------------------------------------------------------------------------
# Result builder
# ---------------------------------------------------------------------------


def _build_result(original: str, normalised: str, confidence: float) -> dict:
    return {
        "original_text": original,
        "normalised_form": normalised,
        "allowed_variants": [],
        "processing_method": "GEOGRAPHIC",
        "confidence": confidence,
        "review_required": confidence < 0.85,
        "review_reason": (
            None
            if confidence >= 0.85
            else "Low confidence geographic match — verify"
        ),
        "should_use_in_screening": True,
        "latin_transliteration": None,
        "analyst_english_rendering": normalised,
    }


# ---------------------------------------------------------------------------
# Partial match (address fields only)
# ---------------------------------------------------------------------------


def _partial_match(key: str) -> dict | None:
    """Prefix scan of alias index. Only called for address-type lookups."""
    for k, v in _ALIAS_INDEX.items():
        if k and (key.startswith(k) or k.startswith(key)):
            return v
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def lookup_geographic(
    text: str,
    field_type: str,
    language: str = "",
    country: str = "",
) -> dict | None:
    """
    Look up a geographic term and return its canonical English form.

    Args:
        text:       The raw input text (country name, city, nationality term).
        field_type: Classifier-assigned field type (must be in GEOGRAPHIC_FIELDS).
        language:   BCP-47 language code hint from the GPT classifier.
        country:    Country context hint (ISO2 or English name).

    Returns:
        Normalisation result dict, or None if no match found.

    Lookup order:
        1. Exact match in ALIAS_INDEX (normalised key)
        2. For nationality fields: resolve to canonical country name via pycountry
        3. For address fields with no exact match: prefix scan (confidence 0.75)
    """
    if not text or field_type not in GEOGRAPHIC_FIELDS:
        return None

    _ensure_index()

    normalised = _normalise_text(text)
    if not normalised:
        return None

    # Step 1: exact alias lookup
    match = _ALIAS_INDEX.get(normalised)
    if match:
        english_name = match["english_name"]
        confidence = 0.92

        # Step 2: for nationality fields, resolve via pycountry to canonical country name
        # This converts demonyms (GERMAN → GERMANY) and ensures consistent output.
        if field_type in NATIONALITY_FIELDS:
            resolved = _resolve_demonym_to_country(english_name, match.get("country_code", ""))
            if resolved:
                english_name = resolved
                confidence = 0.88

        return _build_result(text, english_name.upper(), confidence)

    # Step 3: for address fields, try prefix scan
    if field_type in ADDRESS_FIELDS and len(normalised) > 5:
        partial = _partial_match(normalised)
        if partial:
            return _build_result(text, partial["english_name"].upper(), 0.75)

    return None


def validate_hierarchy(city: str, region: str, country: str) -> tuple[bool, str | None]:
    """
    Validate that a city belongs to the stated region and country.

    Returns:
        (True, None)           — valid or cannot be checked
        (False, reason_str)    — mismatch detected

    Example:
        validate_hierarchy("Tokyo", "Osaka", "Japan") →
        (False, "Tokyo is in Tokyo, not Osaka")
    """
    _ensure_index()

    city_key = _normalise_text(city)
    city_match = _ALIAS_INDEX.get(city_key)
    if not city_match or city_match.get("feature") != "city":
        return (True, None)  # cannot validate — pass through

    record_iso2 = city_match.get("country_code", "")
    record_country = _COUNTRY_BY_CODE.get(record_iso2, {})
    record_country_name = record_country.get("name", record_iso2).upper()

    if country.upper() not in (record_country_name, record_iso2.upper()):
        return (False, f"{city} is in {record_country_name}, not {country}")

    geonameid = city_match.get("geonameid")
    record = _CANONICAL_INDEX.get(geonameid) if geonameid else None
    if record:
        admin1_code = record.get("admin1_code", "")
        admin1_key = f"{record_iso2}.{admin1_code}"
        admin1_english = _ADMIN1_INDEX.get(admin1_key, "")
        if admin1_english and region.upper() not in admin1_english.upper():
            return (False, f"{city} is in {admin1_english}, not {region}")

    return (True, None)


# ---------------------------------------------------------------------------
# Legacy shim — kept so app/__init__.py works without changes
# ---------------------------------------------------------------------------


class GeographicLookupService:
    """
    Thin compatibility shim over the module-level lookup_geographic().

    The class-based approach has been replaced by a module-level singleton
    pattern for thread-safety and simpler wiring. This shim exists only so
    app/__init__.py (which calls GeographicLookupService()) continues to work
    during the migration. It triggers _ensure_index() at construction time so
    the cache is pre-warmed at app startup.
    """

    def __init__(self, geonames_path: str | None = None, cache_dir=None) -> None:
        # Pre-warm the index at app startup (background thread would be nicer,
        # but synchronous is simpler and avoids request-time latency on first hit).
        _ensure_index()

    def lookup(
        self,
        field_type: str,
        text: str,
        language: str = "",
        country: str = "",
    ) -> dict | None:
        return lookup_geographic(text, field_type, language=language, country=country)
