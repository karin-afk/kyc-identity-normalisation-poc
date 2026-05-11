# Epic 07 — Strategy G: Character Map Normaliser

## Implementation Todos

| # | Task | Status |
|---|------|--------|
| 1 | Create git branch `epic-07-strategy-g` | implemented |
| 2 | Populate `app/data/normalisation/character_maps_new.py` — Turkish, Dutch, Scandinavian, Polish, Portuguese tables | — |
| 3 | Populate `app/data/normalisation/character_maps.py` — import from `src/` and `character_maps_new.py`, build `LANGUAGE_CHAR_MAPS` routing dict | — |
| 4 | Implement `app/pipeline/normalisation/character_map_normaliser.py` — entry point `apply_character_map()`, import existing handlers from `src/`, add five new handlers | — |
| 5 | Wire `_try_strategy_g()` in `app/pipeline/normalisation/router.py` — replace `_try_stub` delegation with real call | — |
| 6 | Write `tests/test_strategy_g_character_maps.py` — 26 tests, no mocks, covering existing (de/fr/es/en) + new (tr/nl/da/no/sv/pl/pt) + non-Latin None + router | — |
| 7 | Run `pytest tests/test_strategy_g_character_maps.py` and report outcome | — |
| 8 | Run `run_integration_diagnostic.py` and report outcome | — |

---

## Copilot instruction — Implement Epic 07 Strategy G

### Context

The following files are relevant. Read them before doing anything:

- `src/config/language_normalisation_tables.py` — contains `GERMAN_UMLAUT_EXPANSIONS`, `GERMAN_UMLAUT_DROPS`, `FRENCH_ACCENT_STRIP`, `SPANISH_ACCENT_STRIP`, `SPANISH_N_TILDE_VARIANTS`, `ITALIAN_ACCENT_STRIP`, `KOREAN_SURNAME_VARIANTS`
- `src/pipeline/transliteration_engine.py` — contains `_normalise_german()`, `_normalise_french()`, `_normalise_spanish()`, `_normalise_italian()`, `_normalise_english()`, `_apply_char_map()`. These are fully implemented — do not rewrite them.
- `app/data/normalisation/character_maps.py` — exists but is empty. You will populate it.
- `app/data/normalisation/character_maps_new.py` — exists but is empty. You will populate it.
- `app/pipeline/normalisation/character_map_normaliser.py` — exists but is a stub. You will replace it.
- `app/pipeline/normalisation/router.py` — contains `_try_strategy_g()` stub. You will wire it.

---

### Step 1 — Populate `app/data/normalisation/character_maps_new.py`

Create this file with exactly this content:

```python
"""
New character mapping tables — Turkish, Dutch, Scandinavian, Polish, Portuguese.
These five language groups are not covered by src/config/language_normalisation_tables.py.
Imported by app/data/normalisation/character_maps.py.
Do not import this file directly anywhere else.
"""

TURKISH_CHAR_MAP: dict[str, str] = {
    "İ": "I",   # U+0130 uppercase dotted I — distinct from standard I in Turkish
    "ı": "i",   # U+0131 lowercase dotless I
    "Ğ": "G", "ğ": "g",
    "Ş": "S", "ş": "s",
    "Ç": "C", "ç": "c",
    "Ö": "O", "ö": "o",
    "Ü": "U", "ü": "u",
}

DUTCH_CHAR_MAP: dict[str, str] = {
    "Ĳ": "IJ",  # U+0132 uppercase IJ ligature
    "ĳ": "ij",  # U+0133 lowercase IJ ligature
    # Two-character I+J digraph handled in _normalise_dutch() handler
}

SCANDINAVIAN_CHAR_MAP: dict[str, str] = {
    "Æ": "AE", "æ": "ae",
    "Ø": "O",  "ø": "o",
    "Å": "A",  "å": "a",
    "Ä": "A",  "ä": "a",   # Swedish
    "Ö": "O",  "ö": "o",   # Swedish
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

---

### Step 2 — Populate `app/data/normalisation/character_maps.py`

Import the existing maps from `src/` rather than redefining them. Import the new maps from `character_maps_new.py`. Build the `LANGUAGE_CHAR_MAPS` routing dict.

```python
"""
All character mapping tables for Strategy G.
Existing maps imported from src/config/language_normalisation_tables.py.
New maps imported from app/data/normalisation/character_maps_new.py.
"""

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[4] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from config.language_normalisation_tables import (
    GERMAN_UMLAUT_EXPANSIONS,
    GERMAN_UMLAUT_DROPS,
    FRENCH_ACCENT_STRIP,
    SPANISH_ACCENT_STRIP,
    SPANISH_N_TILDE_VARIANTS,
    ITALIAN_ACCENT_STRIP,
)

from app.data.normalisation.character_maps_new import (
    TURKISH_CHAR_MAP,
    DUTCH_CHAR_MAP,
    SCANDINAVIAN_CHAR_MAP,
    POLISH_CHAR_MAP,
    PORTUGUESE_CHAR_MAP,
)

# Primary map per language code
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

# Variant maps — secondary forms for watchlist matching
LANGUAGE_VARIANT_MAPS: dict[str, dict[str, str]] = {
    "de": GERMAN_UMLAUT_DROPS,
}
```

---

### Step 3 — Implement `app/pipeline/normalisation/character_map_normaliser.py`

Replace the stub entirely. Import the existing handlers from `src/` — do not copy or rewrite them. Only implement the five new handlers.

```python
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
    _normalise_english,
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
    if not handler:
        return None
    try:
        return handler(text, field_type)
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
```

---

### Step 4 — Wire into `app/pipeline/normalisation/router.py`

Replace `_try_strategy_g()` stub with:

```python
def _try_strategy_g(text: str, field_type: str, language: str) -> dict | None:
    try:
        from app.pipeline.normalisation.character_map_normaliser import apply_character_map
        return apply_character_map(text, language, field_type)
    except Exception:
        return None
```

---

### Step 5 — Tests `tests/test_strategy_g_character_maps.py`

No mocks. All tests call `apply_character_map()` directly or `route_field()`.

```python
from app.pipeline.normalisation.character_map_normaliser import apply_character_map
from app.pipeline.normalisation.router import route_field

# Existing — must still pass
def test_german_umlaut_expansion():
    assert apply_character_map("Müller", "de", "person_name")["normalised_form"] == "MUELLER"

def test_german_umlaut_drop_variant():
    assert "MULLER" in apply_character_map("Müller", "de", "person_name")["allowed_variants"]

def test_german_sz():
    assert apply_character_map("Straße", "de", "person_name")["normalised_form"] == "STRASSE"

def test_french_accent():
    assert apply_character_map("Élodie", "fr", "person_name")["normalised_form"] == "ELODIE"

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
    assert apply_character_map("Ĳsselmeer", "nl", "person_name")["normalised_form"] == "IJSSELMEER"

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

# Non-Latin returns None
def test_arabic_returns_none():
    assert apply_character_map("محمد", "ar", "person_name") is None

def test_japanese_returns_none():
    assert apply_character_map("田中", "ja", "person_name") is None

# Router
def test_german_routes_to_character_map():
    r = route_field({"original_text": "Müller", "field_type": "person_name", "language": "de"})
    assert r["processing_method"] == "CHARACTER_MAP"
    assert r["normalised_form"] == "MUELLER"
```

---

### Acceptance criteria

- `apply_character_map("Müller", "de", "person_name")` → `MUELLER` with `MULLER` in variants
- `apply_character_map("İstanbul", "tr", "person_name")` → `ISTANBUL`
- `apply_character_map("Łódź", "pl", "person_name")` → `LODZ`
- `apply_character_map("Ærø", "da", "person_name")` → `AERO`
- `apply_character_map("محمد", "ar", "person_name")` → `None`
- `route_field({"original_text": "Müller", "field_type": "person_name", "language": "de"})` → `processing_method == "CHARACTER_MAP"`
- All tests pass
- `src/pipeline/transliteration_engine.py` is not modified
- `src/config/language_normalisation_tables.py` is not modified