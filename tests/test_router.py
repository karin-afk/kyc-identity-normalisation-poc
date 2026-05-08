"""Tests for minimal normalisation router, detector, and orchestrator."""

import pytest

from app.pipeline.normalisation.field_type_detector import detect_field_type
from app.pipeline.normalisation.router import route_field
from app.pipeline.orchestrator import process_document_file, process_field_row


@pytest.mark.parametrize(
    "field_type,value",
    [
        ("passport_no", "TK1234567"),
        ("id_no", "987654321"),
        ("email", "john.doe@example.com"),
        ("registration_no", "DE123456789"),
        ("company_no", "SC123456"),
        ("tax_id", "GB123456789"),
    ],
)
def test_preserve_fields_returned_verbatim(field_type, value):
    result = route_field({"original_text": value, "field_type": field_type})
    assert result["normalised_form"] == value
    assert result["processing_method"] == "PRESERVE"
    assert result["confidence"] == 1.0
    assert result["review_required"] is False
    assert result["allowed_variants"] == []
    assert result["should_use_in_screening"] is True


def test_preserve_arabic_indic_digits_not_converted():
    result = route_field({"original_text": "١٢٣٤٥٦٧", "field_type": "id_no"})
    assert result["normalised_form"] == "١٢٣٤٥٦٧"


def test_preserve_full_width_digits_not_converted():
    result = route_field({"original_text": "Ａ１２３４５", "field_type": "passport_no"})
    assert result["normalised_form"] == "Ａ１２３４５"


def test_preserve_empty_string():
    result = route_field({"original_text": "", "field_type": "passport_no"})
    assert result["normalised_form"] == ""
    assert result["processing_method"] == "PRESERVE"


@pytest.mark.parametrize(
    "field_type",
    [
        "person_name",
        "company_name",
        "address",
        "legal_form",
        "status",
        "nationality",
    ],
)
def test_unresolved_for_non_preserve_fields(field_type):
    result = route_field({"original_text": "Some text", "field_type": field_type})
    assert result["processing_method"] == "UNRESOLVED"
    assert result["review_required"] is True
    assert result["normalised_form"] is None
    assert result["should_use_in_screening"] is False


def test_detect_email():
    ft, conf = detect_field_type("john.doe@example.com")
    assert ft == "email"
    assert conf >= 0.90


def test_detect_date_iso():
    ft, _ = detect_field_type("1985-03-12")
    assert ft == "date_of_birth"


def test_detect_date_japanese_era():
    ft, _ = detect_field_type("令和5年7月3日")
    assert ft == "date_of_birth"


def test_detect_person_name_short():
    ft, _ = detect_field_type("田中 太郎")
    assert ft == "person_name"


def test_detect_company_with_ltd():
    ft, conf = detect_field_type("Acme Corp Ltd")
    assert ft == "company_name"
    assert conf >= 0.85


def test_detect_address_street_keyword():
    ft, _ = detect_field_type("123 Main Street London")
    assert ft == "address"


def test_detect_fallback():
    ft, _ = detect_field_type("x")
    assert ft in ("person_name", "unstructured_text")


def test_orchestrator_preserve():
    result = process_field_row(
        {
            "original_text": "TK1234567",
            "field_type": "passport_no",
            "language": "en",
        }
    )
    assert result["normalised_form"] == "TK1234567"
    assert result["processing_method"] == "PRESERVE"


def test_orchestrator_unresolved():
    result = process_field_row(
        {
            "original_text": "محمد",
            "field_type": "person_name",
            "language": "ar",
        }
    )
    assert result["processing_method"] == "UNRESOLVED"
    assert result["review_required"] is True


def test_strategy_b_calendar_in_router():
    result = route_field(
        {
            "original_text": "2568/5/8",
            "field_type": "date_of_birth",
            "language": "th",
        }
    )
    assert result["processing_method"] == "CALENDAR"
    assert result["normalised_form"] == "2025-05-08"


def test_strategy_b_numeric_in_router():
    result = route_field(
        {
            "original_text": "△4.191",
            "field_type": "total_assets",
            "language": "ja",
        }
    )
    assert result["processing_method"] == "NUMERIC"
    assert result["normalised_form"] == "-4191"


def test_orchestrator_document_file_raises_not_implemented():
    with pytest.raises(NotImplementedError):
        process_document_file("/some/file.pdf", "auto", "")
