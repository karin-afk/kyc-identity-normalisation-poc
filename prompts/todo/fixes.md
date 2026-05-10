# Integration Diagnostic — Fix Tracker

## Todo

- [x] **Fix 1** — Add missing field types to `field_type_detector.py` (`passport_no`, `registration_no`, `email`, `id_no`, `total_assets`, `revenue`, `net_assets`) → fixes A.1, A.2, A.3, B.7–B.11
- [x] **Fix 2** — Add calendar disambiguation hints to GPT-4o-mini system prompt in `field_type_detector.py` → fixes B.1, B.5, B.6
- [x] **Fix 3** — Check `status_terms.json` for missing entries (`現役`, `منتهي`, `aufgelöst`) and fix vocabulary lookup wiring if needed → fixes C.4, C.5, C.8. Root cause: GPT-4o-mini classification failure (returned `unstructured_text`). Fixed by adding Arabic status example (`نشط`) and Korean/Italian examples to `_EXAMPLES` in `field_type_detector.py`. JSON tables and wiring were correct throughout.
- [x] **Fix 4** — Wire Strategy D (geographic lookup) for `nationality` field type in `router.py` → fixes D.1–D.4. Root cause: `_GEOGRAPHIC_FIELDS` frozenset in `geographic_lookup.py` didn't include `country_of_registration`, `country_of_incorporation`, or `country_of_birth` — the field types GPT-4o-mini actually returns for country name inputs. Added all three to the frozenset and routed them to `lookup_country()`. D.1–D.4 and D.6 now pass.
- [ ] Fix 5 — In router.py, ensure strategies E, F, G, and H each have a stub entry in the routing chain that catches ImportError and NotImplementedError and returns None gracefully, allowing the router to fall through to UNRESOLVED cleanly rather than crashing or skipping silently. The stubs should log a single line: "Strategy X not yet implemented — field routed to UNRESOLVED". This does not fix the transliteration failures (F.1–F.5) but confirms the router chain is correctly structured and the failures are reported honestly rather than silently.
- [x] **Fix 6** — Add optional language hint to the paste tab UI → fixes B.6 (Minguo) and any structurally ambiguous date. Three-part change: (1) collapsed `<details>` section in `paste_sentence.html` with 24-language dropdown, sent as `language_hint` field; (2) `paste.py` extracts `language_hint` from form and passes it to `detect_field_type()`; (3) `field_type_detector.py` builds user message dynamically — if hint present, prepends `"Language hint provided by analyst: {hint}\n\nText to classify:\n"` — and adds one rule to `_SYSTEM_PROMPT` instructing the model to treat the hint as authoritative for `language_code` and calendar disambiguation.

---

This is excellent diagnostic output — now you know exactly what is broken and why. Let me answer your three questions.

---

## 1. Is adding a language hint text box a good idea?

Yes, but only for the calendar cases. Here is the honest analysis of which failures benefit from it:

**Would be fixed by a language hint:**
- B.1 `2568/5/8` — GPT-4o-mini returns `en`, needs `th` to trigger Thai Buddhist calendar
- B.5 `1404/2/15` — GPT-4o-mini returns `en`, needs `fa` to trigger Solar Hijri
- B.6 `114/5/8` — GPT-4o-mini can't distinguish Minguo from any other short date

**Would NOT be fixed by a language hint** (different root cause):
- A.1–A.3: FIELD_TYPES list is wrong — GPT-4o-mini doesn't know `passport_no` is a valid type
- C.4, C.5, C.8: vocabulary table issue — language is fine, field type is the problem
- D.1–D.4: router wiring issue — language is correct, strategy just isn't called
- F.1–F.5: router wiring issue — classification is perfect, transliteration not called
- G.1–G.7: strategy not implemented yet

So a language hint helps 3 out of 30 failures directly. It is still worth doing because calendar conversion is genuinely language-dependent and numeric-only dates are structurally ambiguous. But it will not solve most of what is failing.

---

## 2. Is the current GPT-4o-mini prompt the problem?

Yes — two specific issues:

**Problem A — FIELD_TYPES list is incomplete in the system prompt.** Looking at root cause 1, `passport_no`, `registration_no`, `email`, `id_no`, `total_assets` are not in the list you give GPT-4o-mini, so it correctly falls back to `unstructured_text`. This is a bug in `field_type_detector.py`, not in the prompt design.

**Problem B — No examples in the current prompt.** Your current prompt lists the options but gives no examples. The corrected `field_type_detector.py` I wrote earlier includes six worked examples in the system prompt — that is why it performs better. The examples show the model what `passport_no`, `legal_form`, `date_of_birth` look like in practice.

The prompt change for language hint I would suggest is this — add one sentence:

```python
"If the text could represent a date in multiple calendar systems "
"(e.g. a 3-part numeric date like 2568/5/8 or 114/5/8), "
"pay close attention to the language_code — it determines which "
"calendar system to use. A 4-digit year above 2400 is likely Thai Buddhist (th). "
"A 2-3 digit year is likely Minguo/ROC (zh). A 4-digit year 1300-1499 is likely Solar Hijri (fa)."
```

This alone would fix B.1, B.5, and B.6 without any UI change.

---

## 3. Do you have sufficient representative tests?

The current 40 tests are a good start but have three gaps:

**Gap 1 — No compound/full-name tests.** All person name tests are single words or single names. Real documents have `田中 太郎` (surname + given), `محمد بن عبد الله` (with particles), `Jean-François Müller` (hyphenated, cross-language). These are harder and more representative.

**Gap 2 — No suffix-in-context tests for Strategy C.** `株式会社` passes but `三菱商事株式会社` (legal form embedded in company name) needs suffix extraction. `GmbH` passes but `Müller & Söhne GmbH` (legal form at end of string) does not test the suffix matching logic.

**Gap 3 — No date format variants.** You test `2568/5/8` but not `08/05/2568` (day-first Thai format), not `พ.ศ. 2568` (with Thai era label), not `١٤/٠٣/١٤٤٥` (Hijri day-first Arabic-Indic). These are the formats that actually appear on documents.

---

## Best next steps in priority order

**Fix first — 30 minutes each, no new code:**

1. **Add missing FIELD_TYPES to `field_type_detector.py`** — add `passport_no`, `registration_no`, `email`, `id_no`, `total_assets`, `revenue`, `net_assets` to the list. This fixes root cause 1 (A.1–A.3, B.7–B.11) and adds 8 passes immediately.

2. **Add calendar hints to the GPT-4o-mini system prompt** — the sentence above about 4-digit years. Fixes B.1, B.5, B.6.

3. **Check `status_terms.json` for missing entries** — `現役`, `منتهي`, `aufgelöst` should be in the JSON. If they are, the vocabulary lookup wiring for `status` field type is the bug. If they are not, add them. This fixes C.4, C.5, C.8.

**Fix second — router wiring (1-2 hours with Copilot):**

4. **Wire Strategy D for `nationality` field type** — the geographic lookup exists, it is just not being called for `nationality`. One line change in `router.py`.

5. **Wire Strategy F for `person_name` field type** — transliteration exists in `src/`, the router just isn't calling it for `person_name`. One line change in `router.py`.

**Fix third — new implementation:**

6. **Epic 07 Strategy G** — character maps. This is the only item that requires new code.

**After the fixes, rerun the diagnostic.** You should expect to go from 10/40 to approximately 30/40 with fixes 1–5 alone. The remaining failures will be F and G specific cases.