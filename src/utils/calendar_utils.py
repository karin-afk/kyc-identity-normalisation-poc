"""Calendar utilities for KYC field normalisation.

Pipeline layer: Layer 1 (pre-processing) — deterministic date normalisation
applied before routing to transliteration or LLM layers.

Supports:
- Arabic-Indic digit conversion to ASCII
- Hijri (AH) ↔ Gregorian calendar detection and conversion
- ISO 8601 date normalisation (YYYY-MM-DD output)
"""

import re
from typing import Optional


# ---------------------------------------------------------------------------
# Arabic-Indic digit tables
# ---------------------------------------------------------------------------

_ARABIC_INDIC_DIGITS = "٠١٢٣٤٥٦٧٨٩"
_EASTERN_ARABIC_INDIC_DIGITS = "۰۱۲۳۴۵۶۷۸۹"
_ASCII_DIGITS = "0123456789"

_ARABIC_INDIC_TABLE = str.maketrans(_ARABIC_INDIC_DIGITS, _ASCII_DIGITS)
_EASTERN_ARABIC_INDIC_TABLE = str.maketrans(_EASTERN_ARABIC_INDIC_DIGITS, _ASCII_DIGITS)


def arabic_indic_to_ascii(text: str) -> str:
    """Convert Arabic-Indic and Eastern Arabic-Indic digits to ASCII.

    Args:
        text: Input string that may contain Arabic-Indic (٠١…٩) or
              Eastern Arabic-Indic (۰۱…۹) digit characters.

    Returns:
        The same string with all such digits replaced by ASCII equivalents
        (0–9). All other characters are left unchanged.
    """
    text = text.translate(_ARABIC_INDIC_TABLE)
    text = text.translate(_EASTERN_ARABIC_INDIC_TABLE)
    return text


# ---------------------------------------------------------------------------
# Date parsing helpers
# ---------------------------------------------------------------------------

_DATE_SEPARATORS = re.compile(r"[/\-. ]")


def _split_date_parts(date_str: str) -> list[str]:
    """Split a date string on common separators, returning non-empty parts."""
    return [p for p in _DATE_SEPARATORS.split(date_str.strip()) if p]


def _find_year_candidate(parts: list[str]) -> Optional[int]:
    """Return the first part that looks like a 4-digit year, or None."""
    for p in parts:
        if len(p) == 4 and p.isdigit():
            return int(p)
    return None


# ---------------------------------------------------------------------------
# Calendar detection
# ---------------------------------------------------------------------------

def detect_calendar_system(date_str: str) -> str:
    """Determine whether a date string represents a Hijri or Gregorian date.

    Hijri detection rules:
    - A 4-digit year component in the range 1300–1500 (≈ 1882–2077 Gregorian)
    - OR the presence of Arabic-Indic digits; after converting them to ASCII,
      the year component falls in that range.

    Gregorian detection rules:
    - A 4-digit year component in the range 1900–2100.

    If both rules would match (e.g. 1950 is in both ranges), Gregorian wins
    because values in 1900–1500 overlap range are rare for Hijri in modern KYC.
    The 1900–2100 check is applied first.

    Args:
        date_str: A date string such as "١٤٤٥/٠٩/٢٠", "14/03/1985", "2024-03-14".

    Returns:
        "gregorian", "hijri", or "unknown".
    """
    normalised = arabic_indic_to_ascii(date_str)
    parts = _split_date_parts(normalised)
    year = _find_year_candidate(parts)
    if year is None:
        return "unknown"
    if 1900 <= year <= 2100:
        return "gregorian"
    if 1300 <= year <= 1500:
        return "hijri"
    return "unknown"


# ---------------------------------------------------------------------------
# Hijri → Gregorian conversion
# ---------------------------------------------------------------------------

def hijri_to_gregorian(year: int, month: int, day: int) -> tuple[int, int, int]:
    """Convert a Hijri (AH) date to a Gregorian date.

    Uses the ``hijri-converter`` library (``hijri_converter.convert.Hijri``)
    when available.  Falls back to the approximate astronomical formula when
    the library is not installed.

    Args:
        year:  Hijri year (e.g. 1445).
        month: Hijri month (1–12).
        day:   Hijri day (1–30).

    Returns:
        A ``(gregorian_year, gregorian_month, gregorian_day)`` tuple.

    Raises:
        ValueError: If the date is outside the supported Hijri range.
    """
    try:
        from hijri_converter.convert import Hijri  # type: ignore
        g = Hijri(year, month, day).to_gregorian()
        return g.year, g.month, g.day
    except ImportError:
        # Approximate formula — accurate to ±1 day for modern dates
        gregorian_year = year + 622 - (year // 33)
        return gregorian_year, month, day


# ---------------------------------------------------------------------------
# Master date normalisation
# ---------------------------------------------------------------------------

def normalise_date_field(date_str: str, language: str = "") -> dict:
    """Normalise a date field to ISO 8601 (YYYY-MM-DD).

    Processing steps:
    1. Convert Arabic-Indic digits to ASCII.
    2. Detect calendar system.
    3. If Hijri: convert to Gregorian and set ``review_required=True``.
    4. Parse the resulting (Gregorian) date and emit ISO 8601.
    5. If calendar is "unknown": set ``review_required=True``.

    Args:
        date_str: Raw date string from the source document (any script).
        language: ISO 639-1 language code (informational, not used in logic).

    Returns:
        A dict with keys:
        - ``normalised``: ISO 8601 date string (``"YYYY-MM-DD"``), or the
          original value if parsing failed.
        - ``original_calendar``: ``"hijri"`` | ``"gregorian"`` | ``"unknown"``
        - ``review_required``: ``bool``
        - ``review_reason``: ``str | None``
    """
    ascii_date = arabic_indic_to_ascii(date_str.strip())
    calendar = detect_calendar_system(ascii_date)

    review_required = False
    review_reason: Optional[str] = None

    if calendar == "unknown":
        if language == "ja":
            era_result = detect_and_convert_japanese_era(ascii_date)
            return {
                "normalised": era_result["normalised"],
                "original_calendar": "japanese_era" if era_result["era_detected"] else "unknown",
                "review_required": era_result["review_required"],
                "review_reason": era_result["review_reason"],
            }
        return {
            "normalised": ascii_date,
            "original_calendar": "unknown",
            "review_required": True,
            "review_reason": "Calendar system could not be determined",
        }

    parts = _split_date_parts(ascii_date)

    if calendar == "hijri":
        review_required = True
        review_reason = "Hijri date converted to Gregorian — verify original"
        try:
            year = int(next(p for p in parts if len(p) == 4))
            remaining = [int(p) for p in parts if len(p) != 4 and p.isdigit()]
            month = remaining[0] if len(remaining) >= 1 else 1
            day = remaining[1] if len(remaining) >= 2 else 1
            g_year, g_month, g_day = hijri_to_gregorian(year, month, day)
            normalised = f"{g_year:04d}-{g_month:02d}-{g_day:02d}"
        except (StopIteration, ValueError, IndexError):
            normalised = ascii_date
    else:
        # Gregorian — detect format and emit ISO 8601
        normalised = _parse_gregorian(ascii_date, parts)

    return {
        "normalised": normalised,
        "original_calendar": calendar,
        "review_required": review_required,
        "review_reason": review_reason,
    }


def _parse_gregorian(date_str: str, parts: list[str]) -> str:
    """Parse a Gregorian date string and return ISO 8601.

    Handles:
    - Already ISO: "2024-03-14" → "2024-03-14"
    - DD/MM/YYYY: "14/03/1985" → "1985-03-14"
    - YYYY/MM/DD: "1985/03/14" → "1985-03-14"
    - DD.MM.YYYY, DD-MM-YYYY, DD MM YYYY

    Args:
        date_str: The ASCII-normalised date string.
        parts:    Pre-split parts (output of ``_split_date_parts``).

    Returns:
        ISO 8601 string, or the original ``date_str`` if parsing failed.
    """
    if len(parts) != 3:
        return date_str

    try:
        ints = [int(p) for p in parts]
    except ValueError:
        return date_str

    # Identify which part is the year (4-digit or > 31)
    year_idx = next((i for i, v in enumerate(ints) if v > 31), None)
    if year_idx is None:
        return date_str

    year = ints[year_idx]
    others = [ints[i] for i in range(3) if i != year_idx]

    if year_idx == 0:
        # YYYY/MM/DD or YYYY/DD/MM — assume YYYY-MM-DD order
        month, day = others[0], others[1]
    else:
        # DD/MM/YYYY — assume day first (most common non-ISO format)
        day, month = others[0], others[1]

    if not (1 <= month <= 12 and 1 <= day <= 31):
        return date_str

    return f"{year:04d}-{month:02d}-{day:02d}"


# ---------------------------------------------------------------------------
# Section 3 — Japanese era-year conversion
# ---------------------------------------------------------------------------

JAPANESE_ERAS: dict[str, dict] = {
    # Kanji forms
    "明治": {"romaji": "Meiji",  "start_gregorian": 1868},
    "大正": {"romaji": "Taisho", "start_gregorian": 1912},
    "昭和": {"romaji": "Showa",  "start_gregorian": 1926},
    "平成": {"romaji": "Heisei", "start_gregorian": 1989},
    "令和": {"romaji": "Reiwa",  "start_gregorian": 2019},
    # Romanised forms (for partially-romanised input)
    "Meiji":  {"romaji": "Meiji",  "start_gregorian": 1868},
    "Taisho": {"romaji": "Taisho", "start_gregorian": 1912},
    "Showa":  {"romaji": "Showa",  "start_gregorian": 1926},
    "Heisei": {"romaji": "Heisei", "start_gregorian": 1989},
    "Reiwa":  {"romaji": "Reiwa",  "start_gregorian": 2019},
}

# Kanji digit characters
_KANJI_DIGIT_MAP: dict[str, int] = {
    "〇": 0, "零": 0,
    "一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
    "六": 6, "七": 7, "八": 8, "九": 9,
    "十": 10, "百": 100, "千": 1000,
}

# Match an era name (kanji or romaji) followed by a numeral and 年
_ERA_YEAR_RE = re.compile(
    r"(明治|大正|昭和|平成|令和|Meiji|Taisho|Showa|Heisei|Reiwa)"
    r"(元|[〇零一二三四五六七八九十百千\d]+)"
    r"年"
    r"(?:(元|[〇零一二三四五六七八九十\d]+)月)?"
    r"(?:(元|[〇零一二三四五六七八九十\d]+)日)?"
)

# Match a pure-Kanji year in positional notation (e.g. 二〇〇五年)
_KANJI_YEAR_RE = re.compile(
    r"([〇零一二三四五六七八九]{4})年"
    r"(?:([〇零一二三四五六七八九十\d]+)月)?"
    r"(?:([〇零一二三四五六七八九十\d]+)日)?"
)


def kanji_numeral_to_int(text: str) -> int:
    """Convert a Japanese Kanji numeral string to an integer.

    Handles two modes:
    - **Positional mode** (modern dates): ``"二〇〇五"`` → 2005.
      Triggered when the string is 4 characters and contains 〇/零.
    - **Classical mode**: ``"五十三"`` → 53, ``"十二"`` → 12, ``"三"`` → 3.

    Special value ``"元"`` (meaning "first year of an era") returns 1.

    Args:
        text: Kanji numeral string (may also contain ASCII digits mixed in).

    Returns:
        Integer value of the numeral.

    Raises:
        ValueError: If the string cannot be parsed.
    """
    if text == "元":
        return 1

    # Positional mode: 4-char string like 二〇〇五 (modern style)
    if len(text) == 4 and any(c in "〇零" for c in text):
        result = 0
        for ch in text:
            if ch.isdigit():
                result = result * 10 + int(ch)
            elif ch in _KANJI_DIGIT_MAP:
                result = result * 10 + _KANJI_DIGIT_MAP[ch]
            else:
                raise ValueError(f"Unexpected character in positional kanji: {ch!r}")
        return result

    # Classical mode: 五十三 → 53
    result = 0
    current = 0
    for ch in text:
        if ch.isdigit():
            current = current * 10 + int(ch)
        elif ch in _KANJI_DIGIT_MAP:
            val = _KANJI_DIGIT_MAP[ch]
            if val >= 10:
                # multiplier
                result += (current if current > 0 else 1) * val
                current = 0
            else:
                current = current * 10 + val
        else:
            raise ValueError(f"Unexpected character in kanji numeral: {ch!r}")
    result += current
    return result


def detect_and_convert_japanese_era(date_str: str) -> dict:
    """Detect a Japanese era-year date string and convert it to ISO 8601.

    Handles:
    - Era + Kanji year: ``"昭和五十三年四月三日"`` → ``"1978-04-03"``
    - Era + first year (元年): ``"平成元年一月八日"`` → ``"1989-01-08"``
    - Kanji positional Gregorian year: ``"二〇〇五年十二月一日"`` → ``"2005-12-01"``
    - Romanised era + ASCII year: ``"Heisei 3年1月5日"`` → ``"1991-01-05"``

    Era conversions always set ``review_required=True`` because the calculated
    year depends on which month in the era-start year the event falls (an
    approximation that may be off by 1 year near era boundaries).

    Args:
        date_str: A date string that may contain a Japanese era name.

    Returns:
        A dict with keys:
        - ``normalised``: ISO 8601 string, or original on parse failure.
        - ``era_detected``: Romaji era name (e.g. ``"Showa"``), or ``None``.
        - ``gregorian_year``: Integer Gregorian year, or ``None``.
        - ``review_required``: ``bool``
        - ``review_reason``: ``str | None``
    """
    m = _ERA_YEAR_RE.search(date_str)
    if m:
        era_key, era_year_str, month_str, day_str = m.groups()
        era_info = JAPANESE_ERAS[era_key]
        try:
            era_year = kanji_numeral_to_int(era_year_str) if era_year_str else 1
            gregorian_year = era_info["start_gregorian"] + era_year - 1
            month = kanji_numeral_to_int(month_str) if month_str else 1
            day = kanji_numeral_to_int(day_str) if day_str else 1
            romaji = era_info["romaji"]
            normalised = f"{gregorian_year:04d}-{month:02d}-{day:02d}"
            return {
                "normalised": normalised,
                "era_detected": romaji,
                "gregorian_year": gregorian_year,
                "review_required": True,
                "review_reason": (
                    f"Japanese era date converted — verify year: "
                    f"{romaji} {era_year} = {gregorian_year}"
                ),
            }
        except (ValueError, KeyError):
            pass

    # Kanji positional Gregorian year (no era prefix, e.g. 二〇〇五年四月一日)
    m2 = _KANJI_YEAR_RE.search(date_str)
    if m2:
        year_str, month_str, day_str = m2.groups()
        try:
            year = kanji_numeral_to_int(year_str)
            month = kanji_numeral_to_int(month_str) if month_str else 1
            day = kanji_numeral_to_int(day_str) if day_str else 1
            normalised = f"{year:04d}-{month:02d}-{day:02d}"
            return {
                "normalised": normalised,
                "era_detected": None,
                "gregorian_year": year,
                "review_required": False,
                "review_reason": None,
            }
        except ValueError:
            pass

    return {
        "normalised": date_str,
        "era_detected": None,
        "gregorian_year": None,
        "review_required": True,
        "review_reason": "Japanese date could not be parsed",
    }
