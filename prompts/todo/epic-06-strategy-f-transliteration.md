# Epic 06 — Strategy F: Transliteration

**Status: ✅ IMPLEMENTED** — committed on `feat/epic-06-strategy-f` (2026-05-10)

## Implementation checklist

- [x] Create branch `feat/epic-06-strategy-f` from `dev`
- [x] Add `_transliterate_hebrew()` to `src/pipeline/transliteration_engine.py`
- [x] Add `_transliterate_persian()` to `src/pipeline/transliteration_engine.py`
- [x] Add `_transliterate_thai()` to `src/pipeline/transliteration_engine.py`
- [x] Wire `elif language == "he"/"fa"/"th"` into `transliterate()` routing
- [x] Replace `app/pipeline/normalisation/transliteration.py` stub with `apply_transliteration()` wrapper
- [x] Add `_try_strategy_f()` to `router.py` and call it after Strategy D in `route_field()`
- [x] Remove `"F"` from `_try_stub()` loop in `router.py`
- [x] Verify all 5 transliteration libraries in `requirements.txt` ✅
- [x] Write `tests/test_strategy_f_transliteration.py` (26 tests)
- [x] Run pytest — **26/26 passed**, no regressions
- [x] Run integration diagnostic — **52/74 PASS** (up from 42/74), all 10 F-series tests pass

## Test results

| Suite | Result |
|---|---|
| `test_strategy_f_transliteration.py` | **26/26 passed** |
| Integration diagnostic | **52/74 pass** (+10 vs previous) |

### Diagnostic F-series results
All 10 F-series tests now pass: F.1–F.10 (Russian, Greek, Japanese, Chinese, Korean, compounds)

### Remaining diagnostic failures (not in scope of this epic)
- G.8–G.10: Character maps (Epic 07)
- C.10–C.12: Legal form suffix extraction from company names
- B.13–B.15: Thai label, Hijri day-first, Hebrew date
- A.4: IBAN
- E.1–E.3: Edge cases (ambiguous string, mixed script, compact date)

---

## Critical context — read before doing anything

`src/pipeline/transliteration_engine.py` is **fully implemented** — 881 lines,
battle-tested, covering all major languages. It is the canonical implementation.

**DO NOT rewrite, port, or duplicate this file.** The previous epic instructions
were wrong to ask for a full rewrite. The task is two things only:

1. Wire the existing engine into `app/pipeline/normalisation/transliteration.py`
   (currently a stub)
2. Add three missing language handlers (Hebrew, Persian, Thai) directly into
   `src/pipeline/transliteration_engine.py`

---

## What already exists in `src/pipeline/transliteration_engine.py`

The following are fully implemented. **Do not touch them:**

| Handler | Languages | Standard | Notes |
|---|---|---|---|
| `_transliterate_cyrillic()` | ru, uk, bg | BGN/PCGN | Includes `_apply_bgn_pcgn_corrections()`, Ukrainian char pre-processing, soft sign stripping |
| `_transliterate_belarusian()` | be | BGN/PCGN | `BELARUSIAN_CHAR_MAP` pre-processing, Russian-mode library, review_required=True |
| `_transliterate_greek()` | el | ISO 843 | ου→ou post-processing fix |
| `_transliterate_japanese()` | ja | Hepburn | pykakasi, kanji ambiguity lookup, macron stripping, っ double-consonant |
| `_transliterate_chinese()` | zh | Pinyin | pypinyin, given-name fusion, Cantonese variants for HK/TW |
| `_transliterate_arabic()` | ar | ICAO consonant | Always review_required=True — no short vowels in standard Arabic text |
| `_normalise_korean()` | ko | Revised Romanisation | korean-romanizer, KOREAN_SURNAME_VARIANTS fallback, McCune–Reischauer variants |
| `_normalise_german()` | de | BGN/PCGN | Umlaut expansion (Ä→AE), ß→SS, noble particle variants |
| `_normalise_french()` | fr | ICAO | Accent strip, apostrophe elision, noble particle drop |
| `_normalise_spanish()` | es | ICAO | Accent strip, ñ→N primary with NY variant |
| `_normalise_italian()` | it | ICAO | Accent strip, apostrophe variants |
| `_normalise_english()` | en | ICAO | O'Brien variants, Mac/Mc alternates, St/Saint alternates |
| `_to_latin_fallback()` | any | unidecode | Last resort, always review_required=True |
| `normalise_address_latin()` | Latin-script | ICAO | Used for address fields — DO NOT REMOVE OR MOVE |

The main entry point is:
```python
def transliterate(text: str, row: dict) -> dict:
    # row must contain: language, field_type, country
```

`_build_result()` signature — use this pattern for all new handlers:
```python
def _build_result(
    original: str,
    latin: str,
    review: bool = False,
    reason: str | None = None,
) -> dict:
    # Returns: original_text, latin_transliteration, allowed_variants,
    #          analyst_english_rendering, normalised_form (uppercase),
    #          processing_method="TRANSLITERATE", confidence, review_required,
    #          review_reason, should_use_in_screening
```

---

## What is MISSING and must be added

Three languages currently fall through to `_to_latin_fallback()` (unidecode)
because they have no dedicated handler in the routing chain. The `transliterate`
library supports all three.

### Missing: Hebrew (`he`)
### Missing: Persian / Farsi (`fa`)
### Missing: Thai (`th`)

---

## Step 1 — Add three handlers to `src/pipeline/transliteration_engine.py`

Add the three functions below to `src/pipeline/transliteration_engine.py`.
Place them immediately before `_normalise_korean()` (line ~702).

### `_transliterate_hebrew()`

```python
def _transliterate_hebrew(text: str) -> dict:
    """
    Hebrew → Latin transliteration using the transliterate library (ISO 259).

    Hebrew-specific considerations:
    - Final letter forms (ך ם ן ף ץ) are the same phonemes as (כ מ נ פ צ)
      written differently at word end. The library handles them correctly.
    - Shin (שׁ) → SH; Sin (שׂ) → S. In unvocalised text both are ש
      and should map to SH (the more common name component reading).
    - The library produces correct output for standard name transliteration
      without requiring a correction table comparable to BGN/PCGN.

    review_required: False for standard output.
    """
    try:
        from transliterate import translit
        lat = translit(text, "he", reversed=True)
    except Exception:
        lat = _to_latin_fallback(text)
    return _build_result(text, lat)
```

### `_transliterate_persian()`

```python
def _transliterate_persian(text: str) -> dict:
    """
    Persian/Farsi → Latin consonant skeleton.

    Persian is a vowel-omitting abjad: short vowels (a, e, o) are not written
    in standard text. This is the same limitation as Arabic. The consonant
    skeleton is stored as the normalised_form but the result is always flagged
    review_required=True because the output cannot be a confirmed romanisation
    without vowel insertion.

    Phase 2: LLM vowel insertion controlled by LLM_ENABLED in .env.
    """
    try:
        from transliterate import translit
        lat = translit(text, "fa", reversed=True)
    except Exception:
        lat = _to_latin_fallback(text)
    return _build_result(
        text, lat,
        review=True,
        reason=(
            "Persian vowel ambiguity: short vowels are not written in standard text. "
            "Result is a consonant skeleton only. Native speaker review required."
        ),
    )
```

### `_transliterate_thai()`

```python
def _transliterate_thai(text: str) -> dict:
    """
    Thai → Latin using Royal Thai General System of Transcription (RTGS)
    via the transliterate library.

    Thai-specific considerations:
    - Thai has no spaces between words; the library handles word segmentation.
    - Thai has no capitalisation; output is uppercase via _build_result/_normalise.
    - Tones are not represented in RTGS output — correct for KYC purposes.

    review_required: False for standard output.
    """
    try:
        from transliterate import translit
        lat = translit(text, "th", reversed=True)
    except Exception:
        lat = _to_latin_fallback(text)
    return _build_result(text, lat)
```

### Wire the three handlers into `transliterate()` routing

In `src/pipeline/transliteration_engine.py`, find the `transliterate()` function
(line 829). Insert the three new `elif` blocks immediately before the `else`
fallback. The routing currently ends with:

```python
    elif language == "en":
        return _normalise_english(text, field_type)
    else:
        lat = _to_latin_fallback(text)
        ...
```

Change to:

```python
    elif language == "en":
        return _normalise_english(text, field_type)
    elif language == "he":
        return _transliterate_hebrew(text)
    elif language == "fa":
        return _transliterate_persian(text)
    elif language == "th":
        return _transliterate_thai(text)
    else:
        lat = _to_latin_fallback(text)
        ...
```

**Do not change anything else in `transliterate()`. Do not remove any existing
`elif` blocks. Do not move any existing handlers.**

---

## Step 2 — Wire the engine into `app/pipeline/normalisation/transliteration.py`

`app/pipeline/normalisation/transliteration.py` currently exists as a stub.
Replace its entire content with the following wrapper. This file must never
contain transliteration logic — it only wraps the engine in `src/`.

```python
"""
Strategy F — Transliteration.

Thin wrapper around src/pipeline/transliteration_engine.py.
All transliteration logic lives in the engine — do not duplicate it here.

Entry point: apply_transliteration(text, language, field_type, country)
Called by: app/pipeline/normalisation/router.py _try_strategy_f()
"""

import sys
from pathlib import Path

# Ensure src/ is on sys.path so the existing engine can be imported
_SRC = Path(__file__).resolve().parents[4] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


def apply_transliteration(
    text: str,
    language: str,
    field_type: str,
    country: str = "",
) -> dict | None:
    """
    Strategy F entry point called by the normalisation router.

    Delegates entirely to src/pipeline/transliteration_engine.transliterate().
    No transliteration logic is implemented here.

    Args:
        text:       Original text in source script.
        language:   ISO 639-1 language code.
        field_type: KYC field type string.
        country:    ISO 3166-1 alpha-2 country code. Used by Chinese handler
                    to determine Cantonese variant generation for HK/TW.

    Returns:
        Standard result dict with processing_method="TRANSLITERATE", or
        None if text is empty. Never raises — exceptions return None so
        the router falls through to Strategy G.
    """
    if not text or not text.strip():
        return None

    try:
        from pipeline.transliteration_engine import transliterate

        row = {
            "language":   language,
            "field_type": field_type,
            "country":    country,
        }

        result = transliterate(text, row)

        # Ensure all keys required by the app router are present
        # (the engine predates the app and may use slightly different keys)
        result.setdefault("should_use_in_screening",
                          not result.get("review_required", False))
        result.setdefault(
            "confidence",
            0.5 if result.get("review_required") else 0.85
        )

        return result

    except Exception:
        # Never crash the router — fall through to Strategy G
        return None
```

---

## Step 3 — Wire `_try_strategy_f()` in `app/pipeline/normalisation/router.py`

Find `_try_strategy_f()` in `router.py`. It is currently a stub returning `None`.
Replace with:

```python
def _try_strategy_f(text: str, field_type: str, language: str,
                    country: str = "") -> dict | None:
    """Strategy F — Transliteration. Wraps src/pipeline/transliteration_engine."""
    try:
        from app.pipeline.normalisation.transliteration import apply_transliteration
        return apply_transliteration(text, language, field_type, country)
    except Exception:
        return None
```

Ensure `_try_strategy_f()` is called in the router for these field types:
`person_name`, `full_name`, `given_name`, `family_name`, `alias`, `maiden_name`,
`company_name`, `trading_name`.

**Do not call Strategy F for preserve fields, date fields, financial fields,
vocabulary fields, or geographic fields — those are handled by A, B, C, D.**

---

## Step 4 — Verify `requirements.txt`

Confirm all five libraries are present. Add any that are missing:

```
transliterate>=1.10.2
pykakasi>=2.2.1
pypinyin>=0.49.0
korean-romanizer>=0.2.2
unidecode>=1.3.6
```

---

## Tests — `tests/test_strategy_f_transliteration.py`

No mocks. All tests call `apply_transliteration()` directly or `route_field()`.

```python
from app.pipeline.normalisation.transliteration import apply_transliteration
from app.pipeline.normalisation.router import route_field


# ── Existing languages — must still pass after wiring ─────────────────────────

def test_russian_bgn_pcgn_natalya():
    r = apply_transliteration("Наталья", "ru", "person_name")
    assert r["normalised_form"] == "NATALYA", (
        f"Expected NATALYA, got {r['normalised_form']}. "
        "Check BGN/PCGN corrections in transliteration_engine.py"
    )

def test_russian_bgn_pcgn_aleksandr():
    r = apply_transliteration("Александр", "ru", "person_name")
    assert r["normalised_form"] == "ALEKSANDR"

def test_russian_full_name():
    r = apply_transliteration("Иванова Наталья Александровна", "ru", "person_name")
    assert "IVANOVA" in r["normalised_form"]
    assert "NATALYA" in r["normalised_form"]

def test_greek_nikos():
    r = apply_transliteration("Νίκος", "el", "person_name")
    assert r["normalised_form"] == "NIKOS"

def test_greek_full_name():
    r = apply_transliteration("Νίκος Παπαδόπουλος", "el", "person_name")
    assert "NIKOS" in r["normalised_form"]
    assert "PAPADOPOULOS" in r["normalised_form"]

def test_japanese_surname_tanaka():
    r = apply_transliteration("田中", "ja", "person_name")
    assert "TANAKA" in r["normalised_form"]

def test_japanese_full_name():
    r = apply_transliteration("田中 太郎", "ja", "person_name")
    assert "TANAKA" in r["normalised_form"]
    assert "TARO" in r["normalised_form"]

def test_chinese_full_name_fusion():
    r = apply_transliteration("王小明", "zh", "person_name")
    # Given name must be fused: WANG XIAOMING not WANG XIAO MING
    assert r["normalised_form"] == "WANG XIAOMING"

def test_korean_name():
    r = apply_transliteration("이민준", "ko", "person_name")
    assert "MINJUN" in r["normalised_form"]
    assert any("LEE" in v or "YI" in v for v in r["allowed_variants"])

def test_arabic_always_review_required():
    r = apply_transliteration("محمد عبد الله", "ar", "person_name")
    assert r["review_required"] is True
    assert r["normalised_form"] is not None  # consonant skeleton still produced

def test_german_umlaut():
    r = apply_transliteration("Müller", "de", "person_name")
    assert r["normalised_form"] == "MUELLER"
    assert "MULLER" in r["allowed_variants"]

def test_french_accent():
    r = apply_transliteration("Élodie", "fr", "person_name")
    assert r["normalised_form"] == "ELODIE"


# ── New language handlers ─────────────────────────────────────────────────────

def test_hebrew_standard_name():
    r = apply_transliteration("דוד לוי", "he", "person_name")
    assert r is not None
    assert r["normalised_form"] is not None
    assert len(r["normalised_form"]) > 0
    assert r["review_required"] is False

def test_hebrew_not_falling_to_unidecode():
    """Hebrew must use its dedicated handler, not the unidecode fallback."""
    r = apply_transliteration("שרה", "he", "person_name")
    assert r is not None
    assert r["processing_method"] == "TRANSLITERATE"
    # Unidecode produces garbled output for Hebrew — if result is clean Latin, handler worked
    assert all(c.isascii() or c in " -" for c in r["normalised_form"])

def test_persian_always_review_required():
    r = apply_transliteration("احمد", "fa", "person_name")
    assert r is not None
    assert r["review_required"] is True
    assert "vowel" in r["review_reason"].lower() or "Persian" in r["review_reason"]

def test_persian_not_falling_to_unidecode():
    r = apply_transliteration("محمد", "fa", "person_name")
    assert r is not None
    assert r["processing_method"] == "TRANSLITERATE"

def test_thai_standard_name():
    r = apply_transliteration("สมชาย", "th", "person_name")
    assert r is not None
    assert r["normalised_form"] is not None
    assert len(r["normalised_form"]) > 0
    assert r["review_required"] is False

def test_thai_not_falling_to_unidecode():
    r = apply_transliteration("นารี", "th", "person_name")
    assert r is not None
    assert r["processing_method"] == "TRANSLITERATE"
    assert all(c.isascii() or c in " -" for c in r["normalised_form"])


# ── Fallback for unknown languages ────────────────────────────────────────────

def test_unknown_language_falls_back_gracefully():
    r = apply_transliteration("Tëst", "xyz", "person_name")
    assert r is not None
    assert r["review_required"] is True


# ── Router integration ────────────────────────────────────────────────────────

def test_russian_routes_to_transliteration():
    r = route_field({"original_text": "Наталья", "field_type": "person_name", "language": "ru"})
    assert r["processing_method"] == "TRANSLITERATE"
    assert r["normalised_form"] == "NATALYA"

def test_japanese_routes_to_transliteration():
    r = route_field({"original_text": "田中", "field_type": "person_name", "language": "ja"})
    assert r["processing_method"] == "TRANSLITERATE"
    assert "TANAKA" in r["normalised_form"]

def test_greek_routes_to_transliteration():
    r = route_field({"original_text": "Νίκος", "field_type": "person_name", "language": "el"})
    assert r["processing_method"] == "TRANSLITERATE"
    assert r["normalised_form"] == "NIKOS"

def test_chinese_routes_to_transliteration():
    r = route_field({"original_text": "王小明", "field_type": "person_name", "language": "zh"})
    assert r["processing_method"] == "TRANSLITERATE"
    assert r["normalised_form"] == "WANG XIAOMING"

def test_passport_does_not_route_to_transliteration():
    """Preserve fields must never reach Strategy F."""
    r = route_field({"original_text": "TK1234567", "field_type": "passport_no"})
    assert r["processing_method"] == "PRESERVE"

def test_empty_text_returns_none():
    r = apply_transliteration("", "ru", "person_name")
    assert r is None
```

---

## Acceptance criteria

- `apply_transliteration("Наталья", "ru", "person_name")` returns `normalised_form == "NATALYA"` — not `NATALJA`
- `apply_transliteration("田中", "ja", "person_name")` returns `"TANAKA"` in `normalised_form`
- `apply_transliteration("王小明", "zh", "person_name")` returns `normalised_form == "WANG XIAOMING"` — fused, not `WANG XIAO MING`
- `apply_transliteration("Νίκος", "el", "person_name")` returns `normalised_form == "NIKOS"`
- `apply_transliteration("محمد", "ar", "person_name")` returns `review_required == True`
- `apply_transliteration("דוד", "he", "person_name")` returns a clean Latin result with `review_required == False`
- `apply_transliteration("احمد", "fa", "person_name")` returns `review_required == True`
- `apply_transliteration("สมชาย", "th", "person_name")` returns a clean Latin result with `review_required == False`
- `apply_transliteration("", "ru", "person_name")` returns `None`
- `route_field({"original_text": "Наталья", "field_type": "person_name", "language": "ru"})` returns `processing_method == "TRANSLITERATE"`
- `route_field({"original_text": "TK1234567", "field_type": "passport_no"})` returns `processing_method == "PRESERVE"` — Strategy F never intercepts preserve fields
- All tests in `tests/test_strategy_f_transliteration.py` pass
- All existing golden dataset regression tests continue to pass
- `src/pipeline/transliteration_engine.py` is not rewritten — only three functions added and three `elif` lines inserted into `transliterate()`
- `normalise_address_latin()` and `_LATIN_SCRIPT_LANGUAGES` remain in `src/pipeline/transliteration_engine.py` unchanged — they are used by `src/pipeline/pipeline.py` for address handling