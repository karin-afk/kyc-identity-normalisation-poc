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

CONFIDENCE_THRESHOLD = 0.75

# Conflict resolution priority
LAYER_PRIORITY = ["RULE", "TRANSLITERATE", "LLM"]

# Maps field_type → treatment label used by field_classifier
TREATMENT_MAP: dict[str, str] = {
    "passport_no": "PRESERVE",
    "id_no": "PRESERVE",
    "email": "PRESERVE",
    "person_name": "TRANSLITERATE",
    "alias": "TRANSLITERATE",
    "address": "TRANSLATE_NORMALISE",
    "company_name": "TRANSLATE_NORMALISE",
}
