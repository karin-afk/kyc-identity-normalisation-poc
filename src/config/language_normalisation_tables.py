"""Language-specific normalisation tables for KYC identity field normalisation.

Pipeline layer: Layer 2 (deterministic) — used by the transliteration handlers
for de, fr, es, it, ko, and en language codes.

All constants are module-level. Do not import from pipeline modules here
(avoid circular imports).
"""

# ---------------------------------------------------------------------------
# German
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# French
# ---------------------------------------------------------------------------

FRENCH_ACCENT_STRIP: dict[str, str] = {
    "É": "E", "é": "e",
    "È": "E", "è": "e",
    "Ê": "E", "ê": "e",
    "Ë": "E", "ë": "e",
    "À": "A", "à": "a",
    "Â": "A", "â": "a",
    "Ù": "U", "ù": "u",
    "Û": "U", "û": "u",
    "Ü": "U", "ü": "u",
    "Î": "I", "î": "i",
    "Ï": "I", "ï": "i",
    "Ô": "O", "ô": "o",
    "Ÿ": "Y", "ÿ": "y",
    "Ç": "C", "ç": "c",
    "Œ": "OE", "œ": "oe",
    "Æ": "AE", "æ": "ae",
}


# ---------------------------------------------------------------------------
# Spanish
# ---------------------------------------------------------------------------

SPANISH_ACCENT_STRIP: dict[str, str] = {
    "Á": "A", "á": "a",
    "É": "E", "é": "e",
    "Í": "I", "í": "i",
    "Ó": "O", "ó": "o",
    "Ú": "U", "ú": "u",
    "Ü": "U", "ü": "u",
    "Ñ": "N", "ñ": "n",
}

# ñ can appear as either "n" or "ny" on international watchlists
SPANISH_N_TILDE_VARIANTS: list[str] = ["n", "ny"]


# ---------------------------------------------------------------------------
# Italian
# ---------------------------------------------------------------------------

ITALIAN_ACCENT_STRIP: dict[str, str] = {
    "À": "A", "à": "a",
    "È": "E", "è": "e",
    "É": "E", "é": "e",
    "Ì": "I", "ì": "i",
    "Î": "I", "î": "i",
    "Ò": "O", "ò": "o",
    "Ó": "O", "ó": "o",
    "Ù": "U", "ù": "u",
}


# ---------------------------------------------------------------------------
# Korean surname variants (Revised Romanisation → alternate romanisations)
# Cannot be derived algorithmically. Hard-coded per KYC watchlist convention.
# ---------------------------------------------------------------------------

KOREAN_SURNAME_VARIANTS: dict[str, list[str]] = {
    "이": ["I", "Yi", "Lee", "Rhee", "Ri", "Rhie"],
    "박": ["Bak", "Park", "Pak"],
    "최": ["Choe", "Choi", "Ch'oe"],
    "류": ["Ryu", "Yu", "Yoo", "Lyu"],
    "유": ["Yu", "Yoo", "Ryu"],
    "정": ["Jeong", "Jung", "Chung", "Chŏng"],
    "권": ["Gwon", "Kwon", "Kwŏn"],
    "윤": ["Yun", "Yoon"],
    "임": ["Im", "Lim"],
    "나": ["Na", "Rah"],
    "라": ["Ra", "Na", "Rah"],
    "노": ["No", "Roh"],
    "오": ["O", "Oh"],
    "조": ["Jo", "Cho"],
    "신": ["Sin", "Shin"],
}


# ---------------------------------------------------------------------------
# Korean Hangul romanisation tables (Revised Romanisation of Korea)
# Used as built-in fallback when the korean-romanizer library is unavailable.
# ---------------------------------------------------------------------------

# Choseong (initial consonant) index 0–18
_KR_CHOSEONG: list[str] = [
    "g", "kk", "n", "d", "tt", "r", "m", "b", "pp",
    "s", "ss", "", "j", "jj", "ch", "k", "t", "p", "h",
]

# Jungseong (vowel) index 0–20
_KR_JUNGSEONG: list[str] = [
    "a", "ae", "ya", "yae", "eo", "e", "yeo", "ye", "o",
    "wa", "wae", "oe", "yo", "u", "wo", "we", "wi", "yu", "eu", "ui", "i",
]

# Jongseong (final consonant) index 0–27 (0 = no final)
_KR_JONGSEONG: list[str] = [
    "", "k", "k", "k", "n", "n", "n", "t", "l",
    "k", "m", "p", "l", "l", "p", "l", "m", "p", "p",
    "t", "t", "ng", "t", "t", "k", "t", "p", "t",
]

_HANGUL_START = 0xAC00
_HANGUL_END   = 0xD7A3


def hangul_syllable_to_roman(syllable: str) -> str:
    """Convert a single Hangul syllable character to Revised Romanisation.

    Args:
        syllable: A single Hangul syllable character (U+AC00–U+D7A3).

    Returns:
        Romanised string (e.g. '박' → 'bak').
    """
    code = ord(syllable) - _HANGUL_START
    jong = code % 28
    code //= 28
    jung = code % 21
    cho = code // 21
    return _KR_CHOSEONG[cho] + _KR_JUNGSEONG[jung] + _KR_JONGSEONG[jong]


def romanise_hangul(text: str) -> str:
    """Romanise a Hangul string to Revised Romanisation of Korea.

    Non-Hangul characters (spaces, hyphens, ASCII) are passed through.

    Args:
        text: A string that may contain Hangul syllable characters.

    Returns:
        Romanised string with Hangul replaced by RR equivalents.
    """
    result: list[str] = []
    for ch in text:
        if _HANGUL_START <= ord(ch) <= _HANGUL_END:
            result.append(hangul_syllable_to_roman(ch))
        else:
            result.append(ch)
    return "".join(result)
