from config.rules import TREATMENT_MAP

# Multilingual descriptor phrases that signal a composite alias.
# A composite alias contains both a name token and a natural-language
# descriptor (e.g. "nicknamed", "also known as") that must be *translated*
# rather than transliterated. Text matching is case-insensitive.
_COMPOSITE_PHRASES = [
    # English (already-Latin aliases)
    "also known as", "aka", "nicknamed", "known as", "alias",
    # Russian / Ukrainian
    "по прозвищу", "известный как", "известная как", "также известен как",
    # Chinese
    "又名", "亦名", "别名", "別名",
    # Greek
    "γνωστός ως", "γνωστή ως", "επίσης γνωστός", "επίσης γνωστή",
    # Arabic
    "المعروف بـ", "الملقب بـ", "المعروفة بـ",
    # Japanese
    "別名", "またの名",
]


def get_treatment(field_type: str) -> str:
    """Return the treatment type for a given field type."""
    return TREATMENT_MAP.get(field_type, "PRESERVE")


def is_composite_alias(text: str) -> bool:
    """Return True if the alias text contains a descriptor phrase that
    requires translation rather than pure transliteration.

    Examples that return True:
        "по прозвищу САША"    (Russian: nicknamed Sasha)
        "又名 王小强"           (Chinese: also known as Wang Xiaoqiang)
        "γνωστός ως ΝΙΚΟΣ"   (Greek: known as Nikos)
        "ALSO KNOWN AS JIMMY" (already-Latin descriptor)
    """
    t = text.lower()
    return any(phrase in t for phrase in _COMPOSITE_PHRASES)
