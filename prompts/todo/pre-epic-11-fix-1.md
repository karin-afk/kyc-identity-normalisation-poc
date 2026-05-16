# Pre-Epic 11 — Fix 1: Remove Flask context dependency from router

**File location:** `prompts/todo/pre-epic-11-fix-1-vocab-service-injection.md`
**Status:** Ready to implement
**Blocks:** Epic 11 (document upload pipeline)
**Risk:** Low. One module touched in production, one in tests. Diagnostic must still pass 138/164 after.

---

## 1. Problem

`app/pipeline/normalisation/router.py::_try_strategy_c()` reads `flask.current_app.vocab_service` directly. This works today because every live caller (paste route, diagnostic harness invoking via the Flask app context) happens to have an app context pushed. It will silently break in Epic 11 when the document aggregator loops `route_field()` calls — particularly if any loop runs outside an app context (worker process, async task, plain script).

We need to remove the Flask coupling from the router. The router should be a pure function of its inputs. The transport layer (route handler, orchestrator, future aggregator) is responsible for obtaining the vocab service and passing it in.

## 2. Goal

After this fix:
- `route_field()` does not import `flask` and does not reference `current_app`
- The vocab service is supplied to the router by the caller
- `app/pipeline/orchestrator.py::process_field_row()` is responsible for resolving the vocab service from the app context (or accepting one passed in)
- 164-test diagnostic still passes 138/164. No regression.

## 3. Investigation step (do this first, output to chat, wait for sign-off)

Before changing any code, report:

1. The exact lines in `router.py` where `current_app` or `flask` is imported or used. Quote them with line numbers.
2. Every reference to `vocab_service` across the codebase. Quote each call site.
3. Where `vocab_service` is *created* and attached to the Flask app. Quote that initialisation code.
4. Whether `_try_strategy_c` is the only strategy helper that reaches into Flask context, or whether any other `_try_strategy_*` helper does the same. Check every strategy helper.
5. Whether `VocabularyLookupService` has any state worth preserving across calls (caching, lazy-loaded tables) — i.e. is it expensive to construct on every call, or cheap? Read the class and tell me.

Stop after the report. Wait for sign-off.

## 4. Implementation

After sign-off, do the following in this order. One change at a time, run the diagnostic between each — no batching.

### 4.1 Add an optional parameter to `route_field`

Change the signature:

```python
def route_field(row: dict, *, vocab_service=None) -> dict:
```

`vocab_service` is keyword-only and optional. When `None`, behaviour is undefined for vocabulary lookups (caller's responsibility to provide it). Do not add a fallback that re-imports `flask.current_app` — the whole point of this fix is to remove that coupling.

### 4.2 Update `_try_strategy_c` to use the passed-in service

Replace the `from flask import current_app` / `current_app.vocab_service` block with a parameter received from `route_field`. Either thread `vocab_service` down through the helper call, or refactor `_try_strategy_c` to be a closure / take the service as an argument. Pick the simpler change.

If `vocab_service is None` when `_try_strategy_c` runs, return `None` (strategy miss) and log a `router_vocab_service_missing` event with `source="backend"`. Do not raise — the existing pattern is that strategies miss silently, not crash.

### 4.3 Update the orchestrator to obtain and pass the service

`app/pipeline/orchestrator.py::process_field_row()` becomes responsible for the Flask coupling. Two options — pick (a):

(a) Import `flask.current_app` in the orchestrator, fetch `vocab_service`, pass it to `route_field`. The Flask coupling moves up one layer. This is the minimum change.

(b) Add a `vocab_service` parameter to `process_field_row()` and require every caller (paste route, diagnostic, future aggregator) to pass one. Cleaner but touches more files.

Default to (a) for this commit. (b) is a follow-up if Epic 11 finds it inconvenient.

### 4.4 Verify no other strategy helpers reach into Flask

The investigation step should have surfaced this. If any other `_try_strategy_*` uses `current_app`, fix it the same way in this commit. Don't leave a half-clean router.

### 4.5 Remove the now-unused import

If `from flask import current_app` is no longer referenced anywhere in `router.py`, delete the import line.

## 5. Tests

### 5.1 Run the existing 164-test diagnostic

```
python run_integration_diagnostic.py
```

Confirm 138/164. If any test that previously passed now fails, stop. Do not commit. Diagnose first.

If the count *increased* (a test that previously failed now passes), still stop and diagnose — an unexpected pass is also a regression signal (the test may now be testing a different code path than intended).

### 5.2 Add a regression test

Add `tests/unit/pipeline/test_router_no_flask_context.py`:

```python
"""Router must work outside a Flask application context.

This test exists because the document aggregator (Epic 11) will call
route_field() from contexts that do not have a Flask app pushed.
If a future change re-introduces a current_app dependency in the router,
this test fails immediately.
"""

def test_route_field_runs_without_app_context(vocab_service_fixture):
    from app.pipeline.normalisation.router import route_field

    row = {
        "original_text": "GmbH",
        "field_type": "legal_form",
        "language": "de",
        "country": "",
    }

    # Note: no Flask app context pushed.
    result = route_field(row, vocab_service=vocab_service_fixture)

    assert result["normalised_form"] == "GMBH"
    assert result["processing_method"] == "VOCABULARY"
```

`vocab_service_fixture` is a pytest fixture that constructs a real `VocabularyLookupService` (or a minimal test double) without going through the Flask app factory. Add it to `tests/conftest.py` if it doesn't exist.

The test must pass when run with `pytest tests/unit/pipeline/test_router_no_flask_context.py` directly, without invoking the Flask app at all. If the test only passes when run as part of a larger suite that happens to push an app context, the fix is incomplete.

## 6. Commit

Single commit. Message:

```
refactor(router): remove flask.current_app dependency

The vocabulary service is now passed in by the caller rather than
fetched from Flask application context inside the router. Unblocks
Epic 11 (document aggregator will loop route_field calls outside
the request context).

- route_field() takes optional vocab_service kwarg
- process_field_row() resolves vocab_service from current_app and forwards
- Added regression test that runs route_field without app context

Diagnostic: 138/164 (no change)
```

Include the diagnostic output in the commit message body or as `reports/integration-report-latest.md` (whichever convention the repo uses for this).

## 7. Definition of done

- [ ] `router.py` does not import `flask`
- [ ] `grep -r "current_app" app/pipeline/` returns no hits inside the `normalisation/` subdirectory
- [ ] `process_field_row()` is the single point that bridges Flask context to the router
- [ ] `tests/unit/pipeline/test_router_no_flask_context.py` passes when run in isolation
- [ ] `python run_integration_diagnostic.py` reports 138/164
- [ ] Committed as a single commit with the message above
- [ ] Fix 2 has not been touched (no in-place mutation changes in this commit)

## 8. What this commit does NOT do

Out of scope, for Fix 2 or later:

- Do not move the classifier-metadata stamping out of `paste.py` (that's Fix 2)
- Do not change `process_field_row`'s return shape
- Do not add Pydantic models for the router result
- Do not touch `LLM_ENABLED` env var handling
- Do not modify `process_document_file()` — it stays as the `NotImplementedError` stub
- Do not refactor any strategy module beyond what's needed to remove the Flask import

If you find yourself wanting to do any of the above, stop and ask. They belong in separate commits.