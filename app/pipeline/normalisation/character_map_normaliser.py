"""
Strategy G — Character Map Normaliser.

Entry point: apply_character_map(text, language, field_type) -> dict | None

Existing handlers (de, fr, es, it, en) are imported from
src/pipeline/transliteration_engine.py — do not duplicate them here.

New handlers (tr, nl, no, sv, da, pl, pt) are implemented in this file.
"""

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[4] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import re
import unicodedata

from pipeline.transliteration_engine import (
    _normalise_german,
    _normalise_french,
    _normalise_spanish,
    _normalise_italian,
    _apply_char_map,
)

from app.data.normalisation.character_maps import (
    LANGUAGE_CHAR_MAPS,
    TURKISH_CHAR_MAP,
    DUTCH_CHAR_MAP,
    SCANDINAVIAN_CHAR_MAP,
    POLISH_CHAR_MAP,
    PORTUGUESE_CHAR_MAP,
)


def apply_character_map(text: str, language: str, field_type: str) -> dict | None:
    """
    Strategy G entry point called by the normalisation router.

    Returns None if the language has no character map — signals the router
    to continue to Strategy H. Returns None for non-Latin scripts.
    Never raises.
    """
    handlers = {
        "de": _normalise_german,
        "fr": _normalise_french,
        "es": _normalise_spanish,
        "it": _normalise_italian,
        "tr": _normalise_turkish,
        "nl": _normalise_dutch,
        "no": _normalise_scandinavian,
        "sv": _normalise_scandinavian,
        "da": _normalise_scandinavian,
        "pl": _normalise_polish,
        "pt": _normalise_portuguese,
    }
    # de/fr/es/it/en handlers are imported from transliteration_engine which
    # stamps processing_method='TRANSLITERATE'.  Override here so callers
    # always see CHARACTER_MAP when Strategy G is responsible.
    _TRANSLITERATE_METHOD_LANGS = {"de", "fr", "es", "it"}

    handler = handlers.get(language)
    if not handler:
        return None
    # T2-G-2: if none of the input characters is a key in the language's map,
    # G has nothing to do — return None so the router tries D or F instead.
    # Check against map membership, not output equality, to avoid false negatives
    # on already-uppercased inputs like "MUELLER".
    if language in LANGUAGE_CHAR_MAPS and not any(c in LANGUAGE_CHAR_MAPS[language] for c in text):
        return None
    try:
        result = handler(text, field_type)
        if result and language in _TRANSLITERATE_METHOD_LANGS:
            result["processing_method"] = "CHARACTER_MAP"
        return result
    except Exception:
        return None


def _build_result(original: str, normalised: str,
                  variants: list[str] | None = None) -> dict:
    return {
        "original_text":           original,
        "normalised_form":         normalised,
        "allowed_variants":        variants or [],
        "processing_method":       "CHARACTER_MAP",
        "confidence":              0.95,
        "review_required":         False,
        "review_reason":           None,
        "should_use_in_screening": True,
    }


# ── Five new handlers ──────────────────────────────────────────────────────────

def _normalise_turkish(text: str, field_type: str) -> dict:
    normalised = _apply_char_map(text, TURKISH_CHAR_MAP).upper()
    variants: set[str] = set()
    if "-" in normalised:
        variants.add(normalised.replace("-", " "))
    result = _build_result(text, normalised)
    result["allowed_variants"] = sorted(v for v in variants if v != normalised)
    return result


def _normalise_dutch(text: str, field_type: str) -> dict:
    mapped = _apply_char_map(text, DUTCH_CHAR_MAP)
    normalised = mapped.upper()
    variants: set[str] = set()
    if "-" in normalised:
        variants.add(normalised.replace("-", " "))
    for particle in ("VAN DE ", "VAN DEN ", "VAN DER ", "VAN "):
        if f" {particle}" in normalised or normalised.startswith(particle):
            variants.add(normalised.replace(particle, particle.title()))
    result = _build_result(text, normalised)
    result["allowed_variants"] = sorted(v for v in variants if v != normalised)
    return result


def _normalise_scandinavian(text: str, field_type: str) -> dict:
    normalised = _apply_char_map(text, SCANDINAVIAN_CHAR_MAP).upper()
    variants: set[str] = set()
    if "-" in normalised:
        variants.add(normalised.replace("-", " "))
    result = _build_result(text, normalised)
    result["allowed_variants"] = sorted(v for v in variants if v != normalised)
    return result


def _normalise_polish(text: str, field_type: str) -> dict:
    normalised = _apply_char_map(text, POLISH_CHAR_MAP).upper()
    variants: set[str] = set()
    if "-" in normalised:
        variants.add(normalised.replace("-", " "))
    result = _build_result(text, normalised)
    result["allowed_variants"] = sorted(v for v in variants if v != normalised)
    return result


def _normalise_portuguese(text: str, field_type: str) -> dict:
    normalised = _apply_char_map(text, PORTUGUESE_CHAR_MAP).upper()
    variants: set[str] = set()
    if "-" in normalised:
        variants.add(normalised.replace("-", " "))
    for particle in ("DOS ", "DAS ", "DA ", "DO ", "DE "):
        if f" {particle}" in normalised or normalised.startswith(particle):
            variants.add(normalised.replace(particle, "").strip())
    result = _build_result(text, normalised)
    result["allowed_variants"] = sorted(v for v in variants if v != normalised)
    return result
