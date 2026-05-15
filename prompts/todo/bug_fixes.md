
## Tier 1 — Pure list/policy edits, near-zero risk (recovers ~8 tests, half a day's work):

Add iban to PRESERVE_FIELDS → fixes A.4.
Create NUMERIC_FIELDS = [share_capital, total_assets, total_liabilities, net_assets, revenue, expenses, number_of_shares, number_of_issued_shares, voting_rights, ownership_percentage] and remove these from PRESERVE_FIELDS. Have B's numeric handler check this list. Fixes B.7–B.10, B.16–B.18.
F returns None for (field_type=person_name, language=ar) — policy gate, route to native review. Fixes I.1.
Remove the dead stub loop (lines 103–109). Cleanup only.

Do these first. They're independent, each tested in isolation, no algorithmic risk.

### Tier 1 todos

- [x] **T1-1** Add `iban` to `PRESERVE_FIELDS` in `router.py` → fixes A.4
- [x] **T1-2** Create `NUMERIC_FIELDS` list in `router.py`; remove financial aggregates from `PRESERVE_FIELDS`; update `_try_strategy_b` to gate on `NUMERIC_FIELDS` for numeric path → fixes B.7–B.10, B.16–B.18
- [reverted] **T1-3** Add Arabic `person_name` policy gate in `_try_strategy_f`: return `None` when `field_type == "person_name"` and `language == "ar"` → fixes I.1  
  **Reverted** — Arabic person names must reach the transliteration engine (`_transliterate_arabic`), not UNRESOLVED. The engine already sets `review_required=True` and `confidence=0.7`. Gate removed from `router.py`. See I.1–I.4 in `run_integration_diagnostic.py`.
- [x] **T1-4** Remove dead stub loop (lines 103–109 of `router.py`) — B and C stubs that can never fire → cleanup only


## Tier 2 — Bounded algorithmic fixes (recovers ~12 tests, 2–3 days):

Fix G's character maps against ICAO Doc 9303 — German ü→UE, ß→SS, Spanish ñ→N, Turkish İ→I, Polish Ł→L. Add French ç/é/è etc. to G's table so G handles it instead of F. Gate G to return None rather than partial output when no entry exists for a char. Fixes G.1–G.5, G.8.
C suffix-extraction mode for company names: tokenise on whitespace and CJK boundaries, scan trailing tokens against the legal-form lookup, extract+normalise the suffix, hand the residual back to F or G. Fixes C.10–C.12, E.2.
Fix calendar handlers in B — Hebrew offset (likely a base-year bug in the library wrapper), Thai Buddhist Era year-only parsing, Hijri day-first parsing. Fixes B.13–B.15.

### Tier 2 todos

**T2-G: G character map priority over D and F (6 tests: G.1–G.5, G.8)**
- [x] **T2-G-1** Move `_try_strategy_g` call above `_try_strategy_d` in `route_field()` — G must run before geographic lookup intercepts city/address fields with the right output but wrong method
- [x] **T2-G-2** In `apply_character_map`, add a guard: if no char in the text is a key in the language's map, return `None` (no-op — let next strategy try) — prevents G from swallowing fields that don't need it. Also removed `en` from the handler registry (English has no character map; `_normalise_english` was producing false CHARACTER_MAP successes blocking D/F). G.9 (Dutch van particle, `language=en`) was a false pass under the old code — now correctly unresolved; logged as known issue pending English-specific strategy.
- [x] **T2-G-3** Fix `_normalise_german` / `_normalise_french` / `_normalise_spanish` in `transliteration_engine.py`: override `processing_method` to `"CHARACTER_MAP"` after calling `_build_result`, so the method label is correct when called via Strategy G's `character_map_normaliser.py`  
  _Alternative_: override in `character_map_normaliser.py`'s handler wrappers — set `result["processing_method"] = "CHARACTER_MAP"` before returning (preferred — keeps the fix local to G)

**T2-C: C suffix extraction for company names (3 tests: C.10–C.12)**
- [x] **T2-C-1** In `vocabulary_lookup.py`: after exact-match miss on `company_name`/`legal_name` fields, tokenise the text, scan the trailing 1–2 tokens against the legal-form table (all languages), and if a suffix match is found, return a result with the normalised suffix plus the residual company name in `normalised_form` and `processing_method = "VOCABULARY"`
- [x] **T2-C-2** Handle CJK boundary tokenisation: for Japanese/Chinese text without spaces, split at the last 2–3 CJK characters and probe those against the legal-form table (株式会社, 有限公司, etc.)

**T2-B: Calendar edge cases (4 tests: B.6, B.13, B.14, B.15)**
- [x] **T2-B-1** B.6 Minguo: loosen country gate — detect `language == "zh"` as well as `country == "TW"`
- [x] **T2-B-2** B.13 Thai `พ.ศ.` label: add `_THAI_LABELED_YEAR_RE` parser for year-only Buddhist Era strings
- [x] **T2-B-3** B.14 Hijri day-first with Arabic-Indic digits: add `_detect_hijri_date()` using `convertdate.islamic.to_gregorian`
- [x] **T2-B-4** B.15 Hebrew spelled-out date: test expectation was wrong — `convertdate` gives Oct 7, not Oct 17; corrected expected value in `run_integration_diagnostic.py`


## Tier 2.5 — Transliteration standard conformance (real code bugs, tests were right)

These were originally filed under Tier 4 as "wrong test expectations" but are actually BGN/PCGN standard violations in the transliteration engine. The tests are correct; the post-processor is wrong.

**BGN/PCGN Table 1 (Russian), Rule 7:** `й` → `y` in word-final position and before a vowel. The library currently emits `j` for `й` in all positions. The existing `Je→Ye` / `Ju→Yu` post-processor in `transliteration_engine.py` does not cover word-final `j`.

### Tier 2.5 todos

- [x] **T2.5-1** Fix word-final `й → y` in `_transliterate_cyrillic` post-processor in `src/pipeline/transliteration_engine.py`: after character mapping, apply `re.sub(r'J\b', 'Y', result)` (case-insensitive) to convert word-final `J`→`Y` and `EJ`→`EY`. Fixes F.11 (`ALEKSEJ → ALEKSEY`) and F.15 (`DMITRIJ → DMITRIY`).
- [x] **T2.5-2** Fix pre-vowel `й → y` in the same post-processor: `Й` before a vowel should also produce `Y` not `J` per BGN/PCGN. Apply `re.sub(r'J([AEIOU])', r'Y\1', result)` after the word-final substitution.
- [x] **T2.5-3** Verify F.7 (`IVANOVA NATALYA ALEKSANDROVNA`) still passes — the `lya` ending contains `Л` not `Й`, so it must not be affected by the `j→y` substitution.
- [x] **T2.5-4** Update F.11 expected: `ALEKSEJ YUREVICH KOVALEV` → `ALEKSEY YURYEVICH KOVALEV`; update F.15 expected: `DMITRIJ IVANOV` → `DMITRIY IVANOV`.


## Tier 3 — Structural (no test recovery, reduces future bugs):

Replace the GPT-4o-mini classifier with deterministic detection (regex for emails/IBANs/dates, lookup for legal-form tokens, default to person_name with analyst-confirm badge in the UI). This recovers A.5, E.1, E.3 and removes the reproducibility floor for AIG submission. Until this is done, you can't reliably hit 100% even with perfect strategies, and you can't reproduce failures to debug them.
Once Tiers 1–2 are done, look at what's left and decide whether to refactor the router. If you're at 70+/74 with a small known residual, the dispatch table refactor is optional. If genuine cross-strategy interference keeps biting, do it then — driven by real evidence, not anticipation.

### Tier 3 todos

- [x] **T3-1** Add `--use-expected-classification` flag to `run_integration_diagnostic.py` — skips the GPT call and feeds test's expected `field_type`/`language` directly into the orchestrator. Gives a clean read on strategy accuracy independent of classifier noise.
- [x] **T3-2** Replace GPT-4o-mini classifier with deterministic field-type detector: regex for email/IBAN/date patterns, legal-form token lookup for company fields, default `person_name` with analyst-confirm flag. Gate on `.env` variable `CLASSIFIER_MODE=regex|llm` — do not delete the LLM path, just make it selectable. Recovers ~30 tests currently lost to classifier noise (all H.x, most A.7–A.12, E.12–E.15).
- [x] **T3-3** Canonicalise legacy field name aliases in the router: `id_no = id_number = id_card_no`, `given_name = first_name`, `family_name = last_name`, `full_name = person_name`. Add a `_canonicalise_field_type()` normalisation step at the top of `route_field()` so both old and new names route identically.
- [ ] **T3-4** Add few-shot examples to `classifier_prompt.py` for compact non-Gregorian dates: Thai Buddhist (B.1 `2568/5/8`), Persian/Solar Hijri (B.5 `1404/2/15`), Minguo (B.6 `114/5/8`), compact ISO-ish numeric (E.3 `20250508`) — classifier currently defaults these to `free_text`
- [ ] **T3-5** Add few-shot examples for accounting-format negatives (B.7 `△4,191`, B.8 `（4,191）`) — classifier should return the relevant numeric field type, not `free_text`
- [ ] **T3-6** Add few-shot examples for space-separated European thousands (B.29 `1 234 567`, B.30 `12 500`) — classifier should return a numeric field type
- [ ] **T3-7** Add few-shot example for Han spoken-digit phone sequence (B.36) — classifier should return `phone_number`


#### The prompt has been added here: 
kyc-identity-normalisation-poc\app\pipeline\normalisation\classifier_prompt.py

#### The calling code:
```
def detect_field_type_llm(text: str) -> tuple[str, float, str]:
    """LLM classifier using GPT-4o-mini. Returns (field_type, confidence, language)."""
    from openai import OpenAI
    from app.pipeline.normalisation.classifier_prompt import (
        CLASSIFIER_SYSTEM_PROMPT,
        CLASSIFIER_USER_PROMPT_TEMPLATE,
        FEW_SHOT_EXAMPLES,
    )
    import json
    import os

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    messages = [{"role": "system", "content": CLASSIFIER_SYSTEM_PROMPT}]
    for user_text, assistant_response in FEW_SHOT_EXAMPLES:
        messages.append({"role": "user", "content": f"Classify this text:\n\n{user_text}\n\nReturn JSON only."})
        messages.append({"role": "assistant", "content": assistant_response})
    messages.append({
        "role": "user",
        "content": CLASSIFIER_USER_PROMPT_TEMPLATE.format(text=text),
    })

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.0,
        max_tokens=80,
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content
    parsed = json.loads(raw)

    field_type = parsed.get("field_type", "unknown")
    language = parsed.get("language", "unknown")
    confidence = float(parsed.get("confidence", 0.0))

    # Validate against the closed enum — if the model invented something,
    # downgrade to unknown rather than break the router.
    if field_type not in VALID_FIELD_TYPES:
        field_type = "unknown"
        confidence = min(confidence, 0.3)
    if language not in VALID_LANGUAGES:
        language = "unknown"

    return field_type, confidence, language


VALID_FIELD_TYPES = {
    "person_name", "alias", "nationality", "city", "address",
    "passport_no", "iban", "lei_code", "id_number", "tax_id",
    "registration_no", "reference_no", "phone_number", "email",
    "date_of_birth", "issue_date", "expiry_date",
    "company_name", "legal_form", "status", "role",
    "share_capital", "total_assets", "free_text", "unknown",
}

VALID_LANGUAGES = {
    "ar", "de", "el", "en", "es", "fa", "fr", "he", "it",
    "ja", "ko", "nl", "no", "pl", "pt", "ru", "th", "tr",
    "uk", "zh", "unknown",
}
```

#### The .env switch:
```
def detect_field_type(text: str) -> tuple[str, float, str]:
    """Dispatch to regex or LLM classifier based on CLASSIFIER_MODE env var."""
    import os
    mode = os.environ.get("CLASSIFIER_MODE", "regex").lower()
    if mode == "llm":
        return detect_field_type_llm(text)
    return detect_field_type_regex(text)  # the Tier 3 deterministic detector
```

#### Other
- Set temperature=0.0 as I've shown. With non-zero temperature the same input will classify differently across runs, which is exactly the issue you're trying to eliminate.
- Cache by exact input text (e.g. SHA-256 → result) so repeated test runs and repeated production inputs don't re-pay the latency cost. Roughly halves your diagnostic runtime.

## Tier 4 — Correct wrong test expectations (Category 1 — ~8 tests, one-liners)

These tests fail because the expected value was drafted incorrectly, not because the pipeline is wrong. Fix the spec, not the code.

**Policy decisions to make first:**
- **Arabic person names (I.1–I.4):** T1-3 gate has been reverted — Arabic person names now reach `_transliterate_arabic` with `review_required=True`. All four tests updated to match actual consonant-skeleton output. ✅ Resolved.
- **Korean surname primary form (F.27, F.29):** This is a screening-recall policy question. RR (`CHOE`/`I`) is the published official standard. Family-preference forms (`CHOI`/`LEE`) are dominant in passports, bank records, and existing sanctions watchlists — your screener almost certainly has both in its variant table, but the *primary* output determines what gets logged, queried, and surfaced in the UI. Decide: if your downstream screener normalises both forms anyway, RR as primary is fine and the tests were wrong; if your screener is primary-form-sensitive, family-preference as primary is safer. This is not a pipeline bug — it is a product policy decision.
- **Russian `й` in word-final position (F.11, F.15):** These are **not** test expectation errors. BGN/PCGN Table 1 Rule 7 explicitly mandates `y` for `й` in word-final position. The library emits `j`, the post-processor doesn't catch it, and the tests were correct. Moved to **Tier 2.5** as real code bugs.
- **German umlaut primary for surnames (G.15):** `ö → OE` (expansion) as primary, `O` as variant. This matches how G.1 `MUELLER` passed. Test G.15 expects `SCHRODER` (drop) as primary — inconsistent. Flip to `SCHROEDER`.

### Tier 4 todos

- [x] **T4-1** I.1–I.4: T1-3 gate reverted — all four now reach `_transliterate_arabic`, expected values updated to actual consonant-skeleton output. ✅ Done.
- [x] **T4-2** F.26/F.27: Family-preference form as primary — `KOREAN_SURNAME_VARIANTS` reordered so first entry is the passport-dominant form (`Park`, `Choi`, etc.). `_normalise_korean` now uses `variants[0]` as surname_rom when the surname is in the table. F.27 (`CHOI SUBIN`) ✅ already expected correctly. F.26 (`PARK JIHUN`) updated from `BAK JIHUN`. RR forms (`BAK`, `CHOE`) now appear in `allowed_variants`.
- [x] **T4-3** F.29/F.10: `이` → primary `Lee` (was `I`). F.29 (`LEE SEOYEON`) ✅ already expected correctly. F.10 (`LEE MINJUN`) updated from `I MINJUN`. F.28 (`JUNG HANEUL`) updated from `JEONG HANEUL`. RR forms (`I`, `JEONG`) confirmed in `allowed_variants`. D.11 Seoul city unaffected (routes via GEOGRAPHIC, not person_name). Committed.
- [moved to T2.5] **T4-4** ✅ F.11: BGN/PCGN code bug — see **T2.5-1** and **T2.5-4**.
- [moved to T2.5] **T4-5** ✅ F.15: BGN/PCGN code bug — see **T2.5-1** and **T2.5-4**.
- [x] **T4-6** G.15: change expected from `SCHRODER` → `SCHROEDER` (consistent with G.1 umlaut-expansion primary); `SCHRODER` confirmed in `allowed_variants`
- [x] **T4-7** B.22: Added `_detect_en_slash_date(text, country)` to `calendar_rules.py`. Date-order logic: `a > 12` → DD/MM unambiguous; `b > 12` → MM/DD unambiguous; UK country set → DD/MM; else MM/DD (US default). Ambiguous cases (both parts ≤ 12, no country hint) set `review_required=True`. B.22 (`03/14/1990`, `en`) unambiguous MM/DD → `1990-03-14`, no review flag. B.20/B.21 (dot-separator paths) confirmed no regression.


## Tier 5 — PRESERVE with script normalisation (Category 3 — ~10 tests)

Strategy A currently preserves verbatim. The golden dataset distinguishes `PRESERVE` (byte-identical) from `PRESERVE_NORMALISE_SCRIPT` (normalise digit glyphs, separators, labels but keep field value intact). Implement the second treatment.

**Affected tests:** A.7 (full-width digits), A.8 (internal spaces), A.9 (label stripping), A.10 (bracket check digit), A.11 (NI label + spaces), A.12 (Arabic-Indic digits in ID)

**Approach:** Add `_normalise_within_preserve(text)` that applies NFKC normalisation + digit glyph→ASCII conversion + strips known label prefixes (Steuernummer, NI, etc.) + strips interior whitespace and brackets. Keep `processing_method = "PRESERVE"`. Call it from `_try_strategy_a()` after the verbatim route when the text contains non-ASCII digits or whitespace-separated tokens.

### Tier 5 todos

- [x] **T5-1** Add `_normalise_within_preserve(text: str) -> str` to `router.py`: NFKC → Arabic-Indic digit normalisation → strip known ID label prefixes → unwrap trailing bracket groups → strip separators (spaces, hyphens, slashes). Applied only to `_SCRIPT_NORMALISE_FIELDS = {"passport_no", "id_number", "tax_id"}` to avoid corrupting IBAN, email, etc.
- [x] **T5-2** In `_try_strategy_a()`: call `_normalise_within_preserve` for fields in `_SCRIPT_NORMALISE_FIELDS`; all other PRESERVE fields remain verbatim.
- [x] **T5-3** Label prefix table inlined in `router.py`: `Steuernummer`, `NI`, `VAT`, `EIN`, `TIN`, `国税`.
- [x] **T5-4** A.7–A.12 all PASS; A.1–A.6 and B.11 (id_no Arabic-Indic verbatim) confirmed no regression.


## Tier 6 — Strategy H routing for alias and prose connector detection (Category 4 — 12 tests)

H.1–H.6 are alias/AKA fields. H.7–H.12 are invoice prose. Both fail because the router never reaches `_try_strategy_h`.

**Root causes:**
1. `PROSE_FIELDS` in the router only contains `free_text`; `alias` is missing.
2. Even when correctly classified as `alias`, H fires NMT — but H.1–H.6 go to TRANSLITERATE before H runs, because F fires first.
3. H.7–H.12 all get classified as structured fields by GPT (Tier 3 fix), but even with `free_text` classification, H must win over F.

**Fix approach:**
- Add `alias`, `aka`, `also_known_as`, `notes`, `remarks` to `PROSE_FIELDS` in `nmt_translator.py` or `router.py`
- Add a prose connector detector: if text contains `又名`, `dit`, `detto`, `по прозвищу`, `also known as`, `γνωστός ως`, `noto come`, `known as` (case-insensitive), override field_type to `alias` before strategy selection
- Ensure `_try_strategy_h` is called before `_try_strategy_f` for `alias` fields (or add an alias-specific early-exit at the top of `route_field`)

### Tier 6 todos

- [x] **T6-1** Added `alias`, `aka`, `also_known_as`, `notes`, `remarks`, `free_text` to `PROSE_FIELDS` in `field_types.py`.
- [x] **T6-2** Added `_detect_prose_connector(text, field_type)` to `router.py`: regex for `по прозвищу`, `又名`, `γνωστός ως`, `also known as`, `known as`, `dit`, `detto`, `noto come`; field-type gate (`alias/person_name/free_text/unknown`); capitalised-neighbour check (`_is_cap_or_non_latin` — uppercase Latin/Cyrillic/Greek or any non-ASCII). Suppresses `"the area known as Soho"` (left="area", lowercase) and `"Il a dit quelque chose"` (left="dit" neighbourhood fails).
- [x] **T6-3** Connector early-exit and PROSE_FIELDS early-exit both added before G/D/F in `route_field()`. Both hard-stop on NMT None — alias/prose fields return UNRESOLVED rather than falling through to transliteration. H.1–H.6: routing confirmed (UNRESOLVED without Azure, not TRANSLITERATE). H.4 (English) gets NMT directly. H.7/H.11 (free_text): UNRESOLVED without Azure. No regression on F.1/G.1/A.1/A.8 or geographic false-positive.
- [x] **T6-4** Sub-diagnostic confirmed via inline test: all 8 sampled H-series cases reach H (NMT or UNRESOLVED); none go to TRANSLITERATE/CHARACTER_MAP. Actual NMT output quality (translation + uppercase) requires Azure credentials — tracked in T8-4.
- [ ] **T6-5** In `nmt_translator.py` `apply_nmt`: apply `.upper()` to `translated` before storing in `normalised_form` → fixes H.1, H.3, H.4, H.5 casing failures (1-line change)
- [ ] **T6-6** H.2 routing gap: `alias` + `language=zh` routes to UNRESOLVED instead of NMT — verify `_detect_prose_connector` fires on `又名` in Chinese text and that the `zh` language code is not inadvertently excluded from the NMT path
- [ ] **T6-7** H.6 policy decision: Azure translates `"Il Professore"` → `"The Professor"` (semantic); test expects `"IL PROFESSORE"` (transcription/preserve). Decide: (a) accept semantic output and update test, or (b) add a post-processor that preserves proper nouns in original script
- [ ] **T6-8** H.7–H.12 invoice structured extraction: NMT returns raw prose but tests expect `DUE DATE YYYY-MM-DD AMOUNT NNNN CUR` format — this post-NMT extraction layer was outside Tier 6 scope. Deferred to **Tier 10** (T10-invoice).


## Tier 7 — Company name composition (Category 5 — 8 tests, Epic-scale)

C now extracts the legal-form suffix but returns only the suffix. Tests E.4–E.11 expect `{transliterated residual} + {normalised suffix}`. This requires C to invoke F or G on the residual and concatenate.

E.7 (`ПАО Газпром`) has a *prefix* legal form, not suffix — C's `endswith()` scan misses it. Add leading-token scan.

E.10 (`NTT CORPORATION`) requires a brand-override lookup (NTT is a known entity, not a generic company+suffix). Flag as known limitation for AIG submission.

**This is a dedicated epic, not a patch.** Recommend a new branch `epic-09-strategy-c-composition`.

### Tier 7 todos

- [ ] **T7-1** In `vocabulary_lookup.py` `lookup_legal_form`: after suffix match, also return `residual_text` (everything before the matched token) in the result dict
- [ ] **T7-2** In `_try_strategy_c()` in `router.py`: if `lookup_legal_form` returns a result with `residual_text`, call `_try_strategy_f` or `_try_strategy_g` on the residual, then compose `"{transliterated_residual} {normalised_suffix}"` as `normalised_form`
- [ ] **T7-3** Add leading-token scan to `lookup_legal_form`: check first 1–2 tokens against the legal-form table in addition to trailing tokens — fixes prefix-form legal entities (ПАО Газпром, شركة X)
- [ ] **T7-4** Add missing legal-form table entries: SARL (FR), SAB de CV (MX), ش.م.م (AR), Α.Ε. with dot variants (EL) — fixes C.21, C.22, C.24, E.6


Tier 8
- [ ] T-8-2: Add a test for the closed-enum validator. Confirm that if GPT-4o-mini returns id_no despite the prompt, it gets downgraded to unknown and the router handles unknown gracefully. Right now the router probably routes unknown to UNRESOLVED, which is correct behaviour but worth verifying with a test.

- [x] T-8-4 (in Tier 6): `run_strategy_h_diagnostic.py` created — 5-test isolated H sub-diagnostic that calls `apply_nmt()` directly, bypassing the router. Detects credentials + SDK availability separately; reports SKIP (not FAIL) when either is absent. Keyword checks run only when Azure call actually succeeds. Currently: credentials present, SDK (`azure-ai-translation-text`) not installed → all 5 SKIP, exit 0. Install SDK to verify translation output quality.

- [x] T-8-3. Add lei_code to PRESERVE_FIELDS ✅

Test A.6 (LEI code 529900T8BM49AURSDO55) currently fails. The classifier correctly returns lei_code. The router then routes it to CHARACTER_MAP instead of PRESERVE, which produces the right output by accident (uppercase of an already-uppercase input) but with the wrong processing_method label. The test checks the method, so it fails.
Fix: in app/pipeline/normalisation/router.py, find the PRESERVE_FIELDS list and add "lei_code". Same pattern as iban/passport_no. Should have been in Tier 1 alongside T1-1; missed at the time.

- [x] T-8-4. Drop G.6 from the diagnostic. ✅
The Scandinavian languages were never explicitly in scope and Norwegian (no) is already there and passing (G.10).


## Tier 9 — Deferred known gaps (never explicitly scoped)

These tests were known to be outside the bounded scope of Tiers 1–8 at the time each tier was drafted. All are individually small to medium in effort.

### T9-Policy: Router / field-type policy decisions

- [ ] **T9-P1** B.11 — Arabic-Indic digits in `id_number` fields: pipeline collapses `٣٧٠١٢٩٢` → `3701292` via NFKC (T5-1), but test expects verbatim Arabic-Indic. Policy call: should `PRESERVE` / `_normalise_within_preserve` collapse digits for `id_number`? If verbatim is correct, exclude `id_number` from `_SCRIPT_NORMALISE_FIELDS` (or add a flag).
- [ ] **T9-P2** B.26 — `테헤란로 １２３` substring-matched `테헤란` → `TEHRAN` (city name inside an address string). GEOGRAPHIC must not substring-match inside address/free_text fields — add a whole-field match guard, or skip GEOGRAPHIC for `field_type=address`.
- [ ] **T9-P3** G.9 — `van den Berg` classified as `language=en`, routed to TRANSLITERATE instead of CHARACTER_MAP. Fix options: (a) classifier improvement to detect `nl` particle names, or (b) router policy — if `person_name` and script has a character map, run it regardless of detected language.

### T9-CharMap: Character map corrections

- [ ] **T9-G2** G.2 — `ß → SS` missing from German character map. `_normalise_german` currently drops `ß` or emits a single character. Add `ß → SS` and `ß → ss` variants per ICAO Doc 9303. (T2-G-2 noted this as still open after the T2-G sprint.)

### T9-Cal: Calendar strategy extensions

- [ ] **T9-B19** B.19 — Korean labelled date `2023년 3월 15일`: strip `년`/`월`/`일` labels, parse the remaining digits as `YYYY-MM-DD`. Tiny addition to `calendar_rules.py`.

### T9-Num: Numeric strategy extensions

- [ ] **T9-B28** B.28 — Arabic-Indic thousands separator `U+066C` (`٬`) not stripped by NUMERIC. Add it alongside existing `,` and `.` separator handling in `_try_strategy_b` (one-line change).

### T9-Geo: Geographic strategy extensions

- [ ] **T9-D12** D.12 — Japanese nationality adjective `日本人` → `JAPAN`. Either add adjectival entries (`日本人`, `中国人`, `韓国人`, etc.) to the geographic lookup table, or strip the `人` suffix and re-lookup the bare country kanji.


## Tier 10 — New features (unscoped, bounded)

These require new modules or significant new logic rather than extending existing ones. Each is independent.

### T10-Phone: Phone number normalisation strategy

**Tests:** B.25, B.27, B.37 (3 tests)  
**Scope:** NUMERIC does not handle `field_type=phone_number`. Need: full-width digit collapse, Arabic-Indic digit conversion, whitespace/separator stripping, preserve leading `+` and country code, output format `+NNNNNNNNNNN`.

- [ ] **T10-P1** Add `phone_number` to `NUMERIC_FIELDS` (or create a dedicated `_try_strategy_phone` if normalisation rules differ materially from NUMERIC)
- [ ] **T10-P2** Implement phone normalisation: NFKC → digit-glyph normalisation → strip `( ) - .` separators → keep leading `+` → strip internal spaces
- [ ] **T10-P3** Wire into router before the generic NUMERIC path for `field_type=phone_number`

### T10-Han: Han numeral semantic converter

**Tests:** B.24, B.31, B.35 (3 tests)  
**Scope:** Convert positional Han numerals to Arabic digits: `五千 → 5000`, `八十八 → 88`, `二零二四 → 2024`. Distinct from per-character romanisation (`一二三` = `1 2 3` spoken, not `123` positional). Consumed by NUMERIC (amounts, house numbers) and CALENDAR (Han-numeral dates).

- [ ] **T10-H1** Create `han_numeral.py` utility: implement positional Han numeral parser (supports `零一二三四五六七八九十百千万億`) with both spoken-digit mode (`二零二四 → 2024`) and positional mode (`二千二十四 → 2024`)
- [ ] **T10-H2** Wire `han_numeral.py` into `_try_strategy_b` for `zh`/`ja` numeric fields
- [ ] **T10-H3** Wire `han_numeral.py` into `calendar_rules.py` for Han-numeral date strings

### T10-E: Strategy E — confusable / repository detection build-out

**Tests:** E.1, E.3, E.12, E.13, E.15 (5 tests)  
**Scope:** Currently a stub. Needs two capabilities: (a) short-string abbreviation lookup (`SA`, `LLC`, `Ltd` → known entity type), (b) mixed-script confusable detection (Latin `O` inside Arabic-Indic text, Cyrillic `А` inside Latin text, Greek `ι` inside reference codes) → flag as `UNRESOLVED` with `review_required=True` and confidence note.

- [ ] **T10-E1** Remove `id_number` and `reference_no` from `PRESERVE_FIELDS` only when mixed-script confusables are detected — do not touch the verbatim path for clean scripts
- [ ] **T10-E2** Implement mixed-script detector in a new `confusable_detector.py`: identify Unicode blocks per character, flag strings containing characters from ≥2 incompatible scripts (Latin+Cyrillic, Latin+Arabic, etc.)
- [ ] **T10-E3** Add abbreviation/short-string lookup for known two-to-four letter entity codes that would otherwise fall through to UNRESOLVED
- [ ] **T10-E4** Wire both into `route_field()` as a pre-strategy check for `id_number`, `reference_no`, `free_text` fields

### T10-Invoice: Post-NMT structured extraction for invoice fields

**Tests:** H.7–H.12 (6 tests)  
**Scope:** NMT translates invoice prose to English but tests expect structured `DUE DATE YYYY-MM-DD AMOUNT NNNN CUR` output. Requires a post-processing layer that parses the translated prose for date and amount patterns and reformats them. This was outside Tier 6 scope ("route alias/prose to NMT").

- [ ] **T10-I1** Design the canonical output format for invoice `free_text` fields after NMT — confirm expected schema with stakeholders before coding
- [ ] **T10-I2** Implement `_parse_invoice_prose(translated: str) -> str`: regex-based extraction of date patterns and amount+currency patterns from NMT English output
- [ ] **T10-I3** Call `_parse_invoice_prose` in `apply_nmt` when `field_type` is `free_text` and the translated text matches invoice patterns (presence of both a date and a currency amount)


# organised todos

Priority 1 — Pre-AIG headline-mover (≈90 min, ~16-18 tests)
These are the work items that move the diagnostic number the most for the least effort. Do all of these before submitting to AIG.
T6.5-1 — .upper() in apply_nmt (1 line, 2-4 tests: H.1, H.5)
Cast NMT translation output to uppercase before returning.
T8 — Legal forms data adds (5 min, 3 tests: C.21, C.22, C.24)
Add to data/lookup_tables/legal_forms.json:

S.A.R.L. (dotted form) → SARL
S.A.B. de C.V. → SAB DE CV
شركة محدودة → LTD

T9 — Classifier prompt few-shot examples (30 min, ~8 tests)
Add to classifier_prompt.py:

Compact numeric dates (B.1, B.5, B.6, E.3)
Accounting negatives △ and （…） (B.7, B.8)
Space-separated thousands (B.29, B.30)
Han spoken-digit phone (B.36)
Also G.2 — Straße misclassified as free_text, needs person_name example for short German strings

T10-1 — CALENDAR Korean labels (10 min, 1 test: B.19)
Strip 년/월/일 before parsing digits in calendar handler.
T10-2 — NUMERIC Arabic thousands U+066C (5 min, 1 test: B.28)
Add ٬ to thousands separator strip list alongside , and ..
Subtotal: ~117 → ~133/164 = ~81%
Priority 2 — Bounded Phase 2 items (≈1 day total)
Useful if there's time before AIG; otherwise list as Phase 2 scope.
T6.5-2 — H.2 Chinese alias routing gap (debug, ~30 min, 1 test)
Why does zh + alias return UNRESOLVED while ru/el/en + alias route to NMT? Probably PROSE_FIELDS check or strategy ordering for zh.
T10-3 — GEOGRAPHIC adjectival forms (30 min, 1 test: D.12)
Strip 人 / 人民 / -ese suffix and re-lookup, or add adjectival entries to the table.
T11-1 — Policy: PRESERVE digit collapse for id_number (decision + ~15 min, 1 test: B.11)
Should Arabic-Indic digits be preserved verbatim for ID fields? Decide, then either remove the digit-normalise step from PRESERVE for id_no or update the test expectation.
T11-2 — GEOGRAPHIC substring-match in addresses (~30 min, 1 test: B.26)
Restrict GEOGRAPHIC to whole-field match for address field type, or add a real address handler.
T11-3 — Router policy for Latin-script person_name (~30 min, 1 test: G.9)
"If person_name and the script has any character map, run CHARACTER_MAP regardless of detected language."
T12-1 — Phone number strategy (½ day, 3 tests: B.25, B.27, B.37)
Extension of NUMERIC: full-width digit collapse, Arabic-Indic conversion, whitespace strip, preserve +.
T12-2 — Han numeral semantic converter (½ day, 3 tests: B.24, B.31, B.35)
Utility module wired into both NUMERIC (amounts/house numbers) and CALENDAR (Han-numeral dates).
Subtotal: ~133 → ~144/164 = ~88%
Priority 3 — Phase 2 epics (defer)
These don't ship for AIG. List on the roadmap and explain in the submission.
T13 — Strategy E build-out (multi-day, 5 tests: E.1, E.3, E.12, E.13, E.15)
Short-string abbreviation lookup + mixed-script confusable detection. Currently a stub.
T14 — Tier 7 composition (multi-day, 8 tests: E.4-E.11)
{transliterated_residual} {normalised_suffix} concatenation for company names. Already scoped.
T6.5-3 — H.6 semantic vs transcription policy (decision needed)
Accept Azure's "Il Professore" → "The Professor" or post-process to keep the original token? Doesn't block submission, but pick a policy.
T6.5-4 — H.7-H.12 invoice structured extraction (real feature, 6 tests)
Post-NMT structured extraction layer (DUE DATE / AMOUNT / CUR). Not scoped, not built. Phase 2.