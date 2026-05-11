"""
Strategy D â€” Geographic Lookup tests (v2, GeoNames-backed).

All tests use the real lookup_geographic() function â€” no mocks.
The index is built from cache on first call (< 2 s) or from source files
(30â€“90 s) on first run.

Note on D.7 / Arabic nationality adjective (Ø³Ø¹ÙˆØ¯ÙŠ):
  The epic spec says lookup_geographic() returns the canonical country NAME,
  not the English adjective. So Ø³Ø¹ÙˆØ¯ÙŠ â†’ "SAUDI ARABIA" (not "SAUDI ARABIAN").
  The integration diagnostic expectation for D.7 has been updated to match.
"""

from __future__ import annotations

import pytest

from app import create_app
from app.pipeline.normalisation.geographic_lookup import (
    GEOGRAPHIC_FIELDS,
    NATIONALITY_FIELDS,
    ADDRESS_FIELDS,
    lookup_geographic,
    validate_hierarchy,
)


# ---------------------------------------------------------------------------
# Fixture â€” app context so Flask globals are available
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def app_context():
    """Push a testing app context. Index is pre-warmed by app startup."""
    app = create_app("testing")
    ctx = app.app_context()
    ctx.push()
    # Explicitly warm the geographic index for this test session
    from app.pipeline.normalisation.geographic_lookup import _ensure_index
    _ensure_index()
    yield
    ctx.pop()


# ---------------------------------------------------------------------------
# Field-set sanity
# ---------------------------------------------------------------------------


def test_nationality_fields_subset_of_geographic():
    assert NATIONALITY_FIELDS <= GEOGRAPHIC_FIELDS


def test_address_fields_subset_of_geographic():
    assert ADDRESS_FIELDS <= GEOGRAPHIC_FIELDS


# ---------------------------------------------------------------------------
# Country name resolution
# ---------------------------------------------------------------------------


def test_arabic_germany(app_context):
    r = lookup_geographic("Ø£Ù„Ù…Ø§Ù†ÙŠØ§", "nationality", "ar")
    assert r is not None
    assert r["normalised_form"] == "GERMANY"
    assert r["processing_method"] == "GEOGRAPHIC"


def test_japanese_japan(app_context):
    r = lookup_geographic("æ—¥æœ¬", "nationality", "ja")
    assert r is not None
    assert r["normalised_form"] == "JAPAN"


def test_russian_germany(app_context):
    r = lookup_geographic("Ð“ÐµÑ€Ð¼Ð°Ð½Ð¸Ñ", "nationality", "ru")
    assert r is not None
    assert r["normalised_form"] == "GERMANY"


def test_greek_germany(app_context):
    r = lookup_geographic("Î“ÎµÏÎ¼Î±Î½Î¯Î±", "nationality", "el")
    assert r is not None
    assert r["normalised_form"] == "GERMANY"


def test_chinese_china(app_context):
    """D.5 fix: ä¸­å›½ must classify as nationality (not unstructured_text)."""
    r = lookup_geographic("ä¸­å›½", "nationality", "zh")
    assert r is not None
    assert r["normalised_form"] == "CHINA"


def test_korean_usa(app_context):
    r = lookup_geographic("ë¯¸êµ­", "country_of_incorporation", "ko")
    assert r is not None
    assert r["normalised_form"] == "UNITED STATES"


def test_arabic_saudi_nationality(app_context):
    """D.7 fix: Ø³Ø¹ÙˆØ¯ÙŠ resolves to canonical country name SAUDI ARABIA."""
    r = lookup_geographic("Ø³Ø¹ÙˆØ¯ÙŠ", "nationality", "ar")
    assert r is not None
    assert r["normalised_form"] == "SAUDI ARABIA"
    assert r["processing_method"] == "GEOGRAPHIC"


def test_english_germany(app_context):
    r = lookup_geographic("Germany", "nationality", "en")
    assert r is not None
    assert r["normalised_form"] == "GERMANY"


def test_english_united_states(app_context):
    r = lookup_geographic("United States", "nationality", "en")
    assert r is not None
    assert "UNITED STATES" in r["normalised_form"]


# ---------------------------------------------------------------------------
# City lookups
# ---------------------------------------------------------------------------


def test_arabic_cairo(app_context):
    r = lookup_geographic("Ø§Ù„Ù‚Ø§Ù‡Ø±Ø©", "city", "ar")
    assert r is not None
    assert r["normalised_form"] == "CAIRO"


def test_japanese_tokyo(app_context):
    r = lookup_geographic("æ±äº¬", "city", "ja")
    assert r is not None
    assert r["normalised_form"] == "TOKYO"


def test_russian_moscow(app_context):
    r = lookup_geographic("ÐœÐ¾ÑÐºÐ²Ð°", "city", "ru")
    assert r is not None
    assert r["normalised_form"] == "MOSCOW"


def test_german_munich(app_context):
    r = lookup_geographic("MÃ¼nchen", "city", "de")
    assert r is not None
    assert r["normalised_form"] == "MUNICH"


def test_english_city_tokyo(app_context):
    r = lookup_geographic("Tokyo", "city", "en")
    assert r is not None
    assert r["normalised_form"] == "TOKYO"


# ---------------------------------------------------------------------------
# Demonym â†’ country name resolution (nationality fields)
# ---------------------------------------------------------------------------


def test_demonym_arabic_germany_no_adjectival_form(app_context):
    """German adjectival/country name in Arabic â†’ GERMANY, never GERMAN."""
    r = lookup_geographic("Ø£Ù„Ù…Ø§Ù†ÙŠØ§", "nationality", "ar")
    assert r is not None
    assert r["normalised_form"] == "GERMANY"
    # Must not return the adjectival form
    assert r["normalised_form"] != "GERMAN"


def test_demonym_japanese_resolves_to_japan(app_context):
    r = lookup_geographic("æ—¥æœ¬", "nationality", "ja")
    assert r is not None
    assert r["normalised_form"] == "JAPAN"
    assert "JAPANESE" not in r["normalised_form"]


# ---------------------------------------------------------------------------
# Returns None for non-geographic field types
# ---------------------------------------------------------------------------


def test_returns_none_for_person_name(app_context):
    assert lookup_geographic("ç”°ä¸­", "person_name", "ja") is None


def test_returns_none_for_legal_form(app_context):
    assert lookup_geographic("GmbH", "legal_form", "de") is None


def test_returns_none_for_status(app_context):
    assert lookup_geographic("ACTIVE", "status", "en") is None


def test_returns_none_for_empty_text(app_context):
    assert lookup_geographic("", "nationality", "en") is None


def test_returns_none_for_unknown_text(app_context):
    assert lookup_geographic("xyzxyzxyz_notaplace_123", "nationality", "en") is None


# ---------------------------------------------------------------------------
# Confidence and review_required
# ---------------------------------------------------------------------------


def test_exact_match_confidence_high(app_context):
    r = lookup_geographic("Germany", "nationality", "en")
    assert r is not None
    assert r["confidence"] >= 0.85


def test_exact_match_no_review_required(app_context):
    r = lookup_geographic("Germany", "nationality", "en")
    assert r is not None
    assert r["review_required"] is False


# ---------------------------------------------------------------------------
# Hierarchy validation
# ---------------------------------------------------------------------------


def test_valid_hierarchy_tokyo_japan(app_context):
    valid, reason = validate_hierarchy("Tokyo", "Tokyo", "Japan")
    assert valid is True
    assert reason is None


def test_invalid_hierarchy_wrong_country(app_context):
    """Tokyo is not in Germany."""
    valid, reason = validate_hierarchy("Tokyo", "Tokyo", "Germany")
    assert valid is False
    assert reason is not None


def test_unknown_city_passes_through(app_context):
    """City not in index â†’ returns True (cannot validate)."""
    valid, reason = validate_hierarchy("SmallUnknownVillage99999", "SomeRegion", "Germany")
    assert valid is True
    assert reason is None


# ---------------------------------------------------------------------------
# Router integration
# ---------------------------------------------------------------------------


def test_router_returns_geographic_for_nationality(app_context):
    from app.pipeline.normalisation.router import route_field

    result = route_field({"original_text": "Germany", "field_type": "nationality"})
    assert result["processing_method"] == "GEOGRAPHIC"


