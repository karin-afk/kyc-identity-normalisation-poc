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
