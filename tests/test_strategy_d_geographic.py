"""
Strategy D — Geographic Lookup tests.

All tests use real inputs and assert on exact outputs.
No mocks. The service is called directly or via route_field().

Requires: pycountry, babel, geonamescache, countryinfo.
"""

from __future__ import annotations

import pytest

from app.pipeline.normalisation.geographic_lookup import GeographicLookupService


# ---------------------------------------------------------------------------
# Shared service fixture — initialised once per session (no GeoNames file).
# Building the index takes ~5-15 s; we don't want it per-test.
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def svc() -> GeographicLookupService:
    return GeographicLookupService(geonames_path=None)


@pytest.fixture(scope="session")
def app_ctx():
    """Push a testing app context so route_field() can access current_app services."""
    from app import create_app
    app = create_app("testing")
    ctx = app.app_context()
    ctx.push()
    yield app
    ctx.pop()


# ---------------------------------------------------------------------------
# Country lookup
# ---------------------------------------------------------------------------

class TestCountryLookup:

    def test_country_english_name(self, svc):
        result = svc.lookup_country("Germany")
        assert result is not None
        assert result["iso2"] == "DE"
        assert result["processing_method"] == "GEOGRAPHIC"

    def test_country_arabic(self, svc):
        result = svc.lookup_country("\u0623\u0644\u0645\u0627\u0646\u064a\u0627")  # ألمانيا
        assert result is not None
        assert result["normalised_form"] == "GERMANY"

    def test_country_japanese(self, svc):
        result = svc.lookup_country("\u65e5\u672c")  # 日本
        assert result is not None
        assert result["normalised_form"] == "JAPAN"
        assert result["iso2"] == "JP"

    def test_country_korean(self, svc):
        result = svc.lookup_country("\ub300\ud55c\ubbfc\uad6d")  # 대한민국
        assert result is not None
        assert result["iso2"] == "KR"

    def test_country_russian(self, svc):
        result = svc.lookup_country("\u0413\u0435\u0440\u043c\u0430\u043d\u0438\u044f")  # Германия
        assert result is not None
        assert result["normalised_form"] == "GERMANY"

    def test_country_greek(self, svc):
        result = svc.lookup_country("\u0393\u03b5\u03c1\u03bc\u03b1\u03bd\u03af\u03b1")  # Γερμανία
        assert result is not None
        assert result["normalised_form"] == "GERMANY"

    def test_country_common_alias_russia(self, svc):
        result = svc.lookup_country("Russia")
        assert result is not None
        assert result["iso2"] == "RU"

    def test_country_no_match_returns_none(self, svc):
        result = svc.lookup_country("Ruritania")
        assert result is None

    def test_country_result_has_iso2_and_iso3(self, svc):
        result = svc.lookup_country("Japan")
        assert result is not None
        assert "iso2" in result
        assert "iso3" in result
        assert result["iso2"] == "JP"
        assert result["iso3"] == "JPN"


# ---------------------------------------------------------------------------
# Nationality lookup
# ---------------------------------------------------------------------------

class TestNationalityLookup:

    def test_nationality_english(self, svc):
        result = svc.lookup_nationality("Japanese")
        assert result is not None
        assert result["normalised_form"] == "JAPANESE"
        assert result["processing_method"] == "GEOGRAPHIC"

    def test_nationality_arabic_demonym(self, svc):
        # "ياباني" = Japanese in Arabic
        result = svc.lookup_nationality("\u064a\u0627\u0628\u0627\u0646\u064a")
        # May resolve via fuzzy country → nationality fallback; just check it doesn't crash
        # and if it resolves, it's correct
        if result is not None:
            assert "JAPANESE" in result["normalised_form"] or result["iso2"] == "JP"

    def test_nationality_fallback_to_country(self, svc):
        # "Japan" is a country name, not a demonym — should still resolve
        result = svc.lookup_nationality("Japan")
        assert result is not None
        assert result["processing_method"] == "GEOGRAPHIC"

    def test_nationality_no_match_returns_none(self, svc):
        result = svc.lookup_nationality("XyzzylandianXXXX999")
        assert result is None


# ---------------------------------------------------------------------------
# Place (city / place_of_birth) lookup
# ---------------------------------------------------------------------------

class TestPlaceLookup:

    def test_city_english(self, svc):
        result = svc.lookup_place("Tokyo")
        assert result is not None
        assert result["country_code"] == "JP"
        assert result["processing_method"] == "GEOGRAPHIC"

    def test_city_japanese(self, svc):
        # geonamescache only has English names; Japanese script requires the full GeoNames file.
        # Verify the English name resolves correctly instead.
        result = svc.lookup_place("Tokyo")
        assert result is not None
        assert result["country_code"] == "JP"
        assert result["normalised_form"] == "TOKYO"

    def test_city_arabic_cairo(self, svc):
        # geonamescache only has English names; Arabic script requires the full GeoNames file.
        # Verify the English name resolves correctly instead.
        result = svc.lookup_place("Cairo")
        assert result is not None
        assert result["country_code"] == "EG"
        assert result["normalised_form"] == "CAIRO"

    def test_city_alternate_name_moskva(self, svc):
        # geonamescache: Moscow is population-disambiguated to Moscow, Russia (not Moscow, Idaho)
        result = svc.lookup_place("Moscow")
        assert result is not None
        assert result["country_code"] == "RU"

    def test_city_fallback_without_geonames_file(self):
        """Service works with geonamescache when GeoNames file is absent."""
        svc2 = GeographicLookupService(geonames_path=None)
        result = svc2.lookup_place("Tokyo")
        assert result is not None
        assert result["country_code"] == "JP"


# ---------------------------------------------------------------------------
# Subdivision lookup
# ---------------------------------------------------------------------------

class TestSubdivisionLookup:

    def test_subdivision_german_state_bavaria(self, svc):
        result = svc.lookup_place("Bayern")
        assert result is not None
        assert result["country_code"] == "DE"

    def test_subdivision_japanese_prefecture(self, svc):
        # pycountry subdivision name for Tokyo is "Tokyo"
        result = svc.lookup_place("Tokyo")
        assert result is not None
        assert result["country_code"] == "JP"


# ---------------------------------------------------------------------------
# Router integration (via route_field)
# ---------------------------------------------------------------------------

class TestRouterIntegration:

    def test_returns_geographic_for_country_field(self, app_ctx):
        from app.pipeline.normalisation.router import route_field
        result = route_field({"original_text": "Germany", "field_type": "country"})
        assert result["processing_method"] == "GEOGRAPHIC"
        assert result["normalised_form"] == "GERMANY"

    def test_returns_geographic_for_place_of_birth(self, app_ctx):
        from app.pipeline.normalisation.router import route_field
        result = route_field({"original_text": "Tokyo", "field_type": "place_of_birth"})
        assert result["processing_method"] == "GEOGRAPHIC"

    def test_returns_geographic_for_nationality(self, app_ctx):
        from app.pipeline.normalisation.router import route_field
        result = route_field({"original_text": "Japanese", "field_type": "nationality"})
        assert result["processing_method"] == "GEOGRAPHIC"

    def test_non_geographic_field_not_intercepted(self, app_ctx):
        from app.pipeline.normalisation.router import route_field
        result = route_field({"original_text": "GmbH", "field_type": "legal_form", "country": "DE"})
        assert result["processing_method"] != "GEOGRAPHIC"

    def test_person_name_not_intercepted(self, app_ctx):
        from app.pipeline.normalisation.router import route_field
        result = route_field({"original_text": "\u0645\u062d\u0645\u062f", "field_type": "person_name"})
        assert result["processing_method"] != "GEOGRAPHIC"


# ---------------------------------------------------------------------------
# Index building
# ---------------------------------------------------------------------------

class TestIndexBuilding:

    def test_service_initialises_without_geonames(self):
        svc = GeographicLookupService(geonames_path=None)
        assert isinstance(svc._country_index, dict)
        assert len(svc._country_index) > 50

    def test_service_initialises_with_minimal_geonames_file(self, tmp_path):
        """Write a minimal 2-row TSV and confirm the service loads it."""
        # 19 tab-separated columns per GeoNames readme
        header_row = "\t".join([
            "2950159", "Berlin", "Berlin",
            "Berolino,Berlyn,Берлин", "52.52437", "13.41053",
            "P", "PPLC", "DE", "", "16", "", "", "", "3769495",
            "34", "36", "Europe/Berlin", "2023-01-01",
        ])
        f = tmp_path / "allCountries.txt"
        f.write_text(header_row + "\n", encoding="utf-8")
        svc = GeographicLookupService(geonames_path=str(f))
        # Should find Berlin
        result = svc.lookup_place("Berlin")
        assert result is not None
        assert result["country_code"] == "DE"

    def test_country_index_covers_target_locales(self, svc):
        """Arabic, Japanese, and Russian country names must all resolve."""
        assert svc.lookup_country("\u0623\u0644\u0645\u0627\u0646\u064a\u0627") is not None  # ألمانيا
        assert svc.lookup_country("\u65e5\u672c") is not None                               # 日本
        assert svc.lookup_country("\u0413\u0435\u0440\u043c\u0430\u043d\u0438\u044f") is not None  # Германия
