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
