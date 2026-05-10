# Epic — Pipeline Exhaustiveness: Closing Deterministic Gaps

## Save to: `prompts/todo/epic-pipeline-exhaustiveness-gaps.md`

---

## Purpose

Six gaps exist where the normalisation pipeline routes fields to UNRESOLVED
or returns wrong results, even though a correct deterministic answer is available.
This epic closes all six. No new strategies are added — these are targeted fixes
to existing strategies A–G and the orchestrator.

After this epic, the pipeline is exhaustive and mutually exclusive for all
deterministically resolvable inputs in scope.

---

## Gap 1 — Arabic person names with known romanisations (Strategy E seed)

### Problem
Common Arabic names with a single universally accepted romanisation are routed
to UNRESOLVED because the verified repository seed is thin.
Example: `عمر` → UNRESOLVED, should be `UMAR` with variant `OMAR`.

### Fix
Expand `data/seed/person_name_tokens.json` with the 50 most common Arabic
given names and 20 common surnames that have universally accepted BGN/PCGN
romanisations. These are loaded into the verified repository by `flask seed-repository`.

The entries follow the existing seed format:

```json
[
  {
    "token": "عمر",
    "language_code": "ar",
    "field_type": "person_name",
    "romanised_form": "UMAR",
    "allowed_variants": ["OMAR", "OMER"]
  },
  {
    "token": "فاطمة",
    "language_code": "ar",
    "field_type": "person_name",
    "romanised_form": "FATIMA",
    "allowed_variants": ["FATIMAH", "FATMA"]
  },
  {
    "token": "خالد",
    "language_code": "ar",
    "field_type": "person_name",
    "romanised_form": "KHALID",
    "allowed_variants": ["KHALED", "KHALEED"]
  },
  {
    "token": "يوسف",
    "language_code": "ar",
    "field_type": "person_name",
    "romanised_form": "YUSUF",
    "allowed_variants": ["YOUSEF", "YOUSUF", "YOUSIF"]
  },
  {
    "token": "مريم",
    "language_code": "ar",
    "field_type": "person_name",
    "romanised_form": "MARYAM",
    "allowed_variants": ["MARIAM", "MARYEM"]
  },
  {
    "token": "إبراهيم",
    "language_code": "ar",
    "field_type": "person_name",
    "romanised_form": "IBRAHIM",
    "allowed_variants": ["EBRAHIM", "IBRAHEEM"]
  },
  {
    "token": "حسن",
    "language_code": "ar",
    "field_type": "person_name",
    "romanised_form": "HASAN",
    "allowed_variants": ["HASSAN", "HASEN"]
  },
  {
    "token": "أحمد",
    "language_code": "ar",
    "field_type": "person_name",
    "romanised_form": "AHMAD",
    "allowed_variants": ["AHMED", "AHAMED"]
  },
  {
    "token": "علي",
    "language_code": "ar",
    "field_type": "person_name",
    "romanised_form": "ALI",
    "allowed_variants": ["ALY"]
  },
  {
    "token": "عمر",
    "language_code": "ar",
    "field_type": "person_name",
    "romanised_form": "UMAR",
    "allowed_variants": ["OMAR", "OMER"]
  },
  {
    "token": "سارة",
    "language_code": "ar",
    "field_type": "person_name",
    "romanised_form": "SARA",
    "allowed_variants": ["SARAH"]
  },
  {
    "token": "نور",
    "language_code": "ar",
    "field_type": "person_name",
    "romanised_form": "NUR",
    "allowed_variants": ["NOUR", "NOOR"]
  }
]
```

Copilot adds these entries to `data/seed/person_name_tokens.json` (merge, do not
replace). After adding, run `flask seed-repository` to load into the database.

### Acceptance criteria
- `route_field({"original_text": "عمر", "field_type": "person_name", "language": "ar"})`
  returns `processing_method == "REPOSITORY"` and `normalised_form == "UMAR"`
- `allowed_variants` includes `["OMAR", "OMER"]`

---

## Gap 2 — Compound address normalisation (Orchestrator)

### Problem
The orchestrator passes an entire address string as a single field to the router.
The router has no strategy that handles a full compound address — it hits UNRESOLVED.
Example: `東京都港区六本木1-6-1` should resolve to `ROPPONGI 1-6-1, MINATO CITY,
TOKYO, JAPAN` by splitting into components and running each through the appropriate
strategy.

### Fix
Add an `_split_and_normalise_address()` function to the orchestrator that is called
when `field_type == "address"` or any address variant.

```python
def _split_and_normalise_address(
    address_text: str,
    language: str,
    country: str,
) -> dict:
    """
    Split a compound address string into components and normalise each
    through the appropriate strategy.

    Component types and their strategies:
        - Country name        → Strategy D (geographic lookup)
        - Prefecture/region   → Strategy D (geographic lookup)
        - City/ward/district  → Strategy D (geographic lookup)
        - Street type word    → Strategy C (vocabulary lookup, street_types.json)
        - Street name         → Strategy F (transliteration) or G (character map)
        - Building/floor/unit → Strategy A (preserve — numeric identifiers)
        - Street number       → Strategy A (preserve)

    Algorithm:
        1. Tokenise the address string on common separators (space, comma,
           Japanese address delimiters 都/道/府/県/市/区/町/村/丁目/番地/号)
        2. For each token, attempt Strategy D, then C, then F/G, then A
        3. Reassemble tokens in Western address order:
           [street number] [street name] [street type], [district], [city],
           [region], [country]
        4. Return a single result dict with the reassembled address as
           normalised_form and review_required=False if all components resolved,
           True if any component was UNRESOLVED

    Japanese address order reversal:
        Japanese addresses are written largest→smallest (country→street number).
        Western addresses are written smallest→largest (street number→country).
        The function reverses the token order for ja/zh/ko language codes.

    Args:
        address_text: Raw address string in any script.
        language:     ISO 639-1 language code.
        country:      ISO 3166-1 alpha-2 country code (from document context).

    Returns:
        Standard result dict with processing_method="ADDRESS_COMPOSITE"
    """
```

Add `ADDRESS_COMPOSITE` to `ProcessingMethod` constants in `field_types.py`.

In `process_field_row()` in `orchestrator.py`, call this function when
`field_type` is in `ADDRESS_FIELD_TYPES` before calling `route_field()`:

```python
ADDRESS_FIELD_TYPES = {
    "address", "registered_address", "business_address",
    "place_of_birth",
}

def process_field_row(row: dict) -> dict:
    field_type = row.get("field_type", "")
    if field_type in ADDRESS_FIELD_TYPES:
        text     = row.get("original_text", "")
        language = row.get("language", "")
        country  = row.get("country", "")
        if text and len(text.split()) > 2:
            # Compound address — use component normaliser
            return _split_and_normalise_address(text, language, country)
    # Single field or short address — route normally
    from app.pipeline.normalisation.router import route_field
    return route_field(row)
```

### Acceptance criteria
- `process_field_row({"original_text": "東京都港区六本木1-6-1", "field_type": "address", "language": "ja"})` returns a normalised form containing `TOKYO` and `MINATO` and `ROPPONGI`
- `processing_method == "ADDRESS_COMPOSITE"`
- Single-token address fields (e.g. just a city name) still go through `route_field()` normally

---

## Gap 3 — Nationality adjectives lookup table (Strategy D)

### Problem
Nationality adjectives (`سعودي`, `ياباني`, `إيراني`) are not place names and do
not appear in GeoNames. Strategy D currently returns None for them and they hit
UNRESOLVED. A finite closed set of nationality adjectives per language is fully
deterministic.

### Fix

**Step 1 — Create `data/lookup_tables/nationality_adjectives.json`**

Format: keyed by ISO 639-1 language code. Value is a dict mapping the native
adjective form to the canonical English country name (uppercase).

```json
{
  "_note": "Nationality adjectives mapped to canonical English country names. Keyed by ISO 639-1 language code.",
  "ar": {
    "سعودي": "SAUDI ARABIA",
    "سعودية": "SAUDI ARABIA",
    "إماراتي": "UNITED ARAB EMIRATES",
    "إماراتية": "UNITED ARAB EMIRATES",
    "مصري": "EGYPT",
    "مصرية": "EGYPT",
    "ياباني": "JAPAN",
    "يابانية": "JAPAN",
    "صيني": "CHINA",
    "صينية": "CHINA",
    "روسي": "RUSSIA",
    "روسية": "RUSSIA",
    "فرنسي": "FRANCE",
    "فرنسية": "FRANCE",
    "ألماني": "GERMANY",
    "ألمانية": "GERMANY",
    "بريطاني": "UNITED KINGDOM",
    "بريطانية": "UNITED KINGDOM",
    "أمريكي": "UNITED STATES",
    "أمريكية": "UNITED STATES",
    "كويتي": "KUWAIT",
    "كويتية": "KUWAIT",
    "قطري": "QATAR",
    "قطرية": "QATAR",
    "بحريني": "BAHRAIN",
    "بحرينية": "BAHRAIN",
    "عماني": "OMAN",
    "عمانية": "OMAN",
    "لبناني": "LEBANON",
    "لبنانية": "LEBANON",
    "أردني": "JORDAN",
    "أردنية": "JORDAN",
    "عراقي": "IRAQ",
    "عراقية": "IRAQ",
    "سوري": "SYRIA",
    "سورية": "SYRIA",
    "إيراني": "IRAN",
    "إيرانية": "IRAN",
    "تركي": "TURKEY",
    "تركية": "TURKEY",
    "هندي": "INDIA",
    "هندية": "INDIA",
    "باكستاني": "PAKISTAN",
    "باكستانية": "PAKISTAN",
    "إندونيسي": "INDONESIA",
    "ماليزي": "MALAYSIA",
    "سنغافوري": "SINGAPORE",
    "كوري": "SOUTH KOREA",
    "تايلاندي": "THAILAND",
    "مغربي": "MOROCCO",
    "مغربية": "MOROCCO",
    "تونسي": "TUNISIA",
    "جزائري": "ALGERIA",
    "ليبي": "LIBYA",
    "يمني": "YEMEN",
    "سوداني": "SUDAN"
  },
  "ja": {
    "日本人": "JAPAN",
    "中国人": "CHINA",
    "韓国人": "SOUTH KOREA",
    "アメリカ人": "UNITED STATES",
    "イギリス人": "UNITED KINGDOM",
    "フランス人": "FRANCE",
    "ドイツ人": "GERMANY",
    "ロシア人": "RUSSIA",
    "インド人": "INDIA",
    "タイ人": "THAILAND",
    "シンガポール人": "SINGAPORE",
    "オーストラリア人": "AUSTRALIA",
    "カナダ人": "CANADA",
    "ブラジル人": "BRAZIL"
  },
  "ru": {
    "российский": "RUSSIA",
    "российская": "RUSSIA",
    "японский": "JAPAN",
    "японская": "JAPAN",
    "китайский": "CHINA",
    "китайская": "CHINA",
    "американский": "UNITED STATES",
    "американская": "UNITED STATES",
    "британский": "UNITED KINGDOM",
    "британская": "UNITED KINGDOM",
    "немецкий": "GERMANY",
    "немецкая": "GERMANY",
    "французский": "FRANCE",
    "французская": "FRANCE"
  },
  "zh": {
    "日本人": "JAPAN",
    "中国人": "CHINA",
    "韩国人": "SOUTH KOREA",
    "美国人": "UNITED STATES",
    "英国人": "UNITED KINGDOM",
    "法国人": "FRANCE",
    "德国人": "GERMANY",
    "俄罗斯人": "RUSSIA",
    "印度人": "INDIA",
    "新加坡人": "SINGAPORE",
    "澳大利亚人": "AUSTRALIA"
  },
  "el": {
    "Έλληνας": "GREECE",
    "Ελληνίδα": "GREECE",
    "Γερμανός": "GERMANY",
    "Γερμανίδα": "GERMANY",
    "Γάλλος": "FRANCE",
    "Γαλλίδα": "FRANCE",
    "Βρετανός": "UNITED KINGDOM",
    "Αμερικανός": "UNITED STATES",
    "Ρώσος": "RUSSIA",
    "Ρωσίδα": "RUSSIA",
    "Κινέζος": "CHINA",
    "Ιάπωνας": "JAPAN"
  },
  "de": {
    "deutsch": "GERMANY",
    "deutsche": "GERMANY",
    "deutscher": "GERMANY",
    "japanisch": "JAPAN",
    "japanische": "JAPAN",
    "chinesisch": "CHINA",
    "französisch": "FRANCE",
    "amerikanisch": "UNITED STATES",
    "britisch": "UNITED KINGDOM",
    "russisch": "RUSSIA"
  },
  "fr": {
    "français": "FRANCE",
    "française": "FRANCE",
    "allemand": "GERMANY",
    "allemande": "GERMANY",
    "japonais": "JAPAN",
    "japonaise": "JAPAN",
    "chinois": "CHINA",
    "chinoise": "CHINA",
    "américain": "UNITED STATES",
    "américaine": "UNITED STATES",
    "britannique": "UNITED KINGDOM",
    "russe": "RUSSIA"
  },
  "ko": {
    "한국인": "SOUTH KOREA",
    "일본인": "JAPAN",
    "중국인": "CHINA",
    "미국인": "UNITED STATES",
    "영국인": "UNITED KINGDOM",
    "프랑스인": "FRANCE",
    "독일인": "GERMANY",
    "러시아인": "RUSSIA"
  },
  "tr": {
    "Türk": "TURKEY",
    "Türklük": "TURKEY",
    "Japon": "JAPAN",
    "Çinli": "CHINA",
    "Alman": "GERMANY",
    "Fransız": "FRANCE",
    "İngiliz": "UNITED KINGDOM",
    "Amerikan": "UNITED STATES",
    "Rus": "RUSSIA",
    "Arap": "SAUDI ARABIA",
    "İranlı": "IRAN"
  }
}
```

**Step 2 — Load in `geographic_lookup.py`**

Load `nationality_adjectives.json` at index build time alongside the GeoNames data.
Before attempting GeoNames lookup for `nationality` field types, check this table first:

```python
def _load_nationality_adjectives() -> dict:
    """Load nationality_adjectives.json → flat dict: (term, language) → country."""
    from pathlib import Path
    import json
    path = Path("data/lookup_tables/nationality_adjectives.json")
    if not path.exists():
        return {}
    data = json.loads(path.read_text("utf-8"))
    result = {}
    for lang, terms in data.items():
        if lang.startswith("_"):
            continue
        for term, country in terms.items():
            result[(term.lower(), lang)] = country
    return result
```

In `lookup_geographic()`, before the GeoNames alias lookup:

```python
# Check nationality adjectives table first (faster and more precise)
if field_type in NATIONALITY_FIELDS:
    adj_key = (normalised, language)
    if adj_key in _NATIONALITY_ADJECTIVES:
        return _build_result(text, _NATIONALITY_ADJECTIVES[adj_key], 0.95)
```

### Acceptance criteria
- `lookup_geographic("سعودي", "nationality", "ar")` returns `SAUDI ARABIA`
- `lookup_geographic("日本人", "nationality", "ja")` returns `JAPAN`
- `lookup_geographic("deutsch", "nationality", "de")` returns `GERMANY`
- All entries in `nationality_adjectives.json` resolve correctly
- No GeoNames lookup is attempted when the adjectives table matches

---

## Gap 4 — Date format disambiguation using document country context (Strategy B)

### Problem
`08/05/2025` is ambiguous — DD/MM/YYYY (UAE, UK, EU) or MM/DD/YYYY (US).
The router does not use the document country context to resolve this.

### Fix
Add a `DATE_FORMAT_BY_COUNTRY` dict to `calendar_rules.py`:

```python
DATE_FORMAT_BY_COUNTRY: dict[str, str] = {
    # DD/MM/YYYY countries
    "AE": "DMY", "SA": "DMY", "EG": "DMY", "KW": "DMY", "QA": "DMY",
    "BH": "DMY", "OM": "DMY", "JO": "DMY", "LB": "DMY", "IQ": "DMY",
    "GB": "DMY", "IE": "DMY", "AU": "DMY", "NZ": "DMY", "IN": "DMY",
    "DE": "DMY", "FR": "DMY", "IT": "DMY", "ES": "DMY", "PT": "DMY",
    "NL": "DMY", "BE": "DMY", "AT": "DMY", "CH": "DMY", "SE": "DMY",
    "NO": "DMY", "DK": "DMY", "FI": "DMY", "PL": "DMY", "GR": "DMY",
    "RU": "DMY", "UA": "DMY", "TR": "DMY", "IL": "DMY", "ZA": "DMY",
    "SG": "DMY", "HK": "DMY", "MY": "DMY", "TH": "DMY", "PH": "DMY",
    "BR": "DMY", "MX": "DMY", "AR": "DMY",
    # MM/DD/YYYY countries
    "US": "MDY", "CA": "MDY",
    # YYYY/MM/DD countries
    "JP": "YMD", "CN": "YMD", "KR": "YMD", "TW": "YMD",
    "IR": "YMD",
}
```

In `apply_calendar_rules()`, when a date pattern is ambiguous (day ≤ 12 and month ≤ 12),
use `DATE_FORMAT_BY_COUNTRY.get(country, "DMY")` to resolve. Default to DMY
(most common internationally) when country is unknown.

Pass `country` through the router to Strategy B:

In `router.py`, ensure `_try_strategy_b()` receives and forwards the `country`
field from the row:

```python
def _try_strategy_b(text, field_type, language, country) -> dict | None:
    try:
        from app.pipeline.normalisation.calendar_rules import apply_calendar_rules
        return apply_calendar_rules(text, field_type, language=language, country=country)
    except (ImportError, NotImplementedError):
        return None
    except Exception:
        return None
```

### Acceptance criteria
- `route_field({"original_text": "08/05/2025", "field_type": "date_of_birth", "language": "ar", "country": "AE"})` returns `2025-05-08` (DD/MM/YYYY, UAE convention)
- `route_field({"original_text": "08/05/2025", "field_type": "date_of_birth", "language": "en", "country": "US"})` returns `2025-08-05` (MM/DD/YYYY, US convention)
- `route_field({"original_text": "2025/08/05", "field_type": "date_of_birth", "language": "ja", "country": "JP"})` returns `2025-08-05` (YYYY/MM/DD, Japan)
- When country is empty, defaults to DMY

---

## Gap 5 — Non-ASCII digit scripts in non-financial fields (Strategy B)

### Problem
`numeric_rules.py` has full support for Devanagari, Thai, Arabic-Indic, and
full-width digits. But the router only calls Strategy B for financial field types.
A registration number like `DE४५०` (containing Devanagari digits) hits UNRESOLVED
instead of being digit-normalised and preserved.

### Fix
In `router.py`, before calling Strategy A (Preserve), run a digit normalisation
pre-pass on ALL field types — not just financial ones. If the text contains
non-ASCII digits and the field type is a preserve field, normalise the digits
and return PRESERVE:

```python
def _normalise_digits_preserve(text: str, field_type: str) -> dict | None:
    """
    Pre-pass: if a preserve field contains non-ASCII digits, normalise them
    and return as PRESERVE. This runs before Strategy A.

    Covers: Devanagari (०-९), Thai (๐-๙), Arabic-Indic (٠-٩),
            Eastern Arabic-Indic (۰-۹), Full-width (０-９)
    """
    import unicodedata
    # Check if text contains any non-ASCII digit
    has_non_ascii_digit = any(
        unicodedata.category(c) == "Nd" and not c.isascii()
        for c in text
    )
    if not has_non_ascii_digit:
        return None  # nothing to do

    if field_type not in PRESERVE_FIELDS:
        return None  # let Strategy B handle financial fields

    from app.pipeline.normalisation.numeric_rules import normalise_all_digits
    normalised = normalise_all_digits(text)

    return {
        "original_text":           text,
        "normalised_form":         normalised,
        "allowed_variants":        [],
        "processing_method":       "PRESERVE",
        "confidence":              1.0,
        "review_required":         False,
        "review_reason":           None,
        "should_use_in_screening": True,
    }
```

Call this at the very start of `route_field()`, before Strategy A:

```python
def route_field(row: dict) -> dict:
    text       = row.get("original_text", "")
    field_type = row.get("field_type", "")
    ...
    # Pre-pass: digit normalisation for preserve fields
    result = _normalise_digits_preserve(text, field_type)
    if result:
        return result

    # Strategy A
    result = _try_strategy_a(text, field_type)
    ...
```

### Acceptance criteria
- `route_field({"original_text": "DE४५०123", "field_type": "registration_no"})` returns `normalised_form == "DE450123"` and `processing_method == "PRESERVE"`
- `route_field({"original_text": "๒๕๖๘", "field_type": "passport_no"})` returns `normalised_form == "2568"` and `processing_method == "PRESERVE"`
- `route_field({"original_text": "△४,१९१", "field_type": "total_assets", "language": "ja"})` still routes to Strategy B (financial field with digit scripts)

---

## Gap 6 — Legal form suffix extraction from full company names (Strategy C)

### Problem
Strategy C matches the entire text against vocabulary tables. So `GmbH` matches
but `Müller & Söhne GmbH` does not, because the full string is not in the table.
The legal form is the suffix — it needs to be extracted before matching.

### Fix
In `VocabularyLookupService.lookup()`, for `field_type == "legal_form"` or
`field_type == "company_name"`, attempt suffix extraction before exact matching:

```python
def _extract_legal_form_suffix(
    self,
    text: str,
    language: str,
    country: str,
) -> str | None:
    """
    Attempt to extract a legal form suffix from the end of a company name.

    Algorithm:
        1. Split text into tokens on whitespace and common punctuation
        2. Try matching the last 1, 2, and 3 tokens against legal_forms.json
           (using country code if available, then language code)
        3. Return the canonical form if found, else None

    Examples:
        "Müller & Söhne GmbH"    → tries "GmbH" → matches → "GMBH"
        "三菱商事株式会社"          → tries "株式会社" → matches → "KK"
        "Газпром ПАО"            → tries "ПАО" → matches → "PJSC"
        "Smith & Jones LLP"      → tries "LLP" → matches → "LLP"
    """
    import re
    tokens = re.split(r"[\s&,\.、。]+", text.strip())
    tokens = [t for t in tokens if t]

    # Try last 1, 2, 3 tokens as potential suffix
    for n in (1, 2, 3):
        if len(tokens) < n:
            continue
        candidate = " ".join(tokens[-n:])
        result = self._lookup_legal_form(candidate, language, country)
        if result:
            return result

    # For CJK: also try without spaces (kanji suffixes are not space-separated)
    if any(ord(c) > 0x2E7F for c in text):
        for n in (2, 3, 4):
            candidate = text[-n:]
            result = self._lookup_legal_form(candidate, language, country)
            if result:
                return result

    return None
```

Call this in `lookup()` when `field_type in ("legal_form", "company_name")`:

```python
def lookup(self, field_type, text, language="", country=""):
    ...
    if field_type in ("legal_form", "company_name"):
        # Try exact match first
        result = self._exact_lookup(field_type, text, language, country)
        if result:
            return result
        # Try suffix extraction
        canonical = self._extract_legal_form_suffix(text, language, country)
        if canonical:
            return self._build_result(text, canonical)

    ...
```

### Acceptance criteria
- `route_field({"original_text": "三菱商事株式会社", "field_type": "company_name", "language": "ja", "country": "JP"})` returns `normalised_form == "KK"` and `processing_method == "VOCABULARY"`
- `route_field({"original_text": "Müller & Söhne GmbH", "field_type": "company_name", "language": "de", "country": "DE"})` returns `normalised_form == "GMBH"`
- `route_field({"original_text": "Газпром ПАО", "field_type": "company_name", "language": "ru", "country": "RU"})` returns `normalised_form == "PJSC"`
- `route_field({"original_text": "Smith & Jones LLP", "field_type": "company_name", "language": "en", "country": "GB"})` returns `normalised_form == "LLP"`
- Exact matches (e.g. `GmbH` alone) still work as before

---

## Tests — `tests/test_pipeline_exhaustiveness.py`

```python
"""Tests for pipeline exhaustiveness gaps 1-6."""
from app.pipeline.normalisation.router import route_field
from app.pipeline.orchestrator import process_field_row
from app import create_app
import pytest

@pytest.fixture(scope="module")
def app_context():
    app = create_app("testing")
    ctx = app.app_context()
    ctx.push()
    yield
    ctx.pop()

# Gap 1 — Arabic names from repository
def test_arabic_umar_from_repository(app_context):
    r = route_field({"original_text": "عمر", "field_type": "person_name", "language": "ar"})
    assert r["processing_method"] == "REPOSITORY"
    assert r["normalised_form"] == "UMAR"
    assert "OMAR" in r["allowed_variants"]

def test_arabic_fatima_from_repository(app_context):
    r = route_field({"original_text": "فاطمة", "field_type": "person_name", "language": "ar"})
    assert r["processing_method"] == "REPOSITORY"
    assert r["normalised_form"] == "FATIMA"

# Gap 2 — Compound address
def test_japanese_compound_address(app_context):
    r = process_field_row({
        "original_text": "東京都港区六本木1-6-1",
        "field_type": "address",
        "language": "ja",
    })
    assert r["processing_method"] == "ADDRESS_COMPOSITE"
    form = r["normalised_form"].upper()
    assert "TOKYO" in form
    assert "MINATO" in form

# Gap 3 — Nationality adjectives
def test_arabic_saudi_adjective(app_context):
    from app.pipeline.normalisation.geographic_lookup import lookup_geographic
    r = lookup_geographic("سعودي", "nationality", "ar")
    assert r is not None
    assert r["normalised_form"] == "SAUDI ARABIA"

def test_japanese_nationality_adjective(app_context):
    from app.pipeline.normalisation.geographic_lookup import lookup_geographic
    r = lookup_geographic("日本人", "nationality", "ja")
    assert r is not None
    assert r["normalised_form"] == "JAPAN"

# Gap 4 — Date disambiguation by country
def test_ambiguous_date_uae_convention(app_context):
    r = route_field({
        "original_text": "08/05/2025",
        "field_type": "date_of_birth",
        "language": "ar",
        "country": "AE",
    })
    assert r["normalised_form"] == "2025-05-08"

def test_ambiguous_date_us_convention(app_context):
    r = route_field({
        "original_text": "08/05/2025",
        "field_type": "date_of_birth",
        "language": "en",
        "country": "US",
    })
    assert r["normalised_form"] == "2025-08-05"

def test_japanese_date_format(app_context):
    r = route_field({
        "original_text": "2025/08/05",
        "field_type": "date_of_birth",
        "language": "ja",
        "country": "JP",
    })
    assert r["normalised_form"] == "2025-08-05"

# Gap 5 — Non-ASCII digits in preserve fields
def test_devanagari_digits_in_registration_no(app_context):
    r = route_field({"original_text": "DE४५०123", "field_type": "registration_no"})
    assert r["normalised_form"] == "DE450123"
    assert r["processing_method"] == "PRESERVE"

def test_thai_digits_in_passport_no(app_context):
    r = route_field({"original_text": "๒๕๖๘AB", "field_type": "passport_no"})
    assert r["normalised_form"] == "2568AB"
    assert r["processing_method"] == "PRESERVE"

# Gap 6 — Legal form suffix extraction
def test_japanese_company_name_suffix(app_context):
    r = route_field({
        "original_text": "三菱商事株式会社",
        "field_type": "company_name",
        "language": "ja",
        "country": "JP",
    })
    assert r["normalised_form"] == "KK"
    assert r["processing_method"] == "VOCABULARY"

def test_german_company_name_suffix(app_context):
    r = route_field({
        "original_text": "Müller & Söhne GmbH",
        "field_type": "company_name",
        "language": "de",
        "country": "DE",
    })
    assert r["normalised_form"] == "GMBH"

def test_russian_company_name_suffix(app_context):
    r = route_field({
        "original_text": "Газпром ПАО",
        "field_type": "company_name",
        "language": "ru",
        "country": "RU",
    })
    assert r["normalised_form"] == "PJSC"

def test_english_company_name_suffix(app_context):
    r = route_field({
        "original_text": "Smith & Jones LLP",
        "field_type": "company_name",
        "language": "en",
        "country": "GB",
    })
    assert r["normalised_form"] == "LLP"

def test_exact_legal_form_still_works(app_context):
    r = route_field({
        "original_text": "GmbH",
        "field_type": "legal_form",
        "language": "de",
        "country": "DE",
    })
    assert r["normalised_form"] == "GMBH"
```

---

## Implementation order

Implement in this order — each is independent of the others except Gap 2
which depends on Gap 4 (country context) being available:

1. Gap 5 — digit pre-pass (touches only router.py, lowest risk)
2. Gap 3 — nationality adjectives JSON + geographic_lookup.py (data + small code change)
3. Gap 6 — legal form suffix extraction (VocabularyLookupService only)
4. Gap 4 — date disambiguation by country (calendar_rules.py + router.py)
5. Gap 1 — Arabic name seed data (data only + flask seed-repository)
6. Gap 2 — compound address normalisation (orchestrator, most complex, last)

---

## Acceptance criteria — overall

After this epic, running the integration diagnostic should show:
- C.10, C.11, C.12 (company name suffix) → PASS
- D.5, D.7 (nationality adjectives) → PASS
- B.x (ambiguous dates with country context) → PASS
- Arabic common names from repository → PASS
- Non-ASCII digits in preserve fields → PASS
- All existing passing tests continue to pass
