import pytest
from pipeline.rules_engine import apply_rules
from utils.calendar_utils import arabic_indic_to_ascii, detect_calendar_system, normalise_date_field


def test_preserve_passport_number():
    result = apply_rules("passport_no", "563982174")
    assert result is not None
    assert result["normalised_form"] == "563982174"
    assert result["processing_method"] == "RULE"
    assert result["review_required"] is False
    assert result["original_text"] == "563982174"


def test_preserve_email():
    result = apply_rules("email", "john.doe@test.com")
    assert result["normalised_form"] == "john.doe@test.com"
    assert result["processing_method"] == "RULE"


def test_preserve_email_with_special_chars():
    # KYC025 — email with + must not be modified
    result = apply_rules("email", "test.user+aml@gmail.com")
    assert result["normalised_form"] == "test.user+aml@gmail.com"


def test_preserve_id_number():
    result = apply_rules("id_no", "ABC-123456")
    assert result["normalised_form"] == "ABC-123456"


def test_non_preserve_person_name_returns_none():
    result = apply_rules("person_name", "Taro Yamada")
    assert result is None


def test_non_preserve_address_returns_none():
    result = apply_rules("address", "123 Main Street")
    assert result is None


# ---------------------------------------------------------------------------
# Section 2: Arabic-Indic digit conversion
# ---------------------------------------------------------------------------

def test_arabic_indic_to_ascii_arabic():
    """Eastern Arabic-Indic digits ٠١٢٣٤٥٦٧٨٩ convert to ASCII."""
    assert arabic_indic_to_ascii("١٤٤٥") == "1445"


def test_arabic_indic_to_ascii_persian():
    """Persian/Farsi digits ۰۱…۹ convert to ASCII."""
    assert arabic_indic_to_ascii("۱۹۹۲") == "1992"


def test_arabic_indic_mixed_with_separators():
    """Digits and separators both preserved after conversion."""
    assert arabic_indic_to_ascii("٠٨/١١/١٩٩٢") == "08/11/1992"


# ---------------------------------------------------------------------------
# Section 2: Calendar detection
# ---------------------------------------------------------------------------

def test_detect_hijri_year():
    assert detect_calendar_system("1445/09/20") == "hijri"


def test_detect_gregorian_year():
    assert detect_calendar_system("1985/03/14") == "gregorian"


def test_detect_gregorian_arabic_indic():
    """Arabic-Indic date with Gregorian year → gregorian."""
    assert detect_calendar_system("٠٨/١١/١٩٩٢") == "gregorian"


def test_detect_hijri_arabic_indic():
    """Arabic-Indic date with Hijri year → hijri."""
    assert detect_calendar_system("١٤٤٥/٠٩/٢٠") == "hijri"


# ---------------------------------------------------------------------------
# Section 2: Date field normalisation via rules engine
# ---------------------------------------------------------------------------

def test_gregorian_arabic_indic_normalised():
    """٠٨/١١/١٩٩٢ (Arabic-Indic, Gregorian, DD/MM/YYYY) → 1992-11-08."""
    result = apply_rules("birth_date", "٠٨/١١/١٩٩٢")
    assert result is not None
    assert result["normalised_form"] == "1992-11-08"
    assert result["original_calendar"] == "gregorian"
    assert result["review_required"] is False
    assert result["processing_method"] == "RULE"


def test_gregorian_dd_mm_yyyy_normalised():
    """14/03/1985 (ASCII, DD/MM/YYYY) → 1985-03-14."""
    result = apply_rules("birth_date", "14/03/1985")
    assert result is not None
    assert result["normalised_form"] == "1985-03-14"
    assert result["original_calendar"] == "gregorian"
    assert result["review_required"] is False


def test_iso_gregorian_passthrough():
    """2024-03-14 already in ISO 8601 → unchanged."""
    result = apply_rules("date", "2024-03-14")
    assert result is not None
    assert result["normalised_form"] == "2024-03-14"
    assert result["original_calendar"] == "gregorian"
    assert result["review_required"] is False


def test_hijri_date_converted_and_flagged():
    """١٤٤٥/٠٩/٢٠ (Hijri) → Gregorian ISO 8601, review_required=True."""
    result = apply_rules("birth_date", "١٤٤٥/٠٩/٢٠")
    assert result is not None
    # Hijri 1445/09/20 → Gregorian 2024-03-30 (library result)
    assert result["normalised_form"] == "2024-03-30"
    assert result["original_calendar"] == "hijri"
    assert result["review_required"] is True
    assert result["review_reason"] is not None
    assert "Hijri" in result["review_reason"]


def test_birth_date_field_type_handled():
    """birth_date field type is handled by RULE (NORMALISE_NUMERIC)."""
    result = apply_rules("birth_date", "01/01/2000")
    assert result is not None
    assert result["processing_method"] == "RULE"


def test_date_field_type_handled():
    """date field type is handled by RULE (NORMALISE_NUMERIC)."""
    result = apply_rules("date", "01/01/2000")
    assert result is not None
    assert result["processing_method"] == "RULE"
