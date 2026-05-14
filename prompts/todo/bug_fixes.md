
## Tier 1 — Pure list/policy edits, near-zero risk (recovers ~8 tests, half a day's work):

Add iban to PRESERVE_FIELDS → fixes A.4.
Create NUMERIC_FIELDS = [share_capital, total_assets, total_liabilities, net_assets, revenue, expenses, number_of_shares, number_of_issued_shares, voting_rights, ownership_percentage] and remove these from PRESERVE_FIELDS. Have B's numeric handler check this list. Fixes B.7–B.10, B.16–B.18.
F returns None for (field_type=person_name, language=ar) — policy gate, route to native review. Fixes I.1.
Remove the dead stub loop (lines 103–109). Cleanup only.

Do these first. They're independent, each tested in isolation, no algorithmic risk.

### Tier 1 todos

- [x] **T1-1** Add `iban` to `PRESERVE_FIELDS` in `router.py` → fixes A.4
- [x] **T1-2** Create `NUMERIC_FIELDS` list in `router.py`; remove financial aggregates from `PRESERVE_FIELDS`; update `_try_strategy_b` to gate on `NUMERIC_FIELDS` for numeric path → fixes B.7–B.10, B.16–B.18
- [x] **T1-3** Add Arabic `person_name` policy gate in `_try_strategy_f`: return `None` when `field_type == "person_name"` and `language == "ar"` → fixes I.1
- [x] **T1-4** Remove dead stub loop (lines 103–109 of `router.py`) — B and C stubs that can never fire → cleanup only


## Tier 2 — Bounded algorithmic fixes (recovers ~12 tests, 2–3 days):

Fix G's character maps against ICAO Doc 9303 — German ü→UE, ß→SS, Spanish ñ→N, Turkish İ→I, Polish Ł→L. Add French ç/é/è etc. to G's table so G handles it instead of F. Gate G to return None rather than partial output when no entry exists for a char. Fixes G.1–G.5, G.8.
C suffix-extraction mode for company names: tokenise on whitespace and CJK boundaries, scan trailing tokens against the legal-form lookup, extract+normalise the suffix, hand the residual back to F or G. Fixes C.10–C.12, E.2.
Fix calendar handlers in B — Hebrew offset (likely a base-year bug in the library wrapper), Thai Buddhist Era year-only parsing, Hijri day-first parsing. Fixes B.13–B.15.

### Tier 2 todos

**T2-G: G character map priority over D and F (6 tests: G.1–G.5, G.8)**
- [ ] **T2-G-1** Move `_try_strategy_g` call above `_try_strategy_d` in `route_field()` — G must run before geographic lookup intercepts city/address fields with the right output but wrong method
- [ ] **T2-G-2** In `apply_character_map`, add a guard: after running the handler, if `normalised_form == original_text.upper()` and no char in the text is in the language's map, return `None` (no-op — let next strategy try) — prevents G from swallowing fields that don't need it
- [ ] **T2-G-3** Fix `_normalise_german` / `_normalise_french` / `_normalise_spanish` in `transliteration_engine.py`: override `processing_method` to `"CHARACTER_MAP"` after calling `_build_result`, so the method label is correct when called via Strategy G's `character_map_normaliser.py`  
  _Alternative_: override in `character_map_normaliser.py`'s handler wrappers — set `result["processing_method"] = "CHARACTER_MAP"` before returning (preferred — keeps the fix local to G)

**T2-C: C suffix extraction for company names (3 tests: C.10–C.12)**
- [ ] **T2-C-1** In `vocabulary_lookup.py`: after exact-match miss on `company_name`/`legal_name` fields, tokenise the text, scan the trailing 1–2 tokens against the legal-form table (all languages), and if a suffix match is found, return a result with the normalised suffix plus the residual company name in `normalised_form` and `processing_method = "VOCABULARY"`
- [ ] **T2-C-2** Handle CJK boundary tokenisation: for Japanese/Chinese text without spaces, split at the last 2–3 CJK characters and probe those against the legal-form table (株式会社, 有限公司, etc.)

**T2-B: Calendar edge cases (4 tests: B.6, B.13, B.14, B.15)**
- [ ] **T2-B-1** B.6 Minguo: fix epoch arithmetic in `calendar_rules.py` — ROC year + 1911 should yield the Gregorian year; check whether the converter is adding 1911 or 1912
- [ ] **T2-B-2** B.13 Thai `พ.ศ.` label: extend the Thai Buddhist Era parser to recognise the `พ.ศ.` prefix before the year digits (currently only handles bare year)
- [ ] **T2-B-3** B.14 Hijri day-first with Arabic-Indic digits: ensure the Hijri parser normalises Arabic-Indic digits to ASCII before parsing and handles DD/MM/YYYY order
- [ ] **T2-B-4** B.15 Hebrew spelled-out date: fix base-year offset — check the Hebrew calendar library wrapper's epoch constant (should be 3761 BC baseline)


## Tier 3 — Structural (no test recovery, reduces future bugs):

Replace the GPT-4o-mini classifier with deterministic detection (regex for emails/IBANs/dates, lookup for legal-form tokens, default to person_name with analyst-confirm badge in the UI). This recovers A.5, E.1, E.3 and removes the reproducibility floor for AIG submission. Until this is done, you can't reliably hit 100% even with perfect strategies, and you can't reproduce failures to debug them.
Once Tiers 1–2 are done, look at what's left and decide whether to refactor the router. If you're at 70+/74 with a small known residual, the dispatch table refactor is optional. If genuine cross-strategy interference keeps biting, do it then — driven by real evidence, not anticipation.

### Tier 3 todos

- [ ] **T3-1** Replace GPT-4o-mini classifier with deterministic field-type detector: regex for email/IBAN/date patterns, legal-form token lookup for company fields, default `person_name` with analyst-confirm flag — recovers A.5, E.1, E.3 and makes the suite fully reproducible