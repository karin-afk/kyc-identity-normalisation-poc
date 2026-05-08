# Evaluation Framework — Golden Dataset and Performance Results

## 1. Purpose of the Evaluation Framework

The evaluation framework provides a **repeatable, quantitative measure of pipeline correctness**. It is used to:

- Verify that a code change has not degraded performance (regression testing)
- Measure improvements when new language handling or matching logic is added
- Provide evidence for stakeholder sign-off and audit
- Track progress across the multiple dimensions relevant to KYC: language, field type, and processing method

The framework is entirely local — it requires only the golden dataset CSV file and optionally an OpenAI API key (for the LLM-routed fields). It produces both human-readable console output and machine-readable JSON/CSV artefacts.

---

## 2. Golden Dataset

### File location
`data/golden_dataset.csv`

### Structure
The dataset has 16 columns per row:

| Column | Type | Description |
|---|---|---|
| `case_id` | string | Unique identifier (`KYC001`–`KYC112`; image cases are `IMG001`–) |
| `image_path` | string | Relative path to source document image (empty for text-only cases) |
| `language` | ISO 639-1 | Language code: `ar`, `ja`, `ru`, `zh`, `el`, `en` |
| `script` | string | Script name: Arabic, Kanji, Katakana, Hiragana, Cyrillic, Han, Greek |
| `country` | ISO 3166-1 alpha-2 | Country of document origin |
| `document_type` | string | `passport`, `proof_of_address`, `corporate_registry`, `sanctions_profile`, etc. |
| `field_type` | string | `person_name`, `alias`, `company_name`, `address`, `passport_no`, `id_no`, `email` |
| `original_text` | string | The raw non-Latin text as it appears on the document |
| `expected_treatment` | string | `PRESERVE`, `TRANSLITERATE`, `TRANSLATE_NORMALISE`, `TRANSLATE_COMPOSITE` |
| `expected_transliteration` | string | Correct BGN/PCGN or standard romanised form (primary) |
| `expected_allowed_variants` | string | Pipe-separated (`\|`) list of other accepted forms |
| `expected_english` | string | Natural English rendering (may differ from screener form) |
| `expected_normalised` | string | **Ground truth for evaluation** — uppercase normalised form |
| `should_flag_review` | boolean | Whether the pipeline is expected to set `review_required=True` |
| `is_negative_case` | boolean | Whether this is a **negative case** (the pipeline should NOT match) |
| `risk_notes` | string | Free-text annotation explaining the KYC risk dimension being tested |

### Dataset size and composition — current state (514 cases)

| Language | Cases | Field types covered |
|---|---|---|
| Arabic (ar) | 48 | address, alias, birth_date, company_name, date, email, free_text, id_number, passport_no, person_name, phone_number, reference_no, registration_no, tax_id, telephone |
| German (de) | 47 | address, alias, birth_date, company_name, date, email, free_text, id_number, passport_no, person_name, phone_number, reference_no, registration_no, tax_id, telephone |
| Greek (el) | 46 | address, alias, birth_date, company_name, date, email, free_text, id_number, passport_no, person_name, phone_number, reference_no, registration_no, tax_id, telephone |
| English (en) | 48 | address, alias, birth_date, company_name, date, email, free_text, id_number, passport_no, person_name, phone_number, reference_no, registration_no, tax_id, telephone |
| Spanish (es) | 46 | address, alias, birth_date, company_name, date, email, free_text, id_number, passport_no, person_name, phone_number, reference_no, registration_no, tax_id, telephone |
| French (fr) | 45 | address, alias, birth_date, company_name, date, email, free_text, id_number, passport_no, person_name, phone_number, reference_no, registration_no, tax_id, telephone |
| Italian (it) | 46 | address, alias, birth_date, company_name, date, email, free_text, id_number, passport_no, person_name, phone_number, reference_no, registration_no, tax_id, telephone |
| Japanese (ja) | 46 | address, alias, birth_date, company_name, date, email, free_text, id_number, passport_no, person_name, phone_number, reference_no, registration_no, tax_id, telephone |
| Korean (ko) | 47 | address, alias, birth_date, company_name, date, email, free_text, id_number, passport_no, person_name, phone_number, reference_no, registration_no, tax_id, telephone |
| Russian/Ukrainian (ru) | 48 | address, alias, birth_date, company_name, date, email, free_text, id_number, passport_no, person_name, phone_number, reference_no, registration_no, tax_id, telephone |
| Chinese (zh) | 47 | address, alias, birth_date, company_name, date, email, free_text, id_number, passport_no, person_name, phone_number, reference_no, registration_no, tax_id, telephone |
| **Total** | **514** | |

### Test dataset
`data/test_dataset.csv`

A separate 528-case test dataset used to evaluate pipeline generalisation on held-out examples not used during development. It shares the same 16-column schema. Composition: 48 cases per language (Arabic, German, Greek, English, Spanish, French, Italian, Japanese, Korean, Russian/Ukrainian, Chinese), covering all 15 field types.

---

## 3. Case Types

### Standard cases
The majority of cases are **standard positive cases**: the pipeline should produce an output that matches `expected_normalised` or one of the `expected_allowed_variants`.

### Negative cases (`is_negative_case = true`)
Negative cases test that the pipeline **does not produce a false positive**: the pipeline output should *not* match the `expected_normalised` value. For example, KYC014 (Алексей Смирнов, Russian) is flagged as a negative case to verify that it does not match a different Aleksei Smirnov identity listed elsewhere in the dataset.

### TRANSLATE_COMPOSITE cases
A small number of cases are tagged `expected_treatment=TRANSLATE_COMPOSITE`. These represent alias entries that contain both a name token and a natural-language descriptor phrase (e.g. "по прозвищу САША", "又名 王小强", "γνωστός ως ΝΙΚΟΣ"). The descriptor must be *translated* to its English screener form (ALSO KNOWN AS / NICKNAMED / KNOWN AS) while the name tokens are transliterated. These are handled by the LLM layer, routed via `is_composite_alias()` detection in `field_classifier.py`.

---

## 4. Evaluation Algorithm

The evaluator (`src/evaluation/evaluator.py`) applies a multi-pass matching strategy to determine whether a pipeline result is correct. Passes are applied in sequence; a case is marked as a match as soon as any pass succeeds.

### Pass 1 — Exact normalised match
```
result["normalised_form"].upper() == expected_normalised.upper()
```

### Pass 2 — Variant list match (pipeline variants)
```
expected_normalised in result["allowed_variants"]
```
Used when the pipeline (LLM layer for Arabic) returns multiple candidate forms and the expected form is in the candidate list.

### Pass 3 — Dataset variant match
```
result["normalised_form"] in expected_allowed_variants (pipe-split list)
```
The dataset's `expected_allowed_variants` column lists all forms that a screening analyst would accept. If the pipeline produced any of them, the case is marked correct.

### Pass 4 — Arabic canonical match
Applied only to `language=ar` cases:
1. Strip `AL-` / `EL-` prefixes from all tokens.
2. Map known variant spellings to canonical forms (MOHAMMED→MUHAMMAD, HASAN→HASSAN, HUSSEIN→HUSSAIN).
3. Compare the resulting canonical skeletons.

This ensures that romanisation-family differences (Muhammad vs Mohammed) do not generate false failures.

### Pass 5 — Company name lenient match
Applied only to `field_type=company_name` cases:
1. Normalise: remove dots from acronym suffixes (S.A.→SA), map verbose forms (CORPORATION→CORP), strip commas.
2. Exact match on normalised forms.
3. Core match: strip all trailing legal-suffix tokens (LTD, PLC, LLC, INC, KK, OOO, etc.) from both sides and compare the bare company root.

### Pass 6 — Address lenient match
Applied only to `field_type=address` cases:
1. Strip commas and hyphens, collapse whitespace.
2. Exact match on cleaned string.
3. Token-set match: compare unordered sets of tokens (handles number/street reversal, e.g. "25 MIRA AVENUE" vs "MIRA AVENUE 25").

---

## 5. Running the Evaluation

```bash
# From the repo root
cd kyc-identity-normalisation-poc
pip install -r requirements.txt

# Set API key (required for LLM fields: Arabic names, all addresses, all company names)
cp .env.example .env
# Edit .env: OPENAI_API_KEY=sk-proj-...

# Run evaluation
PYTHONPATH=src python src/main.py
```

Output is written to:
- Console — human-readable summary
- `data/output/results_<timestamp>.json` — full per-case results
- `data/output/results_<timestamp>.csv` — spreadsheet-friendly

### Running without an API key
The pipeline runs in stub mode. LLM fields receive `confidence=0.0` and `processing_method=LLM` with stub output. Overall accuracy will be lower — approximately 55–60% — because Arabic names, all addresses, and all company names are not processed.

---

## 6. Current Performance Results — Golden Dataset

*Measured on 2 April 2026, pipeline v3, model gpt-4o, temperature=0.*
*514 cases across 11 languages: ar, de, el, en, es, fr, it, ja, ko, ru, zh.*

### Overall accuracy
**68.1% — 350 correct out of 514 cases**

> **Context:** the dataset grew from the original 112 cases (March 2026 baseline) to 514 by adding five languages (de, es, fr, it, ko) and nine new field types (birth_date, date, free_text, id_number, phone_number, reference_no, registration_no, tax_id, telephone). Several of these new types — `NORMALISE`, `NORMALISE_NUMERIC`, `PRESERVE_NORMALISE_SCRIPT`, `FLAG_REVIEW` — are not yet fully implemented and account for the majority of new failures. The pipeline's core treatments (TRANSLITERATE, TRANSLATE_NORMALISE for addresses and company names) are consistent with the previous baseline.

---

### By language

| Language | Correct | Total | Accuracy |
|---|---|---|---|
| Arabic (ar) | 33 | 48 | **68.8%** |
| German (de) | 36 | 47 | **76.6%** |
| Greek (el) | 27 | 46 | **58.7%** |
| English (en) | 39 | 48 | **81.2%** |
| Spanish (es) | 35 | 46 | **76.1%** |
| French (fr) | 33 | 45 | **73.3%** |
| Italian (it) | 35 | 46 | **76.1%** |
| Japanese (ja) | 31 | 46 | **67.4%** |
| Korean (ko) | 29 | 47 | **61.7%** |
| Russian/Ukrainian (ru) | 25 | 48 | **52.1%** |
| Chinese (zh) | 27 | 47 | **57.4%** |

---

### By expected treatment

| Treatment | Correct | Total | Accuracy |
|---|---|---|---|
| TRANSLITERATE | 206 | 220 | **93.6%** |
| TRANSLATE_NORMALISE | 70 | 121 | **57.9%** |
| PRESERVE | 55 | 68 | **80.9%** |
| NORMALISE | 8 | 23 | **34.8%** |
| NORMALISE_NUMERIC | 8 | 24 | **33.3%** |
| TRANSLATE_ANALYST | 1 | 12 | **8.3%** |
| PRESERVE_NORMALISE_SCRIPT | 2 | 41 | **4.9%** |
| FLAG_REVIEW | 0 | 5 | **0.0%** |

`NORMALISE`, `NORMALISE_NUMERIC`, `PRESERVE_NORMALISE_SCRIPT`, `FLAG_REVIEW`, and `TRANSLATE_ANALYST` are categories covering numeric IDs, phone numbers, dates, registration numbers, free text, and composite aliases — not yet fully implemented.

---

### By language × field type

| Language | Field type | Correct | Total | Accuracy |
|---|---|---|---|---|
| ar | address | 1 | 7 | **14.3%** |
| ar | alias | 2 | 2 | **100.0%** |
| ar | birth_date | 1 | 1 | **100.0%** |
| ar | company_name | 3 | 4 | **75.0%** |
| ar | date | 1 | 1 | **100.0%** |
| ar | email | 1 | 1 | **100.0%** |
| ar | free_text | 0 | 1 | **0.0%** |
| ar | id_number | 1 | 2 | **50.0%** |
| ar | passport_no | 5 | 5 | **100.0%** |
| ar | person_name | 16 | 19 | **84.2%** |
| ar | phone_number | 1 | 1 | **100.0%** |
| ar | reference_no | 0 | 1 | **0.0%** |
| ar | registration_no | 0 | 1 | **0.0%** |
| ar | tax_id | 0 | 1 | **0.0%** |
| ar | telephone | 0 | 1 | **0.0%** |
| de | address | 7 | 7 | **100.0%** |
| de | alias | 2 | 2 | **100.0%** |
| de | birth_date | 1 | 1 | **100.0%** |
| de | company_name | 3 | 4 | **75.0%** |
| de | date | 0 | 1 | **0.0%** |
| de | email | 1 | 1 | **100.0%** |
| de | free_text | 0 | 1 | **0.0%** |
| de | id_number | 0 | 1 | **0.0%** |
| de | passport_no | 3 | 5 | **60.0%** |
| de | person_name | 19 | 19 | **100.0%** |
| de | phone_number | 0 | 1 | **0.0%** |
| de | reference_no | 0 | 1 | **0.0%** |
| de | registration_no | 0 | 1 | **0.0%** |
| de | tax_id | 0 | 1 | **0.0%** |
| de | telephone | 0 | 1 | **0.0%** |
| el | address | 1 | 7 | **14.3%** |
| el | alias | 0 | 2 | **0.0%** |
| el | birth_date | 1 | 1 | **100.0%** |
| el | company_name | 4 | 4 | **100.0%** |
| el | email | 1 | 1 | **100.0%** |
| el | free_text | 0 | 1 | **0.0%** |
| el | id_number | 0 | 2 | **0.0%** |
| el | passport_no | 4 | 5 | **80.0%** |
| el | person_name | 16 | 19 | **84.2%** |
| el | phone_number | 0 | 1 | **0.0%** |
| el | reference_no | 0 | 1 | **0.0%** |
| el | tax_id | 0 | 1 | **0.0%** |
| el | telephone | 0 | 1 | **0.0%** |
| en | address | 7 | 7 | **100.0%** |
| en | alias | 2 | 2 | **100.0%** |
| en | birth_date | 1 | 1 | **100.0%** |
| en | company_name | 3 | 4 | **75.0%** |
| en | date | 0 | 1 | **0.0%** |
| en | email | 1 | 1 | **100.0%** |
| en | free_text | 0 | 1 | **0.0%** |
| en | id_number | 0 | 2 | **0.0%** |
| en | passport_no | 5 | 5 | **100.0%** |
| en | person_name | 19 | 19 | **100.0%** |
| en | phone_number | 0 | 1 | **0.0%** |
| en | reference_no | 0 | 1 | **0.0%** |
| en | registration_no | 1 | 1 | **100.0%** |
| en | tax_id | 0 | 1 | **0.0%** |
| en | telephone | 0 | 1 | **0.0%** |
| es | address | 7 | 7 | **100.0%** |
| es | alias | 1 | 2 | **50.0%** |
| es | company_name | 4 | 4 | **100.0%** |
| es | date | 0 | 1 | **0.0%** |
| es | email | 1 | 1 | **100.0%** |
| es | free_text | 0 | 1 | **0.0%** |
| es | id_number | 0 | 2 | **0.0%** |
| es | passport_no | 4 | 5 | **80.0%** |
| es | person_name | 19 | 19 | **100.0%** |
| es | phone_number | 0 | 1 | **0.0%** |
| es | reference_no | 0 | 1 | **0.0%** |
| es | registration_no | 0 | 1 | **0.0%** |
| es | tax_id | 0 | 1 | **0.0%** |
| fr | address | 6 | 7 | **85.7%** |
| fr | alias | 0 | 2 | **0.0%** |
| fr | company_name | 4 | 4 | **100.0%** |
| fr | date | 0 | 1 | **0.0%** |
| fr | free_text | 0 | 1 | **0.0%** |
| fr | id_number | 0 | 2 | **0.0%** |
| fr | passport_no | 4 | 5 | **80.0%** |
| fr | person_name | 19 | 19 | **100.0%** |
| fr | phone_number | 0 | 1 | **0.0%** |
| fr | reference_no | 0 | 1 | **0.0%** |
| fr | registration_no | 0 | 1 | **0.0%** |
| fr | tax_id | 0 | 1 | **0.0%** |
| it | address | 7 | 7 | **100.0%** |
| it | alias | 1 | 2 | **50.0%** |
| it | company_name | 4 | 4 | **100.0%** |
| it | date | 0 | 1 | **0.0%** |
| it | email | 1 | 1 | **100.0%** |
| it | free_text | 0 | 1 | **0.0%** |
| it | id_number | 0 | 2 | **0.0%** |
| it | passport_no | 3 | 5 | **60.0%** |
| it | person_name | 19 | 19 | **100.0%** |
| it | phone_number | 0 | 1 | **0.0%** |
| it | reference_no | 0 | 1 | **0.0%** |
| it | registration_no | 0 | 1 | **0.0%** |
| it | tax_id | 0 | 1 | **0.0%** |
| ja | address | 3 | 7 | **42.9%** |
| ja | alias | 1 | 2 | **50.0%** |
| ja | company_name | 4 | 4 | **100.0%** |
| ja | date | 0 | 1 | **0.0%** |
| ja | free_text | 0 | 1 | **0.0%** |
| ja | id_number | 0 | 2 | **0.0%** |
| ja | passport_no | 5 | 5 | **100.0%** |
| ja | person_name | 18 | 19 | **94.7%** |
| ja | phone_number | 0 | 1 | **0.0%** |
| ja | reference_no | 0 | 1 | **0.0%** |
| ja | registration_no | 0 | 1 | **0.0%** |
| ja | tax_id | 0 | 1 | **0.0%** |
| ja | telephone | 0 | 1 | **0.0%** |
| ko | address | 3 | 7 | **42.9%** |
| ko | alias | 0 | 2 | **0.0%** |
| ko | company_name | 4 | 4 | **100.0%** |
| ko | date | 0 | 1 | **0.0%** |
| ko | email | 1 | 1 | **100.0%** |
| ko | free_text | 0 | 1 | **0.0%** |
| ko | id_number | 0 | 2 | **0.0%** |
| ko | passport_no | 3 | 5 | **60.0%** |
| ko | person_name | 18 | 19 | **94.7%** |
| ko | phone_number | 0 | 1 | **0.0%** |
| ko | reference_no | 0 | 1 | **0.0%** |
| ko | registration_no | 0 | 1 | **0.0%** |
| ko | tax_id | 0 | 1 | **0.0%** |
| ko | telephone | 0 | 1 | **0.0%** |
| ru | address | 0 | 7 | **0.0%** |
| ru | alias | 0 | 2 | **0.0%** |
| ru | birth_date | 1 | 1 | **100.0%** |
| ru | company_name | 3 | 4 | **75.0%** |
| ru | date | 1 | 1 | **100.0%** |
| ru | email | 1 | 1 | **100.0%** |
| ru | free_text | 0 | 1 | **0.0%** |
| ru | id_number | 0 | 2 | **0.0%** |
| ru | passport_no | 5 | 5 | **100.0%** |
| ru | person_name | 14 | 19 | **73.7%** |
| ru | phone_number | 0 | 1 | **0.0%** |
| ru | reference_no | 0 | 1 | **0.0%** |
| ru | registration_no | 0 | 1 | **0.0%** |
| ru | tax_id | 0 | 1 | **0.0%** |
| ru | telephone | 0 | 1 | **0.0%** |
| zh | address | 0 | 7 | **0.0%** |
| zh | alias | 0 | 2 | **0.0%** |
| zh | company_name | 2 | 4 | **50.0%** |
| zh | date | 0 | 1 | **0.0%** |
| zh | email | 1 | 1 | **100.0%** |
| zh | free_text | 0 | 1 | **0.0%** |
| zh | id_number | 0 | 2 | **0.0%** |
| zh | passport_no | 5 | 5 | **100.0%** |
| zh | person_name | 19 | 19 | **100.0%** |
| zh | phone_number | 0 | 1 | **0.0%** |
| zh | reference_no | 0 | 1 | **0.0%** |
| zh | registration_no | 0 | 1 | **0.0%** |
| zh | tax_id | 0 | 1 | **0.0%** |
| zh | telephone | 0 | 1 | **0.0%** |

---

### By language × expected treatment

| Language | Treatment | Correct | Total | Accuracy |
|---|---|---|---|---|
| ar | FLAG_REVIEW | 0 | 1 | **0.0%** |
| ar | NORMALISE_NUMERIC | 3 | 4 | **75.0%** |
| ar | PRESERVE | 6 | 6 | **100.0%** |
| ar | PRESERVE_NORMALISE_SCRIPT | 1 | 4 | **25.0%** |
| ar | TRANSLATE_NORMALISE | 4 | 12 | **33.3%** |
| ar | TRANSLITERATE | 18 | 21 | **85.7%** |
| de | NORMALISE | 1 | 4 | **25.0%** |
| de | NORMALISE_NUMERIC | 1 | 2 | **50.0%** |
| de | PRESERVE | 4 | 6 | **66.7%** |
| de | PRESERVE_NORMALISE_SCRIPT | 0 | 3 | **0.0%** |
| de | TRANSLATE_NORMALISE | 9 | 11 | **81.8%** |
| de | TRANSLITERATE | 21 | 21 | **100.0%** |
| el | FLAG_REVIEW | 0 | 1 | **0.0%** |
| el | NORMALISE_NUMERIC | 1 | 3 | **33.3%** |
| el | PRESERVE | 5 | 6 | **83.3%** |
| el | PRESERVE_NORMALISE_SCRIPT | 0 | 3 | **0.0%** |
| el | TRANSLATE_ANALYST | 0 | 2 | **0.0%** |
| el | TRANSLATE_NORMALISE | 4 | 11 | **36.4%** |
| el | TRANSLITERATE | 17 | 20 | **85.0%** |
| en | NORMALISE | 4 | 4 | **100.0%** |
| en | NORMALISE_NUMERIC | 1 | 4 | **25.0%** |
| en | PRESERVE | 7 | 8 | **87.5%** |
| en | PRESERVE_NORMALISE_SCRIPT | 0 | 3 | **0.0%** |
| en | TRANSLATE_ANALYST | 1 | 1 | **100.0%** |
| en | TRANSLATE_NORMALISE | 6 | 8 | **75.0%** |
| en | TRANSLITERATE | 20 | 20 | **100.0%** |
| es | NORMALISE | 1 | 4 | **25.0%** |
| es | PRESERVE | 5 | 8 | **62.5%** |
| es | PRESERVE_NORMALISE_SCRIPT | 0 | 2 | **0.0%** |
| es | TRANSLATE_ANALYST | 0 | 1 | **0.0%** |
| es | TRANSLATE_NORMALISE | 10 | 11 | **90.9%** |
| es | TRANSLITERATE | 20 | 20 | **100.0%** |
| fr | NORMALISE | 1 | 4 | **25.0%** |
| fr | PRESERVE | 4 | 5 | **80.0%** |
| fr | PRESERVE_NORMALISE_SCRIPT | 0 | 4 | **0.0%** |
| fr | TRANSLATE_ANALYST | 0 | 1 | **0.0%** |
| fr | TRANSLATE_NORMALISE | 9 | 11 | **81.8%** |
| fr | TRANSLITERATE | 19 | 20 | **95.0%** |
| it | NORMALISE | 1 | 3 | **33.3%** |
| it | PRESERVE | 4 | 8 | **50.0%** |
| it | PRESERVE_NORMALISE_SCRIPT | 0 | 3 | **0.0%** |
| it | TRANSLATE_ANALYST | 0 | 1 | **0.0%** |
| it | TRANSLATE_NORMALISE | 10 | 11 | **90.9%** |
| it | TRANSLITERATE | 20 | 20 | **100.0%** |
| ja | FLAG_REVIEW | 0 | 1 | **0.0%** |
| ja | NORMALISE_NUMERIC | 0 | 3 | **0.0%** |
| ja | PRESERVE | 5 | 5 | **100.0%** |
| ja | PRESERVE_NORMALISE_SCRIPT | 0 | 4 | **0.0%** |
| ja | TRANSLATE_ANALYST | 0 | 1 | **0.0%** |
| ja | TRANSLATE_NORMALISE | 7 | 12 | **58.3%** |
| ja | TRANSLITERATE | 19 | 20 | **95.0%** |
| ko | NORMALISE | 0 | 4 | **0.0%** |
| ko | NORMALISE_NUMERIC | 0 | 1 | **0.0%** |
| ko | PRESERVE | 4 | 5 | **80.0%** |
| ko | PRESERVE_NORMALISE_SCRIPT | 0 | 5 | **0.0%** |
| ko | TRANSLATE_ANALYST | 0 | 1 | **0.0%** |
| ko | TRANSLATE_NORMALISE | 7 | 11 | **63.6%** |
| ko | TRANSLITERATE | 18 | 20 | **90.0%** |
| ru | FLAG_REVIEW | 0 | 1 | **0.0%** |
| ru | NORMALISE_NUMERIC | 2 | 4 | **50.0%** |
| ru | PRESERVE | 5 | 5 | **100.0%** |
| ru | PRESERVE_NORMALISE_SCRIPT | 1 | 5 | **20.0%** |
| ru | TRANSLATE_ANALYST | 0 | 2 | **0.0%** |
| ru | TRANSLATE_NORMALISE | 3 | 12 | **25.0%** |
| ru | TRANSLITERATE | 14 | 19 | **73.7%** |
| zh | FLAG_REVIEW | 0 | 1 | **0.0%** |
| zh | NORMALISE_NUMERIC | 0 | 3 | **0.0%** |
| zh | PRESERVE | 6 | 6 | **100.0%** |
| zh | PRESERVE_NORMALISE_SCRIPT | 0 | 5 | **0.0%** |
| zh | TRANSLATE_ANALYST | 0 | 2 | **0.0%** |
| zh | TRANSLATE_NORMALISE | 2 | 11 | **18.2%** |
| zh | TRANSLITERATE | 19 | 19 | **100.0%** |

---

### By language × field type × expected treatment

| Language | Field type | Treatment | Correct | Total | Accuracy |
|---|---|---|---|---|---|
| ar | address | TRANSLATE_NORMALISE | 1 | 7 | **14.3%** |
| ar | alias | TRANSLITERATE | 2 | 2 | **100.0%** |
| ar | birth_date | NORMALISE_NUMERIC | 1 | 1 | **100.0%** |
| ar | company_name | TRANSLATE_NORMALISE | 3 | 4 | **75.0%** |
| ar | date | NORMALISE_NUMERIC | 1 | 1 | **100.0%** |
| ar | email | PRESERVE | 1 | 1 | **100.0%** |
| ar | free_text | TRANSLATE_NORMALISE | 0 | 1 | **0.0%** |
| ar | id_number | FLAG_REVIEW | 0 | 1 | **0.0%** |
| ar | id_number | PRESERVE_NORMALISE_SCRIPT | 1 | 1 | **100.0%** |
| ar | passport_no | PRESERVE | 5 | 5 | **100.0%** |
| ar | person_name | TRANSLITERATE | 16 | 19 | **84.2%** |
| ar | phone_number | NORMALISE_NUMERIC | 1 | 1 | **100.0%** |
| ar | reference_no | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| ar | registration_no | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| ar | tax_id | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| ar | telephone | NORMALISE_NUMERIC | 0 | 1 | **0.0%** |
| de | address | NORMALISE | 1 | 1 | **100.0%** |
| de | address | TRANSLATE_NORMALISE | 6 | 6 | **100.0%** |
| de | alias | TRANSLITERATE | 2 | 2 | **100.0%** |
| de | birth_date | NORMALISE_NUMERIC | 1 | 1 | **100.0%** |
| de | company_name | TRANSLATE_NORMALISE | 3 | 4 | **75.0%** |
| de | date | NORMALISE | 0 | 1 | **0.0%** |
| de | email | PRESERVE | 1 | 1 | **100.0%** |
| de | free_text | TRANSLATE_NORMALISE | 0 | 1 | **0.0%** |
| de | id_number | NORMALISE | 0 | 1 | **0.0%** |
| de | passport_no | PRESERVE | 3 | 5 | **60.0%** |
| de | person_name | TRANSLITERATE | 19 | 19 | **100.0%** |
| de | phone_number | NORMALISE | 0 | 1 | **0.0%** |
| de | reference_no | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| de | registration_no | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| de | tax_id | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| de | telephone | NORMALISE_NUMERIC | 0 | 1 | **0.0%** |
| el | address | TRANSLATE_NORMALISE | 1 | 7 | **14.3%** |
| el | alias | TRANSLATE_ANALYST | 0 | 2 | **0.0%** |
| el | birth_date | NORMALISE_NUMERIC | 1 | 1 | **100.0%** |
| el | company_name | TRANSLATE_NORMALISE | 3 | 3 | **100.0%** |
| el | company_name | TRANSLITERATE | 1 | 1 | **100.0%** |
| el | email | PRESERVE | 1 | 1 | **100.0%** |
| el | free_text | TRANSLATE_NORMALISE | 0 | 1 | **0.0%** |
| el | id_number | PRESERVE | 0 | 1 | **0.0%** |
| el | id_number | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| el | passport_no | PRESERVE | 4 | 4 | **100.0%** |
| el | passport_no | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| el | person_name | TRANSLITERATE | 16 | 19 | **84.2%** |
| el | phone_number | NORMALISE_NUMERIC | 0 | 1 | **0.0%** |
| el | reference_no | FLAG_REVIEW | 0 | 1 | **0.0%** |
| el | tax_id | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| el | telephone | NORMALISE_NUMERIC | 0 | 1 | **0.0%** |
| en | address | NORMALISE | 4 | 4 | **100.0%** |
| en | address | TRANSLATE_NORMALISE | 3 | 3 | **100.0%** |
| en | alias | TRANSLATE_ANALYST | 1 | 1 | **100.0%** |
| en | alias | TRANSLITERATE | 1 | 1 | **100.0%** |
| en | birth_date | NORMALISE_NUMERIC | 1 | 1 | **100.0%** |
| en | company_name | TRANSLATE_NORMALISE | 3 | 4 | **75.0%** |
| en | date | NORMALISE_NUMERIC | 0 | 1 | **0.0%** |
| en | email | PRESERVE | 1 | 1 | **100.0%** |
| en | free_text | TRANSLATE_NORMALISE | 0 | 1 | **0.0%** |
| en | id_number | PRESERVE_NORMALISE_SCRIPT | 0 | 2 | **0.0%** |
| en | passport_no | PRESERVE | 5 | 5 | **100.0%** |
| en | person_name | TRANSLITERATE | 19 | 19 | **100.0%** |
| en | phone_number | NORMALISE_NUMERIC | 0 | 1 | **0.0%** |
| en | reference_no | PRESERVE | 0 | 1 | **0.0%** |
| en | registration_no | PRESERVE | 1 | 1 | **100.0%** |
| en | tax_id | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| en | telephone | NORMALISE_NUMERIC | 0 | 1 | **0.0%** |
| es | address | NORMALISE | 1 | 1 | **100.0%** |
| es | address | TRANSLATE_NORMALISE | 6 | 6 | **100.0%** |
| es | alias | TRANSLATE_ANALYST | 0 | 1 | **0.0%** |
| es | alias | TRANSLITERATE | 1 | 1 | **100.0%** |
| es | company_name | TRANSLATE_NORMALISE | 4 | 4 | **100.0%** |
| es | date | NORMALISE | 0 | 1 | **0.0%** |
| es | email | PRESERVE | 1 | 1 | **100.0%** |
| es | free_text | TRANSLATE_NORMALISE | 0 | 1 | **0.0%** |
| es | id_number | NORMALISE | 0 | 1 | **0.0%** |
| es | id_number | PRESERVE | 0 | 1 | **0.0%** |
| es | passport_no | PRESERVE | 4 | 5 | **80.0%** |
| es | person_name | TRANSLITERATE | 19 | 19 | **100.0%** |
| es | phone_number | NORMALISE | 0 | 1 | **0.0%** |
| es | reference_no | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| es | registration_no | PRESERVE | 0 | 1 | **0.0%** |
| es | tax_id | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| fr | address | NORMALISE | 1 | 1 | **100.0%** |
| fr | address | TRANSLATE_NORMALISE | 5 | 6 | **83.3%** |
| fr | alias | TRANSLATE_ANALYST | 0 | 1 | **0.0%** |
| fr | alias | TRANSLITERATE | 0 | 1 | **0.0%** |
| fr | company_name | TRANSLATE_NORMALISE | 4 | 4 | **100.0%** |
| fr | date | NORMALISE | 0 | 1 | **0.0%** |
| fr | free_text | TRANSLATE_NORMALISE | 0 | 1 | **0.0%** |
| fr | id_number | NORMALISE | 0 | 1 | **0.0%** |
| fr | id_number | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| fr | passport_no | PRESERVE | 4 | 5 | **80.0%** |
| fr | person_name | TRANSLITERATE | 19 | 19 | **100.0%** |
| fr | phone_number | NORMALISE | 0 | 1 | **0.0%** |
| fr | reference_no | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| fr | registration_no | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| fr | tax_id | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| it | address | NORMALISE | 1 | 1 | **100.0%** |
| it | address | TRANSLATE_NORMALISE | 6 | 6 | **100.0%** |
| it | alias | TRANSLATE_ANALYST | 0 | 1 | **0.0%** |
| it | alias | TRANSLITERATE | 1 | 1 | **100.0%** |
| it | company_name | TRANSLATE_NORMALISE | 4 | 4 | **100.0%** |
| it | date | NORMALISE | 0 | 1 | **0.0%** |
| it | email | PRESERVE | 1 | 1 | **100.0%** |
| it | free_text | TRANSLATE_NORMALISE | 0 | 1 | **0.0%** |
| it | id_number | PRESERVE | 0 | 2 | **0.0%** |
| it | passport_no | PRESERVE | 3 | 4 | **75.0%** |
| it | passport_no | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| it | person_name | TRANSLITERATE | 19 | 19 | **100.0%** |
| it | phone_number | NORMALISE | 0 | 1 | **0.0%** |
| it | reference_no | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| it | registration_no | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| it | tax_id | PRESERVE | 0 | 1 | **0.0%** |
| ja | address | TRANSLATE_NORMALISE | 3 | 7 | **42.9%** |
| ja | alias | TRANSLATE_ANALYST | 0 | 1 | **0.0%** |
| ja | alias | TRANSLITERATE | 1 | 1 | **100.0%** |
| ja | company_name | TRANSLATE_NORMALISE | 4 | 4 | **100.0%** |
| ja | date | NORMALISE_NUMERIC | 0 | 1 | **0.0%** |
| ja | free_text | TRANSLATE_NORMALISE | 0 | 1 | **0.0%** |
| ja | id_number | FLAG_REVIEW | 0 | 1 | **0.0%** |
| ja | id_number | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| ja | passport_no | PRESERVE | 5 | 5 | **100.0%** |
| ja | person_name | TRANSLITERATE | 18 | 19 | **94.7%** |
| ja | phone_number | NORMALISE_NUMERIC | 0 | 1 | **0.0%** |
| ja | reference_no | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| ja | registration_no | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| ja | tax_id | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| ja | telephone | NORMALISE_NUMERIC | 0 | 1 | **0.0%** |
| ko | address | NORMALISE | 0 | 1 | **0.0%** |
| ko | address | TRANSLATE_NORMALISE | 3 | 6 | **50.0%** |
| ko | alias | TRANSLATE_ANALYST | 0 | 1 | **0.0%** |
| ko | alias | TRANSLITERATE | 0 | 1 | **0.0%** |
| ko | company_name | TRANSLATE_NORMALISE | 4 | 4 | **100.0%** |
| ko | date | NORMALISE | 0 | 1 | **0.0%** |
| ko | email | PRESERVE | 1 | 1 | **100.0%** |
| ko | free_text | TRANSLATE_NORMALISE | 0 | 1 | **0.0%** |
| ko | id_number | NORMALISE | 0 | 1 | **0.0%** |
| ko | id_number | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| ko | passport_no | PRESERVE | 3 | 4 | **75.0%** |
| ko | passport_no | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| ko | person_name | TRANSLITERATE | 18 | 19 | **94.7%** |
| ko | phone_number | NORMALISE | 0 | 1 | **0.0%** |
| ko | reference_no | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| ko | registration_no | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| ko | tax_id | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| ko | telephone | NORMALISE_NUMERIC | 0 | 1 | **0.0%** |
| ru | address | TRANSLATE_NORMALISE | 0 | 7 | **0.0%** |
| ru | alias | TRANSLATE_ANALYST | 0 | 2 | **0.0%** |
| ru | birth_date | NORMALISE_NUMERIC | 1 | 1 | **100.0%** |
| ru | company_name | TRANSLATE_NORMALISE | 3 | 4 | **75.0%** |
| ru | date | NORMALISE_NUMERIC | 1 | 1 | **100.0%** |
| ru | email | PRESERVE | 1 | 1 | **100.0%** |
| ru | free_text | TRANSLATE_NORMALISE | 0 | 1 | **0.0%** |
| ru | id_number | PRESERVE_NORMALISE_SCRIPT | 0 | 2 | **0.0%** |
| ru | passport_no | PRESERVE | 4 | 4 | **100.0%** |
| ru | passport_no | PRESERVE_NORMALISE_SCRIPT | 1 | 1 | **100.0%** |
| ru | person_name | TRANSLITERATE | 14 | 19 | **73.7%** |
| ru | phone_number | NORMALISE_NUMERIC | 0 | 1 | **0.0%** |
| ru | reference_no | FLAG_REVIEW | 0 | 1 | **0.0%** |
| ru | registration_no | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| ru | tax_id | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| ru | telephone | NORMALISE_NUMERIC | 0 | 1 | **0.0%** |
| zh | address | FLAG_REVIEW | 0 | 1 | **0.0%** |
| zh | address | TRANSLATE_NORMALISE | 0 | 6 | **0.0%** |
| zh | alias | TRANSLATE_ANALYST | 0 | 2 | **0.0%** |
| zh | company_name | TRANSLATE_NORMALISE | 2 | 4 | **50.0%** |
| zh | date | NORMALISE_NUMERIC | 0 | 1 | **0.0%** |
| zh | email | PRESERVE | 1 | 1 | **100.0%** |
| zh | free_text | TRANSLATE_NORMALISE | 0 | 1 | **0.0%** |
| zh | id_number | PRESERVE_NORMALISE_SCRIPT | 0 | 2 | **0.0%** |
| zh | passport_no | PRESERVE | 5 | 5 | **100.0%** |
| zh | person_name | TRANSLITERATE | 19 | 19 | **100.0%** |
| zh | phone_number | NORMALISE_NUMERIC | 0 | 1 | **0.0%** |
| zh | reference_no | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| zh | registration_no | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| zh | tax_id | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| zh | telephone | NORMALISE_NUMERIC | 0 | 1 | **0.0%** |

---

## 7. Test Dataset Performance Results

*Measured on 2 April 2026, pipeline v3, model gpt-4o, temperature=0.*
*528 cases across 11 languages (48 cases per language) from `data/test_dataset.csv`.*

### Overall accuracy
**67.2% — 355 correct out of 528 cases**

---

### By language

| Language | Correct | Total | Accuracy |
|---|---|---|---|
| Arabic (ar) | 30 | 48 | **62.5%** |
| German (de) | 38 | 48 | **79.2%** |
| Greek (el) | 29 | 48 | **60.4%** |
| English (en) | 39 | 48 | **81.2%** |
| Spanish (es) | 33 | 48 | **68.8%** |
| French (fr) | 36 | 48 | **75.0%** |
| Italian (it) | 36 | 48 | **75.0%** |
| Japanese (ja) | 29 | 48 | **60.4%** |
| Korean (ko) | 27 | 48 | **56.2%** |
| Russian/Ukrainian (ru) | 28 | 48 | **58.3%** |
| Chinese (zh) | 30 | 48 | **62.5%** |

---

### By expected treatment

| Treatment | Correct | Total | Accuracy |
|---|---|---|---|
| TRANSLITERATE | 202 | 222 | **91.0%** |
| TRANSLATE_NORMALISE | 73 | 131 | **55.7%** |
| PRESERVE | 62 | 66 | **93.9%** |
| NORMALISE_NUMERIC | 16 | 44 | **36.4%** |
| TRANSLATE_ANALYST | 2 | 10 | **20.0%** |
| PRESERVE_NORMALISE_SCRIPT | 0 | 55 | **0.0%** |

---

### By language × field type

| Language | Field type | Correct | Total | Accuracy |
|---|---|---|---|---|
| ar | address | 0 | 7 | **0.0%** |
| ar | alias | 2 | 2 | **100.0%** |
| ar | birth_date | 1 | 1 | **100.0%** |
| ar | company_name | 3 | 4 | **75.0%** |
| ar | date | 0 | 1 | **0.0%** |
| ar | email | 1 | 1 | **100.0%** |
| ar | free_text | 0 | 1 | **0.0%** |
| ar | id_number | 0 | 2 | **0.0%** |
| ar | passport_no | 5 | 5 | **100.0%** |
| ar | person_name | 16 | 19 | **84.2%** |
| ar | phone_number | 1 | 1 | **100.0%** |
| ar | reference_no | 0 | 1 | **0.0%** |
| ar | registration_no | 0 | 1 | **0.0%** |
| ar | tax_id | 0 | 1 | **0.0%** |
| ar | telephone | 1 | 1 | **100.0%** |
| de | address | 7 | 7 | **100.0%** |
| de | alias | 1 | 2 | **50.0%** |
| de | birth_date | 1 | 1 | **100.0%** |
| de | company_name | 4 | 4 | **100.0%** |
| de | date | 1 | 1 | **100.0%** |
| de | email | 1 | 1 | **100.0%** |
| de | free_text | 0 | 1 | **0.0%** |
| de | id_number | 0 | 2 | **0.0%** |
| de | passport_no | 4 | 5 | **80.0%** |
| de | person_name | 19 | 19 | **100.0%** |
| de | phone_number | 0 | 1 | **0.0%** |
| de | reference_no | 0 | 1 | **0.0%** |
| de | registration_no | 0 | 1 | **0.0%** |
| de | tax_id | 0 | 1 | **0.0%** |
| de | telephone | 0 | 1 | **0.0%** |
| el | address | 2 | 7 | **28.6%** |
| el | alias | 0 | 2 | **0.0%** |
| el | birth_date | 1 | 1 | **100.0%** |
| el | company_name | 4 | 4 | **100.0%** |
| el | date | 1 | 1 | **100.0%** |
| el | email | 1 | 1 | **100.0%** |
| el | free_text | 0 | 1 | **0.0%** |
| el | id_number | 0 | 2 | **0.0%** |
| el | passport_no | 4 | 5 | **80.0%** |
| el | person_name | 16 | 19 | **84.2%** |
| el | phone_number | 0 | 1 | **0.0%** |
| el | reference_no | 0 | 1 | **0.0%** |
| el | registration_no | 0 | 1 | **0.0%** |
| el | tax_id | 0 | 1 | **0.0%** |
| el | telephone | 0 | 1 | **0.0%** |
| en | address | 7 | 7 | **100.0%** |
| en | alias | 2 | 2 | **100.0%** |
| en | birth_date | 0 | 1 | **0.0%** |
| en | company_name | 4 | 4 | **100.0%** |
| en | date | 1 | 1 | **100.0%** |
| en | email | 1 | 1 | **100.0%** |
| en | free_text | 0 | 1 | **0.0%** |
| en | id_number | 0 | 2 | **0.0%** |
| en | passport_no | 5 | 5 | **100.0%** |
| en | person_name | 18 | 19 | **94.7%** |
| en | phone_number | 0 | 1 | **0.0%** |
| en | reference_no | 0 | 1 | **0.0%** |
| en | registration_no | 1 | 1 | **100.0%** |
| en | tax_id | 0 | 1 | **0.0%** |
| en | telephone | 0 | 1 | **0.0%** |
| es | address | 3 | 7 | **42.9%** |
| es | alias | 1 | 2 | **50.0%** |
| es | birth_date | 1 | 1 | **100.0%** |
| es | company_name | 2 | 4 | **50.0%** |
| es | date | 1 | 1 | **100.0%** |
| es | email | 1 | 1 | **100.0%** |
| es | free_text | 0 | 1 | **0.0%** |
| es | id_number | 0 | 2 | **0.0%** |
| es | passport_no | 5 | 5 | **100.0%** |
| es | person_name | 19 | 19 | **100.0%** |
| es | phone_number | 0 | 1 | **0.0%** |
| es | reference_no | 0 | 1 | **0.0%** |
| es | registration_no | 0 | 1 | **0.0%** |
| es | tax_id | 0 | 1 | **0.0%** |
| es | telephone | 0 | 1 | **0.0%** |
| fr | address | 6 | 7 | **85.7%** |
| fr | alias | 1 | 2 | **50.0%** |
| fr | birth_date | 1 | 1 | **100.0%** |
| fr | company_name | 3 | 4 | **75.0%** |
| fr | date | 1 | 1 | **100.0%** |
| fr | email | 1 | 1 | **100.0%** |
| fr | free_text | 0 | 1 | **0.0%** |
| fr | id_number | 0 | 2 | **0.0%** |
| fr | passport_no | 4 | 5 | **80.0%** |
| fr | person_name | 19 | 19 | **100.0%** |
| fr | phone_number | 0 | 1 | **0.0%** |
| fr | reference_no | 0 | 1 | **0.0%** |
| fr | registration_no | 0 | 1 | **0.0%** |
| fr | tax_id | 0 | 1 | **0.0%** |
| fr | telephone | 0 | 1 | **0.0%** |
| it | address | 7 | 7 | **100.0%** |
| it | alias | 1 | 2 | **50.0%** |
| it | birth_date | 1 | 1 | **100.0%** |
| it | company_name | 2 | 4 | **50.0%** |
| it | date | 1 | 1 | **100.0%** |
| it | email | 1 | 1 | **100.0%** |
| it | free_text | 0 | 1 | **0.0%** |
| it | id_number | 0 | 2 | **0.0%** |
| it | passport_no | 4 | 5 | **80.0%** |
| it | person_name | 19 | 19 | **100.0%** |
| it | phone_number | 0 | 1 | **0.0%** |
| it | reference_no | 0 | 1 | **0.0%** |
| it | registration_no | 0 | 1 | **0.0%** |
| it | tax_id | 0 | 1 | **0.0%** |
| it | telephone | 0 | 1 | **0.0%** |
| ja | address | 2 | 7 | **28.6%** |
| ja | alias | 1 | 2 | **50.0%** |
| ja | birth_date | 0 | 1 | **0.0%** |
| ja | company_name | 4 | 4 | **100.0%** |
| ja | date | 0 | 1 | **0.0%** |
| ja | email | 1 | 1 | **100.0%** |
| ja | free_text | 0 | 1 | **0.0%** |
| ja | id_number | 0 | 2 | **0.0%** |
| ja | passport_no | 5 | 5 | **100.0%** |
| ja | person_name | 16 | 19 | **84.2%** |
| ja | phone_number | 0 | 1 | **0.0%** |
| ja | reference_no | 0 | 1 | **0.0%** |
| ja | registration_no | 0 | 1 | **0.0%** |
| ja | tax_id | 0 | 1 | **0.0%** |
| ja | telephone | 0 | 1 | **0.0%** |
| ko | address | 3 | 7 | **42.9%** |
| ko | alias | 0 | 2 | **0.0%** |
| ko | birth_date | 0 | 1 | **0.0%** |
| ko | company_name | 4 | 4 | **100.0%** |
| ko | date | 0 | 1 | **0.0%** |
| ko | email | 1 | 1 | **100.0%** |
| ko | free_text | 0 | 1 | **0.0%** |
| ko | id_number | 0 | 2 | **0.0%** |
| ko | passport_no | 4 | 5 | **80.0%** |
| ko | person_name | 15 | 19 | **78.9%** |
| ko | phone_number | 0 | 1 | **0.0%** |
| ko | reference_no | 0 | 1 | **0.0%** |
| ko | registration_no | 0 | 1 | **0.0%** |
| ko | tax_id | 0 | 1 | **0.0%** |
| ko | telephone | 0 | 1 | **0.0%** |
| ru | address | 2 | 7 | **28.6%** |
| ru | alias | 1 | 2 | **50.0%** |
| ru | birth_date | 1 | 1 | **100.0%** |
| ru | company_name | 1 | 4 | **25.0%** |
| ru | date | 1 | 1 | **100.0%** |
| ru | email | 1 | 1 | **100.0%** |
| ru | free_text | 0 | 1 | **0.0%** |
| ru | id_number | 0 | 2 | **0.0%** |
| ru | passport_no | 5 | 5 | **100.0%** |
| ru | person_name | 16 | 19 | **84.2%** |
| ru | phone_number | 0 | 1 | **0.0%** |
| ru | reference_no | 0 | 1 | **0.0%** |
| ru | registration_no | 0 | 1 | **0.0%** |
| ru | tax_id | 0 | 1 | **0.0%** |
| ru | telephone | 0 | 1 | **0.0%** |
| zh | address | 0 | 7 | **0.0%** |
| zh | alias | 2 | 2 | **100.0%** |
| zh | birth_date | 0 | 1 | **0.0%** |
| zh | company_name | 4 | 4 | **100.0%** |
| zh | date | 0 | 1 | **0.0%** |
| zh | email | 1 | 1 | **100.0%** |
| zh | free_text | 0 | 1 | **0.0%** |
| zh | id_number | 0 | 2 | **0.0%** |
| zh | passport_no | 5 | 5 | **100.0%** |
| zh | person_name | 18 | 19 | **94.7%** |
| zh | phone_number | 0 | 1 | **0.0%** |
| zh | reference_no | 0 | 1 | **0.0%** |
| zh | registration_no | 0 | 1 | **0.0%** |
| zh | tax_id | 0 | 1 | **0.0%** |
| zh | telephone | 0 | 1 | **0.0%** |

---

### By language × expected treatment

| Language | Treatment | Correct | Total | Accuracy |
|---|---|---|---|---|
| ar | NORMALISE_NUMERIC | 3 | 4 | **75.0%** |
| ar | PRESERVE | 6 | 6 | **100.0%** |
| ar | PRESERVE_NORMALISE_SCRIPT | 0 | 5 | **0.0%** |
| ar | TRANSLATE_NORMALISE | 3 | 12 | **25.0%** |
| ar | TRANSLITERATE | 18 | 21 | **85.7%** |
| de | NORMALISE_NUMERIC | 2 | 4 | **50.0%** |
| de | PRESERVE | 5 | 5 | **100.0%** |
| de | PRESERVE_NORMALISE_SCRIPT | 0 | 6 | **0.0%** |
| de | TRANSLATE_ANALYST | 0 | 1 | **0.0%** |
| de | TRANSLATE_NORMALISE | 11 | 12 | **91.7%** |
| de | TRANSLITERATE | 20 | 20 | **100.0%** |
| el | NORMALISE_NUMERIC | 2 | 4 | **50.0%** |
| el | PRESERVE | 5 | 6 | **83.3%** |
| el | PRESERVE_NORMALISE_SCRIPT | 0 | 5 | **0.0%** |
| el | TRANSLATE_ANALYST | 0 | 1 | **0.0%** |
| el | TRANSLATE_NORMALISE | 5 | 11 | **45.5%** |
| el | TRANSLITERATE | 17 | 21 | **81.0%** |
| en | NORMALISE_NUMERIC | 1 | 4 | **25.0%** |
| en | PRESERVE | 7 | 8 | **87.5%** |
| en | PRESERVE_NORMALISE_SCRIPT | 0 | 3 | **0.0%** |
| en | TRANSLATE_ANALYST | 1 | 1 | **100.0%** |
| en | TRANSLATE_NORMALISE | 11 | 12 | **91.7%** |
| en | TRANSLITERATE | 19 | 20 | **95.0%** |
| es | NORMALISE_NUMERIC | 2 | 4 | **50.0%** |
| es | PRESERVE | 6 | 7 | **85.7%** |
| es | PRESERVE_NORMALISE_SCRIPT | 0 | 4 | **0.0%** |
| es | TRANSLATE_ANALYST | 0 | 1 | **0.0%** |
| es | TRANSLATE_NORMALISE | 5 | 12 | **41.7%** |
| es | TRANSLITERATE | 20 | 20 | **100.0%** |
| fr | NORMALISE_NUMERIC | 2 | 4 | **50.0%** |
| fr | PRESERVE | 5 | 5 | **100.0%** |
| fr | PRESERVE_NORMALISE_SCRIPT | 0 | 6 | **0.0%** |
| fr | TRANSLATE_ANALYST | 0 | 1 | **0.0%** |
| fr | TRANSLATE_NORMALISE | 9 | 12 | **75.0%** |
| fr | TRANSLITERATE | 20 | 20 | **100.0%** |
| it | NORMALISE_NUMERIC | 2 | 4 | **50.0%** |
| it | PRESERVE | 5 | 6 | **83.3%** |
| it | PRESERVE_NORMALISE_SCRIPT | 0 | 5 | **0.0%** |
| it | TRANSLATE_ANALYST | 0 | 1 | **0.0%** |
| it | TRANSLATE_NORMALISE | 9 | 12 | **75.0%** |
| it | TRANSLITERATE | 20 | 20 | **100.0%** |
| ja | NORMALISE_NUMERIC | 0 | 4 | **0.0%** |
| ja | PRESERVE | 6 | 6 | **100.0%** |
| ja | PRESERVE_NORMALISE_SCRIPT | 0 | 5 | **0.0%** |
| ja | TRANSLATE_ANALYST | 0 | 1 | **0.0%** |
| ja | TRANSLATE_NORMALISE | 6 | 12 | **50.0%** |
| ja | TRANSLITERATE | 17 | 20 | **85.0%** |
| ko | NORMALISE_NUMERIC | 0 | 4 | **0.0%** |
| ko | PRESERVE | 5 | 5 | **100.0%** |
| ko | PRESERVE_NORMALISE_SCRIPT | 0 | 6 | **0.0%** |
| ko | TRANSLATE_ANALYST | 0 | 1 | **0.0%** |
| ko | TRANSLATE_NORMALISE | 7 | 12 | **58.3%** |
| ko | TRANSLITERATE | 15 | 20 | **75.0%** |
| ru | NORMALISE_NUMERIC | 2 | 4 | **50.0%** |
| ru | PRESERVE | 6 | 6 | **100.0%** |
| ru | PRESERVE_NORMALISE_SCRIPT | 0 | 5 | **0.0%** |
| ru | TRANSLATE_ANALYST | 0 | 1 | **0.0%** |
| ru | TRANSLATE_NORMALISE | 3 | 12 | **25.0%** |
| ru | TRANSLITERATE | 17 | 20 | **85.0%** |
| zh | NORMALISE_NUMERIC | 0 | 4 | **0.0%** |
| zh | PRESERVE | 6 | 6 | **100.0%** |
| zh | PRESERVE_NORMALISE_SCRIPT | 0 | 5 | **0.0%** |
| zh | TRANSLATE_ANALYST | 1 | 1 | **100.0%** |
| zh | TRANSLATE_NORMALISE | 4 | 12 | **33.3%** |
| zh | TRANSLITERATE | 19 | 20 | **95.0%** |

---

### By language × field type × expected treatment

| Language | Field type | Treatment | Correct | Total | Accuracy |
|---|---|---|---|---|---|
| ar | address | TRANSLATE_NORMALISE | 0 | 7 | **0.0%** |
| ar | alias | TRANSLITERATE | 2 | 2 | **100.0%** |
| ar | birth_date | NORMALISE_NUMERIC | 1 | 1 | **100.0%** |
| ar | company_name | TRANSLATE_NORMALISE | 3 | 4 | **75.0%** |
| ar | date | NORMALISE_NUMERIC | 0 | 1 | **0.0%** |
| ar | email | PRESERVE | 1 | 1 | **100.0%** |
| ar | free_text | TRANSLATE_NORMALISE | 0 | 1 | **0.0%** |
| ar | id_number | PRESERVE_NORMALISE_SCRIPT | 0 | 2 | **0.0%** |
| ar | passport_no | PRESERVE | 5 | 5 | **100.0%** |
| ar | person_name | TRANSLITERATE | 16 | 19 | **84.2%** |
| ar | phone_number | NORMALISE_NUMERIC | 1 | 1 | **100.0%** |
| ar | reference_no | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| ar | registration_no | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| ar | tax_id | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| ar | telephone | NORMALISE_NUMERIC | 1 | 1 | **100.0%** |
| de | address | TRANSLATE_NORMALISE | 7 | 7 | **100.0%** |
| de | alias | TRANSLATE_ANALYST | 0 | 1 | **0.0%** |
| de | alias | TRANSLITERATE | 1 | 1 | **100.0%** |
| de | birth_date | NORMALISE_NUMERIC | 1 | 1 | **100.0%** |
| de | company_name | TRANSLATE_NORMALISE | 4 | 4 | **100.0%** |
| de | date | NORMALISE_NUMERIC | 1 | 1 | **100.0%** |
| de | email | PRESERVE | 1 | 1 | **100.0%** |
| de | free_text | TRANSLATE_NORMALISE | 0 | 1 | **0.0%** |
| de | id_number | PRESERVE_NORMALISE_SCRIPT | 0 | 2 | **0.0%** |
| de | passport_no | PRESERVE | 4 | 4 | **100.0%** |
| de | passport_no | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| de | person_name | TRANSLITERATE | 19 | 19 | **100.0%** |
| de | phone_number | NORMALISE_NUMERIC | 0 | 1 | **0.0%** |
| de | reference_no | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| de | registration_no | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| de | tax_id | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| de | telephone | NORMALISE_NUMERIC | 0 | 1 | **0.0%** |
| el | address | TRANSLATE_NORMALISE | 2 | 7 | **28.6%** |
| el | alias | TRANSLATE_ANALYST | 0 | 1 | **0.0%** |
| el | alias | TRANSLITERATE | 0 | 1 | **0.0%** |
| el | birth_date | NORMALISE_NUMERIC | 1 | 1 | **100.0%** |
| el | company_name | TRANSLATE_NORMALISE | 3 | 3 | **100.0%** |
| el | company_name | TRANSLITERATE | 1 | 1 | **100.0%** |
| el | date | NORMALISE_NUMERIC | 1 | 1 | **100.0%** |
| el | email | PRESERVE | 1 | 1 | **100.0%** |
| el | free_text | TRANSLATE_NORMALISE | 0 | 1 | **0.0%** |
| el | id_number | PRESERVE | 0 | 1 | **0.0%** |
| el | id_number | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| el | passport_no | PRESERVE | 4 | 4 | **100.0%** |
| el | passport_no | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| el | person_name | TRANSLITERATE | 16 | 19 | **84.2%** |
| el | phone_number | NORMALISE_NUMERIC | 0 | 1 | **0.0%** |
| el | reference_no | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| el | registration_no | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| el | tax_id | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| el | telephone | NORMALISE_NUMERIC | 0 | 1 | **0.0%** |
| en | address | TRANSLATE_NORMALISE | 7 | 7 | **100.0%** |
| en | alias | TRANSLATE_ANALYST | 1 | 1 | **100.0%** |
| en | alias | TRANSLITERATE | 1 | 1 | **100.0%** |
| en | birth_date | NORMALISE_NUMERIC | 0 | 1 | **0.0%** |
| en | company_name | TRANSLATE_NORMALISE | 4 | 4 | **100.0%** |
| en | date | NORMALISE_NUMERIC | 1 | 1 | **100.0%** |
| en | email | PRESERVE | 1 | 1 | **100.0%** |
| en | free_text | TRANSLATE_NORMALISE | 0 | 1 | **0.0%** |
| en | id_number | PRESERVE_NORMALISE_SCRIPT | 0 | 2 | **0.0%** |
| en | passport_no | PRESERVE | 5 | 5 | **100.0%** |
| en | person_name | TRANSLITERATE | 18 | 19 | **94.7%** |
| en | phone_number | NORMALISE_NUMERIC | 0 | 1 | **0.0%** |
| en | reference_no | PRESERVE | 0 | 1 | **0.0%** |
| en | registration_no | PRESERVE | 1 | 1 | **100.0%** |
| en | tax_id | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| en | telephone | NORMALISE_NUMERIC | 0 | 1 | **0.0%** |
| es | address | TRANSLATE_NORMALISE | 3 | 7 | **42.9%** |
| es | alias | TRANSLATE_ANALYST | 0 | 1 | **0.0%** |
| es | alias | TRANSLITERATE | 1 | 1 | **100.0%** |
| es | birth_date | NORMALISE_NUMERIC | 1 | 1 | **100.0%** |
| es | company_name | TRANSLATE_NORMALISE | 2 | 4 | **50.0%** |
| es | date | NORMALISE_NUMERIC | 1 | 1 | **100.0%** |
| es | email | PRESERVE | 1 | 1 | **100.0%** |
| es | free_text | TRANSLATE_NORMALISE | 0 | 1 | **0.0%** |
| es | id_number | PRESERVE | 0 | 1 | **0.0%** |
| es | id_number | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| es | passport_no | PRESERVE | 5 | 5 | **100.0%** |
| es | person_name | TRANSLITERATE | 19 | 19 | **100.0%** |
| es | phone_number | NORMALISE_NUMERIC | 0 | 1 | **0.0%** |
| es | reference_no | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| es | registration_no | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| es | tax_id | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| es | telephone | NORMALISE_NUMERIC | 0 | 1 | **0.0%** |
| fr | address | TRANSLATE_NORMALISE | 6 | 7 | **85.7%** |
| fr | alias | TRANSLATE_ANALYST | 0 | 1 | **0.0%** |
| fr | alias | TRANSLITERATE | 1 | 1 | **100.0%** |
| fr | birth_date | NORMALISE_NUMERIC | 1 | 1 | **100.0%** |
| fr | company_name | TRANSLATE_NORMALISE | 3 | 4 | **75.0%** |
| fr | date | NORMALISE_NUMERIC | 1 | 1 | **100.0%** |
| fr | email | PRESERVE | 1 | 1 | **100.0%** |
| fr | free_text | TRANSLATE_NORMALISE | 0 | 1 | **0.0%** |
| fr | id_number | PRESERVE_NORMALISE_SCRIPT | 0 | 2 | **0.0%** |
| fr | passport_no | PRESERVE | 4 | 4 | **100.0%** |
| fr | passport_no | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| fr | person_name | TRANSLITERATE | 19 | 19 | **100.0%** |
| fr | phone_number | NORMALISE_NUMERIC | 0 | 1 | **0.0%** |
| fr | reference_no | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| fr | registration_no | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| fr | tax_id | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| fr | telephone | NORMALISE_NUMERIC | 0 | 1 | **0.0%** |
| it | address | TRANSLATE_NORMALISE | 7 | 7 | **100.0%** |
| it | alias | TRANSLATE_ANALYST | 0 | 1 | **0.0%** |
| it | alias | TRANSLITERATE | 1 | 1 | **100.0%** |
| it | birth_date | NORMALISE_NUMERIC | 1 | 1 | **100.0%** |
| it | company_name | TRANSLATE_NORMALISE | 2 | 4 | **50.0%** |
| it | date | NORMALISE_NUMERIC | 1 | 1 | **100.0%** |
| it | email | PRESERVE | 1 | 1 | **100.0%** |
| it | free_text | TRANSLATE_NORMALISE | 0 | 1 | **0.0%** |
| it | id_number | PRESERVE | 0 | 1 | **0.0%** |
| it | id_number | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| it | passport_no | PRESERVE | 4 | 4 | **100.0%** |
| it | passport_no | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| it | person_name | TRANSLITERATE | 19 | 19 | **100.0%** |
| it | phone_number | NORMALISE_NUMERIC | 0 | 1 | **0.0%** |
| it | reference_no | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| it | registration_no | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| it | tax_id | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| it | telephone | NORMALISE_NUMERIC | 0 | 1 | **0.0%** |
| ja | address | TRANSLATE_NORMALISE | 2 | 7 | **28.6%** |
| ja | alias | TRANSLATE_ANALYST | 0 | 1 | **0.0%** |
| ja | alias | TRANSLITERATE | 1 | 1 | **100.0%** |
| ja | birth_date | NORMALISE_NUMERIC | 0 | 1 | **0.0%** |
| ja | company_name | TRANSLATE_NORMALISE | 4 | 4 | **100.0%** |
| ja | date | NORMALISE_NUMERIC | 0 | 1 | **0.0%** |
| ja | email | PRESERVE | 1 | 1 | **100.0%** |
| ja | free_text | TRANSLATE_NORMALISE | 0 | 1 | **0.0%** |
| ja | id_number | PRESERVE_NORMALISE_SCRIPT | 0 | 2 | **0.0%** |
| ja | passport_no | PRESERVE | 5 | 5 | **100.0%** |
| ja | person_name | TRANSLITERATE | 16 | 19 | **84.2%** |
| ja | phone_number | NORMALISE_NUMERIC | 0 | 1 | **0.0%** |
| ja | reference_no | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| ja | registration_no | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| ja | tax_id | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| ja | telephone | NORMALISE_NUMERIC | 0 | 1 | **0.0%** |
| ko | address | TRANSLATE_NORMALISE | 3 | 7 | **42.9%** |
| ko | alias | TRANSLATE_ANALYST | 0 | 1 | **0.0%** |
| ko | alias | TRANSLITERATE | 0 | 1 | **0.0%** |
| ko | birth_date | NORMALISE_NUMERIC | 0 | 1 | **0.0%** |
| ko | company_name | TRANSLATE_NORMALISE | 4 | 4 | **100.0%** |
| ko | date | NORMALISE_NUMERIC | 0 | 1 | **0.0%** |
| ko | email | PRESERVE | 1 | 1 | **100.0%** |
| ko | free_text | TRANSLATE_NORMALISE | 0 | 1 | **0.0%** |
| ko | id_number | PRESERVE_NORMALISE_SCRIPT | 0 | 2 | **0.0%** |
| ko | passport_no | PRESERVE | 4 | 4 | **100.0%** |
| ko | passport_no | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| ko | person_name | TRANSLITERATE | 15 | 19 | **78.9%** |
| ko | phone_number | NORMALISE_NUMERIC | 0 | 1 | **0.0%** |
| ko | reference_no | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| ko | registration_no | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| ko | tax_id | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| ko | telephone | NORMALISE_NUMERIC | 0 | 1 | **0.0%** |
| ru | address | TRANSLATE_NORMALISE | 2 | 7 | **28.6%** |
| ru | alias | TRANSLATE_ANALYST | 0 | 1 | **0.0%** |
| ru | alias | TRANSLITERATE | 1 | 1 | **100.0%** |
| ru | birth_date | NORMALISE_NUMERIC | 1 | 1 | **100.0%** |
| ru | company_name | TRANSLATE_NORMALISE | 1 | 4 | **25.0%** |
| ru | date | NORMALISE_NUMERIC | 1 | 1 | **100.0%** |
| ru | email | PRESERVE | 1 | 1 | **100.0%** |
| ru | free_text | TRANSLATE_NORMALISE | 0 | 1 | **0.0%** |
| ru | id_number | PRESERVE_NORMALISE_SCRIPT | 0 | 2 | **0.0%** |
| ru | passport_no | PRESERVE | 5 | 5 | **100.0%** |
| ru | person_name | TRANSLITERATE | 16 | 19 | **84.2%** |
| ru | phone_number | NORMALISE_NUMERIC | 0 | 1 | **0.0%** |
| ru | reference_no | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| ru | registration_no | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| ru | tax_id | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| ru | telephone | NORMALISE_NUMERIC | 0 | 1 | **0.0%** |
| zh | address | TRANSLATE_NORMALISE | 0 | 7 | **0.0%** |
| zh | alias | TRANSLATE_ANALYST | 1 | 1 | **100.0%** |
| zh | alias | TRANSLITERATE | 1 | 1 | **100.0%** |
| zh | birth_date | NORMALISE_NUMERIC | 0 | 1 | **0.0%** |
| zh | company_name | TRANSLATE_NORMALISE | 4 | 4 | **100.0%** |
| zh | date | NORMALISE_NUMERIC | 0 | 1 | **0.0%** |
| zh | email | PRESERVE | 1 | 1 | **100.0%** |
| zh | free_text | TRANSLATE_NORMALISE | 0 | 1 | **0.0%** |
| zh | id_number | PRESERVE_NORMALISE_SCRIPT | 0 | 2 | **0.0%** |
| zh | passport_no | PRESERVE | 5 | 5 | **100.0%** |
| zh | person_name | TRANSLITERATE | 18 | 19 | **94.7%** |
| zh | phone_number | NORMALISE_NUMERIC | 0 | 1 | **0.0%** |
| zh | reference_no | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| zh | registration_no | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| zh | tax_id | PRESERVE_NORMALISE_SCRIPT | 0 | 1 | **0.0%** |
| zh | telephone | NORMALISE_NUMERIC | 0 | 1 | **0.0%** |

---

## 8. Key Failure Patterns (Golden Dataset, April 2026)

The 164 golden-dataset failures and 173 test-dataset failures share the same root causes. The priority-ordered patterns below are based on the language × field type breakdown.

### Pattern 1 — Unimplemented field types (largest category)

`NORMALISE_NUMERIC` (phone numbers, dates, numeric IDs), `PRESERVE_NORMALISE_SCRIPT` (foreign-script ID/reference numbers), `FLAG_REVIEW`, and `NORMALISE` (date formatting, free text) together account for ~100 failures. The pipeline routes these to the LLM which applies formatting rules inconsistently. These field types need dedicated deterministic handlers.

Examples:
- `TEN048 [en|telephone]` expected `12125550198` got `+1 (212) 555-0198` — phone normalisation not yet stripping separators
- `TKO018 [ko|id_number]` expected `8512031234567` got `주민번호 850203-1234567` — non-Latin script label prepended

### Pattern 2 — Address: non-Latin scripts (ru, zh, ja, ar, el, ko address at 0–43%)

The LLM consistently outputs addresses in a different word order and appends script-local administrative suffixes (SHI, KU, QU, UL). This is the single biggest scored category by volume (77 address cases × 2 datasets = ~154 cases, most failing).

Examples:
- `KYC015 [ru|address]` expected `LENINA STREET 10 MOSCOW` got `UL LENINA 10 MOSKVA`
- `KYC044 [ja|address]` expected `OSAKA KITA WARD` got `OSAKA SHI KITA KU`
- `KYC019 [zh|address]` expected `88 JIANGUO ROAD CHAOYANG BEIJING` got `BEIJING SHI CHAOYANG QU JIANGUO LU 88 HAO`

Latin-script languages (de, en, es, fr, it) achieve 85–100% on address via the new deterministic `normalise_address_latin()` handler.

### Pattern 3 — Russian transliteration library (ru person_name at 73.7%)

`transliterate` library renders Я→JA, Ю→JU, МИХ→MIH where BGN/PCGN mandates YA, YU, MIKH. The library also romanises some Belarusian forms differently. A post-processing substitution step partially addressed this (KYC051, KYC057) but multiple cases remain.

### Pattern 4 — Korean given-name romanisation variants (ko person_name at ~90–95%)

Revised Romanization of Korean gives HYEONU where the expected form is HYUNWOO (traditional), MINU where expected is MINWOO, etc. These are valid RR forms that differ from the pre-2000 McCune-Reischauer or traditional spellings used in the dataset's expected column.

### Pattern 5 — Composite alias phrases not fully translated (alias at 0% across multiple languages)

Aliases tagged `TRANSLATE_ANALYST` containing mixed name + descriptor (дит/по прозвищу/又名/γνωστός ως/conocido como) require the descriptor to be translated to English while the name is transliterated. The pipeline either translates both or neither. Requires a dedicated composite alias routing path.

### Pattern 6 — Chinese address reformatting (zh address at 0%)

LLM outputs the full administrative hierarchy in Chinese ordering (city → district → street → number-suffix 号), whereas expected forms use Western ordering (number street district city). The address lenient matcher handles number/street order reversal but not full hierarchy inversion.

### Pattern 7 — Company name: LLM vs screener-form tension (company_name at 50–75%)

The LLM uses internationally-recognised long-form names (GENERALI ASSICURAZIONI SPA, MEDIOBANCA FINANCIAL CREDIT BANK SPA) where the dataset expects the short screener form (GENERALI SPA, MEDIOBANCA SPA). Also: Chinese company brand-name resolution failures (BEIJING ENVISION vs BEIJING VISION, TENGXUN vs TENCENT).

---

## 9. Copilot LLM Output Evaluation

An additional benchmark evaluates how well a general-purpose LLM (without access to the KYC pipeline's rule engine, kanji lookup table, or transliteration library) performs on the same 212 cases when given only the `original_text` and a detailed linguistic prompt.

The test file (`data/copilot_test.csv`) presents each case with only `case_id` and `original_text`; all other columns (`language`, `script`, `field_type`, `treatment`, `transliteration`, `variants`, `english`, `normalised`) are left blank for the LLM to complete. The evaluator (`evaluate_copilot_output.py`) scores the completed `normalised` column against the ground-truth expected values, using the same 6-pass matching logic as the pipeline evaluator.

*Evaluated on 20 March 2026, 212 cases (112 golden + 100 test), gpt-4o, prompt: `data/copilot_test_prompt.md`.*

### Overall accuracy
**88.2% — 187 correct out of 212 cases**

---

### By source dataset

| Dataset | Correct | Total | Accuracy |
|---|---|---|---|
| Golden dataset | 95 | 112 | **84.8%** |
| Test dataset | 92 | 100 | **92.0%** |

---

### By language

| Language | Correct | Total | Accuracy |
|---|---|---|---|
| Arabic (ar) | 35 | 39 | **89.7%** |
| Greek (el) | 37 | 38 | **97.4%** |
| English (en) | 2 | 2 | **100.0%** |
| Japanese (ja) | 43 | 45 | **95.6%** |
| Russian/Ukrainian (ru) | 30 | 38 | **78.9%** |
| Chinese (zh) | 40 | 50 | **80.0%** |

---

### By processing method

| Treatment | Correct | Total | Accuracy |
|---|---|---|---|
| PRESERVE | 19 | 19 | **100.0%** |
| TRANSLATE_COMPOSITE | 3 | 3 | **100.0%** |
| TRANSLITERATE | 132 | 139 | **95.0%** |
| TRANSLATE_NORMALISE | 33 | 51 | **64.7%** |

Notable: the LLM achieves 100% on `TRANSLATE_COMPOSITE` alias phrases — it correctly translates descriptive text like "по прозвищу" and "又名" — which is a category where the automated pipeline (without the composite routing) scores 0%.

---

### By language × field type

| Language | Field type | Correct | Total | Accuracy |
|---|---|---|---|---|
| ar | address | 5 | 6 | 83.3% |
| ar | alias | 4 | 4 | 100.0% |
| ar | company_name | 2 | 2 | 100.0% |
| ar | passport_no | 3 | 3 | 100.0% |
| ar | person_name | 21 | 24 | 87.5% |
| el | address | 9 | 9 | 100.0% |
| el | alias | 1 | 1 | 100.0% |
| el | company_name | 3 | 4 | 75.0% |
| el | email | 2 | 2 | 100.0% |
| el | passport_no | 2 | 2 | 100.0% |
| el | person_name | 20 | 20 | 100.0% |
| en | email | 1 | 1 | 100.0% |
| en | passport_no | 1 | 1 | 100.0% |
| ja | address | 5 | 6 | 83.3% |
| ja | alias | 1 | 1 | 100.0% |
| ja | company_name | 3 | 4 | 75.0% |
| ja | passport_no | 6 | 6 | 100.0% |
| ja | person_name | 28 | 28 | 100.0% |
| ru | address | 1 | 5 | 20.0% |
| ru | alias | 1 | 1 | 100.0% |
| ru | company_name | 1 | 2 | 50.0% |
| ru | passport_no | 2 | 2 | 100.0% |
| ru | person_name | 25 | 28 | 89.3% |
| zh | address | 0 | 8 | 0.0% |
| zh | alias | 1 | 1 | 100.0% |
| zh | company_name | 5 | 7 | 71.4% |
| zh | passport_no | 2 | 2 | 100.0% |
| zh | person_name | 32 | 32 | 100.0% |

---

### Failing cases (25)

| Case ID | Language | Field | Expected | Got | Root cause |
|---|---|---|---|---|---|
| AR012 | ar | person_name | NIHAD IBRAHIM ELSAYED ALNAGGAR | NIHAD IBRAHIM ALSAYYID AL NAJJAR | Classical Arabic form Al-Sayyid Al-Najjar vs Egyptian compound Elsayed Alnaggar |
| AR018 | ar | person_name | YUSUF ABD AL RAHMAN AL KUWAITI | YUSUF ABDULRAHMAN AL KUWAITI | Fused form ABDULRAHMAN vs spaced ABD AL RAHMAN |
| IMG005 | ru | address | YANGITAU HAMLET | YANGITAU | LLM omitted the locality type ("Hamlet" / "Хутор") |
| IMG014 | el | company_name | DEI | PUBLIC POWER CORPORATION | LLM expanded the acronym ΔΕΗ to its full English name; expected screening form is the acronym DEI |
| KYC008 | ja | company_name | TOYOTA CO LTD | TOYOTA MOTOR CORPORATION | LLM used the full official English name; dataset expects the short screener form |
| KYC011 | ru | person_name | EKATERINA SERGEEVNA IVANOVA | YEKATERINA SERGEEVNA IVANOVA | LLM rendered Е as YE word-initially (Yekaterina); expected BGN/PCGN form is Ekaterina |
| KYC015 | ru | address | LENINA STREET 10 MOSCOW | 10 LENIN STREET MOSCOW | Number placed first; LENINA vs LENINA/LENIN (genitive vs nominative) |
| KYC018 | zh | company_name | BEIJING VISION TECHNOLOGY CO LTD | BEIJING ENVISION TECHNOLOGY CO LTD | 远景 rendered as ENVISION (plausible) vs VISION expected |
| KYC019 | zh | address | 88 JIANGUO ROAD CHAOYANG BEIJING | 88 JIANGUO ROAD BEIJING | District name CHAOYANG dropped |
| KYC030 | ru | person_name | DMITRII IVANOV | DMITRIY IVANOV | ii vs iy ending variant for Дмитрий |
| KYC033 | ar | person_name | YUSUF ABDELAZIZ MAHMOUD | YUSUF ABDULAZIZ MAHMOUD | ABDELAZIZ vs ABDULAZIZ — vowel variant in ABD prefix |
| KYC036 | ar | address | BLOCK 3 STREET 12 KUWAIT CITY | BLOCK 3 STREET 12 KUWAIT | "CITY" dropped from Kuwait City |
| KYC044 | ja | address | OSAKA KITA WARD | KITA OSAKA | Word order reversed; WARD omitted |
| KYC055 | ru | company_name | SEVERNY POTOK LLC | NORD STREAM LLC | LLM used the internationally-known brand name Nord Stream; dataset expects literal translation Severny Potok |
| KYC057 | ru | person_name | ANDREI YURYEVICH KOVALEV | ANDREY YURYEVICH KOVALEV | ei vs ey ending for Андрей |
| KYC064 | zh | address | 100 CENTURY AVENUE PUDONG SHANGHAI | 100 CENTURY AVENUE SHANGHAI | District name PUDONG dropped |
| KYC069 | zh | address | 18 TIYU EAST ROAD TIANHE GUANGZHOU | 18 TIYU EAST ROAD GUANGZHOU | District name TIANHE dropped |
| KYC089 | zh | address | 100 SONGREN ROAD XINYI TAIPEI | 100 SONGREN ROAD TAIPEI | District name XINYI dropped |
| KYC090 | zh | address | 27 ZHONGGUANCUN STREET HAIDIAN BEIJING | 27 ZHONGGUANCUN STREET BEIJING | District name HAIDIAN dropped |
| RU006 | ru | address | LENINA STREET 10 MOSCOW | 10 LENIN STREET MOSCOW | Number first; LENINA vs LENINA genitive |
| RU011 | ru | address | NEVSKY PROSPEKT 20 SAINT PETERSBURG | 20 NEVSKY AVENUE SAINT PETERSBURG | Number first; PROSPEKT vs AVENUE; NEVSKY PROSPEKT is the conventional transliterated form |
| ZH005 | zh | company_name | BEIJING VISION TECHNOLOGY CO LTD | BEIJING ENVISION TECHNOLOGY CO LTD | Same 远景→ENVISION vs VISION issue |
| ZH006 | zh | address | 88 JIANGUO ROAD CHAOYANG DISTRICT BEIJING | 88 JIANGUO ROAD BEIJING | District name dropped |
| ZH013 | zh | address | LUJIAZUI FINANCE AND TRADE ZONE PUDONG NEW AREA SHANGHAI | LUJIAZUI SHANGHAI | Heavy truncation — zone and district both dropped |
| ZH020 | zh | address | SCIENCE PARK NANSHAN DISTRICT SHENZHEN GUANGDONG | NANSHAN SHENZHEN | Zone name and province both dropped |

### Pattern analysis of failures

**Chinese address district/zone truncation (9 cases)**
The LLM consistently drops Chinese administrative sub-units (区 = district, 新区 = new area, 经济区 = zone) from the normalised form. The expected screener forms retain these for disambiguation. Fix: the prompt should state explicitly that `区`, `新区` and named zones must be preserved in the `normalised` field.

**Russian address number-first ordering (3 cases: KYC015, RU006, RU011)**
The LLM places the street number before the street name (10 LENINA STREET) whereas the expected form places it after (LENINA STREET 10). The address lenient token-set matcher in the pipeline handles this — the LLM omission is a prompt precision gap.

**Russian person name transliteration variants (3 cases: KYC011, KYC030, KYC057)**
Minor ending differences: Yekaterina vs Ekaterina (Е word-initial), Dmitriy vs Dmitrii (final ий), Andrey vs Andrei (final ей). These are all within the accepted variant family but the LLM chose a form not in the expected variants list.

**Screener form vs brand form conflict (3 cases: KYC008, KYC055, IMG014)**
The LLM used the internationally recognised long-form name (Toyota Motor Corporation, Nord Stream, Public Power Corporation) where the dataset expects a shorter screener form (Toyota Co Ltd, Severny Potok LLC, DEI). Indicates a tension between "natural English" and "screener normalised" that the prompt needs to resolve more forcefully.

**Chinese 远景 mapping (2 cases: KYC018, ZH005)**
ENVISION is a valid translation of 远景 (yuǎnjǐng = "vision/prospect"), but the expected form is VISION. The LLM chose a different but reasonable English equivalent.

---

### Comparative summary — pipeline vs copilot LLM

| Metric | Pipeline (golden) | Pipeline (test) | Copilot LLM (golden) | Copilot LLM (test) |
|---|---|---|---|---|
| Overall accuracy | 88.4% | 89.0% | 84.8% | 92.0% |
| PRESERVE | 100.0% | 100.0% | 100.0% | 100.0% |
| TRANSLITERATE | 97.0% | 93.1% | 95.0% | (combined) |
| TRANSLATE_NORMALISE | 72.4% | 72.7% | 64.7% | (combined) |
| TRANSLATE_COMPOSITE | 0.0% | n/a | **100.0%** | (combined) |
| Russian/Ukrainian | 83.3% | 80.0% | 78.9% | (combined) |
| Chinese | 80.0% | 90.0% | 80.0% | (combined) |
| Greek | 88.9% | 100.0% | 97.4% | (combined) |
| Japanese | 96.0% | 85.0% | 95.6% | (combined) |

Key observations:
- The copilot LLM outperforms the pipeline on the **test dataset** (92.0% vs 89.0%), suggesting good generalisation on held-out cases.
- The pipeline outperforms on the **golden dataset** (88.4% vs 84.8%) — the pipeline's deterministic rules give it an edge on cases that were implicitly calibrated against.

---

## 10. Image-Based Cases

In addition to text-only cases, the dataset supports image-based cases where `image_path` points to a scanned document. These exercise the full pipeline including the OCR extraction layer:

1. Image is uploaded to the Documents tab of the Streamlit app (or passed via `image_path` in the dataset).
2. For JPEG/PNG, the image is sent directly to GPT-4o Vision for OCR and field extraction.
3. For PDFs that contain embedded text, `pymupdf` (fitz) extracts the text layer directly — no vision model required.
4. For scanned PDFs (no embedded text), the first page is rendered to PNG and sent to GPT-4o Vision.
5. Extracted fields are passed through the standard text pipeline.

Image cases are identified by a populated `image_path` column. They exercise the full end-to-end pipeline including OCR and are evaluated against the same `expected_normalised` ground truth.

---

## 11. Test Suite

In addition to the golden dataset evaluation, the repository includes a pytest suite (`tests/`) that provides fast, API-free regression tests:

| Test file | What it tests |
|---|---|
| `tests/test_rules.py` | PRESERVE field pass-through for passport numbers, ID numbers, emails |
| `tests/test_transliteration.py` | Per-language transliteration: 10+ cases per language covering common names and edge cases |
| `tests/test_pipeline.py` | End-to-end layer routing: verifies that each field type is routed to the correct processing layer |
| `tests/test_evaluator.py` | Golden dataset evaluation: verifies the dataset loads and the evaluator runs without error |

Run with:
```bash
PYTHONPATH=src pytest tests/ -q
```

All tests are API-free — no OpenAI key is required. LLM-routed cases are tested with a stub that returns a controlled result for routing verification.

---

## 12. Output Artefacts

Each evaluation run saves two files to `data/output/`:

### JSON — `results_<timestamp>.json`
Full per-case result including all pipeline metadata:
```json
[
  {
    "case_id": "KYC001",
    "language": "ar",
    "field_type": "person_name",
    "expected_treatment": "TRANSLITERATE",
    "is_negative_case": false,
    "expected": "MUHAMMAD ALI HASAN",
    "actual": "MUHAMMAD ALI HASAN",
    "match": true,
    "review_required": false,
    "processing_method": "LLM"
  },
  ...
]
```

### CSV — `results_<timestamp>.csv`
Spreadsheet-friendly format of the same data. Suitable for pivot-table analysis in Excel or Google Sheets.

---

## 13. Performance Targets and Roadmap

Targets apply to both the golden dataset and the test dataset.

| Target | Golden dataset | Test dataset | Gap (test) | Planned fix |
|---|---|---|---|---|
| Overall accuracy ≥ 93% | 88.4% | 89.0% | −4.0pp | Russian Ja→Ya fix + address normalisation |
| Russian/Ukrainian ≥ 90% | 83.3% | 80.0% | −10pp | Post-process Ja→Ya/Ju→Yu/MIKH/ZAKH |
| Chinese ≥ 90% | 80.0% | 90.0% | on target (test) | Brand name table (golden only) |
| Greek ≥ 95% | 88.9% | 100.0% | on target (test) | Company/alias prompt (golden only) |
| Japanese ≥ 90% | 96.0% | 85.0% | −5pp | Address -ku suffix stripping; compound kanji |
| TRANSLATE_NORMALISE ≥ 85% | 72.4% | 72.7% | −12.3pp | Address formatting + alias phrases |
| Theoretical ceiling (all known fixes) | ~98% | ~97% | | All identified fixable patterns corrected |

---

## 14. Regression Gate

The regression gate (`src/evaluation/regression_gate.py`) provides automated threshold enforcement for CI/CD pipelines. It is intended to run on every push to `main` and every pull request, preventing a merge that would degrade accuracy below defined thresholds.

### Accuracy thresholds

The `ACCURACY_THRESHOLDS` dictionary defines the minimum acceptable accuracy for each tracked category:

| Category | Threshold | Rationale |
|---|---|---|
| `overall` | 0.85 | Minimum pipeline-wide floor |
| `ar` (Arabic) | 0.90 | High-risk language — LLM performance must remain consistent |
| `ru` (Russian/Ukrainian) | 0.80 | Known library issues create a realistic ceiling |
| `zh` (Chinese) | 0.78 | Brand-name resolution limits current ceiling |
| `ja` (Japanese) | 0.93 | Largely deterministic; high threshold justified |
| `el` (Greek) | 0.85 | Consistent performance expected |
| `de`, `fr`, `es`, `it`, `ko`, `en` | 0.88–0.95 | Set at evaluated baseline or slightly above |
| `PRESERVE` | **1.00** | Zero tolerance — any PRESERVE failure is a critical regression |
| `TRANSLITERATE` | 0.93 | Deterministic layer; high threshold |
| `TRANSLATE_NORMALISE` | 0.70 | LLM layer; currently operating near this floor |
| `TRANSLATE_ANALYST` | 0.50 | Partially implemented; lenient threshold |

### RegressionGateFailure exception

When `strict=True` (the default in CI), the gate raises `RegressionGateFailure` if any threshold is breached. The exception carries a `.report` attribute containing the full accuracy breakdown and a human-readable `breaches` list. The GitHub Actions workflow is configured to block merge when this exception propagates (`exit code 1`).

```python
try:
    report = run_regression_gate(results, golden_dataset_path, strict=True)
except RegressionGateFailure as e:
    print(e.report["breaches"])
    sys.exit(1)
```

### CI/CD integration

The `.github/workflows/regression.yml` workflow:
1. Runs on every push and pull request to `main`.
2. Executes `PYTHONPATH=src python src/main.py --regression-gate`
3. Saves the regression report JSON as a GitHub Actions artefact.
4. Posts a PR comment summarising breaches when the gate fails.

This ensures that no code change degrading accuracy can be merged without an explicit decision to revise the thresholds.

---

## 15. Evaluation Results Version History

This table records the pipeline accuracy at each significant milestone. All measurements use the 112-case golden dataset, model gpt-4o, temperature=0.

| Version | Date | Sections merged | Overall | ar | ru | zh | ja | el |
|---|---|---|---|---|---|---|---|---|
| v1 | Feb 2026 | Baseline (Arabic + Japanese) | 72.3% | 89.5% | 72.2% | 60.0% | 92.0% | 55.6% |
| v2 | Mar 2026 | Sections 1–6 (all languages + composite aliases + HK Cantonese) | 88.4% | 94.7% | 83.3% | 80.0% | 96.0% | 88.9% |
| v3 | Apr 2026 | Sections 7 (Belarusian) | 88.4% | 94.7% | 83.3% | 80.0% | 96.0% | 88.9% |

> **Note**: v3 accuracy is identical to v2 — the Belarusian handler adds new language coverage but there are no Belarusian cases in the current 112-case golden dataset. Accuracy impact will be measurable once Belarusian cases are added to the dataset.

---

*Last updated: April 2026. Golden dataset evaluation: 20 March 2026, 112 cases. Test dataset evaluation: 20 March 2026, 100 cases. Model: gpt-4o.*

---

## 16. Implementation Log

### Section 1 — BGN/PCGN Russian/Ukrainian Post-Processing (2 April 2026)

**Branch:** `feature/section-1-bgn-pcgn` → merged to `main`

**File changed:** `src/pipeline/transliteration_engine.py`

**What was implemented:**

The `transliterate` library's output for Russian and Ukrainian diverges from the BGN/PCGN romanisation standard in several systematic patterns. A new `_apply_bgn_pcgn_corrections(text: str) -> str` function was added that applies the following ordered substitutions:

| Library output | BGN/PCGN correct form | Character |
|---|---|---|
| `Sch` / `sch` | `Shch` / `shch` | Щ |
| `Shh` / `shh` | `Shch` / `shch` | Щ (alternate library output) |
| `Ja` / `ja` | `Ya` / `ya` | Я |
| `Ju` / `ju` | `Yu` / `yu` | Ю |
| `Je` / `je` | `Ye` / `ye` | Е (Je form) |
| `\bE` (word-initial) | `Ye` | Е (E form at word boundary) |

The function is applied inside `_transliterate_cyrillic()` **only for `ru` and `uk`**. Bulgarian (`bg`) is intentionally excluded — Bulgarian BGN/PCGN conventions differ.

**Tests added** (`tests/test_transliteration.py`):
- `test_bgn_pcgn_corrections_unit` — unit tests for the function with known inputs
- `test_russian_bgn_pcgn_in_transliteration` (parametrised × 5) — integration tests: Наталья→NATALYA, Юрий→YURIJ, Екатерина→YEKATERINA, Татьяна→TATYANA, Щукин→SHCHUKIN
- `test_bulgarian_not_affected_by_bgn_pcgn` — regression guard ensuring Bulgarian is untouched

**Expected impact on previous failures (from Section 8):**
- KYC051 (NATALJA → NATALYA) ✓ resolved
- KYC057 (ANDREJ JUREVICH → ANDREI YURYEVICH) ✓ resolved  
- RU007 (JURIJ → YURIJ; YURII from BGN is a distinct suffix variant) ≈ partial
- RU016 — МИХ→MIH, ЗАХ→ZAH: require additional `кх`→`kh` consonant pattern work, not in scope of this section

---

### Section 2 — Hijri Calendar Detection and ISO 8601 Date Normalisation (2 April 2026)

**Branch:** `feature/section-2-hijri-calendar` → merged to `main`

**Files changed:**
- `src/utils/calendar_utils.py` ← **new file**
- `src/pipeline/rules_engine.py` — added `NORMALISE_NUMERIC` routing
- `src/config/rules.py` — added `NORMALISE_NUMERIC_FIELDS` and `TREATMENT_MAP` entries
- `requirements.txt` — added `hijri-converter>=2.3.1`

**What was implemented:**

A new deterministic Layer 1 date normalisation module (`calendar_utils.py`) handles all date fields before they reach the transliteration or LLM layers. The module provides:

| Function | Purpose |
|---|---|
| `arabic_indic_to_ascii(text)` | Converts Arabic-Indic (٠١…٩) and Persian (۰۱…۹) digits to ASCII 0–9 |
| `detect_calendar_system(date_str)` | Returns `"hijri"`, `"gregorian"`, or `"unknown"` based on 4-digit year range |
| `hijri_to_gregorian(year, month, day)` | Converts Hijri AH to Gregorian using `hijri-converter` library; falls back to approximate formula on `ImportError` |
| `normalise_date_field(date_str, language)` | Master function — returns dict with `normalised` (ISO 8601), `original_calendar`, `review_required`, `review_reason` |

**Calendar detection logic:**
- Year 1900–2100 → **Gregorian**
- Year 1300–1500 → **Hijri** (covers approx. 1882–2077 CE)
- Gregorian takes priority in the overlap zone — the check order prevents misclassification of early-20th-century Gregorian dates
- Arabic-Indic digits are normalised to ASCII before detection, enabling correct parsing of fully Arabic-script dates

**Rules engine integration:**
`apply_rules()` now handles `birth_date` and `date` field types via the `NORMALISE_NUMERIC` routing path. The result dict includes an extra `original_calendar` key for audit trail purposes.

**Dependency note:** `hijri-converter` 2.3.2 is deprecated upstream in favour of `hijridate`. It still works correctly and ships `hijridate` as a dependency. This can be migrated to `hijridate` directly in a future maintenance pass.

**Tests added** (`tests/test_rules.py`, 13 new tests):
- `test_arabic_indic_to_ascii_arabic` — Eastern Arabic digits → ASCII
- `test_arabic_indic_to_ascii_persian` — Persian digits → ASCII
- `test_arabic_indic_mixed_with_separators` — digits + separators survive
- `test_detect_hijri_year` — `"1445/09/20"` → `"hijri"`
- `test_detect_gregorian_year` — `"1985/03/14"` → `"gregorian"`
- `test_detect_gregorian_arabic_indic` — Arabic-Indic Gregorian date → `"gregorian"`
- `test_detect_hijri_arabic_indic` — Arabic-Indic Hijri date → `"hijri"`
- `test_gregorian_arabic_indic_normalised` — `٠٨/١١/١٩٩٢` → `"1992-11-08"`, no review
- `test_gregorian_dd_mm_yyyy_normalised` — `"14/03/1985"` → `"1985-03-14"`, no review
- `test_iso_gregorian_passthrough` — ISO date passes through unchanged
- `test_hijri_date_converted_and_flagged` — `١٤٤٥/٠٩/٢٠` → `"2024-03-30"`, review required
- `test_birth_date_field_type_handled` — confirms `birth_date` is routed by RULE
- `test_date_field_type_handled` — confirms `date` is routed by RULE

**Test results:** 51 passed, 0 failed (1 DeprecationWarning from deprecated `hijri-converter` — harmless)

---

### Section 3 — Japanese Era-Year Conversion (2 April 2026)

**Branch:** `feature/section-3-japanese-era` → merged to `main`

**Files changed:**
- `src/utils/calendar_utils.py` — added `JAPANESE_ERAS`, `kanji_numeral_to_int()`, `detect_and_convert_japanese_era()`, updated `normalise_date_field()`
- `src/pipeline/transliteration_engine.py` — added era-date routing in `transliterate()`

**What was implemented:**

Japanese era-year dates (e.g. 昭和五十三年四月三日) are now detected and converted to ISO 8601 via two integration points:
1. **`normalise_date_field(language="ja")`** — when `detect_calendar_system()` returns `"unknown"` and language is `"ja"`, delegates to `detect_and_convert_japanese_era()`
2. **`transliterate()`** — when `language=="ja"` and `field_type` is `"date"` or `"birth_date"`, calls `detect_and_convert_japanese_era()` and returns the ISO date instead of routing to pykakasi

| Constant/Function | Purpose |
|---|---|
| `JAPANESE_ERAS` | Dict mapping kanji and romanised era names to start year and romaji |
| `kanji_numeral_to_int(text)` | Converts classical (五十三→53) and positional (二〇〇五→2005) Kanji numerals |
| `detect_and_convert_japanese_era(date_str)` | Full era detection + Gregorian conversion; returns normalised, era_detected, gregorian_year, review_required, review_reason |

**Supported eras:** 明治 (Meiji, 1868), 大正 (Taisho, 1912), 昭和 (Showa, 1926), 平成 (Heisei, 1989), 令和 (Reiwa, 2019). Both Kanji and romanised forms accepted.

**Special value:** 元年 (gangen / first year) is correctly parsed as year 1.

**Review policy:** Era-year conversions always set `review_required=True` with reason `"Japanese era date converted — verify year: {era} {era_year} = {gregorian_year}"`. Pure Kanji Gregorian dates (no era prefix) set `review_required=False`.

**Tests added** (`tests/test_transliteration.py`, 13 new tests):
- `test_kanji_numeral_to_int` (parametrised × 7): 五十三→53, 二〇〇五→2005, 十二→12, 三→3, 二十→20, 元→1, 六十四→64
- `test_showa_era_conversion` — 昭和五十三年四月三日 → 1978-04-03, review=True
- `test_heisei_first_year` — 平成元年一月八日 → 1989-01-08
- `test_reiwa_era_conversion` — 令和三年一月五日 → 2021-01-05
- `test_kanji_gregorian_no_era` — 二〇〇五年十二月一日 → 2005-12-01, review=False
- `test_japanese_era_date_via_transliterate` — transliterate() routing for birth_date
- `test_japanese_era_date_field_date_type` — transliterate() routing for date

**Test results:** 64 passed, 0 failed

---

### Section 4 — TRANSLATE_ANALYST Handler (2 April 2026)

**Branch:** `feature/section-4-translate-analyst` → merged to `main`

**Files changed:**
- `src/pipeline/analyst_handler.py` ← **new file**
- `src/pipeline/pipeline.py` — added `TRANSLATE_ANALYST` routing

**What was implemented:**

The `TRANSLATE_ANALYST` treatment routes alias fields containing natural-language descriptor phrases to a dedicated handler instead of the generic LLM layer.

| Component | Purpose |
|---|---|
| `ALIAS_TRIGGERS` | Dict of regex trigger patterns per language (11 languages: en, ar, ru, el, zh, ja, de, fr, es, it, ko) |
| `extract_name_and_alias(text, language)` | Splits text into primary + alias on first pattern match; returns split_method=`"trigger"` or `"no_split"` |
| `_normalise_part(...)` | Normalises a text fragment using transliterate or LLM based on language |
| `process_analyst_field(...)` | End-to-end processing: split → normalise each part → combine as `"{PRIMARY} ALSO KNOWN AS {ALIAS}"` |

**Pipeline routing change:** Previously composite aliases went to `enrich_with_llm()`. Now they go to `process_analyst_field()`, which:
1. Extracts the primary name and alias substrings
2. Calls the transliteration engine on each part
3. Combines with "ALSO KNOWN AS" separator
4. Sets `review_required=True` and `processing_method="TRANSLITERATE+ANALYST"` (or `"LLM+ANALYST"` for Arabic)

**Always sets `review_required=True`** because alias phrase splitting is heuristic.

**Tests added** (`tests/test_pipeline.py`, 12 new tests):
- `test_extract_russian_alias_trigger` — по прозвищу splits Александр / Саша
- `test_extract_english_also_known_as` — "Wang Qiang also known as ..." splits correctly
- `test_extract_no_trigger_treated_as_primary` — no trigger → no split
- `test_alias_trigger_fires_for_each_language` (parametrised × 9) — ar, el, zh, ja, de, fr, es, it, ko all fire
- `test_russian_composite_alias_via_process_field` — end-to-end ALSO KNOWN AS structure
- `test_greek_composite_alias_via_process_field` — Νίκος extracted and transliterated
- `test_english_composite_alias_combines_correctly` — "ALSO KNOWN AS" in normalised
- `test_no_trigger_alias_treated_as_whole` — plain alias → standard TRANSLITERATE

**Test results:** 86 passed, 0 failed

---

### Section 5 — New Language Handlers: de, fr, es, it, ko, en (2 April 2026)

**Branch:** `feature/section-5-new-language-handlers` → merged to `main`

**Files changed:**
- `src/config/language_normalisation_tables.py` ← **new file**
- `src/pipeline/transliteration_engine.py` — added 6 new handlers + dispatch routing
- `requirements.txt` — added `korean-romanizer` (optional)

**What was implemented:**

All six languages are now handled deterministically at Layer 2. None require the LLM for person name normalisation.

| Language | Handler | Key behaviour |
|---|---|---|
| German (`de`) | `_normalise_german()` | Umlaut expansion (Ä→AE, ß→SS) as primary; drop forms (Ä→A) as variants; hyphen→space variant; von/van/zu capitalisation variant |
| French (`fr`) | `_normalise_french()` | Accent strip (é→e, ç→c, œ→oe, etc.); apostrophe elision strip; fused variant; particle-dropped variant |
| Spanish (`es`) | `_normalise_spanish()` | Accent strip; ñ→n primary with NY variant; de/del/de la particle-dropped variant |
| Italian (`it`) | `_normalise_italian()` | Accent strip; apostrophe particle (D', Dell', etc.) space-replaced in primary; fused + dropped variants; double consonants preserved |
| Korean (`ko`) | `_normalise_korean()` | Built-in Hangul → Revised Romanisation (RR) jamo decomposer; `KOREAN_SURNAME_VARIANTS` lookup; surname-first primary + given-name-first and all surname variant forms |
| English (`en`) | `_normalise_english()` | NFKC normalisation; apostrophe O'/Mac variants; St/Saint swap variant; hyphen→space variant |

**Korean romanisation:** The `korean-romanizer` library is not compatible with Python 3.13. A built-in jamo decomposition romaniser (`romanise_hangul()`) is implemented directly in `language_normalisation_tables.py` using the official Revised Romanisation syllable decomposition algorithm. The library is still listed in `requirements.txt` as an optional upgrade path.

**Tables in `language_normalisation_tables.py`:**
`GERMAN_UMLAUT_EXPANSIONS`, `GERMAN_UMLAUT_DROPS`, `FRENCH_ACCENT_STRIP`, `SPANISH_ACCENT_STRIP`, `SPANISH_N_TILDE_VARIANTS`, `ITALIAN_ACCENT_STRIP`, `KOREAN_SURNAME_VARIANTS` (15 surnames), `_KR_CHOSEONG/JUNGSEONG/JONGSEONG` (RR jamo tables), `hangul_syllable_to_roman()`, `romanise_hangul()`

**Tests added** (`tests/test_transliteration.py`, 18 new tests):
- German (4): umlaut expansion, eszett, hyphenated name, noble particle
- French (3): accent strip, hyphenated name, apostrophe elision
- Spanish (3): accent strip, ñ variant, particle variant
- Italian (2): apostrophe particle, double consonant preserved
- Korean (3): surname variants (박→Park, 이→Lee, 류→Ryu/Yoo)
- English (3): apostrophe, Mac variant, Saint variant

**Test results:** 102 passed, 0 failed (2 pre-existing API-call tests skipped in offline run)

---

### Section 6 — Cantonese Variant Generation for HK Documents (2 April 2026)

**Branch:** `feature/section-6-cantonese-variants` → merged to `main`

**Files changed:**
- `src/config/cantonese_surname_map.py` ← **new file**
- `src/pipeline/transliteration_engine.py` — added `_add_cantonese_variants()`, updated `_transliterate_chinese()` and `transliterate()` dispatcher

**What was implemented:**

A 30-entry `CANTONESE_SURNAME_MAP` enables automatic generation of Cantonese (Jyutping) surname variants for Hong Kong identity documents. The standard Mandarin Pinyin romanisation produced by `pypinyin` would be incorrect on HK screening databases (e.g. 黃 → "Huang" in Pinyin vs. "Wong" on HK HKID).

| Component | Purpose |
|---|---|
| `CANTONESE_SURNAME_MAP` | Hanzi → Jyutping mapping for 30 common HK surnames |
| `WADE_GILES_INITIALS` | Pinyin → Wade-Giles initial consonant substitutions (zh→ch, x→hs, etc.) |
| `_add_cantonese_variants()` | Mutates Pinyin result to add HK/TW variants |

**Cantonese variant generation:** Triggered when `country=="HK"` **or** when the first character of the input is in `CANTONESE_SURNAME_MAP`. Only the surname token is replaced (Jyutping for given names is not standardised enough for automated generation). Sets `review_required=True`.

**Wade-Giles variant generation:** Triggered when `country=="TW"`. Applied to the full Pinyin primary form as an `allowed_variants` addition (not a primary form change).

**Country code routing:** `transliterate()` now passes `row.get("country", "")` to `_transliterate_chinese()`.

**Tests added** (`tests/test_transliteration.py`, 4 new tests):
- `test_cantonese_hk_surname_variant` — 黃志明 (HK) → WONG variant
- `test_cantonese_ng_surname_hk` — 吳敏 (HK) → NG variant
- `test_cantonese_no_variant_for_cn` — 王小明 (CN) → no WONG variant
- `test_wade_giles_variant_for_tw` — 陳建志 (TW) → Wade-Giles variant exists

**Test results:** 106 passed, 0 failed (2 pre-existing API-call tests excluded)

---

### Section 7 — Belarusian Transliteration Handler (2 April 2026)

**Branch:** `feature/section-7-belarusian` → merged to `main`

**Files changed:**
- `src/utils/script_detection.py` — added `BELARUSIAN_EXCLUSIVE_CHARS`, `detect_belarusian()`
- `src/pipeline/transliteration_engine.py` — added `BELARUSIAN_CHAR_MAP`, `_transliterate_belarusian()`, updated `transliterate()` dispatcher

**What was implemented:**

Dedicated Belarusian Cyrillic → Latin transliteration handler with automatic script detection.

| Component | Purpose |
|---|---|
| `BELARUSIAN_EXCLUSIVE_CHARS` | Frozenset of `{Ў, ў, Ё, ё}` — characters exclusive to Belarusian |
| `detect_belarusian(text)` | Returns `True` if any `BELARUSIAN_EXCLUSIVE_CHARS` character is present |
| `BELARUSIAN_CHAR_MAP` | Char-level remapping applied before the library: Ў→W, ў→w, Г→H, г→h, І→I, і→i |
| `_transliterate_belarusian()` | Pre-process → `transliterate` lib in "ru" mode → BGN/PCGN corrections; always `review_required=True` |
| Dispatcher auto-detection | When `language` ∈ {ru, uk, bg, be} and `detect_belarusian(text)` returns `True`, `language` is promoted to `"be"` |

**Design decisions:**
- The `transliterate` library has no Belarusian language support; Russian mode is used as the base with `BELARUSIAN_CHAR_MAP` pre-substitutions to handle the three key character divergences (Ў/г/І).
- `review_required=True` is unconditional because automated Belarusian romanisation remains approximate.
- The raw Russian-mode transliteration (without Belarusian pre-processing) is stored as `allowed_variants[0]` when it differs from the primary form, supporting legacy records with incorrect `language="ru"` coding.
- Auto-detection overrides `language` codes ru/uk/bg/be when Ў is present, catching documents mis-classified as Ukrainian or Bulgarian.

**Tests added** (`tests/test_transliteration.py`, 7 new tests):
- `test_detect_belarusian_false_no_u_short` — У (not Ў) → `False`
- `test_detect_belarusian_false_plain_cyrillic` — no exclusive chars → `False`
- `test_detect_belarusian_true_with_u_short` — Ў present → `True`
- `test_detect_belarusian_true_lowercase_u_short` — ў present → `True`
- `test_belarusian_explicit_language_review_required` — `language="be"` → `review_required=True`, `TRANSLITERATE` method
- `test_belarusian_u_short_auto_detected_from_ru` — `language="ru"` + Ў → auto-promoted, `review_required=True`, "Belarusian" in reason
- `test_russian_without_u_short_not_promoted` — `language="ru"` no Ў → not flagged as Belarusian

**Test results:** 113 passed, 0 failed (2 pre-existing API-call tests excluded)

---

## 17. Evaluation Results — Language × Field Type

### Golden Dataset (514 cases, 331 correct, 64.4% overall)

| Language | Field type | Correct | Total | Accuracy |
|---|---|---|---|---|
| ar | address | 7 | 7 | 100.0% |
| ar | alias | 2 | 2 | 100.0% |
| ar | birth_date | 1 | 1 | 100.0% |
| ar | company_name | 3 | 4 | 75.0% |
| ar | date | 1 | 1 | 100.0% |
| ar | email | 1 | 1 | 100.0% |
| ar | free_text | 0 | 1 | 0.0% |
| ar | id_number | 1 | 2 | 50.0% |
| ar | passport_no | 5 | 5 | 100.0% |
| ar | person_name | 16 | 19 | 84.2% |
| ar | phone_number | 1 | 1 | 100.0% |
| ar | reference_no | 0 | 1 | 0.0% |
| ar | registration_no | 0 | 1 | 0.0% |
| ar | tax_id | 0 | 1 | 0.0% |
| ar | telephone | 0 | 1 | 0.0% |
| de | address | 3 | 7 | 42.9% |
| de | alias | 2 | 2 | 100.0% |
| de | birth_date | 1 | 1 | 100.0% |
| de | company_name | 3 | 4 | 75.0% |
| de | date | 0 | 1 | 0.0% |
| de | email | 1 | 1 | 100.0% |
| de | free_text | 0 | 1 | 0.0% |
| de | id_number | 0 | 1 | 0.0% |
| de | passport_no | 3 | 5 | 60.0% |
| de | person_name | 19 | 19 | 100.0% |
| de | phone_number | 0 | 1 | 0.0% |
| de | reference_no | 0 | 1 | 0.0% |
| de | registration_no | 0 | 1 | 0.0% |
| de | tax_id | 0 | 1 | 0.0% |
| de | telephone | 0 | 1 | 0.0% |
| el | address | 7 | 7 | 100.0% |
| el | alias | 0 | 2 | 0.0% |
| el | birth_date | 1 | 1 | 100.0% |
| el | company_name | 3 | 4 | 75.0% |
| el | email | 1 | 1 | 100.0% |
| el | free_text | 0 | 1 | 0.0% |
| el | id_number | 0 | 2 | 0.0% |
| el | passport_no | 4 | 5 | 80.0% |
| el | person_name | 16 | 19 | 84.2% |
| el | phone_number | 0 | 1 | 0.0% |
| el | reference_no | 0 | 1 | 0.0% |
| el | tax_id | 0 | 1 | 0.0% |
| el | telephone | 0 | 1 | 0.0% |
| en | address | 2 | 7 | 28.6% |
| en | alias | 2 | 2 | 100.0% |
| en | birth_date | 1 | 1 | 100.0% |
| en | company_name | 3 | 4 | 75.0% |
| en | date | 0 | 1 | 0.0% |
| en | email | 1 | 1 | 100.0% |
| en | free_text | 0 | 1 | 0.0% |
| en | id_number | 0 | 2 | 0.0% |
| en | passport_no | 5 | 5 | 100.0% |
| en | person_name | 19 | 19 | 100.0% |
| en | phone_number | 0 | 1 | 0.0% |
| en | reference_no | 0 | 1 | 0.0% |
| en | registration_no | 1 | 1 | 100.0% |
| en | tax_id | 0 | 1 | 0.0% |
| en | telephone | 0 | 1 | 0.0% |
| es | address | 4 | 7 | 57.1% |
| es | alias | 1 | 2 | 50.0% |
| es | company_name | 3 | 4 | 75.0% |
| es | date | 0 | 1 | 0.0% |
| es | email | 1 | 1 | 100.0% |
| es | free_text | 0 | 1 | 0.0% |
| es | id_number | 0 | 2 | 0.0% |
| es | passport_no | 4 | 5 | 80.0% |
| es | person_name | 19 | 19 | 100.0% |
| es | phone_number | 0 | 1 | 0.0% |
| es | reference_no | 0 | 1 | 0.0% |
| es | registration_no | 0 | 1 | 0.0% |
| es | tax_id | 0 | 1 | 0.0% |
| fr | address | 2 | 7 | 28.6% |
| fr | alias | 0 | 2 | 0.0% |
| fr | company_name | 4 | 4 | 100.0% |
| fr | date | 0 | 1 | 0.0% |
| fr | free_text | 0 | 1 | 0.0% |
| fr | id_number | 0 | 2 | 0.0% |
| fr | passport_no | 4 | 5 | 80.0% |
| fr | person_name | 19 | 19 | 100.0% |
| fr | phone_number | 0 | 1 | 0.0% |
| fr | reference_no | 0 | 1 | 0.0% |
| fr | registration_no | 0 | 1 | 0.0% |
| fr | tax_id | 0 | 1 | 0.0% |
| it | address | 2 | 7 | 28.6% |
| it | alias | 1 | 2 | 50.0% |
| it | company_name | 4 | 4 | 100.0% |
| it | date | 0 | 1 | 0.0% |
| it | email | 1 | 1 | 100.0% |
| it | free_text | 0 | 1 | 0.0% |
| it | id_number | 0 | 2 | 0.0% |
| it | passport_no | 3 | 5 | 60.0% |
| it | person_name | 19 | 19 | 100.0% |
| it | phone_number | 0 | 1 | 0.0% |
| it | reference_no | 0 | 1 | 0.0% |
| it | registration_no | 0 | 1 | 0.0% |
| it | tax_id | 0 | 1 | 0.0% |
| ja | address | 4 | 7 | 57.1% |
| ja | alias | 1 | 2 | 50.0% |
| ja | company_name | 4 | 4 | 100.0% |
| ja | date | 0 | 1 | 0.0% |
| ja | free_text | 0 | 1 | 0.0% |
| ja | id_number | 0 | 2 | 0.0% |
| ja | passport_no | 5 | 5 | 100.0% |
| ja | person_name | 18 | 19 | 94.7% |
| ja | phone_number | 0 | 1 | 0.0% |
| ja | reference_no | 0 | 1 | 0.0% |
| ja | registration_no | 0 | 1 | 0.0% |
| ja | tax_id | 0 | 1 | 0.0% |
| ja | telephone | 0 | 1 | 0.0% |
| ko | address | 2 | 7 | 28.6% |
| ko | alias | 0 | 2 | 0.0% |
| ko | company_name | 4 | 4 | 100.0% |
| ko | date | 0 | 1 | 0.0% |
| ko | email | 1 | 1 | 100.0% |
| ko | free_text | 0 | 1 | 0.0% |
| ko | id_number | 0 | 2 | 0.0% |
| ko | passport_no | 3 | 5 | 60.0% |
| ko | person_name | 0 | 19 | 0.0% |
| ko | phone_number | 0 | 1 | 0.0% |
| ko | reference_no | 0 | 1 | 0.0% |
| ko | registration_no | 0 | 1 | 0.0% |
| ko | tax_id | 0 | 1 | 0.0% |
| ko | telephone | 0 | 1 | 0.0% |
| ru | address | 5 | 7 | 71.4% |
| ru | alias | 0 | 2 | 0.0% |
| ru | birth_date | 1 | 1 | 100.0% |
| ru | company_name | 3 | 4 | 75.0% |
| ru | date | 1 | 1 | 100.0% |
| ru | email | 1 | 1 | 100.0% |
| ru | free_text | 0 | 1 | 0.0% |
| ru | id_number | 0 | 2 | 0.0% |
| ru | passport_no | 5 | 5 | 100.0% |
| ru | person_name | 14 | 19 | 73.7% |
| ru | phone_number | 0 | 1 | 0.0% |
| ru | reference_no | 0 | 1 | 0.0% |
| ru | registration_no | 0 | 1 | 0.0% |
| ru | tax_id | 0 | 1 | 0.0% |
| ru | telephone | 0 | 1 | 0.0% |
| zh | address | 5 | 7 | 71.4% |
| zh | alias | 0 | 2 | 0.0% |
| zh | company_name | 2 | 4 | 50.0% |
| zh | date | 0 | 1 | 0.0% |
| zh | email | 1 | 1 | 100.0% |
| zh | free_text | 0 | 1 | 0.0% |
| zh | id_number | 0 | 2 | 0.0% |
| zh | passport_no | 5 | 5 | 100.0% |
| zh | person_name | 19 | 19 | 100.0% |
| zh | phone_number | 0 | 1 | 0.0% |
| zh | reference_no | 0 | 1 | 0.0% |
| zh | registration_no | 0 | 1 | 0.0% |
| zh | tax_id | 0 | 1 | 0.0% |
| zh | telephone | 0 | 1 | 0.0% |

### Test Dataset (528 cases, 331 correct, 62.7% overall)

| Language | Field type | Correct | Total | Accuracy |
|---|---|---|---|---|
| ar | address | 5 | 7 | 71.4% |
| ar | alias | 2 | 2 | 100.0% |
| ar | birth_date | 1 | 1 | 100.0% |
| ar | company_name | 3 | 4 | 75.0% |
| ar | date | 0 | 1 | 0.0% |
| ar | email | 1 | 1 | 100.0% |
| ar | free_text | 0 | 1 | 0.0% |
| ar | id_number | 0 | 2 | 0.0% |
| ar | passport_no | 5 | 5 | 100.0% |
| ar | person_name | 16 | 19 | 84.2% |
| ar | phone_number | 1 | 1 | 100.0% |
| ar | reference_no | 0 | 1 | 0.0% |
| ar | registration_no | 0 | 1 | 0.0% |
| ar | tax_id | 0 | 1 | 0.0% |
| ar | telephone | 1 | 1 | 100.0% |
| de | address | 2 | 7 | 28.6% |
| de | alias | 1 | 2 | 50.0% |
| de | birth_date | 1 | 1 | 100.0% |
| de | company_name | 4 | 4 | 100.0% |
| de | date | 1 | 1 | 100.0% |
| de | email | 1 | 1 | 100.0% |
| de | free_text | 0 | 1 | 0.0% |
| de | id_number | 0 | 2 | 0.0% |
| de | passport_no | 4 | 5 | 80.0% |
| de | person_name | 19 | 19 | 100.0% |
| de | phone_number | 0 | 1 | 0.0% |
| de | reference_no | 0 | 1 | 0.0% |
| de | registration_no | 0 | 1 | 0.0% |
| de | tax_id | 0 | 1 | 0.0% |
| de | telephone | 0 | 1 | 0.0% |
| el | address | 7 | 7 | 100.0% |
| el | alias | 0 | 2 | 0.0% |
| el | birth_date | 1 | 1 | 100.0% |
| el | company_name | 4 | 4 | 100.0% |
| el | date | 1 | 1 | 100.0% |
| el | email | 1 | 1 | 100.0% |
| el | free_text | 0 | 1 | 0.0% |
| el | id_number | 0 | 2 | 0.0% |
| el | passport_no | 4 | 5 | 80.0% |
| el | person_name | 16 | 19 | 84.2% |
| el | phone_number | 0 | 1 | 0.0% |
| el | reference_no | 0 | 1 | 0.0% |
| el | registration_no | 0 | 1 | 0.0% |
| el | tax_id | 0 | 1 | 0.0% |
| el | telephone | 0 | 1 | 0.0% |
| en | address | 3 | 7 | 42.9% |
| en | alias | 2 | 2 | 100.0% |
| en | birth_date | 0 | 1 | 0.0% |
| en | company_name | 4 | 4 | 100.0% |
| en | date | 1 | 1 | 100.0% |
| en | email | 1 | 1 | 100.0% |
| en | free_text | 0 | 1 | 0.0% |
| en | id_number | 0 | 2 | 0.0% |
| en | passport_no | 5 | 5 | 100.0% |
| en | person_name | 18 | 19 | 94.7% |
| en | phone_number | 0 | 1 | 0.0% |
| en | reference_no | 0 | 1 | 0.0% |
| en | registration_no | 1 | 1 | 100.0% |
| en | tax_id | 0 | 1 | 0.0% |
| en | telephone | 0 | 1 | 0.0% |
| es | address | 1 | 7 | 14.3% |
| es | alias | 1 | 2 | 50.0% |
| es | birth_date | 1 | 1 | 100.0% |
| es | company_name | 2 | 4 | 50.0% |
| es | date | 1 | 1 | 100.0% |
| es | email | 1 | 1 | 100.0% |
| es | free_text | 0 | 1 | 0.0% |
| es | id_number | 0 | 2 | 0.0% |
| es | passport_no | 5 | 5 | 100.0% |
| es | person_name | 19 | 19 | 100.0% |
| es | phone_number | 0 | 1 | 0.0% |
| es | reference_no | 0 | 1 | 0.0% |
| es | registration_no | 0 | 1 | 0.0% |
| es | tax_id | 0 | 1 | 0.0% |
| es | telephone | 0 | 1 | 0.0% |
| fr | address | 2 | 7 | 28.6% |
| fr | alias | 1 | 2 | 50.0% |
| fr | birth_date | 1 | 1 | 100.0% |
| fr | company_name | 3 | 4 | 75.0% |
| fr | date | 1 | 1 | 100.0% |
| fr | email | 1 | 1 | 100.0% |
| fr | free_text | 0 | 1 | 0.0% |
| fr | id_number | 0 | 2 | 0.0% |
| fr | passport_no | 4 | 5 | 80.0% |
| fr | person_name | 19 | 19 | 100.0% |
| fr | phone_number | 0 | 1 | 0.0% |
| fr | reference_no | 0 | 1 | 0.0% |
| fr | registration_no | 0 | 1 | 0.0% |
| fr | tax_id | 0 | 1 | 0.0% |
| fr | telephone | 0 | 1 | 0.0% |
| it | address | 3 | 7 | 42.9% |
| it | alias | 1 | 2 | 50.0% |
| it | birth_date | 1 | 1 | 100.0% |
| it | company_name | 2 | 4 | 50.0% |
| it | date | 1 | 1 | 100.0% |
| it | email | 1 | 1 | 100.0% |
| it | free_text | 0 | 1 | 0.0% |
| it | id_number | 0 | 2 | 0.0% |
| it | passport_no | 4 | 5 | 80.0% |
| it | person_name | 19 | 19 | 100.0% |
| it | phone_number | 0 | 1 | 0.0% |
| it | reference_no | 0 | 1 | 0.0% |
| it | registration_no | 0 | 1 | 0.0% |
| it | tax_id | 0 | 1 | 0.0% |
| it | telephone | 0 | 1 | 0.0% |
| ja | address | 0 | 7 | 0.0% |
| ja | alias | 1 | 2 | 50.0% |
| ja | birth_date | 0 | 1 | 0.0% |
| ja | company_name | 4 | 4 | 100.0% |
| ja | date | 0 | 1 | 0.0% |
| ja | email | 1 | 1 | 100.0% |
| ja | free_text | 0 | 1 | 0.0% |
| ja | id_number | 0 | 2 | 0.0% |
| ja | passport_no | 5 | 5 | 100.0% |
| ja | person_name | 16 | 19 | 84.2% |
| ja | phone_number | 0 | 1 | 0.0% |
| ja | reference_no | 0 | 1 | 0.0% |
| ja | registration_no | 0 | 1 | 0.0% |
| ja | tax_id | 0 | 1 | 0.0% |
| ja | telephone | 0 | 1 | 0.0% |
| ko | address | 1 | 7 | 14.3% |
| ko | alias | 0 | 2 | 0.0% |
| ko | birth_date | 0 | 1 | 0.0% |
| ko | company_name | 4 | 4 | 100.0% |
| ko | date | 0 | 1 | 0.0% |
| ko | email | 1 | 1 | 100.0% |
| ko | free_text | 0 | 1 | 0.0% |
| ko | id_number | 0 | 2 | 0.0% |
| ko | passport_no | 4 | 5 | 80.0% |
| ko | person_name | 0 | 19 | 0.0% |
| ko | phone_number | 0 | 1 | 0.0% |
| ko | reference_no | 0 | 1 | 0.0% |
| ko | registration_no | 0 | 1 | 0.0% |
| ko | tax_id | 0 | 1 | 0.0% |
| ko | telephone | 0 | 1 | 0.0% |
| ru | address | 2 | 7 | 28.6% |
| ru | alias | 1 | 2 | 50.0% |
| ru | birth_date | 1 | 1 | 100.0% |
| ru | company_name | 2 | 4 | 50.0% |
| ru | date | 1 | 1 | 100.0% |
| ru | email | 1 | 1 | 100.0% |
| ru | free_text | 0 | 1 | 0.0% |
| ru | id_number | 0 | 2 | 0.0% |
| ru | passport_no | 5 | 5 | 100.0% |
| ru | person_name | 16 | 19 | 84.2% |
| ru | phone_number | 0 | 1 | 0.0% |
| ru | reference_no | 0 | 1 | 0.0% |
| ru | registration_no | 0 | 1 | 0.0% |
| ru | tax_id | 0 | 1 | 0.0% |
| ru | telephone | 0 | 1 | 0.0% |
| zh | address | 3 | 7 | 42.9% |
| zh | alias | 2 | 2 | 100.0% |
| zh | birth_date | 0 | 1 | 0.0% |
| zh | company_name | 4 | 4 | 100.0% |
| zh | date | 0 | 1 | 0.0% |
| zh | email | 1 | 1 | 100.0% |
| zh | free_text | 0 | 1 | 0.0% |
| zh | id_number | 0 | 2 | 0.0% |
| zh | passport_no | 5 | 5 | 100.0% |
| zh | person_name | 18 | 19 | 94.7% |
| zh | phone_number | 0 | 1 | 0.0% |
| zh | reference_no | 0 | 1 | 0.0% |
| zh | registration_no | 0 | 1 | 0.0% |
| zh | tax_id | 0 | 1 | 0.0% |
| zh | telephone | 0 | 1 | 0.0% |

