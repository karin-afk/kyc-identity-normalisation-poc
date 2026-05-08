"""Unit tests for Strategy A preserve behavior."""

import pytest

from app.pipeline.normalisation.field_types import (
    FINANCIAL_NUMERIC_FIELDS,
    PRESERVE_FIELDS,
    ProcessingMethod,
)
from app.pipeline.normalisation.preserve import apply_preserve


@pytest.mark.parametrize("field_type", PRESERVE_FIELDS)
def test_preserve_returns_result_for_all_preserve_fields(field_type: str) -> None:
    result = apply_preserve(field_type, "ABC123")
    assert result is not None


@pytest.mark.parametrize("field_type", PRESERVE_FIELDS)
def test_preserve_normalised_form_equals_input(field_type: str) -> None:
    value = "X1234567"
    result = apply_preserve(field_type, value)
    assert result["normalised_form"] == value


@pytest.mark.parametrize("field_type", PRESERVE_FIELDS)
def test_preserve_never_alters_value(field_type: str) -> None:
    value = "abc-123 / xyz"
    result = apply_preserve(field_type, value)
    assert result["normalised_form"] == value


def test_preserve_confidence_is_1() -> None:
    result = apply_preserve("passport_no", "TK1234567")
    assert result["confidence"] == 1.0


def test_preserve_review_not_required() -> None:
    result = apply_preserve("passport_no", "TK1234567")
    assert result["review_required"] is False


def test_preserve_no_variants() -> None:
    result = apply_preserve("passport_no", "TK1234567")
    assert result["allowed_variants"] == []


def test_preserve_processing_method_label() -> None:
    result = apply_preserve("passport_no", "TK1234567")
    assert result["processing_method"] == ProcessingMethod.PRESERVE


def test_preserve_should_use_in_screening() -> None:
    result = apply_preserve("passport_no", "TK1234567")
    assert result["should_use_in_screening"] is True


@pytest.mark.parametrize(
    "field_type",
    [
        "person_name",
        "company_name",
        "address",
        "legal_form",
        "status",
        "nationality",
        "date_of_birth",
        "business_purpose",
    ],
)
def test_preserve_returns_none_for_non_preserve_fields(field_type: str) -> None:
    result = apply_preserve(field_type, "some value")
    assert result is None


def test_preserve_empty_string() -> None:
    result = apply_preserve("passport_no", "")
    assert result is not None
    assert result["normalised_form"] == ""


def test_preserve_arabic_indic_digits_not_converted() -> None:
    value = "١٢٣٤٥٦٧"
    result = apply_preserve("id_no", value)
    assert result["normalised_form"] == value


def test_preserve_unicode_not_normalised() -> None:
    value = "Ａ１２３"
    result = apply_preserve("registration_no", value)
    assert result["normalised_form"] == value


@pytest.mark.parametrize("field_type", FINANCIAL_NUMERIC_FIELDS)
def test_financial_numeric_fields_are_not_preserve(field_type: str) -> None:
    result = apply_preserve(field_type, "1.234.567,89")
    assert result is None
