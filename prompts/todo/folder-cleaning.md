# Folder Cleaning

Addresses structural inconsistencies that cause import confusion.
Branch: `folder-cleaning` off `dev`.

---

## Assessment of proposed changes

### Issue 1 — Move calendar/numeric files ✅ AGREE, DO NOW

The four files are standalone: `calendar_hebrew.py`, `calendar_offset.py`, `calendar_solar_hijri.py` import only `re` and `math`. `numeric_rules.py` imports only stdlib. None of the three calendar files are imported anywhere in the codebase yet.

`numeric_rules.py` is imported by `calendar_rules.py` via a sys.path hack (`SRC_DIR` injection). After the move, replace that hack with a clean relative import (`from .numeric_rules import ...`).

### Issue 2 — data/ path ambiguity ✅ AGREE, DOCUMENT ONLY

No files to move. VocabularyLookupService already loads from `data/lookup_tables/` (root) correctly. Just make the canonical paths explicit in a reference note at the top of each epic that touches data paths. No code change.

### Issue 3 — app/data/__init__.py vs data/ ✅ AGREE, NOTE ONLY

`data/` is a data directory (no `__init__.py`), `app/data/` is a Python package (has `__init__.py`). This is correct as-is. The only action is adding a comment in `app/data/__init__.py` to make the distinction explicit for future Copilot sessions.

### Issue 4 — Epic file numbering ✅ AGREE, DO NOW

Rename with `git mv` so the order is unambiguous. `epic-04-1-orchestrator-minimal.md` is NOT renamed (not in the user's list; its current name does not conflict once the strategy files are renumbered).

### Issue 5 — character_maps.py stub ✅ NOTE ONLY

File confirmed as a 4-line placeholder. Implementation deferred to Epic 07. No action in this branch.

---

## Todo list

### 1. Move files: src/pipeline/ → app/pipeline/normalisation/

- [x] Copy `src/pipeline/calendar_solar_hijri.py` → `app/pipeline/normalisation/calendar_solar_hijri.py`
- [x] Copy `src/pipeline/calendar_hebrew.py` → `app/pipeline/normalisation/calendar_hebrew.py`
- [x] Copy `src/pipeline/calendar_offset.py` → `app/pipeline/normalisation/calendar_offset.py`
- [x] Copy `src/pipeline/numeric_rules.py` → `app/pipeline/normalisation/numeric_rules.py`
- [x] Delete `src/pipeline/calendar_solar_hijri.py`
- [x] Delete `src/pipeline/calendar_hebrew.py`
- [x] Delete `src/pipeline/calendar_offset.py`
- [x] Delete `src/pipeline/numeric_rules.py`

### 2. Fix calendar_rules.py imports

- [x] Remove the `SRC_DIR` / `sys.path.insert` block (lines 10-13)
- [x] Replace `from pipeline.numeric_rules import ...` with `from .numeric_rules import ...`
- [x] Verify no other `from pipeline.` imports remain in `app/` code that referenced the moved files

### 3. Add clarifying comment to app/data/__init__.py

- [x] Add a two-line comment stating that JSON lookup data lives in `data/lookup_tables/` at the project root, and that `app/data/` contains Python character map modules only

### 4. Rename epic files for consistent numbering (git mv)

- [x] `epic-01-strategy-b-calendar-numeric.md` → `epic-02-strategy-b-calendar-numeric.md`
- [x] `epic-01-strategy-c-vocabulary.md` → `epic-03-strategy-c-vocabulary.md`
- [x] `epic-01-strategy-d-geographic-lookup.md` → `epic-04-strategy-d-geographic-lookup.md`
- [x] `epic-01-strategy-e-verified-repository.md` → `epic-05-strategy-e-verified-repository.md`
- [x] `epic-01-strategy-f-transliteration.md` → `epic-06-strategy-f-transliteration.md`

### 5. Run full test suite

- [x] `& "C:\Python314\python.exe" -m pytest -q` — all tests must pass with no regressions

### 6. Commit and push

- [x] `git add -A`
- [x] Commit: `chore: move calendar/numeric files to app/pipeline/normalisation, rename epic files`
- [x] Push to `origin/folder-cleaning`

---

## Canonical data path reference (for all future epics)

| Data type | Location |
|---|---|
| JSON lookup tables | `data/lookup_tables/` (project root) |
| Seed JSON | `data/seed/` (project root) |
| GeoNames dataset | `data/geonames/allCountries.txt` (project root, gitignored) |
| Geographic index cache | `data/geo_cache/` (project root, gitignored) |
| Python character maps | `app/data/normalisation/` (Python package) |
| Uploaded files | `uploads/` (project root, gitignored) |

`app/data/` is a Python package with `__init__.py`.
`data/` is a plain directory with no `__init__.py` — it is NOT importable.
