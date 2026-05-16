"""
Offset-based calendar conversions: Thai Buddhist Era and Minguo (ROC).

Both calendars use exactly the same month and day structure as the Gregorian
calendar — only the year count differs. Conversion is therefore simple arithmetic
with no leap year recalculation or month-length adjustment needed.

────────────────────────────────────────────────────────────────────────────────
THAI BUDDHIST ERA (พุทธศักราช, abbreviated พ.ศ. or B.E.)
────────────────────────────────────────────────────────────────────────────────

The Thai Buddhist Era counts years from the death (parinirvana) of the Buddha,
traditionally placed in 543 BCE. The Thai calendar is solar and follows the same
month/day structure as the Gregorian calendar.

Conversion: Gregorian year = Thai Buddhist year − 543

Examples:
    2568 BE → 2568 − 543 = 2025 CE
    2500 BE → 2500 − 543 = 1957 CE

Year ranges on modern documents:
    Thai passports:         2500–2600 BE (1957–2057 CE)
    Thai company registries: 2490–2600 BE (1947–2057 CE)

The Thai calendar year begins on 1 January (since 1941 CE). Before 1941,
the Thai year began on 1 April, which creates a 3-month discrepancy for
old documents. This module does NOT handle the pre-1941 convention because
it will not appear on company registry or KYC documents in scope.

Thai numerals (เลขไทย):
    ๐ ๑ ๒ ๓ ๔ ๕ ๖ ๗ ๘ ๙  (U+0E50–U+0E59)
These appear on official Thai documents and must be converted before parsing.

Thai month names (for documents that spell out the month):
    มกราคม (January), กุมภาพันธ์ (February), มีนาคม (March),
    เมษายน (April), พฤษภาคม (May), มิถุนายน (June),
    กรกฎาคม (July), สิงหาคม (August), กันยายน (September),
    ตุลาคม (October), พฤศจิกายน (November), ธันวาคม (December)

────────────────────────────────────────────────────────────────────────────────
MINGUO (民國) / REPUBLIC OF CHINA CALENDAR
────────────────────────────────────────────────────────────────────────────────

The Minguo calendar (also called the Republic of China calendar) counts years
from the founding of the Republic of China on 1 January 1912. It is the official
calendar of Taiwan and appears on Taiwanese passports, national identity cards
(國民身分證), and company registration documents issued by the Ministry of
Economic Affairs (經濟部).

Conversion: Gregorian year = Minguo year + 1911

Examples:
    114 ROC → 114 + 1911 = 2025 CE
    100 ROC → 100 + 1911 = 2011 CE
     89 ROC →  89 + 1911 = 2000 CE

Year ranges on modern documents:
    Taiwanese passports:            80–130 ROC (1991–2041 CE)
    Taiwanese company registries:   60–130 ROC (1971–2041 CE)

Minguo years are typically 2–3 digits (since only 114 years have elapsed by 2025).
This low digit count is the primary distinguishing feature — a 2- or 3-digit year
in a Taiwanese document context is almost certainly Minguo.

The calendar uses the same month/day structure as Gregorian, including the same
leap year rule (year divisible by 4, with century exceptions). Since Minguo year 1
= 1912 CE, the Gregorian leap year calculation applies directly to the converted
Gregorian year, not to the Minguo year.

Minguo year labels on documents: 民國, 民国, ROC, R.O.C., 中華民國, 中华民国
The year may be followed by 年 (year), 月 (month), 日 (day) in Chinese.
"""

import re


# ── Digit normalisation ───────────────────────────────────────────────────────

_THAI_DIGITS    = "๐๑๒๓๔๕๖๗๘๙"
_THAI_TABLE     = str.maketrans(_THAI_DIGITS, "0123456789")

# Persian-Indic and Arabic-Indic included for robustness on mixed documents
_PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"
_ARABIC_DIGITS  = "٠١٢٣٤٥٦٧٨٩"
_PERSIAN_TABLE  = str.maketrans(_PERSIAN_DIGITS, "0123456789")
_ARABIC_TABLE   = str.maketrans(_ARABIC_DIGITS,  "0123456789")


def _normalise_digits(text: str) -> str:
    """
    Convert Thai, Persian-Indic, and Arabic-Indic digits to ASCII.
    Applied before any numeric parsing.
    """
    return (
        text
        .translate(_THAI_TABLE)
        .translate(_PERSIAN_TABLE)
        .translate(_ARABIC_TABLE)
    )


# ── Thai Buddhist Era ─────────────────────────────────────────────────────────

_THAI_BE_OFFSET = 543

_THAI_MONTH_NAMES: dict[str, int] = {
    "มกราคม":   1,
    "กุมภาพันธ์": 2,
    "มีนาคม":   3,
    "เมษายน":  4,
    "พฤษภาคม": 5,
    "มิถุนายน": 6,
    "กรกฎาคม": 7,
    "สิงหาคม":  8,
    "กันยายน":  9,
    "ตุลาคม":  10,
    "พฤศจิกายน": 11,
    "ธันวาคม":  12,
}

# Abbreviated Thai month names (3-letter abbreviations used on some documents)
_THAI_MONTH_ABBR: dict[str, int] = {
    "ม.ค.": 1,  "ก.พ.": 2,  "มี.ค.": 3,  "เม.ย.": 4,
    "พ.ค.": 5,  "มิ.ย.": 6, "ก.ค.":  7,  "ส.ค.":  8,
    "ก.ย.": 9,  "ต.ค.": 10, "พ.ย.": 11,  "ธ.ค.": 12,
}


def thai_buddhist_to_gregorian(year: int, month: int, day: int) -> tuple[int, int, int]:
    """
    Convert a Thai Buddhist Era date to the Gregorian calendar.

    The conversion is a simple year offset: Gregorian year = BE year − 543.
    Month and day are identical between the two calendars.

    Args:
        year:  Thai Buddhist Era year (e.g. 2568 for 2025 CE).
               Valid range for KYC documents: 2490–2600 (1947–2057 CE).
        month: Month number (1 = January, 12 = December). Identical to Gregorian.
        day:   Day of month (1–31). Identical to Gregorian.

    Returns:
        Tuple (gregorian_year, gregorian_month, gregorian_day).

    Raises:
        ValueError: If the converted Gregorian year, month, or day are implausible
                    for a KYC document.

    Examples:
        >>> thai_buddhist_to_gregorian(2568, 5, 8)
        (2025, 5, 8)
        >>> thai_buddhist_to_gregorian(2500, 7, 15)
        (1957, 7, 15)
        >>> thai_buddhist_to_gregorian(2560, 2, 29)  # leap year: 2560-543=2017 — NOT leap
        ValueError (29 Feb 2017 does not exist)
    """
    if month < 1 or month > 12:
        raise ValueError(f"Invalid month: {month}. Must be 1–12.")
    if day < 1 or day > 31:
        raise ValueError(f"Invalid day: {day}. Must be 1–31.")

    gregorian_year = year - _THAI_BE_OFFSET

    # Sanity check: result should be a plausible document year
    if not (1900 <= gregorian_year <= 2100):
        raise ValueError(
            f"Thai Buddhist year {year} converts to Gregorian year {gregorian_year}, "
            f"which is outside the plausible range for a KYC document (1900–2100)."
        )

    # Validate day against the actual month length in the Gregorian year
    _validate_gregorian_date(gregorian_year, month, day)

    return gregorian_year, month, day


# ── Minguo (Republic of China) ────────────────────────────────────────────────

_MINGUO_OFFSET = 1911

_MINGUO_MONTH_NAMES: dict[str, int] = {
    "一月":   1, "二月":  2, "三月":  3,
    "四月":   4, "五月":  5, "六月":  6,
    "七月":   7, "八月":  8, "九月":  9,
    "十月":  10, "十一月": 11, "十二月": 12,
}


def minguo_to_gregorian(year: int, month: int, day: int) -> tuple[int, int, int]:
    """
    Convert a Minguo (Republic of China) date to the Gregorian calendar.

    The conversion is a simple year offset: Gregorian year = Minguo year + 1911.
    Month and day are identical between the two calendars.

    Args:
        year:  Minguo year (e.g. 114 for 2025 CE).
               Minguo year 1 = 1912 CE.
               Valid range for KYC documents: 60–130 (1971–2041 CE).
        month: Month number (1–12). Identical to Gregorian.
        day:   Day of month (1–31). Identical to Gregorian.

    Returns:
        Tuple (gregorian_year, gregorian_month, gregorian_day).

    Raises:
        ValueError: If the converted Gregorian year, month, or day are implausible.

    Examples:
        >>> minguo_to_gregorian(114, 5, 8)
        (2025, 5, 8)
        >>> minguo_to_gregorian(100, 1, 1)
        (2011, 1, 1)
        >>> minguo_to_gregorian(89, 2, 29)   # 89+1911=2000 — IS a leap year
        (2000, 2, 29)
    """
    if month < 1 or month > 12:
        raise ValueError(f"Invalid month: {month}. Must be 1–12.")
    if day < 1 or day > 31:
        raise ValueError(f"Invalid day: {day}. Must be 1–31.")

    gregorian_year = year + _MINGUO_OFFSET

    if not (1900 <= gregorian_year <= 2100):
        raise ValueError(
            f"Minguo year {year} converts to Gregorian year {gregorian_year}, "
            f"which is outside the plausible range for a KYC document (1900–2100)."
        )

    _validate_gregorian_date(gregorian_year, month, day)

    return gregorian_year, month, day


# ── Gregorian date validation ─────────────────────────────────────────────────

def _is_gregorian_leap(year: int) -> bool:
    """Return True if the given Gregorian year is a leap year."""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


_DAYS_IN_MONTH = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def _validate_gregorian_date(year: int, month: int, day: int) -> None:
    """
    Raise ValueError if the given Gregorian date does not exist.
    Used to catch invalid conversions (e.g. 29 Feb in a non-leap year).
    """
    max_day = _DAYS_IN_MONTH[month]
    if month == 2 and _is_gregorian_leap(year):
        max_day = 29
    if day > max_day:
        raise ValueError(
            f"{year:04d}-{month:02d}-{day:02d} is not a valid Gregorian date. "
            f"Month {month} of {year} has {max_day} days."
        )


# ── Detection patterns ────────────────────────────────────────────────────────

# Thai digit character class (for regex)
_THAI_DIG_RE = r"[๐-๙\d]"
_SEP         = r"[\s\/\-\.]"

# Thai Buddhist Era detection patterns
# Thai years on documents: 2490–2600 (4 digits, always starting with 2)
# Thai digits (๒๕๖๘) or ASCII digits (2568)
THAI_DATE_PATTERNS = [
    # Full date: DD/MM/YYYY or YYYY/MM/DD with Thai or ASCII digits
    # e.g. "08/05/2568" or "๐๘/๐๕/๒๕๖๘"
    re.compile(
        rf"([{_THAI_DIG_RE}]{{1,2}}){_SEP}([{_THAI_DIG_RE}]{{1,2}}){_SEP}([{_THAI_DIG_RE}]{{4}})"
    ),
    # YYYY first: e.g. "2568/05/08"
    re.compile(
        rf"([{_THAI_DIG_RE}]{{4}}){_SEP}([{_THAI_DIG_RE}]{{1,2}}){_SEP}([{_THAI_DIG_RE}]{{1,2}})"
    ),
    # Thai month name + year: e.g. "8 พฤษภาคม 2568"
    re.compile(
        r"(\d{1,2}|\s*[๐-๙]{1,2})\s+("
        + "|".join(re.escape(m) for m in sorted(_THAI_MONTH_NAMES.keys(), key=len, reverse=True))
        + r")\s+([๐-๙\d]{4})"
    ),
    # Abbreviated Thai month: e.g. "8 พ.ค. 2568"
    re.compile(
        r"(\d{1,2})\s+("
        + "|".join(re.escape(m) for m in _THAI_MONTH_ABBR.keys())
        + r")\s+([๐-๙\d]{4})"
    ),
    # Year only: พ.ศ. 2568 or พ.ศ.2568
    re.compile(r"พ\.?ศ\.?\s*([๐-๙]{4}|\d{4})"),
]

# Minguo detection patterns
# Minguo years: 2-3 digits (60–130 for modern documents)
# Preceded by 民國, 民国, ROC, R.O.C., or followed by 年
MINGUO_DATE_PATTERNS = [
    # Chinese format: 民國/民国 + year + 年 + month + 月 + day + 日
    # e.g. "民國114年5月8日"
    re.compile(
        r"(?:民[國国]|ROC|R\.O\.C\.)\s*(\d{2,3})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日"
    ),
    # Year only with label: 民國114年 or ROC 114
    re.compile(
        r"(?:民[國国]|ROC|R\.O\.C\.)\s*(\d{2,3})(?:\s*年)?"
    ),
    # Numeric format with Minguo label in vicinity:
    # e.g. "114/05/08" preceded or followed by 民國 within 20 chars
    re.compile(
        r"(\d{2,3})[\/\-\.](\d{1,2})[\/\-\.](\d{1,2})"
    ),
    # Chinese numeric month names with Minguo year
    re.compile(
        r"(\d{2,3})\s*年\s*("
        + "|".join(re.escape(m) for m in _MINGUO_MONTH_NAMES.keys())
        + r")\s*(\d{1,2})\s*日"
    ),
]


# ── Detect Thai Buddhist Era date ─────────────────────────────────────────────

def detect_thai_date(text: str) -> dict | None:
    """
    Attempt to detect and parse a Thai Buddhist Era date string from text.

    Tries each pattern in THAI_DATE_PATTERNS in order. Converts Thai digits
    to ASCII before parsing. Validates that the detected year falls in the
    Thai Buddhist Era range (2490–2600 BE).

    Args:
        text: Raw text from a document field (may contain Thai script numerals).

    Returns:
        Result dict if a Thai date is detected:
            normalised_form:   ISO 8601 date (YYYY-MM-DD) or year (YYYY)
            original_calendar: "thai_buddhist"
            original_text:     matched substring
            confidence:        0.90
            review_required:   False
        Returns None if no Thai date pattern found or conversion fails.

    Notes:
        - DD/MM/YYYY format is ambiguous — it could be Gregorian or Thai BE.
          The year range 2490–2600 is used as the disambiguating signal.
          Years in this range are unambiguously Thai BE for document purposes.
        - YYYY/MM/DD with year in range 2490–2600 is also treated as Thai BE.
    """
    if not text:
        return None

    normalised = _normalise_digits(text)

    # Pattern 0: DD/MM/YYYY — check if year is in Thai BE range
    match = THAI_DATE_PATTERNS[0].search(normalised)
    if match:
        try:
            d, m, y = int(match.group(1)), int(match.group(2)), int(match.group(3))
            if 2490 <= y <= 2600 and 1 <= m <= 12:
                g_year, g_month, g_day = thai_buddhist_to_gregorian(y, m, d)
                return _thai_result(g_year, g_month, g_day, match.group(0))
        except (ValueError, IndexError):
            pass

    # Pattern 1: YYYY/MM/DD — check if year is in Thai BE range
    match = THAI_DATE_PATTERNS[1].search(normalised)
    if match:
        try:
            y, m, d = int(match.group(1)), int(match.group(2)), int(match.group(3))
            if 2490 <= y <= 2600 and 1 <= m <= 12:
                g_year, g_month, g_day = thai_buddhist_to_gregorian(y, m, d)
                return _thai_result(g_year, g_month, g_day, match.group(0))
        except (ValueError, IndexError):
            pass

    # Pattern 2: Thai month name
    match = THAI_DATE_PATTERNS[2].search(text)  # search original for Thai chars
    if match:
        try:
            d = int(_normalise_digits(match.group(1).strip()))
            m = _THAI_MONTH_NAMES.get(match.group(2))
            y = int(_normalise_digits(match.group(3)))
            if m and 2490 <= y <= 2600:
                g_year, g_month, g_day = thai_buddhist_to_gregorian(y, m, d)
                return _thai_result(g_year, g_month, g_day, match.group(0))
        except (ValueError, IndexError):
            pass

    # Pattern 3: Abbreviated Thai month
    match = THAI_DATE_PATTERNS[3].search(text)
    if match:
        try:
            d = int(match.group(1))
            m = _THAI_MONTH_ABBR.get(match.group(2))
            y = int(_normalise_digits(match.group(3)))
            if m and 2490 <= y <= 2600:
                g_year, g_month, g_day = thai_buddhist_to_gregorian(y, m, d)
                return _thai_result(g_year, g_month, g_day, match.group(0))
        except (ValueError, IndexError):
            pass

    # Pattern 4: Year only with พ.ศ. label
    match = THAI_DATE_PATTERNS[4].search(text)
    if match:
        try:
            y = int(_normalise_digits(match.group(1)))
            if 2490 <= y <= 2600:
                g_year = y - _THAI_BE_OFFSET
                return {
                    "normalised_form":    str(g_year),
                    "original_calendar":  "thai_buddhist",
                    "original_text":      match.group(0),
                    "confidence":         0.80,
                    "review_required":    False,
                    "review_reason":      None,
                }
        except (ValueError, IndexError):
            pass

    return None


def _thai_result(g_year: int, g_month: int, g_day: int, original: str) -> dict:
    return {
        "normalised_form":    f"{g_year:04d}-{g_month:02d}-{g_day:02d}",
        "original_calendar":  "thai_buddhist",
        "original_text":      original,
        "confidence":         0.90,
        "review_required":    False,
        "review_reason":      None,
    }


# ── Detect Minguo date ────────────────────────────────────────────────────────

def detect_minguo_date(text: str) -> dict | None:
    """
    Attempt to detect and parse a Minguo (Republic of China) date from text.

    Minguo years are 2–3 digits. The calendar label (民國, ROC) is the primary
    disambiguating signal. Without the label, a 2- or 3-digit year in a date
    string from a Taiwanese document is treated as Minguo only if the
    COUNTRY field is TW — the router in calendar_rules.py enforces this
    (see: `if country == "TW": detect_minguo_date(text)`).

    Args:
        text: Raw text from a document field.

    Returns:
        Result dict if a Minguo date is detected:
            normalised_form:   ISO 8601 date (YYYY-MM-DD) or year (YYYY)
            original_calendar: "minguo"
            original_text:     matched substring
            confidence:        0.90 (with label) / 0.80 (without label)
            review_required:   False
        Returns None if no Minguo date pattern found or conversion fails.
    """
    if not text:
        return None

    # Pattern 0: Full date with 民國/ROC label — highest confidence
    match = MINGUO_DATE_PATTERNS[0].search(text)
    if match:
        try:
            y, m, d = int(match.group(1)), int(match.group(2)), int(match.group(3))
            if 1 <= m <= 12:
                g_year, g_month, g_day = minguo_to_gregorian(y, m, d)
                return _minguo_result(g_year, g_month, g_day, match.group(0), confidence=0.92)
        except (ValueError, IndexError):
            pass

    # Pattern 1: Year only with label
    match = MINGUO_DATE_PATTERNS[1].search(text)
    if match:
        try:
            y = int(match.group(1))
            g_year = y + _MINGUO_OFFSET
            if 1900 <= g_year <= 2100:
                return {
                    "normalised_form":    str(g_year),
                    "original_calendar":  "minguo",
                    "original_text":      match.group(0),
                    "confidence":         0.85,
                    "review_required":    False,
                    "review_reason":      None,
                }
        except (ValueError, IndexError):
            pass

    # Pattern 2: Numeric date without label — only valid in TW context
    # The caller (detect_minguo_date is only called when country=="TW")
    # so we can treat a 2-3 digit year as Minguo here.
    match = MINGUO_DATE_PATTERNS[2].search(text)
    if match:
        try:
            y, m, d = int(match.group(1)), int(match.group(2)), int(match.group(3))
            # Minguo years 60–130 (Gregorian 1971–2041) for modern KYC docs
            if 60 <= y <= 130 and 1 <= m <= 12:
                g_year, g_month, g_day = minguo_to_gregorian(y, m, d)
                return _minguo_result(g_year, g_month, g_day, match.group(0), confidence=0.80)
        except (ValueError, IndexError):
            pass

    # Pattern 3: Chinese numeric month names
    match = MINGUO_DATE_PATTERNS[3].search(text)
    if match:
        try:
            y = int(match.group(1))
            m = _MINGUO_MONTH_NAMES.get(match.group(2))
            d = int(match.group(3))
            if m and 60 <= y <= 130:
                g_year, g_month, g_day = minguo_to_gregorian(y, m, d)
                return _minguo_result(g_year, g_month, g_day, match.group(0), confidence=0.88)
        except (ValueError, IndexError):
            pass

    return None


def _minguo_result(g_year: int, g_month: int, g_day: int,
                   original: str, confidence: float = 0.90) -> dict:
    return {
        "normalised_form":    f"{g_year:04d}-{g_month:02d}-{g_day:02d}",
        "original_calendar":  "minguo",
        "original_text":      original,
        "confidence":         confidence,
        "review_required":    False,
        "review_reason":      None,
    }
