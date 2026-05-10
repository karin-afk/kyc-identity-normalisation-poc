# Fix Session — Strategy C & Test Quality

**Branch:** `feat/fix-strategy-c-and-tests`
**Date:** 2026-05-10

## Baseline state (before this session)

- Flask app tests: **85 passed**, 0 failed
- src pipeline tests: **144 passed**, 3 failed (all real OpenAI API calls — pre-existing, not code bugs)
- Python runtime used: `C:\Python314\python.exe` (Flask installed in user site-packages)
- Run command: `& "C:\Python314\python.exe" -m pytest -q`

## Context: what is wrong and why

### Problem 1 — Strategy C does not handle `issuing_authority`

The LLM classifier (`field_type_detector.py`) correctly detects `issuing_authority` as the field type
for inputs like `東京都公安委員会`. The router calls `_try_strategy_c()`, which calls
`VocabularyLookupService.lookup()`. However:

1. `issuing_authority` is **missing from `VOCABULARY_FIELDS`** set in `vocabulary_lookup.py`
2. There is **no `elif field_type == "issuing_authority"` branch** in `lookup()` dispatch
3. The lookup data (`issuing_authorities.json`) **exists and is loaded** into `self.issuing_authorities`
4. Result: Strategy C always skips `issuing_authority` → falls through to UNRESOLVED

**Fix:** Add `issuing_authority` to `VOCABULARY_FIELDS` and add `lookup_issuing_authority()` method + dispatch.

### Problem 2 — `app/data/lookup_tables/`, `app/data/geonames/`, `app/data/seed/` are empty dead folders

The todo doc for Strategy C said to save JSON files to `app/data/lookup_tables/` — but the actual service
loads from `data/lookup_tables/` (repo root). The three `app/data/` subdirectories are empty and create
false confusion about where the real data lives.

- `app/data/lookup_tables/` — EMPTY, can be removed
- `app/data/geonames/` — EMPTY, can be removed
- `app/data/seed/` — EMPTY, can be removed
- `app/data/normalisation/` — contains active Python files (`character_maps.py`, `kanji_lookup.py`, etc.) — KEEP

### Problem 3 — Tests mock exactly what's broken (self-verifying mocks)

- `test_paste_translate_returns_result_partial` monkeypatches `detect_field_type` — so it never tests
  whether the real route actually calls it correctly
- The `test_router.py` LLM tests monkeypatch the OpenAI client correctly, but do not test Strategy C routing
- `test_strategy_c_vocabulary.py` does NOT test `issuing_authority` — the broken field type

**Fix:** Add targeted real tests that verify the actual pipeline wiring (not just the mocked version).

## Todo list

- [x] 1. Create this todo file
- [x] 2. Fix Strategy C: add `issuing_authority` to `VOCABULARY_FIELDS` + `lookup_issuing_authority()` + dispatch in `vocabulary_lookup.py`
- [x] 3. Remove dead empty folders: `app/data/lookup_tables/`, `app/data/geonames/`, `app/data/seed/`
- [x] 4. Add test: `test_lookup_issuing_authority_japanese` — Strategy C resolves `東京都公安委員会` via VOCABULARY
- [x] 5. Add test: real paste route test with no mock — posts to `/paste/translate`, checks 200 and contains result keys (LLM_ENABLED=False in testing config so will fall to UNRESOLVED gracefully)
- [x] 6. Add test: LLM fallback — monkeypatch `_get_client` to raise, confirm `detect_field_type` returns `("unstructured_text", 0.5, "en")`
- [x] 7. Fix `pyproject.toml` pytest configuration to note correct Python executable
- [x] 8. Run all tests, fix any regressions → **RESULT: 95 Flask tests passed, 0 failed**

## Files to change

| File | Change |
|------|--------|
| `app/pipeline/normalisation/vocabulary_lookup.py` | Add `issuing_authority` to `VOCABULARY_FIELDS`, add `lookup_issuing_authority()`, add dispatch branch |
| `app/data/lookup_tables/` | DELETE (empty folder) |
| `app/data/geonames/` | DELETE (empty folder) |
| `app/data/seed/` | DELETE (empty folder) |
| `tests/test_strategy_c_vocabulary.py` | Add `issuing_authority` lookup tests |
| `tests/test_frontend_ui_epic.py` | Add real no-mock paste route test |
| `tests/test_router.py` | Add Strategy C routing test for `issuing_authority` |

## Epics consulted (Status: IMPLEMENTED only)

- `epic-01-strategy-a-preserve.md` — PRESERVE_FIELDS definition, ProcessingMethod constants contract
- `epic-01-strategy-b-calendar-numeric.md` — calendar/numeric routing for Strategy B
- `epic-01-strategy-c-vocabulary.md` — vocabulary lookup service spec (note: data path mismatch documented here)
- `epic-04-1-orchestrator-minimal.md` — orchestrator wires strategies; `process_field_row()` calls router

## Notes

- `issuing_authority` also appears in `REPOSITORY_CHECKED_FIELDS` and `NAME_FIELDS` in `field_types.py`
  (Strategies E and F). Strategy C should handle it FIRST when a known authority name matches the lookup table.
  When no match is found in the vocabulary, it falls through to UNRESOLVED (correct — Strategy E/F not yet implemented).
- The `lookup_issuing_authority()` should match by country key first, then fall back to any-country scan
  (same pattern as `lookup_legal_form()`).
- `data/seed/issuing_authorities.json` also exists — this is the seed data file used to populate
  `data/lookup_tables/issuing_authorities.json`. They are different files with different formats.
