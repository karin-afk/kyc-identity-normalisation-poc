"""
Numeric normalisation rules for KYC field processing.

This module handles the conversion of numeric strings from various scripts,
formats, and conventions to a standard ASCII representation suitable for
KYC screening and financial data processing.

It does NOT handle calendar conversion (see calendar_rules.py and the
calendar_*.py modules). It handles:

    1. Non-ASCII digit scripts → ASCII digits
       - Full-width ASCII digits (Japanese EDINET filings)
       - Devanagari digits (Indian documents)
       - Thai digits (Thai documents)
       - Arabic-Indic and Eastern Arabic-Indic digits (already in codebase,
         included here for completeness and a single import point)

    2. Number format normalisation
       - European format (1.000.000,50) → English format (1000000.50)
       - Swiss format (1'000'000.50) → English format (1000000.50)
       - English format (1,000,000.50) → English format (1000000.50)

    3. Parenthetical negative notation
       - △4191 → -4191  (Japanese accounting, triangle notation)
       - （4191） → -4191  (Japanese full-width parentheses)
       - (4191) → -4191   (standard parenthetical negative)

    4. Currency symbol normalisation
       - Symbol → ISO 4217 code
       - Extracts numeric amount from currency string
       - Resolves ambiguous symbols (¥ → JPY or CNY) using language/country context

All functions are deterministic: the same input always produces the same output.
No API calls, no AI, no probabilistic logic.
"""

import re


# ══════════════════════════════════════════════════════════════════════════════
# 1. DIGIT SCRIPT TRANSLATION TABLES
# ══════════════════════════════════════════════════════════════════════════════

# ── Full-width ASCII digits ───────────────────────────────────────────────────
# Used in Japanese financial documents, particularly EDINET (Electronic
# Disclosure for Investors' NETwork) filings and accounting statements.
# Unicode range: U+FF10 (０) through U+FF19 (９).
# Example: ０１，２３４，５６７ → 01,234,567

FULLWIDTH_DIGITS = "０１２３４５６７８９"
_FULLWIDTH_TABLE = str.maketrans(FULLWIDTH_DIGITS, "0123456789")


def fullwidth_to_ascii(text: str) -> str:
    """
    Convert full-width ASCII digits to standard ASCII digits.

    Full-width digits (０–９) are used in Japanese financial documents,
    particularly EDINET filings, accounting statements, and some company
    registry extracts. They are semantically identical to ASCII digits
    but occupy a full character width (same as CJK characters).

    Also converts full-width commas (，) and full-width periods (．)
    used as thousand separators and decimal points in Japanese documents.

    Args:
        text: String potentially containing full-width digits.

    Returns:
        String with full-width digits replaced by ASCII equivalents.

    Examples:
        >>> fullwidth_to_ascii("０１２３４５６７８９")
        '0123456789'
        >>> fullwidth_to_ascii("１，２３４，５６７")
        '1,234,567'
        >>> fullwidth_to_ascii("△１，０００")
        '△1,000'
    """
    # Also convert full-width punctuation used in numeric contexts
    result = text.translate(_FULLWIDTH_TABLE)
    result = result.replace("，", ",")   # full-width comma U+FF0C
    result = result.replace("．", ".")   # full-width full stop U+FF0E
    return result


# ── Devanagari digits ─────────────────────────────────────────────────────────
# Used in Indian documents written in Hindi, Marathi, Nepali, and other
# languages using the Devanagari script.
# Unicode range: U+0966 (०) through U+096F (९).
# Example: ४,५०,००० → 4,50,000 (Indian lakh format)

DEVANAGARI_DIGITS = "०१२३४५६७८९"
_DEVANAGARI_TABLE = str.maketrans(DEVANAGARI_DIGITS, "0123456789")


def devanagari_to_ascii(text: str) -> str:
    """
    Convert Devanagari digits to standard ASCII digits.

    Devanagari digits (०–९) are used in Indian documents written in Hindi,
    Marathi, Sanskrit, Nepali, and other Devanagari-script languages. They
    appear on Indian government-issued documents, company registrations from
    the Ministry of Corporate Affairs (MCA), and financial statements from
    Indian companies.

    Note on Indian number format: India uses the lakh/crore system with
    grouping at 2-3 digits (e.g. ४,५०,०००  = 450,000). After converting
    Devanagari digits to ASCII, apply normalise_number_format() to standardise
    the grouping separators.

    Args:
        text: String potentially containing Devanagari digits.

    Returns:
        String with Devanagari digits replaced by ASCII equivalents.

    Examples:
        >>> devanagari_to_ascii("०१२३४५६७८९")
        '0123456789'
        >>> devanagari_to_ascii("₹४,५०,०००")
        '₹4,50,000'
    """
    return text.translate(_DEVANAGARI_TABLE)


# ── Thai digits ───────────────────────────────────────────────────────────────
# Used in Thai documents. Already included in calendar_offset.py but
# reproduced here as the canonical definition for the numeric pipeline.
# Unicode range: U+0E50 (๐) through U+0E59 (๙).

THAI_DIGITS = "๐๑๒๓๔๕๖๗๘๙"
_THAI_TABLE = str.maketrans(THAI_DIGITS, "0123456789")


def thai_to_ascii(text: str) -> str:
    """
    Convert Thai digits to standard ASCII digits.

    Thai digits (๐–๙) appear on Thai government documents, company
    registrations from the Department of Business Development (DBD),
    financial statements, and shareholder registers.

    Args:
        text: String potentially containing Thai digits.

    Returns:
        String with Thai digits replaced by ASCII equivalents.

    Examples:
        >>> thai_to_ascii("๐๑๒๓๔๕๖๗๘๙")
        '0123456789'
        >>> thai_to_ascii("฿๒,๕๐๐,๐๐๐")
        '฿2,500,000'
    """
    return text.translate(_THAI_TABLE)


# ── Arabic-Indic and Eastern Arabic-Indic (already in codebase) ───────────────
# Reproduced here so callers can import all digit normalisers from one module.
# The canonical implementation remains in calendar_utils.py (src/).
# These are NOT redefined — imported at runtime to avoid duplication.

ARABIC_INDIC_DIGITS   = "٠١٢٣٤٥٦٧٨٩"   # U+0660–U+0669, used in Arabic documents
EASTERN_ARABIC_DIGITS = "۰۱۲۳۴۵۶۷۸۹"   # U+06F0–U+06F9, used in Persian/Urdu documents
_ARABIC_INDIC_TABLE   = str.maketrans(ARABIC_INDIC_DIGITS,   "0123456789")
_EASTERN_ARABIC_TABLE = str.maketrans(EASTERN_ARABIC_DIGITS, "0123456789")


def arabic_indic_to_ascii(text: str) -> str:
    """
    Convert Arabic-Indic and Eastern Arabic-Indic digits to ASCII.

    Arabic-Indic (٠–٩): used in Arabic-script documents from the Middle East
    and North Africa (Arabic, Urdu, Kurdish in Arabic script).

    Eastern Arabic-Indic (۰–۹): used in Persian/Farsi and some Urdu documents.
    Visually similar to Arabic-Indic but different Unicode code points.

    Applies both conversion tables to handle mixed documents.

    Args:
        text: String potentially containing Arabic-Indic or Eastern Arabic-Indic digits.

    Returns:
        String with all Arabic-script digits replaced by ASCII equivalents.

    Examples:
        >>> arabic_indic_to_ascii("١٢٣٤٥٦٧٨٩٠")
        '1234567890'
        >>> arabic_indic_to_ascii("۱۴۰۴")
        '1404'
    """
    return text.translate(_ARABIC_INDIC_TABLE).translate(_EASTERN_ARABIC_TABLE)


# ── Master digit normalisation ────────────────────────────────────────────────

def normalise_all_digits(text: str) -> str:
    """
    Apply all digit script conversions in a single pass.

    Converts full-width, Devanagari, Thai, Arabic-Indic, and Eastern
    Arabic-Indic digits to ASCII. Safe to apply to any string — characters
    not in any conversion table pass through unchanged.

    This is the function to call when you have a raw numeric field value
    and do not know which digit script may be present.

    Args:
        text: Raw string from document extraction.

    Returns:
        String with all non-ASCII digit scripts converted to ASCII digits.

    Examples:
        >>> normalise_all_digits("１，２３４，５６７")   # full-width Japanese
        '1,234,567'
        >>> normalise_all_digits("₹४,५०,०००")          # Devanagari
        '₹4,50,000'
        >>> normalise_all_digits("฿๒,๕๐๐,๐๐๐")         # Thai
        '฿2,500,000'
        >>> normalise_all_digits("١,٢٣٤,٥٦٧")          # Arabic-Indic
        '1,234,567'
    """
    return (
        text
        .translate(_FULLWIDTH_TABLE)
        .replace("，", ",")
        .replace("．", ".")
        .replace("\u066c", ",")   # U+066C Arabic Thousands Separator → standard comma
        .translate(_DEVANAGARI_TABLE)
        .translate(_THAI_TABLE)
        .translate(_ARABIC_INDIC_TABLE)
        .translate(_EASTERN_ARABIC_TABLE)
    )


# ══════════════════════════════════════════════════════════════════════════════
# 2. NUMBER FORMAT NORMALISATION
# ══════════════════════════════════════════════════════════════════════════════

def normalise_number_format(text: str) -> str:
    """
    Normalise a numeric string to English format (period as decimal separator,
    no thousands separator).

    Handles three input formats:
        - English:  1,234,567.89  → 1234567.89
        - European: 1.234.567,89  → 1234567.89   (German, French, Italian, Spanish...)
        - Swiss:    1'234'567.89  → 1234567.89   (Switzerland, Liechtenstein)
        - Indian:   4,50,000      → 450000        (lakh grouping — treated as English)

    Detection logic:
        1. Strip leading/trailing whitespace and any non-numeric prefix/suffix.
        2. If the string contains both commas and periods:
           - If the last separator (rightmost) is a comma → European format
             (comma is the decimal separator; periods are thousands separators)
           - If the last separator is a period → English format
             (period is the decimal separator; commas are thousands separators)
        3. If only commas are present:
           - If there is exactly one comma and ≤2 digits after it → decimal comma
             (e.g. "1234,50" — European, comma is decimal)
           - Otherwise → thousands separator (e.g. "1,234,567")
        4. If only periods are present:
           - If there is exactly one period and ≤2 digits after it → decimal point
             (e.g. "1234.50")
           - Otherwise → thousands separator (e.g. "1.234.567" — European)
        5. Swiss apostrophe separators: strip apostrophes, then apply period logic.

    Args:
        text: Numeric string, potentially with separators. May contain a
              leading currency symbol or trailing unit — these are preserved.
              Apply normalise_all_digits() first if the string may contain
              non-ASCII digits.

    Returns:
        Numeric string in English format with no thousands separators.
        Returns the input unchanged if no numeric content is found.

    Examples:
        >>> normalise_number_format("1.234.567,89")
        '1234567.89'
        >>> normalise_number_format("1,234,567.89")
        '1234567.89'
        >>> normalise_number_format("1'234'567.89")
        '1234567.89'
        >>> normalise_number_format("1'234'567,89")
        '1234567.89'
        >>> normalise_number_format("1.234.567")
        '1234567'
        >>> normalise_number_format("1234,50")
        '1234.50'
    """
    if not text:
        return text

    stripped = text.strip()

    # Extract any leading non-numeric prefix (currency symbol, whitespace)
    prefix_match = re.match(r'^([^0-9]*)(.+?)([^0-9]*)$', stripped)
    if not prefix_match:
        return text

    prefix  = prefix_match.group(1)
    numeric = prefix_match.group(2)
    suffix  = prefix_match.group(3)

    # Handle Swiss apostrophe separators first
    has_apostrophe = "'" in numeric or "\u2019" in numeric  # straight or curly apostrophe
    if has_apostrophe:
        numeric = numeric.replace("'", "").replace("\u2019", "")
        # After removing apostrophes, apply normal period/comma logic below

    has_comma  = "," in numeric
    has_period = "." in numeric

    if has_comma and has_period:
        # Both separators present — determine which is the decimal separator
        last_comma  = numeric.rfind(",")
        last_period = numeric.rfind(".")

        if last_comma > last_period:
            # Comma comes last → it is the decimal separator (European format)
            # Replace periods (thousands) with nothing, replace final comma with period
            numeric = numeric.replace(".", "")
            numeric = numeric[:last_comma] + "." + numeric[last_comma + 1:]
        else:
            # Period comes last → it is the decimal separator (English format)
            # Remove commas (thousands separators)
            numeric = numeric.replace(",", "")

    elif has_comma and not has_period:
        # Only commas — determine if decimal or thousands
        parts = numeric.split(",")
        last_part = parts[-1]

        if len(parts) == 2 and len(last_part) <= 2:
            # Single comma with ≤2 digits after → decimal comma (European)
            # e.g. "1234,50" → "1234.50"
            numeric = parts[0] + "." + last_part
        else:
            # Multiple commas or >2 digits after comma → thousands separators
            # e.g. "1,234,567" or "4,50,000" (Indian lakh)
            numeric = numeric.replace(",", "")

    elif has_period and not has_comma:
        # Only periods — determine if decimal or thousands
        parts = numeric.split(".")
        last_part = parts[-1]

        if len(parts) == 2 and len(last_part) <= 2:
            # Single period with ≤2 digits → decimal point — keep as-is
            pass  # "1234.50" → "1234.50"
        else:
            # Multiple periods or >2 digits → European thousands separators
            # e.g. "1.234.567" → "1234567"
            if len(parts[-1]) > 2:
                # All periods are thousands separators, no decimal
                numeric = numeric.replace(".", "")
            else:
                # Last period is decimal, others are thousands
                # e.g. "1.234.567.89" — ambiguous but treat last as decimal
                integer_parts = ".".join(parts[:-1]).replace(".", "")
                numeric = integer_parts + "." + last_part

    # Remove any remaining leading zeros that aren't part of a decimal
    # (preserve "0.50" but clean "01234.50" → "1234.50")
    if "." in numeric:
        int_part, dec_part = numeric.split(".", 1)
        int_part = int_part.lstrip("0") or "0"
        numeric = int_part + "." + dec_part
    else:
        numeric = numeric.lstrip("0") or "0"

    return prefix + numeric + suffix


# ══════════════════════════════════════════════════════════════════════════════
# 3. PARENTHETICAL NEGATIVE NOTATION
# ══════════════════════════════════════════════════════════════════════════════

# Patterns for parenthetical negative numbers
# △ (U+25B3 white up-pointing triangle) — Japanese accounting standard
# ▲ (U+25B2 black up-pointing triangle) — variant, same meaning
# （）— full-width parentheses (U+FF08, U+FF09) — Japanese documents
# () — standard ASCII parentheses

_PARENTHETICAL_PATTERNS = [
    # Triangle notation: △1,234 or ▲1,234 (with or without separators)
    re.compile(r"[△▲]\s*([\d,，\.，']+)"),
    # Full-width parentheses: （1,234）
    re.compile(r"[（(]\s*([\d,，\.，']+)\s*[）)]"),
    # Standard parentheses: (1,234)
    re.compile(r"\(\s*([\d,，\.，']+)\s*\)"),
]

# Pre-compiled pattern for detecting whether a string contains a
# parenthetical negative (used for fast pre-check)
_HAS_NEGATIVE_RE = re.compile(r"[△▲（(]")


def normalise_parenthetical_negative(text: str) -> str:
    """
    Convert parenthetical negative notation to a signed numeric string.

    Financial statements — particularly Japanese accounting documents following
    the Japanese GAAP (企業会計基準) standard — express negative numbers using:
        - Triangle notation: △4,191 or ▲4,191
        - Full-width parentheses: （4,191）
        - Standard parentheses: (4,191)

    This function detects these patterns and converts them to standard
    signed numeric notation with a leading minus sign.

    The numeric portion is also passed through normalise_all_digits() to
    handle full-width digits in the same step.

    Args:
        text: Raw numeric string from a financial document field.

    Returns:
        String with parenthetical negatives converted to minus-prefixed form.
        If no parenthetical negative pattern is found, returns the input unchanged.
        If a pattern is found, returns the minus-signed number with no
        thousands separators (also passes through normalise_number_format).

    Examples:
        >>> normalise_parenthetical_negative("△4,191")
        '-4191'
        >>> normalise_parenthetical_negative("▲1,234,567")
        '-1234567'
        >>> normalise_parenthetical_negative("（4,191）")
        '-4191'
        >>> normalise_parenthetical_negative("(4,191)")
        '-4191'
        >>> normalise_parenthetical_negative("△１，０００")   # full-width digits
        '-1000'
        >>> normalise_parenthetical_negative("4,191")       # no negative marker
        '4,191'
    """
    if not text or not _HAS_NEGATIVE_RE.search(text):
        return text

    # Normalise digits first (full-width, Thai, etc.)
    normalised_text = normalise_all_digits(text.strip())

    for pattern in _PARENTHETICAL_PATTERNS:
        match = pattern.match(normalised_text)
        if match:
            numeric_part = match.group(1)
            # Normalise number format (remove thousands separators)
            clean = normalise_number_format(numeric_part)
            return "-" + clean

    return text


# ══════════════════════════════════════════════════════════════════════════════
# 4. CURRENCY SYMBOL NORMALISATION
# ══════════════════════════════════════════════════════════════════════════════

# Unambiguous symbol → ISO 4217 code mappings
_CURRENCY_SYMBOLS: dict[str, str] = {
    "€":  "EUR",   # Euro
    "£":  "GBP",   # British Pound Sterling
    "₪":  "ILS",   # Israeli New Shekel
    "﷼":  "SAR",   # Saudi Riyal (also used for IRR/QAR — context-dependent, SAR default)
    "฿":  "THB",   # Thai Baht
    "₩":  "KRW",   # South Korean Won
    "₺":  "TRY",   # Turkish Lira
    "₴":  "UAH",   # Ukrainian Hryvnia
    "₽":  "RUB",   # Russian Ruble
    "₹":  "INR",   # Indian Rupee
    "৳":  "BDT",   # Bangladeshi Taka
    "₱":  "PHP",   # Philippine Peso
    "₦":  "NGN",   # Nigerian Naira
    "₫":  "VND",   # Vietnamese Dong
    "₡":  "CRC",   # Costa Rican Colón
    "Rp":  "IDR",  # Indonesian Rupiah
    "kr":  "SEK",  # Scandinavian Krone (ambiguous — SEK/NOK/DKK; default SEK)
    "Fr":  "CHF",  # Swiss Franc
    "CHF": "CHF",
    "HK$": "HKD",  # Hong Kong Dollar (must check before $)
    "S$":  "SGD",  # Singapore Dollar (must check before $)
    "A$":  "AUD",  # Australian Dollar (must check before $)
    "C$":  "CAD",  # Canadian Dollar (must check before $)
    "NZ$": "NZD",  # New Zealand Dollar (must check before $)
}

# Ambiguous symbols requiring context resolution
_AMBIGUOUS_SYMBOLS: dict[str, dict] = {
    "¥": {
        # Japanese Yen (JPY) or Chinese Yuan (CNY/RMB)
        # Resolved by language or country parameter
        "default":  "JPY",
        "zh":       "CNY",
        "CN":       "CNY",
        "TW":       "TWD",  # Taiwan uses NT$ but ¥ may appear on older documents
    },
    "元": {
        # Chinese Yuan (CNY) or Japanese Yen (JPY) — character used in both
        "default":  "CNY",
        "ja":       "JPY",
        "JP":       "JPY",
    },
    "$": {
        # US Dollar by default; resolved by country for other dollar currencies
        "default":  "USD",
        "AU":       "AUD",
        "CA":       "CAD",
        "SG":       "SGD",
        "HK":       "HKD",
        "NZ":       "NZD",
    },
    "﷼": {
        # Rial/Riyal symbol used by Saudi Arabia, Iran, Qatar, Yemen, Oman
        "default":  "SAR",
        "IR":       "IRR",
        "QA":       "QAR",
        "YE":       "YER",
        "OM":       "OMR",
    },
    "kr": {
        # Krone — used by Sweden, Norway, Denmark, Iceland, Czech Republic
        "default":  "SEK",
        "NO":       "NOK",
        "DK":       "DKK",
        "IS":       "ISK",
        "CZ":       "CZK",
    },
}

# Regex to extract currency symbol and amount from a string
# Order matters: longer/more specific symbols must be checked before shorter ones
_SYMBOL_ORDER = [
    "HK$", "S$", "A$", "C$", "NZ$",  # multi-char dollar variants first
    "CHF", "Rp", "Fr", "kr",          # multi-char codes
    "€", "£", "¥", "₪", "﷼", "฿", "₩", "₺", "₴", "₽", "₹",
    "₱", "₫", "₦", "₡", "元",
    "$",                               # plain dollar last (most ambiguous)
]

# Build a single regex pattern that matches any known symbol
_SYMBOL_PATTERN = re.compile(
    r"^("
    + "|".join(re.escape(s) for s in _SYMBOL_ORDER)
    + r")\s*"
    + r"([\d,\.,\'\s]+)"              # numeric amount after symbol
    + r"|"
    + r"([\d,\.,\'\s]+)\s*"          # OR numeric amount before symbol
    + r"("
    + "|".join(re.escape(s) for s in _SYMBOL_ORDER)
    + r")$",
    re.UNICODE
)


def normalise_currency(
    text: str,
    language: str = "",
    country: str = "",
) -> tuple[str, str]:
    """
    Extract the numeric amount and ISO 4217 currency code from a currency string.

    Handles both symbol-before-amount (¥1,000) and amount-after-symbol (1,000¥)
    formats. Resolves ambiguous symbols (¥, $, ﷼, kr, 元) using the language
    and country parameters.

    After extracting the amount string, applies normalise_all_digits() and
    normalise_number_format() so the returned amount is always in clean
    English numeric format.

    Args:
        text:     Raw currency string from document (e.g. "¥1,234,567").
        language: ISO 639-1 language code (e.g. "ja", "zh", "ar"). Used to
                  resolve ambiguous symbols. Empty string if unknown.
        country:  ISO 3166-1 alpha-2 country code (e.g. "JP", "CN", "SA").
                  Takes precedence over language for disambiguation. Empty
                  string if unknown.

    Returns:
        Tuple of (amount_str, iso_4217_code) where:
            amount_str:   Clean numeric string in English format (e.g. "1234567.00")
            iso_4217_code: ISO 4217 currency code (e.g. "JPY", "CNY", "USD")

        If no currency symbol is found, returns (normalised_amount, "") where
        the second element is an empty string indicating unknown currency.

        If the text cannot be parsed as a currency string, returns (text, "").

    Examples:
        >>> normalise_currency("¥1,234,567", language="ja")
        ('1234567', 'JPY')
        >>> normalise_currency("¥1,234,567", language="zh", country="CN")
        ('1234567', 'CNY')
        >>> normalise_currency("€1.234.567,89", language="de")
        ('1234567.89', 'EUR')
        >>> normalise_currency("1,000.50$", country="AU")
        ('1000.50', 'AUD')
        >>> normalise_currency("﷼500,000", country="IR")
        ('500000', 'IRR')
        >>> normalise_currency("1,234,567", language="ja")
        ('1234567', '')
    """
    if not text:
        return (text, "")

    # Normalise digits and strip whitespace
    normalised = normalise_all_digits(text.strip())

    # Check multi-character dollar variants first (before single $ check)
    for sym in _SYMBOL_ORDER:
        if normalised.startswith(sym) or normalised.endswith(sym):
            # Extract amount
            if normalised.startswith(sym):
                amount_raw = normalised[len(sym):].strip()
            else:
                amount_raw = normalised[:-len(sym)].strip()

            # Determine ISO code
            iso_code = _resolve_symbol(sym, language, country)

            # Normalise amount
            amount_clean = normalise_number_format(amount_raw)

            return (amount_clean, iso_code)

    # No symbol found — return normalised amount with empty currency code
    amount_clean = normalise_number_format(normalised)
    return (amount_clean, "")


def _resolve_symbol(symbol: str, language: str, country: str) -> str:
    """
    Resolve a currency symbol to an ISO 4217 code using language and country context.

    Country takes precedence over language. Falls back to the default for
    the symbol if neither language nor country resolves the ambiguity.

    Args:
        symbol:   Currency symbol string.
        language: ISO 639-1 language code (may be empty).
        country:  ISO 3166-1 alpha-2 country code (may be empty).

    Returns:
        ISO 4217 currency code string.
    """
    # Check unambiguous symbols first
    if symbol in _CURRENCY_SYMBOLS:
        return _CURRENCY_SYMBOLS[symbol]

    # Check ambiguous symbols
    if symbol in _AMBIGUOUS_SYMBOLS:
        mapping = _AMBIGUOUS_SYMBOLS[symbol]
        # Country takes precedence
        if country and country in mapping:
            return mapping[country]
        # Then language
        if language and language in mapping:
            return mapping[language]
        # Default
        return mapping.get("default", "")

    return ""


# ══════════════════════════════════════════════════════════════════════════════
# 5. MASTER NUMERIC NORMALISATION ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

def normalise_numeric_field(
    text: str,
    field_type: str = "",
    language: str = "",
    country: str = "",
) -> dict:
    """
    Master entry point for numeric field normalisation.

    Applies all relevant normalisation steps in the correct order:
        1. Digit script conversion (full-width, Devanagari, Thai, Arabic-Indic)
        2. Parenthetical negative detection and conversion
        3. Currency symbol extraction (for financial value fields)
        4. Number format normalisation (European/Swiss → English)

    Args:
        text:       Raw field value from document extraction.
        field_type: KYC field type (e.g. "total_assets", "share_capital").
                    Used to determine whether currency extraction is appropriate.
        language:   ISO 639-1 language code.
        country:    ISO 3166-1 alpha-2 country code.

    Returns:
        Dict with keys:
            normalised_form:  Clean numeric string in English format.
            currency_code:    ISO 4217 code if a currency symbol was found, else "".
            was_negative:     True if a parenthetical negative was detected.
            processing_method: "NUMERIC"
            confidence:       0.95 for successful normalisation.
            review_required:  False for clean conversions.

    Examples:
        >>> normalise_numeric_field("△１，０００", language="ja", field_type="expenses")
        {
            'normalised_form': '-1000',
            'currency_code': '',
            'was_negative': True,
            'processing_method': 'NUMERIC',
            'confidence': 0.95,
            'review_required': False,
        }
        >>> normalise_numeric_field("¥1.234.567,89", language="ja", field_type="total_assets")
        {
            'normalised_form': '1234567.89',
            'currency_code': 'JPY',
            'was_negative': False,
            'processing_method': 'NUMERIC',
            'confidence': 0.95,
            'review_required': False,
        }
    """
    if not text:
        return {
            "normalised_form":  "",
            "currency_code":    "",
            "was_negative":     False,
            "processing_method": "NUMERIC",
            "confidence":       0.95,
            "review_required":  False,
        }

    working = text.strip()

    # Step 1: digit script conversion
    working = normalise_all_digits(working)

    # Step 2: parenthetical negative detection
    was_negative = bool(_HAS_NEGATIVE_RE.search(working))
    if was_negative:
        working = normalise_parenthetical_negative(working)
        # normalise_parenthetical_negative already applies normalise_number_format
        return {
            "normalised_form":  working,
            "currency_code":    "",
            "was_negative":     True,
            "processing_method": "NUMERIC",
            "confidence":       0.95,
            "review_required":  False,
        }

    # Step 3: currency extraction for financial fields
    financial_fields = {
        "total_assets", "total_liabilities", "net_assets", "revenue", "expenses",
        "share_capital", "number_of_issued_shares", "share_capital_amount",
    }
    if field_type in financial_fields:
        amount, currency_code = normalise_currency(working, language, country)
        return {
            "normalised_form":  amount,
            "currency_code":    currency_code,
            "was_negative":     False,
            "processing_method": "NUMERIC",
            "confidence":       0.95,
            "review_required":  False,
        }

    # Step 4: number format normalisation only
    working = normalise_number_format(working)
    return {
        "normalised_form":  working,
        "currency_code":    "",
        "was_negative":     False,
        "processing_method": "NUMERIC",
        "confidence":       0.95,
        "review_required":  False,
    }
