"""Data integrity tests.

Validates lookup table JSON files against canonical value sets.
No app code — pure JSON loading. Runs at repository root.
"""

import json
from pathlib import Path

import pytest

TABLES = Path(__file__).resolve().parents[1] / "data" / "lookup_tables"

EXPECTED_FILES = [
    "capital_change_types.json",
    "document_type_labels.json",
    "industry_codes.json",
    "issuing_authorities.json",
    "legal_forms.json",
    "role_titles.json",
    "share_classes.json",
    "status_terms.json",
    "street_types.json",
]

ALLOWED_STATUS_VALUES = {
    "ACTIVE", "DISSOLVED", "DORMANT", "INACTIVE",
    "IN_LIQUIDATION", "STRUCK_OFF", "SUSPENDED",
}

ALLOWED_DOCUMENT_TYPE_LABELS = {
    "aoa", "company_registry_local", "drivers_licence", "financial_statement",
    "national_id", "passport", "shareholder_table", "unknown",
}

ALLOWED_SHARE_VALUES = {"ORDINARY", "PREFERENCE", "REDEEMABLE", "NON-VOTING", "MANAGEMENT"}

ALLOWED_CAPITAL_VALUES = {"INCREASE", "DECREASE", "CONVERSION", "SPLIT", "CONSOLIDATION"}


# ---------------------------------------------------------------------------
# File-level sanity
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("filename", EXPECTED_FILES)
def test_lookup_file_exists_and_is_non_empty(filename):
    path = TABLES / filename
    assert path.is_file(), f"{filename} missing from data/lookup_tables/"
    data = json.loads(path.read_text("utf-8"))
    assert data, f"{filename} is empty"


# ---------------------------------------------------------------------------
# Canonical value validation
# ---------------------------------------------------------------------------


def test_status_terms_values_are_canonical():
    data = json.loads((TABLES / "status_terms.json").read_text("utf-8"))
    for lang, mapping in data.items():
        if lang.startswith("_"):
            continue
        for native, canonical in mapping.items():
            assert canonical in ALLOWED_STATUS_VALUES, (
                f"status_terms.json [{lang}] '{native}' → '{canonical}' not in canonical set"
            )


def test_document_type_values_are_canonical():
    data = json.loads((TABLES / "document_type_labels.json").read_text("utf-8"))
    for lang, mapping in data.items():
        if lang.startswith("_"):
            continue
        for native, canonical in mapping.items():
            assert canonical in ALLOWED_DOCUMENT_TYPE_LABELS, (
                f"document_type_labels.json [{lang}] '{native}' → '{canonical}' not in canonical set"
            )


def test_share_class_values_are_canonical():
    data = json.loads((TABLES / "share_classes.json").read_text("utf-8"))
    for lang, mapping in data.items():
        if lang.startswith("_"):
            continue
        for native, canonical in mapping.items():
            assert canonical in ALLOWED_SHARE_VALUES, (
                f"share_classes.json [{lang}] '{native}' → '{canonical}' not in canonical set"
            )


def test_capital_change_values_are_canonical():
    data = json.loads((TABLES / "capital_change_types.json").read_text("utf-8"))
    for lang, mapping in data.items():
        if lang.startswith("_"):
            continue
        for native, canonical in mapping.items():
            assert canonical in ALLOWED_CAPITAL_VALUES, (
                f"capital_change_types.json [{lang}] '{native}' → '{canonical}' not in canonical set"
            )


# ---------------------------------------------------------------------------
# Structural validation
# ---------------------------------------------------------------------------


def test_legal_forms_country_codes_are_two_chars():
    data = json.loads((TABLES / "legal_forms.json").read_text("utf-8"))
    for key in data:
        if not key.startswith("_"):
            assert len(key) == 2, f"legal_forms.json has non-ISO country key: '{key}'"


def test_issuing_authorities_country_codes_are_two_chars():
    data = json.loads((TABLES / "issuing_authorities.json").read_text("utf-8"))
    for key in data:
        if not key.startswith("_"):
            assert len(key) == 2, f"issuing_authorities.json has non-ISO country key: '{key}'"


def test_legal_forms_values_are_non_empty_strings():
    data = json.loads((TABLES / "legal_forms.json").read_text("utf-8"))
    for country, mapping in data.items():
        if country.startswith("_"):
            continue
        assert isinstance(mapping, dict), f"legal_forms.json[{country}] is not a dict"
        for native, canonical in mapping.items():
            assert isinstance(canonical, str) and canonical, (
                f"legal_forms.json[{country}]['{native}'] is blank or non-string"
            )


def test_issuing_authorities_values_are_non_empty_strings():
    data = json.loads((TABLES / "issuing_authorities.json").read_text("utf-8"))
    for country, mapping in data.items():
        if country.startswith("_"):
            continue
        assert isinstance(mapping, dict), f"issuing_authorities.json[{country}] is not a dict"
        for native, canonical in mapping.items():
            assert isinstance(canonical, str) and canonical, (
                f"issuing_authorities.json[{country}]['{native}'] is blank or non-string"
            )
