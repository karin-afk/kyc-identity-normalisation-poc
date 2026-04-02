_SCRIPT_RANGES = {
    "Arabic":    (0x0600, 0x06FF),
    "Cyrillic":  (0x0400, 0x04FF),
    "Han":       (0x4E00, 0x9FFF),
    "Hiragana":  (0x3040, 0x309F),
    "Katakana":  (0x30A0, 0x30FF),
    "Greek":     (0x0370, 0x03FF),
    "Latin":     (0x0041, 0x007A),
}


def detect_script(text: str) -> str:
    """Return the dominant Unicode script name found in text."""
    counts: dict[str, int] = {s: 0 for s in _SCRIPT_RANGES}
    for ch in text:
        cp = ord(ch)
        for script, (lo, hi) in _SCRIPT_RANGES.items():
            if lo <= cp <= hi:
                counts[script] += 1
    if not any(counts.values()):
        return "Latin"
    return max(counts, key=lambda s: counts[s])


# ---------------------------------------------------------------------------
# Belarusian detection
# ---------------------------------------------------------------------------

# Characters exclusive to (or mandatory in) Belarusian Cyrillic.
# Ў (U+040E / U+045E) does not appear in Russian or Ukrainian.
BELARUSIAN_EXCLUSIVE_CHARS: frozenset[str] = frozenset({"Ў", "ў", "Ё", "ё"})


def detect_belarusian(text: str) -> bool:
    """Return True if ``text`` contains a definitive Belarusian Cyrillic marker.

    Ў / ў (Short U, U+040E / U+045E) is exclusive to Belarusian and does not
    appear in Russian or Ukrainian. Its presence is a definitive indicator that
    the text uses the Belarusian Cyrillic script.

    Args:
        text: Input string to inspect.

    Returns:
        ``True`` if Ў or ў is found; ``False`` otherwise.
    """
    return any(ch in ("Ў", "ў") for ch in text)

