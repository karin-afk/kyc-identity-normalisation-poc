Here's the prompt:

---

I need you to do a minimal, low-risk consolidation of the codebase before we start Epic 11. The goal is **discoverability**, not perfection. We are not rewriting anything. We are documenting what exists, archiving what's dead, and removing the most painful duplicates.

The 164-test diagnostic must stay at 138/164 throughout. If at any point it drops, stop and diagnose before continuing.

Work through the tasks below **in order**. Do not skip. Do not bundle. After each task, stop and wait for sign-off before proceeding.

---

**Task 1 — Map what's there.**

Read every file under `src/` and `app/` (excluding tests for now). For each, produce a one-line summary in this format:

```
src/pipeline/transliteration_engine.py — IMPORTED BY: app/pipeline/normalisation/transliteration.py. Role: core transliteration logic. Status: ALIVE.
src/pipeline/pipeline.py — IMPORTED BY: nothing in app/, nothing in routes. Role: pre-Flask orchestrator. Status: SUSPECTED DEAD.
```

For each file report:
- **IMPORTED BY** — list every other file in the repo that imports it. If nothing imports it, say "nothing." Use grep / search to verify.
- **Role** — one sentence on what it does
- **Status** — ALIVE (imported by live code) / SUSPECTED DEAD (no imports found) / DUPLICATE (another file does the same job) / DATA (it's a lookup table or static config, not code)

Pay particular attention to:
- The pre-Flask orchestrators: `src/main.py`, `src/run_ocr.py`, `src/pipeline/pipeline.py`, `src/pipeline/field_classifier.py`
- Anything that looks like it might be archaeology: `_fix_dataset_a.py`, `_geo_debug.py`, `_geo_smoke_test.py` at the repo root
- Duplicate filenames: `src/utils/logging_utils.py` vs `app/utils/logging_utils.py`
- The `src/evaluation/` subtree — is any of it imported by active code or only by old scripts?
- Anything in `src/pipeline/` that has a sibling in `app/pipeline/normalisation/`

Output the full inventory in chat as a table or list. Stop. Wait for sign-off.

---

**Task 2 — Propose the archive list.**

Based on Task 1's inventory, propose three lists:

1. **KEEP in current location** — file works, is imported, no good reason to move
2. **DEDUPLICATE** — file is a duplicate of another; pick which copy lives and which dies, with reasoning
3. **ARCHIVE** — file is SUSPECTED DEAD; move to `_archive/` preserving the directory structure (so `src/pipeline/pipeline.py` → `_archive/src/pipeline/pipeline.py`)

For each item in the ARCHIVE list, double-check by searching for ANY reference (imports, string references, dynamic imports via `importlib`, references in config files, references in docstrings, references in README or markdown docs). If you find even one reference, move it to the KEEP list and flag for human review.

For each item in the DEDUPLICATE list, identify:
- Which copy is canonical (the one imported by more live callers)
- Which copy gets deleted
- Any imports that need updating

Do **not** propose moving anything from `src/` to `app/`. That's a bigger refactor. Out of scope for this task.

Do **not** propose archiving anything in `app/`. The `app/` tree is the live tree.

Output the three lists in chat. Stop. Wait for sign-off before any file moves.

---

**Task 3 — Write `ARCHITECTURE.md`.**

Create `ARCHITECTURE.md` at the repo root. Three sections:

### Section 1: Active modules

Walk through the live code and explain what's where. Use this rough structure:

- **Entry points** — `app.py`, `run.py`, `run_integration_diagnostic.py`, `run_strategy_h_diagnostic.py`
- **Flask app** — `app/__init__.py`, `app/config.py`, `app/routes/`, `app/templates/`
- **Pipeline** — `app/pipeline/orchestrator.py` is the entry. From here, explain the data flow: orchestrator → router → strategy modules → result. Name each strategy and where it lives. Be explicit about which strategies delegate to `src/` (Strategy F → `src/pipeline/transliteration_engine.py`).
- **Persistence** — `app/models/`
- **Async tasks** — `app/tasks/`
- **Utilities** — `app/utils/`

For each subsystem, write 2–3 sentences. Not exhaustive. The goal is "a new developer reads this and knows where to look."

### Section 2: Legacy core still in use

The `src/` files that survived Task 2's archive sweep. Explain why each one stayed — usually "imported by Strategy X for historical reasons; on the migration backlog but not blocking."

Be honest: this is technical debt. Say so. List the canonical migration target ("eventually moves to `app/pipeline/normalisation/`").

### Section 3: Archived

Point at `_archive/`. One sentence per archived file explaining why it was retired. The goal is so that six months from now, when someone wonders "did we ever build X?", they can grep `_archive/` and find the answer.

### Section 4: Conventions

A short list of rules for new code:

- New code goes in `app/`, never `src/`
- New imports prefer `app/` modules; `src/` is import-of-last-resort and only via existing wrappers
- New utilities go in `app/utils/`
- Lookup tables go in `data/lookup_tables/`
- Anything pre-Flask in design goes to `_archive/`
- The 164-test diagnostic must pass before any merge

Show me the draft `ARCHITECTURE.md` in chat. Stop. Wait for sign-off and edits before committing.

---

**Task 4 — Execute the file moves.**

Once Task 2's archive list and Task 3's `ARCHITECTURE.md` are both signed off:

1. Create `_archive/` at the repo root
2. Move every file from Task 2's ARCHIVE list into `_archive/`, preserving directory structure
3. Delete every file from Task 2's DEDUPLICATE "delete" list
4. Update every import that pointed at a deleted/moved file
5. Commit `ARCHITECTURE.md`
6. Run `python run_integration_diagnostic.py`. Confirm **138/164**.

If the diagnostic count changes (up or down), stop. Diagnose. Do not "fix" by adjusting test expectations — that's a regression signal, not a calibration step.

If the count is exactly 138/164, commit. Single commit. Message:

```
chore: archive dead modules and add ARCHITECTURE.md

Discoverability pass before Epic 11. Moved {N} files to _archive/,
deduplicated {M} files, wrote ARCHITECTURE.md describing the active
pipeline and the surviving src/ legacy.

No behaviour changes. Diagnostic: 138/164 (no change).

Files archived:
  - {list each}

Files deduplicated:
  - {list each, showing which copy survived}
```

Show me the commit diff summary in chat. Stop. Wait for final sign-off before pushing.

---

**Task 5 — Smoke test the live surfaces.**

After the commit, verify the app still actually works end-to-end (not just the diagnostic):

1. Start the Flask dev server (`python app.py` or whatever the entry is)
2. Submit one paste-tab field manually — confirm it returns a normal result
3. Hit `/upload` and confirm the "not yet implemented" partial renders (this is fine — Epic 11 hasn't started yet)
4. Run `pytest tests/` and confirm no test failures introduced

Report the results in chat. If anything fails, roll back the archive commit (`git revert HEAD`) and re-investigate.

---

**Rules throughout:**

- **One task per turn.** Stop after each task and wait for "proceed."
- **No refactoring of `src/` internals.** This isn't the right exercise for that.
- **No moving files from `src/` to `app/`.** Bigger refactor, out of scope.
- **No changes to the router or strategy modules.** They are at 138/164 and they stay there.
- **Archive, don't delete (with the exception of true duplicates).** Reversibility matters.
- **If a file's status is genuinely unclear, KEEP it.** False archives are worse than false keeps. Better to leave a file alive than to break something six months from now because someone moved code that turned out to be needed.
- **Ask before deciding.** If anything in the inventory is ambiguous, surface it in chat. Don't guess.

Begin with Task 1.

