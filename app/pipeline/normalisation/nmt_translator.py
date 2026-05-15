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
            "should_use_in_screening": False,
        }

    if len(text.strip()) < 4:
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
            "normalised_form":         translated.upper(),
            "allowed_variants":        [],
            "processing_method":       ProcessingMethod.NMT,
            "confidence":              STRATEGY_CONFIDENCE[ProcessingMethod.NMT],
            "review_required":         False,
            "review_reason":           None,
            "should_use_in_screening": False,
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
    infrastructure, not by this code.
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
