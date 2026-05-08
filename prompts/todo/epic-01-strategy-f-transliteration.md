# Epic 06 — Strategy F: Transliteration Libraries

## What you need to provide

Nothing. Strategy F is built entirely from existing code and Python libraries. No data files, no downloads, no lookup tables required from you.

---

## What exists in the current codebase

Strategy F is the most developed strategy in the existing codebase. The following is fully implemented and tested in `src/pipeline/transliteration_engine.py`. Copilot moves it into the new structure without modification:

**Carry forward unchanged:**
- `_transliterate_cyrillic()` — Russian, Ukrainian, Bulgarian, Belarusian via `transliterate` library with BGN/PCGN post-processing corrections (`_BGN_PCGN_CORRECTIONS` table, word-initial Е→Ye regex, soft/hard sign stripping)
- `_transliterate_greek()` — ISO 843 via `transliterate` library, ου→ou post-processing fix
- `_transliterate_belarusian()` — pre-processing substitutions before `transliterate` library call
- `_transliterate_japanese()` — `pykakasi` Hepburn romanisation, Kanji ambiguity lookup table, `allowed_variants` generation from all listed readings, long vowel macron stripping (ō→o, ū→u), っ double-consonant handling
- `_transliterate_chinese()` — `pypinyin` Pinyin, given-name fusion (Wang Xiaoming not Wang Xiao Ming), Cantonese/Wade-Giles variant generation via `_add_cantonese_variants()`
- `_transliterate_arabic()` — consonant skeleton map (`_ARABIC_MAP`), compound token pre-processing (`_ARABIC_TOKENS`). Always flags `review_required=True` because short vowels are absent from text — this is correct and intentional in Phase 1
- `_apply_bgn_pcgn_corrections()` — ordered substitution table for Russian/Ukrainian corrections
- `_to_latin_fallback()` — unidecode fallback for unrecognised languages, always flags `review_required=True`
- `_build_result()` — standard result dict builder
- `_normalise()` — NFKC + uppercase helper

**Also carry forward — Korean handler from `_normalise_korean()`:**
- Revised Romanisation via `korean-romanizer` library with hard-coded `KOREAN_SURNAME_VARIANTS` fallback
- Given name fused and hyphenated variants both generated
- McCune–Reischauer variants for documented surnames

**Note on Arabic:** The Arabic handler produces a consonant skeleton only and always flags for native speaker review. This is the correct Phase 1 behaviour — do not change it. Phase 2 adds LLM vowel insertion controlled by `LLM_ENABLED` in `.env`.

---

## What does NOT exist and must be built

Three languages currently fall through to `_to_latin_fallback()` (unidecode) in the existing routing. The `transliterate` library already supports them — they just need to be wired in:

### Hebrew (`he`)
`transliterate` library supports Hebrew transliteration. Wire into the routing function. Apply the same pattern as Greek: call the library, apply any post-processing corrections needed to match ISO 259 output, flag `review_required=False` for standard cases.

Hebrew-specific considerations:
- Final letter forms (ך, ם, ן, ף, ץ) — these are the same letters as כ, מ, נ, פ, צ but written differently at word end. The library handles this but verify output is consistent.
- Shin dot (שׁ→SH) vs Sin dot (שׂ→S) — when diacritics are present in the input, the library should distinguish these. When absent (standard unvocalised Hebrew text), shin and sin are both ש and should map to SH (the more common name component).
- Add a known correction table analogous to `_BGN_PCGN_CORRECTIONS` for any systematic library output errors.

### Persian / Farsi (`fa`)
`transliterate` library supports Persian. Wire into routing. Flag `review_required=True` always — Persian is a vowel-omitting abjad like Arabic, so short vowels cannot be recovered from consonant-only text. The consonant skeleton is useful as a screening variant but must not be presented as a confirmed romanisation.

### Thai (`th`)
`transliterate` library supports Thai (Royal Thai General System of Transcription). Wire into routing. Thai does not have capitalisation or spaces between words — the library handles word segmentation. Flag `review_required=False` for clear output, `review_required=True` where the library signals ambiguity.

---

## What this epic builds

### `app/pipeline/normalisation/transliteration.py` — NEW FILE

This is a direct refactor of `src/pipeline/transliteration_engine.py` into the new structure. The logic is identical — only the following change:

1. All imports updated to new module paths (`app.data.normalisation.kanji_lookup` etc.)
2. Three new language handlers added: `_transliterate_hebrew()`, `_transliterate_persian()`, `_transliterate_thai()`
3. Routing function updated to call the three new handlers before falling through to `_to_latin_fallback()`
4. Latin-script handlers (`de`, `fr`, `es`, `it`, `en`) removed from this module — they move to Strategy G (Epic 07). The routing function delegates these to `app.pipeline.normalisation.character_maps` instead.

**Updated routing function signature:**

```python
def apply_transliteration(text: str, language: str, field_type: str, country: str = "") -> dict | None:
    """
    Strategy F entry point called by the normalisation router.

    Converts non-Latin script text to Latin using established international
    standards. Generates allowed_variants list for all outputs.

    Returns None only if the field_type is not a transliteration field.
    For unrecognised languages, returns a result with review_required=True
    and processing_method=FALLBACK rather than None, so the router does not
    continue to Strategy G for non-Latin text.

    Args:
        text: Original text in source script.
        language: ISO 639-1 language code.
        field_type: KYC field type string.
        country: ISO 3166-1 alpha-2 country code (used by Chinese handler
                 to determine Cantonese variant generation for HK/TW).
    """
```

**New routing block to add (insert before the `else` fallback):**

```python
    elif language == "he":
        return _transliterate_hebrew(text)
    elif language == "fa":
        return _transliterate_persian(text)
    elif language == "th":
        return _transliterate_thai(text)
    elif language in ("de", "fr", "es", "it", "nl", "tr", "pl", "pt", "sv", "no", "da", "en"):
        # Latin-script languages — delegate to Strategy G (character maps)
        # Return None so the router continues to the next strategy
        return None
```

**New handlers to implement:**

```python
def _transliterate_hebrew(text: str) -> dict:
    """
    Hebrew → Latin transliteration using the transliterate library (ISO 259).

    Post-processing:
    - Apply correction table for known library output errors
    - Shin without dot → SH (not S)
    - Final letter forms handled by library — verify consistency

    review_required: False for standard output.
    """

def _transliterate_persian(text: str) -> dict:
    """
    Persian/Farsi → Latin consonant skeleton.

    Always flags review_required=True because short vowels are not written
    in standard Persian text. The consonant skeleton is stored as an
    allowed_variant only, not as the normalised_form.

    Same limitation as Arabic — Phase 2 LLM handles vowel insertion.
    """

def _transliterate_thai(text: str) -> dict:
    """
    Thai → Latin using Royal Thai General System of Transcription (RTGS)
    via the transliterate library.

    Thai-specific considerations:
    - No spaces between words in Thai — library handles segmentation
    - No capitalisation in Thai — apply title case to output
    - Tones are not represented in RTGS output (correct for KYC purposes)

    review_required: False for standard output.
    """
```

### `requirements.txt`

No new libraries required. `transliterate`, `pykakasi`, `pypinyin`, `korean-romanizer`, and `unidecode` are already in `requirements.txt`. Verify they are all present — if any are missing, add them.

---

## Tests

`tests/test_strategy_f_transliteration.py`

Carry forward all existing transliteration tests from the golden dataset. Add new tests for the three new language handlers:

```python
# --- Existing — carry forward and verify still pass ---
def test_russian_bgn_pcgn(): ...               # Наталья → NATALYA (not NATALJA)
def test_ukrainian_exclusive_chars(): ...       # Є, І, Ї handled correctly
def test_belarusian_auto_detect(): ...          # Ў triggers Belarusian mode
def test_greek_ou_correction(): ...             # ου → OU not OY
def test_japanese_kana_hepburn(): ...           # ひらがな → correct Hepburn
def test_japanese_kanji_ambiguity(): ...        # 健 → KEN with KEN/TAKESHI/MASARU variants
def test_japanese_long_vowel_no_macron(): ...   # ō → O, ū → U
def test_chinese_pinyin_given_name_fusion(): .. # 王小明 → WANG XIAOMING
def test_chinese_cantonese_hk_variants(): ...   # HK documents get Cantonese variants
def test_korean_rr_primary(): ...               # 이 → I (RR) with LEE/YI/RHEE variants
def test_arabic_consonant_skeleton(): ...       # محمد → MHM_D consonant skeleton, review=True
def test_arabic_always_review_required(): ...

# --- New ---
def test_hebrew_standard_name(): ...            # דוד → DAVID (or DAVAD — verify with library)
def test_hebrew_shin_without_dot(): ...         # ש → SH
def test_hebrew_final_letters(): ...            # ך behaves same as כ in output
def test_hebrew_review_not_required(): ...      # Standard Hebrew output review_required=False

def test_persian_consonant_skeleton(): ...      # احمد → consonant skeleton
def test_persian_always_review_required(): ...  # review_required=True always

def test_thai_standard_name(): ...              # สมชาย → SOMCHAI (verify with library)
def test_thai_review_not_required(): ...

# --- Routing ---
def test_latin_languages_return_none(): ...     # "de", "fr", "es" → None (delegate to G)
def test_unknown_language_returns_fallback(): ... # "xyz" → unidecode, review_required=True
def test_returns_none_for_non_name_field(): ... # field_type="legal_form" → None

# --- Regression gate ---
def test_golden_dataset_f_scores_unchanged(): ... # All existing golden dataset F scores pass
```

---

## Acceptance criteria

- All existing golden dataset regression tests continue to pass — no existing transliteration behaviour changes.
- `apply_transliteration("Наталья", language="ru", field_type="person_name")` returns `normalised_form == "NATALYA"` (not `NATALJA`).
- `apply_transliteration("محمد", language="ar", field_type="person_name")` returns `review_required == True`.
- `apply_transliteration("田中太郎", language="ja", field_type="person_name")` returns a result with `TANAKA` in `normalised_form` and multiple readings in `allowed_variants`.
- `apply_transliteration("Müller", language="de", field_type="person_name")` returns `None` — Latin-script languages are delegated to Strategy G.
- `apply_transliteration("unknown_text", language="xyz", field_type="person_name")` returns a result with `processing_method == FALLBACK` and `review_required == True`.
- Hebrew, Persian, and Thai are no longer routed to `_to_latin_fallback()` — they use their dedicated handlers.
- All new tests pass.
- No LLM is called at any point in this strategy.
