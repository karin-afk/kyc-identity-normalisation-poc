"""Analyst alias handler for KYC identity normalisation.

Pipeline layer: Layer 3 (specialist routing) — invoked when a field has
treatment TRANSLATE_ANALYST, i.e. an alias field that contains a natural-
language descriptor phrase such as "also known as", "по прозвищу", 民间称为, etc.

The handler splits the combined text into a *primary name* and an *alias name*,
normalises each independently using the appropriate transliteration or LLM path,
and recombines them as  "{PRIMARY} ALSO KNOWN AS {ALIAS}".
"""

import re
from typing import Callable, Optional


# ---------------------------------------------------------------------------
# Trigger patterns — multilingual alias-phrase detection
# ---------------------------------------------------------------------------

ALIAS_TRIGGERS: dict[str, list[str]] = {
    "en": [
        r"\balso\s+known\s+as\b", r"\baka\b", r"\balias\b",
        r"\bknown\s+as\b", r"\bnicknamed?\b", r"\bcalled\b",
        r"\bformerly\s+known\s+as\b",
    ],
    "ar": [
        r"المعروف\s+ب", r"المعروف\s+بـ", r"الملقب\s+ب",
        r"يُعرف\s+بـ?", r"المُلقَّب",
    ],
    "ru": [
        r"по\s+прозвищу", r"известный\s+как", r"также\s+известен\s+как",
        r"кличка", r"псевдоним",
    ],
    "el": [
        r"γνωστός\s+ως", r"γνωστή\s+ως", r"αλλιώς\s+γνωστός",
        r"επίσης\s+γνωστός",
    ],
    "zh": [r"又名", r"又称", r"亦称", r"别名", r"化名"],
    "ja": [r"別名", r"通称", r"またの名"],
    "de": [r"\bgenannt\b", r"\bbekannt\s+als\b", r"\baliasname\b"],
    "fr": [r"\bdit\b", r"\bdite\b", r"\bégalement\s+connu\s+sous", r"\bconnu\s+sous\b"],
    "es": [r"\bconocido\s+como\b", r"\bconocida\s+como\b", r"\btambién\s+conocido\b"],
    "it": [r"\bdetto\b", r"\bdetta\b", r"\bconosciuto\s+come\b", r"\banche\s+detto\b"],
    "ko": [r"일명", r"별명", r"별칭", r"이라고도\s+불림"],
}


def _get_patterns(language: str) -> list[str]:
    """Return trigger patterns for the given language, always including English."""
    patterns = list(ALIAS_TRIGGERS.get(language, []))
    if language != "en":
        patterns = patterns + ALIAS_TRIGGERS["en"]
    return patterns


def extract_name_and_alias(text: str, language: str) -> dict:
    """Split an alias phrase into primary name and alias name.

    Algorithm:
    1. Try each trigger pattern for the given language (plus English patterns).
    2. On first match: split on the trigger.
       - ``primary_text`` = text before the trigger (stripped)
       - ``alias_text`` = text after the trigger (stripped)
    3. If no trigger found: treat the entire text as the primary name.

    Args:
        text: Combined alias field text (e.g. "Александр по прозвищу Саша").
        language: ISO 639-1 language code of the source document.

    Returns:
        A dict with keys:
        - ``primary_text``: str — text before the trigger phrase
        - ``alias_text``: str | None — text after the trigger phrase, or None
        - ``trigger_found``: str | None — the matched regex pattern
        - ``split_method``: ``"trigger"`` | ``"no_split"``
    """
    for pattern in _get_patterns(language):
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            primary_text = text[: m.start()].strip()
            alias_text = text[m.end():].strip()
            return {
                "primary_text": primary_text or text.strip(),
                "alias_text": alias_text if alias_text else None,
                "trigger_found": pattern,
                "split_method": "trigger",
            }
    return {
        "primary_text": text.strip(),
        "alias_text": None,
        "trigger_found": None,
        "split_method": "no_split",
    }


def _normalise_part(
    part_text: str,
    language: str,
    row: dict,
    transliterate_fn: Callable,
    llm_fn: Optional[Callable],
) -> str:
    """Normalise a single name part using the appropriate strategy.

    Routing logic mirrors the main pipeline:
    - Arabic or LLM-required text: use ``llm_fn`` if available.
    - All other scripts: use ``transliterate_fn``.

    Args:
        part_text: The text fragment to normalise.
        language: ISO 639-1 language code.
        row: Original field row dict (used as template for transliterate_fn).
        transliterate_fn: The transliteration function.
        llm_fn: The LLM enrichment function (may be None).

    Returns:
        Uppercase normalised string.
    """
    part_row = {**row, "original_text": part_text}
    if language == "ar" and llm_fn is not None:
        result = llm_fn(part_text, part_row)
    else:
        result = transliterate_fn(part_text, part_row)
    return result.get("normalised_form", part_text.upper())


def process_analyst_field(
    text: str,
    language: str,
    transliterate_fn: Callable,
    llm_fn: Optional[Callable],
    row: dict,
) -> dict:
    """Process a TRANSLATE_ANALYST field end-to-end.

    Steps:
    1. Extract primary name and alias text via ``extract_name_and_alias()``.
    2. Normalise the primary text.
    3. If an alias was found, normalise it and combine as
       "{PRIMARY} ALSO KNOWN AS {ALIAS}".
    4. Return a full result dict.

    The result always has ``review_required=True`` because analyst-field alias
    extraction is heuristic and may split incorrectly near era boundaries.

    Args:
        text: Raw field text.
        language: ISO 639-1 language code.
        transliterate_fn: The transliteration engine function.
        llm_fn: The LLM enrichment function (may be None).
        row: Original field row dict.

    Returns:
        A full pipeline result dict.
    """
    split = extract_name_and_alias(text, language)
    primary_norm = _normalise_part(split["primary_text"], language, row, transliterate_fn, llm_fn)

    if split["alias_text"]:
        alias_norm = _normalise_part(split["alias_text"], language, row, transliterate_fn, llm_fn)
        combined = f"{primary_norm} ALSO KNOWN AS {alias_norm}"
        allowed_variants = [primary_norm, alias_norm]
        method = "TRANSLITERATE+ANALYST" if language != "ar" else "LLM+ANALYST"
    else:
        combined = primary_norm
        allowed_variants = [primary_norm]
        method = "TRANSLITERATE+ANALYST"

    return {
        "original_text": text,
        "latin_transliteration": combined,
        "allowed_variants": allowed_variants,
        "analyst_english_rendering": combined,
        "normalised_form": combined,
        "processing_method": method,
        "confidence": 0.75,
        "review_required": True,
        "review_reason": "Analyst field: alias phrase extracted and normalised",
        "should_use_in_screening": True,
    }
