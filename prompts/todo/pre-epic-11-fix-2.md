# Pre-Epic 11 — Fix 2: Move classifier-metadata stamping into the orchestrator

**File location:** `prompts/todo/pre-epic-11-fix-2-classifier-metadata-stamping.md`
**Status:** Ready to implement
**Depends on:** Fix 1 committed and 138/164 still green
**Blocks:** Epic 11 (document upload pipeline)
**Risk:** Low. Two modules touched in production. Diagnostic must still pass 138/164 after.

---

## 1. Problem

`app/routes/paste.py` calls `process_field_row()`, then mutates the returned dict in place to add four classifier-metadata keys before passing it to the Jinja template:

```python
result = process_field_row({...})
result["detected_field_type"] = field_type
result["detected_language"] = language
result["detected_language_label"] = _LANGUAGE_LABELS.get(language, language)
result["classification_confidence"] = classification_confidence
```

This works today with one caller. The moment Epic 11's document aggregator loops `process_field_row()` over 27 fields and surfaces them through a UI that reuses `paste_result.html` (or shares any rendering code), every row will have `None`/undefined for those four keys. The orchestrator's contract is fuzzy: it returns "the router's dict, sometimes with extra keys, depending on who called it."

The orchestrator should own the response shape. Every caller — paste route, document aggregator, diagnostic harness — should receive the same dict.

## 2. Goal

After this fix:
- `process_field_row()` returns a dict that includes `detected_field_type`, `detected_language`, `detected_language_label`, `classification_confidence`
- `app/routes/paste.py` does not mutate the returned dict — it passes it to the template as-is
- The four metadata fields have explicit defaults when not provided (e.g. caller didn't run the classifier separately)
- 164-test diagnostic still passes 138/164. No regression.

## 3. Investigation step (do this first, output to chat, wait for sign-off)

Before changing any code, report:

1. The exact lines in `paste.py` where the result dict is mutated. Quote them.
2. The exact template (`paste_result.html`) and which of the four keys it actually reads. Search the template file. If it only reads three of the four, we only need to stamp three.
3. Whether any other route handler or test mutates the result dict from `process_field_row` in the same way. Search the codebase.
4. Whether the diagnostic harness (`run_integration_diagnostic.py`) reads any of these four keys from `process_field_row`'s return value or from the classifier separately. Quote the relevant lines.
5. Where `_LANGUAGE_LABELS` is defined and whether it's reused elsewhere (might need to be relocated).

Stop after the report. Wait for sign-off.

## 4. Implementation

After sign-off, do the following in order. One change at a time, run the diagnostic between each — no batching.

### 4.1 Extend the orchestrator signature

`process_field_row` takes the row dict today. The classifier runs *before* the orchestrator is called, and its outputs are not currently passed in — only `field_type` and `language` are part of the row. We need to thread `classification_confidence` (and the language label) through.

Two options:

(a) Add an optional `classification_metadata` parameter:
```python
def process_field_row(row: dict, *, classification_metadata: dict | None = None) -> dict:
```
where `classification_metadata` contains `{"classification_confidence": float, "detected_language_label": str}` (the two pieces not already in `row`).

(b) Extend the row dict to include the metadata fields as additional keys, and have the orchestrator pick them out.

Prefer (a). It keeps the row dict's purpose narrow (the field to normalise) and surfaces the metadata as a separate concept. The caller assembles the metadata explicitly.

### 4.2 Stamp the metadata onto the result inside `process_field_row`

After `route_field` returns, the orchestrator adds:

```python
result["detected_field_type"] = row.get("field_type", "")
result["detected_language"] = row.get("language", "")
result["detected_language_label"] = (
    classification_metadata.get("detected_language_label", row.get("language", ""))
    if classification_metadata else row.get("language", "")
)
result["classification_confidence"] = (
    classification_metadata.get("classification_confidence", None)
    if classification_metadata else None
)
```

Document the four keys in the orchestrator function's docstring as part of the return contract.

When `classification_metadata` is `None` (caller didn't classify separately — e.g. document aggregator may use DI's field labels directly without re-classifying), `classification_confidence` is `None` and the language label falls back to the raw language code. The UI must handle `None` gracefully.

### 4.3 Move `_LANGUAGE_LABELS` if needed

If `_LANGUAGE_LABELS` lives in `paste.py` today and the orchestrator now needs it, relocate it to a shared module (`app/pipeline/language_labels.py` or similar). Don't duplicate the dict.

Investigation step 5 will confirm whether this is needed. If `_LANGUAGE_LABELS` is only used in paste.py and the orchestrator receives the label pre-computed (via `classification_metadata`), no relocation is needed. Default to passing the label in — keeps the dict where it is.

### 4.4 Update `paste.py` to pass metadata in, not stamp after

The new shape of paste.py's call:

```python
field_type, classification_confidence, language = detect_field_type(text, language_hint=language_hint)
language_label = _LANGUAGE_LABELS.get(language, language)

result = process_field_row(
    {"original_text": text, "field_type": field_type, "language": language},
    classification_metadata={
        "classification_confidence": classification_confidence,
        "detected_language_label": language_label,
    },
)

# No more mutation. result already has all four metadata keys.
return render_template("partials/paste_result.html", result=result, original=text, field_type=field_type)
```

The four `result["..."] = ...` lines are deleted.

### 4.5 Update the diagnostic harness if it cares

The diagnostic currently calls `detect_field_type` and `process_field_row` separately and reads classifier output from the former. If it does not currently read the four metadata keys from `process_field_row`'s return, no change needed. If it does, update it to use the new shape.

Most likely: no change. The diagnostic reports classifier output in its own column already.

## 5. Tests

### 5.1 Run the existing 164-test diagnostic

```
python run_integration_diagnostic.py
```

Confirm 138/164. Stop on any change to the count.

### 5.2 Add a unit test for the orchestrator's response shape

Add `tests/unit/pipeline/test_orchestrator_response_shape.py`:

```python
"""Orchestrator response shape contract test.

process_field_row() must return a dict containing the four
classifier-metadata keys for every caller, not only paste.py.
Epic 11's document aggregator depends on this contract.
"""

def test_process_field_row_includes_classifier_metadata(vocab_service_fixture):
    from app.pipeline.orchestrator import process_field_row

    result = process_field_row(
        {"original_text": "GmbH", "field_type": "legal_form", "language": "de", "country": ""},
        classification_metadata={
            "classification_confidence": 0.95,
            "detected_language_label": "German",
        },
    )

    assert result["detected_field_type"] == "legal_form"
    assert result["detected_language"] == "de"
    assert result["detected_language_label"] == "German"
    assert result["classification_confidence"] == 0.95
    assert result["normalised_form"] == "GMBH"


def test_process_field_row_without_classifier_metadata_uses_defaults():
    from app.pipeline.orchestrator import process_field_row

    result = process_field_row(
        {"original_text": "GmbH", "field_type": "legal_form", "language": "de", "country": ""},
    )

    # When metadata is not supplied, the orchestrator falls back to the raw language code
    # and confidence is None. This is the path the document aggregator will use.
    assert result["detected_field_type"] == "legal_form"
    assert result["detected_language"] == "de"
    assert result["detected_language_label"] == "de"
    assert result["classification_confidence"] is None
```

If `vocab_service_fixture` was added in Fix 1, reuse it. If not, this test may need to push a Flask app context (less ideal — fix 1 should have decoupled this).

### 5.3 Smoke test the paste route

Run the Flask app locally and submit a field via the paste tab. Confirm the result panel renders identically to before — same four pieces of metadata visible. No template errors in the logs.

If you have an existing route-level test (e.g. `tests/integration/test_paste_route.py`), run it. If you don't, manual smoke test is acceptable for this commit — but add it to the Epic 11 followup list.

## 6. Commit

Single commit. Message:

```
refactor(orchestrator): own the classifier-metadata response shape

process_field_row() now stamps the four classifier-metadata keys
(detected_field_type, detected_language, detected_language_label,
classification_confidence) onto its return value. paste.py no longer
mutates the result dict in place. Unblocks Epic 11 (document aggregator
will produce many rows; the response shape must be consistent across
callers).

- process_field_row() takes optional classification_metadata kwarg
- paste.py passes classifier output via the new kwarg, drops post-hoc mutation
- Added unit tests covering both supplied and default metadata paths

Diagnostic: 138/164 (no change)
```

## 7. Definition of done

- [ ] `process_field_row` returns a dict containing all four metadata keys for every call
- [ ] `paste.py` does not contain any `result[...] = ...` mutation after the orchestrator call
- [ ] `tests/unit/pipeline/test_orchestrator_response_shape.py` passes
- [ ] `python run_integration_diagnostic.py` reports 138/164
- [ ] Manual smoke test of the paste tab confirms UI renders identically
- [ ] Committed as a single commit with the message above
- [ ] Fix 1 is already in main (this commit builds on it)

## 8. What this commit does NOT do

Out of scope, for Epic 11 or later:

- Do not convert the response dict to a Pydantic model (still a dict for now — Pydantic is an Epic 11 design discussion)
- Do not change the router's signature again
- Do not modify `process_document_file()`
- Do not refactor the classifier
- Do not touch `LLM_ENABLED` env var handling
- Do not add the document aggregator (that's Epic 11)

If you find yourself wanting to do any of the above, stop and ask.

---

## Next step after this commit lands

Epic 11 Phase 0. See `prompts/todo/epic-11-document-upload-pipeline.md`.