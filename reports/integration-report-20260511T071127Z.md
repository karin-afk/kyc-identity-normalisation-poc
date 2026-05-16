# KYC Integration Diagnostic Report

**Run date:** 2026-05-11 07:09:53
**Examples:** 74
**Pipeline:** `detect_field_type()` → `process_field_row()` → `route_field()` → strategy
**Mocks:** None — all calls are real


## Summary

| Result | Count |
|---|---|
| ✅ Pass | 48 |
| ❌ Fail | 26 |
| Total | 74 |

| ID | Description | Result |
|---|---|---|
| E.3 | Number that looks like a date | ❌ FAIL |
| E.2 | Mixed script company name | ❌ FAIL |
| E.1 | Short ambiguous string | ❌ FAIL |
| G.10 | Norwegian o-stroke | ✅ PASS |
| G.9 | Dutch van particle | ✅ PASS |
| G.8 | French accented name | ❌ FAIL |
| C.19 | French role manager | ✅ PASS |
| C.18 | Russian role general director | ✅ PASS |
| C.17 | Arabic role general manager | ✅ PASS |
| C.16 | Chinese status struck off | ✅ PASS |
| C.15 | Chinese status active | ✅ PASS |
| C.14 | French status dissolved | ✅ PASS |
| C.13 | Russian status active | ✅ PASS |
| D.7 | Nationality adjective in Arabic | ✅ PASS |
| D.6 | Country name in Korean | ✅ PASS |
| D.5 | Country name in Chinese | ✅ PASS |
| B.18 | Saudi Riyal | ❌ FAIL |
| B.17 | Euro European format | ❌ FAIL |
| B.16 | Japanese yen amount | ❌ FAIL |
| A.6 | LEI code | ✅ PASS |
| A.5 | Tax ID with country prefix | ❌ FAIL |
| A.4 | IBAN | ❌ FAIL |
| B.15 | Hebrew date spelled out | ❌ FAIL |
| B.14 | Hijri date day-first Arabic-Indic | ❌ FAIL |
| B.13 | Thai date with พ.ศ. label | ❌ FAIL |
| B.12 | Thai date day-first format | ✅ PASS |
| C.12 | Russian legal form at end of company name | ❌ FAIL |
| C.11 | German legal form at end of company name | ❌ FAIL |
| C.10 | Japanese legal form at end of company name | ❌ FAIL |
| F.10 | Korean full name | ✅ PASS |
| F.9 | Greek full name | ✅ PASS |
| F.8 | Chinese full name | ✅ PASS |
| F.7 | Russian full name with patronymic | ✅ PASS |
| F.6 | Japanese full name surname + given | ✅ PASS |
| I.1 | Arabic person name (unresolved) | ❌ FAIL |
| G.7 | Portuguese tilde | ✅ PASS |
| G.6 | Scandinavian Æ | ✅ PASS |
| G.5 | Polish ł | ❌ FAIL |
| G.4 | Turkish dotted I | ❌ FAIL |
| G.3 | Spanish ñ | ❌ FAIL |
| G.2 | German ß | ❌ FAIL |
| G.1 | German umlaut expansion | ❌ FAIL |
| F.5 | Chinese name | ✅ PASS |
| F.4 | Japanese surname | ✅ PASS |
| F.3 | Greek male name | ✅ PASS |
| F.2 | Russian male name | ✅ PASS |
| F.1 | Russian female name | ✅ PASS |
| D.4 | Country name in Greek | ✅ PASS |
| D.3 | Country name in Russian | ✅ PASS |
| D.2 | Country name in Japanese | ✅ PASS |
| D.1 | Country name in Arabic | ✅ PASS |
| C.9 | Greek legal form SA | ✅ PASS |
| C.8 | German status dissolved | ✅ PASS |
| C.7 | Japanese role representative director | ✅ PASS |
| C.6 | Japanese role director | ✅ PASS |
| C.5 | Arabic status dissolved | ✅ PASS |
| C.4 | Japanese status active | ✅ PASS |
| C.3 | Russian LLC | ✅ PASS |
| C.2 | German GmbH | ✅ PASS |
| C.1 | Japanese legal form KK | ✅ PASS |
| B.11 | Arabic-Indic digits | ✅ PASS |
| B.10 | Swiss apostrophe number format | ❌ FAIL |
| B.9 | European number format | ❌ FAIL |
| B.8 | Full-width parenthetical negative | ❌ FAIL |
| B.7 | Japanese triangle negative | ❌ FAIL |
| B.6 | Minguo (Taiwan ROC) date | ❌ FAIL |
| B.5 | Solar Hijri date | ✅ PASS |
| B.4 | Hijri date with Arabic-Indic digits | ✅ PASS |
| B.3 | Japanese Showa era date | ✅ PASS |
| B.2 | Japanese Reiwa era date | ✅ PASS |
| B.1 | Thai Buddhist Era date | ✅ PASS |
| A.3 | Email address | ✅ PASS |
| A.2 | Registration number | ✅ PASS |
| A.1 | Passport number | ✅ PASS |

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
| **field_type** | `passport_no` | `passport_no` | ✅ match |
| **language** | `en` | `en` | ✅ match |
| **confidence** | — | `0.92` | — |
| **latency** | — | `3.31s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "TK1234567", "field_type": "passport_no", "language": "en"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `PRESERVE` |
| normalised_form | `TK1234567` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `PRESERVE` | `PRESERVE` | ✅ PASS |
| **normalised_form** | `TK1234567` | `TK1234567` | ✅ PASS |

### Overall: ✅ PASS

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
| **field_type** | `registration_no` | `registration_no` | ✅ match |
| **language** | `en` | `de` | ⚠️ mismatch |
| **confidence** | — | `0.95` | — |
| **latency** | — | `2.24s` | — |

> ⚠️ **Classification mismatch on language.** GPT-4o-mini returned `de` but expected `en`. This may affect strategy selection (e.g. character map handler chosen for wrong language).

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "DE123456789", "field_type": "registration_no", "language": "de"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `PRESERVE` |
| normalised_form | `DE123456789` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `PRESERVE` | `PRESERVE` | ✅ PASS |
| **normalised_form** | `DE123456789` | `DE123456789` | ✅ PASS |

### Overall: ✅ PASS

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
| **field_type** | `email` | `email` | ✅ match |
| **language** | `en` | `en` | ✅ match |
| **confidence** | — | `0.99` | — |
| **latency** | — | `1.66s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "test.user@example.com", "field_type": "email", "language": "en"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `PRESERVE` |
| normalised_form | `test.user@example.com` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `PRESERVE` | `PRESERVE` | ✅ PASS |
| **normalised_form** | `test.user@example.com` | `test.user@example.com` | ✅ PASS |

### Overall: ✅ PASS

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
| **language** | `th` | `th` | ✅ match |
| **confidence** | — | `0.93` | — |
| **latency** | — | `1.17s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "2568/5/8", "field_type": "date_of_birth", "language": "th"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CALENDAR` |
| normalised_form | `2025-05-08` |
| confidence | `0.95` |
| review_required | `False` |
| latency | `0.02s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CALENDAR` | `CALENDAR` | ✅ PASS |
| **normalised_form** | `2025-05-08` | `2025-05-08` | ✅ PASS |

### Overall: ✅ PASS

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
| **confidence** | — | `0.95` | — |
| **latency** | — | `1.85s` | — |

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
| **confidence** | — | `0.95` | — |
| **latency** | — | `1.12s` | — |

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
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.93s` | — |

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
| latency | `0.01s` |

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
| **language** | `fa` | `fa` | ✅ match |
| **confidence** | — | `0.91` | — |
| **latency** | — | `1.44s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "1404/2/15", "field_type": "date_of_birth", "language": "fa"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CALENDAR` |
| normalised_form | `2025-05-05` |
| confidence | `0.95` |
| review_required | `False` |
| latency | `0.02s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CALENDAR` | `CALENDAR` | ✅ PASS |
| **normalised_form** | `2025-05-05` | `2025-05-05` | ✅ PASS |

### Overall: ✅ PASS

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
| **field_type** | `date_of_birth` | `date_of_birth` | ✅ match |
| **language** | `zh` | `zh` | ✅ match |
| **confidence** | — | `0.88` | — |
| **latency** | — | `1.22s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "114/5/8", "field_type": "date_of_birth", "language": "zh"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CALENDAR` |
| normalised_form | `114/5/8` |
| confidence | `0.95` |
| review_required | `True` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CALENDAR` | `CALENDAR` | ✅ PASS |
| **normalised_form** | `2025-05-08` | `114/5/8` | ❌ FAIL |

> ❌ **Form failure diagnosis:** Calendar conversion produced '114/5/8' instead of '2025-05-08'. Check the epoch calculation in the relevant calendar module.

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
| **field_type** | `total_assets` | `total_assets` | ✅ match |
| **language** | `ja` | `ja` | ✅ match |
| **confidence** | — | `0.94` | — |
| **latency** | — | `1.42s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "△4,191", "field_type": "total_assets", "language": "ja"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `PRESERVE` |
| normalised_form | `△4,191` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `NUMERIC` | `PRESERVE` | ❌ FAIL |
| **normalised_form** | `-4191` | `△4,191` | ❌ FAIL |

> ❌ **Method failure diagnosis:** Field type 'total_assets' is in the PRESERVE_FIELDS list but should not be. Check PRESERVE_FIELDS in router.py or preserve.py.

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
| **field_type** | `total_assets` | `net_assets` | ⚠️ mismatch |
| **language** | `ja` | `ja` | ✅ match |
| **confidence** | — | `0.94` | — |
| **latency** | — | `1.88s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `net_assets` but expected `total_assets`. The router will process the field as `net_assets` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "（4,191）", "field_type": "net_assets", "language": "ja"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `PRESERVE` |
| normalised_form | `（4,191）` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `NUMERIC` | `PRESERVE` | ❌ FAIL |
| **normalised_form** | `-4191` | `（4,191）` | ❌ FAIL |

> ❌ **Method failure diagnosis:** Field type 'net_assets' is in the PRESERVE_FIELDS list but should not be. Check PRESERVE_FIELDS in router.py or preserve.py.

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
| **field_type** | `total_assets` | `total_assets` | ✅ match |
| **language** | `de` | `de` | ✅ match |
| **confidence** | — | `0.91` | — |
| **latency** | — | `1.34s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "1.234.567,89", "field_type": "total_assets", "language": "de"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `PRESERVE` |
| normalised_form | `1.234.567,89` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `NUMERIC` | `PRESERVE` | ❌ FAIL |
| **normalised_form** | `1234567.89` | `1.234.567,89` | ❌ FAIL |

> ❌ **Method failure diagnosis:** Field type 'total_assets' is in the PRESERVE_FIELDS list but should not be. Check PRESERVE_FIELDS in router.py or preserve.py.

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
| **field_type** | `total_assets` | `total_assets` | ✅ match |
| **language** | `fr` | `en` | ⚠️ mismatch |
| **confidence** | — | `0.95` | — |
| **latency** | — | `1.18s` | — |

> ⚠️ **Classification mismatch on language.** GPT-4o-mini returned `en` but expected `fr`. This may affect strategy selection (e.g. character map handler chosen for wrong language).

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "1'234'567.89", "field_type": "total_assets", "language": "en"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `PRESERVE` |
| normalised_form | `1'234'567.89` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `NUMERIC` | `PRESERVE` | ❌ FAIL |
| **normalised_form** | `1234567.89` | `1'234'567.89` | ❌ FAIL |

> ❌ **Method failure diagnosis:** Field type 'total_assets' is in the PRESERVE_FIELDS list but should not be. Check PRESERVE_FIELDS in router.py or preserve.py.

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
| **field_type** | `id_no` | `id_no` | ✅ match |
| **language** | `ar` | `ar` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `2.10s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "٠١٢٣٤٥٦٧٨٩", "field_type": "id_no", "language": "ar"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `PRESERVE` |
| normalised_form | `٠١٢٣٤٥٦٧٨٩` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `PRESERVE` | `PRESERVE` | ✅ PASS |
| **normalised_form** | `٠١٢٣٤٥٦٧٨٩` | `٠١٢٣٤٥٦٧٨٩` | ✅ PASS |

### Overall: ✅ PASS

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
| **confidence** | — | `0.95` | — |
| **latency** | — | `2.43s` | — |

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
| latency | `0.00s` |

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
| **confidence** | — | `0.95` | — |
| **latency** | — | `2.50s` | — |

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
| **confidence** | — | `0.95` | — |
| **latency** | — | `1.14s` | — |

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
| **field_type** | `status` | `status` | ✅ match |
| **language** | `ja` | `ja` | ✅ match |
| **confidence** | — | `0.92` | — |
| **latency** | — | `0.87s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "現役", "field_type": "status", "language": "ja"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `VOCABULARY` |
| normalised_form | `ACTIVE` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `VOCABULARY` | `VOCABULARY` | ✅ PASS |
| **normalised_form** | `ACTIVE` | `ACTIVE` | ✅ PASS |

### Overall: ✅ PASS

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
| **field_type** | `status` | `status` | ✅ match |
| **language** | `ar` | `ar` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `1.45s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "منتهي", "field_type": "status", "language": "ar"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `VOCABULARY` |
| normalised_form | `DISSOLVED` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `VOCABULARY` | `VOCABULARY` | ✅ PASS |
| **normalised_form** | `DISSOLVED` | `DISSOLVED` | ✅ PASS |

### Overall: ✅ PASS

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
| **confidence** | — | `0.92` | — |
| **latency** | — | `0.89s` | — |

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
| latency | `0.00s` |

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
| **confidence** | — | `0.92` | — |
| **latency** | — | `1.00s` | — |

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
| latency | `0.00s` |

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
| **field_type** | `status` | `status` | ✅ match |
| **language** | `de` | `de` | ✅ match |
| **confidence** | — | `0.85` | — |
| **latency** | — | `0.93s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "aufgelöst", "field_type": "status", "language": "de"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `VOCABULARY` |
| normalised_form | `DISSOLVED` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `VOCABULARY` | `VOCABULARY` | ✅ PASS |
| **normalised_form** | `DISSOLVED` | `DISSOLVED` | ✅ PASS |

### Overall: ✅ PASS

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
| **confidence** | — | `0.95` | — |
| **latency** | — | `1.01s` | — |

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
| **confidence** | — | `0.92` | — |
| **latency** | — | `1.64s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "ألمانيا", "field_type": "nationality", "language": "ar"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `GEOGRAPHIC` |
| normalised_form | `GERMANY` |
| confidence | `0.88` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `GEOGRAPHIC` | `GEOGRAPHIC` | ✅ PASS |
| **normalised_form** | `GERMANY` | `GERMANY` | ✅ PASS |

### Overall: ✅ PASS

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
| **confidence** | — | `0.95` | — |
| **latency** | — | `1.15s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "日本", "field_type": "nationality", "language": "ja"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `GEOGRAPHIC` |
| normalised_form | `JAPAN` |
| confidence | `0.88` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `GEOGRAPHIC` | `GEOGRAPHIC` | ✅ PASS |
| **normalised_form** | `JAPAN` | `JAPAN` | ✅ PASS |

### Overall: ✅ PASS

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
| **language** | `ru` | `ru` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `1.14s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Германия", "field_type": "nationality", "language": "ru"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `GEOGRAPHIC` |
| normalised_form | `GERMANY` |
| confidence | `0.88` |
| review_required | `False` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `GEOGRAPHIC` | `GEOGRAPHIC` | ✅ PASS |
| **normalised_form** | `GERMANY` | `GERMANY` | ✅ PASS |

### Overall: ✅ PASS

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
| **confidence** | — | `0.92` | — |
| **latency** | — | `1.03s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Γερμανία", "field_type": "nationality", "language": "el"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `GEOGRAPHIC` |
| normalised_form | `GERMANY` |
| confidence | `0.88` |
| review_required | `False` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `GEOGRAPHIC` | `GEOGRAPHIC` | ✅ PASS |
| **normalised_form** | `GERMANY` | `GERMANY` | ✅ PASS |

### Overall: ✅ PASS

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
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.89s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Наталья", "field_type": "person_name", "language": "ru"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `TRANSLITERATE` |
| normalised_form | `NATALYA` |
| confidence | `0.90` |
| review_required | `False` |
| latency | `0.02s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `TRANSLITERATION` or `TRANSLITERATE` | `TRANSLITERATE` | ✅ PASS |
| **normalised_form** | `NATALYA` | `NATALYA` | ✅ PASS |

### Overall: ✅ PASS

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
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.90s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Александр", "field_type": "person_name", "language": "ru"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `TRANSLITERATE` |
| normalised_form | `ALEKSANDR` |
| confidence | `0.90` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `TRANSLITERATION` or `TRANSLITERATE` | `TRANSLITERATE` | ✅ PASS |
| **normalised_form** | `ALEKSANDR` | `ALEKSANDR` | ✅ PASS |

### Overall: ✅ PASS

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
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.86s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Νίκος", "field_type": "person_name", "language": "el"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `TRANSLITERATE` |
| normalised_form | `NIKOS` |
| confidence | `0.90` |
| review_required | `False` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `TRANSLITERATION` or `TRANSLITERATE` | `TRANSLITERATE` | ✅ PASS |
| **normalised_form** | `NIKOS` | `NIKOS` | ✅ PASS |

### Overall: ✅ PASS

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
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.85s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "田中", "field_type": "person_name", "language": "ja"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `TRANSLITERATE` |
| normalised_form | `TANAKA` |
| confidence | `0.70` |
| review_required | `True` |
| latency | `0.18s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `TRANSLITERATION` or `TRANSLITERATE` | `TRANSLITERATE` | ✅ PASS |
| **normalised_form** | `TANAKA` | `TANAKA` | ✅ PASS |

### Overall: ✅ PASS

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
| **latency** | — | `1.28s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "王小明", "field_type": "person_name", "language": "zh"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `TRANSLITERATE` |
| normalised_form | `WANG XIAOMING` |
| confidence | `0.70` |
| review_required | `True` |
| latency | `0.12s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `TRANSLITERATION` or `TRANSLITERATE` | `TRANSLITERATE` | ✅ PASS |
| **normalised_form** | `WANG XIAOMING` | `WANG XIAOMING` | ✅ PASS |

### Overall: ✅ PASS

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
| **confidence** | — | `0.92` | — |
| **latency** | — | `0.92s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Müller", "field_type": "person_name", "language": "de"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `TRANSLITERATE` |
| normalised_form | `MUELLER` |
| confidence | `0.90` |
| review_required | `False` |
| allowed_variants | `MULLER` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CHARACTER_MAP` | `TRANSLITERATE` | ❌ FAIL |
| **normalised_form** | `MUELLER` | `MUELLER` | ✅ PASS |

> ❌ **Method failure diagnosis:** Expected CHARACTER_MAP but got TRANSLITERATE. Check that character_map_normaliser.py is wired in _try_strategy_g() and that language 'de' is in LANGUAGE_CHAR_MAPS.

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
| **confidence** | — | `0.85` | — |
| **latency** | — | `0.97s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `address` but expected `person_name`. The router will process the field as `address` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Straße", "field_type": "address", "language": "de"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `GEOGRAPHIC` |
| normalised_form | `SAO TOME AND PRINCIPE` |
| confidence | `0.75` |
| review_required | `True` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CHARACTER_MAP` | `GEOGRAPHIC` | ❌ FAIL |
| **normalised_form** | `STRASSE` | `SAO TOME AND PRINCIPE` | ❌ FAIL |

> ❌ **Method failure diagnosis:** Expected CHARACTER_MAP but got GEOGRAPHIC. Check that character_map_normaliser.py is wired in _try_strategy_g() and that language 'de' is in LANGUAGE_CHAR_MAPS.

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
| **field_type** | `person_name` | `family_name` | ⚠️ mismatch |
| **language** | `es` | `es` | ✅ match |
| **confidence** | — | `0.85` | — |
| **latency** | — | `2.13s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `family_name` but expected `person_name`. The router will process the field as `family_name` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Muñoz", "field_type": "family_name", "language": "es"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `TRANSLITERATE` |
| normalised_form | `MUNOZ` |
| confidence | `0.90` |
| review_required | `False` |
| allowed_variants | `MUNYOZ` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CHARACTER_MAP` | `TRANSLITERATE` | ❌ FAIL |
| **normalised_form** | `MUNOZ` | `MUNOZ` | ✅ PASS |

> ❌ **Method failure diagnosis:** Expected CHARACTER_MAP but got TRANSLITERATE. Check that character_map_normaliser.py is wired in _try_strategy_g() and that language 'es' is in LANGUAGE_CHAR_MAPS.

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
| **field_type** | `person_name` | `city` | ⚠️ mismatch |
| **language** | `tr` | `tr` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.95s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `city` but expected `person_name`. The router will process the field as `city` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "İstanbul", "field_type": "city", "language": "tr"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `GEOGRAPHIC` |
| normalised_form | `ISTANBUL` |
| confidence | `0.92` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CHARACTER_MAP` | `GEOGRAPHIC` | ❌ FAIL |
| **normalised_form** | `ISTANBUL` | `ISTANBUL` | ✅ PASS |

> ❌ **Method failure diagnosis:** Expected CHARACTER_MAP but got GEOGRAPHIC. Check that character_map_normaliser.py is wired in _try_strategy_g() and that language 'tr' is in LANGUAGE_CHAR_MAPS.

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
| **field_type** | `person_name` | `city` | ⚠️ mismatch |
| **language** | `pl` | `pl` | ✅ match |
| **confidence** | — | `0.85` | — |
| **latency** | — | `1.33s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `city` but expected `person_name`. The router will process the field as `city` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Łódź", "field_type": "city", "language": "pl"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `GEOGRAPHIC` |
| normalised_form | `LODZ` |
| confidence | `0.92` |
| review_required | `False` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CHARACTER_MAP` | `GEOGRAPHIC` | ❌ FAIL |
| **normalised_form** | `LODZ` | `LODZ` | ✅ PASS |

> ❌ **Method failure diagnosis:** Expected CHARACTER_MAP but got GEOGRAPHIC. Check that character_map_normaliser.py is wired in _try_strategy_g() and that language 'pl' is in LANGUAGE_CHAR_MAPS.

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
| **field_type** | `person_name` | `company_name` | ⚠️ mismatch |
| **language** | `da` | `da` | ✅ match |
| **confidence** | — | `0.85` | — |
| **latency** | — | `0.84s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `company_name` but expected `person_name`. The router will process the field as `company_name` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Ærø", "field_type": "company_name", "language": "da"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CHARACTER_MAP` |
| normalised_form | `AERO` |
| confidence | `0.95` |
| review_required | `False` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CHARACTER_MAP` | `CHARACTER_MAP` | ✅ PASS |
| **normalised_form** | `AERO` | `AERO` | ✅ PASS |

### Overall: ✅ PASS

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
| **field_type** | `person_name` | `given_name` | ⚠️ mismatch |
| **language** | `pt` | `pt` | ✅ match |
| **confidence** | — | `0.85` | — |
| **latency** | — | `1.00s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `given_name` but expected `person_name`. The router will process the field as `given_name` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "João", "field_type": "given_name", "language": "pt"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CHARACTER_MAP` |
| normalised_form | `JOAO` |
| confidence | `0.95` |
| review_required | `False` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CHARACTER_MAP` | `CHARACTER_MAP` | ✅ PASS |
| **normalised_form** | `JOAO` | `JOAO` | ✅ PASS |

### Overall: ✅ PASS

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
| **latency** | — | `1.31s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "محمد عبد الله", "field_type": "person_name", "language": "ar"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `TRANSLITERATE` |
| normalised_form | `MHMD ABDULLAH` |
| confidence | `0.70` |
| review_required | `True` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `UNRESOLVED` | `TRANSLITERATE` | ❌ FAIL |
| **normalised_form** | `None` | `MHMD ABDULLAH` | ❌ FAIL |

> ❌ **Method failure diagnosis:** Got 'TRANSLITERATE', expected one of ['UNRESOLVED']. Check router.py strategy wiring.

### Overall: ❌ FAIL

---

## F.6 — Japanese full name surname + given

| | |
|---|---|
| **Input** | `田中 太郎` |
| **Expected field type** | `person_name` |
| **Expected language** | `ja` |
| **Expected normalised form** | `TANAKA TARO` |
| **Expected method** | `['TRANSLITERATION', 'TRANSLITERATE']` |
| **Notes** | Compound Japanese name — expected to fail until Epic 06 wired |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `person_name` | ✅ match |
| **language** | `ja` | `ja` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.85s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "田中 太郎", "field_type": "person_name", "language": "ja"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `TRANSLITERATE` |
| normalised_form | `TANAKA TARO` |
| confidence | `0.70` |
| review_required | `True` |
| allowed_variants | `TANAKA TAROU` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `TRANSLITERATION` or `TRANSLITERATE` | `TRANSLITERATE` | ✅ PASS |
| **normalised_form** | `TANAKA TARO` | `TANAKA TARO` | ✅ PASS |

### Overall: ✅ PASS

---

## F.7 — Russian full name with patronymic

| | |
|---|---|
| **Input** | `Иванова Наталья Александровна` |
| **Expected field type** | `person_name` |
| **Expected language** | `ru` |
| **Expected normalised form** | `IVANOVA NATALYA ALEKSANDROVNA` |
| **Expected method** | `['TRANSLITERATION', 'TRANSLITERATE']` |
| **Notes** | Russian three-part name — expected to fail until Epic 06 wired |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `full_name` | ⚠️ mismatch |
| **language** | `ru` | `ru` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.93s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `full_name` but expected `person_name`. The router will process the field as `full_name` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Иванова Наталья Александровна", "field_type": "full_name", "language": "ru"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `TRANSLITERATE` |
| normalised_form | `IVANOVA NATALYA ALEKSANDROVNA` |
| confidence | `0.90` |
| review_required | `False` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `TRANSLITERATION` or `TRANSLITERATE` | `TRANSLITERATE` | ✅ PASS |
| **normalised_form** | `IVANOVA NATALYA ALEKSANDROVNA` | `IVANOVA NATALYA ALEKSANDROVNA` | ✅ PASS |

### Overall: ✅ PASS

---

## F.8 — Chinese full name

| | |
|---|---|
| **Input** | `王小明` |
| **Expected field type** | `person_name` |
| **Expected language** | `zh` |
| **Expected normalised form** | `WANG XIAOMING` |
| **Expected method** | `['TRANSLITERATION', 'TRANSLITERATE']` |
| **Notes** | Already in suite but keeping for reference |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `person_name` | ✅ match |
| **language** | `zh` | `zh` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `1.21s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "王小明", "field_type": "person_name", "language": "zh"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `TRANSLITERATE` |
| normalised_form | `WANG XIAOMING` |
| confidence | `0.70` |
| review_required | `True` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `TRANSLITERATION` or `TRANSLITERATE` | `TRANSLITERATE` | ✅ PASS |
| **normalised_form** | `WANG XIAOMING` | `WANG XIAOMING` | ✅ PASS |

### Overall: ✅ PASS

---

## F.9 — Greek full name

| | |
|---|---|
| **Input** | `Νίκος Παπαδόπουλος` |
| **Expected field type** | `person_name` |
| **Expected language** | `el` |
| **Expected normalised form** | `NIKOS PAPADOPOULOS` |
| **Expected method** | `['TRANSLITERATION', 'TRANSLITERATE']` |
| **Notes** | Compound Greek name — expected to fail until Epic 06 wired |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `person_name` | ✅ match |
| **language** | `el` | `el` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `1.21s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Νίκος Παπαδόπουλος", "field_type": "person_name", "language": "el"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `TRANSLITERATE` |
| normalised_form | `NIKOS PAPADOPOULOS` |
| confidence | `0.90` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `TRANSLITERATION` or `TRANSLITERATE` | `TRANSLITERATE` | ✅ PASS |
| **normalised_form** | `NIKOS PAPADOPOULOS` | `NIKOS PAPADOPOULOS` | ✅ PASS |

### Overall: ✅ PASS

---

## F.10 — Korean full name

| | |
|---|---|
| **Input** | `이민준` |
| **Expected field type** | `person_name` |
| **Expected language** | `ko` |
| **Expected normalised form** | `I MINJUN` |
| **Expected method** | `['TRANSLITERATION', 'TRANSLITERATE']` |
| **Notes** | Korean name romanisation |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `person_name` | ✅ match |
| **language** | `ko` | `ko` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.86s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "이민준", "field_type": "person_name", "language": "ko"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `TRANSLITERATE` |
| normalised_form | `I MINJUN` |
| confidence | `0.70` |
| review_required | `True` |
| allowed_variants | `LEE MINJUN`, `MINJUN I`, `MINJUN LEE`, `MINJUN RHEE`, `MINJUN RHIE`, `MINJUN RI`, `MINJUN YI`, `RHEE MINJUN`, `RHIE MINJUN`, `RI MINJUN`, `YI MINJUN` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `TRANSLITERATION` or `TRANSLITERATE` | `TRANSLITERATE` | ✅ PASS |
| **normalised_form** | `I MINJUN` | `I MINJUN` | ✅ PASS |

### Overall: ✅ PASS

---

## C.10 — Japanese legal form at end of company name

| | |
|---|---|
| **Input** | `三菱商事株式会社` |
| **Expected field type** | `company_name` |
| **Expected language** | `ja` |
| **Expected normalised form** | `KK` |
| **Expected method** | `VOCABULARY` |
| **Notes** | Suffix 株式会社 must be extracted from full company name string |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `company_name` | `company_name` | ✅ match |
| **language** | `ja` | `ja` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `1.17s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "三菱商事株式会社", "field_type": "company_name", "language": "ja"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `TRANSLITERATE` |
| normalised_form | `MITSUBISHISHOUJI KABUSHIKIGAISHA` |
| confidence | `0.70` |
| review_required | `True` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `VOCABULARY` | `TRANSLITERATE` | ❌ FAIL |
| **normalised_form** | `KK` | `MITSUBISHISHOUJI KABUSHIKIGAISHA` | ❌ FAIL |

> ❌ **Method failure diagnosis:** Expected VOCABULARY lookup but got TRANSLITERATE. Check that the lookup table for field_type='company_name' language='ja' exists in data/lookup_tables/ and that VocabularyLookupService is correctly wired in _try_strategy_c().

### Overall: ❌ FAIL

---

## C.11 — German legal form at end of company name

| | |
|---|---|
| **Input** | `Müller & Söhne GmbH` |
| **Expected field type** | `company_name` |
| **Expected language** | `de` |
| **Expected normalised form** | `GMBH` |
| **Expected method** | `VOCABULARY` |
| **Notes** | Suffix GmbH must be extracted from full string |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `company_name` | `company_name` | ✅ match |
| **language** | `de` | `de` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.85s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Müller & Söhne GmbH", "field_type": "company_name", "language": "de"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `TRANSLITERATE` |
| normalised_form | `MUELLER & SOEHNE GMBH` |
| confidence | `0.90` |
| review_required | `False` |
| allowed_variants | `MULLER & SOHNE GMBH` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `VOCABULARY` | `TRANSLITERATE` | ❌ FAIL |
| **normalised_form** | `GMBH` | `MUELLER & SOEHNE GMBH` | ❌ FAIL |

> ❌ **Method failure diagnosis:** Expected VOCABULARY lookup but got TRANSLITERATE. Check that the lookup table for field_type='company_name' language='de' exists in data/lookup_tables/ and that VocabularyLookupService is correctly wired in _try_strategy_c().

### Overall: ❌ FAIL

---

## C.12 — Russian legal form at end of company name

| | |
|---|---|
| **Input** | `Газпром ПАО` |
| **Expected field type** | `company_name` |
| **Expected language** | `ru` |
| **Expected normalised form** | `PJSC` |
| **Expected method** | `VOCABULARY` |
| **Notes** | ПАО = PJSC suffix extraction |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `company_name` | `company_name` | ✅ match |
| **language** | `ru` | `ru` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `1.05s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Газпром ПАО", "field_type": "company_name", "language": "ru"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `TRANSLITERATE` |
| normalised_form | `GAZPROM PAO` |
| confidence | `0.90` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `VOCABULARY` | `TRANSLITERATE` | ❌ FAIL |
| **normalised_form** | `PJSC` | `GAZPROM PAO` | ❌ FAIL |

> ❌ **Method failure diagnosis:** Expected VOCABULARY lookup but got TRANSLITERATE. Check that the lookup table for field_type='company_name' language='ru' exists in data/lookup_tables/ and that VocabularyLookupService is correctly wired in _try_strategy_c().

### Overall: ❌ FAIL

---

## B.12 — Thai date day-first format

| | |
|---|---|
| **Input** | `08/05/2568` |
| **Expected field type** | `date_of_birth` |
| **Expected language** | `th` |
| **Expected normalised form** | `2025-05-08` |
| **Expected method** | `CALENDAR` |
| **Notes** | Day-first Thai Buddhist date — common on Thai IDs |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `date_of_birth` | `date_of_birth` | ✅ match |
| **language** | `th` | `th` | ✅ match |
| **confidence** | — | `0.93` | — |
| **latency** | — | `0.92s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "08/05/2568", "field_type": "date_of_birth", "language": "th"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CALENDAR` |
| normalised_form | `2025-05-08` |
| confidence | `0.95` |
| review_required | `False` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CALENDAR` | `CALENDAR` | ✅ PASS |
| **normalised_form** | `2025-05-08` | `2025-05-08` | ✅ PASS |

### Overall: ✅ PASS

---

## B.13 — Thai date with พ.ศ. label

| | |
|---|---|
| **Input** | `พ.ศ. 2568` |
| **Expected field type** | `issue_date` |
| **Expected language** | `th` |
| **Expected normalised form** | `2025` |
| **Expected method** | `CALENDAR` |
| **Notes** | Year-only Thai date with era label |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `issue_date` | `date_of_birth` | ⚠️ mismatch |
| **language** | `th` | `th` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.93s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `date_of_birth` but expected `issue_date`. The router will process the field as `date_of_birth` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "พ.ศ. 2568", "field_type": "date_of_birth", "language": "th"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CALENDAR` |
| normalised_form | `พ.ศ. 2568` |
| confidence | `0.95` |
| review_required | `True` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CALENDAR` | `CALENDAR` | ✅ PASS |
| **normalised_form** | `2025` | `พ.ศ. 2568` | ❌ FAIL |

> ❌ **Form failure diagnosis:** Calendar conversion produced 'พ.ศ. 2568' instead of '2025'. Check the epoch calculation in the relevant calendar module.

### Overall: ❌ FAIL

---

## B.14 — Hijri date day-first Arabic-Indic

| | |
|---|---|
| **Input** | `١٤/٠٣/١٤٤٥` |
| **Expected field type** | `date_of_birth` |
| **Expected language** | `ar` |
| **Expected normalised form** | `2023-09-29` |
| **Expected method** | `CALENDAR` |
| **Notes** | Day-first Hijri date format common on Gulf documents |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `date_of_birth` | `date_of_birth` | ✅ match |
| **language** | `ar` | `ar` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `1.01s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "١٤/٠٣/١٤٤٥", "field_type": "date_of_birth", "language": "ar"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CALENDAR` |
| normalised_form | `14/03/1445` |
| confidence | `0.95` |
| review_required | `True` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CALENDAR` | `CALENDAR` | ✅ PASS |
| **normalised_form** | `2023-09-29` | `14/03/1445` | ❌ FAIL |

> ❌ **Form failure diagnosis:** Calendar conversion produced '14/03/1445' instead of '2023-09-29'. Check the epoch calculation in the relevant calendar module.

### Overall: ❌ FAIL

---

## B.15 — Hebrew date spelled out

| | |
|---|---|
| **Input** | `15 תשרי 5786` |
| **Expected field type** | `date_of_birth` |
| **Expected language** | `he` |
| **Expected normalised form** | `2025-10-17` |
| **Expected method** | `CALENDAR` |
| **Notes** | Hebrew date with month name spelled out |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `date_of_birth` | `date_of_birth` | ✅ match |
| **language** | `he` | `he` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.97s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "15 תשרי 5786", "field_type": "date_of_birth", "language": "he"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CALENDAR` |
| normalised_form | `2025-10-07` |
| confidence | `0.95` |
| review_required | `False` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CALENDAR` | `CALENDAR` | ✅ PASS |
| **normalised_form** | `2025-10-17` | `2025-10-07` | ❌ FAIL |

> ❌ **Form failure diagnosis:** Calendar conversion produced '2025-10-07' instead of '2025-10-17'. Check the epoch calculation in the relevant calendar module.

### Overall: ❌ FAIL

---

## A.4 — IBAN

| | |
|---|---|
| **Input** | `GB29 NWBK 6016 1331 9268 19` |
| **Expected field type** | `iban` |
| **Expected language** | `en` |
| **Expected normalised form** | `GB29 NWBK 6016 1331 9268 19` |
| **Expected method** | `PRESERVE` |
| **Notes** | IBAN must be preserved verbatim |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `iban` | `iban` | ✅ match |
| **language** | `en` | `en` | ✅ match |
| **confidence** | — | `0.99` | — |
| **latency** | — | `0.86s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "GB29 NWBK 6016 1331 9268 19", "field_type": "iban", "language": "en"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `TRANSLITERATE` |
| normalised_form | `GB29 NWBK 6016 1331 9268 19` |
| confidence | `0.90` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `PRESERVE` | `TRANSLITERATE` | ❌ FAIL |
| **normalised_form** | `GB29 NWBK 6016 1331 9268 19` | `GB29 NWBK 6016 1331 9268 19` | ✅ PASS |

> ❌ **Method failure diagnosis:** Got 'TRANSLITERATE', expected one of ['PRESERVE']. Check router.py strategy wiring.

### Overall: ❌ FAIL

---

## A.5 — Tax ID with country prefix

| | |
|---|---|
| **Input** | `DE811100090` |
| **Expected field type** | `tax_id` |
| **Expected language** | `de` |
| **Expected normalised form** | `DE811100090` |
| **Expected method** | `PRESERVE` |
| **Notes** | German VAT number preserved verbatim |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `tax_id` | `iban` | ⚠️ mismatch |
| **language** | `de` | `de` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.92s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `iban` but expected `tax_id`. The router will process the field as `iban` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "DE811100090", "field_type": "iban", "language": "de"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `TRANSLITERATE` |
| normalised_form | `DE811100090` |
| confidence | `0.90` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `PRESERVE` | `TRANSLITERATE` | ❌ FAIL |
| **normalised_form** | `DE811100090` | `DE811100090` | ✅ PASS |

> ❌ **Method failure diagnosis:** Got 'TRANSLITERATE', expected one of ['PRESERVE']. Check router.py strategy wiring.

### Overall: ❌ FAIL

---

## A.6 — LEI code

| | |
|---|---|
| **Input** | `529900T8BM49AURSDO55` |
| **Expected field type** | `lei_code` |
| **Expected language** | `en` |
| **Expected normalised form** | `529900T8BM49AURSDO55` |
| **Expected method** | `PRESERVE` |
| **Notes** | Legal Entity Identifier — 20 char alphanumeric |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `lei_code` | `passport_no` | ⚠️ mismatch |
| **language** | `en` | `en` | ✅ match |
| **confidence** | — | `0.92` | — |
| **latency** | — | `1.04s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `passport_no` but expected `lei_code`. The router will process the field as `passport_no` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "529900T8BM49AURSDO55", "field_type": "passport_no", "language": "en"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `PRESERVE` |
| normalised_form | `529900T8BM49AURSDO55` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `PRESERVE` | `PRESERVE` | ✅ PASS |
| **normalised_form** | `529900T8BM49AURSDO55` | `529900T8BM49AURSDO55` | ✅ PASS |

### Overall: ✅ PASS

---

## B.16 — Japanese yen amount

| | |
|---|---|
| **Input** | `¥1,234,567` |
| **Expected field type** | `share_capital` |
| **Expected language** | `ja` |
| **Expected normalised form** | `1234567` |
| **Expected method** | `NUMERIC` |
| **Notes** | JPY amount — currency extracted, number normalised |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `share_capital` | `share_capital` | ✅ match |
| **language** | `ja` | `en` | ⚠️ mismatch |
| **confidence** | — | `0.95` | — |
| **latency** | — | `1.84s` | — |

> ⚠️ **Classification mismatch on language.** GPT-4o-mini returned `en` but expected `ja`. This may affect strategy selection (e.g. character map handler chosen for wrong language).

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "¥1,234,567", "field_type": "share_capital", "language": "en"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `PRESERVE` |
| normalised_form | `¥1,234,567` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `NUMERIC` | `PRESERVE` | ❌ FAIL |
| **normalised_form** | `1234567` | `¥1,234,567` | ❌ FAIL |

> ❌ **Method failure diagnosis:** Field type 'share_capital' is in the PRESERVE_FIELDS list but should not be. Check PRESERVE_FIELDS in router.py or preserve.py.

### Overall: ❌ FAIL

---

## B.17 — Euro European format

| | |
|---|---|
| **Input** | `€2.500.000,00` |
| **Expected field type** | `share_capital` |
| **Expected language** | `de` |
| **Expected normalised form** | `2500000.00` |
| **Expected method** | `NUMERIC` |
| **Notes** | EUR amount in European format |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `share_capital` | `share_capital` | ✅ match |
| **language** | `de` | `de` | ✅ match |
| **confidence** | — | `0.91` | — |
| **latency** | — | `0.95s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "€2.500.000,00", "field_type": "share_capital", "language": "de"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `PRESERVE` |
| normalised_form | `€2.500.000,00` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `NUMERIC` | `PRESERVE` | ❌ FAIL |
| **normalised_form** | `2500000.00` | `€2.500.000,00` | ❌ FAIL |

> ❌ **Method failure diagnosis:** Field type 'share_capital' is in the PRESERVE_FIELDS list but should not be. Check PRESERVE_FIELDS in router.py or preserve.py.

### Overall: ❌ FAIL

---

## B.18 — Saudi Riyal

| | |
|---|---|
| **Input** | `﷼500,000` |
| **Expected field type** | `share_capital` |
| **Expected language** | `ar` |
| **Expected normalised form** | `500000` |
| **Expected method** | `NUMERIC` |
| **Notes** | SAR amount |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `share_capital` | `share_capital` | ✅ match |
| **language** | `ar` | `ar` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.83s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "﷼500,000", "field_type": "share_capital", "language": "ar"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `PRESERVE` |
| normalised_form | `﷼500,000` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `NUMERIC` | `PRESERVE` | ❌ FAIL |
| **normalised_form** | `500000` | `﷼500,000` | ❌ FAIL |

> ❌ **Method failure diagnosis:** Field type 'share_capital' is in the PRESERVE_FIELDS list but should not be. Check PRESERVE_FIELDS in router.py or preserve.py.

### Overall: ❌ FAIL

---

## D.5 — Country name in Chinese

| | |
|---|---|
| **Input** | `中国` |
| **Expected field type** | `nationality` |
| **Expected language** | `zh` |
| **Expected normalised form** | `CHINA` |
| **Expected method** | `GEOGRAPHIC` |
| **Notes** | China in Chinese |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `nationality` | `nationality` | ✅ match |
| **language** | `zh` | `zh` | ✅ match |
| **confidence** | — | `0.93` | — |
| **latency** | — | `0.84s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "中国", "field_type": "nationality", "language": "zh"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `GEOGRAPHIC` |
| normalised_form | `CHINA` |
| confidence | `0.88` |
| review_required | `False` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `GEOGRAPHIC` | `GEOGRAPHIC` | ✅ PASS |
| **normalised_form** | `CHINA` | `CHINA` | ✅ PASS |

### Overall: ✅ PASS

---

## D.6 — Country name in Korean

| | |
|---|---|
| **Input** | `미국` |
| **Expected field type** | `nationality` |
| **Expected language** | `ko` |
| **Expected normalised form** | `UNITED STATES` |
| **Expected method** | `GEOGRAPHIC` |
| **Notes** | USA in Korean |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `nationality` | `nationality` | ✅ match |
| **language** | `ko` | `ko` | ✅ match |
| **confidence** | — | `0.92` | — |
| **latency** | — | `3.86s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "미국", "field_type": "nationality", "language": "ko"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `GEOGRAPHIC` |
| normalised_form | `UNITED STATES` |
| confidence | `0.88` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `GEOGRAPHIC` | `GEOGRAPHIC` | ✅ PASS |
| **normalised_form** | `UNITED STATES` | `UNITED STATES` | ✅ PASS |

### Overall: ✅ PASS

---

## D.7 — Nationality adjective in Arabic

| | |
|---|---|
| **Input** | `سعودي` |
| **Expected field type** | `nationality` |
| **Expected language** | `ar` |
| **Expected normalised form** | `SAUDI ARABIA` |
| **Expected method** | `GEOGRAPHIC` |
| **Notes** | Saudi nationality adjective — resolves to country name, not adjectival form |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `nationality` | `nationality` | ✅ match |
| **language** | `ar` | `ar` | ✅ match |
| **confidence** | — | `0.91` | — |
| **latency** | — | `1.41s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "سعودي", "field_type": "nationality", "language": "ar"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `GEOGRAPHIC` |
| normalised_form | `SAUDI ARABIA` |
| confidence | `0.88` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `GEOGRAPHIC` | `GEOGRAPHIC` | ✅ PASS |
| **normalised_form** | `SAUDI ARABIA` | `SAUDI ARABIA` | ✅ PASS |

### Overall: ✅ PASS

---

## C.13 — Russian status active

| | |
|---|---|
| **Input** | `действующая` |
| **Expected field type** | `status` |
| **Expected language** | `ru` |
| **Expected normalised form** | `ACTIVE` |
| **Expected method** | `VOCABULARY` |
| **Notes** | Russian feminine active status |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `status` | `status` | ✅ match |
| **language** | `ru` | `ru` | ✅ match |
| **confidence** | — | `0.92` | — |
| **latency** | — | `1.00s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "действующая", "field_type": "status", "language": "ru"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `VOCABULARY` |
| normalised_form | `ACTIVE` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `VOCABULARY` | `VOCABULARY` | ✅ PASS |
| **normalised_form** | `ACTIVE` | `ACTIVE` | ✅ PASS |

### Overall: ✅ PASS

---

## C.14 — French status dissolved

| | |
|---|---|
| **Input** | `dissoute` |
| **Expected field type** | `status` |
| **Expected language** | `fr` |
| **Expected normalised form** | `DISSOLVED` |
| **Expected method** | `VOCABULARY` |
| **Notes** | French feminine dissolved status |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `status` | `status` | ✅ match |
| **language** | `fr` | `fr` | ✅ match |
| **confidence** | — | `0.85` | — |
| **latency** | — | `0.83s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "dissoute", "field_type": "status", "language": "fr"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `VOCABULARY` |
| normalised_form | `DISSOLVED` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `VOCABULARY` | `VOCABULARY` | ✅ PASS |
| **normalised_form** | `DISSOLVED` | `DISSOLVED` | ✅ PASS |

### Overall: ✅ PASS

---

## C.15 — Chinese status active

| | |
|---|---|
| **Input** | `存续` |
| **Expected field type** | `status` |
| **Expected language** | `zh` |
| **Expected normalised form** | `ACTIVE` |
| **Expected method** | `VOCABULARY` |
| **Notes** | Chinese active/ongoing status — appears on SAMR extracts |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `status` | `status` | ✅ match |
| **language** | `zh` | `zh` | ✅ match |
| **confidence** | — | `0.91` | — |
| **latency** | — | `1.61s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "存续", "field_type": "status", "language": "zh"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `VOCABULARY` |
| normalised_form | `ACTIVE` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `VOCABULARY` | `VOCABULARY` | ✅ PASS |
| **normalised_form** | `ACTIVE` | `ACTIVE` | ✅ PASS |

### Overall: ✅ PASS

---

## C.16 — Chinese status struck off

| | |
|---|---|
| **Input** | `吊销` |
| **Expected field type** | `status` |
| **Expected language** | `zh` |
| **Expected normalised form** | `STRUCK_OFF` |
| **Expected method** | `VOCABULARY` |
| **Notes** | Chinese administrative revocation — distinct from voluntary dissolution |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `status` | `status` | ✅ match |
| **language** | `zh` | `zh` | ✅ match |
| **confidence** | — | `0.85` | — |
| **latency** | — | `0.66s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "吊销", "field_type": "status", "language": "zh"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `VOCABULARY` |
| normalised_form | `STRUCK_OFF` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `VOCABULARY` | `VOCABULARY` | ✅ PASS |
| **normalised_form** | `STRUCK_OFF` | `STRUCK_OFF` | ✅ PASS |

### Overall: ✅ PASS

---

## C.17 — Arabic role general manager

| | |
|---|---|
| **Input** | `مدير عام` |
| **Expected field type** | `role` |
| **Expected language** | `ar` |
| **Expected normalised form** | `GENERAL MANAGER` |
| **Expected method** | `VOCABULARY` |
| **Notes** | Common Gulf company role |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `role` | `role` | ✅ match |
| **language** | `ar` | `ar` | ✅ match |
| **confidence** | — | `0.92` | — |
| **latency** | — | `0.80s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "مدير عام", "field_type": "role", "language": "ar"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `VOCABULARY` |
| normalised_form | `GENERAL MANAGER` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `VOCABULARY` | `VOCABULARY` | ✅ PASS |
| **normalised_form** | `GENERAL MANAGER` | `GENERAL MANAGER` | ✅ PASS |

### Overall: ✅ PASS

---

## C.18 — Russian role general director

| | |
|---|---|
| **Input** | `Генеральный директор` |
| **Expected field type** | `role` |
| **Expected language** | `ru` |
| **Expected normalised form** | `GENERAL DIRECTOR` |
| **Expected method** | `VOCABULARY` |
| **Notes** | Standard Russian company role on registry extracts |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `role` | `role` | ✅ match |
| **language** | `ru` | `ru` | ✅ match |
| **confidence** | — | `0.92` | — |
| **latency** | — | `0.90s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Генеральный директор", "field_type": "role", "language": "ru"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `VOCABULARY` |
| normalised_form | `GENERAL DIRECTOR` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `VOCABULARY` | `VOCABULARY` | ✅ PASS |
| **normalised_form** | `GENERAL DIRECTOR` | `GENERAL DIRECTOR` | ✅ PASS |

### Overall: ✅ PASS

---

## C.19 — French role manager

| | |
|---|---|
| **Input** | `Gérant` |
| **Expected field type** | `role` |
| **Expected language** | `fr` |
| **Expected normalised form** | `MANAGER` |
| **Expected method** | `VOCABULARY` |
| **Notes** | French SARL manager role |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `role` | `role` | ✅ match |
| **language** | `fr` | `fr` | ✅ match |
| **confidence** | — | `0.92` | — |
| **latency** | — | `2.73s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Gérant", "field_type": "role", "language": "fr"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `VOCABULARY` |
| normalised_form | `MANAGER` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `VOCABULARY` | `VOCABULARY` | ✅ PASS |
| **normalised_form** | `MANAGER` | `MANAGER` | ✅ PASS |

### Overall: ✅ PASS

---

## G.8 — French accented name

| | |
|---|---|
| **Input** | `Élodie Lefèvre` |
| **Expected field type** | `person_name` |
| **Expected language** | `fr` |
| **Expected normalised form** | `ELODIE LEFEVRE` |
| **Expected method** | `CHARACTER_MAP` |
| **Notes** | French accents stripped — expected to fail until Epic 07 |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `person_name` | ✅ match |
| **language** | `fr` | `fr` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.86s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Élodie Lefèvre", "field_type": "person_name", "language": "fr"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `TRANSLITERATE` |
| normalised_form | `ELODIE LEFEVRE` |
| confidence | `0.90` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CHARACTER_MAP` | `TRANSLITERATE` | ❌ FAIL |
| **normalised_form** | `ELODIE LEFEVRE` | `ELODIE LEFEVRE` | ✅ PASS |

> ❌ **Method failure diagnosis:** Expected CHARACTER_MAP but got TRANSLITERATE. Check that character_map_normaliser.py is wired in _try_strategy_g() and that language 'fr' is in LANGUAGE_CHAR_MAPS.

### Overall: ❌ FAIL

---

## G.9 — Dutch van particle

| | |
|---|---|
| **Input** | `van den Berg` |
| **Expected field type** | `person_name` |
| **Expected language** | `nl` |
| **Expected normalised form** | `VAN DEN BERG` |
| **Expected method** | `CHARACTER_MAP` |
| **Notes** | Dutch noble particle preserved — expected to fail until Epic 07 |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `person_name` | ✅ match |
| **language** | `nl` | `nl` | ✅ match |
| **confidence** | — | `0.85` | — |
| **latency** | — | `0.95s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "van den Berg", "field_type": "person_name", "language": "nl"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CHARACTER_MAP` |
| normalised_form | `VAN DEN BERG` |
| confidence | `0.95` |
| review_required | `False` |
| allowed_variants | `Van DEN BERG`, `Van Den BERG` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CHARACTER_MAP` | `CHARACTER_MAP` | ✅ PASS |
| **normalised_form** | `VAN DEN BERG` | `VAN DEN BERG` | ✅ PASS |

### Overall: ✅ PASS

---

## G.10 — Norwegian o-stroke

| | |
|---|---|
| **Input** | `Bjørnstad` |
| **Expected field type** | `person_name` |
| **Expected language** | `no` |
| **Expected normalised form** | `BJORNSTAD` |
| **Expected method** | `CHARACTER_MAP` |
| **Notes** | ø→O — expected to fail until Epic 07 |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `person_name` | ✅ match |
| **language** | `no` | `no` | ✅ match |
| **confidence** | — | `0.91` | — |
| **latency** | — | `0.75s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Bjørnstad", "field_type": "person_name", "language": "no"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CHARACTER_MAP` |
| normalised_form | `BJORNSTAD` |
| confidence | `0.95` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CHARACTER_MAP` | `CHARACTER_MAP` | ✅ PASS |
| **normalised_form** | `BJORNSTAD` | `BJORNSTAD` | ✅ PASS |

### Overall: ✅ PASS

---

## E.1 — Short ambiguous string

| | |
|---|---|
| **Input** | `SA` |
| **Expected field type** | `legal_form` |
| **Expected language** | `fr` |
| **Expected normalised form** | `SA` |
| **Expected method** | `VOCABULARY` |
| **Notes** | SA is both a legal form and a country code — field type resolves the ambiguity |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `legal_form` | `registration_no` | ⚠️ mismatch |
| **language** | `fr` | `en` | ⚠️ mismatch |
| **confidence** | — | `0.85` | — |
| **latency** | — | `0.99s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `registration_no` but expected `legal_form`. The router will process the field as `registration_no` which may select the wrong strategy.

> ⚠️ **Classification mismatch on language.** GPT-4o-mini returned `en` but expected `fr`. This may affect strategy selection (e.g. character map handler chosen for wrong language).

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "SA", "field_type": "registration_no", "language": "en"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `PRESERVE` |
| normalised_form | `SA` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `VOCABULARY` | `PRESERVE` | ❌ FAIL |
| **normalised_form** | `SA` | `SA` | ✅ PASS |

> ❌ **Method failure diagnosis:** Field type 'registration_no' is in the PRESERVE_FIELDS list but should not be. Check PRESERVE_FIELDS in router.py or preserve.py.

### Overall: ❌ FAIL

---

## E.2 — Mixed script company name

| | |
|---|---|
| **Input** | `Sony株式会社` |
| **Expected field type** | `company_name` |
| **Expected language** | `ja` |
| **Expected normalised form** | `KK` |
| **Expected method** | `VOCABULARY` |
| **Notes** | Latin + kanji mixed — legal form suffix must be extracted |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `company_name` | `company_name` | ✅ match |
| **language** | `ja` | `ja` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.96s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Sony株式会社", "field_type": "company_name", "language": "ja"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `TRANSLITERATE` |
| normalised_form | `SONY KABUSHIKIGAISHA` |
| confidence | `0.70` |
| review_required | `True` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `VOCABULARY` | `TRANSLITERATE` | ❌ FAIL |
| **normalised_form** | `KK` | `SONY KABUSHIKIGAISHA` | ❌ FAIL |

> ❌ **Method failure diagnosis:** Expected VOCABULARY lookup but got TRANSLITERATE. Check that the lookup table for field_type='company_name' language='ja' exists in data/lookup_tables/ and that VocabularyLookupService is correctly wired in _try_strategy_c().

### Overall: ❌ FAIL

---

## E.3 — Number that looks like a date

| | |
|---|---|
| **Input** | `20250508` |
| **Expected field type** | `date_of_birth` |
| **Expected language** | `en` |
| **Expected normalised form** | `2025-05-08` |
| **Expected method** | `CALENDAR` |
| **Notes** | ISO 8601 compact format without separators |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `date_of_birth` | `date_of_birth` | ✅ match |
| **language** | `en` | `th` | ⚠️ mismatch |
| **confidence** | — | `0.90` | — |
| **latency** | — | `1.08s` | — |

> ⚠️ **Classification mismatch on language.** GPT-4o-mini returned `th` but expected `en`. This may affect strategy selection (e.g. character map handler chosen for wrong language).

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "20250508", "field_type": "date_of_birth", "language": "th"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CALENDAR` |
| normalised_form | `20250508` |
| confidence | `0.95` |
| review_required | `True` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CALENDAR` | `CALENDAR` | ✅ PASS |
| **normalised_form** | `2025-05-08` | `20250508` | ❌ FAIL |

> ❌ **Form failure diagnosis:** Calendar conversion produced '20250508' instead of '2025-05-08'. Check the epoch calculation in the relevant calendar module.

### Overall: ❌ FAIL

---
