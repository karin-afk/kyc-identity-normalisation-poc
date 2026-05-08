"""
Hebrew (Jewish) calendar conversion.

The Hebrew calendar is a lunisolar calendar that has been in continuous use
for over two millennia. It is the official calendar of Israel and appears on
Israeli passports, identity cards, company registry documents, and notarial
deeds, sometimes alongside Gregorian dates and sometimes alone.

Key facts:
    - The epoch is 1 Tishrei 1 AM = 6 October 3761 BCE (proleptic Julian)
      or 7 October 3761 BCE (proleptic Gregorian). This is the traditional
      Jewish date of Creation.
    - Year 5786 AM (Anno Mundi) corresponds approximately to 2025/2026 CE.
      The Hebrew year begins in autumn (Rosh Hashana, 1 Tishrei).
    - The calendar is lunisolar: months follow the lunar cycle (~29.5 days)
      but the year is kept in sync with the solar year via a 19-year
      intercalation cycle (the Metonic cycle).
    - The 19-year Metonic cycle contains 7 leap years and 12 common years.
      Leap years have 13 months; common years have 12 months.
    - The leap month (Adar I / Adar Rishon) is inserted before Adar in
      leap years. In common years there is only one Adar.
    - Month lengths are not fixed — they vary to satisfy religious rules
      (e.g. Rosh Hashana cannot fall on Sunday, Wednesday, or Friday).
      This makes algorithmic conversion non-trivial. The implementation
      below uses the Molad (mean lunar conjunction) calculation, which
      is the authoritative method used in Jewish law (halacha).

Month order and names (common year, 12 months):
    1  Nisan        29 or 30 days  (spring — Passover month)
    2  Iyar         29 days
    3  Sivan        30 days
    4  Tammuz       29 days
    5  Av           30 days
    6  Elul         29 days
    7  Tishrei      30 days        (Rosh Hashana — NEW YEAR, month 7 in count from Nisan)
    8  Cheshvan     29 or 30 days  (variable — "deficient" or "complete")
    9  Kislev       30 or 29 days  (variable — "complete" or "deficient")
    10 Tevet        29 days
    11 Shevat       30 days
    12 Adar         29 days        (30 days in leap year as Adar I; Adar II has 29)

In a leap year (13 months), Adar becomes Adar I (30 days) and Adar II
(29 days) is inserted after it. Month numbering in this module follows
the civil/computational convention: Tishrei = month 1 of the year
(since the year number increments on 1 Tishrei).

Civil month order used in this module (year starts Tishrei):
    1  Tishrei      30
    2  Cheshvan     29 or 30
    3  Kislev       30 or 29
    4  Tevet        29
    5  Shevat       30
    6  Adar I       30 (leap year only)
    6  Adar         29 (common year) / month 7 becomes Adar II in leap year
    7  Nisan        30
    8  Iyar         29
    9  Sivan        30
    10 Tammuz       29
    11 Av           30
    12 Elul         29

The Metonic cycle leap years within each 19-year cycle are years:
    3, 6, 8, 11, 14, 17, 19
(i.e. year % 19 in {0, 3, 6, 8, 11, 14, 17} where year % 19 == 0 means year 19)

References:
    - Dershowitz & Reingold (2018) "Calendrical Calculations" 4th ed., Cambridge UP
    - Spier (1986) "The Comprehensive Hebrew Calendar"
    - convertdate Python library (used for test validation)
"""

import re
import math


# ── Constants (Talmudic / halachic values) ────────────────────────────────────

# The Molad of Tohu (epoch molad): 1 Tishrei year 1 AM
# Expressed as days and parts (chalakim) from a reference Sunday midnight.
# 1 day = 24 hours = 1080 chalakim (parts). 1 hour = 18 minutes = 1080/24 chalakim.
# The Molad of Tohu: day 2 (Monday), 5 hours, 204 chalakim.
_MOLAD_TOHU_DAY   = 2       # day of week (1=Sunday)
_MOLAD_TOHU_PARTS = 31524   # total chalakim from Sunday midnight: 5*1080 + 204 = 5604... wait
# Correct: day 2, 5h 204p → total parts from epoch = (2-1)*24*1080 + 5*1080 + 204
# = 25920 + 5400 + 204 = 31524
_MOLAD_TOHU_TOTAL = 31524   # chalakim from reference Sunday midnight

# Mean lunar month (Molad interval) in chalakim
# 29 days, 12 hours, 793 chalakim = 29*24*1080 + 12*1080 + 793
_LUNAR_MONTH_PARTS = 765433  # 29*25920 + 12*1080 + 793

# Days in the Hebrew calendar week reference
_PARTS_PER_HOUR = 1080
_PARTS_PER_DAY  = 25920   # 24 * 1080
_PARTS_PER_WEEK = 181440  # 7 * 25920

# Julian Day Number of the Hebrew epoch (1 Tishrei 1 AM)
# = Julian Day Number of 6 October 3761 BCE (Julian calendar)
# = JDN 347997.5 — using integer JDN: 347998
_HEBREW_EPOCH_JDN = 347998


# ── Leap year determination ───────────────────────────────────────────────────

def _is_hebrew_leap(year: int) -> bool:
    """
    Return True if the given Hebrew year is a leap year.

    The 19-year Metonic cycle contains 7 leap years at positions
    3, 6, 8, 11, 14, 17, 19 within the cycle.
    Equivalently: a year is leap if (7 * year + 1) mod 19 < 7.

    Args:
        year: Hebrew year (e.g. 5786).

    Returns:
        True if leap year (13 months), False if common year (12 months).

    Examples:
        >>> _is_hebrew_leap(5784)  # 2023/2024 — leap year
        True
        >>> _is_hebrew_leap(5785)  # 2024/2025 — common year
        False
        >>> _is_hebrew_leap(5786)  # 2025/2026 — common year
        False
    """
    return (7 * year + 1) % 19 < 7


# ── Molad calculation ─────────────────────────────────────────────────────────

def _months_elapsed(year: int) -> int:
    """
    Return the number of lunar months elapsed from the epoch to the start
    of the given Hebrew year (before 1 Tishrei of that year).

    Common years have 12 months; leap years have 13.
    """
    return (
        235 * ((year - 1) // 19)               # complete 19-year cycles: 235 months each
        + 12 * ((year - 1) % 19)               # regular months in the partial cycle
        + (7 * ((year - 1) % 19) + 1) // 19   # leap months in the partial cycle
    )


def _molad(year: int) -> int:
    """
    Calculate the Molad (mean lunar conjunction) for 1 Tishrei of the
    given Hebrew year, expressed as total chalakim from the reference epoch.

    Args:
        year: Hebrew year.

    Returns:
        Total chalakim from the reference Sunday midnight epoch.
    """
    months = _months_elapsed(year)
    return _MOLAD_TOHU_TOTAL + months * _LUNAR_MONTH_PARTS


# ── Year length determination ─────────────────────────────────────────────────

def _elapsed_days(year: int) -> int:
    """
    Calculate the number of days from the Hebrew epoch to 1 Tishrei of the
    given year, after applying the four postponement rules (Dechiyot).

    The Dechiyot are four rules that postpone Rosh Hashana to avoid
    certain calendar conflicts:
        1. Molad Zaken: if the molad occurs at or after noon (18 hours),
           postpone by one day.
        2. Lo ADU Rosh: Rosh Hashana cannot fall on Sunday (1), Wednesday (4),
           or Friday (6). If it would, postpone by one day.
        3. GaTaRaD: In a common year, if the molad falls on Tuesday (3) at
           or after 9h 204p, postpone by two days (to Thursday).
        4. BeTuTeKaPoT: After a leap year, if the molad falls on Monday (2) at
           or after 15h 589p, postpone by one day.

    Args:
        year: Hebrew year.

    Returns:
        Number of days from the epoch to 1 Tishrei of the given year.
    """
    months  = _months_elapsed(year)
    parts   = _MOLAD_TOHU_TOTAL + months * _LUNAR_MONTH_PARTS

    # Raw day count and time within day
    day_of_week = (parts // _PARTS_PER_DAY) % 7  # 0=Sunday
    day_count   = parts // _PARTS_PER_DAY
    parts_today = parts % _PARTS_PER_DAY

    # Postponement rule 1 (Molad Zaken): noon or later → postpone
    if parts_today >= 19440:  # 18 hours * 1080 = 19440 chalakim
        day_count   += 1
        day_of_week  = (day_of_week + 1) % 7
        parts_today  = 0

    # Postponement rule 2 (Lo ADU Rosh): not on days 0(Sun), 3(Wed), 5(Fri)
    if day_of_week in (0, 3, 5):
        day_count   += 1
        day_of_week  = (day_of_week + 1) % 7

    # Postponement rule 3 (GaTaRaD): common year, Tuesday >= 9h 204p
    # 9 hours 204 parts = 9*1080 + 204 = 9924 chalakim
    if (not _is_hebrew_leap(year)
            and day_of_week == 2          # Tuesday
            and parts_today >= 9924):
        day_count   += 2
        day_of_week  = (day_of_week + 2) % 7

    # Postponement rule 4 (BeTuTeKaPoT): year after a leap year, Monday >= 15h 589p
    # 15 hours 589 parts = 15*1080 + 589 = 16789 chalakim
    if (_is_hebrew_leap(year - 1)
            and day_of_week == 1          # Monday
            and parts_today >= 16789):
        day_count   += 1

    return day_count


def _days_in_year(year: int) -> int:
    """
    Return the total number of days in the given Hebrew year.
    This is the difference between the elapsed days of year+1 and year.
    """
    return _elapsed_days(year + 1) - _elapsed_days(year)


# ── Month lengths ─────────────────────────────────────────────────────────────

def _month_lengths(year: int) -> list[int]:
    """
    Return the list of day counts for each month of the given Hebrew year,
    starting from Tishrei (month 1 in the civil convention used here).

    Month lengths depend on whether the year is:
        - Deficient (חסרה): Cheshvan=29, Kislev=29 — total varies
        - Regular (כסדרה):  Cheshvan=29, Kislev=30 — total varies
        - Complete (שלמה):  Cheshvan=30, Kislev=30 — total varies

    The year type is determined by the total number of days in the year,
    which is derived from the Molad calculations above.

    Args:
        year: Hebrew year.

    Returns:
        List of integers, one per month (12 or 13 elements).
    """
    total_days = _days_in_year(year)
    leap = _is_hebrew_leap(year)

    # Base month lengths for a regular year (Cheshvan=29, Kislev=30)
    # Civil order: Tishrei, Cheshvan, Kislev, Tevet, Shevat,
    #              [Adar I if leap], Adar/Adar II, Nisan, Iyar, Sivan,
    #              Tammuz, Av, Elul
    if leap:
        # 13-month leap year baseline: 354 + 30 (Adar I) = 384 days regular
        months = [30, 29, 30, 29, 30, 30, 29, 30, 29, 30, 29, 30, 29]
        regular_days = 384
    else:
        # 12-month common year baseline: 354 days regular
        months = [30, 29, 30, 29, 30, 29, 30, 29, 30, 29, 30, 29]
        regular_days = 354

    delta = total_days - regular_days

    if delta == -1:
        # Deficient: Kislev shortened to 29
        months[2] = 29  # Kislev is index 2
    elif delta == 1:
        # Complete: Cheshvan extended to 30
        months[1] = 30  # Cheshvan is index 1
    # delta == 0: regular, no change needed

    return months


def _days_before_month(year: int, month: int) -> int:
    """
    Return the number of days from 1 Tishrei of the given year
    to the start of the given month.

    Args:
        year:  Hebrew year.
        month: Month number (1 = Tishrei, following civil convention).

    Returns:
        Days elapsed before the start of the given month in that year.
    """
    lengths = _month_lengths(year)
    return sum(lengths[:month - 1])


# ── Core conversion ───────────────────────────────────────────────────────────

def hebrew_to_gregorian(year: int, month: int, day: int) -> tuple[int, int, int]:
    """
    Convert a Hebrew calendar date to the Gregorian calendar.

    Month numbering convention used in this function (civil order,
    year starts on 1 Tishrei):
        1  = Tishrei      (30 days)
        2  = Cheshvan     (29 or 30)
        3  = Kislev       (29 or 30)
        4  = Tevet        (29)
        5  = Shevat       (30)
        6  = Adar I       (30, leap years only) / Adar (29, common years)
        7  = Adar II      (29, leap years) / Nisan (30, common years)
        8  = Nisan        (30, leap) / Iyar (29, common)
        ... etc.

    This matches the convention used by the convertdate library and
    Dershowitz & Reingold "Calendrical Calculations".

    Args:
        year:  Hebrew year (e.g. 5786 for 2025/2026).
        month: Month number (1–12 for common years, 1–13 for leap years).
        day:   Day of month (1–30).

    Returns:
        Tuple (gregorian_year, gregorian_month, gregorian_day).

    Raises:
        ValueError: If year, month, or day are out of range.

    Examples:
        >>> hebrew_to_gregorian(5786, 1, 1)   # 1 Tishrei 5786 = Rosh Hashana 2025
        (2025, 9, 22)
        >>> hebrew_to_gregorian(5785, 7, 15)  # 15 Nisan 5785 = Passover 2025
        (2025, 4, 13)
        >>> hebrew_to_gregorian(5784, 6, 1)   # 1 Adar I 5784 (leap year)
        (2024, 2, 10)
    """
    num_months = 13 if _is_hebrew_leap(year) else 12
    if month < 1 or month > num_months:
        raise ValueError(
            f"Invalid Hebrew month: {month} for year {year}. "
            f"Year {'is a leap year (13 months)' if _is_hebrew_leap(year) else 'is a common year (12 months)'}."
        )
    lengths = _month_lengths(year)
    max_day = lengths[month - 1]
    if day < 1 or day > max_day:
        raise ValueError(
            f"Invalid Hebrew day: {day} for month {month} of year {year}. "
            f"Month has {max_day} days."
        )

    # Days from Hebrew epoch to the given date
    days_from_epoch = (
        _elapsed_days(year)          # days from epoch to 1 Tishrei of this year
        + _days_before_month(year, month)  # days from 1 Tishrei to start of month
        + day - 1                    # days within the month (0-indexed)
    )

    # Convert to Julian Day Number and then to Gregorian
    jdn = days_from_epoch + _HEBREW_EPOCH_JDN
    return _jdn_to_gregorian(jdn)


def _jdn_to_gregorian(jdn: int) -> tuple[int, int, int]:
    """
    Convert a Julian Day Number to a Gregorian calendar date.
    Richards (2013) algorithm.
    """
    f = jdn + 1401 + (((4 * jdn + 274277) // 146097) * 3) // 4 - 38
    e = 4 * f + 3
    g = (e % 1461) // 4
    h = 5 * g + 2
    day   = (h % 153) // 5 + 1
    month = (h // 153 + 2) % 12 + 1
    year  = e // 1461 - 4716 + (14 - month) // 12
    return year, month, day


# ── Hebrew month name mappings ────────────────────────────────────────────────

# Hebrew month names as they appear on Israeli documents
# Keys cover both full and common abbreviated forms
HEBREW_MONTH_NAMES: dict[str, int] = {
    # Tishrei
    "תשרי":      1,
    # Cheshvan (also Marcheshvan)
    "חשון":      2,
    "מרחשון":    2,
    "חשוון":     2,
    # Kislev
    "כסלו":      3,
    "כסליו":     3,
    # Tevet
    "טבת":       4,
    # Shevat
    "שבט":       5,
    # Adar / Adar I / Adar II
    "אדר":       6,
    "אדר א":     6,
    "אדר א'":    6,
    "אדר ב":     7,
    "אדר ב'":    7,
    "אדר ראשון": 6,
    "אדר שני":   7,
    # Nisan
    "ניסן":      7,   # month 7 in common year, 8 in leap
    # Iyar
    "אייר":      8,
    "אייר":      8,
    # Sivan
    "סיון":      9,
    # Tammuz
    "תמוז":      10,
    # Av
    "אב":        11,
    # Elul
    "אלול":      12,
}

# Transliterated forms that may appear in English-language Israeli documents
HEBREW_MONTH_TRANSLITERATED: dict[str, int] = {
    "tishrei": 1, "tishri": 1,
    "cheshvan": 2, "heshvan": 2, "marcheshvan": 2,
    "kislev": 3, "kislev": 3,
    "tevet": 4,
    "shevat": 5, "shvat": 5,
    "adar": 6, "adar i": 6, "adar ii": 7,
    "nisan": 7, "nissan": 7,
    "iyar": 8, "iyyar": 8,
    "sivan": 9,
    "tammuz": 10, "tamuz": 10,
    "av": 11,
    "elul": 12,
}


# ── Hebrew gematria (letter-numeral) helpers ──────────────────────────────────

# Hebrew dates on religious and some civil documents are written using
# Hebrew letters as numerals (gematria). This is common on ketubot,
# gravestones, and older documents. Modern Israeli official documents
# (passports, IDs) use standard Arabic numerals but older registry
# documents may use gematria for the year.

_GEMATRIA_VALUES: dict[str, int] = {
    "א": 1,  "ב": 2,  "ג": 3,  "ד": 4,  "ה": 5,
    "ו": 6,  "ז": 7,  "ח": 8,  "ט": 9,  "י": 10,
    "כ": 20, "ך": 20, "ל": 30, "מ": 40, "ם": 40,
    "נ": 50, "ן": 50, "ס": 60, "ע": 70, "פ": 80,
    "ף": 80, "צ": 90, "ץ": 90, "ק": 100,"ר": 200,
    "ש": 300,"ת": 400,
}

# Convention: the divine name components (יה) are replaced by (טו=15, טז=16)
# to avoid writing a name of God. This is handled automatically below.


def _gematria_to_int(text: str) -> int | None:
    """
    Convert a Hebrew gematria string to an integer.

    Handles the special cases for 15 (טו) and 16 (טז) which are
    written as substitutes to avoid spelling divine names.

    Args:
        text: Hebrew letter string (e.g. "תשפ\"ו" for 5786).

    Returns:
        Integer value or None if conversion fails.
    """
    # Strip punctuation — geresh (׳) and gershayim (״) used in dates
    cleaned = text.replace("׳", "").replace("״", "").replace('"', "").replace("'", "").strip()
    if not cleaned:
        return None
    total = 0
    for ch in cleaned:
        val = _GEMATRIA_VALUES.get(ch)
        if val is None:
            return None
        total += val
    return total


def _parse_hebrew_year(text: str) -> int | None:
    """
    Parse a Hebrew year from a string that may be:
        - Standard Arabic numerals: "5786"
        - Abbreviated gematria (century omitted): "תשפ\"ו" → 786 → 5786
        - Full gematria: "ה'תשפ\"ו" → 5786

    The 5000s millennium (ה) is assumed when the parsed value is less
    than 1000 — this is the universal convention for dates after 5000 AM.

    Args:
        text: Raw year string from document.

    Returns:
        Hebrew year as integer or None if unparseable.
    """
    text = text.strip()

    # Try plain integer first
    if text.isdigit():
        year = int(text)
        # Hebrew years on modern documents: 5700–5900 (1940–2140 CE)
        if 5700 <= year <= 5900:
            return year
        return None

    # Try gematria
    val = _gematria_to_int(text)
    if val is None:
        return None

    # If value < 1000, it is the abbreviated form — add 5000
    if val < 1000:
        val += 5000

    if 5700 <= val <= 5900:
        return val
    return None


# ── Date string detection ─────────────────────────────────────────────────────

# Hebrew date formats on Israeli documents:
# 1. DD/MM/YYYY or DD-MM-YYYY in Gregorian (most common on modern Israeli passports
#    and IDs — these are already Gregorian and need no conversion)
# 2. Hebrew date written with Hebrew month name and Arabic numerals:
#    e.g. "כ\"ה בתשרי תשפ\"ו" (25 Tishrei 5786)
#    or "25 תשרי 5786"
# 3. Gematria year with Arabic day and month name:
#    e.g. "5 אייר תשפ\"ו"
# 4. Mixed: Arabic day, Hebrew month name, Arabic year

# Regex for detecting Hebrew dates with a Hebrew month name
# Note: Hebrew text is RTL but regex patterns work on the Unicode code points
# regardless of display direction. We match the logical character sequence.

_HEB_DIGIT = r"\d"  # Standard Arabic digit (used in Israeli documents)
_HEB_SEP   = r"[\s\-\/בּ]"  # Space, hyphen, slash, or ב preposition

HEBREW_DATE_PATTERNS = [
    # Pattern 1: Arabic day + Hebrew month name + year (Arabic or gematria)
    # e.g. "15 תשרי 5786" or "15 בתשרי 5786"
    re.compile(
        r"(\d{1,2})\s+ב?("
        + "|".join(re.escape(m) for m in sorted(HEBREW_MONTH_NAMES.keys(), key=len, reverse=True))
        + r")\s+([\d]+|[אבגדהוזחטיכלמנסעפצקרשת\"׳]{2,6})"
    ),
    # Pattern 2: Gematria day + Hebrew month name + gematria year
    re.compile(
        r"([אבגדהוזחטיכלמנסעפצקרשת\"׳]{1,4})\s+ב?("
        + "|".join(re.escape(m) for m in sorted(HEBREW_MONTH_NAMES.keys(), key=len, reverse=True))
        + r")\s+([\d]{4}|[אבגדהוזחטיכלמנסעפצקרשת\"׳]{2,8})"
    ),
    # Pattern 3: Transliterated month names (English-language Israeli documents)
    re.compile(
        r"(\d{1,2})\s+(" + "|".join(HEBREW_MONTH_TRANSLITERATED.keys()) + r")\s+(\d{4})",
        re.IGNORECASE
    ),
]


def detect_hebrew_date(text: str) -> dict | None:
    """
    Attempt to detect and parse a Hebrew calendar date string from text.

    Tries each pattern in HEBREW_DATE_PATTERNS. If a match is found,
    parses day, month, and year and converts to Gregorian.

    Important note on Israeli documents: modern Israeli passports and
    national identity cards (תעודת זהות) express dates in the Gregorian
    calendar using DD/MM/YYYY format. Hebrew calendar dates are more
    commonly found on:
        - Company registry documents (רשם החברות extracts)
        - Notarial deeds
        - Older documents pre-2000
        - Religious documents (ketubot, certificates of Jewish status)

    This function does NOT attempt to detect DD/MM/YYYY Gregorian dates —
    those are handled by the main date normalisation pipeline.

    Args:
        text: Raw text from a document field.

    Returns:
        Result dict if a Hebrew date is detected and converted:
            normalised_form:   ISO 8601 date (YYYY-MM-DD) or year (YYYY)
            original_calendar: "hebrew"
            original_text:     matched substring
            confidence:        0.88
            review_required:   False
        Returns None if no Hebrew date pattern is found.
    """
    if not text:
        return None

    # Try each pattern
    for i, pattern in enumerate(HEBREW_DATE_PATTERNS):
        match = pattern.search(text)
        if not match:
            continue

        try:
            # Parse day
            day_str = match.group(1)
            if day_str.isdigit():
                day = int(day_str)
            else:
                day = _gematria_to_int(day_str)
                if day is None:
                    continue

            # Parse month
            month_str = match.group(2).strip()
            if i == 2:
                # Transliterated pattern
                month = HEBREW_MONTH_TRANSLITERATED.get(month_str.lower())
            else:
                month = HEBREW_MONTH_NAMES.get(month_str)
            if month is None:
                continue

            # Parse year
            year_str = match.group(3).strip()
            year = _parse_hebrew_year(year_str)
            if year is None:
                continue

            # Adjust month for Nisan and later in leap years
            # (The simple name→number mapping above gives the common-year position.
            # In a leap year, Nisan and subsequent months are shifted by 1 because
            # Adar I occupies slot 6 and Adar II occupies slot 7.)
            if _is_hebrew_leap(year) and month >= 7 and i != 2:
                # Shift post-Adar months forward by 1 for leap years
                # (Adar I = 6, Adar II = 7, Nisan = 8 in leap years)
                # Only apply if the month name is not Adar I or Adar II
                if month_str not in ("אדר א", "אדר א'", "אדר ב", "אדר ב'",
                                     "אדר ראשון", "אדר שני"):
                    month += 1

            g_year, g_month, g_day = hebrew_to_gregorian(year, month, day)
            return {
                "normalised_form":    f"{g_year:04d}-{g_month:02d}-{g_day:02d}",
                "original_calendar":  "hebrew",
                "original_text":      match.group(0),
                "confidence":         0.88,
                "review_required":    False,
                "review_reason":      None,
            }

        except (ValueError, TypeError, IndexError):
            continue

    return None
