from pathlib import Path
import json

from app.pipeline.normalisation.vocabulary_lookup import (
    ALLOWED_DOCUMENT_TYPE_LABELS,
    ALLOWED_STATUS_VALUES,
    VocabularyLookupService,
)


TABLES_DIR = Path(__file__).resolve().parents[1] / "data" / "lookup_tables"


def _service() -> VocabularyLookupService:
    return VocabularyLookupService(TABLES_DIR)


def test_lookup_legal_form_de_suffix_match():
    svc = _service()
    result = svc.lookup("legal_form", "Musterfirma GmbH", language="de", country="DE")
    assert result is not None
    assert result["processing_method"] == "VOCABULARY"
    assert result["normalised_form"] == "GMBH"


def test_lookup_status_fallback_to_english():
    svc = _service()
    result = svc.lookup("status", "Good Standing", language="xx", country="")
    assert result is not None
    assert result["normalised_form"] == "ACTIVE"


def test_lookup_role_strips_trailing_punctuation():
    svc = _service()
    result = svc.lookup("role", "Director.", language="en", country="")
    assert result is not None
    assert result["normalised_form"] == "DIRECTOR"


def test_lookup_document_type_arabic():
    svc = _service()
    result = svc.lookup("document_type", "جواز سفر", language="ar", country="")
    assert result is not None
    assert result["normalised_form"] == "passport"


def test_lookup_capital_change_japanese():
    svc = _service()
    result = svc.lookup("capital_change_type", "増資", language="ja", country="")
    assert result is not None
    assert result["normalised_form"] == "INCREASE"


def test_lookup_industry_code_parent_match():
    svc = _service()
    result = svc.lookup("industry_code", "K64.19", language="en", country="")
    assert result is not None
    assert result["normalised_form"] == "Other monetary intermediation"


def test_lookup_unsupported_field_returns_none():
    svc = _service()
    assert svc.lookup("person_name", "John Smith", language="en", country="") is None


def test_status_terms_values_are_canonical():
    raw = json.loads((TABLES_DIR / "status_terms.json").read_text(encoding="utf-8"))
    for lang, mapping in raw.items():
        if str(lang).startswith("_"):
            continue
        for _, canonical in mapping.items():
            assert canonical in ALLOWED_STATUS_VALUES


def test_document_type_values_are_canonical():
    raw = json.loads((TABLES_DIR / "document_type_labels.json").read_text(encoding="utf-8"))
    for lang, mapping in raw.items():
        if str(lang).startswith("_"):
            continue
        for _, canonical in mapping.items():
            assert canonical in ALLOWED_DOCUMENT_TYPE_LABELS
