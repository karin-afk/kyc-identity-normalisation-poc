# KYC Identity Normalisation — User Testing Script

**App URL:** http://localhost:5001
**Date:**
**Tester:**

---

## Before you start

Make sure the app is running: `flask run --port 5001`
Open http://localhost:5001 in your browser.

For each test: paste the input exactly as shown, record what the app actually returns,
and mark Pass / Fail / Partial.

---

## Tab 1 — Sentence Normalisation

Navigate to the **Sentence** tab.

---

### Block 1 — Strategy A: Preserve (identifiers returned unchanged)

These must come back exactly as entered. No changes of any kind.

| # | Paste this | Expected normalised form | Method | Result | Pass? |
|---|---|---|---|---|---|
| 1.1 | `TK1234567` | `TK1234567` | PRESERVE | | |
| 1.2 | `DE123456789` | `DE123456789` | PRESERVE | | |
| 1.3 | `SC123456` | `SC123456` | PRESERVE | | |
| 1.4 | `test.user@example.com` | `test.user@example.com` | PRESERVE | | |
| 1.5 | `GB123456789` | `GB123456789` | PRESERVE | | |

**What to check:** Normalised form is byte-for-byte identical to input. No uppercasing,
no digit conversion, no changes.

**If 1.1–1.5 fail:** Strategy A is not wired into the router, or the paste form field
name is wrong. Run: `pytest tests/test_strategy_a_preserve.py -v`

---

### Block 2 — Strategy B: Dates (calendar conversion)

| # | Paste this | Language hint | Expected normalised form | Calendar | Pass? |
|---|---|---|---|---|---|
| 2.1 | `2568/5/8` | Thai (th) | `2025-05-08` | Thai Buddhist | |
| 2.2 | `114/5/8` | — | `2025-05-08` | Minguo (TW) | |
| 2.3 | `令和5年7月3日` | Japanese (ja) | `2023-07-03` | Japanese era | |
| 2.4 | `١٤٤٥/٠٩/٠١` | Arabic (ar) | `2024-03-11` | Hijri | |
| 2.5 | `1404/2/15` | Farsi (fa) | `2025-05-05` | Solar Hijri | |

**Note:** The paste tab auto-detects language. If auto-detect fails on 2.1–2.5,
note what language it detected and whether the result was still correct.

**If 2.x fail:** Strategy B may not be wired, or the calendar module files
(`calendar_solar_hijri.py`, `calendar_offset.py`, `calendar_hebrew.py`) may still
be in `src/pipeline/` instead of `app/pipeline/normalisation/`.

---

### Block 3 — Strategy B: Numeric normalisation

| # | Paste this | Expected normalised form | Method | Pass? |
|---|---|---|---|---|
| 3.1 | `△4,191` | `-4191` | NUMERIC | |
| 3.2 | `（4,191）` | `-4191` | NUMERIC | |
| 3.3 | `1.234.567,89` | `1234567.89` | NUMERIC | |
| 3.4 | `1'234'567.89` | `1234567.89` | NUMERIC | |
| 3.5 | `٠١٢٣٤٥٦٧٨٩` | `0123456789` | NUMERIC | |

**Note for 3.5:** These are Arabic-Indic digits. Expected result is `0123456789`.

---

### Block 4 — Strategy C: Vocabulary lookup

| # | Paste this | Expected normalised form | Method | Pass? |
|---|---|---|---|---|
| 4.1 | `株式会社` | `KK` | VOCABULARY | |
| 4.2 | `GmbH` | `GMBH` | VOCABULARY | |
| 4.3 | `ООО` | `LLC` | VOCABULARY | |
| 4.4 | `現役` | `ACTIVE` | VOCABULARY | |
| 4.5 | `منتهي` | `DISSOLVED` | VOCABULARY | |
| 4.6 | `取締役` | `DIRECTOR` | VOCABULARY | |
| 4.7 | `代表取締役` | `REPRESENTATIVE DIRECTOR` | VOCABULARY | |
| 4.8 | `aufgelöst` | `DISSOLVED` | VOCABULARY | |

---

### Block 5 — Strategy G: Latin-script character maps

| # | Paste this | Expected normalised form | Variants include | Pass? |
|---|---|---|---|---|
| 5.1 | `Müller` | `MUELLER` | MULLER | |
| 5.2 | `Straße` | `STRASSE` | | |
| 5.3 | `García` | `GARCIA` | | |
| 5.4 | `Muñoz` | `MUNOZ` | MUNYOZ | |
| 5.5 | `İstanbul` | `ISTANBUL` | | |
| 5.6 | `Łódź` | `LODZ` | | |
| 5.7 | `Ærø` | `AERO` | | |
| 5.8 | `Bjørn` | `BJORN` | | |
| 5.9 | `João` | `JOAO` | | |

**If 5.1 fails but returns MULLER:** Character map is applying DROPS not EXPANSIONS as primary.
**If 5.5 fails:** Turkish map not implemented or İ (dotted I) not in the map.

---

### Block 6 — Unresolved → review queue

These should NOT normalise — they should route to native speaker review.

| # | Paste this | Expected result | Pass? |
|---|---|---|---|
| 6.1 | `محمد عبد الله` | "Awaiting review" notice shown | |
| 6.2 | `田中 花子` (if not in seed) | "Awaiting review" notice shown | |

**What to check:** No crash. Clear message that the field is queued for review.

---

### Block 7 — UI checks

| # | Check | Expected | Pass? |
|---|---|---|---|
| 7.1 | Paste tab has no language dropdown | No dropdown visible | |
| 7.2 | Paste tab has no field type dropdown | No dropdown visible | |
| 7.3 | Result shows "Language:" label | Language code displayed | |
| 7.4 | Result shows "Field type:" label | Field type displayed | |
| 7.5 | Result shows "Method:" label | Strategy label displayed | |
| 7.6 | Result shows "Confidence:" | Percentage displayed | |
| 7.7 | Character counter updates as you type | Updates on every keystroke | |
| 7.8 | Submit with empty textarea | Does not crash | |
| 7.9 | Submit 2001 characters | "exceeds 2,000 characters" notice | |

---

## Tab 2 — Document Normalisation

Navigate to the **Document** tab.

| # | Check | Expected | Pass? |
|---|---|---|---|
| 8.1 | Page loads without error | Upload form visible | |
| 8.2 | Document type dropdown visible | Options listed | |
| 8.3 | Upload a PDF | "Not yet available" notice OR real results | |
| 8.4 | Upload with no file selected | Error notice, no crash | |

**Note:** If Document Intelligence is not yet wired, uploading should return the
"not yet available" notice — not a 500 error. A 500 error means the route is broken.

---

## Tab 3 — Human Review

Navigate to the **Review** tab (only visible if you are registered as a native speaker).

| # | Check | Expected | Pass? |
|---|---|---|---|
| 9.1 | Tab visible in nav | Visible during development | |
| 9.2 | Review queue loads | Either empty queue or task list | |
| 9.3 | No crash on load | HTTP 200 | |

---

## Known limitations at current build stage

- Document tab: Document Intelligence not yet integrated — upload returns "not yet available"
- Review tab: Email notifications not yet wired — stub only
- Strategy F (transliteration): May still be a stub for some languages
- Strategy H (Azure NMT): Requires Azure credentials in `.env` to function

---

## What to do when something fails

1. Note the exact input and what the app returned
2. Check the Flask server terminal for any error output
3. Run the relevant pytest: `pytest tests/test_strategy_X.py -v -s`
4. Check the route is receiving the form data: add a `print(request.form)` in the route temporarily