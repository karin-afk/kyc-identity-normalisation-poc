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
