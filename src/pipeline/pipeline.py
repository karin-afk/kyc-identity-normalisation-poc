from pipeline.rules_engine import apply_rules
from pipeline.transliteration_engine import transliterate, normalise_address_latin, _LATIN_SCRIPT_LANGUAGES
from pipeline.llm_layer import enrich_with_llm
from pipeline.field_classifier import is_composite_alias
from pipeline.analyst_handler import process_analyst_field


def process_field(row: dict) -> dict:
    field_type = row["field_type"]
    text = row["original_text"]
    language = row.get("language", "")

    # Step 1: Deterministic rules — handles PRESERVE and NORMALISE_NUMERIC fields
    result = apply_rules(field_type, text)
    if result is not None:
        return result

    # Step 2: Transliteration — names and aliases
    # Routing exceptions that go to the LLM instead:
    #   a) Arabic names: short vowels are not written in standard Arabic text;
    #      the consonant-only map produces unusable output.
    #   b) Composite aliases: the alias text contains a natural-language
    #      descriptor phrase (e.g. "nicknamed", "also known as", "по прозвищу")
    #      that must be *translated*, not transliterated — routed to ANALYST.
    if field_type in ("person_name", "alias"):
        if language == "ar":
            return enrich_with_llm(text, row)
        if field_type == "alias" and is_composite_alias(text):
            return process_analyst_field(
                text,
                language=language,
                transliterate_fn=transliterate,
                llm_fn=enrich_with_llm,
                row=row,
            )
        return transliterate(text, row)

    # Step 3: Addresses
    # Latin-script languages (en/de/fr/es/it/...) use a fully deterministic
    # character-level normaliser — no LLM call needed.  Only diacritic
    # stripping, punctuation removal, and ASCII folding are applied, which
    # correctly preserves source-language street-type words (rue, via, calle)
    # and the original number/street component order.
    # All other scripts (Arabic, CJK, Hangul, Cyrillic, Greek) require the LLM
    # for semantic translation of place-name components.
    if field_type == "address":
        if language in _LATIN_SCRIPT_LANGUAGES:
            return normalise_address_latin(text, language)
        return enrich_with_llm(text, row)

    # Step 4: LLM — company names
    if field_type == "company_name":
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
