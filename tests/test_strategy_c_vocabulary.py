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


def test_lookup_issuing_authority_japanese_with_country():
    svc = _service()
    result = svc.lookup("issuing_authority", "東京都公安委員会", language="ja", country="JP")
    assert result is not None
    assert result["processing_method"] == "VOCABULARY"
    assert result["normalised_form"] == "TOKYO METROPOLITAN PUBLIC SAFETY COMMISSION"


def test_lookup_issuing_authority_japanese_no_country():
    """Should still resolve when no country is provided via any-country scan."""
    svc = _service()
    result = svc.lookup("issuing_authority", "東京都公安委員会", language="ja", country="")
    assert result is not None
    assert result["normalised_form"] == "TOKYO METROPOLITAN PUBLIC SAFETY COMMISSION"


def test_lookup_issuing_authority_arabic_uae():
    svc = _service()
    result = svc.lookup("issuing_authority", "وزارة الداخلية", language="ar", country="AE")
    assert result is not None
    assert result["normalised_form"] == "MINISTRY OF INTERIOR"


def test_lookup_issuing_authority_unknown_returns_none():
    svc = _service()
    result = svc.lookup("issuing_authority", "Unknown Fictional Authority XYZ", language="en", country="GB")
    assert result is None


def test_router_routes_issuing_authority_via_strategy_c():
    """End-to-end: router should resolve a known Japanese issuing authority via Strategy C.
    Requires an app context because _try_strategy_c() uses current_app."""
    from app import create_app
    from app.pipeline.normalisation.router import route_field

    app = create_app("testing")
    with app.app_context():
        result = route_field({
            "original_text": "東京都公安委員会",
            "field_type": "issuing_authority",
            "language": "ja",
            "country": "JP",
        })
    assert result["processing_method"] == "VOCABULARY"
    assert result["normalised_form"] == "TOKYO METROPOLITAN PUBLIC SAFETY COMMISSION"
    assert result["review_required"] is False
