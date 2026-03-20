import pytest
from pipeline.pipeline import process_field


def test_preserve_field_end_to_end():
    """KYC026 — passport number must pass through unchanged."""
    row = {"field_type": "passport_no", "original_text": "563982174", "language": "en"}
    result = process_field(row)
    assert result["normalised_form"] == "563982174"
    assert result["processing_method"] == "RULE"


def test_preserve_email_end_to_end():
    """KYC027 — email must pass through unchanged."""
    row = {"field_type": "email", "original_text": "john.doe@test.com", "language": "en"}
    result = process_field(row)
    assert result["normalised_form"] == "john.doe@test.com"


def test_russian_name_end_to_end():
    """KYC012 — Russian name goes through transliteration layer."""
    row = {"field_type": "person_name", "original_text": "Алексей Смирнов", "language": "ru"}
    result = process_field(row)
    assert result["processing_method"] == "TRANSLITERATE"
    norm = result["normalised_form"]
    assert "SMIRNOV" in norm
    assert any(v in norm for v in ("ALEKSEI", "ALEKSEJ", "ALEXEY", "ALEKSEY"))


def test_address_routes_to_llm():
    """Addresses are routed to the LLM layer (stub returns LLM method)."""
    row = {
        "field_type": "address",
        "original_text": "ул. Ленина 10 Москва",
        "language": "ru",
    }
    result = process_field(row)
    assert result["processing_method"] == "LLM"
    assert result["original_text"] == "ул. Ленина 10 Москва"


def test_company_name_routes_to_llm():
    """Company names are routed to the LLM layer."""
    row = {
        "field_type": "company_name",
        "original_text": "株式会社トヨタ",
        "language": "ja",
    }
    result = process_field(row)
    assert result["processing_method"] == "LLM"


def test_result_always_has_original_text():
    """Every result must preserve the original text."""
    row = {"field_type": "person_name", "original_text": "李伟", "language": "zh"}
    result = process_field(row)
    assert result["original_text"] == "李伟"
