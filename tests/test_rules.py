import pytest
from pipeline.rules_engine import apply_rules


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
