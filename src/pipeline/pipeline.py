from pipeline.rules_engine import apply_rules
from pipeline.transliteration_engine import transliterate
from pipeline.llm_layer import enrich_with_llm


def process_field(row: dict) -> dict:
    field_type = row["field_type"]
    text = row["original_text"]

    # Step 1: Deterministic rules — handles PRESERVE fields
    result = apply_rules(field_type, text)
    if result is not None:
        return result

    # Step 2: Transliteration — names and aliases
    # Arabic names are routed to the LLM because short vowels are not written
    # in standard Arabic text; the consonant-only map produces unusable output.
    if field_type in ("person_name", "alias"):
        if row.get("language") == "ar":
            return enrich_with_llm(text, row)
        return transliterate(text, row)

    # Step 3: LLM — addresses and company names
    if field_type in ("address", "company_name"):
        return enrich_with_llm(text, row)

    # Fallback: preserve unknown field types as-is
    return {
        "original_text": text,
        "normalised_form": text.upper(),
        "processing_method": "RULE",
        "confidence": 0.5,
        "review_required": True,
        "review_reason": f"Unknown field type: {field_type}",
    }
