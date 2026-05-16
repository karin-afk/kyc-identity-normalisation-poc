"""Tests for Strategy B calendar and numeric rules."""

from app.pipeline.normalisation.calendar_rules import (
    apply_calendar_rules,
    apply_numeric_rules,
)
from app.pipeline.normalisation.numeric_rules import normalise_all_digits
from utils.calendar_utils import (
    arabic_indic_to_ascii,
    detect_and_convert_japanese_era,
    detect_calendar_system,
    hijri_to_gregorian,
)


def test_hijri_to_gregorian_known_date():
    y, m, d = hijri_to_gregorian(1445, 9, 1)
    assert f"{y:04d}-{m:02d}-{d:02d}" == "2024-03-11"


def test_japanese_era_showa():
    result = detect_and_convert_japanese_era("昭和60年3月12日")
    assert result["normalised"] == "1985-03-12"


def test_japanese_era_reiwa():
    result = detect_and_convert_japanese_era("令和5年7月3日")
    assert result["normalised"] == "2023-07-03"


def test_arabic_indic_digits():
    assert arabic_indic_to_ascii("١٩٨٥/٠٣/١٢") == "1985/03/12"


def test_eastern_arabic_indic_digits():
    converted = arabic_indic_to_ascii("۱۴۴۵/۰۹/۰۱")
    assert converted == "1445/09/01"
    assert detect_calendar_system(converted) == "hijri"


def test_solar_hijri_known_date():
    result = apply_calendar_rules("date_of_birth", "1404/2/15", language="fa")
    assert result is not None
    assert result["normalised_form"] == "2025-05-05"
    assert result["original_calendar"] == "solar_hijri"


def test_hebrew_known_date():
    result = apply_calendar_rules("date_of_birth", "1 תשרי 5786", language="he")
    assert result is not None
    assert result["normalised_form"] == "2025-09-23"
    assert result["original_calendar"] == "hebrew"


def test_thai_buddhist_known_date():
    result = apply_calendar_rules("date_of_birth", "2568/5/8", language="th")
    assert result is not None
    assert result["normalised_form"] == "2025-05-08"
    assert result["original_calendar"] == "thai_buddhist"


def test_minguo_known_date():
    result = apply_calendar_rules("date_of_birth", "114/5/8", country="TW")
    assert result is not None
    assert result["normalised_form"] == "2025-05-08"
    assert result["original_calendar"] == "minguo"


def test_thai_date_detected_by_language():
    result = apply_calendar_rules("date", "08/05/2568", language="th")
    assert result is not None
    assert result["original_calendar"] == "thai_buddhist"


def test_minguo_detected_by_country_tw():
    result = apply_calendar_rules("date", "114/05/08", country="TW")
    assert result is not None
    assert result["original_calendar"] == "minguo"


def test_solar_hijri_detected_by_language_fa():
    result = apply_calendar_rules("date", "1404/2/15", language="fa")
    assert result is not None
    assert result["original_calendar"] == "solar_hijri"


def test_hebrew_detected_by_language_he():
    result = apply_calendar_rules("date", "15 תשרי 5786", language="he")
    assert result is not None
    assert result["original_calendar"] == "hebrew"


def test_fullwidth_digits():
    assert normalise_all_digits("０１２３") == "0123"


def test_devanagari_digits():
    assert normalise_all_digits("०१२३") == "0123"


def test_thai_digits():
    assert normalise_all_digits("๐๑๒๓") == "0123"


def test_european_number_format():
    result = apply_numeric_rules("total_assets", "1.234.567,89")
    assert result is not None
    assert result["normalised_form"] == "1234567.89"


def test_swiss_number_format():
    result = apply_numeric_rules("total_assets", "1'234'567.89")
    assert result is not None
    assert result["normalised_form"] == "1234567.89"


def test_parenthetical_negative_triangle():
    result = apply_numeric_rules("total_assets", "△4191")
    assert result is not None
    assert result["normalised_form"] == "-4191"


def test_parenthetical_negative_fullwidth():
    result = apply_numeric_rules("total_assets", "（4191）")
    assert result is not None
    assert result["normalised_form"] == "-4191"


def test_parenthetical_negative_ascii():
    result = apply_numeric_rules("total_assets", "(4191)")
    assert result is not None
    assert result["normalised_form"] == "-4191"


def test_currency_yen_japanese():
    result = apply_numeric_rules("share_capital", "¥1,234", language="ja")
    assert result is not None
    assert result["currency_code"] == "JPY"


def test_currency_yen_chinese():
    result = apply_numeric_rules("share_capital", "¥1,234", language="zh", country="CN")
    assert result is not None
    assert result["currency_code"] == "CNY"


def test_currency_rial():
    result = apply_numeric_rules("share_capital", "﷼500,000")
    assert result is not None
    assert result["currency_code"] == "SAR"


def test_currency_shekel():
    result = apply_numeric_rules("share_capital", "₪500,000")
    assert result is not None
    assert result["currency_code"] == "ILS"


def test_returns_none_for_non_numeric_field():
    assert apply_numeric_rules("person_name", "1234") is None


def test_returns_none_for_preserve_field():
    assert apply_numeric_rules("passport_no", "1234") is None


# ---------------------------------------------------------------------------
# Content-driven path: unstructured_text + pure non-ASCII digit glyphs
# ---------------------------------------------------------------------------


def test_arabic_indic_digits_in_unstructured_text_converts():
    """Arabic-Indic digits pasted as unstructured_text must convert to ASCII, preserving separators."""
    result = apply_numeric_rules("unstructured_text", "\u0660,\u0661,\u0662,\u0663,\u0664,\u0665,\u0666,\u0667,\u0668,\u0669", language="ar")
    assert result is not None
    assert result["normalised_form"] == "0,1,2,3,4,5,6,7,8,9"
    assert result["processing_method"] == "NUMERIC"


def test_extended_arabic_indic_digits_in_unstructured_text_converts():
    """Extended Arabic-Indic (Persian) digits must also convert."""
    result = apply_numeric_rules("unstructured_text", "\u06f1\u06f2\u06f3", language="fa")
    assert result is not None
    assert result["normalised_form"] == "123"


def test_arabic_text_in_unstructured_text_does_not_convert():
    """Non-digit Arabic text must NOT be intercepted by the numeric path."""
    result = apply_numeric_rules("unstructured_text", "\u0645\u062d\u0645\u062f \u0639\u0644\u064a", language="ar")
    assert result is None


def test_preserve_field_with_arabic_indic_digits_not_intercepted():
    """id_no with Arabic-Indic digits must NOT be intercepted (PRESERVE takes priority via router)."""
    result = apply_numeric_rules("id_no", "\u0661\u0662\u0663\u0664\u0665\u0666\u0667")
    assert result is None
