"""End-to-end pipeline tests.

Calls process_field_row() with real lookup tables, zero mocks.
Covers all four resolution strategies (A, B, C, UNRESOLVED).

A Flask app context is pushed once per module so Strategy C can access
current_app.vocab_service via the router.
"""

import pytest

from app import create_app
from app.pipeline.orchestrator import process_field_row


@pytest.fixture(scope="module")
def app_ctx():
    """Push a Flask app context for the duration of this module."""
    app = create_app("testing")
    ctx = app.app_context()
    ctx.push()
    yield
    ctx.pop()


# ---------------------------------------------------------------------------
# Strategy A — PRESERVE
# ---------------------------------------------------------------------------


def test_e2e_preserve_arabic_indic_id_no(app_ctx):
    """Arabic-Indic digit id_no must be returned verbatim, not converted."""
    result = process_field_row({"original_text": "١٢٣٤٥٦٧", "field_type": "id_no", "language": "ar"})
    assert result["processing_method"] == "PRESERVE"
    assert result["normalised_form"] == "١٢٣٤٥٦٧"
    assert result["confidence"] == 1.0


def test_e2e_preserve_company_no(app_ctx):
    result = process_field_row({"original_text": "SC123456", "field_type": "company_no"})
    assert result["processing_method"] == "PRESERVE"
    assert result["normalised_form"] == "SC123456"
    assert result["should_use_in_screening"] is True


# ---------------------------------------------------------------------------
# Strategy B — CALENDAR
# ---------------------------------------------------------------------------


def test_e2e_calendar_reiwa_date(app_ctx):
    """Japanese Reiwa 5 year 7 month 3 day → ISO 2023-07-03."""
    result = process_field_row({
        "original_text": "令和5年7月3日",
        "field_type": "date_of_birth",
        "language": "ja",
    })
    assert result["processing_method"] == "CALENDAR"
    assert result["normalised_form"] == "2023-07-03"


def test_e2e_calendar_thai_buddhist_date(app_ctx):
    """Thai Buddhist Era 2568/5/8 → Gregorian 2025-05-08."""
    result = process_field_row({
        "original_text": "2568/5/8",
        "field_type": "date_of_birth",
        "language": "th",
    })
    assert result["processing_method"] == "CALENDAR"
    assert result["normalised_form"] == "2025-05-08"


# ---------------------------------------------------------------------------
# Strategy B — NUMERIC
# ---------------------------------------------------------------------------


def test_e2e_numeric_triangle_negative(app_ctx):
    """Japanese triangle-negative △4,191 must become -4191."""
    result = process_field_row({"original_text": "△4,191", "field_type": "revenue"})
    assert result["processing_method"] == "NUMERIC"
    assert result["normalised_form"] == "-4191"


def test_e2e_numeric_european_format(app_ctx):
    """European decimal format 1.234.567,89 must become 1234567.89."""
    result = process_field_row({"original_text": "1.234.567,89", "field_type": "total_assets"})
    assert result["processing_method"] == "NUMERIC"
    assert result["normalised_form"] == "1234567.89"


# ---------------------------------------------------------------------------
# Strategy C — VOCABULARY
# ---------------------------------------------------------------------------


def test_e2e_vocab_legal_form_japanese_kk(app_ctx):
    result = process_field_row({
        "original_text": "株式会社",
        "field_type": "legal_form",
        "language": "ja",
        "country": "JP",
    })
    assert result["processing_method"] == "VOCABULARY"
    assert result["normalised_form"] == "KK"


def test_e2e_vocab_legal_form_russian_llc(app_ctx):
    result = process_field_row({
        "original_text": "ООО",
        "field_type": "legal_form",
        "language": "ru",
        "country": "RU",
    })
    assert result["processing_method"] == "VOCABULARY"
    assert result["normalised_form"] == "LLC"


def test_e2e_vocab_status_japanese_active(app_ctx):
    result = process_field_row({"original_text": "現役", "field_type": "status", "language": "ja"})
    assert result["processing_method"] == "VOCABULARY"
    assert result["normalised_form"] == "ACTIVE"


def test_e2e_vocab_status_arabic_dissolved(app_ctx):
    result = process_field_row({"original_text": "منتهي", "field_type": "status", "language": "ar"})
    assert result["processing_method"] == "VOCABULARY"
    assert result["normalised_form"] == "DISSOLVED"


def test_e2e_vocab_role_japanese_director(app_ctx):
    result = process_field_row({"original_text": "取締役", "field_type": "role", "language": "ja"})
    assert result["processing_method"] == "VOCABULARY"
    assert result["normalised_form"] == "DIRECTOR"


def test_e2e_vocab_capital_change_japanese_increase(app_ctx):
    result = process_field_row({
        "original_text": "増資",
        "field_type": "capital_change_type",
        "language": "ja",
    })
    assert result["processing_method"] == "VOCABULARY"
    assert result["normalised_form"] == "INCREASE"


def test_e2e_vocab_share_class_english_ordinary(app_ctx):
    result = process_field_row({
        "original_text": "Ordinary Shares",
        "field_type": "share_class",
        "language": "en",
    })
    assert result["processing_method"] == "VOCABULARY"
    assert result["normalised_form"] == "ORDINARY"


def test_e2e_vocab_issuing_authority_japanese(app_ctx):
    result = process_field_row({
        "original_text": "東京都公安委員会",
        "field_type": "issuing_authority",
        "language": "ja",
        "country": "JP",
    })
    assert result["processing_method"] == "VOCABULARY"
    assert result["normalised_form"] == "TOKYO METROPOLITAN PUBLIC SAFETY COMMISSION"


# ---------------------------------------------------------------------------
# UNRESOLVED
# ---------------------------------------------------------------------------


def test_e2e_unresolved_arabic_person_name(app_ctx):
    """Person names are not yet handled by any strategy — must be UNRESOLVED."""
    result = process_field_row({
        "original_text": "محمد علي",
        "field_type": "person_name",
        "language": "ar",
    })
    assert result["processing_method"] == "UNRESOLVED"
    assert result["review_required"] is True
    assert result["should_use_in_screening"] is False
