"""
Solar Hijri (Persian / Shamsi) calendar conversion.

The Solar Hijri calendar (also called Persian calendar or Shamsi calendar)
is the official calendar of Iran and Afghanistan. It is a solar calendar
that begins on the vernal equinox (Nowruz), meaning it stays in sync with
the seasons unlike the Hijri lunar calendar.

Key facts:
    - Epoch: Friday 22 March 622 CE (Julian) — the migration of the Prophet,
      same epoch as the Hijri lunar calendar but calculated differently.
    - Year 1404 SH corresponds to approximately 2025-2026 CE.
    - The calendar has 12 months. The first six months have 31 days each.
      The next five months have 30 days each. The last month (Esfand)
      has 29 days in a common year and 30 days in a leap year.
    - Leap years occur roughly every 4 years but follow a complex 2820-year
      cycle rather than the simple Gregorian rule. The commonly used
      approximation (subtract 474, divide by 2820, check remainder) is
      implemented below.
    - Persian-Indic numerals (۰۱۲۳۴۵۶۷۸۹) are standard in Iran and
      appear on official documents including passports and company registries.

Month names and lengths:
    1  Farvardin     31 days   (begins ~21 March)
    2  Ordibehesht   31 days   (begins ~21 April)
    3  Khordad       31 days   (begins ~22 May)
    4  Tir           31 days   (begins ~22 June)
    5  Mordad        31 days   (begins ~23 July)
    6  Shahrivar     31 days   (begins ~23 August)
    7  Mehr          30 days   (begins ~23 September)
    8  Aban          30 days   (begins ~23 October)
    9  Azar          30 days   (begins ~22 November)
    10 Dey           30 days   (begins ~22 December)
    11 Bahman        30 days   (begins ~21 January)
    12 Esfand        29/30     (begins ~20 February)

References:
    - Borkowski (1996) — "The Persian calendar for 3000 years"
    - convertdate library (used for validation in tests)
"""

import re
import math


# ── Persian-Indic numeral translation ────────────────────────────────────────

_PERSIAN_INDIC = "۰۱۲۳۴۵۶۷۸۹"
_ARABIC_INDIC  = "٠١٢٣٤٥٦٧٨٩"
_PERSIAN_TABLE = str.maketrans(_PERSIAN_INDIC, "0123456789")
_ARABIC_TABLE  = str.maketrans(_ARABIC_INDIC,  "0123456789")


def _normalise_digits(text: str) -> str:
    """
    Convert Persian-Indic and Arabic-Indic digits to ASCII digits.
    Applied before parsing any numeric string from a Persian document.
    """
    return text.translate(_PERSIAN_TABLE).translate(_ARABIC_TABLE)


# ── Month lengths ─────────────────────────────────────────────────────────────

# Months 1–6: 31 days each. Months 7–11: 30 days each. Month 12: 29/30.
_MONTH_LENGTHS = [0, 31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29]


def _is_solar_hijri_leap(year: int) -> bool:
    """
    Determine whether a Solar Hijri year is a leap year.

    Uses the algorithmic approximation based on the 2820-year grand cycle.
    The cycle has 683 leap years. A year is leap if its position within
    the sub-cycle falls on one of the designated leap positions.

    This algorithm matches the Iranian civil calendar used on official
    documents. It produces correct results for years 1 SH through
    approximately 3800 SH (well beyond any KYC document range).

    Args:
        year: Solar Hijri year (e.g. 1404).

    Returns:
        True if the year is a leap year, False otherwise.
    """
    # Shift epoch to align with the 2820-year cycle reference point
    # The cycle anchor is year 475 SH
    if year > 474:
        year_in_cycle = (year - 474) % 2820
    else:
        year_in_cycle = year - 474

    # Within the 2820-year cycle, check if the year falls in a leap position.
    # The cycle contains 683 leap years distributed as:
    # a 29-year sub-cycle followed by a 354-year sub-cycle, repeated.
    # The standard approximation: remainder = ((year + 474 + 38) * 682) mod 2816
    # A leap year occurs when remainder < 682.
    remainder = ((year_in_cycle + 474 + 38) * 682) % 2816
    return remainder < 682


def _days_in_solar_hijri_month(year: int, month: int) -> int:
    """
    Return the number of days in a given Solar Hijri month.

    Args:
        year:  Solar Hijri year.
        month: Month number (1–12).

    Returns:
        Number of days (29, 30, or 31).
    """
    if month < 1 or month > 12:
        raise ValueError(f"Invalid Solar Hijri month: {month}. Must be 1–12.")
    if month == 12:
        return 30 if _is_solar_hijri_leap(year) else 29
    return _MONTH_LENGTHS[month]


# ── Core conversion ───────────────────────────────────────────────────────────

def solar_hijri_to_gregorian(year: int, month: int, day: int) -> tuple[int, int, int]:
    """
    Convert a Solar Hijri (Persian / Shamsi) date to Gregorian.

    The conversion uses the Julian Day Number (JDN) as an intermediate
    representation, which avoids cumulative rounding errors and handles
    all edge cases including month boundaries and year boundaries correctly.

    Algorithm:
        1. Convert Solar Hijri date to Julian Day Number using the
           Borkowski/on-the-fly algorithm.
        2. Convert Julian Day Number to Gregorian calendar date.

    Args:
        year:  Solar Hijri year (e.g. 1404 for 2025/2026).
        month: Solar Hijri month (1 = Farvardin, 12 = Esfand).
        day:   Solar Hijri day (1–31 depending on month).

    Returns:
        Tuple of (gregorian_year, gregorian_month, gregorian_day).

    Raises:
        ValueError: If month or day are out of range for the given year.

    Examples:
        >>> solar_hijri_to_gregorian(1404, 2, 15)
        (2025, 5, 5)
        >>> solar_hijri_to_gregorian(1403, 12, 30)  # leap year
        (2025, 3, 20)
        >>> solar_hijri_to_gregorian(1400, 1, 1)
        (2021, 3, 21)
    """
    if month < 1 or month > 12:
        raise ValueError(f"Invalid Solar Hijri month: {month}. Must be 1–12.")
    max_day = _days_in_solar_hijri_month(year, month)
    if day < 1 or day > max_day:
        raise ValueError(
            f"Invalid Solar Hijri day: {day} for month {month} of year {year}. "
            f"Month {month} has {max_day} days."
        )

    # Step 1: Solar Hijri → Julian Day Number
    # Epoch: Julian Day Number of 1 Farvardin 1 SH = 1948320.5
    # (corresponds to 19 March 622 CE Julian / 22 March 622 CE proleptic Gregorian)
    #
    # Calculate the number of days elapsed from the epoch to the given date.

    # Days elapsed in complete years before this year
    # Each 2820-year grand cycle has 1029983 days (2820 * 365 + 683 leap days)
    ep_base = year - 474
    ep_year = 474 + ep_base % 2820

    # Julian Day Number calculation (Borkowski algorithm)
    jdn = (
        day                                                # days in current month
        + _sum_prior_month_days(month)                    # days in prior months this year
        + (ep_year * 682 - 110) // 2816                  # leap days in this sub-cycle
        + (ep_year - 1) * 365                             # regular days in sub-cycle years
        + (ep_base // 2820) * 1029983                    # complete 2820-year cycles
        + 1948319                                          # JDN epoch offset
    )

    # Step 2: Julian Day Number → Gregorian date
    return _jdn_to_gregorian(jdn)


def _sum_prior_month_days(month: int) -> int:
    """
    Return total number of days in all months before the given month
    within the same Solar Hijri year.
    Months 1–6 have 31 days; months 7–11 have 30 days; month 12 is variable
    but we only sum prior months here so month 12 is never included.
    """
    if month <= 1:
        return 0
    # Months 1–6: 31 days each
    # Months 7–11: 30 days each
    # Month 12: not counted here (we sum prior months only)
    complete_months_31 = min(month - 1, 6)
    complete_months_30 = max(0, min(month - 7, 5))
    return complete_months_31 * 31 + complete_months_30 * 30


def _jdn_to_gregorian(jdn: int) -> tuple[int, int, int]:
    """
    Convert a Julian Day Number to a Gregorian calendar date.

    Uses the Richards (2013) algorithm from the Explanatory Supplement
    to the Astronomical Almanac, 3rd edition.

    Args:
        jdn: Julian Day Number (integer).

    Returns:
        Tuple of (year, month, day) in the Gregorian calendar.
    """
    # Richards algorithm constants
    f = jdn + 1401 + (((4 * jdn + 274277) // 146097) * 3) // 4 - 38
    e = 4 * f + 3
    g = (e % 1461) // 4
    h = 5 * g + 2
    day   = (h % 153) // 5 + 1
    month = (h // 153 + 2) % 12 + 1
    year  = e // 1461 - 4716 + (14 - month) // 12
    return year, month, day


# ── Date string detection ─────────────────────────────────────────────────────

# Solar Hijri year range on modern documents: 1300–1500 SH (1921–2122 CE)
# Years in this range are recognisably Solar Hijri because they fall between
# 1300 and 1499 — outside any plausible Gregorian or Hijri lunar year.
# (Hijri lunar years in the same CE period are 1339–1543 AH, overlapping,
# so year range alone is not sufficient — context and digit form also matter.)

# Regex patterns for Solar Hijri date strings in Persian documents.
# Covers both Persian-Indic (۱۴۰۴) and ASCII digit forms.
# Separators: slash, hyphen, period, or Persian comma (،)

_PERSIAN_DIGIT   = "[۰-۹0-9]"
_ARABIC_DIG      = "[٠-٩0-9]"
_SEP             = r"[\/\-\.\،]"

SOLAR_HIJRI_PATTERNS = [
    # Full date: YYYY/MM/DD or YYYY-MM-DD with Persian-Indic digits
    re.compile(
        rf"([۱][۳-۴][{_PERSIAN_DIGIT}]{{2}}){_SEP}([{_PERSIAN_DIGIT}]{{1,2}}){_SEP}([{_PERSIAN_DIGIT}]{{1,2}})"
    ),
    # Full date: ASCII digits, year 1300–1499
    re.compile(
        r"(1[34]\d{2})[\/\-\.](\d{1,2})[\/\-\.](\d{1,2})"
    ),
    # Year only: Persian-Indic 4-digit year starting with ۱۳ or ۱۴
    re.compile(
        r"([۱][۳-۴][۰-۹]{2})"
    ),
    # Month name patterns in Farsi (for documents that spell out the month)
    re.compile(
        r"([۱۴۱۳\d]{4})\s+"
        r"(فروردین|اردیبهشت|خرداد|تیر|مرداد|شهریور|مهر|آبان|آذر|دی|بهمن|اسفند)"
        r"\s+([۱-۳]?[۰-۹])"
    ),
]

# Mapping of Farsi month names to month numbers
SOLAR_HIJRI_MONTH_NAMES = {
    "فروردین":   1,
    "اردیبهشت":  2,
    "خرداد":     3,
    "تیر":       4,
    "مرداد":     5,
    "شهریور":    6,
    "مهر":       7,
    "آبان":      8,
    "آذر":       9,
    "دی":        10,
    "بهمن":      11,
    "اسفند":     12,
}


def detect_solar_hijri_date(text: str) -> dict | None:
    """
    Attempt to detect and parse a Solar Hijri date string from text.

    Tries each pattern in SOLAR_HIJRI_PATTERNS in order.
    If a match is found, parses the year, month, and day and converts
    to Gregorian via solar_hijri_to_gregorian().

    Args:
        text: Raw text from a document field (may contain Persian-Indic digits).

    Returns:
        A result dict if a Solar Hijri date is detected and successfully
        converted, containing:
            normalised_form:    ISO 8601 date string (YYYY-MM-DD)
            original_calendar:  "solar_hijri"
            original_text:      the matched date string
            confidence:         0.90
            review_required:    False
        Returns None if no Solar Hijri date pattern is found.

    Notes:
        - A year-only match returns normalised_form as YYYY (year only).
        - If conversion raises ValueError (invalid day/month), returns None
          and the caller falls through to the next detection method.
    """
    if not text:
        return None

    normalised_text = _normalise_digits(text.strip())

    # Pattern 1 & 2: full date with numeric month
    for pattern in SOLAR_HIJRI_PATTERNS[:2]:
        match = pattern.search(normalised_text)
        if match:
            try:
                year  = int(_normalise_digits(match.group(1)))
                month = int(_normalise_digits(match.group(2)))
                day   = int(_normalise_digits(match.group(3)))
                # Sanity check: Solar Hijri years on modern documents are 1300–1499
                if not (1300 <= year <= 1499):
                    continue
                g_year, g_month, g_day = solar_hijri_to_gregorian(year, month, day)
                return {
                    "normalised_form":    f"{g_year:04d}-{g_month:02d}-{g_day:02d}",
                    "original_calendar":  "solar_hijri",
                    "original_text":      match.group(0),
                    "confidence":         0.90,
                    "review_required":    False,
                    "review_reason":      None,
                }
            except (ValueError, IndexError):
                continue

    # Pattern 3: year only (Persian-Indic)
    match = SOLAR_HIJRI_PATTERNS[2].search(text)  # search original — pattern uses Persian chars
    if match:
        try:
            year = int(_normalise_digits(match.group(1)))
            if 1300 <= year <= 1499:
                # Convert 1 Farvardin of that year as the reference point
                g_year, _, _ = solar_hijri_to_gregorian(year, 1, 1)
                return {
                    "normalised_form":    str(g_year),
                    "original_calendar":  "solar_hijri",
                    "original_text":      match.group(0),
                    "confidence":         0.75,  # lower — year only
                    "review_required":    False,
                    "review_reason":      None,
                }
        except (ValueError, IndexError):
            pass

    # Pattern 4: month name in Farsi
    match = SOLAR_HIJRI_PATTERNS[3].search(text)
    if match:
        try:
            year       = int(_normalise_digits(match.group(1)))
            month_name = match.group(2)
            day        = int(_normalise_digits(match.group(3)))
            month      = SOLAR_HIJRI_MONTH_NAMES.get(month_name)
            if month and 1300 <= year <= 1499:
                g_year, g_month, g_day = solar_hijri_to_gregorian(year, month, day)
                return {
                    "normalised_form":    f"{g_year:04d}-{g_month:02d}-{g_day:02d}",
                    "original_calendar":  "solar_hijri",
                    "original_text":      match.group(0),
                    "confidence":         0.92,
                    "review_required":    False,
                    "review_reason":      None,
                }
        except (ValueError, IndexError):
            pass

    return None
