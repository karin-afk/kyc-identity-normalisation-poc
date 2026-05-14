import os
import pytest
from app.pipeline.normalisation import nmt_translator
from app.pipeline.normalisation.nmt_translator import apply_nmt


# ── Field type gating — no mock needed, no Azure call made ────────────────────

def test_returns_none_for_person_name():
    assert apply_nmt("محمد عبد الله", "person_name", "ar") is None

def test_returns_none_for_company_name():
    assert apply_nmt("株式会社トヨタ", "company_name", "ja") is None

def test_returns_none_for_legal_form():
    assert apply_nmt("GmbH", "legal_form", "de") is None

def test_returns_none_for_date_field():
    assert apply_nmt("2025-05-08", "date_of_birth", "en") is None

def test_returns_none_for_passport_no():
    assert apply_nmt("TK1234567", "passport_no", "en") is None

def test_returns_none_for_short_text():
    assert apply_nmt("abc", "nature_of_business", "ja") is None


# ── Already English — no translation, return as-is ────────────────────────────

def test_english_prose_returned_as_is():
    r = apply_nmt("General trading and investment activities.", "nature_of_business", "en")
    assert r is not None
    assert r["normalised_form"] == "General trading and investment activities."
    assert r["processing_method"] == "NMT"
    assert r["should_use_in_screening"] is False


# ── Credential check — no mock needed ─────────────────────────────────────────

def test_returns_none_when_no_credentials(monkeypatch):
    monkeypatch.delenv("AZURE_TRANSLATOR_KEY", raising=False)
    monkeypatch.delenv("AZURE_TRANSLATOR_ENDPOINT", raising=False)
    r = apply_nmt("総合商社として国内外における商業活動", "nature_of_business", "ja")
    assert r is None


# ── Successful translation — Azure call mocked at boundary ────────────────────

def test_prose_field_translated(monkeypatch):
    """
    Mocks _call_azure_translator only — not apply_nmt or the router.
    Business logic (field type check, credential check) runs for real.
    """
    monkeypatch.setenv("AZURE_TRANSLATOR_ENDPOINT", "https://fake.cognitiveservices.azure.com/")
    monkeypatch.setenv("AZURE_TRANSLATOR_KEY", "fake-key-for-testing")

    monkeypatch.setattr(
        nmt_translator,
        "_call_azure_translator",
        lambda text, target, source, endpoint, key, region:
            "As a general trading company, engaged in domestic and international commercial activities."
    )

    r = apply_nmt(
        "総合商社として国内外における商業活動",
        "nature_of_business",
        "ja",
    )
    assert r is not None
    assert r["processing_method"] == "NMT"
    assert r["confidence"] == 0.80
    assert r["should_use_in_screening"] is False
    assert "trading" in r["normalised_form"].lower()


def test_accounting_policies_field_translated(monkeypatch):
    monkeypatch.setenv("AZURE_TRANSLATOR_ENDPOINT", "https://fake.cognitiveservices.azure.com/")
    monkeypatch.setenv("AZURE_TRANSLATOR_KEY", "fake-key")
    monkeypatch.setattr(
        nmt_translator, "_call_azure_translator",
        lambda *a, **kw: "Financial statements are prepared on a historical cost basis."
    )
    r = apply_nmt("الحسابات الختامية تُعدّ وفق مبدأ التكلفة التاريخية.", "accounting_policies", "ar")
    assert r is not None
    assert r["processing_method"] == "NMT"


def test_azure_failure_returns_none(monkeypatch):
    """Azure call failure must return None, not raise."""
    monkeypatch.setenv("AZURE_TRANSLATOR_ENDPOINT", "https://fake.cognitiveservices.azure.com/")
    monkeypatch.setenv("AZURE_TRANSLATOR_KEY", "fake-key")
    monkeypatch.setattr(
        nmt_translator, "_call_azure_translator",
        lambda *a, **kw: (_ for _ in ()).throw(RuntimeError("Azure unreachable"))
    )
    r = apply_nmt("総合商社として", "nature_of_business", "ja")
    assert r is None


# ── Router integration ────────────────────────────────────────────────────────

def test_prose_field_routes_to_nmt_when_available(monkeypatch):
    """
    Full route test: route_field() with a prose field type.
    Mocks the Azure boundary call only.
    """
    from app.pipeline.normalisation import nmt_translator as nmt_mod
    from app.pipeline.normalisation.router import route_field

    monkeypatch.setenv("AZURE_TRANSLATOR_ENDPOINT", "https://fake.cognitiveservices.azure.com/")
    monkeypatch.setenv("AZURE_TRANSLATOR_KEY", "fake-key")
    monkeypatch.setattr(
        nmt_mod, "_call_azure_translator",
        lambda *a, **kw: "General trading company engaged in commercial activities."
    )

    r = route_field({
        "original_text": "総合商社として国内外における商業活動",
        "field_type":    "nature_of_business",
        "language":      "ja",
    })
    assert r["processing_method"] == "NMT"
    assert r["should_use_in_screening"] is False


def test_name_field_does_not_route_to_nmt():
    from app.pipeline.normalisation.router import route_field
    r = route_field({
        "original_text": "田中 太郎",
        "field_type":    "person_name",
        "language":      "ja",
    })
    assert r["processing_method"] != "NMT"
