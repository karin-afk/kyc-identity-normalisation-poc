from config.rules import TREATMENT_MAP


def get_treatment(field_type: str) -> str:
    """Return the treatment type for a given field type."""
    return TREATMENT_MAP.get(field_type, "PRESERVE")
