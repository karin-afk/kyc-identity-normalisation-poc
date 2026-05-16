# Epic 08 — Strategy H: Azure Translator NMT

## Status: ✅ IMPLEMENTED — 2026-05-11

**Branch:** `epic-08-strategy-h` (commit `2c7226d`) — pushed to remote  
**Tests:** 13/13 pass (`tests/test_strategy_h_nmt.py`)  
**Router order:** A → B → C → D → G → F → **H** → I

### What was built
- `app/pipeline/normalisation/nmt_translator.py` — full `apply_nmt()` + `_call_azure_translator()` replacing the stub
- `app/pipeline/normalisation/field_types.py` — added `PROSE_FIELDS` list; corrected NMT confidence `0.75 → 0.80`
- `app/pipeline/normalisation/router.py` — real `_try_strategy_h()` wired after F; removed H from `_try_stub` loop
- `requirements.txt` — added `azure-ai-translation-text>=1.0.0`
- `tests/test_strategy_h_nmt.py` — 13 tests (field gating, credential check, already-English, mock translation, Azure failure, router integration)

---

## Save to: `prompts/todo/epic-08-strategy-h-nmt-translator.md`

---

## Context

Strategy H translates free-text prose fields into readable English using Azure AI
Translator (Neural Machine Translation). It is NOT a generative AI — it is a
purpose-built translation engine. The same input always produces the same output.

**Critical constraints:**
- Strategy H is called ONLY for `PROSE_FIELDS` — never for names, identifiers, dates,
  or any field requiring KYC-formatted output or variant generation
- The Azure Translator resource is behind a private endpoint configured for NMT-only mode
- `LLM_ENABLED` in `.env` has no effect on this strategy — NMT is not an LLM
- If `AZURE_TRANSLATOR_KEY` or `AZURE_TRANSLATOR_ENDPOINT` is not set, Strategy H must
  fail gracefully and return `None` so the router falls through to Strategy I

---

## What exists

- `app/pipeline/normalisation/nmt_translator.py` — exists but is a stub
- `AZURE_TRANSLATOR_ENDPOINT`, `AZURE_TRANSLATOR_KEY`, `AZURE_TRANSLATOR_REGION`,
  `AZURE_TRANSLATOR_TARGET_LANGUAGE` — already in `.env.example` and `app/config.py`
- `PROSE_FIELDS` — already defined in `app/pipeline/normalisation/field_types.py`

---

## What does NOT exist and must be built

- The real implementation of `apply_nmt()` in `app/pipeline/normalisation/nmt_translator.py`
- The router stub `_try_strategy_h()` replaced with a real call
- Tests in `tests/test_strategy_h_nmt.py`

---

## What you need to provide before running this epic

Nothing. This epic is built entirely by Copilot using the Azure SDK and config values
already in the codebase. Ensure `AZURE_TRANSLATOR_ENDPOINT` and `AZURE_TRANSLATOR_KEY`
are set in `.env` before running the app — tests mock the Azure call so they run without
a live Azure connection.

---

## Path conventions

- Module: `app/pipeline/normalisation/nmt_translator.py`
- Config values read from `current_app.config` or `os.environ` (no hardcoding)
- JSON data files (if any): `data/lookup_tables/` (project root)
- Test file: `tests/test_strategy_h_nmt.py`
- No imports from `src/` at runtime

---

## Implementation — `app/pipeline/normalisation/nmt_translator.py`

Replace existing stub entirely.

```python
"""
Strategy H — Azure Translator NMT.

Translates prose fields to readable English using Azure AI Translator.
This is Neural Machine Translation — not a generative AI. No text is generated;
the same input always produces the same output.

Applied ONLY to PROSE_FIELDS:
    nature_of_business, business_purpose, accounting_policies,
    locality_information, capital_changes_narrative, unstructured_text

Never applied to:
    person names, company names, addresses, dates, identifiers, legal forms,
    status terms, roles — any field requiring KYC-formatted output or variants.

Fails gracefully if Azure credentials are not configured — returns None so
the router falls through to Strategy I (native speaker review).

Azure SDK: azure-ai-translation-text
Endpoint:  AZURE_TRANSLATOR_ENDPOINT (from .env)
Key:       AZURE_TRANSLATOR_KEY (from .env)
Region:    AZURE_TRANSLATOR_REGION (from .env)
Target:    AZURE_TRANSLATOR_TARGET_LANGUAGE (from .env, default "en")
"""

import os
from app.pipeline.normalisation.field_types import (
    PROSE_FIELDS, ProcessingMethod, STRATEGY_CONFIDENCE,
)


def apply_nmt(text: str, field_type: str, language: str = "") -> dict | None:
    """
    Strategy H entry point called by the normalisation router.

    Returns None if:
    - field_type is not in PROSE_FIELDS
    - Azure credentials are not configured
    - The detected language is already English (language == "en")
    - The text is fewer than 10 characters (not worth translating)
    - Azure call fails for any reason

    Args:
        text:       Raw prose text to translate.
        field_type: KYC field type — must be in PROSE_FIELDS.
        language:   ISO 639-1 source language code. If empty, Azure auto-detects.

    Returns:
        Result dict with processing_method=NMT, or None.
    """
    if field_type not in PROSE_FIELDS:
        return None

    if language == "en":
        # Already English — no translation needed, return as-is
        return {
            "original_text":           text,
            "normalised_form":         text,
            "allowed_variants":        [],
            "processing_method":       ProcessingMethod.NMT,
            "confidence":              1.0,
            "review_required":         False,
            "review_reason":           None,
            "should_use_in_screening": False,  # prose is for analyst readability only
        }

    if len(text.strip()) < 10:
        return None

    endpoint = os.environ.get("AZURE_TRANSLATOR_ENDPOINT", "")
    key      = os.environ.get("AZURE_TRANSLATOR_KEY", "")
    region   = os.environ.get("AZURE_TRANSLATOR_REGION", "")
    target   = os.environ.get("AZURE_TRANSLATOR_TARGET_LANGUAGE", "en")

    if not endpoint or not key:
        return None  # credentials not configured — fall through to review

    try:
        translated = _call_azure_translator(text, target, language, endpoint, key, region)
        if not translated:
            return None

        return {
            "original_text":           text,
            "normalised_form":         translated,
            "allowed_variants":        [],
            "processing_method":       ProcessingMethod.NMT,
            "confidence":              STRATEGY_CONFIDENCE[ProcessingMethod.NMT],
            "review_required":         False,
            "review_reason":           None,
            "should_use_in_screening": False,  # prose fields are for readability, not screening
        }

    except Exception:
        return None  # any Azure error → fall through to Strategy I


def _call_azure_translator(
    text: str,
    target_language: str,
    source_language: str,
    endpoint: str,
    key: str,
    region: str,
) -> str | None:
    """
    Make the Azure Translator API call.

    Uses the azure-ai-translation-text SDK.
    Returns the translated string or None on failure.

    The endpoint is a private endpoint — NMT-only mode is enforced by
    infrastructure, not by this code. Do not add any LLM-related parameters.

    SDK usage:
        from azure.ai.translation.text import TextTranslationClient
        from azure.core.credentials import AzureKeyCredential

        client = TextTranslationClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key),
            region=region,
        )
        response = client.translate(
            body=[{"text": text}],
            to_language=[target_language],
            from_language=source_language if source_language else None,
        )
        return response[0].translations[0].text
    """
    from azure.ai.translation.text import TextTranslationClient
    from azure.core.credentials import AzureKeyCredential

    client = TextTranslationClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key),
        region=region if region else None,
    )
    response = client.translate(
        body=[{"text": text}],
        to_language=[target_language],
        from_language=source_language if source_language else None,
    )
    if response and response[0].translations:
        return response[0].translations[0].text
    return None
```

---

## Wire into the router

In `app/pipeline/normalisation/router.py`, replace `_try_strategy_h()` stub:

```python
def _try_strategy_h(text: str, field_type: str, language: str) -> dict | None:
    """Strategy H — Azure NMT for prose fields only."""
    try:
        from app.pipeline.normalisation.nmt_translator import apply_nmt
        return apply_nmt(text, field_type, language)
    except Exception:
        return None
```

---

## `requirements.txt` addition

```
azure-ai-translation-text>=1.0.0
```

---

## Tests — `tests/test_strategy_h_nmt.py`

The Azure API call is monkeypatched at the `_call_azure_translator` function level.
Business logic (field type gating, credential check, graceful fallback) is NOT mocked.

```python
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
```

---

## Acceptance criteria

- `apply_nmt("محمد", "person_name", "ar")` returns `None` — name fields never translated
- `apply_nmt("TK1234567", "passport_no", "en")` returns `None` — identifiers never translated
- `apply_nmt("text", "nature_of_business", "en")` returns result with `processing_method == "NMT"` and `should_use_in_screening == False`
- With no Azure credentials set, `apply_nmt()` returns `None` — never raises
- With mocked Azure call, prose field returns translated text with `confidence == 0.80`
- Azure failure returns `None`, not an exception
- All tests in `tests/test_strategy_h_nmt.py` pass
- `azure-ai-translation-text` added to `requirements.txt`
- No imports from `src/` at runtime
