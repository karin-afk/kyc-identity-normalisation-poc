"""Han numeral utilities for KYC field normalisation (T12-2).

Two conversion modes:
- Spoken digit mode:  一三八〇〇 → "13800"  (phone numbers, spoken years)
- Positional mode:    五千 → 5000, 八十八 → 88  (amounts, house numbers)

All functions are deterministic and make no external calls.
"""

# Han spoken-digit characters → ASCII digit string
_HAN_SPOKEN: dict[str, str] = {
    "〇": "0", "零": "0",
    "一": "1", "二": "2", "三": "3", "四": "4", "五": "5",
    "六": "6", "七": "7", "八": "8", "九": "9",
}

# Han positional multipliers
_HAN_MULT: dict[str, int] = {
    "十": 10, "百": 100, "千": 1000,
    "万": 10000, "萬": 10000,
    "億": 100000000,
}

# Union of all recognised Han numeral characters
_ALL_HAN: frozenset[str] = frozenset(_HAN_SPOKEN) | frozenset(_HAN_MULT)


def is_pure_han_numeral(text: str) -> bool:
    """Return True if every character in *text* is a Han numeral (digit or multiplier)."""
    return bool(text) and all(c in _ALL_HAN for c in text)


def is_pure_han_spoken(text: str) -> bool:
    """Return True if every character is a Han spoken digit (no multipliers).

    Useful for identifying spoken-digit phone numbers / years like 一三八〇〇.
    """
    return bool(text) and all(c in _HAN_SPOKEN for c in text)


def han_spoken_to_str(text: str) -> str | None:
    """Convert a spoken-digit Han string to an ASCII digit string.

    Returns None if any character is not a Han spoken digit.

    Example:
        han_spoken_to_str("一三八〇〇") → "13800"
    """
    if not text:
        return None
    result = []
    for c in text:
        if c not in _HAN_SPOKEN:
            return None
        result.append(_HAN_SPOKEN[c])
    return "".join(result)


def han_to_int(text: str) -> int | None:
    """Convert a Han numeral string to an integer.

    Auto-selects the appropriate mode:
    - If contains multipliers (十百千万億): positional mode.
    - Otherwise: spoken-digit mode (each char → digit, concatenate).

    Returns None if the string cannot be parsed (unknown characters or overflow).

    Examples:
        han_to_int("五千")       → 5000
        han_to_int("八十八")     → 88
        han_to_int("一三八〇〇") → 13800
        han_to_int("二零二四")   → 2024
    """
    if not text:
        return None
    if any(c in _HAN_MULT for c in text):
        return _han_positional(text)
    spoken = han_spoken_to_str(text)
    if spoken is None:
        return None
    try:
        return int(spoken)
    except ValueError:
        return None


def _han_positional(text: str) -> int | None:
    """Parse positional Han numerals.

    Algorithm:
        result  — accumulated high-order total
        current — coefficient of the next multiplier

    Examples:
        五千      → current=5; 千: result=5000; total=5000
        八十八    → current=8; 十: result=80; current=8; total=88
        十四      → current=0→1 implied; 十: result=10; current=4; total=14
        一万五千  → current=1; 万: result=10000; current=5; 千: result=15000
    """
    result = 0
    current = 0
    for c in text:
        if c in _HAN_SPOKEN:
            current = int(_HAN_SPOKEN[c])
        elif c in _HAN_MULT:
            mult = _HAN_MULT[c]
            coeff = current if current > 0 else 1
            if mult in (10000, 100000000):
                # High-order multiplier: collapses everything accumulated so far
                result = (result + coeff) * mult
            else:
                result += coeff * mult
            current = 0
        else:
            return None  # unexpected character
    result += current
    return result if result >= 0 else None
