# Normalisation Router and Orchestrator

**Status: IMPLEMENTED (minimal)** — branch `feature/epic-04-1-orchestrator-minimal`, commit `5f7f595`, 61 tests passed.

---

## Overview

The router and orchestrator wire the UI tabs to the normalisation pipeline. They are the entry points that all routes call — route handlers do not import strategy modules directly.

| Component | File | Role |
|-----------|------|------|
| Router | `app/pipeline/normalisation/router.py` | Routes one field dict through strategies A–I in order |
| Orchestrator | `app/pipeline/orchestrator.py` | Entry point for UI routes; calls the router for sentence input; stubs document pipeline |
| Field type detector | `app/pipeline/normalisation/field_type_detector.py` | Auto-detects field type from pasted text when analyst selects "Auto-detect" |

---

## Router — `route_field(row)`

### Signature

```python
def route_field(row: dict) -> dict
```

### Input dict

| Key | Type | Required | Notes |
|-----|------|----------|-------|
| `original_text` | `str` | Yes | Raw extracted or pasted text |
| `field_type` | `str` | Yes | KYC field type key (e.g. `"passport_no"`, `"person_name"`) |
| `language` | `str` | No | ISO 639-1 code, or `""` for auto |
| `country` | `str` | No | ISO 3166-1 alpha-2, or `""` |

### Strategy chain

The router tries strategies in this order. It returns the first non-`None` result.

| Step | Strategy | Status |
|------|----------|--------|
| A | Preserve — return identifier verbatim | **Implemented** |
| B | Calendar / numeric rules | Stub — always `None` |
| C | Vocabulary lookup | Stub — always `None` |
| D | Geographic lookup | Stub — always `None` |
| E | Verified repository | Stub — always `None` |
| F | Transliteration libraries | Stub — always `None` |
| G | Character mapping tables | Stub — always `None` |
| H | Azure NMT translation | Stub — always `None` |
| I | LLM (Phase 2, gated) | Stub — only reached when `LLM_ENABLED=true` in `.env` |
| — | UNRESOLVED fallback | Always reached for non-preserve fields currently |

### UNRESOLVED result

When no strategy resolves the field, the router returns:

```python
{
    "original_text":            "<input>",
    "normalised_form":          None,
    "allowed_variants":         [],
    "processing_method":        "UNRESOLVED",
    "confidence":               0.0,
    "review_required":          True,
    "review_reason":            "No normalisation strategy resolved this field",
    "should_use_in_screening":  False,
}
```

The UI renders the `UNRESOLVED` result with an "Awaiting native speaker review" notice in `#DA2128`.

### Guard rails

- If `field_type` is empty, returns `UNRESOLVED` immediately with `reason="Missing field_type"`.
- `LLM_ENABLED` is read from the environment at call time — Strategy I is never reached unless explicitly set in `.env`.
- `src/` import failure in `_try_strategy_a` is caught and the direct fallback dict is returned — no crash.

---

## Orchestrator — `process_field_row` and `process_document_file`

### `process_field_row(row)`

Entry point for the Sentence tab. Accepts the same `row` dict as `route_field` and delegates directly.

```python
def process_field_row(row: dict) -> dict:
    from app.pipeline.normalisation.router import route_field
    return route_field(row)
```

Called by `app/routes/paste.py` → `POST /paste/translate`.

### `process_document_file(file_path, doc_type, language)`

Stub for the document upload pipeline (Epic 11). Always raises `NotImplementedError`.

```python
def process_document_file(file_path: str, doc_type: str, language: str) -> list[dict]:
    raise NotImplementedError(
        "Document processing pipeline not yet implemented (Epic 11). "
        "The UI will show a 'not yet available' notice."
    )
```

Called by `app/routes/upload.py` → `POST /upload/process`. The route catches `NotImplementedError` and renders `partials/not_implemented.html` with HTTP 200 — no crash, no 500.

---

## Field type detector — `detect_field_type(text, language)`

Used by the Sentence tab when the analyst selects **Auto-detect** for field type.

### Heuristics (in priority order)

| Priority | Heuristic | Returns | Confidence |
|----------|-----------|---------|------------|
| 1 | Matches email regex | `"email"` | 0.95 |
| 2 | Matches date patterns (ISO, slash/dot, Japanese era, Arabic-Indic) | `"date_of_birth"` | 0.85 |
| 3 | Alphanumeric 6–20 chars, no spaces, matches ID format | `"id_number"` | 0.85 |
| 4 | Contains street-type keyword (EN/FR/DE/AR/JA/KO/RU/ZH) | `"address"` | 0.85 |
| 5 | 1–4 tokens, no sentence structure, ends with legal suffix (LLC, Ltd, GmbH…) | `"company_name"` | 0.90 |
| 6 | 1–4 tokens, no sentence structure | `"person_name"` | 0.80 |
| 7 | >8 tokens or has sentence structure (verb indicators, punctuation) | `"nature_of_business"` | 0.60 |
| 8 | Fallback | `"unstructured_text"` | 0.50 |

No ML model or external API is involved. Detection is fully deterministic.

### Return value

```python
(field_type: str, confidence: float)
```

The paste route uses the detected `field_type` as the input to `route_field`. The detected type and confidence are passed to `paste_result.html` and shown to the analyst:

> *Field type auto-detected as: Person name (80% confidence) — resubmit with a specific type selected if incorrect.*

---

## Paste route integration

`app/routes/paste.py` → `POST /paste/translate`:

```
1. Validate: text non-empty, len ≤ 2000
2. If field_type == "auto":
       detected_field_type, field_type_confidence = detect_field_type(text, language)
       field_type = detected_field_type
3. row = {"original_text": text, "field_type": field_type, "language": language}
4. result = process_field_row(row)
5. render_template("partials/paste_result.html", result=result,
                   detected_field_type=detected_field_type,
                   field_type_confidence=field_type_confidence)
```

Fallback on `ImportError` / `NotImplementedError`: renders `partials/not_implemented.html`.

---

## Test coverage

```bash
pytest -q tests/test_router.py
```

| Test group | Covers |
|------------|--------|
| Strategy A — preserve fields | `route_field` returns PRESERVE result for all preserve field types; digits not converted |
| Non-preserve fields | `route_field` returns UNRESOLVED for all non-preserve types currently |
| Field type detector | email, ISO date, Japanese era date, person name, company (Ltd), address, fallback |
| Orchestrator | `process_field_row` preserve and unresolved paths; `process_document_file` raises `NotImplementedError` |

Total: **61 tests passed** (router + frontend integration + Flask route smoke tests).

---

## What is not yet implemented

| Feature | Epic |
|---------|------|
| Strategies B–H (calendar, vocabulary, geographic, repository, transliteration, character map, NMT) | Epics 02–08 |
| Strategy I — LLM fallback | Epic 09 (Phase 2, requires AI Governance Board approval) |
| Document pipeline (OCR + field extraction) | Epic 11 |
| Review queue persistence (database model) | Epic 06 |
| Native speaker assignment routing | Epic 07 |
