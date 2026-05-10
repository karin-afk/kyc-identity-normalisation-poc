"""
Strategy F — Transliteration.

Thin wrapper around src/pipeline/transliteration_engine.py.
All transliteration logic lives in the engine — do not duplicate it here.

Entry point: apply_transliteration(text, language, field_type, country)
Called by: app/pipeline/normalisation/router.py _try_strategy_f()
"""

import sys
from pathlib import Path

# Ensure src/ is on sys.path so the existing engine can be imported
_SRC = Path(__file__).resolve().parents[3] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

# Field types that Strategy F handles (name and company transliteration only)
_TRANSLITERATION_FIELDS = {
    "person_name",
    "full_name",
    "given_name",
    "family_name",
    "alias",
    "maiden_name",
    "company_name",
    "trading_name",
}


def apply_transliteration(
    text: str,
    language: str,
    field_type: str,
    country: str = "",
) -> dict | None:
    """
    Strategy F entry point called by the normalisation router.

    Delegates entirely to src/pipeline/transliteration_engine.transliterate().
    No transliteration logic is implemented here.

    Args:
        text:       Original text in source script.
        language:   ISO 639-1 language code.
        field_type: KYC field type string.
        country:    ISO 3166-1 alpha-2 country code. Used by Chinese handler
                    to determine Cantonese variant generation for HK/TW.

    Returns:
        Standard result dict with processing_method="TRANSLITERATE", or
        None if text is empty or field_type is not a transliteration field.
        Never raises — exceptions return None so the router falls through.
    """
    if not text or not text.strip():
        return None

    if field_type not in _TRANSLITERATION_FIELDS:
        return None

    try:
        from pipeline.transliteration_engine import transliterate

        row = {
            "language":   language,
            "field_type": field_type,
            "country":    country,
        }

        result = transliterate(text, row)

        # Normalise processing_method label to what the router expects
        pm = result.get("processing_method", "")
        if pm and pm.upper() in ("TRANSLITERATE", "TRANSLITERATION"):
            result["processing_method"] = "TRANSLITERATE"

        # Ensure keys required by the router are present
        result.setdefault(
            "should_use_in_screening",
            not result.get("review_required", False),
        )
        result.setdefault(
            "confidence",
            0.5 if result.get("review_required") else 0.85,
        )

        return result

    except Exception:
        # Never crash the router — fall through to Strategy G
        return None
