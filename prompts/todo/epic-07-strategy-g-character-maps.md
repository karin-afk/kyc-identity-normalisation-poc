# Epic 07 — Strategy G: Character Mapping Tables

## Save to: `prompts/todo/epic-07-strategy-g-character-maps.md`

---

## Context and current state

Strategy G handles Latin-script languages. It applies fixed character substitution
tables to convert special characters to ASCII for KYC screening output.

The router calls Strategy G after Strategy F returns `None` for Latin-script languages.

**What already exists — do not recreate:**
- `src/config/language_normalisation_tables.py` — contains `GERMAN_UMLAUT_EXPANSIONS`,
  `GERMAN_UMLAUT_DROPS`, `FRENCH_ACCENT_STRIP`, `SPANISH_ACCENT_STRIP`,
  `SPANISH_N_TILDE_VARIANTS`, `ITALIAN_ACCENT_STRIP`
- `src/pipeline/transliteration_engine.py` — contains `_normalise_german()`,
  `_normalise_french()`, `_normalise_spanish()`, `_normalise_italian()`,
  `_normalise_english()` and the helper `_apply_char_map()`
- `app/data/normalisation/character_maps.py` — exists but may be incomplete
- `app/pipeline/normalisation/character_map_normaliser.py` — exists but may be a stub

**What does NOT exist and must be built:**
- Turkish, Dutch, Scandinavian, Polish, Portuguese character maps
- Handler functions for those five new language groups

---

## What you need to provide before running this epic

One Python file with five new character mapping dicts.

### `app/data/normalisation/character_maps_new.py`

```python
"""
New character mapping tables for Epic 07.
Copilot merges these into app/data/normalisation/character_maps.py.
"""

TURKISH_CHAR_MAP: dict[str, str] = {
    "İ": "I",   # U+0130 uppercase dotted I
    "ı": "i",   # U+0131 lowercase dotless I
    "Ğ": "G", "ğ": "g",
    "Ş": "S", "ş": "s",
    "Ç": "C", "ç": "c",
    "Ö": "O", "ö": "o",
    "Ü": "U", "ü": "u",
}

DUTCH_CHAR_MAP: dict[str, str] = {
    "Ĳ": "IJ",  # U+0132
    "ĳ": "ij",  # U+0133
}

SCANDINAVIAN_CHAR_MAP: dict[str, str] = {
    "Æ": "AE", "æ": "ae",
    "Ø": "O",  "ø": "o",
    "Å": "A",  "å": "a",
    "Ä": "A",  "ä": "a",
    "Ö": "O",  "ö": "o",
}

POLISH_CHAR_MAP: dict[str, str] = {
    "Ą": "A", "ą": "a",
    "Ę": "E", "ę": "e",
    "Ś": "S", "ś": "s",
    "Ź": "Z", "ź": "z",
    "Ż": "Z", "ż": "z",
    "Ń": "N", "ń": "n",
    "Ó": "O", "ó": "o",
    "Ć": "C", "ć": "c",
    "Ł": "L", "ł": "l",
}

PORTUGUESE_CHAR_MAP: dict[str, str] = {
    "Ã": "A", "ã": "a",
    "Õ": "O", "õ": "o",
    "Â": "A", "â": "a",
    "Ê": "E", "ê": "e",
    "Ô": "O", "ô": "o",
    "Á": "A", "á": "a",
    "É": "E", "é": "e",
    "Í": "I", "í": "i",
    "Ó": "O", "ó": "o",
    "Ú": "U", "ú": "u",
    "Ç": "C", "ç": "c",
}
```

Save to: `app/data/normalisation/character_maps_new.py`

---

## Path conventions for this epic

- Character map Python files: `app/data/normalisation/`
- Normaliser module: `app/pipeline/normalisation/character_map_normaliser.py`
- JSON data files load from `data/lookup_tables/` (project root) — not `app/data/`
- Test file: `tests/test_strategy_g_character_maps.py`
- No imports from `src/` at runtime in any `app/` module

---

## Step 1 — Complete `app/data/normalisation/character_maps.py`

Check the existing file. It must contain all of the following. Add anything missing.
Do not import from `src/` — copy the dict literals directly.

```python
"""All character mapping tables for Strategy G."""

from app.data.normalisation.character_maps_new import (
    TURKISH_CHAR_MAP,
    DUTCH_CHAR_MAP,
    SCANDINAVIAN_CHAR_MAP,
    POLISH_CHAR_MAP,
    PORTUGUESE_CHAR_MAP,
)

# Carried forward from src/config/language_normalisation_tables.py
GERMAN_UMLAUT_EXPANSIONS: dict[str, str] = {
    "Ä": "AE", "ä": "ae",
    "Ö": "OE", "ö": "oe",
    "Ü": "UE", "ü": "ue",
    "ß": "SS",
}
GERMAN_UMLAUT_DROPS: dict[str, str] = {
    "Ä": "A", "ä": "a",
    "Ö": "O", "ö": "o",
    "Ü": "U", "ü": "u",
    "ß": "S",
}
FRENCH_ACCENT_STRIP: dict[str, str] = {
    "À": "A", "Â": "A", "à": "a", "â": "a",
    "É": "E", "È": "E", "Ê": "E", "Ë": "E",
    "é": "e", "è": "e", "ê": "e", "ë": "e",
    "Î": "I", "Ï": "I", "î": "i", "ï": "i",
    "Ô": "O", "ô": "o",
    "Ù": "U", "Û": "U", "Ü": "U",
    "ù": "u", "û": "u", "ü": "u",
    "Ç": "C", "ç": "c",
    "Œ": "OE", "œ": "oe",
    "Æ": "AE", "æ": "ae",
    "\u2019": "",
}
SPANISH_ACCENT_STRIP: dict[str, str] = {
    "Á": "A", "á": "a",
    "É": "E", "é": "e",
    "Í": "I", "í": "i",
    "Ó": "O", "ó": "o",
    "Ú": "U", "ú": "u",
    "Ü": "U", "ü": "u",
    "Ñ": "N", "ñ": "n",
}
ITALIAN_ACCENT_STRIP: dict[str, str] = {
    "À": "A", "à": "a",
    "È": "E", "è": "e",
    "É": "E", "é": "e",
    "Ì": "I", "ì": "i",
    "Ò": "O", "ò": "o",
    "Ù": "U", "ù": "u",
}

LANGUAGE_CHAR_MAPS: dict[str, dict[str, str]] = {
    "de": GERMAN_UMLAUT_EXPANSIONS,
    "fr": FRENCH_ACCENT_STRIP,
    "es": SPANISH_ACCENT_STRIP,
    "it": ITALIAN_ACCENT_STRIP,
    "tr": TURKISH_CHAR_MAP,
    "nl": DUTCH_CHAR_MAP,
    "no": SCANDINAVIAN_CHAR_MAP,
    "sv": SCANDINAVIAN_CHAR_MAP,
    "da": SCANDINAVIAN_CHAR_MAP,
    "pl": POLISH_CHAR_MAP,
    "pt": PORTUGUESE_CHAR_MAP,
}

LANGUAGE_VARIANT_MAPS: dict[str, dict[str, str]] = {
    "de": GERMAN_UMLAUT_DROPS,
}
```

---

## Step 2 — Implement `app/pipeline/normalisation/character_map_normaliser.py`

Replace the existing file content entirely.

```python
"""
Strategy G — Character Map Normaliser.

Entry point: apply_character_map(text, language, field_type) -> dict | None

Returns None if language has no character map, allowing the router to fall
through to Strategy H. No imports from src/ at runtime.
"""

import unicodedata
import re

from app.data.normalisation.character_maps import (
    LANGUAGE_CHAR_MAPS, LANGUAGE_VARIANT_MAPS,
    GERMAN_UMLAUT_EXPANSIONS, GERMAN_UMLAUT_DROPS,
    FRENCH_ACCENT_STRIP, SPANISH_ACCENT_STRIP, ITALIAN_ACCENT_STRIP,
    DUTCH_CHAR_MAP, SCANDINAVIAN_CHAR_MAP, POLISH_CHAR_MAP,
    PORTUGUESE_CHAR_MAP, TURKISH_CHAR_MAP,
)
from app.pipeline.normalisation.field_types import ProcessingMethod, STRATEGY_CONFIDENCE


def apply_character_map(text: str, language: str, field_type: str) -> dict | None:
    """Strategy G entry point. Returns None if language has no map."""
    if language not in LANGUAGE_CHAR_MAPS and language != "en":
        return None

    handlers = {
        "de": _normalise_german,
        "fr": _normalise_french,
        "es": _normalise_spanish,
        "it": _normalise_italian,
        "en": _normalise_english,
        "tr": _normalise_turkish,
        "nl": _normalise_dutch,
        "no": _normalise_scandinavian,
        "sv": _normalise_scandinavian,
        "da": _normalise_scandinavian,
        "pl": _normalise_polish,
        "pt": _normalise_portuguese,
    }
    handler = handlers.get(language)
    if handler:
        return handler(text, field_type)

    char_map = LANGUAGE_CHAR_MAPS.get(language, {})
    return _build_result(text, _apply_char_map(text, char_map).upper())


def _apply_char_map(text: str, char_map: dict[str, str]) -> str:
    return "".join(char_map.get(c, c) for c in text)


def _build_result(original: str, normalised: str,
                  variants: list[str] | None = None) -> dict:
    return {
        "original_text":           original,
        "normalised_form":         normalised,
        "allowed_variants":        variants or [],
        "processing_method":       ProcessingMethod.CHARACTER_MAP,
        "confidence":              STRATEGY_CONFIDENCE[ProcessingMethod.CHARACTER_MAP],
        "review_required":         False,
        "review_reason":           None,
        "should_use_in_screening": True,
    }


# ── Existing handlers — ported from src/pipeline/transliteration_engine.py ────
# Logic is identical. Only imports are updated. Do not import from src/.

def _normalise_german(text: str, field_type: str) -> dict:
    expanded = _apply_char_map(text, GERMAN_UMLAUT_EXPANSIONS).upper()
    dropped  = _apply_char_map(text, GERMAN_UMLAUT_DROPS).upper()
    variants: set[str] = set()
    if dropped != expanded:
        variants.add(dropped)
    if "-" in expanded:
        variants.add(expanded.replace("-", " "))
    if "-" in dropped:
        variants.add(dropped.replace("-", " "))
    for particle in ("VON ", "VAN ", "ZU "):
        if particle in expanded:
            variants.add(expanded.replace(particle, particle.capitalize()))
    result = _build_result(text, expanded)
    result["allowed_variants"] = sorted(v for v in variants if v != expanded)
    return result


def _normalise_french(text: str, field_type: str) -> dict:
    stripped = _apply_char_map(text, FRENCH_ACCENT_STRIP).upper()
    variants: set[str] = set()
    if "'" in stripped or "\u2019" in stripped:
        variants.add(stripped.replace("'", "").replace("\u2019", ""))
        variants.add(stripped.replace("'", " ").replace("\u2019", " ").strip())
    if "-" in stripped:
        variants.add(stripped.replace("-", " "))
    for particle in ("DE LA ", "DU ", "DES ", "DE "):
        if f" {particle}" in stripped or stripped.startswith(particle):
            variants.add(stripped.replace(particle, "").strip())
    result = _build_result(text, stripped)
    result["allowed_variants"] = sorted(v for v in variants if v != stripped)
    return result


def _normalise_spanish(text: str, field_type: str) -> dict:
    stripped = _apply_char_map(text, SPANISH_ACCENT_STRIP).upper()
    variants: set[str] = set()
    if "Ñ" in text.upper():
        ny_variant = "".join(
            "NY" if orig in "ñÑ" else ch
            for orig, ch in zip(text.upper(), stripped)
        )
        if ny_variant != stripped:
            variants.add(ny_variant)
    if "-" in stripped:
        variants.add(stripped.replace("-", " "))
    for particle in ("DEL ", "DE LA ", "DE LOS ", "DE LAS ", "DE "):
        if f" {particle}" in stripped or stripped.startswith(particle):
            variants.add(stripped.replace(particle, "").strip())
    result = _build_result(text, stripped)
    result["allowed_variants"] = sorted(v for v in variants if v != stripped)
    return result


def _normalise_italian(text: str, field_type: str) -> dict:
    stripped = _apply_char_map(text, ITALIAN_ACCENT_STRIP).upper()
    variants: set[str] = set()
    apos_re = re.compile(r"\b([A-Z]+)'([A-Z])")
    if apos_re.search(stripped):
        variants.add(apos_re.sub(r"\1 \2", stripped))
        variants.add(apos_re.sub(r"\1\2", stripped))
    if "-" in stripped:
        variants.add(stripped.replace("-", " "))
    result = _build_result(text, stripped)
    result["allowed_variants"] = sorted(v for v in variants if v != stripped)
    return result


def _normalise_english(text: str, field_type: str) -> dict:
    normalised = unicodedata.normalize("NFKC", text).upper()
    variants: set[str] = set()
    if "'" in normalised:
        variants.add(normalised.replace("'", ""))
        variants.add(normalised.replace("'", " ").strip())
    if "-" in normalised:
        variants.add(normalised.replace("-", " "))
        variants.add(normalised.replace("-", ""))
    for mac_re, alt in [(re.compile(r"\bMAC([A-Z])"), "MC"),
                        (re.compile(r"\bMC([A-Z])"),  "MAC")]:
        swapped = mac_re.sub(lambda m: alt + m.group(1), normalised)
        if swapped != normalised:
            variants.add(swapped)
    if " ST " in normalised or normalised.startswith("ST "):
        variants.add(normalised.replace("ST ", "SAINT ", 1))
    if "SAINT " in normalised:
        variants.add(normalised.replace("SAINT ", "ST ", 1))
    result = _build_result(text, normalised)
    result["allowed_variants"] = sorted(v for v in variants if v != normalised)
    return result


# ── New handlers ───────────────────────────────────────────────────────────────

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
```

---

## Step 3 — Wire into the router

In `app/pipeline/normalisation/router.py`, replace the `_try_strategy_g()` stub:

```python
def _try_strategy_g(text: str, field_type: str, language: str) -> dict | None:
    try:
        from app.pipeline.normalisation.character_map_normaliser import apply_character_map
        return apply_character_map(text, language, field_type)
    except Exception:
        return None
```

---

## Tests — `tests/test_strategy_g_character_maps.py`

No mocks. Call `apply_character_map()` or `route_field()` with real inputs.

```python
from app.pipeline.normalisation.character_map_normaliser import apply_character_map
from app.pipeline.normalisation.router import route_field

# Existing
def test_german_umlaut_expansion():
    assert apply_character_map("Müller", "de", "person_name")["normalised_form"] == "MUELLER"

def test_german_umlaut_drop_variant():
    assert "MULLER" in apply_character_map("Müller", "de", "person_name")["allowed_variants"]

def test_german_sz():
    assert apply_character_map("Straße", "de", "person_name")["normalised_form"] == "STRASSE"

def test_french_accent():
    assert apply_character_map("Léa", "fr", "person_name")["normalised_form"] == "LEA"

def test_spanish_n_tilde_primary():
    assert apply_character_map("Muñoz", "es", "person_name")["normalised_form"] == "MUNOZ"

def test_spanish_n_tilde_ny_variant():
    assert "MUNYOZ" in apply_character_map("Muñoz", "es", "person_name")["allowed_variants"]

def test_english_obrien_variant():
    r = apply_character_map("O'Brien", "en", "person_name")
    assert "OBRIEN" in r["allowed_variants"] or "O BRIEN" in r["allowed_variants"]

# New
def test_turkish_dotted_i():
    assert apply_character_map("İstanbul", "tr", "person_name")["normalised_form"] == "ISTANBUL"

def test_turkish_dotless_i():
    assert apply_character_map("Işık", "tr", "person_name")["normalised_form"] == "ISIK"

def test_turkish_soft_g():
    assert apply_character_map("Ağaoğlu", "tr", "person_name")["normalised_form"] == "AGAOGLU"

def test_dutch_ij_ligature():
    r = apply_character_map("Ĳsselmeer", "nl", "person_name")
    assert r["normalised_form"] == "IJSSELMEER"

def test_scandinavian_ae():
    assert apply_character_map("Ærø", "da", "person_name")["normalised_form"] == "AERO"

def test_scandinavian_o_stroke():
    assert apply_character_map("Bjørn", "no", "person_name")["normalised_form"] == "BJORN"

def test_scandinavian_a_ring():
    assert apply_character_map("Åberg", "sv", "person_name")["normalised_form"] == "ABERG"

def test_polish_l_stroke():
    assert apply_character_map("Łódź", "pl", "person_name")["normalised_form"] == "LODZ"

def test_polish_nasal_a():
    assert apply_character_map("Wąsik", "pl", "person_name")["normalised_form"] == "WASIK"

def test_portuguese_tilde():
    assert apply_character_map("João", "pt", "person_name")["normalised_form"] == "JOAO"

def test_portuguese_cedilla():
    assert apply_character_map("Gonçalves", "pt", "person_name")["normalised_form"] == "GONCALVES"

# Routing
def test_german_routes_to_character_map():
    r = route_field({"original_text": "Müller", "field_type": "person_name", "language": "de"})
    assert r["processing_method"] == "CHARACTER_MAP"
    assert r["normalised_form"] == "MUELLER"

def test_arabic_returns_none_from_strategy_g():
    assert apply_character_map("محمد", "ar", "person_name") is None

def test_japanese_returns_none_from_strategy_g():
    assert apply_character_map("田中", "ja", "person_name") is None
```

---

## Acceptance criteria

- `apply_character_map("Müller", "de", "person_name")` → `MUELLER` with `MULLER` in variants
- `apply_character_map("İstanbul", "tr", "person_name")` → `ISTANBUL`
- `apply_character_map("Łódź", "pl", "person_name")` → `LODZ`
- `apply_character_map("Ærø", "da", "person_name")` → `AERO`
- `apply_character_map("محمد", "ar", "person_name")` → `None`
- `route_field({"original_text": "Müller", "field_type": "person_name", "language": "de"})` → `processing_method == "CHARACTER_MAP"`
- All existing golden dataset regression tests pass unchanged
- All tests in `tests/test_strategy_g_character_maps.py` pass
- No imports from `src/` at runtime in any `app/` module
