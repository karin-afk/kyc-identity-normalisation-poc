# KYC Integration Diagnostic Report

**Run date:** 2026-05-10 19:28:23
**Examples:** 40
**Pipeline:** `detect_field_type()` → `process_field_row()` → `route_field()` → strategy
**Mocks:** None — all calls are real


## Summary

| Result | Count |
|---|---|
| ✅ Pass | 10 |
| ❌ Fail | 30 |
| Total | 40 |

| ID | Description | Result |
|---|---|---|
| I.1 | Arabic person name (unresolved) | ✅ PASS |
| G.7 | Portuguese tilde | ❌ FAIL |
| G.6 | Scandinavian Æ | ❌ FAIL |
| G.5 | Polish ł | ❌ FAIL |
| G.4 | Turkish dotted I | ❌ FAIL |
| G.3 | Spanish ñ | ❌ FAIL |
| G.2 | German ß | ❌ FAIL |
| G.1 | German umlaut expansion | ❌ FAIL |
| F.5 | Chinese name | ❌ FAIL |
| F.4 | Japanese surname | ❌ FAIL |
| F.3 | Greek male name | ❌ FAIL |
| F.2 | Russian male name | ❌ FAIL |
| F.1 | Russian female name | ❌ FAIL |
| D.4 | Country name in Greek | ❌ FAIL |
| D.3 | Country name in Russian | ❌ FAIL |
| D.2 | Country name in Japanese | ❌ FAIL |
| D.1 | Country name in Arabic | ❌ FAIL |
| C.9 | Greek legal form SA | ✅ PASS |
| C.8 | German status dissolved | ❌ FAIL |
| C.7 | Japanese role representative director | ✅ PASS |
| C.6 | Japanese role director | ✅ PASS |
| C.5 | Arabic status dissolved | ❌ FAIL |
| C.4 | Japanese status active | ❌ FAIL |
| C.3 | Russian LLC | ✅ PASS |
| C.2 | German GmbH | ✅ PASS |
| C.1 | Japanese legal form KK | ✅ PASS |
| B.11 | Arabic-Indic digits | ❌ FAIL |
| B.10 | Swiss apostrophe number format | ❌ FAIL |
| B.9 | European number format | ❌ FAIL |
| B.8 | Full-width parenthetical negative | ❌ FAIL |
| B.7 | Japanese triangle negative | ❌ FAIL |
| B.6 | Minguo (Taiwan ROC) date | ❌ FAIL |
| B.5 | Solar Hijri date | ❌ FAIL |
| B.4 | Hijri date with Arabic-Indic digits | ✅ PASS |
| B.3 | Japanese Showa era date | ✅ PASS |
| B.2 | Japanese Reiwa era date | ✅ PASS |
| B.1 | Thai Buddhist Era date | ❌ FAIL |
| A.3 | Email address | ❌ FAIL |
| A.2 | Registration number | ❌ FAIL |
| A.1 | Passport number | ❌ FAIL |

---

---

## A.1 — Passport number

| | |
|---|---|
| **Input** | `TK1234567` |
| **Expected field type** | `passport_no` |
| **Expected language** | `en` |
| **Expected normalised form** | `TK1234567` |
| **Expected method** | `PRESERVE` |
| **Notes** | Must come back byte-for-byte identical |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `passport_no` | `unstructured_text` | ⚠️ mismatch |
| **language** | `en` | `en` | ✅ match |
| **confidence** | — | `0.80` | — |
| **latency** | — | `3.77s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `unstructured_text` but expected `passport_no`. The router will process the field as `unstructured_text` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "TK1234567", "field_type": "unstructured_text", "language": "en"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `UNRESOLVED` |
| normalised_form | `None` |
| confidence | `0.00` |
| review_required | `True` |
| latency | `0.04s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `PRESERVE` | `UNRESOLVED` | ❌ FAIL |
| **normalised_form** | `TK1234567` | `None` | ❌ FAIL |

> ❌ **Method failure diagnosis:** GPT-4o-mini classified as 'unstructured_text' instead of 'passport_no'. The router received the wrong field type and could not find a matching strategy.

### Overall: ❌ FAIL

---

## A.2 — Registration number

| | |
|---|---|
| **Input** | `DE123456789` |
| **Expected field type** | `registration_no` |
| **Expected language** | `en` |
| **Expected normalised form** | `DE123456789` |
| **Expected method** | `PRESERVE` |
| **Notes** | Must come back byte-for-byte identical |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `registration_no` | `unstructured_text` | ⚠️ mismatch |
| **language** | `en` | `de` | ⚠️ mismatch |
| **confidence** | — | `0.80` | — |
| **latency** | — | `2.07s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `unstructured_text` but expected `registration_no`. The router will process the field as `unstructured_text` which may select the wrong strategy.

> ⚠️ **Classification mismatch on language.** GPT-4o-mini returned `de` but expected `en`. This may affect strategy selection (e.g. character map handler chosen for wrong language).

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "DE123456789", "field_type": "unstructured_text", "language": "de"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `UNRESOLVED` |
| normalised_form | `None` |
| confidence | `0.00` |
| review_required | `True` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `PRESERVE` | `UNRESOLVED` | ❌ FAIL |
| **normalised_form** | `DE123456789` | `None` | ❌ FAIL |

> ❌ **Method failure diagnosis:** GPT-4o-mini classified as 'unstructured_text' instead of 'registration_no'. The router received the wrong field type and could not find a matching strategy.

### Overall: ❌ FAIL

---

## A.3 — Email address

| | |
|---|---|
| **Input** | `test.user@example.com` |
| **Expected field type** | `email` |
| **Expected language** | `en` |
| **Expected normalised form** | `test.user@example.com` |
| **Expected method** | `PRESERVE` |
| **Notes** | Must come back byte-for-byte identical |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `email` | `unstructured_text` | ⚠️ mismatch |
| **language** | `en` | `en` | ✅ match |
| **confidence** | — | `0.90` | — |
| **latency** | — | `0.96s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `unstructured_text` but expected `email`. The router will process the field as `unstructured_text` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "test.user@example.com", "field_type": "unstructured_text", "language": "en"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `UNRESOLVED` |
| normalised_form | `None` |
| confidence | `0.00` |
| review_required | `True` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `PRESERVE` | `UNRESOLVED` | ❌ FAIL |
| **normalised_form** | `test.user@example.com` | `None` | ❌ FAIL |

> ❌ **Method failure diagnosis:** GPT-4o-mini classified as 'unstructured_text' instead of 'email'. The router received the wrong field type and could not find a matching strategy.

### Overall: ❌ FAIL

---

## B.1 — Thai Buddhist Era date

| | |
|---|---|
| **Input** | `2568/5/8` |
| **Expected field type** | `date_of_birth` |
| **Expected language** | `th` |
| **Expected normalised form** | `2025-05-08` |
| **Expected method** | `CALENDAR` |
| **Notes** | 2568 BE minus 543 = 2025 CE |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `date_of_birth` | `date_of_birth` | ✅ match |
| **language** | `th` | `en` | ⚠️ mismatch |
| **confidence** | — | `0.80` | — |
| **latency** | — | `1.21s` | — |

> ⚠️ **Classification mismatch on language.** GPT-4o-mini returned `en` but expected `th`. This may affect strategy selection (e.g. character map handler chosen for wrong language).

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "2568/5/8", "field_type": "date_of_birth", "language": "en"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CALENDAR` |
| normalised_form | `2568/5/8` |
| confidence | `0.95` |
| review_required | `True` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CALENDAR` | `CALENDAR` | ✅ PASS |
| **normalised_form** | `2025-05-08` | `2568/5/8` | ❌ FAIL |

> ❌ **Form failure diagnosis:** Calendar conversion produced '2568/5/8' instead of '2025-05-08'. Check the epoch calculation in the relevant calendar module.

### Overall: ❌ FAIL

---

## B.2 — Japanese Reiwa era date

| | |
|---|---|
| **Input** | `令和5年7月3日` |
| **Expected field type** | `date_of_birth` |
| **Expected language** | `ja` |
| **Expected normalised form** | `2023-07-03` |
| **Expected method** | `CALENDAR` |
| **Notes** | Reiwa 5 = 2023 |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `date_of_birth` | `date_of_birth` | ✅ match |
| **language** | `ja` | `ja` | ✅ match |
| **confidence** | — | `0.90` | — |
| **latency** | — | `1.33s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "令和5年7月3日", "field_type": "date_of_birth", "language": "ja"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CALENDAR` |
| normalised_form | `2023-07-03` |
| confidence | `0.95` |
| review_required | `True` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CALENDAR` | `CALENDAR` | ✅ PASS |
| **normalised_form** | `2023-07-03` | `2023-07-03` | ✅ PASS |

### Overall: ✅ PASS

---

## B.3 — Japanese Showa era date

| | |
|---|---|
| **Input** | `昭和60年3月12日` |
| **Expected field type** | `date_of_birth` |
| **Expected language** | `ja` |
| **Expected normalised form** | `1985-03-12` |
| **Expected method** | `CALENDAR` |
| **Notes** | Showa 60 = 1985 |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `date_of_birth` | `date_of_birth` | ✅ match |
| **language** | `ja` | `ja` | ✅ match |
| **confidence** | — | `0.90` | — |
| **latency** | — | `0.91s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "昭和60年3月12日", "field_type": "date_of_birth", "language": "ja"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CALENDAR` |
| normalised_form | `1985-03-12` |
| confidence | `0.95` |
| review_required | `True` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CALENDAR` | `CALENDAR` | ✅ PASS |
| **normalised_form** | `1985-03-12` | `1985-03-12` | ✅ PASS |

### Overall: ✅ PASS

---

## B.4 — Hijri date with Arabic-Indic digits

| | |
|---|---|
| **Input** | `١٤٤٥/٠٩/٠١` |
| **Expected field type** | `date_of_birth` |
| **Expected language** | `ar` |
| **Expected normalised form** | `2024-03-11` |
| **Expected method** | `CALENDAR` |
| **Notes** | Arabic-Indic digits converted then Hijri→Gregorian |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `date_of_birth` | `date_of_birth` | ✅ match |
| **language** | `ar` | `ar` | ✅ match |
| **confidence** | — | `0.90` | — |
| **latency** | — | `0.65s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "١٤٤٥/٠٩/٠١", "field_type": "date_of_birth", "language": "ar"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CALENDAR` |
| normalised_form | `2024-03-11` |
| confidence | `0.95` |
| review_required | `True` |
| latency | `0.03s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CALENDAR` | `CALENDAR` | ✅ PASS |
| **normalised_form** | `2024-03-11` | `2024-03-11` | ✅ PASS |

### Overall: ✅ PASS

---

## B.5 — Solar Hijri date

| | |
|---|---|
| **Input** | `1404/2/15` |
| **Expected field type** | `date_of_birth` |
| **Expected language** | `fa` |
| **Expected normalised form** | `2025-05-05` |
| **Expected method** | `CALENDAR` |
| **Notes** | Persian Solar Hijri calendar |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `date_of_birth` | `date_of_birth` | ✅ match |
| **language** | `fa` | `en` | ⚠️ mismatch |
| **confidence** | — | `0.90` | — |
| **latency** | — | `0.99s` | — |

> ⚠️ **Classification mismatch on language.** GPT-4o-mini returned `en` but expected `fa`. This may affect strategy selection (e.g. character map handler chosen for wrong language).

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "1404/2/15", "field_type": "date_of_birth", "language": "en"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CALENDAR` |
| normalised_form | `1983-11-19` |
| confidence | `0.95` |
| review_required | `True` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CALENDAR` | `CALENDAR` | ✅ PASS |
| **normalised_form** | `2025-05-05` | `1983-11-19` | ❌ FAIL |

> ❌ **Form failure diagnosis:** Calendar conversion produced '1983-11-19' instead of '2025-05-05'. Check the epoch calculation in the relevant calendar module.

### Overall: ❌ FAIL

---

## B.6 — Minguo (Taiwan ROC) date

| | |
|---|---|
| **Input** | `114/5/8` |
| **Expected field type** | `date_of_birth` |
| **Expected language** | `zh` |
| **Expected normalised form** | `2025-05-08` |
| **Expected method** | `['CALENDAR']` |
| **Notes** | Minguo 114 + 1911 = 2025 |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `date_of_birth` | `unstructured_text` | ⚠️ mismatch |
| **language** | `zh` | `en` | ⚠️ mismatch |
| **confidence** | — | `0.70` | — |
| **latency** | — | `0.97s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `unstructured_text` but expected `date_of_birth`. The router will process the field as `unstructured_text` which may select the wrong strategy.

> ⚠️ **Classification mismatch on language.** GPT-4o-mini returned `en` but expected `zh`. This may affect strategy selection (e.g. character map handler chosen for wrong language).

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "114/5/8", "field_type": "unstructured_text", "language": "en"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `UNRESOLVED` |
| normalised_form | `None` |
| confidence | `0.00` |
| review_required | `True` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CALENDAR` | `UNRESOLVED` | ❌ FAIL |
| **normalised_form** | `2025-05-08` | `None` | ❌ FAIL |

> ❌ **Method failure diagnosis:** GPT-4o-mini classified as 'unstructured_text' instead of 'date_of_birth'. The router received the wrong field type and could not find a matching strategy.

### Overall: ❌ FAIL

---

## B.7 — Japanese triangle negative

| | |
|---|---|
| **Input** | `△4,191` |
| **Expected field type** | `total_assets` |
| **Expected language** | `ja` |
| **Expected normalised form** | `-4191` |
| **Expected method** | `NUMERIC` |
| **Notes** | Japanese accounting triangle notation for negative |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `total_assets` | `unstructured_text` | ⚠️ mismatch |
| **language** | `ja` | `en` | ⚠️ mismatch |
| **confidence** | — | `0.80` | — |
| **latency** | — | `0.64s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `unstructured_text` but expected `total_assets`. The router will process the field as `unstructured_text` which may select the wrong strategy.

> ⚠️ **Classification mismatch on language.** GPT-4o-mini returned `en` but expected `ja`. This may affect strategy selection (e.g. character map handler chosen for wrong language).

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "△4,191", "field_type": "unstructured_text", "language": "en"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `UNRESOLVED` |
| normalised_form | `None` |
| confidence | `0.00` |
| review_required | `True` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `NUMERIC` | `UNRESOLVED` | ❌ FAIL |
| **normalised_form** | `-4191` | `None` | ❌ FAIL |

> ❌ **Method failure diagnosis:** GPT-4o-mini classified as 'unstructured_text' instead of 'total_assets'. The router received the wrong field type and could not find a matching strategy.

### Overall: ❌ FAIL

---

## B.8 — Full-width parenthetical negative

| | |
|---|---|
| **Input** | `（4,191）` |
| **Expected field type** | `total_assets` |
| **Expected language** | `ja` |
| **Expected normalised form** | `-4191` |
| **Expected method** | `NUMERIC` |
| **Notes** | Full-width parentheses negative |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `total_assets` | `unstructured_text` | ⚠️ mismatch |
| **language** | `ja` | `zh` | ⚠️ mismatch |
| **confidence** | — | `0.80` | — |
| **latency** | — | `0.78s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `unstructured_text` but expected `total_assets`. The router will process the field as `unstructured_text` which may select the wrong strategy.

> ⚠️ **Classification mismatch on language.** GPT-4o-mini returned `zh` but expected `ja`. This may affect strategy selection (e.g. character map handler chosen for wrong language).

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "（4,191）", "field_type": "unstructured_text", "language": "zh"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `UNRESOLVED` |
| normalised_form | `None` |
| confidence | `0.00` |
| review_required | `True` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `NUMERIC` | `UNRESOLVED` | ❌ FAIL |
| **normalised_form** | `-4191` | `None` | ❌ FAIL |

> ❌ **Method failure diagnosis:** GPT-4o-mini classified as 'unstructured_text' instead of 'total_assets'. The router received the wrong field type and could not find a matching strategy.

### Overall: ❌ FAIL

---

## B.9 — European number format

| | |
|---|---|
| **Input** | `1.234.567,89` |
| **Expected field type** | `total_assets` |
| **Expected language** | `de` |
| **Expected normalised form** | `1234567.89` |
| **Expected method** | `NUMERIC` |
| **Notes** | Period=thousands, comma=decimal in German format |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `total_assets` | `unstructured_text` | ⚠️ mismatch |
| **language** | `de` | `en` | ⚠️ mismatch |
| **confidence** | — | `0.80` | — |
| **latency** | — | `1.41s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `unstructured_text` but expected `total_assets`. The router will process the field as `unstructured_text` which may select the wrong strategy.

> ⚠️ **Classification mismatch on language.** GPT-4o-mini returned `en` but expected `de`. This may affect strategy selection (e.g. character map handler chosen for wrong language).

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "1.234.567,89", "field_type": "unstructured_text", "language": "en"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `UNRESOLVED` |
| normalised_form | `None` |
| confidence | `0.00` |
| review_required | `True` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `NUMERIC` | `UNRESOLVED` | ❌ FAIL |
| **normalised_form** | `1234567.89` | `None` | ❌ FAIL |

> ❌ **Method failure diagnosis:** GPT-4o-mini classified as 'unstructured_text' instead of 'total_assets'. The router received the wrong field type and could not find a matching strategy.

### Overall: ❌ FAIL

---

## B.10 — Swiss apostrophe number format

| | |
|---|---|
| **Input** | `1'234'567.89` |
| **Expected field type** | `total_assets` |
| **Expected language** | `fr` |
| **Expected normalised form** | `1234567.89` |
| **Expected method** | `NUMERIC` |
| **Notes** | Swiss apostrophe thousands separator |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `total_assets` | `unstructured_text` | ⚠️ mismatch |
| **language** | `fr` | `en` | ⚠️ mismatch |
| **confidence** | — | `0.80` | — |
| **latency** | — | `0.60s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `unstructured_text` but expected `total_assets`. The router will process the field as `unstructured_text` which may select the wrong strategy.

> ⚠️ **Classification mismatch on language.** GPT-4o-mini returned `en` but expected `fr`. This may affect strategy selection (e.g. character map handler chosen for wrong language).

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "1'234'567.89", "field_type": "unstructured_text", "language": "en"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `UNRESOLVED` |
| normalised_form | `None` |
| confidence | `0.00` |
| review_required | `True` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `NUMERIC` | `UNRESOLVED` | ❌ FAIL |
| **normalised_form** | `1234567.89` | `None` | ❌ FAIL |

> ❌ **Method failure diagnosis:** GPT-4o-mini classified as 'unstructured_text' instead of 'total_assets'. The router received the wrong field type and could not find a matching strategy.

### Overall: ❌ FAIL

---

## B.11 — Arabic-Indic digits

| | |
|---|---|
| **Input** | `٠١٢٣٤٥٦٧٨٩` |
| **Expected field type** | `id_no` |
| **Expected language** | `ar` |
| **Expected normalised form** | `٠١٢٣٤٥٦٧٨٩` |
| **Expected method** | `PRESERVE` |
| **Notes** | Arabic-Indic digits in an ID field must be preserved verbatim (Strategy A) |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `id_no` | `unstructured_text` | ⚠️ mismatch |
| **language** | `ar` | `ar` | ✅ match |
| **confidence** | — | `0.90` | — |
| **latency** | — | `1.76s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `unstructured_text` but expected `id_no`. The router will process the field as `unstructured_text` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "٠١٢٣٤٥٦٧٨٩", "field_type": "unstructured_text", "language": "ar"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `NUMERIC` |
| normalised_form | `0123456789` |
| confidence | `0.90` |
| review_required | `False` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `PRESERVE` | `NUMERIC` | ❌ FAIL |
| **normalised_form** | `٠١٢٣٤٥٦٧٨٩` | `0123456789` | ❌ FAIL |

> ❌ **Method failure diagnosis:** Got 'NUMERIC', expected one of ['PRESERVE']. Check router.py strategy wiring.

### Overall: ❌ FAIL

---

## C.1 — Japanese legal form KK

| | |
|---|---|
| **Input** | `株式会社` |
| **Expected field type** | `legal_form` |
| **Expected language** | `ja` |
| **Expected normalised form** | `KK` |
| **Expected method** | `VOCABULARY` |
| **Notes** | Most common Japanese corporate form |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `legal_form` | `legal_form` | ✅ match |
| **language** | `ja` | `ja` | ✅ match |
| **confidence** | — | `0.90` | — |
| **latency** | — | `3.37s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "株式会社", "field_type": "legal_form", "language": "ja"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `VOCABULARY` |
| normalised_form | `KK` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `VOCABULARY` | `VOCABULARY` | ✅ PASS |
| **normalised_form** | `KK` | `KK` | ✅ PASS |

### Overall: ✅ PASS

---

## C.2 — German GmbH

| | |
|---|---|
| **Input** | `GmbH` |
| **Expected field type** | `legal_form` |
| **Expected language** | `de` |
| **Expected normalised form** | `GMBH` |
| **Expected method** | `VOCABULARY` |
| **Notes** | German limited liability company |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `legal_form` | `legal_form` | ✅ match |
| **language** | `de` | `de` | ✅ match |
| **confidence** | — | `0.90` | — |
| **latency** | — | `0.83s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "GmbH", "field_type": "legal_form", "language": "de"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `VOCABULARY` |
| normalised_form | `GMBH` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `VOCABULARY` | `VOCABULARY` | ✅ PASS |
| **normalised_form** | `GMBH` | `GMBH` | ✅ PASS |

### Overall: ✅ PASS

---

## C.3 — Russian LLC

| | |
|---|---|
| **Input** | `ООО` |
| **Expected field type** | `legal_form` |
| **Expected language** | `ru` |
| **Expected normalised form** | `LLC` |
| **Expected method** | `VOCABULARY` |
| **Notes** | Russian OOO = LLC |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `legal_form` | `legal_form` | ✅ match |
| **language** | `ru` | `ru` | ✅ match |
| **confidence** | — | `0.90` | — |
| **latency** | — | `1.91s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "ООО", "field_type": "legal_form", "language": "ru"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `VOCABULARY` |
| normalised_form | `LLC` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `VOCABULARY` | `VOCABULARY` | ✅ PASS |
| **normalised_form** | `LLC` | `LLC` | ✅ PASS |

### Overall: ✅ PASS

---

## C.4 — Japanese status active

| | |
|---|---|
| **Input** | `現役` |
| **Expected field type** | `status` |
| **Expected language** | `ja` |
| **Expected normalised form** | `ACTIVE` |
| **Expected method** | `VOCABULARY` |
| **Notes** | Active status in Japanese |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `status` | `unstructured_text` | ⚠️ mismatch |
| **language** | `ja` | `ja` | ✅ match |
| **confidence** | — | `0.80` | — |
| **latency** | — | `0.75s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `unstructured_text` but expected `status`. The router will process the field as `unstructured_text` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "現役", "field_type": "unstructured_text", "language": "ja"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `UNRESOLVED` |
| normalised_form | `None` |
| confidence | `0.00` |
| review_required | `True` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `VOCABULARY` | `UNRESOLVED` | ❌ FAIL |
| **normalised_form** | `ACTIVE` | `None` | ❌ FAIL |

> ❌ **Method failure diagnosis:** GPT-4o-mini classified as 'unstructured_text' instead of 'status'. The router received the wrong field type and could not find a matching strategy.

### Overall: ❌ FAIL

---

## C.5 — Arabic status dissolved

| | |
|---|---|
| **Input** | `منتهي` |
| **Expected field type** | `status` |
| **Expected language** | `ar` |
| **Expected normalised form** | `DISSOLVED` |
| **Expected method** | `VOCABULARY` |
| **Notes** | Dissolved status in Arabic |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `status` | `unstructured_text` | ⚠️ mismatch |
| **language** | `ar` | `ar` | ✅ match |
| **confidence** | — | `0.70` | — |
| **latency** | — | `0.87s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `unstructured_text` but expected `status`. The router will process the field as `unstructured_text` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "منتهي", "field_type": "unstructured_text", "language": "ar"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `UNRESOLVED` |
| normalised_form | `None` |
| confidence | `0.00` |
| review_required | `True` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `VOCABULARY` | `UNRESOLVED` | ❌ FAIL |
| **normalised_form** | `DISSOLVED` | `None` | ❌ FAIL |

> ❌ **Method failure diagnosis:** GPT-4o-mini classified as 'unstructured_text' instead of 'status'. The router received the wrong field type and could not find a matching strategy.

### Overall: ❌ FAIL

---

## C.6 — Japanese role director

| | |
|---|---|
| **Input** | `取締役` |
| **Expected field type** | `role` |
| **Expected language** | `ja` |
| **Expected normalised form** | `DIRECTOR` |
| **Expected method** | `VOCABULARY` |
| **Notes** | Standard director role |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `role` | `role` | ✅ match |
| **language** | `ja` | `ja` | ✅ match |
| **confidence** | — | `0.90` | — |
| **latency** | — | `0.77s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "取締役", "field_type": "role", "language": "ja"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `VOCABULARY` |
| normalised_form | `DIRECTOR` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `VOCABULARY` | `VOCABULARY` | ✅ PASS |
| **normalised_form** | `DIRECTOR` | `DIRECTOR` | ✅ PASS |

### Overall: ✅ PASS

---

## C.7 — Japanese role representative director

| | |
|---|---|
| **Input** | `代表取締役` |
| **Expected field type** | `role` |
| **Expected language** | `ja` |
| **Expected normalised form** | `REPRESENTATIVE DIRECTOR` |
| **Expected method** | `VOCABULARY` |
| **Notes** | Most senior role in Japanese company |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `role` | `role` | ✅ match |
| **language** | `ja` | `ja` | ✅ match |
| **confidence** | — | `0.90` | — |
| **latency** | — | `0.95s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "代表取締役", "field_type": "role", "language": "ja"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `VOCABULARY` |
| normalised_form | `REPRESENTATIVE DIRECTOR` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `VOCABULARY` | `VOCABULARY` | ✅ PASS |
| **normalised_form** | `REPRESENTATIVE DIRECTOR` | `REPRESENTATIVE DIRECTOR` | ✅ PASS |

### Overall: ✅ PASS

---

## C.8 — German status dissolved

| | |
|---|---|
| **Input** | `aufgelöst` |
| **Expected field type** | `status` |
| **Expected language** | `de` |
| **Expected normalised form** | `DISSOLVED` |
| **Expected method** | `VOCABULARY` |
| **Notes** | German dissolved status |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `status` | `unstructured_text` | ⚠️ mismatch |
| **language** | `de` | `de` | ✅ match |
| **confidence** | — | `0.80` | — |
| **latency** | — | `0.67s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `unstructured_text` but expected `status`. The router will process the field as `unstructured_text` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "aufgelöst", "field_type": "unstructured_text", "language": "de"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `UNRESOLVED` |
| normalised_form | `None` |
| confidence | `0.00` |
| review_required | `True` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `VOCABULARY` | `UNRESOLVED` | ❌ FAIL |
| **normalised_form** | `DISSOLVED` | `None` | ❌ FAIL |

> ❌ **Method failure diagnosis:** GPT-4o-mini classified as 'unstructured_text' instead of 'status'. The router received the wrong field type and could not find a matching strategy.

### Overall: ❌ FAIL

---

## C.9 — Greek legal form SA

| | |
|---|---|
| **Input** | `Α.Ε.` |
| **Expected field type** | `legal_form` |
| **Expected language** | `el` |
| **Expected normalised form** | `SA` |
| **Expected method** | `VOCABULARY` |
| **Notes** | Greek Anonymi Etaireia = SA |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `legal_form` | `legal_form` | ✅ match |
| **language** | `el` | `el` | ✅ match |
| **confidence** | — | `0.90` | — |
| **latency** | — | `0.63s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Α.Ε.", "field_type": "legal_form", "language": "el"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `VOCABULARY` |
| normalised_form | `SA` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `VOCABULARY` | `VOCABULARY` | ✅ PASS |
| **normalised_form** | `SA` | `SA` | ✅ PASS |

### Overall: ✅ PASS

---

## D.1 — Country name in Arabic

| | |
|---|---|
| **Input** | `ألمانيا` |
| **Expected field type** | `nationality` |
| **Expected language** | `ar` |
| **Expected normalised form** | `GERMANY` |
| **Expected method** | `GEOGRAPHIC` |
| **Notes** | Germany in Arabic |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `nationality` | `nationality` | ✅ match |
| **language** | `ar` | `ar` | ✅ match |
| **confidence** | — | `0.90` | — |
| **latency** | — | `0.68s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "ألمانيا", "field_type": "nationality", "language": "ar"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `GEOGRAPHIC` |
| normalised_form | `GERMAN` |
| confidence | `0.88` |
| review_required | `True` |
| latency | `0.02s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `GEOGRAPHIC` | `GEOGRAPHIC` | ✅ PASS |
| **normalised_form** | `GERMANY` | `GERMAN` | ❌ FAIL |

> ❌ **Form failure diagnosis:** Got 'GERMAN', expected 'GERMANY'. Inspect the strategy module output.

### Overall: ❌ FAIL

---

## D.2 — Country name in Japanese

| | |
|---|---|
| **Input** | `日本` |
| **Expected field type** | `nationality` |
| **Expected language** | `ja` |
| **Expected normalised form** | `JAPAN` |
| **Expected method** | `GEOGRAPHIC` |
| **Notes** | Japan in Japanese |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `nationality` | `nationality` | ✅ match |
| **language** | `ja` | `ja` | ✅ match |
| **confidence** | — | `0.90` | — |
| **latency** | — | `0.55s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "日本", "field_type": "nationality", "language": "ja"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `GEOGRAPHIC` |
| normalised_form | `JAPANESE` |
| confidence | `0.88` |
| review_required | `True` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `GEOGRAPHIC` | `GEOGRAPHIC` | ✅ PASS |
| **normalised_form** | `JAPAN` | `JAPANESE` | ❌ FAIL |

> ❌ **Form failure diagnosis:** Got 'JAPANESE', expected 'JAPAN'. Inspect the strategy module output.

### Overall: ❌ FAIL

---

## D.3 — Country name in Russian

| | |
|---|---|
| **Input** | `Германия` |
| **Expected field type** | `nationality` |
| **Expected language** | `ru` |
| **Expected normalised form** | `GERMANY` |
| **Expected method** | `GEOGRAPHIC` |
| **Notes** | Germany in Russian |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `nationality` | `nationality` | ✅ match |
| **language** | `ru` | `bg` | ⚠️ mismatch |
| **confidence** | — | `0.90` | — |
| **latency** | — | `0.62s` | — |

> ⚠️ **Classification mismatch on language.** GPT-4o-mini returned `bg` but expected `ru`. This may affect strategy selection (e.g. character map handler chosen for wrong language).

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Германия", "field_type": "nationality", "language": "bg"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `GEOGRAPHIC` |
| normalised_form | `GERMAN` |
| confidence | `0.88` |
| review_required | `True` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `GEOGRAPHIC` | `GEOGRAPHIC` | ✅ PASS |
| **normalised_form** | `GERMANY` | `GERMAN` | ❌ FAIL |

> ❌ **Form failure diagnosis:** Got 'GERMAN', expected 'GERMANY'. Inspect the strategy module output.

### Overall: ❌ FAIL

---

## D.4 — Country name in Greek

| | |
|---|---|
| **Input** | `Γερμανία` |
| **Expected field type** | `nationality` |
| **Expected language** | `el` |
| **Expected normalised form** | `GERMANY` |
| **Expected method** | `GEOGRAPHIC` |
| **Notes** | Germany in Greek |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `nationality` | `nationality` | ✅ match |
| **language** | `el` | `el` | ✅ match |
| **confidence** | — | `0.90` | — |
| **latency** | — | `0.62s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Γερμανία", "field_type": "nationality", "language": "el"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `GEOGRAPHIC` |
| normalised_form | `GERMAN` |
| confidence | `0.88` |
| review_required | `True` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `GEOGRAPHIC` | `GEOGRAPHIC` | ✅ PASS |
| **normalised_form** | `GERMANY` | `GERMAN` | ❌ FAIL |

> ❌ **Form failure diagnosis:** Got 'GERMAN', expected 'GERMANY'. Inspect the strategy module output.

### Overall: ❌ FAIL

---

## F.1 — Russian female name

| | |
|---|---|
| **Input** | `Наталья` |
| **Expected field type** | `person_name` |
| **Expected language** | `ru` |
| **Expected normalised form** | `NATALYA` |
| **Expected method** | `['TRANSLITERATION', 'TRANSLITERATE']` |
| **Notes** | BGN/PCGN standard |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `person_name` | ✅ match |
| **language** | `ru` | `ru` | ✅ match |
| **confidence** | — | `0.90` | — |
| **latency** | — | `0.85s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Наталья", "field_type": "person_name", "language": "ru"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `UNRESOLVED` |
| normalised_form | `None` |
| confidence | `0.00` |
| review_required | `True` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `TRANSLITERATION` or `TRANSLITERATE` | `UNRESOLVED` | ❌ FAIL |
| **normalised_form** | `NATALYA` | `None` | ❌ FAIL |

> ❌ **Method failure diagnosis:** The strategy for field_type='person_name' language='ru' returned None or raised NotImplementedError. Check that the strategy module is fully implemented and wired into the router.

### Overall: ❌ FAIL

---

## F.2 — Russian male name

| | |
|---|---|
| **Input** | `Александр` |
| **Expected field type** | `person_name` |
| **Expected language** | `ru` |
| **Expected normalised form** | `ALEKSANDR` |
| **Expected method** | `['TRANSLITERATION', 'TRANSLITERATE']` |
| **Notes** | BGN/PCGN standard |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `person_name` | ✅ match |
| **language** | `ru` | `ru` | ✅ match |
| **confidence** | — | `0.90` | — |
| **latency** | — | `0.65s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Александр", "field_type": "person_name", "language": "ru"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `UNRESOLVED` |
| normalised_form | `None` |
| confidence | `0.00` |
| review_required | `True` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `TRANSLITERATION` or `TRANSLITERATE` | `UNRESOLVED` | ❌ FAIL |
| **normalised_form** | `ALEKSANDR` | `None` | ❌ FAIL |

> ❌ **Method failure diagnosis:** The strategy for field_type='person_name' language='ru' returned None or raised NotImplementedError. Check that the strategy module is fully implemented and wired into the router.

### Overall: ❌ FAIL

---

## F.3 — Greek male name

| | |
|---|---|
| **Input** | `Νίκος` |
| **Expected field type** | `person_name` |
| **Expected language** | `el` |
| **Expected normalised form** | `NIKOS` |
| **Expected method** | `['TRANSLITERATION', 'TRANSLITERATE']` |
| **Notes** | Greek to Latin |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `person_name` | ✅ match |
| **language** | `el` | `el` | ✅ match |
| **confidence** | — | `0.90` | — |
| **latency** | — | `0.56s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Νίκος", "field_type": "person_name", "language": "el"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `UNRESOLVED` |
| normalised_form | `None` |
| confidence | `0.00` |
| review_required | `True` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `TRANSLITERATION` or `TRANSLITERATE` | `UNRESOLVED` | ❌ FAIL |
| **normalised_form** | `NIKOS` | `None` | ❌ FAIL |

> ❌ **Method failure diagnosis:** The strategy for field_type='person_name' language='el' returned None or raised NotImplementedError. Check that the strategy module is fully implemented and wired into the router.

### Overall: ❌ FAIL

---

## F.4 — Japanese surname

| | |
|---|---|
| **Input** | `田中` |
| **Expected field type** | `person_name` |
| **Expected language** | `ja` |
| **Expected normalised form** | `TANAKA` |
| **Expected method** | `['TRANSLITERATION', 'TRANSLITERATE']` |
| **Notes** | Hepburn romanisation |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `person_name` | ✅ match |
| **language** | `ja` | `ja` | ✅ match |
| **confidence** | — | `0.90` | — |
| **latency** | — | `0.91s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "田中", "field_type": "person_name", "language": "ja"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `UNRESOLVED` |
| normalised_form | `None` |
| confidence | `0.00` |
| review_required | `True` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `TRANSLITERATION` or `TRANSLITERATE` | `UNRESOLVED` | ❌ FAIL |
| **normalised_form** | `TANAKA` | `None` | ❌ FAIL |

> ❌ **Method failure diagnosis:** The strategy for field_type='person_name' language='ja' returned None or raised NotImplementedError. Check that the strategy module is fully implemented and wired into the router.

### Overall: ❌ FAIL

---

## F.5 — Chinese name

| | |
|---|---|
| **Input** | `王小明` |
| **Expected field type** | `person_name` |
| **Expected language** | `zh` |
| **Expected normalised form** | `WANG XIAOMING` |
| **Expected method** | `['TRANSLITERATION', 'TRANSLITERATE']` |
| **Notes** | Pinyin romanisation |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `person_name` | ✅ match |
| **language** | `zh` | `zh` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.58s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "王小明", "field_type": "person_name", "language": "zh"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `UNRESOLVED` |
| normalised_form | `None` |
| confidence | `0.00` |
| review_required | `True` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `TRANSLITERATION` or `TRANSLITERATE` | `UNRESOLVED` | ❌ FAIL |
| **normalised_form** | `WANG XIAOMING` | `None` | ❌ FAIL |

> ❌ **Method failure diagnosis:** The strategy for field_type='person_name' language='zh' returned None or raised NotImplementedError. Check that the strategy module is fully implemented and wired into the router.

### Overall: ❌ FAIL

---

## G.1 — German umlaut expansion

| | |
|---|---|
| **Input** | `Müller` |
| **Expected field type** | `person_name` |
| **Expected language** | `de` |
| **Expected normalised form** | `MUELLER` |
| **Expected method** | `CHARACTER_MAP` |
| **Notes** | ü→UE primary form, MULLER variant |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `person_name` | ✅ match |
| **language** | `de` | `de` | ✅ match |
| **confidence** | — | `0.90` | — |
| **latency** | — | `0.62s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Müller", "field_type": "person_name", "language": "de"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `UNRESOLVED` |
| normalised_form | `None` |
| confidence | `0.00` |
| review_required | `True` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CHARACTER_MAP` | `UNRESOLVED` | ❌ FAIL |
| **normalised_form** | `MUELLER` | `None` | ❌ FAIL |

> ❌ **Method failure diagnosis:** The strategy for field_type='person_name' language='de' returned None or raised NotImplementedError. Check that the strategy module is fully implemented and wired into the router.

### Overall: ❌ FAIL

---

## G.2 — German ß

| | |
|---|---|
| **Input** | `Straße` |
| **Expected field type** | `person_name` |
| **Expected language** | `de` |
| **Expected normalised form** | `STRASSE` |
| **Expected method** | `CHARACTER_MAP` |
| **Notes** | ß→SS |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `address` | ⚠️ mismatch |
| **language** | `de` | `de` | ✅ match |
| **confidence** | — | `0.90` | — |
| **latency** | — | `1.00s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `address` but expected `person_name`. The router will process the field as `address` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Straße", "field_type": "address", "language": "de"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `UNRESOLVED` |
| normalised_form | `None` |
| confidence | `0.00` |
| review_required | `True` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CHARACTER_MAP` | `UNRESOLVED` | ❌ FAIL |
| **normalised_form** | `STRASSE` | `None` | ❌ FAIL |

> ❌ **Method failure diagnosis:** GPT-4o-mini classified as 'address' instead of 'person_name'. The router received the wrong field type and could not find a matching strategy.

### Overall: ❌ FAIL

---

## G.3 — Spanish ñ

| | |
|---|---|
| **Input** | `Muñoz` |
| **Expected field type** | `person_name` |
| **Expected language** | `es` |
| **Expected normalised form** | `MUNOZ` |
| **Expected method** | `CHARACTER_MAP` |
| **Notes** | ñ→N primary, MUNYOZ variant |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `person_name` | ✅ match |
| **language** | `es` | `es` | ✅ match |
| **confidence** | — | `0.90` | — |
| **latency** | — | `0.63s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Muñoz", "field_type": "person_name", "language": "es"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `UNRESOLVED` |
| normalised_form | `None` |
| confidence | `0.00` |
| review_required | `True` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CHARACTER_MAP` | `UNRESOLVED` | ❌ FAIL |
| **normalised_form** | `MUNOZ` | `None` | ❌ FAIL |

> ❌ **Method failure diagnosis:** The strategy for field_type='person_name' language='es' returned None or raised NotImplementedError. Check that the strategy module is fully implemented and wired into the router.

### Overall: ❌ FAIL

---

## G.4 — Turkish dotted I

| | |
|---|---|
| **Input** | `İstanbul` |
| **Expected field type** | `person_name` |
| **Expected language** | `tr` |
| **Expected normalised form** | `ISTANBUL` |
| **Expected method** | `CHARACTER_MAP` |
| **Notes** | İ (U+0130) → I |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `address` | ⚠️ mismatch |
| **language** | `tr` | `tr` | ✅ match |
| **confidence** | — | `0.90` | — |
| **latency** | — | `0.70s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `address` but expected `person_name`. The router will process the field as `address` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "İstanbul", "field_type": "address", "language": "tr"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `UNRESOLVED` |
| normalised_form | `None` |
| confidence | `0.00` |
| review_required | `True` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CHARACTER_MAP` | `UNRESOLVED` | ❌ FAIL |
| **normalised_form** | `ISTANBUL` | `None` | ❌ FAIL |

> ❌ **Method failure diagnosis:** GPT-4o-mini classified as 'address' instead of 'person_name'. The router received the wrong field type and could not find a matching strategy.

### Overall: ❌ FAIL

---

## G.5 — Polish ł

| | |
|---|---|
| **Input** | `Łódź` |
| **Expected field type** | `person_name` |
| **Expected language** | `pl` |
| **Expected normalised form** | `LODZ` |
| **Expected method** | `CHARACTER_MAP` |
| **Notes** | Ł→L, ó→O, ź→Z |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `address` | ⚠️ mismatch |
| **language** | `pl` | `pl` | ✅ match |
| **confidence** | — | `0.90` | — |
| **latency** | — | `0.62s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `address` but expected `person_name`. The router will process the field as `address` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Łódź", "field_type": "address", "language": "pl"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `UNRESOLVED` |
| normalised_form | `None` |
| confidence | `0.00` |
| review_required | `True` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CHARACTER_MAP` | `UNRESOLVED` | ❌ FAIL |
| **normalised_form** | `LODZ` | `None` | ❌ FAIL |

> ❌ **Method failure diagnosis:** GPT-4o-mini classified as 'address' instead of 'person_name'. The router received the wrong field type and could not find a matching strategy.

### Overall: ❌ FAIL

---

## G.6 — Scandinavian Æ

| | |
|---|---|
| **Input** | `Ærø` |
| **Expected field type** | `person_name` |
| **Expected language** | `da` |
| **Expected normalised form** | `AERO` |
| **Expected method** | `CHARACTER_MAP` |
| **Notes** | Æ→AE, ø→O |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `unstructured_text` | ⚠️ mismatch |
| **language** | `da` | `da` | ✅ match |
| **confidence** | — | `0.70` | — |
| **latency** | — | `0.78s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `unstructured_text` but expected `person_name`. The router will process the field as `unstructured_text` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Ærø", "field_type": "unstructured_text", "language": "da"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `UNRESOLVED` |
| normalised_form | `None` |
| confidence | `0.00` |
| review_required | `True` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CHARACTER_MAP` | `UNRESOLVED` | ❌ FAIL |
| **normalised_form** | `AERO` | `None` | ❌ FAIL |

> ❌ **Method failure diagnosis:** GPT-4o-mini classified as 'unstructured_text' instead of 'person_name'. The router received the wrong field type and could not find a matching strategy.

### Overall: ❌ FAIL

---

## G.7 — Portuguese tilde

| | |
|---|---|
| **Input** | `João` |
| **Expected field type** | `person_name` |
| **Expected language** | `pt` |
| **Expected normalised form** | `JOAO` |
| **Expected method** | `CHARACTER_MAP` |
| **Notes** | ã→A |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `person_name` | ✅ match |
| **language** | `pt` | `pt` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.59s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "João", "field_type": "person_name", "language": "pt"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `UNRESOLVED` |
| normalised_form | `None` |
| confidence | `0.00` |
| review_required | `True` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CHARACTER_MAP` | `UNRESOLVED` | ❌ FAIL |
| **normalised_form** | `JOAO` | `None` | ❌ FAIL |

> ❌ **Method failure diagnosis:** The strategy for field_type='person_name' language='pt' returned None or raised NotImplementedError. Check that the strategy module is fully implemented and wired into the router.

### Overall: ❌ FAIL

---

## I.1 — Arabic person name (unresolved)

| | |
|---|---|
| **Input** | `محمد عبد الله` |
| **Expected field type** | `person_name` |
| **Expected language** | `ar` |
| **Expected normalised form** | `None` |
| **Expected method** | `UNRESOLVED` |
| **Notes** | Arabic names cannot be deterministically transliterated — correct to route to review |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `person_name` | ✅ match |
| **language** | `ar` | `ar` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.57s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "محمد عبد الله", "field_type": "person_name", "language": "ar"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `UNRESOLVED` |
| normalised_form | `None` |
| confidence | `0.00` |
| review_required | `True` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `UNRESOLVED` | `UNRESOLVED` | ✅ PASS |
| **normalised_form** | `None` | `None` | ✅ PASS |

### Overall: ✅ PASS

---
