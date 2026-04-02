from config.rules import NORMALISE_NUMERIC_FIELDS, PRESERVE_FIELDS
from utils.calendar_utils import normalise_date_field


def apply_rules(field_type: str, text: str) -> dict | None:
    """
    Apply deterministic rules.

    Returns a completed result dict for PRESERVE and NORMALISE_NUMERIC fields.
    Returns None to signal downstream layers should process the field.
    """
    if field_type in PRESERVE_FIELDS:
        return {
            "original_text": text,
            "latin_transliteration": None,
            "allowed_variants": [],
            "analyst_english_rendering": text,
            "normalised_form": text,
            "processing_method": "RULE",
            "confidence": 1.0,
            "review_required": False,
            "review_reason": None,
            "should_use_in_screening": True,
        }

    if field_type in NORMALISE_NUMERIC_FIELDS:
        result = normalise_date_field(text)
        return {
            "original_text": text,
            "latin_transliteration": None,
            "allowed_variants": [],
            "analyst_english_rendering": result["normalised"],
            "normalised_form": result["normalised"],
            "processing_method": "RULE",
            "confidence": 1.0,
            "review_required": result["review_required"],
            "review_reason": result["review_reason"],
            "should_use_in_screening": True,
            "original_calendar": result["original_calendar"],
        }

    return None
