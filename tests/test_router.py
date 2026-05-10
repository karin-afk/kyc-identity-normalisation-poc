"""Tests for minimal normalisation router, detector, and orchestrator."""

import pytest

from app import create_app
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


def test_detect_field_type_parses_llm_json(monkeypatch):
    from app.pipeline.normalisation import field_type_detector

    class _FakeCompletions:
        @staticmethod
        def create(**kwargs):
            class _Message:
                content = '{"field_type": "person_name", "language_code": "ja", "confidence": 0.91}'

            class _Choice:
                message = _Message()

            class _Response:
                choices = [_Choice()]

            return _Response()

    class _FakeChat:
        completions = _FakeCompletions()

    class _FakeClient:
        chat = _FakeChat()

    monkeypatch.setattr(field_type_detector, "_get_client", lambda: _FakeClient())

    ft, conf, language = detect_field_type("田中 太郎")
    assert ft == "person_name"
    assert conf == pytest.approx(0.91)
    assert language == "ja"


def test_detect_field_type_fallback_on_error(monkeypatch):
    from app.pipeline.normalisation import field_type_detector

    def _raise():
        raise RuntimeError("no key")

    monkeypatch.setattr(field_type_detector, "_get_client", _raise)

    ft, conf, language = detect_field_type("anything")
    assert ft == "unstructured_text"
    assert conf == pytest.approx(0.5)
    assert language == "en"


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


def test_strategy_c_vocabulary_in_router_with_app_context():
    app = create_app("testing")
    with app.app_context():
        result = route_field(
            {
                "original_text": "GmbH",
                "field_type": "legal_form",
                "language": "de",
                "country": "DE",
            }
        )
    assert result["processing_method"] == "VOCABULARY"
    assert result["normalised_form"] == "GMBH"
    assert result["review_required"] is False


def test_orchestrator_document_file_raises_not_implemented():
    with pytest.raises(NotImplementedError):
        process_document_file("/some/file.pdf", "auto", "")
