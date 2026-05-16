# KYC Integration Diagnostic Report

**Run date:** 2026-05-14 23:50:29
**Examples:** 164
**Pipeline:** `detect_field_type()` → `process_field_row()` → `route_field()` → strategy
**Mocks:** None — all calls are real


## Summary

| Result | Count |
|---|---|
| ✅ Pass | 105 |
| ❌ Fail | 59 |
| Total | 164 |

| ID | Description | Result |
|---|---|---|
| E.16 | Cyrillic А and Latin O in reference | ✅ PASS |
| E.15 | Greek iota and omicron in alphanumeric reference | ❌ FAIL |
| E.14 | Han numeral with embedded Latin O | ❌ FAIL |
| E.13 | Mixed Latin letters and full-width digits | ❌ FAIL |
| E.12 | Arabic-Indic with embedded Latin O | ❌ FAIL |
| H.12 | Korean invoice prose | ❌ FAIL |
| H.11 | German invoice prose | ❌ FAIL |
| H.10 | Russian invoice prose | ❌ FAIL |
| H.9 | Traditional Chinese invoice prose | ❌ FAIL |
| H.8 | Japanese invoice prose with Kanji numerals | ❌ FAIL |
| H.7 | Arabic invoice prose with date and amount | ❌ FAIL |
| H.6 | Italian alias 'detto' | ❌ FAIL |
| H.5 | French alias 'dit' | ❌ FAIL |
| H.4 | English alias 'also known as' | ❌ FAIL |
| H.3 | Greek alias γνωστός ως | ❌ FAIL |
| H.2 | Chinese alias 又名 | ❌ FAIL |
| H.1 | Russian alias explanatory text | ❌ FAIL |
| E.11 | Italian company with SpA suffix | ❌ FAIL |
| E.10 | Japanese brand-name override | ❌ FAIL |
| E.9 | Mexican company with multi-word legal form | ❌ FAIL |
| E.8 | Arabic company with sharika prefix | ❌ FAIL |
| E.7 | Russian company with PAO prefix (not suffix) | ❌ FAIL |
| E.6 | Greek company with Α.Ε. suffix | ❌ FAIL |
| E.5 | Korean company with Jusikhoesa suffix | ❌ FAIL |
| E.4 | Japanese company with KK suffix | ❌ FAIL |
| G.15 | German umlaut ö in surname | ❌ FAIL |
| G.14 | Italian accent ò | ✅ PASS |
| G.13 | French cedilla ç | ✅ PASS |
| G.12 | French accent é | ✅ PASS |
| G.11 | Spanish accented name | ✅ PASS |
| F.30 | Korean surname Ryu/Yoo/Lyu family | ✅ PASS |
| F.29 | Korean surname Lee/Yi/Rhee family | ❌ FAIL |
| F.28 | Korean surname Jeong/Jung/Chung family | ✅ PASS |
| F.27 | Korean surname Choi/Choe variant family | ❌ FAIL |
| F.26 | Korean surname Bak/Park variant family | ✅ PASS |
| F.25 | Chinese short two-character name | ✅ PASS |
| F.24 | Chinese Taiwan Traditional | ✅ PASS |
| F.23 | Chinese mainland Simplified | ✅ PASS |
| F.22 | Japanese katakana name | ✅ PASS |
| F.21 | Japanese full surname-first name | ✅ PASS |
| F.20 | Japanese name with long vowel sho | ✅ PASS |
| F.19 | Japanese name with long vowel ou | ✅ PASS |
| F.18 | Greek name with B→V mapping | ✅ PASS |
| F.17 | Greek name with Ch consonant | ✅ PASS |
| F.16 | Greek compound name | ✅ PASS |
| F.15 | Russian compound name with two parts | ❌ FAIL |
| F.14 | Ukrainian female with feminine patronymic | ✅ PASS |
| F.13 | Ukrainian male name distinct from Russian | ✅ PASS |
| F.12 | Russian female name with patronymic | ✅ PASS |
| F.11 | Russian male name with patronymic and ё | ❌ FAIL |
| D.12 | Nationality adjective in Japanese | ❌ FAIL |
| D.11 | City name in Korean | ✅ PASS |
| D.10 | City name in Chinese | ❌ FAIL |
| D.9 | City name in Japanese | ❌ FAIL |
| D.8 | City name in Arabic | ✅ PASS |
| C.26 | Japanese role auditor | ✅ PASS |
| C.25 | Spanish status in liquidation | ✅ PASS |
| C.24 | Arabic legal form limited company | ❌ FAIL |
| C.23 | Korean legal form Jusikhoesa | ✅ PASS |
| C.22 | Mexican legal form SAB de CV | ❌ FAIL |
| C.21 | French legal form SARL | ❌ FAIL |
| C.20 | Italian legal form SpA | ✅ PASS |
| B.37 | Egyptian Arabic phone number with spaces | ❌ FAIL |
| B.36 | Spoken-style Han digits in phone | ❌ FAIL |
| B.35 | Han numerals in house number | ❌ FAIL |
| B.34 | Korean comma thousands | ✅ PASS |
| B.33 | UK comma thousands separator | ✅ PASS |
| B.32 | European dot thousands separator | ✅ PASS |
| B.31 | Han numerals for amount | ❌ FAIL |
| B.30 | Russian space thousands separator | ✅ PASS |
| B.29 | French space thousands separator | ✅ PASS |
| B.28 | Arabic thousands separator | ❌ FAIL |
| B.27 | Arabic-Indic phone number | ❌ FAIL |
| B.26 | Full-width Korean digits in address | ❌ FAIL |
| B.25 | Full-width Japanese phone number | ❌ FAIL |
| B.24 | Chinese Han numeral date | ❌ FAIL |
| B.23 | Japanese Kanji numeral date | ❌ FAIL |
| B.22 | US MM/DD/YYYY date | ❌ FAIL |
| B.21 | German dot-separated date | ✅ PASS |
| B.20 | Russian dot-separated date | ✅ PASS |
| B.19 | Korean date format | ❌ FAIL |
| A.12 | Arabic-Indic digits in ID number | ❌ FAIL |
| A.11 | UK NI number with spaces | ❌ FAIL |
| A.10 | Hong Kong ID with check digit in brackets | ❌ FAIL |
| A.9 | German tax number with slash separators | ❌ FAIL |
| A.8 | Russian passport with internal spaces | ❌ FAIL |
| A.7 | Full-width digits in passport number | ❌ FAIL |
| E.3 | Number that looks like a date | ❌ FAIL |
| E.2 | Mixed script company name | ✅ PASS |
| E.1 | Short ambiguous string | ❌ FAIL |
| G.10 | Norwegian o-stroke | ✅ PASS |
| G.9 | Dutch van particle | ✅ PASS |
| G.8 | French accented name | ✅ PASS |
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
| B.18 | Saudi Riyal | ✅ PASS |
| B.17 | Euro European format | ✅ PASS |
| B.16 | Japanese yen amount | ✅ PASS |
| A.6 | LEI code | ✅ PASS |
| A.5 | Tax ID with country prefix | ✅ PASS |
| A.4 | IBAN | ✅ PASS |
| B.15 | Hebrew date spelled out | ✅ PASS |
| B.14 | Hijri date day-first Arabic-Indic | ✅ PASS |
| B.13 | Thai date with พ.ศ. label | ✅ PASS |
| B.12 | Thai date day-first format | ✅ PASS |
| C.12 | Russian legal form at end of company name | ✅ PASS |
| C.11 | German legal form at end of company name | ✅ PASS |
| C.10 | Japanese legal form at end of company name | ✅ PASS |
| F.10 | Korean full name | ✅ PASS |
| F.9 | Greek full name | ✅ PASS |
| F.8 | Chinese full name | ✅ PASS |
| F.7 | Russian full name with patronymic | ✅ PASS |
| F.6 | Japanese full name surname + given | ✅ PASS |
| I.4 | Arabic name with Egyptian convention | ❌ FAIL |
| I.3 | Arabic female name with bint lineage marker | ❌ FAIL |
| I.2 | Arabic name with Abd compound prefix | ❌ FAIL |
| I.1 | Arabic person name (transliterated with review flag) | ❌ FAIL |
| G.7 | Portuguese tilde | ✅ PASS |
| G.6 | Scandinavian Æ | ✅ PASS |
| G.5 | Polish ł | ✅ PASS |
| G.4 | Turkish dotted I | ✅ PASS |
| G.3 | Spanish ñ | ✅ PASS |
| G.2 | German ß | ✅ PASS |
| G.1 | German umlaut expansion | ✅ PASS |
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
| B.10 | Swiss apostrophe number format | ✅ PASS |
| B.9 | European number format | ✅ PASS |
| B.8 | Full-width parenthetical negative | ✅ PASS |
| B.7 | Japanese triangle negative | ✅ PASS |
| B.6 | Minguo (Taiwan ROC) date | ✅ PASS |
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
| **latency** | — | `3.20s` | — |

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
| **latency** | — | `0.77s` | — |

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
| **latency** | — | `0.83s` | — |

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
| **latency** | — | `0.91s` | — |

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
| latency | `0.04s` |

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
| **latency** | — | `1.80s` | — |

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
| latency | `0.01s` |

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
| **latency** | — | `0.74s` | — |

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
| **latency** | — | `0.78s` | — |

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
| review_required | `False` |
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
| **latency** | — | `0.84s` | — |

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
| latency | `0.03s` |

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
| **latency** | — | `0.86s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "114/5/8", "field_type": "date_of_birth", "language": "zh"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CALENDAR` |
| normalised_form | `2025-05-08` |
| confidence | `0.95` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CALENDAR` | `CALENDAR` | ✅ PASS |
| **normalised_form** | `2025-05-08` | `2025-05-08` | ✅ PASS |

### Overall: ✅ PASS

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
| **latency** | — | `1.01s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "△4,191", "field_type": "total_assets", "language": "ja"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `NUMERIC` |
| normalised_form | `-4191` |
| confidence | `0.95` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `NUMERIC` | `NUMERIC` | ✅ PASS |
| **normalised_form** | `-4191` | `-4191` | ✅ PASS |

### Overall: ✅ PASS

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
| **latency** | — | `1.22s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `net_assets` but expected `total_assets`. The router will process the field as `net_assets` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "（4,191）", "field_type": "net_assets", "language": "ja"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `NUMERIC` |
| normalised_form | `-4191` |
| confidence | `0.95` |
| review_required | `False` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `NUMERIC` | `NUMERIC` | ✅ PASS |
| **normalised_form** | `-4191` | `-4191` | ✅ PASS |

### Overall: ✅ PASS

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
| **language** | `de` | `en` | ⚠️ mismatch |
| **confidence** | — | `0.95` | — |
| **latency** | — | `1.01s` | — |

> ⚠️ **Classification mismatch on language.** GPT-4o-mini returned `en` but expected `de`. This may affect strategy selection (e.g. character map handler chosen for wrong language).

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "1.234.567,89", "field_type": "total_assets", "language": "en"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `NUMERIC` |
| normalised_form | `1234567.89` |
| confidence | `0.95` |
| review_required | `False` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `NUMERIC` | `NUMERIC` | ✅ PASS |
| **normalised_form** | `1234567.89` | `1234567.89` | ✅ PASS |

### Overall: ✅ PASS

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
| **latency** | — | `1.02s` | — |

> ⚠️ **Classification mismatch on language.** GPT-4o-mini returned `en` but expected `fr`. This may affect strategy selection (e.g. character map handler chosen for wrong language).

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "1'234'567.89", "field_type": "total_assets", "language": "en"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `NUMERIC` |
| normalised_form | `1234567.89` |
| confidence | `0.95` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `NUMERIC` | `NUMERIC` | ✅ PASS |
| **normalised_form** | `1234567.89` | `1234567.89` | ✅ PASS |

### Overall: ✅ PASS

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
| **latency** | — | `0.80s` | — |

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
| latency | `0.01s` |

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
| **confidence** | — | `0.97` | — |
| **latency** | — | `1.32s` | — |

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
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.81s` | — |

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
| latency | `0.01s` |

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
| **latency** | — | `1.33s` | — |

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
| **latency** | — | `3.77s` | — |

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
| latency | `0.01s` |

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
| **latency** | — | `1.63s` | — |

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
| **latency** | — | `0.90s` | — |

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
| **confidence** | — | `0.92` | — |
| **latency** | — | `0.92s` | — |

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
| **field_type** | `status` | `status` | ✅ match |
| **language** | `de` | `de` | ✅ match |
| **confidence** | — | `0.85` | — |
| **latency** | — | `0.81s` | — |

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
| latency | `0.01s` |

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
| **latency** | — | `0.71s` | — |

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
| **latency** | — | `0.76s` | — |

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
| latency | `0.02s` |

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
| **latency** | — | `0.83s` | — |

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
| **latency** | — | `1.06s` | — |

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
| latency | `0.01s` |

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
| **latency** | — | `0.67s` | — |

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
| latency | `0.01s` |

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
| **latency** | — | `0.81s` | — |

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
| latency | `0.05s` |

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
| **latency** | — | `1.14s` | — |

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
| **latency** | — | `1.25s` | — |

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
| **latency** | — | `0.81s` | — |

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
| latency | `0.35s` |

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
| **latency** | — | `0.77s` | — |

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
| latency | `0.27s` |

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
| **latency** | — | `0.74s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Müller", "field_type": "person_name", "language": "de"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CHARACTER_MAP` |
| normalised_form | `MUELLER` |
| confidence | `0.90` |
| review_required | `False` |
| allowed_variants | `MULLER` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CHARACTER_MAP` | `CHARACTER_MAP` | ✅ PASS |
| **normalised_form** | `MUELLER` | `MUELLER` | ✅ PASS |

### Overall: ✅ PASS

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
| **latency** | — | `0.79s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `address` but expected `person_name`. The router will process the field as `address` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Straße", "field_type": "address", "language": "de"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CHARACTER_MAP` |
| normalised_form | `STRASSE` |
| confidence | `0.90` |
| review_required | `False` |
| allowed_variants | `STRASE` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CHARACTER_MAP` | `CHARACTER_MAP` | ✅ PASS |
| **normalised_form** | `STRASSE` | `STRASSE` | ✅ PASS |

### Overall: ✅ PASS

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
| **latency** | — | `0.77s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `family_name` but expected `person_name`. The router will process the field as `family_name` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Muñoz", "field_type": "family_name", "language": "es"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CHARACTER_MAP` |
| normalised_form | `MUNOZ` |
| confidence | `0.90` |
| review_required | `False` |
| allowed_variants | `MUNYOZ` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CHARACTER_MAP` | `CHARACTER_MAP` | ✅ PASS |
| **normalised_form** | `MUNOZ` | `MUNOZ` | ✅ PASS |

### Overall: ✅ PASS

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
| **confidence** | — | `0.85` | — |
| **latency** | — | `0.67s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `city` but expected `person_name`. The router will process the field as `city` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "İstanbul", "field_type": "city", "language": "tr"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CHARACTER_MAP` |
| normalised_form | `ISTANBUL` |
| confidence | `0.95` |
| review_required | `False` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CHARACTER_MAP` | `CHARACTER_MAP` | ✅ PASS |
| **normalised_form** | `ISTANBUL` | `ISTANBUL` | ✅ PASS |

### Overall: ✅ PASS

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
| **latency** | — | `1.36s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `city` but expected `person_name`. The router will process the field as `city` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Łódź", "field_type": "city", "language": "pl"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CHARACTER_MAP` |
| normalised_form | `LODZ` |
| confidence | `0.95` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CHARACTER_MAP` | `CHARACTER_MAP` | ✅ PASS |
| **normalised_form** | `LODZ` | `LODZ` | ✅ PASS |

### Overall: ✅ PASS

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
| **latency** | — | `0.82s` | — |

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
| latency | `0.01s` |

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
| **latency** | — | `0.85s` | — |

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
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CHARACTER_MAP` | `CHARACTER_MAP` | ✅ PASS |
| **normalised_form** | `JOAO` | `JOAO` | ✅ PASS |

### Overall: ✅ PASS

---

## I.1 — Arabic person name (transliterated with review flag)

| | |
|---|---|
| **Input** | `محمد عبد الله` |
| **Expected field type** | `person_name` |
| **Expected language** | `ar` |
| **Expected normalised form** | `MHMD ABDULLAH` |
| **Expected method** | `['TRANSLITERATION', 'TRANSLITERATE']` |
| **Notes** | Compound token عبد الله → Abdullah caught by _ARABIC_TOKENS; remaining محمد → MHMD consonant skeleton. review_required=True, should_use_in_screening=True. Analyst confirms vowel insertion. |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `person_name` | ✅ match |
| **language** | `ar` | `ar` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.89s` | — |

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
| **method** | `TRANSLITERATION` or `TRANSLITERATE` | `UNRESOLVED` | ❌ FAIL |
| **normalised_form** | `MHMD ABDULLAH` | `None` | ❌ FAIL |

> ❌ **Method failure diagnosis:** The strategy for field_type='person_name' language='ar' returned None or raised NotImplementedError. Check that the strategy module is fully implemented and wired into the router.

### Overall: ❌ FAIL

---

## I.2 — Arabic name with Abd compound prefix

| | |
|---|---|
| **Input** | `محمود عبد الحميد سعيد` |
| **Expected field type** | `person_name` |
| **Expected language** | `ar` |
| **Expected normalised form** | `MHMWD ABD ALHMYD SAYD` |
| **Expected method** | `['TRANSLITERATION', 'TRANSLITERATE']` |
| **Notes** | عبد الله token does NOT match here (different second word); falls through to character-by-character. الـ token expands to 'al-' but apostrophe is stripped by _normalise(). Consonant skeleton only — analyst confirms 'Mahmoud Abdelhamid Said'. |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `person_name` | ✅ match |
| **language** | `ar` | `ar` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.82s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "محمود عبد الحميد سعيد", "field_type": "person_name", "language": "ar"}
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
| **normalised_form** | `MHMWD ABD ALHMYD SAYD` | `None` | ❌ FAIL |

> ❌ **Method failure diagnosis:** The strategy for field_type='person_name' language='ar' returned None or raised NotImplementedError. Check that the strategy module is fully implemented and wired into the router.

### Overall: ❌ FAIL

---

## I.3 — Arabic female name with bint lineage marker

| | |
|---|---|
| **Input** | `نورة بنت سعد الغامدي` |
| **Expected field type** | `person_name` |
| **Expected language** | `ar` |
| **Expected normalised form** | `NWRH BNT SAD ALGHAMDY` |
| **Expected method** | `['TRANSLITERATION', 'TRANSLITERATE']` |
| **Notes** | Lineage marker بنت → BNT preserved. ة (ta marbuta) → h. Analyst confirms 'Noura/Nora bint Saad al-Ghamdi'. |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `person_name` | ✅ match |
| **language** | `ar` | `ar` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.91s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "نورة بنت سعد الغامدي", "field_type": "person_name", "language": "ar"}
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
| **normalised_form** | `NWRH BNT SAD ALGHAMDY` | `None` | ❌ FAIL |

> ❌ **Method failure diagnosis:** The strategy for field_type='person_name' language='ar' returned None or raised NotImplementedError. Check that the strategy module is fully implemented and wired into the router.

### Overall: ❌ FAIL

---

## I.4 — Arabic name with Egyptian convention

| | |
|---|---|
| **Input** | `أحمد سمير نصر عبد الناصر` |
| **Expected field type** | `person_name` |
| **Expected language** | `ar` |
| **Expected normalised form** | `AHMD SMYR NSR ABD ALNASR` |
| **Expected method** | `['TRANSLITERATION', 'TRANSLITERATE']` |
| **Notes** | Egyptian Abd-el vs Saudi Abd-al convention divergence resolved by analyst review — pipeline produces consonant skeleton, review_required=True. |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `full_name` | ⚠️ mismatch |
| **language** | `ar` | `ar` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `1.23s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `full_name` but expected `person_name`. The router will process the field as `full_name` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "أحمد سمير نصر عبد الناصر", "field_type": "full_name", "language": "ar"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `TRANSLITERATE` |
| normalised_form | `AHMD SMYR NSR BD AL- NASR` |
| confidence | `0.70` |
| review_required | `True` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `TRANSLITERATION` or `TRANSLITERATE` | `TRANSLITERATE` | ✅ PASS |
| **normalised_form** | `AHMD SMYR NSR ABD ALNASR` | `AHMD SMYR NSR BD AL- NASR` | ❌ FAIL |

> ❌ **Form failure diagnosis:** Got 'AHMD SMYR NSR BD AL- NASR', expected 'AHMD SMYR NSR ABD ALNASR'. Inspect the strategy module output.

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
| **latency** | — | `0.72s` | — |

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
| **latency** | — | `0.89s` | — |

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
| latency | `0.01s` |

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
| **latency** | — | `1.02s` | — |

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
| latency | `0.01s` |

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
| **latency** | — | `1.01s` | — |

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
| **latency** | — | `0.70s` | — |

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
| **language** | `ja` | `zh` | ⚠️ mismatch |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.75s` | — |

> ⚠️ **Classification mismatch on language.** GPT-4o-mini returned `zh` but expected `ja`. This may affect strategy selection (e.g. character map handler chosen for wrong language).

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "三菱商事株式会社", "field_type": "company_name", "language": "zh"}
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
| **latency** | — | `0.96s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Müller & Söhne GmbH", "field_type": "company_name", "language": "de"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `VOCABULARY` |
| normalised_form | `GMBH` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `VOCABULARY` | `VOCABULARY` | ✅ PASS |
| **normalised_form** | `GMBH` | `GMBH` | ✅ PASS |

### Overall: ✅ PASS

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
| **latency** | — | `0.67s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Газпром ПАО", "field_type": "company_name", "language": "ru"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `VOCABULARY` |
| normalised_form | `PJSC` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `VOCABULARY` | `VOCABULARY` | ✅ PASS |
| **normalised_form** | `PJSC` | `PJSC` | ✅ PASS |

### Overall: ✅ PASS

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
| **latency** | — | `0.89s` | — |

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
| latency | `0.01s` |

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
| **confidence** | — | `0.93` | — |
| **latency** | — | `0.76s` | — |

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
| normalised_form | `2025` |
| confidence | `0.95` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CALENDAR` | `CALENDAR` | ✅ PASS |
| **normalised_form** | `2025` | `2025` | ✅ PASS |

### Overall: ✅ PASS

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
| **latency** | — | `1.75s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "١٤/٠٣/١٤٤٥", "field_type": "date_of_birth", "language": "ar"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CALENDAR` |
| normalised_form | `2023-09-29` |
| confidence | `0.95` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CALENDAR` | `CALENDAR` | ✅ PASS |
| **normalised_form** | `2023-09-29` | `2023-09-29` | ✅ PASS |

### Overall: ✅ PASS

---

## B.15 — Hebrew date spelled out

| | |
|---|---|
| **Input** | `15 תשרי 5786` |
| **Expected field type** | `date_of_birth` |
| **Expected language** | `he` |
| **Expected normalised form** | `2025-10-07` |
| **Expected method** | `CALENDAR` |
| **Notes** | Hebrew date with month name spelled out — 15 Tishrei 5786; RH 5786=2025-09-23 so +14d=Oct 7 |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `date_of_birth` | `date_of_birth` | ✅ match |
| **language** | `he` | `he` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `1.01s` | — |

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
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CALENDAR` | `CALENDAR` | ✅ PASS |
| **normalised_form** | `2025-10-07` | `2025-10-07` | ✅ PASS |

### Overall: ✅ PASS

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
| **latency** | — | `0.92s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "GB29 NWBK 6016 1331 9268 19", "field_type": "iban", "language": "en"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `PRESERVE` |
| normalised_form | `GB29 NWBK 6016 1331 9268 19` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `PRESERVE` | `PRESERVE` | ✅ PASS |
| **normalised_form** | `GB29 NWBK 6016 1331 9268 19` | `GB29 NWBK 6016 1331 9268 19` | ✅ PASS |

### Overall: ✅ PASS

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
| **latency** | — | `0.83s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `iban` but expected `tax_id`. The router will process the field as `iban` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "DE811100090", "field_type": "iban", "language": "de"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `PRESERVE` |
| normalised_form | `DE811100090` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `PRESERVE` | `PRESERVE` | ✅ PASS |
| **normalised_form** | `DE811100090` | `DE811100090` | ✅ PASS |

### Overall: ✅ PASS

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
| **latency** | — | `1.01s` | — |

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
| latency | `0.01s` |

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
| **latency** | — | `0.91s` | — |

> ⚠️ **Classification mismatch on language.** GPT-4o-mini returned `en` but expected `ja`. This may affect strategy selection (e.g. character map handler chosen for wrong language).

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "¥1,234,567", "field_type": "share_capital", "language": "en"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `NUMERIC` |
| normalised_form | `1234567` |
| confidence | `0.95` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `NUMERIC` | `NUMERIC` | ✅ PASS |
| **normalised_form** | `1234567` | `1234567` | ✅ PASS |

### Overall: ✅ PASS

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
| **latency** | — | `0.90s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "€2.500.000,00", "field_type": "share_capital", "language": "de"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `NUMERIC` |
| normalised_form | `2500000.00` |
| confidence | `0.95` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `NUMERIC` | `NUMERIC` | ✅ PASS |
| **normalised_form** | `2500000.00` | `2500000.00` | ✅ PASS |

### Overall: ✅ PASS

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
| **latency** | — | `1.41s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "﷼500,000", "field_type": "share_capital", "language": "ar"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `NUMERIC` |
| normalised_form | `500000` |
| confidence | `0.95` |
| review_required | `False` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `NUMERIC` | `NUMERIC` | ✅ PASS |
| **normalised_form** | `500000` | `500000` | ✅ PASS |

### Overall: ✅ PASS

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
| **latency** | — | `0.70s` | — |

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
| latency | `0.01s` |

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
| **latency** | — | `1.13s` | — |

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
| **latency** | — | `0.70s` | — |

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
| **confidence** | — | `0.91` | — |
| **latency** | — | `1.11s` | — |

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
| latency | `0.01s` |

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
| **latency** | — | `0.81s` | — |

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
| latency | `0.01s` |

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
| **latency** | — | `1.02s` | — |

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
| **latency** | — | `0.84s` | — |

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
| latency | `0.01s` |

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
| **latency** | — | `0.88s` | — |

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
| latency | `0.01s` |

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
| **latency** | — | `0.81s` | — |

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
| **latency** | — | `0.81s` | — |

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
| **latency** | — | `0.81s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Élodie Lefèvre", "field_type": "person_name", "language": "fr"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CHARACTER_MAP` |
| normalised_form | `ELODIE LEFEVRE` |
| confidence | `0.90` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CHARACTER_MAP` | `CHARACTER_MAP` | ✅ PASS |
| **normalised_form** | `ELODIE LEFEVRE` | `ELODIE LEFEVRE` | ✅ PASS |

### Overall: ✅ PASS

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
| **confidence** | — | `0.88` | — |
| **latency** | — | `0.70s` | — |

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
| latency | `0.01s` |

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
| **latency** | — | `2.07s` | — |

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
| latency | `0.00s` |

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
| **latency** | — | `0.67s` | — |

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
| **latency** | — | `0.71s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Sony株式会社", "field_type": "company_name", "language": "ja"}
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
| **confidence** | — | `0.92` | — |
| **latency** | — | `0.81s` | — |

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

## A.7 — Full-width digits in passport number

| | |
|---|---|
| **Input** | `C８７６５４３２１` |
| **Expected field type** | `passport_no` |
| **Expected language** | `de` |
| **Expected normalised form** | `C87654321` |
| **Expected method** | `PRESERVE` |
| **Notes** | Full-width digits must collapse to ASCII but value preserved |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `passport_no` | `id_no` | ⚠️ mismatch |
| **language** | `de` | `ja` | ⚠️ mismatch |
| **confidence** | — | `0.90` | — |
| **latency** | — | `1.30s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `id_no` but expected `passport_no`. The router will process the field as `id_no` which may select the wrong strategy.

> ⚠️ **Classification mismatch on language.** GPT-4o-mini returned `ja` but expected `de`. This may affect strategy selection (e.g. character map handler chosen for wrong language).

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "C８７６５４３２１", "field_type": "id_no", "language": "ja"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `PRESERVE` |
| normalised_form | `C８７６５４３２１` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `PRESERVE` | `PRESERVE` | ✅ PASS |
| **normalised_form** | `C87654321` | `C８７６５４３２１` | ❌ FAIL |

> ❌ **Form failure diagnosis:** Got 'C８７６５４３２１', expected 'C87654321'. Inspect the strategy module output.

### Overall: ❌ FAIL

---

## A.8 — Russian passport with internal spaces

| | |
|---|---|
| **Input** | `45 09 123456` |
| **Expected field type** | `passport_no` |
| **Expected language** | `ru` |
| **Expected normalised form** | `4509123456` |
| **Expected method** | `PRESERVE` |
| **Notes** | Russian series+number with whitespace removed |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `passport_no` | `id_no` | ⚠️ mismatch |
| **language** | `ru` | `en` | ⚠️ mismatch |
| **confidence** | — | `0.85` | — |
| **latency** | — | `0.94s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `id_no` but expected `passport_no`. The router will process the field as `id_no` which may select the wrong strategy.

> ⚠️ **Classification mismatch on language.** GPT-4o-mini returned `en` but expected `ru`. This may affect strategy selection (e.g. character map handler chosen for wrong language).

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "45 09 123456", "field_type": "id_no", "language": "en"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `PRESERVE` |
| normalised_form | `45 09 123456` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `PRESERVE` | `PRESERVE` | ✅ PASS |
| **normalised_form** | `4509123456` | `45 09 123456` | ❌ FAIL |

> ❌ **Form failure diagnosis:** Got '45 09 123456', expected '4509123456'. Inspect the strategy module output.

### Overall: ❌ FAIL

---

## A.9 — German tax number with slash separators

| | |
|---|---|
| **Input** | `Steuernummer 123/456/78901` |
| **Expected field type** | `tax_id` |
| **Expected language** | `de` |
| **Expected normalised form** | `12345678901` |
| **Expected method** | `PRESERVE` |
| **Notes** | Label stripped, digits preserved |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `tax_id` | `tax_id` | ✅ match |
| **language** | `de` | `de` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.81s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Steuernummer 123/456/78901", "field_type": "tax_id", "language": "de"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `PRESERVE` |
| normalised_form | `Steuernummer 123/456/78901` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `PRESERVE` | `PRESERVE` | ✅ PASS |
| **normalised_form** | `12345678901` | `Steuernummer 123/456/78901` | ❌ FAIL |

> ❌ **Form failure diagnosis:** Got 'Steuernummer 123/456/78901', expected '12345678901'. Inspect the strategy module output.

### Overall: ❌ FAIL

---

## A.10 — Hong Kong ID with check digit in brackets

| | |
|---|---|
| **Input** | `A123456(3)` |
| **Expected field type** | `id_number` |
| **Expected language** | `zh` |
| **Expected normalised form** | `A1234563` |
| **Expected method** | `PRESERVE` |
| **Notes** | Brackets removed, value preserved |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `id_number` | `id_no` | ⚠️ mismatch |
| **language** | `zh` | `en` | ⚠️ mismatch |
| **confidence** | — | `0.85` | — |
| **latency** | — | `1.42s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `id_no` but expected `id_number`. The router will process the field as `id_no` which may select the wrong strategy.

> ⚠️ **Classification mismatch on language.** GPT-4o-mini returned `en` but expected `zh`. This may affect strategy selection (e.g. character map handler chosen for wrong language).

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "A123456(3)", "field_type": "id_no", "language": "en"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `PRESERVE` |
| normalised_form | `A123456(3)` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `PRESERVE` | `PRESERVE` | ✅ PASS |
| **normalised_form** | `A1234563` | `A123456(3)` | ❌ FAIL |

> ❌ **Form failure diagnosis:** Got 'A123456(3)', expected 'A1234563'. Inspect the strategy module output.

### Overall: ❌ FAIL

---

## A.11 — UK NI number with spaces

| | |
|---|---|
| **Input** | `NI AB 12 34 56 C` |
| **Expected field type** | `id_number` |
| **Expected language** | `en` |
| **Expected normalised form** | `AB123456C` |
| **Expected method** | `PRESERVE` |
| **Notes** | Label and spaces stripped |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `id_number` | `id_no` | ⚠️ mismatch |
| **language** | `en` | `en` | ✅ match |
| **confidence** | — | `0.90` | — |
| **latency** | — | `1.76s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `id_no` but expected `id_number`. The router will process the field as `id_no` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "NI AB 12 34 56 C", "field_type": "id_no", "language": "en"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `PRESERVE` |
| normalised_form | `NI AB 12 34 56 C` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `PRESERVE` | `PRESERVE` | ✅ PASS |
| **normalised_form** | `AB123456C` | `NI AB 12 34 56 C` | ❌ FAIL |

> ❌ **Form failure diagnosis:** Got 'NI AB 12 34 56 C', expected 'AB123456C'. Inspect the strategy module output.

### Overall: ❌ FAIL

---

## A.12 — Arabic-Indic digits in ID number

| | |
|---|---|
| **Input** | `٢٩٨٠٣١٤١٥٠١٢٣٤` |
| **Expected field type** | `id_number` |
| **Expected language** | `ar` |
| **Expected normalised form** | `29803141501234` |
| **Expected method** | `PRESERVE` |
| **Notes** | Arabic-Indic digits converted to ASCII, value preserved |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `id_number` | `id_no` | ⚠️ mismatch |
| **language** | `ar` | `ar` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `6.58s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `id_no` but expected `id_number`. The router will process the field as `id_no` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "٢٩٨٠٣١٤١٥٠١٢٣٤", "field_type": "id_no", "language": "ar"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `PRESERVE` |
| normalised_form | `٢٩٨٠٣١٤١٥٠١٢٣٤` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `PRESERVE` | `PRESERVE` | ✅ PASS |
| **normalised_form** | `29803141501234` | `٢٩٨٠٣١٤١٥٠١٢٣٤` | ❌ FAIL |

> ❌ **Form failure diagnosis:** Got '٢٩٨٠٣١٤١٥٠١٢٣٤', expected '29803141501234'. Inspect the strategy module output.

### Overall: ❌ FAIL

---

## B.19 — Korean date format

| | |
|---|---|
| **Input** | `2024년 3월 14일` |
| **Expected field type** | `date_of_birth` |
| **Expected language** | `ko` |
| **Expected normalised form** | `2024-03-14` |
| **Expected method** | `CALENDAR` |
| **Notes** | Korean year/month/day labels stripped |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `date_of_birth` | `date_of_birth` | ✅ match |
| **language** | `ko` | `ko` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.88s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "2024년 3월 14일", "field_type": "date_of_birth", "language": "ko"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CALENDAR` |
| normalised_form | `2024년 3월 14일` |
| confidence | `0.95` |
| review_required | `True` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CALENDAR` | `CALENDAR` | ✅ PASS |
| **normalised_form** | `2024-03-14` | `2024년 3월 14일` | ❌ FAIL |

> ❌ **Form failure diagnosis:** Calendar conversion produced '2024년 3월 14일' instead of '2024-03-14'. Check the epoch calculation in the relevant calendar module.

### Overall: ❌ FAIL

---

## B.20 — Russian dot-separated date

| | |
|---|---|
| **Input** | `21.06.1990` |
| **Expected field type** | `date_of_birth` |
| **Expected language** | `ru` |
| **Expected normalised form** | `1990-06-21` |
| **Expected method** | `CALENDAR` |
| **Notes** | DD.MM.YYYY Russian/European format |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `date_of_birth` | `date_of_birth` | ✅ match |
| **language** | `ru` | `de` | ⚠️ mismatch |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.81s` | — |

> ⚠️ **Classification mismatch on language.** GPT-4o-mini returned `de` but expected `ru`. This may affect strategy selection (e.g. character map handler chosen for wrong language).

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "21.06.1990", "field_type": "date_of_birth", "language": "de"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CALENDAR` |
| normalised_form | `1990-06-21` |
| confidence | `0.95` |
| review_required | `False` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CALENDAR` | `CALENDAR` | ✅ PASS |
| **normalised_form** | `1990-06-21` | `1990-06-21` | ✅ PASS |

### Overall: ✅ PASS

---

## B.21 — German dot-separated date

| | |
|---|---|
| **Input** | `14.09.1978` |
| **Expected field type** | `date_of_birth` |
| **Expected language** | `de` |
| **Expected normalised form** | `1978-09-14` |
| **Expected method** | `CALENDAR` |
| **Notes** | DD.MM.YYYY German format |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `date_of_birth` | `date_of_birth` | ✅ match |
| **language** | `de` | `de` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `1.01s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "14.09.1978", "field_type": "date_of_birth", "language": "de"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CALENDAR` |
| normalised_form | `1978-09-14` |
| confidence | `0.95` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CALENDAR` | `CALENDAR` | ✅ PASS |
| **normalised_form** | `1978-09-14` | `1978-09-14` | ✅ PASS |

### Overall: ✅ PASS

---

## B.22 — US MM/DD/YYYY date

| | |
|---|---|
| **Input** | `03/14/1990` |
| **Expected field type** | `date_of_birth` |
| **Expected language** | `en` |
| **Expected normalised form** | `1990-03-14` |
| **Expected method** | `CALENDAR` |
| **Notes** | US date order disambiguated by language=en + country context |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `date_of_birth` | `date_of_birth` | ✅ match |
| **language** | `en` | `en` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.78s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "03/14/1990", "field_type": "date_of_birth", "language": "en"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CALENDAR` |
| normalised_form | `03/14/1990` |
| confidence | `0.95` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CALENDAR` | `CALENDAR` | ✅ PASS |
| **normalised_form** | `1990-03-14` | `03/14/1990` | ❌ FAIL |

> ❌ **Form failure diagnosis:** Calendar conversion produced '03/14/1990' instead of '1990-03-14'. Check the epoch calculation in the relevant calendar module.

### Overall: ❌ FAIL

---

## B.23 — Japanese Kanji numeral date

| | |
|---|---|
| **Input** | `二〇二四年三月十四日` |
| **Expected field type** | `date_of_birth` |
| **Expected language** | `ja` |
| **Expected normalised form** | `2024-03-14` |
| **Expected method** | `CALENDAR` |
| **Notes** | Han numerals require value conversion not just transliteration |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `date_of_birth` | `date_of_birth` | ✅ match |
| **language** | `ja` | `zh` | ⚠️ mismatch |
| **confidence** | — | `0.88` | — |
| **latency** | — | `1.06s` | — |

> ⚠️ **Classification mismatch on language.** GPT-4o-mini returned `zh` but expected `ja`. This may affect strategy selection (e.g. character map handler chosen for wrong language).

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "二〇二四年三月十四日", "field_type": "date_of_birth", "language": "zh"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CALENDAR` |
| normalised_form | `二〇二四年三月十四日` |
| confidence | `0.95` |
| review_required | `True` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CALENDAR` | `CALENDAR` | ✅ PASS |
| **normalised_form** | `2024-03-14` | `二〇二四年三月十四日` | ❌ FAIL |

> ❌ **Form failure diagnosis:** Calendar conversion produced '二〇二四年三月十四日' instead of '2024-03-14'. Check the epoch calculation in the relevant calendar module.

### Overall: ❌ FAIL

---

## B.24 — Chinese Han numeral date

| | |
|---|---|
| **Input** | `二零二四年三月十四日` |
| **Expected field type** | `date_of_birth` |
| **Expected language** | `zh` |
| **Expected normalised form** | `2024-03-14` |
| **Expected method** | `CALENDAR` |
| **Notes** | Han numerals for date |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `date_of_birth` | `date_of_birth` | ✅ match |
| **language** | `zh` | `zh` | ✅ match |
| **confidence** | — | `0.88` | — |
| **latency** | — | `0.87s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "二零二四年三月十四日", "field_type": "date_of_birth", "language": "zh"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CALENDAR` |
| normalised_form | `二零二四年三月十四日` |
| confidence | `0.95` |
| review_required | `True` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CALENDAR` | `CALENDAR` | ✅ PASS |
| **normalised_form** | `2024-03-14` | `二零二四年三月十四日` | ❌ FAIL |

> ❌ **Form failure diagnosis:** Calendar conversion produced '二零二四年三月十四日' instead of '2024-03-14'. Check the epoch calculation in the relevant calendar module.

### Overall: ❌ FAIL

---

## B.25 — Full-width Japanese phone number

| | |
|---|---|
| **Input** | `０８０−１２３４−５６７８` |
| **Expected field type** | `phone_number` |
| **Expected language** | `ja` |
| **Expected normalised form** | `08012345678` |
| **Expected method** | `NUMERIC` |
| **Notes** | Full-width digits and dash to ASCII |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `phone_number` | `id_no` | ⚠️ mismatch |
| **language** | `ja` | `ja` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `3.57s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `id_no` but expected `phone_number`. The router will process the field as `id_no` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "０８０−１２３４−５６７８", "field_type": "id_no", "language": "ja"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `PRESERVE` |
| normalised_form | `０８０−１２３４−５６７８` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `NUMERIC` | `PRESERVE` | ❌ FAIL |
| **normalised_form** | `08012345678` | `０８０−１２３４−５６７８` | ❌ FAIL |

> ❌ **Method failure diagnosis:** Field type 'id_no' is in the PRESERVE_FIELDS list but should not be. Check PRESERVE_FIELDS in router.py or preserve.py.

### Overall: ❌ FAIL

---

## B.26 — Full-width Korean digits in address

| | |
|---|---|
| **Input** | `테헤란로 １２３` |
| **Expected field type** | `address` |
| **Expected language** | `ko` |
| **Expected normalised form** | `테헤란로 123` |
| **Expected method** | `NUMERIC` |
| **Notes** | Full-width digits normalised within address text |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `address` | `address` | ✅ match |
| **language** | `ko` | `ko` | ✅ match |
| **confidence** | — | `0.92` | — |
| **latency** | — | `0.91s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "테헤란로 １２３", "field_type": "address", "language": "ko"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `GEOGRAPHIC` |
| normalised_form | `TEHRAN` |
| confidence | `0.75` |
| review_required | `True` |
| latency | `0.02s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `NUMERIC` | `GEOGRAPHIC` | ❌ FAIL |
| **normalised_form** | `테헤란로 123` | `TEHRAN` | ❌ FAIL |

> ❌ **Method failure diagnosis:** Got 'GEOGRAPHIC', expected one of ['NUMERIC']. Check router.py strategy wiring.

### Overall: ❌ FAIL

---

## B.27 — Arabic-Indic phone number

| | |
|---|---|
| **Input** | `+٩٧١ ٥٠ ١٢٣ ٤٥٦٧` |
| **Expected field type** | `phone_number` |
| **Expected language** | `ar` |
| **Expected normalised form** | `+971501234567` |
| **Expected method** | `NUMERIC` |
| **Notes** | Arabic-Indic digits with country code |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `phone_number` | `id_no` | ⚠️ mismatch |
| **language** | `ar` | `ar` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `1.10s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `id_no` but expected `phone_number`. The router will process the field as `id_no` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "+٩٧١ ٥٠ ١٢٣ ٤٥٦٧", "field_type": "id_no", "language": "ar"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `PRESERVE` |
| normalised_form | `+٩٧١ ٥٠ ١٢٣ ٤٥٦٧` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `NUMERIC` | `PRESERVE` | ❌ FAIL |
| **normalised_form** | `+971501234567` | `+٩٧١ ٥٠ ١٢٣ ٤٥٦٧` | ❌ FAIL |

> ❌ **Method failure diagnosis:** Field type 'id_no' is in the PRESERVE_FIELDS list but should not be. Check PRESERVE_FIELDS in router.py or preserve.py.

### Overall: ❌ FAIL

---

## B.28 — Arabic thousands separator

| | |
|---|---|
| **Input** | `١٢٬٥٠٠` |
| **Expected field type** | `share_capital` |
| **Expected language** | `ar` |
| **Expected normalised form** | `12500` |
| **Expected method** | `NUMERIC` |
| **Notes** | U+066C Arabic thousands separator with Arabic-Indic digits |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `share_capital` | `id_no` | ⚠️ mismatch |
| **language** | `ar` | `ar` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `1.36s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `id_no` but expected `share_capital`. The router will process the field as `id_no` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "١٢٬٥٠٠", "field_type": "id_no", "language": "ar"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `PRESERVE` |
| normalised_form | `١٢٬٥٠٠` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `NUMERIC` | `PRESERVE` | ❌ FAIL |
| **normalised_form** | `12500` | `١٢٬٥٠٠` | ❌ FAIL |

> ❌ **Method failure diagnosis:** Field type 'id_no' is in the PRESERVE_FIELDS list but should not be. Check PRESERVE_FIELDS in router.py or preserve.py.

### Overall: ❌ FAIL

---

## B.29 — French space thousands separator

| | |
|---|---|
| **Input** | `12 500` |
| **Expected field type** | `share_capital` |
| **Expected language** | `fr` |
| **Expected normalised form** | `12500` |
| **Expected method** | `NUMERIC` |
| **Notes** | French uses space as thousands separator |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `share_capital` | `total_assets` | ⚠️ mismatch |
| **language** | `fr` | `en` | ⚠️ mismatch |
| **confidence** | — | `0.85` | — |
| **latency** | — | `0.70s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `total_assets` but expected `share_capital`. The router will process the field as `total_assets` which may select the wrong strategy.

> ⚠️ **Classification mismatch on language.** GPT-4o-mini returned `en` but expected `fr`. This may affect strategy selection (e.g. character map handler chosen for wrong language).

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "12 500", "field_type": "total_assets", "language": "en"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `NUMERIC` |
| normalised_form | `12500` |
| confidence | `0.95` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `NUMERIC` | `NUMERIC` | ✅ PASS |
| **normalised_form** | `12500` | `12500` | ✅ PASS |

### Overall: ✅ PASS

---

## B.30 — Russian space thousands separator

| | |
|---|---|
| **Input** | `12 500` |
| **Expected field type** | `share_capital` |
| **Expected language** | `ru` |
| **Expected normalised form** | `12500` |
| **Expected method** | `NUMERIC` |
| **Notes** | Russian uses space as thousands separator |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `share_capital` | `total_assets` | ⚠️ mismatch |
| **language** | `ru` | `en` | ⚠️ mismatch |
| **confidence** | — | `0.85` | — |
| **latency** | — | `0.97s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `total_assets` but expected `share_capital`. The router will process the field as `total_assets` which may select the wrong strategy.

> ⚠️ **Classification mismatch on language.** GPT-4o-mini returned `en` but expected `ru`. This may affect strategy selection (e.g. character map handler chosen for wrong language).

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "12 500", "field_type": "total_assets", "language": "en"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `NUMERIC` |
| normalised_form | `12500` |
| confidence | `0.95` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `NUMERIC` | `NUMERIC` | ✅ PASS |
| **normalised_form** | `12500` | `12500` | ✅ PASS |

### Overall: ✅ PASS

---

## B.31 — Han numerals for amount

| | |
|---|---|
| **Input** | `五千` |
| **Expected field type** | `share_capital` |
| **Expected language** | `ja` |
| **Expected normalised form** | `5000` |
| **Expected method** | `NUMERIC` |
| **Notes** | Han numeral semantic conversion |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `share_capital` | `id_no` | ⚠️ mismatch |
| **language** | `ja` | `zh` | ⚠️ mismatch |
| **confidence** | — | `0.85` | — |
| **latency** | — | `0.73s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `id_no` but expected `share_capital`. The router will process the field as `id_no` which may select the wrong strategy.

> ⚠️ **Classification mismatch on language.** GPT-4o-mini returned `zh` but expected `ja`. This may affect strategy selection (e.g. character map handler chosen for wrong language).

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "五千", "field_type": "id_no", "language": "zh"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `PRESERVE` |
| normalised_form | `五千` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `NUMERIC` | `PRESERVE` | ❌ FAIL |
| **normalised_form** | `5000` | `五千` | ❌ FAIL |

> ❌ **Method failure diagnosis:** Field type 'id_no' is in the PRESERVE_FIELDS list but should not be. Check PRESERVE_FIELDS in router.py or preserve.py.

### Overall: ❌ FAIL

---

## B.32 — European dot thousands separator

| | |
|---|---|
| **Input** | `12.500` |
| **Expected field type** | `share_capital` |
| **Expected language** | `es` |
| **Expected normalised form** | `12500` |
| **Expected method** | `NUMERIC` |
| **Notes** | Spanish/Italian use dot as thousands separator |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `share_capital` | `total_assets` | ⚠️ mismatch |
| **language** | `es` | `en` | ⚠️ mismatch |
| **confidence** | — | `0.85` | — |
| **latency** | — | `0.89s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `total_assets` but expected `share_capital`. The router will process the field as `total_assets` which may select the wrong strategy.

> ⚠️ **Classification mismatch on language.** GPT-4o-mini returned `en` but expected `es`. This may affect strategy selection (e.g. character map handler chosen for wrong language).

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "12.500", "field_type": "total_assets", "language": "en"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `NUMERIC` |
| normalised_form | `12500` |
| confidence | `0.95` |
| review_required | `False` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `NUMERIC` | `NUMERIC` | ✅ PASS |
| **normalised_form** | `12500` | `12500` | ✅ PASS |

### Overall: ✅ PASS

---

## B.33 — UK comma thousands separator

| | |
|---|---|
| **Input** | `12,500` |
| **Expected field type** | `share_capital` |
| **Expected language** | `en` |
| **Expected normalised form** | `12500` |
| **Expected method** | `NUMERIC` |
| **Notes** | UK/US comma thousands separator |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `share_capital` | `total_assets` | ⚠️ mismatch |
| **language** | `en` | `en` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.74s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `total_assets` but expected `share_capital`. The router will process the field as `total_assets` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "12,500", "field_type": "total_assets", "language": "en"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `NUMERIC` |
| normalised_form | `12500` |
| confidence | `0.95` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `NUMERIC` | `NUMERIC` | ✅ PASS |
| **normalised_form** | `12500` | `12500` | ✅ PASS |

### Overall: ✅ PASS

---

## B.34 — Korean comma thousands

| | |
|---|---|
| **Input** | `12,500` |
| **Expected field type** | `share_capital` |
| **Expected language** | `ko` |
| **Expected normalised form** | `12500` |
| **Expected method** | `NUMERIC` |
| **Notes** | Korean uses comma thousands |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `share_capital` | `total_assets` | ⚠️ mismatch |
| **language** | `ko` | `en` | ⚠️ mismatch |
| **confidence** | — | `0.85` | — |
| **latency** | — | `0.92s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `total_assets` but expected `share_capital`. The router will process the field as `total_assets` which may select the wrong strategy.

> ⚠️ **Classification mismatch on language.** GPT-4o-mini returned `en` but expected `ko`. This may affect strategy selection (e.g. character map handler chosen for wrong language).

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "12,500", "field_type": "total_assets", "language": "en"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `NUMERIC` |
| normalised_form | `12500` |
| confidence | `0.95` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `NUMERIC` | `NUMERIC` | ✅ PASS |
| **normalised_form** | `12500` | `12500` | ✅ PASS |

### Overall: ✅ PASS

---

## B.35 — Han numerals in house number

| | |
|---|---|
| **Input** | `八十八` |
| **Expected field type** | `address` |
| **Expected language** | `zh` |
| **Expected normalised form** | `88` |
| **Expected method** | `NUMERIC` |
| **Notes** | Han numeral house number conversion |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `address` | `id_no` | ⚠️ mismatch |
| **language** | `zh` | `zh` | ✅ match |
| **confidence** | — | `0.85` | — |
| **latency** | — | `0.97s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `id_no` but expected `address`. The router will process the field as `id_no` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "八十八", "field_type": "id_no", "language": "zh"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `PRESERVE` |
| normalised_form | `八十八` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.00s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `NUMERIC` | `PRESERVE` | ❌ FAIL |
| **normalised_form** | `88` | `八十八` | ❌ FAIL |

> ❌ **Method failure diagnosis:** Field type 'id_no' is in the PRESERVE_FIELDS list but should not be. Check PRESERVE_FIELDS in router.py or preserve.py.

### Overall: ❌ FAIL

---

## B.36 — Spoken-style Han digits in phone

| | |
|---|---|
| **Input** | `一三八〇〇一三八〇〇〇` |
| **Expected field type** | `phone_number` |
| **Expected language** | `zh` |
| **Expected normalised form** | `13800138000` |
| **Expected method** | `NUMERIC` |
| **Notes** | Chinese spoken digit sequence to ASCII |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `phone_number` | `id_no` | ⚠️ mismatch |
| **language** | `zh` | `zh` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.65s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `id_no` but expected `phone_number`. The router will process the field as `id_no` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "一三八〇〇一三八〇〇〇", "field_type": "id_no", "language": "zh"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `PRESERVE` |
| normalised_form | `一三八〇〇一三八〇〇〇` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `NUMERIC` | `PRESERVE` | ❌ FAIL |
| **normalised_form** | `13800138000` | `一三八〇〇一三八〇〇〇` | ❌ FAIL |

> ❌ **Method failure diagnosis:** Field type 'id_no' is in the PRESERVE_FIELDS list but should not be. Check PRESERVE_FIELDS in router.py or preserve.py.

### Overall: ❌ FAIL

---

## B.37 — Egyptian Arabic phone number with spaces

| | |
|---|---|
| **Input** | `+20 100 123 4567` |
| **Expected field type** | `phone_number` |
| **Expected language** | `ar` |
| **Expected normalised form** | `+201001234567` |
| **Expected method** | `NUMERIC` |
| **Notes** | Spaces removed from phone number |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `phone_number` | `unstructured_text` | ⚠️ mismatch |
| **language** | `ar` | `en` | ⚠️ mismatch |
| **confidence** | — | `0.85` | — |
| **latency** | — | `0.84s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `unstructured_text` but expected `phone_number`. The router will process the field as `unstructured_text` which may select the wrong strategy.

> ⚠️ **Classification mismatch on language.** GPT-4o-mini returned `en` but expected `ar`. This may affect strategy selection (e.g. character map handler chosen for wrong language).

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "+20 100 123 4567", "field_type": "unstructured_text", "language": "en"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CHARACTER_MAP` |
| normalised_form | `+20 100 123 4567` |
| confidence | `0.90` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `NUMERIC` | `CHARACTER_MAP` | ❌ FAIL |
| **normalised_form** | `+201001234567` | `+20 100 123 4567` | ❌ FAIL |

> ❌ **Method failure diagnosis:** Got 'CHARACTER_MAP', expected one of ['NUMERIC']. Check router.py strategy wiring.

### Overall: ❌ FAIL

---

## C.20 — Italian legal form SpA

| | |
|---|---|
| **Input** | `S.p.A.` |
| **Expected field type** | `legal_form` |
| **Expected language** | `it` |
| **Expected normalised form** | `SPA` |
| **Expected method** | `VOCABULARY` |
| **Notes** | Italian Società per Azioni with punctuation variants |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `legal_form` | `legal_form` | ✅ match |
| **language** | `it` | `it` | ✅ match |
| **confidence** | — | `0.85` | — |
| **latency** | — | `0.81s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "S.p.A.", "field_type": "legal_form", "language": "it"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `VOCABULARY` |
| normalised_form | `SPA` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `VOCABULARY` | `VOCABULARY` | ✅ PASS |
| **normalised_form** | `SPA` | `SPA` | ✅ PASS |

### Overall: ✅ PASS

---

## C.21 — French legal form SARL

| | |
|---|---|
| **Input** | `S.A.R.L.` |
| **Expected field type** | `legal_form` |
| **Expected language** | `fr` |
| **Expected normalised form** | `SARL` |
| **Expected method** | `VOCABULARY` |
| **Notes** | French private limited company |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `legal_form` | `legal_form` | ✅ match |
| **language** | `fr` | `fr` | ✅ match |
| **confidence** | — | `0.85` | — |
| **latency** | — | `1.14s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "S.A.R.L.", "field_type": "legal_form", "language": "fr"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CHARACTER_MAP` |
| normalised_form | `S.A.R.L.` |
| confidence | `0.90` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `VOCABULARY` | `CHARACTER_MAP` | ❌ FAIL |
| **normalised_form** | `SARL` | `S.A.R.L.` | ❌ FAIL |

> ❌ **Method failure diagnosis:** Expected VOCABULARY lookup but got CHARACTER_MAP. Check that the lookup table for field_type='legal_form' language='fr' exists in data/lookup_tables/ and that VocabularyLookupService is correctly wired in _try_strategy_c().

### Overall: ❌ FAIL

---

## C.22 — Mexican legal form SAB de CV

| | |
|---|---|
| **Input** | `S.A.B. de C.V.` |
| **Expected field type** | `legal_form` |
| **Expected language** | `es` |
| **Expected normalised form** | `SAB DE CV` |
| **Expected method** | `VOCABULARY` |
| **Notes** | Mexican Sociedad Anónima Bursátil de Capital Variable |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `legal_form` | `company_name` | ⚠️ mismatch |
| **language** | `es` | `es` | ✅ match |
| **confidence** | — | `0.92` | — |
| **latency** | — | `0.81s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `company_name` but expected `legal_form`. The router will process the field as `company_name` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "S.A.B. de C.V.", "field_type": "company_name", "language": "es"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CHARACTER_MAP` |
| normalised_form | `S.A.B. DE C.V.` |
| confidence | `0.90` |
| review_required | `False` |
| allowed_variants | `S.A.B. C.V.` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `VOCABULARY` | `CHARACTER_MAP` | ❌ FAIL |
| **normalised_form** | `SAB DE CV` | `S.A.B. DE C.V.` | ❌ FAIL |

> ❌ **Method failure diagnosis:** Expected VOCABULARY lookup but got CHARACTER_MAP. Check that the lookup table for field_type='company_name' language='es' exists in data/lookup_tables/ and that VocabularyLookupService is correctly wired in _try_strategy_c().

### Overall: ❌ FAIL

---

## C.23 — Korean legal form Jusikhoesa

| | |
|---|---|
| **Input** | `주식회사` |
| **Expected field type** | `legal_form` |
| **Expected language** | `ko` |
| **Expected normalised form** | `CO LTD` |
| **Expected method** | `VOCABULARY` |
| **Notes** | Korean equivalent of KK / joint stock company |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `legal_form` | `legal_form` | ✅ match |
| **language** | `ko` | `ko` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.70s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "주식회사", "field_type": "legal_form", "language": "ko"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `VOCABULARY` |
| normalised_form | `CO LTD` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `VOCABULARY` | `VOCABULARY` | ✅ PASS |
| **normalised_form** | `CO LTD` | `CO LTD` | ✅ PASS |

### Overall: ✅ PASS

---

## C.24 — Arabic legal form limited company

| | |
|---|---|
| **Input** | `شركة محدودة` |
| **Expected field type** | `legal_form` |
| **Expected language** | `ar` |
| **Expected normalised form** | `LTD` |
| **Expected method** | `VOCABULARY` |
| **Notes** | Arabic limited company designation |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `legal_form` | `legal_form` | ✅ match |
| **language** | `ar` | `ar` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `3.98s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "شركة محدودة", "field_type": "legal_form", "language": "ar"}
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
| **normalised_form** | `LTD` | `None` | ❌ FAIL |

> ❌ **Method failure diagnosis:** The strategy for field_type='legal_form' language='ar' returned None or raised NotImplementedError. Check that the strategy module is fully implemented and wired into the router.

### Overall: ❌ FAIL

---

## C.25 — Spanish status in liquidation

| | |
|---|---|
| **Input** | `en liquidación` |
| **Expected field type** | `status` |
| **Expected language** | `es` |
| **Expected normalised form** | `IN_LIQUIDATION` |
| **Expected method** | `VOCABULARY` |
| **Notes** | Spanish liquidation status |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `status` | `status` | ✅ match |
| **language** | `es` | `es` | ✅ match |
| **confidence** | — | `0.92` | — |
| **latency** | — | `1.15s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "en liquidación", "field_type": "status", "language": "es"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `VOCABULARY` |
| normalised_form | `IN_LIQUIDATION` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `VOCABULARY` | `VOCABULARY` | ✅ PASS |
| **normalised_form** | `IN_LIQUIDATION` | `IN_LIQUIDATION` | ✅ PASS |

### Overall: ✅ PASS

---

## C.26 — Japanese role auditor

| | |
|---|---|
| **Input** | `監査役` |
| **Expected field type** | `role` |
| **Expected language** | `ja` |
| **Expected normalised form** | `AUDITOR` |
| **Expected method** | `VOCABULARY` |
| **Notes** | Standard Japanese statutory auditor role |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `role` | `role` | ✅ match |
| **language** | `ja` | `ja` | ✅ match |
| **confidence** | — | `0.92` | — |
| **latency** | — | `0.90s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "監査役", "field_type": "role", "language": "ja"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `VOCABULARY` |
| normalised_form | `AUDITOR` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `VOCABULARY` | `VOCABULARY` | ✅ PASS |
| **normalised_form** | `AUDITOR` | `AUDITOR` | ✅ PASS |

### Overall: ✅ PASS

---

## D.8 — City name in Arabic

| | |
|---|---|
| **Input** | `القاهرة` |
| **Expected field type** | `city` |
| **Expected language** | `ar` |
| **Expected normalised form** | `CAIRO` |
| **Expected method** | `GEOGRAPHIC` |
| **Notes** | Cairo in Arabic |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `city` | `city` | ✅ match |
| **language** | `ar` | `ar` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.81s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "القاهرة", "field_type": "city", "language": "ar"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `GEOGRAPHIC` |
| normalised_form | `CAIRO` |
| confidence | `0.92` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `GEOGRAPHIC` | `GEOGRAPHIC` | ✅ PASS |
| **normalised_form** | `CAIRO` | `CAIRO` | ✅ PASS |

### Overall: ✅ PASS

---

## D.9 — City name in Japanese

| | |
|---|---|
| **Input** | `東京` |
| **Expected field type** | `city` |
| **Expected language** | `ja` |
| **Expected normalised form** | `TOKYO` |
| **Expected method** | `GEOGRAPHIC` |
| **Notes** | Tokyo in Kanji |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `city` | `unstructured_text` | ⚠️ mismatch |
| **language** | `ja` | `ja` | ✅ match |
| **confidence** | — | `0.85` | — |
| **latency** | — | `1.06s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `unstructured_text` but expected `city`. The router will process the field as `unstructured_text` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "東京", "field_type": "unstructured_text", "language": "ja"}
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
| **method** | `GEOGRAPHIC` | `UNRESOLVED` | ❌ FAIL |
| **normalised_form** | `TOKYO` | `None` | ❌ FAIL |

> ❌ **Method failure diagnosis:** GPT-4o-mini classified as 'unstructured_text' instead of 'city'. The router received the wrong field type and could not find a matching strategy.

### Overall: ❌ FAIL

---

## D.10 — City name in Chinese

| | |
|---|---|
| **Input** | `北京` |
| **Expected field type** | `city` |
| **Expected language** | `zh` |
| **Expected normalised form** | `BEIJING` |
| **Expected method** | `GEOGRAPHIC` |
| **Notes** | Beijing in Han |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `city` | `nationality` | ⚠️ mismatch |
| **language** | `zh` | `zh` | ✅ match |
| **confidence** | — | `0.93` | — |
| **latency** | — | `0.80s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `nationality` but expected `city`. The router will process the field as `nationality` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "北京", "field_type": "nationality", "language": "zh"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `GEOGRAPHIC` |
| normalised_form | `CHINA` |
| confidence | `0.88` |
| review_required | `False` |
| latency | `0.02s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `GEOGRAPHIC` | `GEOGRAPHIC` | ✅ PASS |
| **normalised_form** | `BEIJING` | `CHINA` | ❌ FAIL |

> ❌ **Form failure diagnosis:** Got 'CHINA', expected 'BEIJING'. Inspect the strategy module output.

### Overall: ❌ FAIL

---

## D.11 — City name in Korean

| | |
|---|---|
| **Input** | `서울` |
| **Expected field type** | `city` |
| **Expected language** | `ko` |
| **Expected normalised form** | `SEOUL` |
| **Expected method** | `GEOGRAPHIC` |
| **Notes** | Seoul in Hangul |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `city` | `city` | ✅ match |
| **language** | `ko` | `ko` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.85s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "서울", "field_type": "city", "language": "ko"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `GEOGRAPHIC` |
| normalised_form | `SEOUL` |
| confidence | `0.92` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `GEOGRAPHIC` | `GEOGRAPHIC` | ✅ PASS |
| **normalised_form** | `SEOUL` | `SEOUL` | ✅ PASS |

### Overall: ✅ PASS

---

## D.12 — Nationality adjective in Japanese

| | |
|---|---|
| **Input** | `日本人` |
| **Expected field type** | `nationality` |
| **Expected language** | `ja` |
| **Expected normalised form** | `JAPAN` |
| **Expected method** | `GEOGRAPHIC` |
| **Notes** | Adjectival form resolves to country, not adjective |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `nationality` | `nationality` | ✅ match |
| **language** | `ja` | `ja` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.84s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "日本人", "field_type": "nationality", "language": "ja"}
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
| **method** | `GEOGRAPHIC` | `UNRESOLVED` | ❌ FAIL |
| **normalised_form** | `JAPAN` | `None` | ❌ FAIL |

> ❌ **Method failure diagnosis:** The strategy for field_type='nationality' language='ja' returned None or raised NotImplementedError. Check that the strategy module is fully implemented and wired into the router.

### Overall: ❌ FAIL

---

## F.11 — Russian male name with patronymic and ё

| | |
|---|---|
| **Input** | `Алексей Юрьевич Ковалёв` |
| **Expected field type** | `person_name` |
| **Expected language** | `ru` |
| **Expected normalised form** | `ALEKSEI YURYEVICH KOVALEV` |
| **Expected method** | `['TRANSLITERATION', 'TRANSLITERATE']` |
| **Notes** | BGN/PCGN with ё→e, KOVALYOV in variants |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `person_name` | ✅ match |
| **language** | `ru` | `ru` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.70s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Алексей Юрьевич Ковалёв", "field_type": "person_name", "language": "ru"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `TRANSLITERATE` |
| normalised_form | `ALEKSEJ YUREVICH KOVALEV` |
| confidence | `0.90` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `TRANSLITERATION` or `TRANSLITERATE` | `TRANSLITERATE` | ✅ PASS |
| **normalised_form** | `ALEKSEI YURYEVICH KOVALEV` | `ALEKSEJ YUREVICH KOVALEV` | ❌ FAIL |

> ❌ **Form failure diagnosis:** Got 'ALEKSEJ YUREVICH KOVALEV', expected 'ALEKSEI YURYEVICH KOVALEV'. Inspect the strategy module output.

### Overall: ❌ FAIL

---

## F.12 — Russian female name with patronymic

| | |
|---|---|
| **Input** | `Наталья Викторовна Орлова` |
| **Expected field type** | `person_name` |
| **Expected language** | `ru` |
| **Expected normalised form** | `NATALYA VIKTOROVNA ORLOVA` |
| **Expected method** | `['TRANSLITERATION', 'TRANSLITERATE']` |
| **Notes** | Female patronymic; NATALIA in variants |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `full_name` | ⚠️ mismatch |
| **language** | `ru` | `ru` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.79s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `full_name` but expected `person_name`. The router will process the field as `full_name` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Наталья Викторовна Орлова", "field_type": "full_name", "language": "ru"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `TRANSLITERATE` |
| normalised_form | `NATALYA VIKTOROVNA ORLOVA` |
| confidence | `0.90` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `TRANSLITERATION` or `TRANSLITERATE` | `TRANSLITERATE` | ✅ PASS |
| **normalised_form** | `NATALYA VIKTOROVNA ORLOVA` | `NATALYA VIKTOROVNA ORLOVA` | ✅ PASS |

### Overall: ✅ PASS

---

## F.13 — Ukrainian male name distinct from Russian

| | |
|---|---|
| **Input** | `Олександр Іваненко` |
| **Expected field type** | `person_name` |
| **Expected language** | `uk` |
| **Expected normalised form** | `OLEKSANDR IVANENKO` |
| **Expected method** | `['TRANSLITERATION', 'TRANSLITERATE']` |
| **Notes** | Must NOT produce ALEKSANDR — Ukrainian transliteration is distinct |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `person_name` | ✅ match |
| **language** | `uk` | `uk` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.80s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Олександр Іваненко", "field_type": "person_name", "language": "uk"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `TRANSLITERATE` |
| normalised_form | `OLEKSANDR IVANENKO` |
| confidence | `0.70` |
| review_required | `True` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `TRANSLITERATION` or `TRANSLITERATE` | `TRANSLITERATE` | ✅ PASS |
| **normalised_form** | `OLEKSANDR IVANENKO` | `OLEKSANDR IVANENKO` | ✅ PASS |

### Overall: ✅ PASS

---

## F.14 — Ukrainian female with feminine patronymic

| | |
|---|---|
| **Input** | `Ірина Миколаївна Шевченко` |
| **Expected field type** | `person_name` |
| **Expected language** | `uk` |
| **Expected normalised form** | `IRYNA MYKOLAIVNA SHEVCHENKO` |
| **Expected method** | `['TRANSLITERATION', 'TRANSLITERATE']` |
| **Notes** | Ukrainian-specific transliteration |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `full_name` | ⚠️ mismatch |
| **language** | `uk` | `uk` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `1.03s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `full_name` but expected `person_name`. The router will process the field as `full_name` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Ірина Миколаївна Шевченко", "field_type": "full_name", "language": "uk"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `TRANSLITERATE` |
| normalised_form | `IRYNA MYKOLAIVNA SHEVCHENKO` |
| confidence | `0.70` |
| review_required | `True` |
| latency | `0.02s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `TRANSLITERATION` or `TRANSLITERATE` | `TRANSLITERATE` | ✅ PASS |
| **normalised_form** | `IRYNA MYKOLAIVNA SHEVCHENKO` | `IRYNA MYKOLAIVNA SHEVCHENKO` | ✅ PASS |

### Overall: ✅ PASS

---

## F.15 — Russian compound name with two parts

| | |
|---|---|
| **Input** | `Дмитрий Иванов` |
| **Expected field type** | `person_name` |
| **Expected language** | `ru` |
| **Expected normalised form** | `DMITRII IVANOV` |
| **Expected method** | `['TRANSLITERATION', 'TRANSLITERATE']` |
| **Notes** | DMITRY/DMITRIJ in variants |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `person_name` | ✅ match |
| **language** | `ru` | `ru` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `1.18s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Дмитрий Иванов", "field_type": "person_name", "language": "ru"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `TRANSLITERATE` |
| normalised_form | `DMITRIJ IVANOV` |
| confidence | `0.90` |
| review_required | `False` |
| latency | `0.02s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `TRANSLITERATION` or `TRANSLITERATE` | `TRANSLITERATE` | ✅ PASS |
| **normalised_form** | `DMITRII IVANOV` | `DMITRIJ IVANOV` | ❌ FAIL |

> ❌ **Form failure diagnosis:** Got 'DMITRIJ IVANOV', expected 'DMITRII IVANOV'. Inspect the strategy module output.

### Overall: ❌ FAIL

---

## F.16 — Greek compound name

| | |
|---|---|
| **Input** | `Γεώργιος Παπαδόπουλος` |
| **Expected field type** | `person_name` |
| **Expected language** | `el` |
| **Expected normalised form** | `GEORGIOS PAPADOPOULOS` |
| **Expected method** | `['TRANSLITERATION', 'TRANSLITERATE']` |
| **Notes** | Standard Greek romanisation |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `person_name` | ✅ match |
| **language** | `el` | `el` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `1.41s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Γεώργιος Παπαδόπουλος", "field_type": "person_name", "language": "el"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `TRANSLITERATE` |
| normalised_form | `GEORGIOS PAPADOPOULOS` |
| confidence | `0.90` |
| review_required | `False` |
| latency | `0.02s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `TRANSLITERATION` or `TRANSLITERATE` | `TRANSLITERATE` | ✅ PASS |
| **normalised_form** | `GEORGIOS PAPADOPOULOS` | `GEORGIOS PAPADOPOULOS` | ✅ PASS |

### Overall: ✅ PASS

---

## F.17 — Greek name with Ch consonant

| | |
|---|---|
| **Input** | `Χρήστος Βασιλείου` |
| **Expected field type** | `person_name` |
| **Expected language** | `el` |
| **Expected normalised form** | `CHRISTOS VASILEIOU` |
| **Expected method** | `['TRANSLITERATION', 'TRANSLITERATE']` |
| **Notes** | Χ→CH primary, HRISTOS in variants |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `person_name` | ✅ match |
| **language** | `el` | `el` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.67s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Χρήστος Βασιλείου", "field_type": "person_name", "language": "el"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `TRANSLITERATE` |
| normalised_form | `CHRISTOS VASILEIOU` |
| confidence | `0.90` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `TRANSLITERATION` or `TRANSLITERATE` | `TRANSLITERATE` | ✅ PASS |
| **normalised_form** | `CHRISTOS VASILEIOU` | `CHRISTOS VASILEIOU` | ✅ PASS |

### Overall: ✅ PASS

---

## F.18 — Greek name with B→V mapping

| | |
|---|---|
| **Input** | `Βασίλης Νικολάου` |
| **Expected field type** | `person_name` |
| **Expected language** | `el` |
| **Expected normalised form** | `VASILIS NIKOLAOU` |
| **Expected method** | `['TRANSLITERATION', 'TRANSLITERATE']` |
| **Notes** | Modern Greek β→V not B |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `person_name` | ✅ match |
| **language** | `el` | `el` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `1.04s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Βασίλης Νικολάου", "field_type": "person_name", "language": "el"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `TRANSLITERATE` |
| normalised_form | `VASILIS NIKOLAOU` |
| confidence | `0.90` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `TRANSLITERATION` or `TRANSLITERATE` | `TRANSLITERATE` | ✅ PASS |
| **normalised_form** | `VASILIS NIKOLAOU` | `VASILIS NIKOLAOU` | ✅ PASS |

### Overall: ✅ PASS

---

## F.19 — Japanese name with long vowel ou

| | |
|---|---|
| **Input** | `伊藤 恒一` |
| **Expected field type** | `person_name` |
| **Expected language** | `ja` |
| **Expected normalised form** | `ITO KOICHI` |
| **Expected method** | `['TRANSLITERATION', 'TRANSLITERATE']` |
| **Notes** | Hepburn; KOUICHI and KOOICHI in variants |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `person_name` | ✅ match |
| **language** | `ja` | `ja` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.91s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "伊藤 恒一", "field_type": "person_name", "language": "ja"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `TRANSLITERATE` |
| normalised_form | `ITO KOICHI` |
| confidence | `0.70` |
| review_required | `True` |
| allowed_variants | `ITO KOOICHI`, `ITO KOUICHI`, `ITO TSUNEKAZU`, `ITOH KOICHI` |
| latency | `0.02s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `TRANSLITERATION` or `TRANSLITERATE` | `TRANSLITERATE` | ✅ PASS |
| **normalised_form** | `ITO KOICHI` | `ITO KOICHI` | ✅ PASS |

### Overall: ✅ PASS

---

## F.20 — Japanese name with long vowel sho

| | |
|---|---|
| **Input** | `中村 翔` |
| **Expected field type** | `person_name` |
| **Expected language** | `ja` |
| **Expected normalised form** | `NAKAMURA SHO` |
| **Expected method** | `['TRANSLITERATION', 'TRANSLITERATE']` |
| **Notes** | SHOU and SHOO in variants |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `person_name` | ✅ match |
| **language** | `ja` | `ja` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.90s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "中村 翔", "field_type": "person_name", "language": "ja"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `TRANSLITERATE` |
| normalised_form | `NAKAMURA SHO` |
| confidence | `0.70` |
| review_required | `True` |
| allowed_variants | `NAKAMURA KAKERU` |
| latency | `0.02s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `TRANSLITERATION` or `TRANSLITERATE` | `TRANSLITERATE` | ✅ PASS |
| **normalised_form** | `NAKAMURA SHO` | `NAKAMURA SHO` | ✅ PASS |

### Overall: ✅ PASS

---

## F.21 — Japanese full surname-first name

| | |
|---|---|
| **Input** | `山田 太郎` |
| **Expected field type** | `person_name` |
| **Expected language** | `ja` |
| **Expected normalised form** | `YAMADA TARO` |
| **Expected method** | `['TRANSLITERATION', 'TRANSLITERATE']` |
| **Notes** | Surname-first primary; TARO YAMADA in variants |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `person_name` | ✅ match |
| **language** | `ja` | `ja` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.73s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "山田 太郎", "field_type": "person_name", "language": "ja"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `TRANSLITERATE` |
| normalised_form | `YAMADA TARO` |
| confidence | `0.70` |
| review_required | `True` |
| allowed_variants | `YAMADA TAROU` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `TRANSLITERATION` or `TRANSLITERATE` | `TRANSLITERATE` | ✅ PASS |
| **normalised_form** | `YAMADA TARO` | `YAMADA TARO` | ✅ PASS |

### Overall: ✅ PASS

---

## F.22 — Japanese katakana name

| | |
|---|---|
| **Input** | `タナカ ケン` |
| **Expected field type** | `person_name` |
| **Expected language** | `ja` |
| **Expected normalised form** | `TANAKA KEN` |
| **Expected method** | `['TRANSLITERATION', 'TRANSLITERATE']` |
| **Notes** | Katakana straightforward Hepburn |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `person_name` | ✅ match |
| **language** | `ja` | `ja` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.93s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "タナカ ケン", "field_type": "person_name", "language": "ja"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `TRANSLITERATE` |
| normalised_form | `TANAKA KEN` |
| confidence | `0.90` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `TRANSLITERATION` or `TRANSLITERATE` | `TRANSLITERATE` | ✅ PASS |
| **normalised_form** | `TANAKA KEN` | `TANAKA KEN` | ✅ PASS |

### Overall: ✅ PASS

---

## F.23 — Chinese mainland Simplified

| | |
|---|---|
| **Input** | `张伟` |
| **Expected field type** | `person_name` |
| **Expected language** | `zh` |
| **Expected normalised form** | `ZHANG WEI` |
| **Expected method** | `['TRANSLITERATION', 'TRANSLITERATE']` |
| **Notes** | Standard Pinyin; very common name |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `person_name` | ✅ match |
| **language** | `zh` | `zh` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `1.05s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "张伟", "field_type": "person_name", "language": "zh"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `TRANSLITERATE` |
| normalised_form | `ZHANG WEI` |
| confidence | `0.70` |
| review_required | `True` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `TRANSLITERATION` or `TRANSLITERATE` | `TRANSLITERATE` | ✅ PASS |
| **normalised_form** | `ZHANG WEI` | `ZHANG WEI` | ✅ PASS |

### Overall: ✅ PASS

---

## F.24 — Chinese Taiwan Traditional

| | |
|---|---|
| **Input** | `陳志強` |
| **Expected field type** | `person_name` |
| **Expected language** | `zh` |
| **Expected normalised form** | `CHEN ZHIQIANG` |
| **Expected method** | `['TRANSLITERATION', 'TRANSLITERATE']` |
| **Notes** | Pinyin primary; Wade-Giles CHEN CHIH-CHIANG in variants |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `person_name` | ✅ match |
| **language** | `zh` | `zh` | ✅ match |
| **confidence** | — | `0.88` | — |
| **latency** | — | `4.64s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "陳志強", "field_type": "person_name", "language": "zh"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `TRANSLITERATE` |
| normalised_form | `CHEN ZHIQIANG` |
| confidence | `0.70` |
| review_required | `True` |
| allowed_variants | `CHAN ZHIQIANG` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `TRANSLITERATION` or `TRANSLITERATE` | `TRANSLITERATE` | ✅ PASS |
| **normalised_form** | `CHEN ZHIQIANG` | `CHEN ZHIQIANG` | ✅ PASS |

### Overall: ✅ PASS

---

## F.25 — Chinese short two-character name

| | |
|---|---|
| **Input** | `李伟` |
| **Expected field type** | `person_name` |
| **Expected language** | `zh` |
| **Expected normalised form** | `LI WEI` |
| **Expected method** | `['TRANSLITERATION', 'TRANSLITERATE']` |
| **Notes** | Short ambiguous name; surname-first |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `person_name` | ✅ match |
| **language** | `zh` | `zh` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `1.32s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "李伟", "field_type": "person_name", "language": "zh"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `TRANSLITERATE` |
| normalised_form | `LI WEI` |
| confidence | `0.70` |
| review_required | `True` |
| allowed_variants | `LEE WEI` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `TRANSLITERATION` or `TRANSLITERATE` | `TRANSLITERATE` | ✅ PASS |
| **normalised_form** | `LI WEI` | `LI WEI` | ✅ PASS |

### Overall: ✅ PASS

---

## F.26 — Korean surname Bak/Park variant family

| | |
|---|---|
| **Input** | `박지훈` |
| **Expected field type** | `person_name` |
| **Expected language** | `ko` |
| **Expected normalised form** | `BAK JIHUN` |
| **Expected method** | `['TRANSLITERATION', 'TRANSLITERATE']` |
| **Notes** | RR primary; PARK and PAK must appear in variants |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `person_name` | ✅ match |
| **language** | `ko` | `ko` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.81s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "박지훈", "field_type": "person_name", "language": "ko"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `TRANSLITERATE` |
| normalised_form | `BAK JIHUN` |
| confidence | `0.70` |
| review_required | `True` |
| allowed_variants | `JIHUN BAK`, `JIHUN PAK`, `JIHUN PARK`, `PAK JIHUN`, `PARK JIHUN` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `TRANSLITERATION` or `TRANSLITERATE` | `TRANSLITERATE` | ✅ PASS |
| **normalised_form** | `BAK JIHUN` | `BAK JIHUN` | ✅ PASS |

### Overall: ✅ PASS

---

## F.27 — Korean surname Choi/Choe variant family

| | |
|---|---|
| **Input** | `최수빈` |
| **Expected field type** | `person_name` |
| **Expected language** | `ko` |
| **Expected normalised form** | `CHOI SUBIN` |
| **Expected method** | `['TRANSLITERATION', 'TRANSLITERATE']` |
| **Notes** | CHOE in variants per RR |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `person_name` | ✅ match |
| **language** | `ko` | `ko` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.81s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "최수빈", "field_type": "person_name", "language": "ko"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `TRANSLITERATE` |
| normalised_form | `CHOE SUBIN` |
| confidence | `0.70` |
| review_required | `True` |
| allowed_variants | `CH'OE SUBIN`, `CHOI SUBIN`, `SUBIN CH'OE`, `SUBIN CHOE`, `SUBIN CHOI` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `TRANSLITERATION` or `TRANSLITERATE` | `TRANSLITERATE` | ✅ PASS |
| **normalised_form** | `CHOI SUBIN` | `CHOE SUBIN` | ❌ FAIL |

> ❌ **Form failure diagnosis:** Got 'CHOE SUBIN', expected 'CHOI SUBIN'. Inspect the strategy module output.

### Overall: ❌ FAIL

---

## F.28 — Korean surname Jeong/Jung/Chung family

| | |
|---|---|
| **Input** | `정하늘` |
| **Expected field type** | `person_name` |
| **Expected language** | `ko` |
| **Expected normalised form** | `JEONG HANEUL` |
| **Expected method** | `['TRANSLITERATION', 'TRANSLITERATE']` |
| **Notes** | JUNG and CHUNG must appear in variants |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `person_name` | ✅ match |
| **language** | `ko` | `ko` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.83s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "정하늘", "field_type": "person_name", "language": "ko"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `TRANSLITERATE` |
| normalised_form | `JEONG HANEUL` |
| confidence | `0.70` |
| review_required | `True` |
| allowed_variants | `CHUNG HANEUL`, `CHŎNG HANEUL`, `HANEUL CHUNG`, `HANEUL CHŎNG`, `HANEUL JEONG`, `HANEUL JUNG`, `JUNG HANEUL` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `TRANSLITERATION` or `TRANSLITERATE` | `TRANSLITERATE` | ✅ PASS |
| **normalised_form** | `JEONG HANEUL` | `JEONG HANEUL` | ✅ PASS |

### Overall: ✅ PASS

---

## F.29 — Korean surname Lee/Yi/Rhee family

| | |
|---|---|
| **Input** | `이서연` |
| **Expected field type** | `person_name` |
| **Expected language** | `ko` |
| **Expected normalised form** | `LEE SEOYEON` |
| **Expected method** | `['TRANSLITERATION', 'TRANSLITERATE']` |
| **Notes** | YI, RHEE, RI in variants — calcified family-preference spellings |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `person_name` | ✅ match |
| **language** | `ko` | `ko` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.64s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "이서연", "field_type": "person_name", "language": "ko"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `TRANSLITERATE` |
| normalised_form | `I SEOYEON` |
| confidence | `0.70` |
| review_required | `True` |
| allowed_variants | `LEE SEOYEON`, `RHEE SEOYEON`, `RHIE SEOYEON`, `RI SEOYEON`, `SEOYEON I`, `SEOYEON LEE`, `SEOYEON RHEE`, `SEOYEON RHIE`, `SEOYEON RI`, `SEOYEON YI`, `YI SEOYEON` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `TRANSLITERATION` or `TRANSLITERATE` | `TRANSLITERATE` | ✅ PASS |
| **normalised_form** | `LEE SEOYEON` | `I SEOYEON` | ❌ FAIL |

> ❌ **Form failure diagnosis:** Got 'I SEOYEON', expected 'LEE SEOYEON'. Inspect the strategy module output.

### Overall: ❌ FAIL

---

## F.30 — Korean surname Ryu/Yoo/Lyu family

| | |
|---|---|
| **Input** | `류민석` |
| **Expected field type** | `person_name` |
| **Expected language** | `ko` |
| **Expected normalised form** | `RYU MINSEOK` |
| **Expected method** | `['TRANSLITERATION', 'TRANSLITERATE']` |
| **Notes** | YOO and LYU in variants |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `person_name` | ✅ match |
| **language** | `ko` | `ko` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.74s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "류민석", "field_type": "person_name", "language": "ko"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `TRANSLITERATE` |
| normalised_form | `RYU MINSEOK` |
| confidence | `0.70` |
| review_required | `True` |
| allowed_variants | `LYU MINSEOK`, `MINSEOK LYU`, `MINSEOK RYU`, `MINSEOK YOO`, `MINSEOK YU`, `YOO MINSEOK`, `YU MINSEOK` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `TRANSLITERATION` or `TRANSLITERATE` | `TRANSLITERATE` | ✅ PASS |
| **normalised_form** | `RYU MINSEOK` | `RYU MINSEOK` | ✅ PASS |

### Overall: ✅ PASS

---

## G.11 — Spanish accented name

| | |
|---|---|
| **Input** | `José Luis García` |
| **Expected field type** | `person_name` |
| **Expected language** | `es` |
| **Expected normalised form** | `JOSE LUIS GARCIA` |
| **Expected method** | `CHARACTER_MAP` |
| **Notes** | Accents stripped per ICAO 9303 |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `person_name` | ✅ match |
| **language** | `es` | `es` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.96s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "José Luis García", "field_type": "person_name", "language": "es"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CHARACTER_MAP` |
| normalised_form | `JOSE LUIS GARCIA` |
| confidence | `0.90` |
| review_required | `False` |
| latency | `0.02s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CHARACTER_MAP` | `CHARACTER_MAP` | ✅ PASS |
| **normalised_form** | `JOSE LUIS GARCIA` | `JOSE LUIS GARCIA` | ✅ PASS |

### Overall: ✅ PASS

---

## G.12 — French accent é

| | |
|---|---|
| **Input** | `Hélène Masson` |
| **Expected field type** | `person_name` |
| **Expected language** | `fr` |
| **Expected normalised form** | `HELENE MASSON` |
| **Expected method** | `CHARACTER_MAP` |
| **Notes** | é→E |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `person_name` | ✅ match |
| **language** | `fr` | `fr` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.95s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Hélène Masson", "field_type": "person_name", "language": "fr"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CHARACTER_MAP` |
| normalised_form | `HELENE MASSON` |
| confidence | `0.90` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CHARACTER_MAP` | `CHARACTER_MAP` | ✅ PASS |
| **normalised_form** | `HELENE MASSON` | `HELENE MASSON` | ✅ PASS |

### Overall: ✅ PASS

---

## G.13 — French cedilla ç

| | |
|---|---|
| **Input** | `François Leclerc` |
| **Expected field type** | `person_name` |
| **Expected language** | `fr` |
| **Expected normalised form** | `FRANCOIS LECLERC` |
| **Expected method** | `CHARACTER_MAP` |
| **Notes** | ç→C |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `person_name` | ✅ match |
| **language** | `fr` | `fr` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.70s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "François Leclerc", "field_type": "person_name", "language": "fr"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CHARACTER_MAP` |
| normalised_form | `FRANCOIS LECLERC` |
| confidence | `0.90` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CHARACTER_MAP` | `CHARACTER_MAP` | ✅ PASS |
| **normalised_form** | `FRANCOIS LECLERC` | `FRANCOIS LECLERC` | ✅ PASS |

### Overall: ✅ PASS

---

## G.14 — Italian accent ò

| | |
|---|---|
| **Input** | `Niccolò Bianchi` |
| **Expected field type** | `person_name` |
| **Expected language** | `it` |
| **Expected normalised form** | `NICCOLO BIANCHI` |
| **Expected method** | `CHARACTER_MAP` |
| **Notes** | ò→O |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `person_name` | ✅ match |
| **language** | `it` | `it` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `1.11s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Niccolò Bianchi", "field_type": "person_name", "language": "it"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CHARACTER_MAP` |
| normalised_form | `NICCOLO BIANCHI` |
| confidence | `0.90` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CHARACTER_MAP` | `CHARACTER_MAP` | ✅ PASS |
| **normalised_form** | `NICCOLO BIANCHI` | `NICCOLO BIANCHI` | ✅ PASS |

### Overall: ✅ PASS

---

## G.15 — German umlaut ö in surname

| | |
|---|---|
| **Input** | `Schröder` |
| **Expected field type** | `person_name` |
| **Expected language** | `de` |
| **Expected normalised form** | `SCHRODER` |
| **Expected method** | `CHARACTER_MAP` |
| **Notes** | ö→O primary, SCHROEDER in variants |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `person_name` | `person_name` | ✅ match |
| **language** | `de` | `de` | ✅ match |
| **confidence** | — | `0.92` | — |
| **latency** | — | `1.13s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Schröder", "field_type": "person_name", "language": "de"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CHARACTER_MAP` |
| normalised_form | `SCHROEDER` |
| confidence | `0.90` |
| review_required | `False` |
| allowed_variants | `SCHRODER` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `CHARACTER_MAP` | `CHARACTER_MAP` | ✅ PASS |
| **normalised_form** | `SCHRODER` | `SCHROEDER` | ❌ FAIL |

> ❌ **Form failure diagnosis:** Character map produced 'SCHROEDER' instead of 'SCHRODER'. Check that the correct map (expansion vs drop) is applied as primary and that all characters in 'Schröder' are in the map.

### Overall: ❌ FAIL

---

## E.4 — Japanese company with KK suffix

| | |
|---|---|
| **Input** | `三菱商事株式会社` |
| **Expected field type** | `company_name` |
| **Expected language** | `ja` |
| **Expected normalised form** | `MITSUBISHI SHOJI KK` |
| **Expected method** | `['VOCABULARY', 'COMPOSITION']` |
| **Notes** | Suffix 株式会社→KK extracted, residual 三菱商事 transliterated |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `company_name` | `company_name` | ✅ match |
| **language** | `ja` | `zh` | ⚠️ mismatch |
| **confidence** | — | `0.95` | — |
| **latency** | — | `1.40s` | — |

> ⚠️ **Classification mismatch on language.** GPT-4o-mini returned `zh` but expected `ja`. This may affect strategy selection (e.g. character map handler chosen for wrong language).

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "三菱商事株式会社", "field_type": "company_name", "language": "zh"}
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
| **method** | `VOCABULARY` or `COMPOSITION` | `VOCABULARY` | ✅ PASS |
| **normalised_form** | `MITSUBISHI SHOJI KK` | `KK` | ❌ FAIL |

> ❌ **Form failure diagnosis:** Vocabulary lookup returned 'KK' instead of 'MITSUBISHI SHOJI KK'. Check the JSON lookup table entry for '三菱商事株式会社'.

### Overall: ❌ FAIL

---

## E.5 — Korean company with Jusikhoesa suffix

| | |
|---|---|
| **Input** | `삼성전자 주식회사` |
| **Expected field type** | `company_name` |
| **Expected language** | `ko` |
| **Expected normalised form** | `SAMSUNG ELECTRONICS CO LTD` |
| **Expected method** | `['VOCABULARY', 'COMPOSITION']` |
| **Notes** | Brand override applies (Samsung Electronics, not Samseong Jeonja) |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `company_name` | `company_name` | ✅ match |
| **language** | `ko` | `ko` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `1.11s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "삼성전자 주식회사", "field_type": "company_name", "language": "ko"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `VOCABULARY` |
| normalised_form | `CO LTD` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `VOCABULARY` or `COMPOSITION` | `VOCABULARY` | ✅ PASS |
| **normalised_form** | `SAMSUNG ELECTRONICS CO LTD` | `CO LTD` | ❌ FAIL |

> ❌ **Form failure diagnosis:** Vocabulary lookup returned 'CO LTD' instead of 'SAMSUNG ELECTRONICS CO LTD'. Check the JSON lookup table entry for '삼성전자 주식회사'.

### Overall: ❌ FAIL

---

## E.6 — Greek company with Α.Ε. suffix

| | |
|---|---|
| **Input** | `Εθνική Τράπεζα της Ελλάδος Α.Ε.` |
| **Expected field type** | `company_name` |
| **Expected language** | `el` |
| **Expected normalised form** | `NATIONAL BANK OF GREECE SA` |
| **Expected method** | `['VOCABULARY', 'COMPOSITION']` |
| **Notes** | Suffix Α.Ε.→SA; established English brand |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `company_name` | `company_name` | ✅ match |
| **language** | `el` | `el` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.92s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Εθνική Τράπεζα της Ελλάδος Α.Ε.", "field_type": "company_name", "language": "el"}
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
| **method** | `VOCABULARY` or `COMPOSITION` | `VOCABULARY` | ✅ PASS |
| **normalised_form** | `NATIONAL BANK OF GREECE SA` | `SA` | ❌ FAIL |

> ❌ **Form failure diagnosis:** Vocabulary lookup returned 'SA' instead of 'NATIONAL BANK OF GREECE SA'. Check the JSON lookup table entry for 'Εθνική Τράπεζα της Ελλάδος Α.Ε.'.

### Overall: ❌ FAIL

---

## E.7 — Russian company with PAO prefix (not suffix)

| | |
|---|---|
| **Input** | `ПАО Газпром` |
| **Expected field type** | `company_name` |
| **Expected language** | `ru` |
| **Expected normalised form** | `GAZPROM PJSC` |
| **Expected method** | `['VOCABULARY', 'COMPOSITION']` |
| **Notes** | Legal form sits at FRONT in Russian — extraction must scan leading tokens too |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `company_name` | `company_name` | ✅ match |
| **language** | `ru` | `ru` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.93s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "ПАО Газпром", "field_type": "company_name", "language": "ru"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `TRANSLITERATE` |
| normalised_form | `PAO GAZPROM` |
| confidence | `0.90` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `VOCABULARY` or `COMPOSITION` | `TRANSLITERATE` | ❌ FAIL |
| **normalised_form** | `GAZPROM PJSC` | `PAO GAZPROM` | ❌ FAIL |

> ❌ **Method failure diagnosis:** Expected VOCABULARY lookup but got TRANSLITERATE. Check that the lookup table for field_type='company_name' language='ru' exists in data/lookup_tables/ and that VocabularyLookupService is correctly wired in _try_strategy_c().

### Overall: ❌ FAIL

---

## E.8 — Arabic company with sharika prefix

| | |
|---|---|
| **Input** | `شركة النور للتجارة المحدودة` |
| **Expected field type** | `company_name` |
| **Expected language** | `ar` |
| **Expected normalised form** | `AL NOOR TRADING CO LTD` |
| **Expected method** | `['VOCABULARY', 'COMPOSITION']` |
| **Notes** | شركة prefix and المحدودة suffix; mid-name descriptors |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `company_name` | `company_name` | ✅ match |
| **language** | `ar` | `ar` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.98s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "شركة النور للتجارة المحدودة", "field_type": "company_name", "language": "ar"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `TRANSLITERATE` |
| normalised_form | `SHRKH AL- NWR LLTJARH AL- MHDWDH` |
| confidence | `0.70` |
| review_required | `True` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `VOCABULARY` or `COMPOSITION` | `TRANSLITERATE` | ❌ FAIL |
| **normalised_form** | `AL NOOR TRADING CO LTD` | `SHRKH AL- NWR LLTJARH AL- MHDWDH` | ❌ FAIL |

> ❌ **Method failure diagnosis:** Expected VOCABULARY lookup but got TRANSLITERATE. Check that the lookup table for field_type='company_name' language='ar' exists in data/lookup_tables/ and that VocabularyLookupService is correctly wired in _try_strategy_c().

### Overall: ❌ FAIL

---

## E.9 — Mexican company with multi-word legal form

| | |
|---|---|
| **Input** | `Grupo Bimbo S.A.B. de C.V.` |
| **Expected field type** | `company_name` |
| **Expected language** | `es` |
| **Expected normalised form** | `GRUPO BIMBO SAB DE CV` |
| **Expected method** | `['VOCABULARY', 'COMPOSITION']` |
| **Notes** | Multi-word legal form S.A.B. de C.V. must be extracted as a unit |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `company_name` | `company_name` | ✅ match |
| **language** | `es` | `es` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `1.12s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Grupo Bimbo S.A.B. de C.V.", "field_type": "company_name", "language": "es"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CHARACTER_MAP` |
| normalised_form | `GRUPO BIMBO S.A.B. DE C.V.` |
| confidence | `0.90` |
| review_required | `False` |
| allowed_variants | `GRUPO BIMBO S.A.B. C.V.` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `VOCABULARY` or `COMPOSITION` | `CHARACTER_MAP` | ❌ FAIL |
| **normalised_form** | `GRUPO BIMBO SAB DE CV` | `GRUPO BIMBO S.A.B. DE C.V.` | ❌ FAIL |

> ❌ **Method failure diagnosis:** Expected VOCABULARY lookup but got CHARACTER_MAP. Check that the lookup table for field_type='company_name' language='es' exists in data/lookup_tables/ and that VocabularyLookupService is correctly wired in _try_strategy_c().

### Overall: ❌ FAIL

---

## E.10 — Japanese brand-name override

| | |
|---|---|
| **Input** | `日本電信電話株式会社` |
| **Expected field type** | `company_name` |
| **Expected language** | `ja` |
| **Expected normalised form** | `NTT CORPORATION` |
| **Expected method** | `['VOCABULARY', 'COMPOSITION']` |
| **Notes** | Established English brand differs from literal transliteration |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `company_name` | `company_name` | ✅ match |
| **language** | `ja` | `ja` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `1.18s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "日本電信電話株式会社", "field_type": "company_name", "language": "ja"}
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
| **method** | `VOCABULARY` or `COMPOSITION` | `VOCABULARY` | ✅ PASS |
| **normalised_form** | `NTT CORPORATION` | `KK` | ❌ FAIL |

> ❌ **Form failure diagnosis:** Vocabulary lookup returned 'KK' instead of 'NTT CORPORATION'. Check the JSON lookup table entry for '日本電信電話株式会社'.

### Overall: ❌ FAIL

---

## E.11 — Italian company with SpA suffix

| | |
|---|---|
| **Input** | `Ferrari S.p.A.` |
| **Expected field type** | `company_name` |
| **Expected language** | `it` |
| **Expected normalised form** | `FERRARI SPA` |
| **Expected method** | `['VOCABULARY', 'COMPOSITION']` |
| **Notes** | Suffix S.p.A.→SPA; residual Ferrari preserved |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `company_name` | `company_name` | ✅ match |
| **language** | `it` | `it` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.91s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Ferrari S.p.A.", "field_type": "company_name", "language": "it"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `VOCABULARY` |
| normalised_form | `SPA` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `VOCABULARY` or `COMPOSITION` | `VOCABULARY` | ✅ PASS |
| **normalised_form** | `FERRARI SPA` | `SPA` | ❌ FAIL |

> ❌ **Form failure diagnosis:** Vocabulary lookup returned 'SPA' instead of 'FERRARI SPA'. Check the JSON lookup table entry for 'Ferrari S.p.A.'.

### Overall: ❌ FAIL

---

## H.1 — Russian alias explanatory text

| | |
|---|---|
| **Input** | `Александр по прозвищу Саша` |
| **Expected field type** | `alias` |
| **Expected language** | `ru` |
| **Expected normalised form** | `ALEXANDER NICKNAMED SASHA` |
| **Expected method** | `NMT` |
| **Notes** | TRANSLATE_ANALYST — alias narrative not for screening match |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `alias` | `alias` | ✅ match |
| **language** | `ru` | `ru` | ✅ match |
| **confidence** | — | `0.85` | — |
| **latency** | — | `1.12s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Александр по прозвищу Саша", "field_type": "alias", "language": "ru"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `TRANSLITERATE` |
| normalised_form | `ALEKSANDR PO PROZVISHCHU SASHA` |
| confidence | `0.90` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `NMT` | `TRANSLITERATE` | ❌ FAIL |
| **normalised_form** | `ALEXANDER NICKNAMED SASHA` | `ALEKSANDR PO PROZVISHCHU SASHA` | ❌ FAIL |

> ❌ **Method failure diagnosis:** Got 'TRANSLITERATE', expected one of ['NMT']. Check router.py strategy wiring.

### Overall: ❌ FAIL

---

## H.2 — Chinese alias 又名

| | |
|---|---|
| **Input** | `王强又名王小强` |
| **Expected field type** | `alias` |
| **Expected language** | `zh` |
| **Expected normalised form** | `WANG QIANG ALSO KNOWN AS WANG XIAOQIANG` |
| **Expected method** | `NMT` |
| **Notes** | Chinese alias connector 又名 |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `alias` | `alias` | ✅ match |
| **language** | `zh` | `zh` | ✅ match |
| **confidence** | — | `0.88` | — |
| **latency** | — | `0.94s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "王强又名王小强", "field_type": "alias", "language": "zh"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `TRANSLITERATE` |
| normalised_form | `WANG QIANG YOU MING WANG XIAO QIANG` |
| confidence | `0.70` |
| review_required | `True` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `NMT` | `TRANSLITERATE` | ❌ FAIL |
| **normalised_form** | `WANG QIANG ALSO KNOWN AS WANG XIAOQIANG` | `WANG QIANG YOU MING WANG XIAO QIANG` | ❌ FAIL |

> ❌ **Method failure diagnosis:** Got 'TRANSLITERATE', expected one of ['NMT']. Check router.py strategy wiring.

### Overall: ❌ FAIL

---

## H.3 — Greek alias γνωστός ως

| | |
|---|---|
| **Input** | `γνωστός ως Νίκος` |
| **Expected field type** | `alias` |
| **Expected language** | `el` |
| **Expected normalised form** | `KNOWN AS NIKOS` |
| **Expected method** | `NMT` |
| **Notes** | Greek alias narrative phrase |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `alias` | `alias` | ✅ match |
| **language** | `el` | `el` | ✅ match |
| **confidence** | — | `0.92` | — |
| **latency** | — | `0.94s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "γνωστός ως Νίκος", "field_type": "alias", "language": "el"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `TRANSLITERATE` |
| normalised_form | `GNOSTOS OS NIKOS` |
| confidence | `0.90` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `NMT` | `TRANSLITERATE` | ❌ FAIL |
| **normalised_form** | `KNOWN AS NIKOS` | `GNOSTOS OS NIKOS` | ❌ FAIL |

> ❌ **Method failure diagnosis:** Got 'TRANSLITERATE', expected one of ['NMT']. Check router.py strategy wiring.

### Overall: ❌ FAIL

---

## H.4 — English alias 'also known as'

| | |
|---|---|
| **Input** | `John Michael Smith also known as Johnny Smith` |
| **Expected field type** | `alias` |
| **Expected language** | `en` |
| **Expected normalised form** | `JOHN MICHAEL SMITH ALSO KNOWN AS JOHNNY SMITH` |
| **Expected method** | `NMT` |
| **Notes** | Already English but flagged as prose; preserve casing pattern |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `alias` | `full_name` | ⚠️ mismatch |
| **language** | `en` | `en` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `1.11s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `full_name` but expected `alias`. The router will process the field as `full_name` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "John Michael Smith also known as Johnny Smith", "field_type": "full_name", "language": "en"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CHARACTER_MAP` |
| normalised_form | `JOHN MICHAEL SMITH ALSO KNOWN AS JOHNNY SMITH` |
| confidence | `0.90` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `NMT` | `CHARACTER_MAP` | ❌ FAIL |
| **normalised_form** | `JOHN MICHAEL SMITH ALSO KNOWN AS JOHNNY SMITH` | `JOHN MICHAEL SMITH ALSO KNOWN AS JOHNNY SMITH` | ✅ PASS |

> ❌ **Method failure diagnosis:** Got 'CHARACTER_MAP', expected one of ['NMT']. Check router.py strategy wiring.

### Overall: ❌ FAIL

---

## H.5 — French alias 'dit'

| | |
|---|---|
| **Input** | `Pierre-Henri Lefèvre dit Le Vieux` |
| **Expected field type** | `alias` |
| **Expected language** | `fr` |
| **Expected normalised form** | `PIERRE-HENRI LEFEVRE KNOWN AS LE VIEUX` |
| **Expected method** | `NMT` |
| **Notes** | French dit → 'known as'; accents stripped |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `alias` | `person_name` | ⚠️ mismatch |
| **language** | `fr` | `fr` | ✅ match |
| **confidence** | — | `0.92` | — |
| **latency** | — | `1.68s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `person_name` but expected `alias`. The router will process the field as `person_name` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Pierre-Henri Lefèvre dit Le Vieux", "field_type": "person_name", "language": "fr"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CHARACTER_MAP` |
| normalised_form | `PIERRE-HENRI LEFEVRE DIT LE VIEUX` |
| confidence | `0.90` |
| review_required | `False` |
| allowed_variants | `PIERRE HENRI LEFEVRE DIT LE VIEUX` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `NMT` | `CHARACTER_MAP` | ❌ FAIL |
| **normalised_form** | `PIERRE-HENRI LEFEVRE KNOWN AS LE VIEUX` | `PIERRE-HENRI LEFEVRE DIT LE VIEUX` | ❌ FAIL |

> ❌ **Method failure diagnosis:** Got 'CHARACTER_MAP', expected one of ['NMT']. Check router.py strategy wiring.

### Overall: ❌ FAIL

---

## H.6 — Italian alias 'detto'

| | |
|---|---|
| **Input** | `Mario De Luca detto Il Professore` |
| **Expected field type** | `alias` |
| **Expected language** | `it` |
| **Expected normalised form** | `MARIO DE LUCA KNOWN AS IL PROFESSORE` |
| **Expected method** | `NMT` |
| **Notes** | Italian detto → 'known as' |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `alias` | `alias` | ✅ match |
| **language** | `it` | `it` | ✅ match |
| **confidence** | — | `0.92` | — |
| **latency** | — | `0.64s` | — |

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Mario De Luca detto Il Professore", "field_type": "alias", "language": "it"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CHARACTER_MAP` |
| normalised_form | `MARIO DE LUCA DETTO IL PROFESSORE` |
| confidence | `0.90` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `NMT` | `CHARACTER_MAP` | ❌ FAIL |
| **normalised_form** | `MARIO DE LUCA KNOWN AS IL PROFESSORE` | `MARIO DE LUCA DETTO IL PROFESSORE` | ❌ FAIL |

> ❌ **Method failure diagnosis:** Got 'CHARACTER_MAP', expected one of ['NMT']. Check router.py strategy wiring.

### Overall: ❌ FAIL

---

## H.7 — Arabic invoice prose with date and amount

| | |
|---|---|
| **Input** | `تاريخ الاستحقاق ٠٥/٠٩/٢٠٢٦ والمبلغ ١٢٬٥٠٠ ريال` |
| **Expected field type** | `free_text` |
| **Expected language** | `ar` |
| **Expected normalised form** | `DUE DATE 2026-09-05 AMOUNT 12500 QAR` |
| **Expected method** | `NMT` |
| **Notes** | Arabic invoice line; date+amount extracted and normalised |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `free_text` | `expiry_date` | ⚠️ mismatch |
| **language** | `ar` | `ar` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `0.80s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `expiry_date` but expected `free_text`. The router will process the field as `expiry_date` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "تاريخ الاستحقاق ٠٥/٠٩/٢٠٢٦ والمبلغ ١٢٬٥٠٠ ريال", "field_type": "expiry_date", "language": "ar"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CALENDAR` |
| normalised_form | `تاريخ الاستحقاق 05/09/2026 والمبلغ 12٬500 ريال` |
| confidence | `0.95` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `NMT` | `CALENDAR` | ❌ FAIL |
| **normalised_form** | `DUE DATE 2026-09-05 AMOUNT 12500 QAR` | `تاريخ الاستحقاق 05/09/2026 والمبلغ 12٬500 ريال` | ❌ FAIL |

> ❌ **Method failure diagnosis:** Got 'CALENDAR', expected one of ['NMT']. Check router.py strategy wiring.

### Overall: ❌ FAIL

---

## H.8 — Japanese invoice prose with Kanji numerals

| | |
|---|---|
| **Input** | `支払期限は二〇二六年九月五日、金額は五千円です。` |
| **Expected field type** | `free_text` |
| **Expected language** | `ja` |
| **Expected normalised form** | `DUE DATE 2026-09-05 AMOUNT 5000 JPY` |
| **Expected method** | `NMT` |
| **Notes** | Japanese business sentence with Kanji date and amount |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `free_text` | `expiry_date` | ⚠️ mismatch |
| **language** | `ja` | `ja` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `1.15s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `expiry_date` but expected `free_text`. The router will process the field as `expiry_date` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "支払期限は二〇二六年九月五日、金額は五千円です。", "field_type": "expiry_date", "language": "ja"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CALENDAR` |
| normalised_form | `2026-09-05` |
| confidence | `0.95` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `NMT` | `CALENDAR` | ❌ FAIL |
| **normalised_form** | `DUE DATE 2026-09-05 AMOUNT 5000 JPY` | `2026-09-05` | ❌ FAIL |

> ❌ **Method failure diagnosis:** Got 'CALENDAR', expected one of ['NMT']. Check router.py strategy wiring.

### Overall: ❌ FAIL

---

## H.9 — Traditional Chinese invoice prose

| | |
|---|---|
| **Input** | `付款日期為二〇二六年九月五日，金額為新台幣五千元。` |
| **Expected field type** | `free_text` |
| **Expected language** | `zh` |
| **Expected normalised form** | `PAYMENT DATE 2026-09-05 AMOUNT 5000 TWD` |
| **Expected method** | `NMT` |
| **Notes** | Traditional Chinese with Han numerals and currency designator |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `free_text` | `date_of_birth` | ⚠️ mismatch |
| **language** | `zh` | `zh` | ✅ match |
| **confidence** | — | `0.85` | — |
| **latency** | — | `1.63s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `date_of_birth` but expected `free_text`. The router will process the field as `date_of_birth` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "付款日期為二〇二六年九月五日，金額為新台幣五千元。", "field_type": "date_of_birth", "language": "zh"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CALENDAR` |
| normalised_form | `付款日期為二〇二六年九月五日,金額為新台幣五千元。` |
| confidence | `0.95` |
| review_required | `True` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `NMT` | `CALENDAR` | ❌ FAIL |
| **normalised_form** | `PAYMENT DATE 2026-09-05 AMOUNT 5000 TWD` | `付款日期為二〇二六年九月五日,金額為新台幣五千元。` | ❌ FAIL |

> ❌ **Method failure diagnosis:** Got 'CALENDAR', expected one of ['NMT']. Check router.py strategy wiring.

### Overall: ❌ FAIL

---

## H.10 — Russian invoice prose

| | |
|---|---|
| **Input** | `Срок оплаты: 05.09.2026, сумма: 12 500 руб.` |
| **Expected field type** | `free_text` |
| **Expected language** | `ru` |
| **Expected normalised form** | `DUE DATE 2026-09-05 AMOUNT 12500 RUB` |
| **Expected method** | `NMT` |
| **Notes** | Russian native date and space-thousands |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `free_text` | `total_assets` | ⚠️ mismatch |
| **language** | `ru` | `ru` | ✅ match |
| **confidence** | — | `0.92` | — |
| **latency** | — | `0.76s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `total_assets` but expected `free_text`. The router will process the field as `total_assets` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Срок оплаты: 05.09.2026, сумма: 12 500 руб.", "field_type": "total_assets", "language": "ru"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `NUMERIC` |
| normalised_form | `Срокоплаты:05.09.2026сумма:12500руб.` |
| confidence | `0.95` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `NMT` | `NUMERIC` | ❌ FAIL |
| **normalised_form** | `DUE DATE 2026-09-05 AMOUNT 12500 RUB` | `Срокоплаты:05.09.2026сумма:12500руб.` | ❌ FAIL |

> ❌ **Method failure diagnosis:** Got 'NUMERIC', expected one of ['NMT']. Check router.py strategy wiring.

### Overall: ❌ FAIL

---

## H.11 — German invoice prose

| | |
|---|---|
| **Input** | `Zahlungsziel: 05.09.2026, Betrag: 12.500 EUR` |
| **Expected field type** | `free_text` |
| **Expected language** | `de` |
| **Expected normalised form** | `DUE DATE 2026-09-05 AMOUNT 12500 EUR` |
| **Expected method** | `NMT` |
| **Notes** | German dot-thousands separator |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `free_text` | `total_assets` | ⚠️ mismatch |
| **language** | `de` | `de` | ✅ match |
| **confidence** | — | `0.92` | — |
| **latency** | — | `0.67s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `total_assets` but expected `free_text`. The router will process the field as `total_assets` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "Zahlungsziel: 05.09.2026, Betrag: 12.500 EUR", "field_type": "total_assets", "language": "de"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `NUMERIC` |
| normalised_form | `Zahlungsziel:05.09.2026Betrag:12.500EUR` |
| confidence | `0.95` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `NMT` | `NUMERIC` | ❌ FAIL |
| **normalised_form** | `DUE DATE 2026-09-05 AMOUNT 12500 EUR` | `Zahlungsziel:05.09.2026Betrag:12.500EUR` | ❌ FAIL |

> ❌ **Method failure diagnosis:** Got 'NUMERIC', expected one of ['NMT']. Check router.py strategy wiring.

### Overall: ❌ FAIL

---

## H.12 — Korean invoice prose

| | |
|---|---|
| **Input** | `지급기한: 2026년 09월 05일, 금액: 12,500 원` |
| **Expected field type** | `free_text` |
| **Expected language** | `ko` |
| **Expected normalised form** | `DUE DATE 2026-09-05 AMOUNT 12500 KRW` |
| **Expected method** | `NMT` |
| **Notes** | Korean labels and KRW currency |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `free_text` | `expiry_date` | ⚠️ mismatch |
| **language** | `ko` | `ko` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `10.01s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `expiry_date` but expected `free_text`. The router will process the field as `expiry_date` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "지급기한: 2026년 09월 05일, 금액: 12,500 원", "field_type": "expiry_date", "language": "ko"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `CALENDAR` |
| normalised_form | `지급기한: 2026년 09월 05일, 금액: 12,500 원` |
| confidence | `0.95` |
| review_required | `True` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `NMT` | `CALENDAR` | ❌ FAIL |
| **normalised_form** | `DUE DATE 2026-09-05 AMOUNT 12500 KRW` | `지급기한: 2026년 09월 05일, 금액: 12,500 원` | ❌ FAIL |

> ❌ **Method failure diagnosis:** Got 'CALENDAR', expected one of ['NMT']. Check router.py strategy wiring.

### Overall: ❌ FAIL

---

## E.12 — Arabic-Indic with embedded Latin O

| | |
|---|---|
| **Input** | `O١٢٣٤٥٦٧٨` |
| **Expected field type** | `id_number` |
| **Expected language** | `ar` |
| **Expected normalised form** | `None` |
| **Expected method** | `UNRESOLVED` |
| **Notes** | Latin O easily confused with Arabic-Indic zero — flag for review |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `id_number` | `id_no` | ⚠️ mismatch |
| **language** | `ar` | `ar` | ✅ match |
| **confidence** | — | `0.95` | — |
| **latency** | — | `1.11s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `id_no` but expected `id_number`. The router will process the field as `id_no` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "O١٢٣٤٥٦٧٨", "field_type": "id_no", "language": "ar"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `PRESERVE` |
| normalised_form | `O١٢٣٤٥٦٧٨` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `UNRESOLVED` | `PRESERVE` | ❌ FAIL |
| **normalised_form** | `None` | `O١٢٣٤٥٦٧٨` | ❌ FAIL |

> ❌ **Method failure diagnosis:** Field type 'id_no' is in the PRESERVE_FIELDS list but should not be. Check PRESERVE_FIELDS in router.py or preserve.py.

### Overall: ❌ FAIL

---

## E.13 — Mixed Latin letters and full-width digits

| | |
|---|---|
| **Input** | `I２３４５B８` |
| **Expected field type** | `id_number` |
| **Expected language** | `ja` |
| **Expected normalised form** | `None` |
| **Expected method** | `UNRESOLVED` |
| **Notes** | Latin I/full-width digits/Latin B/8 — visual ambiguity |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `id_number` | `passport_no` | ⚠️ mismatch |
| **language** | `ja` | `ja` | ✅ match |
| **confidence** | — | `0.90` | — |
| **latency** | — | `0.96s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `passport_no` but expected `id_number`. The router will process the field as `passport_no` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "I２３４５B８", "field_type": "passport_no", "language": "ja"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `PRESERVE` |
| normalised_form | `I２３４５B８` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `UNRESOLVED` | `PRESERVE` | ❌ FAIL |
| **normalised_form** | `None` | `I２３４５B８` | ❌ FAIL |

> ❌ **Method failure diagnosis:** Field type 'passport_no' is in the PRESERVE_FIELDS list but should not be. Check PRESERVE_FIELDS in router.py or preserve.py.

### Overall: ❌ FAIL

---

## E.14 — Han numeral with embedded Latin O

| | |
|---|---|
| **Input** | `一O八号` |
| **Expected field type** | `address` |
| **Expected language** | `zh` |
| **Expected normalised form** | `None` |
| **Expected method** | `UNRESOLVED` |
| **Notes** | Latin O inside Han numeral house number — should not auto-resolve to 108 |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `address` | `id_no` | ⚠️ mismatch |
| **language** | `zh` | `zh` | ✅ match |
| **confidence** | — | `0.85` | — |
| **latency** | — | `0.90s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `id_no` but expected `address`. The router will process the field as `id_no` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "一O八号", "field_type": "id_no", "language": "zh"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `PRESERVE` |
| normalised_form | `一O八号` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `UNRESOLVED` | `PRESERVE` | ❌ FAIL |
| **normalised_form** | `None` | `一O八号` | ❌ FAIL |

> ❌ **Method failure diagnosis:** Field type 'id_no' is in the PRESERVE_FIELDS list but should not be. Check PRESERVE_FIELDS in router.py or preserve.py.

### Overall: ❌ FAIL

---

## E.15 — Greek iota and omicron in alphanumeric reference

| | |
|---|---|
| **Input** | `REF-Ι23O5` |
| **Expected field type** | `reference_no` |
| **Expected language** | `el` |
| **Expected normalised form** | `None` |
| **Expected method** | `UNRESOLVED` |
| **Notes** | Greek Ι (iota) and Ο (omicron) mimic Latin I and O |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `reference_no` | `id_no` | ⚠️ mismatch |
| **language** | `el` | `el` | ✅ match |
| **confidence** | — | `0.88` | — |
| **latency** | — | `1.11s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `id_no` but expected `reference_no`. The router will process the field as `id_no` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "REF-Ι23O5", "field_type": "id_no", "language": "el"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `PRESERVE` |
| normalised_form | `REF-Ι23O5` |
| confidence | `1.00` |
| review_required | `False` |
| latency | `0.01s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `UNRESOLVED` | `PRESERVE` | ❌ FAIL |
| **normalised_form** | `None` | `REF-Ι23O5` | ❌ FAIL |

> ❌ **Method failure diagnosis:** Field type 'id_no' is in the PRESERVE_FIELDS list but should not be. Check PRESERVE_FIELDS in router.py or preserve.py.

### Overall: ❌ FAIL

---

## E.16 — Cyrillic А and Latin O in reference

| | |
|---|---|
| **Input** | `СЧЕТ 5O12А8` |
| **Expected field type** | `reference_no` |
| **Expected language** | `ru` |
| **Expected normalised form** | `None` |
| **Expected method** | `UNRESOLVED` |
| **Notes** | Cyrillic А vs Latin A and Latin O vs zero — OCR ambiguity |

### Step 1 — GPT-4o-mini classification

| | Expected | Got | Status |
|---|---|---|---|
| **field_type** | `reference_no` | `accounting_policies` | ⚠️ mismatch |
| **language** | `ru` | `ru` | ✅ match |
| **confidence** | — | `0.85` | — |
| **latency** | — | `0.81s` | — |

> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `accounting_policies` but expected `reference_no`. The router will process the field as `accounting_policies` which may select the wrong strategy.

### Step 2 — Orchestrator + Router

**Row passed to orchestrator:**

```json
{"original_text": "СЧЕТ 5O12А8", "field_type": "accounting_policies", "language": "ru"}
```

**Router result:**

| Field | Value |
|---|---|
| processing_method | `UNRESOLVED` |
| normalised_form | `None` |
| confidence | `0.00` |
| review_required | `True` |
| latency | `2.06s` |

### Step 3 — Expected vs Actual

| | Expected | Got | Status |
|---|---|---|---|
| **method** | `UNRESOLVED` | `UNRESOLVED` | ✅ PASS |
| **normalised_form** | `None` | `None` | ✅ PASS |

### Overall: ✅ PASS

---
