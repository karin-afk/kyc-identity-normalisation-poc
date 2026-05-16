# Epic 01 — Normalisation Strategy B: Calendar and Numeric Rules

**Status: IMPLEMENTED** — branch `feature/epic-01b-strategy-b-calendar-numeric`.

## Execution Todo Checklist (this run)

- [x] Create source conversion modules:
    - [x] `src/pipeline/calendar_solar_hijri.py`
    - [x] `src/pipeline/calendar_hebrew.py`
    - [x] `src/pipeline/calendar_offset.py`
    - [x] `src/pipeline/numeric_rules.py`
- [x] Add `convertdate>=2.4.0` to `requirements.txt`
- [x] Implement `app/pipeline/normalisation/calendar_rules.py` with:
    - [x] `apply_calendar_rules(...)`
    - [x] `apply_numeric_rules(...)`
    - [x] Calendar routing for Japanese/Hebrew/Thai/Minguo/Solar-Hijri/Hijri/Gregorian
    - [x] Numeric script + formatting + currency normalisation helpers
- [x] Update router Strategy B wiring in `app/pipeline/normalisation/router.py`
- [x] Update orchestrator integration in `app/pipeline/orchestrator.py` (ensure Strategy B path is reachable for sentence and document stubs)
- [x] Add tests in `tests/test_strategy_b_calendar.py`
- [x] Update impacted router/orchestrator tests for new Strategy B behavior
- [x] Run tests and fix regressions
- [x] Run Flask app on `127.0.0.1:5001` for manual UI verification
- [x] Provide copy/paste examples for the Sentence tab

## What you need to provide

You need to provide **four Python files** containing the conversion logic for calendar systems and numeric scripts that do not exist in the current codebase. The format for each is specified below.

Copilot will merge what you provide with the existing logic from `src/utils/calendar_utils.py` into the final `app/pipeline/normalisation/calendar_rules.py`.

---

### File 1 — Solar Hijri / Persian calendar conversion

**What it is:** Converts Solar Hijri dates (used on Iranian and Afghan official documents) to Gregorian. Solar Hijri is a solar calendar — unlike Hijri lunar, it stays in sync with the seasons. Year ~1404 corresponds to 2025.

**What to include:** A function `solar_hijri_to_gregorian(year: int, month: int, day: int) -> tuple[int, int, int]` with the conversion logic. Include inline comments explaining month length rules (first six months have 31 days, next five have 30, last month has 29 or 30 in leap years) and any edge cases. Also include a regex pattern for detecting Solar Hijri date strings in document text — Persian-Indic numerals (۱۴۰۴) are common and must be handled.

**Save to:** `\src\pipeline\calendar_solar_hijri.py`

---

### File 2 — Hebrew calendar conversion

**What it is:** Converts Hebrew calendar dates (used on Israeli official documents) to Gregorian. The Hebrew calendar is lunisolar with a 19-year Metonic cycle. Year 5786 approximately corresponds to 2025/2026.

**What to include:** A function `hebrew_to_gregorian(year: int, month: int, day: int) -> tuple[int, int, int]`. Include comments on the leap year cycle (7 leap years per 19-year cycle) and month ordering. Also include a regex pattern for Hebrew date strings, noting that Hebrew is written right-to-left and dates may appear in various formats.

**Save to:** `\src\pipeline\calendar_hebrew.py`

---

### File 3 — Thai Buddhist Era and Minguo calendar conversions

**What it is:** Two simple offset-based conversions.
- Thai Buddhist Era (used on Thai official documents): subtract 543 from the year. 2568 BE → 2025 CE.
- Minguo / Republic of China (used on Taiwanese documents): add 1911 to the year. 114 ROC → 2025 CE.

Both use the same month/day structure as Gregorian — only the year count differs.

**What to include:** Two functions — `thai_buddhist_to_gregorian(year, month, day)` and `minguo_to_gregorian(year, month, day)` — with regex patterns for detecting each format in document text. Thai documents often show the year as a 4-digit Thai-script numeral (๒๕๖๘); Minguo years are typically 2–3 digits.

**Save to:** `\src\pipeline\calendar_offset.py`

---

### File 4 — Numeric normalisation rules

**What it is:** Translation tables and functions for numeric scripts and formats not currently in the codebase.

**What to include — each as a separate function or table with a docstring:**

- Full-width ASCII digit table: `０１２３４５６７８９` → `0123456789`. Used in Japanese financial documents (EDINET filings).
- Devanagari digit table: `०१२३४५६७८९` → `0123456789`. Used in Indian documents.
- Thai digit table: `๐๑๒๓๔๕๖๗๘๙` → `0123456789`.
- Number format normalisation function: converts European format (`1.000.000,50`) and Swiss format (`1'000'000.50`) to English format (`1000000.50`). Include detection logic (if the last separator before digits is a comma → European; if period → English).
- Parenthetical negative notation function: `△4191` → `-4191`, `（4191）` → `-4191`, `(4191)` → `-4191`. Used in Japanese financial statements.
- Currency symbol mapping: dict mapping symbol → ISO 4217 code. Cover at minimum: `¥` (ambiguous — JPY vs CNY, resolved by `language` or `country` parameter), `﷼` → `SAR`, `₪` → `ILS`, `€` → `EUR`, `£` → `GBP`, `$` → `USD`. Include a `normalise_currency(text, language, country)` function that extracts the amount and returns `(amount_str, iso_4217_code)`.

**Save to:** `\src\pipeline\numeric_rules.py`

---

## What exists in the current codebase — Copilot carries forward

The following already exist in `src/utils/calendar_utils.py` and are correct. Copilot copies them into `app/pipeline/normalisation/calendar_rules.py` without modification:

- `arabic_indic_to_ascii()` — converts both Arabic-Indic (`٠١…٩`) and Eastern Arabic-Indic / Persian-Indic (`۰۱…۹`) digits to ASCII. Already handles both tables.
- `detect_calendar_system()` — detects Hijri vs Gregorian from year range.
- `hijri_to_gregorian()` — Hijri lunar conversion using `hijri-converter` library with fallback formula.
- `normalise_date_field()` — master date normalisation entry point.
- `_parse_gregorian()` — Gregorian date format detection and ISO 8601 output.
- `detect_and_convert_japanese_era()` — all five modern Japanese eras (Meiji, Taisho, Showa, Heisei, Reiwa), Kanji numeral parsing, era-boundary handling.
- `kanji_numeral_to_int()` — positional and classical Kanji numeral conversion.

Also from `src/utils/normalisation.py`:
- `to_normalised_form()` — NFKC + ASCII + uppercase. Carry forward as a utility.

---

## What this epic builds

### `app/pipeline/normalisation/calendar_rules.py` — NEW FILE

Copilot creates this by merging the existing code (listed above) with the four files you provide. The result is a single module covering all calendar systems and all numeric normalisation.

The module must expose one public entry point for dates and one for numeric values:

```python
def apply_calendar_rules(field_type: str, text: str, language: str = "", country: str = "") -> dict | None:
    """
    Entry point for Strategy B date fields.

    Called by the normalisation router when field_type is in NUMERIC_FIELDS.

    Steps in order:
    1. Apply all digit script conversions (arabic_indic, eastern_arabic_indic,
       fullwidth, devanagari, thai) to normalise any non-ASCII digits to ASCII.
    2. Detect calendar system from the resulting string and the language/country hint.
    3. Convert to Gregorian if needed.
    4. Parse and output ISO 8601 (YYYY-MM-DD, or YYYY-MM, or YYYY where
       month and day are absent).

    Returns a result dict on success. Returns None if field_type is not in
    NUMERIC_FIELDS (signals router to try next strategy).

    Calendar system detection priority:
    - language == "ja" → attempt Japanese era-year first
    - language == "he" → attempt Hebrew calendar
    - language == "th" → attempt Thai Buddhist Era
    - language == "zh" and country == "TW" → attempt Minguo
    - language in ("fa", "ps") or country in ("IR", "AF") → attempt Solar Hijri
    - Otherwise → detect Hijri vs Gregorian by year range (existing logic)
    """

def apply_numeric_rules(field_type: str, text: str, language: str = "", country: str = "") -> dict | None:
    """
    Entry point for Strategy B financial numeric fields.

    Called by the normalisation router when field_type is in PRESERVE_FIELDS
    and the field holds a financial value (number_of_shares, total_assets etc.).

    Steps in order:
    1. Apply all digit script conversions.
    2. Apply parenthetical negative conversion.
    3. Apply number format normalisation (European/Swiss → English).
    4. Extract and normalise currency symbol if present.

    Returns a result dict with normalised_form as a clean numeric string.
    Returns None if text contains no recognisable numeric content.
    """
```

Result dict shape — same structure used by all strategies:

```python
{
    "original_text":           str,   # raw input unchanged
    "normalised_form":         str,   # ISO 8601 date or normalised number
    "allowed_variants":        [],    # always empty for B — dates have one canonical form
    "processing_method":       str,   # ProcessingMethod.CALENDAR or ProcessingMethod.NUMERIC
    "confidence":              float, # from STRATEGY_CONFIDENCE in field_types.py
    "review_required":         bool,
    "review_reason":           str | None,
    "should_use_in_screening": bool,
    # Date-specific additional fields:
    "original_calendar":       str | None,  # "gregorian", "hijri", "japanese_era",
                                             # "solar_hijri", "hebrew", "thai_buddhist",
                                             # "minguo", "unknown"
}
```

### `app/pipeline/normalisation/calendar_rules.py` — calendar system routing logic

Copilot adds the following routing block to `normalise_date_field()` to call the four new calendar files you provide:

```python
# New calendar systems — added in Epic 02
if language == "he":
    from app.pipeline.normalisation.calendar_hebrew import hebrew_to_gregorian, detect_hebrew_date
    result = detect_hebrew_date(ascii_date)
    if result:
        return result

if language == "th" or country == "TH":
    from app.pipeline.normalisation.calendar_offset import thai_buddhist_to_gregorian, detect_thai_date
    result = detect_thai_date(ascii_date)
    if result:
        return result

if (language == "zh" and country == "TW") or country == "TW":
    from app.pipeline.normalisation.calendar_offset import minguo_to_gregorian, detect_minguo_date
    result = detect_minguo_date(ascii_date)
    if result:
        return result

if language in ("fa", "ps") or country in ("IR", "AF"):
    from app.pipeline.normalisation.calendar_solar_hijri import solar_hijri_to_gregorian, detect_solar_hijri_date
    result = detect_solar_hijri_date(ascii_date)
    if result:
        return result

# Fall through to existing Hijri/Gregorian detection
```

### `requirements.txt` — add `convertdate`

```
convertdate>=2.4.0
```

Use `convertdate` as a reference implementation to validate the logic in the files you provide. If `convertdate` produces the same results as your implementations, the implementations are correct.

---

## Tests

`tests/test_strategy_b_calendar.py` — Copilot writes these after you have provided your four files.

The test file must cover:

```python
# --- Existing (carry forward from golden dataset) ---
def test_hijri_to_gregorian_known_date(): ...         # 1445/9/1 → 2024-03-11
def test_japanese_era_showa(): ...                     # 昭和60年3月12日 → 1985-03-12
def test_japanese_era_reiwa(): ...                     # 令和5年7月3日 → 2023-07-03
def test_arabic_indic_digits(): ...                    # ١٩٨٥/٠٣/١٢ → 1985-03-12
def test_eastern_arabic_indic_digits(): ...            # ۱۴۴۵/۰۹/۰۱ → detect as Hijri

# --- New calendar systems ---
def test_solar_hijri_known_date(): ...                 # 1404/2/15 → 2025-05-05 (verify with convertdate)
def test_hebrew_known_date(): ...                      # 5786/1/1 → 2025-10-02 (approx — verify with convertdate)
def test_thai_buddhist_known_date(): ...               # 2568/5/8 → 2025-05-08
def test_minguo_known_date(): ...                      # 114/5/8 → 2025-05-08

# --- Language/country routing ---
def test_thai_date_detected_by_language(): ...         # language="th" triggers Thai Buddhist
def test_minguo_detected_by_country_tw(): ...          # country="TW" triggers Minguo
def test_solar_hijri_detected_by_language_fa(): ...    # language="fa" triggers Solar Hijri
def test_hebrew_detected_by_language_he(): ...         # language="he" triggers Hebrew

# --- Numeric normalisations ---
def test_fullwidth_digits(): ...                       # ０１２３ → 0123
def test_devanagari_digits(): ...                      # ०१२३ → 0123
def test_thai_digits(): ...                            # ๐๑๒๓ → 0123
def test_european_number_format(): ...                 # 1.234.567,89 → 1234567.89
def test_swiss_number_format(): ...                    # 1'234'567.89 → 1234567.89
def test_parenthetical_negative_triangle(): ...        # △4191 → -4191
def test_parenthetical_negative_fullwidth(): ...       # （4191） → -4191
def test_parenthetical_negative_ascii(): ...           # (4191) → -4191
def test_currency_yen_japanese(): ...                  # ¥ with language="ja" → JPY
def test_currency_yen_chinese(): ...                   # ¥ with language="zh" → CNY
def test_currency_rial(): ...                          # ﷼ → SAR
def test_currency_shekel(): ...                        # ₪ → ILS

# --- No modification of non-B fields ---
def test_returns_none_for_non_numeric_field(): ...     # field_type="person_name" → None
def test_returns_none_for_preserve_field(): ...        # field_type="passport_no" → None
```

---

## Acceptance criteria

- All tests pass.
- `apply_calendar_rules("date_of_birth", "2568/5/8", language="th")` returns `normalised_form == "2025-05-08"`.
- `apply_calendar_rules("date_of_birth", "114/5/8", country="TW")` returns `normalised_form == "2025-05-08"`.
- `apply_numeric_rules("total_assets", "△4.191")` returns `normalised_form == "-4191"`.
- `apply_numeric_rules("share_capital", "１，０００，０００")` returns `normalised_form == "1000000"`.
- All existing golden dataset regression tests continue to pass — existing Hijri and Japanese era-year behaviour is unchanged.
- `convertdate` added to `requirements.txt`.
- No LLM is called at any point in this strategy.
