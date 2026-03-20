from config.rules import PRESERVE_FIELDS


def apply_rules(field_type: str, text: str) -> dict | None:
    """
    Apply deterministic rules.

    Returns a completed result dict for PRESERVE fields.
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
    return None
