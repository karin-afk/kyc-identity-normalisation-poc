# Strategy A — Preserve

**Status: IMPLEMENTED** — branch `feature/epic-01a-preserve`, commit `0df7fd9`.

---

## What Strategy A does

Strategy A is the first strategy checked by the normalisation router. It returns structured identifiers byte-for-byte exactly as extracted from the source document — no normalisation, no transliteration, no translation, no API calls.

If the field type is in `PRESERVE_FIELDS`, the router returns immediately without attempting any further strategy. This ensures that document numbers, tax IDs, emails, and financial values are never accidentally altered.

---

## Implementation files

| File | Role |
|------|------|
| `app/pipeline/normalisation/router.py` | Defines `PRESERVE_FIELDS` and calls `_try_strategy_a()` first in the strategy chain |
| `app/pipeline/normalisation/preserve.py` | `apply_preserve()` — returns the result dict for preserve fields |
| `app/pipeline/normalisation/field_types.py` | `PRESERVE_FIELDS` constant list and `ProcessingMethod` labels |
| `src/pipeline/rules_engine.py` | Legacy preserve logic (`apply_rules()`); reused by router via `sys.path` injection until cutover |

---

## PRESERVE_FIELDS list

The following field types are preserved verbatim. This list is the single source of truth — do not hardcode these strings elsewhere.

### Identity document identifiers
- `passport_no`
- `id_no`
- `id_number`
- `licence_no`
- `document_number`

### Company identifiers
- `registration_no`
- `company_no`
- `commercial_registration_no`

### Financial identifiers
- `reference_no`
- `tax_id`
- `vat_number`

### Contact
- `email`

### Financial numeric values
These are preserved verbatim (value must not change). Format normalisation of digit scripts and separators is Strategy B's responsibility.

- `number_of_shares`
- `voting_rights`
- `ownership_percentage`
- `share_capital`
- `number_of_issued_shares`
- `total_assets`
- `total_liabilities`
- `net_assets`
- `revenue`
- `expenses`

---

## Result dict returned by Strategy A

```python
{
    "original_text":            "<value as extracted>",
    "normalised_form":          "<identical to original_text>",
    "allowed_variants":         [],
    "processing_method":        "PRESERVE",
    "confidence":               1.0,
    "review_required":          False,
    "review_reason":            None,
    "should_use_in_screening":  True,
}
```

Key invariants:
- `normalised_form` is byte-for-byte identical to `original_text` for all inputs, including empty string, Arabic-Indic numerals, full-width digits, and Unicode characters.
- `confidence` is always `1.0`.
- `review_required` is always `False`.
- `allowed_variants` is always `[]`.
- No external API, database, or library call is made.

---

## Router integration

`app/pipeline/normalisation/router.py` → `route_field(row)`:

1. Extracts `original_text`, `field_type`, `language` from `row`.
2. Calls `_try_strategy_a(text, field_type)`.
3. If result is not `None`, returns immediately — no further strategies are tried.
4. If result is `None` (field not in `PRESERVE_FIELDS`), falls through to Strategy B stub.

The router currently imports from `src/pipeline/rules_engine.apply_rules()` for backward compatibility. The direct fallback dict inside `_try_strategy_a` covers the case where the `src/` import fails.

---

## Processing method label

`"PRESERVE"` — defined as `ProcessingMethod.PRESERVE` in `app/pipeline/normalisation/field_types.py`. This label is a stable contract written to every result dict and audit log entry. It must not be renamed.

---

## Confidence score

`1.0` — defined in `STRATEGY_CONFIDENCE[ProcessingMethod.PRESERVE]`. Human-verified preserve fields have the highest possible confidence because they are returned without modification.

---

## Test coverage

| Test file | What it covers |
|-----------|----------------|
| `tests/test_strategy_a_preserve.py` | `apply_preserve()` for all PRESERVE_FIELDS, edge cases (empty string, Arabic-Indic digits, Unicode), non-preserve returns `None` |
| `tests/test_router.py` | `route_field()` returns `PRESERVE` result for all preserve field types; full-width and Arabic-Indic digits not converted |

```bash
pytest -q tests/test_strategy_a_preserve.py tests/test_router.py
```

---

## What is NOT Strategy A's responsibility

| Concern | Handled by |
|---------|------------|
| Format of numeric digit scripts (e.g. `٣` → `3`) | Strategy B (calendar/numeric rules) |
| Date normalisation | Strategy B |
| Name transliteration | Strategy F |
| Address normalisation | Strategies D / G |
| Routing decision | `router.py` — Strategy A is checked first, then falls through |
