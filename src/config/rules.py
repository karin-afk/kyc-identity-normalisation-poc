PRESERVE_FIELDS = [
    "passport_no",
    "id_no",
    "email",
]

TRANSLITERATE_FIELDS = [
    "person_name",
    "alias",
]

TRANSLATE_FIELDS = [
    "address",
    "company_name",
]

# Date fields that require numeric normalisation (calendar conversion + ISO 8601)
NORMALISE_NUMERIC_FIELDS = [
    "birth_date",
    "date",
]

CONFIDENCE_THRESHOLD = 0.75

# Conflict resolution priority
LAYER_PRIORITY = ["RULE", "TRANSLITERATE", "LLM"]

# Maps field_type → treatment label used by field_classifier.
# Note: alias fields that contain a descriptor phrase (e.g. "also known as",
# "по прозвищу") are dynamically reclassified to TRANSLATE_COMPOSITE by
# field_classifier.is_composite_alias() — they are not listed here because
# the classification depends on the text content, not just the field type.
TREATMENT_MAP: dict[str, str] = {
    "passport_no": "PRESERVE",
    "id_no": "PRESERVE",
    "email": "PRESERVE",
    "person_name": "TRANSLITERATE",
    "alias": "TRANSLITERATE",
    "address": "TRANSLATE_NORMALISE",
    "company_name": "TRANSLATE_NORMALISE",
    "birth_date": "NORMALISE_NUMERIC",
    "date": "NORMALISE_NUMERIC",
}
