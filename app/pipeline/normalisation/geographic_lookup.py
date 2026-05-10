"""
Strategy D — Geographic Lookup.

Resolves country names, nationality demonyms, and place names from
authoritative reference data. All lookups are in-memory — no database
queries, no API calls at request time.

Three indexes are built at startup:
  1. Country index — maps country names in any script/language to English
     name and ISO codes. Built from pycountry + babel.
  2. City index — maps city and town names to English form and country.
     Built from GeoNames full dataset if available, geonamescache otherwise.
  3. Subdivision index — maps province, region, and prefecture names to
     English form. Built from pycountry ISO 3166-2 subdivisions.

Startup time is approximately 10–30 seconds on first run while indexes build.
Indexes are held in memory for the lifetime of the process.
"""

from __future__ import annotations

import logging
import unicodedata
from pathlib import Path

log = logging.getLogger(__name__)

_GEOGRAPHIC_FIELDS: frozenset[str] = frozenset(
    ["nationality", "country", "country_of_residence", "place_of_birth", "city"]
)

_PROCESSING_METHOD = "GEOGRAPHIC"

# Common English aliases not in pycountry's primary name
_COUNTRY_ALIASES: dict[str, str] = {
    "russia": "RU",
    "south korea": "KR",
    "north korea": "KP",
    "taiwan": "TW",
    "iran": "IR",
    "syria": "SY",
    "bolivia": "BO",
    "venezuela": "VE",
    "moldova": "MD",
    "tanzania": "TZ",
    "vietnam": "VN",
    "ivory coast": "CI",
    "democratic republic of the congo": "CD",
    "republic of the congo": "CG",
}


def _normalise_key(text: str) -> str:
    """Lowercase + NFKD strip accents + collapse whitespace."""
    nfkd = unicodedata.normalize("NFKD", text)
    ascii_text = "".join(c for c in nfkd if not unicodedata.combining(c))
    return " ".join(ascii_text.lower().split())


class GeographicLookupService:
    """In-memory geographic normalisation service (Strategy D)."""

    TARGET_LOCALES: list[str] = [
        "ar", "zh", "zh_TW", "ja", "ko", "ru", "uk", "el",
        "de", "fr", "es", "it", "tr", "he", "th", "pt", "nl",
        "pl", "sv", "no", "da",
    ]

    def __init__(self, geonames_path: str | None = None) -> None:
        self._country_index: dict[str, dict] = {}   # normalised_key → {name_en, iso2, iso3}
        self._nationality_index: dict[str, dict] = {}  # normalised_key → {english_nationality, iso2}
        self._city_index: dict[str, dict] = {}      # normalised_key → {name_en, country_code}
        self._subdivision_index: dict[str, dict] = {}  # normalised_key → {name_en, country_code, type}

        self._build_country_index()
        self._build_nationality_index()
        self._build_city_index(geonames_path)
        self._build_subdivision_index()

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def lookup(
        self,
        field_type: str,
        text: str,
        language: str = "",
        country: str = "",
    ) -> dict | None:
        """Route to the correct sub-lookup based on field_type. Returns None if no match."""
        if not text or field_type not in _GEOGRAPHIC_FIELDS:
            return None

        if field_type == "nationality":
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
        """Match a country name in any script/language to its English name and ISO codes."""
        if not text:
            return None

        # 1. Exact normalised match
        key = _normalise_key(text)
        entry = self._country_index.get(key)
        if entry:
            return self._build_result(
                entry["name_en"].upper(), 0.99,
                iso2=entry["iso2"], iso3=entry["iso3"],
            )

        # 2. ASCII-only normalised match (already done above since _normalise_key strips accents)
        # Try raw lowercase as fallback
        raw_key = text.strip().lower()
        entry = self._country_index.get(raw_key)
        if entry:
            return self._build_result(
                entry["name_en"].upper(), 0.97,
                iso2=entry["iso2"], iso3=entry["iso3"],
            )

        # 3. pycountry fuzzy search (confidence gate: only use if high confidence)
        try:
            import pycountry
            matches = pycountry.countries.search_fuzzy(text)
            if matches:
                m = matches[0]
                return self._build_result(
                    m.name.upper(), 0.90,
                    iso2=m.alpha_2, iso3=m.alpha_3,
                )
        except Exception:
            pass

        return None

    # ------------------------------------------------------------------
    # Nationality lookup
    # ------------------------------------------------------------------

    def lookup_nationality(self, text: str, language: str = "") -> dict | None:
        """Resolve a nationality demonym in any language to its English form."""
        if not text:
            return None

        key = _normalise_key(text)
        entry = self._nationality_index.get(key)
        if entry:
            return self._build_result(
                entry["english_nationality"].upper(), 0.95,
                iso2=entry["iso2"],
            )

        # Fallback: treat input as country name and derive nationality
        country_result = self.lookup_country(text)
        if country_result:
            iso2 = country_result.get("iso2", "")
            nat_entry = self._iso2_to_nationality.get(iso2)
            if nat_entry:
                return self._build_result(
                    nat_entry.upper(), 0.88,
                    iso2=iso2,
                )

        return None

    # ------------------------------------------------------------------
    # Place name lookup
    # ------------------------------------------------------------------

    def lookup_place(self, text: str) -> dict | None:
        """Match a city/town/village name to its English form and country."""
        if not text:
            return None

        key = _normalise_key(text)

        # 1. GeoNames / geonamescache city index
        entry = self._city_index.get(key)
        if entry:
            return self._build_result(
                entry["name_en"].upper(), 0.95,
                country_code=entry["country_code"],
            )

        # 2. Subdivision index (prefecture, province, state)
        entry = self._subdivision_index.get(key)
        if entry:
            return self._build_result(
                entry["name_en"].upper(), 0.90,
                country_code=entry["country_code"],
                subdivision_type=entry.get("subdivision_type"),
            )

        return None

    # ------------------------------------------------------------------
    # Index builders
    # ------------------------------------------------------------------

    def _build_country_index(self) -> None:
        """Index country names from pycountry + babel across all TARGET_LOCALES."""
        import pycountry
        try:
            from babel import Locale
            from babel.core import UnknownLocaleError
        except ImportError:
            Locale = None
            UnknownLocaleError = Exception

        self._iso2_to_nationality: dict[str, str] = {}

        for country in pycountry.countries:
            iso2 = country.alpha_2
            iso3 = country.alpha_3
            name_en = country.name

            entry = {"name_en": name_en, "iso2": iso2, "iso3": iso3}

            # Index English primary name and common name
            self._country_index[_normalise_key(name_en)] = entry
            if hasattr(country, "common_name") and country.common_name:
                self._country_index[_normalise_key(country.common_name)] = entry
            if hasattr(country, "official_name") and country.official_name:
                self._country_index[_normalise_key(country.official_name)] = entry

            # Index babel localised names
            if Locale is not None:
                for locale_str in self.TARGET_LOCALES:
                    try:
                        locale = Locale.parse(locale_str)
                        localised = locale.territories.get(iso2)
                        if localised:
                            self._country_index[_normalise_key(localised)] = entry
                    except (UnknownLocaleError, ValueError, KeyError):
                        pass
                    except Exception as exc:
                        log.warning("babel error for %s/%s: %s", locale_str, iso2, exc)

        # Hard-code common English aliases
        for alias, iso2 in _COUNTRY_ALIASES.items():
            try:
                import pycountry
                c = pycountry.countries.get(alpha_2=iso2)
                if c:
                    self._country_index[alias] = {
                        "name_en": c.name, "iso2": c.alpha_2, "iso3": c.alpha_3
                    }
            except Exception:
                pass

        log.info("Country index built: %d entries", len(self._country_index))

    def _build_nationality_index(self) -> None:
        """Build nationality demonym index using countryinfo."""
        try:
            from countryinfo import CountryInfo
            import pycountry
        except ImportError:
            log.warning("countryinfo not installed — nationality index will be empty")
            return

        for country in pycountry.countries:
            iso2 = country.alpha_2
            try:
                info = CountryInfo(iso2)
                demonym = info.demonym()
                if demonym:
                    self._iso2_to_nationality[iso2] = demonym
                    key = _normalise_key(demonym)
                    self._nationality_index[key] = {
                        "english_nationality": demonym,
                        "iso2": iso2,
                    }
            except Exception:
                pass

        log.info("Nationality index built: %d entries", len(self._nationality_index))

    def _build_city_index(self, geonames_path: str | None) -> None:
        """Build city/place index from GeoNames file or geonamescache fallback."""
        path = Path(geonames_path) if geonames_path else None

        if path and path.exists():
            self._load_geonames_file(path)
        else:
            if geonames_path:
                log.warning(
                    "GeoNames file not found at %s. Falling back to geonamescache "
                    "(~25,000 cities). Place-of-birth lookups for small towns and "
                    "villages will not resolve automatically.", geonames_path
                )
            else:
                log.info("No GeoNames path provided. Using geonamescache fallback.")
            self._load_geonamescache()

    def _load_geonames_file(self, path: Path) -> None:
        """Parse GeoNames allCountries.txt (tab-separated, 19 columns)."""
        count = 0
        try:
            with path.open(encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    parts = line.rstrip("\n").split("\t")
                    if len(parts) < 15:
                        continue
                    name = parts[1]
                    ascii_name = parts[2]
                    alternate_names_raw = parts[3]
                    country_code = parts[8]
                    try:
                        population = int(parts[14])
                    except (ValueError, IndexError):
                        population = 0

                    if not name or not ascii_name or population <= 0:
                        continue

                    entry = {"name_en": ascii_name, "country_code": country_code}

                    for candidate in [name, ascii_name]:
                        k = _normalise_key(candidate)
                        if k:
                            self._city_index[k] = entry

                    if alternate_names_raw:
                        for alt in alternate_names_raw.split(","):
                            alt = alt.strip()
                            if alt:
                                k = _normalise_key(alt)
                                if k and k not in self._city_index:
                                    self._city_index[k] = entry

                    count += 1

            log.info("GeoNames city index built from file: %d places", count)
        except Exception as exc:
            log.error("Failed to load GeoNames file: %s — falling back to geonamescache", exc)
            self._load_geonamescache()

    def _load_geonamescache(self) -> None:
        """Load city data from bundled geonamescache (~25,000 cities)."""
        try:
            import geonamescache
            gc = geonamescache.GeonamesCache()
            # Collect with population so ambiguous names resolve to the larger city
            candidates: dict[str, tuple[int, dict]] = {}
            for city in gc.get_cities().values():
                name = city.get("name", "")
                country_code = city.get("countrycode", "")
                population = city.get("population", 0) or 0
                if not name:
                    continue
                entry = {"name_en": name, "country_code": country_code}
                k = _normalise_key(name)
                if k:
                    existing_pop = candidates.get(k, (-1, None))[0]
                    if population > existing_pop:
                        candidates[k] = (population, entry)
            for k, (_, entry) in candidates.items():
                self._city_index[k] = entry
            log.info("City index built from geonamescache: %d entries", len(self._city_index))
        except Exception as exc:
            log.error("geonamescache load failed: %s", exc)

    def _build_subdivision_index(self) -> None:
        """Index pycountry ISO 3166-2 subdivision names + babel localisations."""
        try:
            import pycountry
            from babel import Locale
            from babel.core import UnknownLocaleError
        except ImportError:
            log.warning("pycountry/babel not available — subdivision index empty")
            return

        for sub in pycountry.subdivisions:
            iso2 = sub.country_code
            name_en = sub.name
            sub_type = sub.type

            entry = {"name_en": name_en, "country_code": iso2, "subdivision_type": sub_type}
            k = _normalise_key(name_en)
            if k:
                self._subdivision_index[k] = entry

            # Also index babel localisations
            for locale_str in self.TARGET_LOCALES:
                try:
                    locale = Locale.parse(locale_str)
                    territories = locale.territories
                    # Subdivisions don't always have territory data; try anyway
                    localised = territories.get(sub.code.replace(f"{iso2}-", ""))
                    if localised:
                        lk = _normalise_key(localised)
                        if lk and lk not in self._subdivision_index:
                            self._subdivision_index[lk] = entry
                except (UnknownLocaleError, ValueError, KeyError):
                    pass
                except Exception:
                    pass

        log.info("Subdivision index built: %d entries", len(self._subdivision_index))

    # ------------------------------------------------------------------
    # Result builder
    # ------------------------------------------------------------------

    @staticmethod
    def _build_result(normalised_form: str, confidence: float, **extra) -> dict:
        return {
            "normalised_form": normalised_form,
            "allowed_variants": [],
            "processing_method": _PROCESSING_METHOD,
            "confidence": confidence,
            "review_required": confidence < 0.90,
            "review_reason": (
                None if confidence >= 0.90
                else "Geographic lookup confidence below threshold"
            ),
            "should_use_in_screening": True,
            **extra,
        }
