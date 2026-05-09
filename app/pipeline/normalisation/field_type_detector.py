"""LLM-based field/language classifier for sentence normalisation."""

from __future__ import annotations

import json

from openai import OpenAI

FIELD_TYPES = [
    "person_name",
    "company_name",
    "address",
    "date_of_birth",
    "nationality",
    "legal_form",
    "status",
    "role",
    "nature_of_business",
    "issuing_authority",
    "unstructured_text",
]

LANGUAGE_CODES = [
    "ar",
    "be",
    "bg",
    "da",
    "de",
    "el",
    "en",
    "es",
    "fa",
    "fr",
    "he",
    "it",
    "ja",
    "ko",
    "nl",
    "no",
    "pl",
    "pt",
    "ru",
    "sv",
    "th",
    "tr",
    "uk",
    "zh",
]

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI()
    return _client


def _coerce_confidence(value: object) -> float:
    try:
        confidence = float(value)
    except (TypeError, ValueError):
        return 0.5
    return max(0.0, min(1.0, confidence))


def detect_field_type(text: str, language: str = "") -> tuple[str, float, str]:
    """Classify pasted text with GPT-4o-mini.

    Returns:
        (field_type, confidence, language_code)

    On any error, returns a safe fallback so processing can continue.
    """
    del language

    try:
        response = _get_client().chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=60,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a KYC data classifier. Given a text snippet, "
                        "return ONLY a JSON object with three fields: "
                        "'field_type' (one of: "
                        + ", ".join(FIELD_TYPES)
                        + "), "
                        "'language_code' (ISO 639-1, one of: "
                        + ", ".join(LANGUAGE_CODES)
                        + "), "
                        "'confidence' (float 0.0-1.0). "
                        "No explanation. No markdown. JSON only."
                    ),
                },
                {"role": "user", "content": (text or "")[:500]},
            ],
        )

        content = response.choices[0].message.content or "{}"
        parsed = json.loads(content)

        field_type = parsed.get("field_type", "unstructured_text")
        detected_language = parsed.get("language_code", "en")
        confidence = _coerce_confidence(parsed.get("confidence", 0.5))

        if field_type not in FIELD_TYPES:
            field_type = "unstructured_text"
        if detected_language not in LANGUAGE_CODES:
            detected_language = "en"

        return field_type, confidence, detected_language
    except Exception:
        return "unstructured_text", 0.5, "en"
