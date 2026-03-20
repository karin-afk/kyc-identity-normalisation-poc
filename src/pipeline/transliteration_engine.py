"""
Transliteration engine.

Handles script-to-Latin conversion for:
  - Russian / Ukrainian / Bulgarian (Cyrillic) via `transliterate` package
  - Greek via `transliterate` package
  - Japanese via `pykakasi` (Hepburn romanisation)
  - Chinese (Mandarin) via `pypinyin` (Pinyin)
  - Arabic: basic ICAO consonant mapping; all results are flagged review_required=True
    because Arabic short vowels are omitted from standard text.
    Accurate Arabic transliteration requires the LLM layer (Phase 2).

Install: pip install transliterate pykakasi pypinyin unidecode
"""

import unicodedata


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _to_latin_fallback(text: str) -> str:
    """Last-resort Latin conversion using unidecode."""
    try:
        from unidecode import unidecode
        return unidecode(text)
    except ImportError:
        nfkd = unicodedata.normalize("NFKD", text)
        return nfkd.encode("ascii", "ignore").decode()


def _normalise(text: str) -> str:
    """Strip diacritics and return uppercase ASCII — the canonical matching form."""
    nfkd = unicodedata.normalize("NFKD", text)
    return nfkd.encode("ascii", "ignore").decode().upper()


def _build_result(
    original: str,
    latin: str,
    review: bool = False,
    reason: str | None = None,
) -> dict:
    return {
        "original_text": original,
        "latin_transliteration": latin,
        "allowed_variants": [],
        "analyst_english_rendering": latin,
        "normalised_form": _normalise(latin),
        "processing_method": "TRANSLITERATE",
        "confidence": 0.7 if review else 0.9,
        "review_required": review,
        "review_reason": reason,
        "should_use_in_screening": True,
    }


# ---------------------------------------------------------------------------
# Language-specific handlers
# ---------------------------------------------------------------------------

def _transliterate_cyrillic(text: str, language: str) -> dict:
    """Russian / Ukrainian / Bulgarian Cyrillic → Latin (BGN/PCGN-ish via transliterate lib)."""
    # Ukrainian-exclusive characters (absent from standard Russian/Bulgarian text).
    # Documents from former Soviet states often carry Ukrainian characters in rows
    # tagged as Russian — detect them and switch to Ukrainian transliteration mode.
    _UA_CHARS = "ЄєІіЇї"
    has_ua_chars = any(c in text for c in _UA_CHARS)
    effective_language = "uk" if (language == "uk" or has_ua_chars) else language

    if has_ua_chars or language == "uk":
        # The `transliterate` library drops/mangles these characters even in uk mode;
        # pre-process them to Latin equivalents before the library call.
        # Ї → plain I (not Yi) because inter-vocalic ї in patronymics romanises as
        # 'i' in standard KYC practice (e.g. Mykolaivna, not Mykolayivna).
        text = (
            text
            .replace("Є", "Ye").replace("є", "ye")   # U+0404 / U+0454 — Cyrillic Ye
            .replace("І", "I").replace("і", "i")     # U+0406 / U+0456 — Ukrainian I
            .replace("Ї", "I").replace("ї", "i")     # U+0407 / U+0457 — Yi (plain I for name forms)
        )
    try:
        from transliterate import translit
        lat = translit(text, effective_language, reversed=True)
    except Exception:
        lat = _to_latin_fallback(text)

    # The transliterate library emits a literal apostrophe for the Cyrillic soft sign
    # (e.g. NATAL'JA, JUR'EVICH).  Strip it — the soft sign has no Latin equivalent
    # in ICAO/BGN romanisation.
    lat = lat.replace("'", "")

    review = effective_language == "uk"  # Ukrainian/Russian distinction needs analyst check
    return _build_result(
        text, lat,
        review=review,
        reason="Ukrainian/Russian script distinction requires analyst review" if review else None,
    )


def _transliterate_greek(text: str) -> dict:
    """Greek → Latin via transliterate lib (ISO 843-ish)."""
    try:
        from transliterate import translit
        lat = translit(text, "el", reversed=True)
        # The transliterate lib renders ου as 'oy'; standardise to 'ou'
        lat = lat.replace("oy", "ou").replace("OY", "OU").replace("Oy", "Ou")
    except Exception:
        lat = _to_latin_fallback(text)
    return _build_result(text, lat)


def _transliterate_japanese(text: str) -> dict:
    """Japanese → Hepburn romanisation via pykakasi, with kanji-lookup override.

    For each pykakasi token whose original script appears in KANJI_AMBIGUITY:
    - Use the first listed reading as the primary form (overrides pykakasi's guess)
    - Collect all listed readings as per-token alternatives
    The alternatives are then recombined into full-name variant strings and
    stored in allowed_variants so the evaluator can accept any of them.
    """
    try:
        from config.kanji_lookup import KANJI_AMBIGUITY
    except ImportError:
        KANJI_AMBIGUITY = {}

    try:
        import pykakasi
        kks = pykakasi.kakasi()
        parts = kks.convert(text)

        primary_tokens: list[str] = []
        per_token_options: list[list[str]] = []  # all readings per token position

        for item in parts:
            hepburn = item.get("hepburn", "").strip()
            if not hepburn:
                continue
            orig = item.get("orig", "")

            # Lookup: try exact match, then longest-prefix substring
            readings: list[str] | None = KANJI_AMBIGUITY.get(orig)
            if readings is None and orig:
                for length in range(len(orig), 0, -1):
                    readings = KANJI_AMBIGUITY.get(orig[:length])
                    if readings:
                        break

            if readings:
                primary = readings[0].capitalize()
                alts = [r.capitalize() for r in readings]
            else:
                primary = hepburn.capitalize()
                alts = [primary]

            primary_tokens.append(primary)
            per_token_options.append(alts)

        lat = " ".join(primary_tokens)

        # Build allowed_variants: for each token with alternatives, produce a
        # full-name string with just that one token swapped.
        variants_set: set[str] = set()
        for i, options in enumerate(per_token_options):
            for alt in options:
                v = _normalise(" ".join(primary_tokens[:i] + [alt] + primary_tokens[i + 1:]))
                if v != _normalise(lat):
                    variants_set.add(v)

        allowed_variants = sorted(variants_set)

    except Exception:
        lat = _to_latin_fallback(text)
        allowed_variants = []

    has_kanji = any("\u4e00" <= ch <= "\u9fff" for ch in text)
    result = _build_result(
        text, lat,
        review=has_kanji,
        reason="Kanji reading ambiguity: furigana or MRZ required for certainty" if has_kanji else None,
    )
    result["allowed_variants"] = allowed_variants
    return result


def _transliterate_chinese(text: str, field_type: str = "") -> dict:
    """Chinese (Mandarin/Han) → Pinyin via pypinyin."""
    try:
        from pypinyin import lazy_pinyin, Style
        parts = lazy_pinyin(text, style=Style.NORMAL)
        if field_type == "person_name" and len(parts) >= 2:
            # Standard Chinese name structure: single-character surname + given name.
            # Fuse all given-name syllables into one token (e.g. CHEN ZHI QIANG →
            # CHEN ZHIQIANG) to match passport / document rendering conventions.
            lat = parts[0].capitalize() + " " + "".join(p.capitalize() for p in parts[1:])
        else:
            lat = " ".join(p.capitalize() for p in parts)
    except Exception:
        lat = _to_latin_fallback(text)

    return _build_result(
        text, lat,
        review=True,
        reason="Surname-first ordering ambiguity: analyst should confirm name order",
    )


# Simplified ICAO consonant map.
# Arabic short vowels (a/i/u) are not written in standard text, so vowel
# insertion is impossible without a name lexicon or LLM.
_ARABIC_MAP: dict[str, str] = {
    "\u0627": "a", "\u0628": "b", "\u062a": "t", "\u062b": "th", "\u062c": "j",
    "\u062d": "h", "\u062e": "kh", "\u062f": "d", "\u0630": "dh", "\u0631": "r",
    "\u0632": "z", "\u0633": "s", "\u0634": "sh", "\u0635": "s", "\u0636": "d",
    "\u0637": "t", "\u0638": "th", "\u0639": "", "\u063a": "gh", "\u0641": "f",
    "\u0642": "q", "\u0643": "k", "\u0644": "l", "\u0645": "m", "\u0646": "n",
    "\u0647": "h", "\u0648": "w", "\u064a": "y", "\u0649": "a", "\u0629": "h",
    "\u0623": "a", "\u0625": "i", "\u0622": "aa", "\u0624": "w", "\u0626": "y",
    "\u0621": "", " ": " ",
}

# Common compound tokens handled before character-by-character mapping
_ARABIC_TOKENS: dict[str, str] = {
    "\u0639\u0628\u062f \u0627\u0644\u0644\u0647": "Abdullah",
    "\u0627\u0644": "al-",
}


def _transliterate_arabic(text: str) -> dict:
    """
    Basic Arabic consonant transliteration.

    Result is always flagged review_required=True because vowel ambiguity
    makes fully accurate transliteration impossible without LLM assistance.
    Connect OPENAI_API_KEY in .env to improve Arabic accuracy in Phase 2.
    """
    working = text
    for token, replacement in _ARABIC_TOKENS.items():
        working = working.replace(token, f" {replacement} ")

    output: list[str] = []
    for ch in working:
        output.append(_ARABIC_MAP.get(ch, ch))
    lat = " ".join("".join(output).split())

    return _build_result(
        text, lat,
        review=True,
        reason=(
            "Arabic vowel ambiguity: short vowels are not written in standard text. "
            "Connect OPENAI_API_KEY in .env to enable LLM-assisted transliteration."
        ),
    )


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def transliterate(text: str, row: dict) -> dict:
    """
    Transliterate non-Latin text to Latin script.
    `row` must contain a 'language' key (ISO 639-1 code).
    """
    language = row.get("language", "")

    if language in ("ru", "uk", "bg"):
        return _transliterate_cyrillic(text, language)
    elif language == "ja":
        return _transliterate_japanese(text)
    elif language == "zh":
        return _transliterate_chinese(text, row.get("field_type", ""))
    elif language == "el":
        return _transliterate_greek(text)
    elif language == "ar":
        return _transliterate_arabic(text)
    else:
        lat = _to_latin_fallback(text)
        return _build_result(
            text, lat,
            review=True,
            reason=f"Language '{language}': fallback transliteration used",
        )