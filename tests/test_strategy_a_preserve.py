"""Strategy A (PRESERVE) tests.

All tests call route_field() directly, no mocks, no Flask app context required.
Strategy A is handled by src/pipeline/rules_engine.apply_rules() via the router
before Strategy C is ever reached, so no app context is needed for these tests.

Note on financial field types (revenue, total_assets, etc.):
The router tries Strategy B (NUMERIC) before Strategy A (PRESERVE). For financial
field types that are also in PRESERVE_FIELDS, a digit-containing input is intercepted
by Strategy B first. Tests use purely alphabetic inputs to exercise the PRESERVE path.
"""

import pytest

from app.pipeline.normalisation.router import PRESERVE_FIELDS, route_field


@pytest.mark.parametrize("field_type", PRESERVE_FIELDS)
def test_preserve_all_fields_returned_verbatim(field_type):
    """Every field in PRESERVE_FIELDS passes through unchanged for a non-numeric input."""
    result = route_field({"original_text": "ALPHA-XYZ", "field_type": field_type})
    assert result["normalised_form"] == "ALPHA-XYZ"
    assert result["processing_method"] == "PRESERVE"
    assert result["confidence"] == 1.0
    assert result["review_required"] is False
    assert result["allowed_variants"] == []
    assert result["should_use_in_screening"] is True


def test_preserve_arabic_indic_digits_not_transliterated():
    """Arabic-Indic digit strings must not be converted to ASCII by Strategy A."""
    result = route_field({"original_text": "\u06f1\u06f2\u06f3\u06f4\u06f5\u06f6\u06f7\u06f8\u06f9", "field_type": "id_no"})
    assert result["normalised_form"] == "\u06f1\u06f2\u06f3\u06f4\u06f5\u06f6\u06f7\u06f8\u06f9"
    assert result["processing_method"] == "PRESERVE"


def test_preserve_full_width_chars_not_normalised():
    """Full-width alphanumerics must survive PRESERVE without narrowing."""
    result = route_field({"original_text": "\uff21\uff11\uff12\uff13\uff14\uff15", "field_type": "passport_no"})
    assert result["normalised_form"] == "\uff21\uff11\uff12\uff13\uff14\uff15"
    assert result["processing_method"] == "PRESERVE"


def test_preserve_empty_string():
    result = route_field({"original_text": "", "field_type": "passport_no"})
    assert result["normalised_form"] == ""
    assert result["processing_method"] == "PRESERVE"
    assert result["confidence"] == 1.0


def test_preserve_registration_no_verbatim():
    result = route_field({"original_text": "DE-REG-ALPHA", "field_type": "registration_no"})
    assert result["normalised_form"] == "DE-REG-ALPHA"
    assert result["processing_method"] == "PRESERVE"


def test_preserve_email_verbatim():
    result = route_field({"original_text": "user@example.co.jp", "field_type": "email"})
    assert result["normalised_form"] == "user@example.co.jp"
    assert result["processing_method"] == "PRESERVE"


def test_preserve_tax_id_verbatim():
    result = route_field({"original_text": "GBREG-ALPHA", "field_type": "tax_id"})
    assert result["normalised_form"] == "GBREG-ALPHA"
    assert result["processing_method"] == "PRESERVE"
    assert result["should_use_in_screening"] is True
