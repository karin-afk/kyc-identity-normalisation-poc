"""
LLM layer — used for TRANSLATE_NORMALISE fields (addresses, company names)
and optionally for Arabic transliteration disambiguation.

=== API CONNECTION ===

1. Copy .env.example → .env
2. Set OPENAI_API_KEY=<your key>

To use Azure OpenAI instead of the standard API:
    Set OPENAI_API_KEY=<azure-key>
    Set OPENAI_API_BASE=https://<your-resource>.openai.azure.com/
    Set OPENAI_API_VERSION=2024-02-01
    Then change the client instantiation below to:
        openai.AzureOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            azure_endpoint=os.getenv("OPENAI_API_BASE"),
            api_version=os.getenv("OPENAI_API_VERSION"),
        )

The model is intentionally pinned. Change MODEL below if needed.
"""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4o"  # Pin model version for reproducibility

_PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts"


def _load_prompt(key: str) -> str:
    path = _PROMPTS_DIR / f"prompt_{key}.txt"
    return path.read_text(encoding="utf-8").strip() if path.exists() else ""


def enrich_with_llm(text: str, row: dict) -> dict:
    """
    Call OpenAI to translate/normalise an address or company name field.
    If OPENAI_API_KEY is not set, returns a stub result flagged for review.
    """
    if not OPENAI_API_KEY:
        # ── STUB (no API key) ─────────────────────────────────────────────────────
        return {
            "original_text": text,
            "latin_transliteration": None,
            "allowed_variants": [],
            "analyst_english_rendering": text,
            "normalised_form": text.upper(),
            "processing_method": "LLM",
            "model_version": None,
            "confidence": 0.0,
            "review_required": True,
            "review_reason": "OPENAI_API_KEY not set — LLM stub active. Set key in .env to enable.",
            "should_use_in_screening": False,
        }

    # ── LIVE LLM CALL ────────────────────────────────────────────────────────────
    import openai

    import json as _json

    from pipeline.field_classifier import is_composite_alias

    field_type = row.get("field_type", "")
    is_arabic_name = (
        row.get("language") == "ar"
        and field_type in ("person_name", "alias")
    )
    is_composite = (
        field_type == "alias"
        and not is_arabic_name
        and is_composite_alias(text)
    )

    prompt_key = (
        "person_name_ar" if is_arabic_name
        else "alias" if is_composite
        else "person_name" if field_type in ("person_name", "alias")
        else "address" if field_type == "address"
        else "company"
    )

    template = _load_prompt(prompt_key) or (
        "Translate and normalise this {field_type} to English. "
        "Output only the result, no explanation.\n{original_text}"
    )
    prompt = template.format(
        source_language=row.get("language", ""),
        original_text=text,
        field_type=field_type,
    )

    # Arabic name and composite alias prompts return JSON — structured output
    # guarantees valid JSON even when the model is uncertain.
    extra_kwargs: dict = {}
    if is_arabic_name or is_composite:
        extra_kwargs["response_format"] = {"type": "json_object"}

    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0,
        **extra_kwargs,
    )

    raw = response.choices[0].message.content.strip()

    # Parse JSON response for Arabic names and composite aliases
    allowed_variants: list[str] = []
    if is_arabic_name or is_composite:
        try:
            parsed = _json.loads(raw)
            primary = str(parsed.get("primary", raw)).upper()
            allowed_variants = [
                str(v).upper() for v in parsed.get("variants", []) if v
            ]
            result_text = primary
        except (_json.JSONDecodeError, AttributeError):
            # Fallback: treat raw text as the primary form
            result_text = raw.upper()
    else:
        result_text = raw

    processing_method = "LLM/COMPOSITE" if is_composite else "LLM"

    return {
        "original_text": text,
        "latin_transliteration": result_text,
        "allowed_variants": allowed_variants,
        "analyst_english_rendering": result_text,
        "normalised_form": result_text.upper() if not (is_arabic_name or is_composite) else result_text,
        "processing_method": processing_method,
        "model_version": MODEL,
        "confidence": 0.85,
        "review_required": False,
        "review_reason": None,
        "should_use_in_screening": True,
    }