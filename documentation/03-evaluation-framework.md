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
| `expected_treatment` | string | `PRESERVE`, `TRANSLITERATE`, `TRANSLATE_NORMALISE`, `TRANSLATE_ANALYST` |
| `expected_transliteration` | string | Correct BGN/PCGN or standard romanised form (primary) |
| `expected_allowed_variants` | string | Pipe-separated (`\|`) list of other accepted forms |
| `expected_english` | string | Natural English rendering (may differ from screener form) |
| `expected_normalised` | string | **Ground truth for evaluation** — uppercase normalised form |
| `should_flag_review` | boolean | Whether the pipeline is expected to set `review_required=True` |
| `is_negative_case` | boolean | Whether this is a **negative case** (the pipeline should NOT match) |
| `risk_notes` | string | Free-text annotation explaining the KYC risk dimension being tested |

### Dataset size and composition — current state (112 cases)

| Language | Cases | Field types covered |
|---|---|---|
| Arabic (ar) | 19 | person_name, alias, company_name, address, passport_no |
| Greek (el) | 18 | person_name, alias, company_name, address, email, passport_no |
| English (en) | 2 | passport_no, email |
| Japanese (ja) | 25 | person_name, alias, company_name, address, passport_no |
| Russian/Ukrainian (ru) | 18 | person_name, alias, company_name, address, passport_no |
| Chinese (zh) | 30 | person_name, alias, company_name, address, passport_no |
| **Total** | **112** | |

---

## 3. Case Types

### Standard cases
The majority of cases are **standard positive cases**: the pipeline should produce an output that matches `expected_normalised` or one of the `expected_allowed_variants`.

### Negative cases (`is_negative_case = true`)
Negative cases test that the pipeline **does not produce a false positive**: the pipeline output should *not* match the `expected_normalised` value. For example, KYC014 (Алексей Смирнов, Russian) is flagged as a negative case to verify that it does not match a different Aleksei Smirnov identity listed elsewhere in the dataset.

### TRANSLATE_ANALYST cases
A small number of cases are tagged `expected_treatment=TRANSLATE_ANALYST`. These represent alias entries containing descriptive phrases mixed with identity text (e.g. "ALEXANDER NICKNAMED SASHA"). These require an analyst to interpret the semantics of the phrase — they are not currently handled by the automated pipeline and are tracked as a known gap.

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

## 6. Current Performance Results

*Measured on 20 March 2026, pipeline v2, model gpt-4o, temperature=0.*

### Overall accuracy
**88.4% — 99 correct out of 112 cases**

---

### By language

| Language | Correct | Total | Accuracy |
|---|---|---|---|
| Arabic (ar) | 18 | 19 | **94.7%** |
| Greek (el) | 16 | 18 | **88.9%** |
| English (en) | 2 | 2 | **100.0%** |
| Japanese (ja) | 24 | 25 | **96.0%** |
| Russian/Ukrainian (ru) | 15 | 18 | **83.3%** |
| Chinese (zh) | 24 | 30 | **80.0%** |

---

### By processing method (expected treatment)

| Treatment | Correct | Total | Accuracy |
|---|---|---|---|
| PRESERVE | 13 | 13 | **100.0%** |
| TRANSLITERATE | 65 | 67 | **97.0%** |
| TRANSLATE_NORMALISE | 21 | 29 | **72.4%** |
| TRANSLATE_ANALYST | 0 | 3 | **0.0%** |

PRESERVE achieves 100% as expected — these are pass-through fields with no transformation risk.

TRANSLITERATE achieves 97% — the two failures are known `Ja→Ya` library issues (see below).

TRANSLATE_NORMALISE achieves 72.4% — failures are concentrated in company name translation where LLM brand-name knowledge is incomplete.

TRANSLATE_ANALYST is 0% — this treatment category is not yet implemented. These are alias fields with mixed descriptive phrases that require semantic parsing beyond current scope.

---

### By language × field type (full cross-tabulation)

| Language | Field type | Correct | Total | Accuracy |
|---|---|---|---|---|
| ar | address | 3 | 3 | 100.0% |
| ar | alias | 2 | 2 | 100.0% |
| ar | company_name | 0 | 1 | 0.0% |
| ar | passport_no | 2 | 2 | 100.0% |
| ar | person_name | 11 | 11 | 100.0% |
| el | address | 5 | 5 | 100.0% |
| el | alias | 0 | 1 | 0.0% |
| el | company_name | 1 | 2 | 50.0% |
| el | email | 1 | 1 | 100.0% |
| el | passport_no | 1 | 1 | 100.0% |
| el | person_name | 8 | 8 | 100.0% |
| en | email | 1 | 1 | 100.0% |
| en | passport_no | 1 | 1 | 100.0% |
| ja | address | 4 | 4 | 100.0% |
| ja | alias | 1 | 1 | 100.0% |
| ja | company_name | 1 | 2 | 50.0% |
| ja | passport_no | 5 | 5 | 100.0% |
| ja | person_name | 13 | 13 | 100.0% |
| ru | address | 3 | 3 | 100.0% |
| ru | alias | 0 | 1 | 0.0% |
| ru | company_name | 1 | 1 | 100.0% |
| ru | passport_no | 1 | 1 | 100.0% |
| ru | person_name | 10 | 12 | 83.3% |
| zh | address | 4 | 5 | 80.0% |
| zh | alias | 0 | 1 | 0.0% |
| zh | company_name | 0 | 4 | 0.0% |
| zh | passport_no | 1 | 1 | 100.0% |
| zh | person_name | 19 | 19 | 100.0% |

---

## 7. Failing Cases — Root Cause Analysis

The 13 failing cases as of the current evaluation run, with root cause:

| Case ID | Language | Field | Expected | Got | Root Cause |
|---|---|---|---|---|---|
| KYC018 | zh | company_name | BEIJING VISION TECHNOLOGY CO LTD | BEIJING YUANJING KEJI CO LTD | LLM transliterated (不 translating) Chinese brand word 远景 instead of translating to "Vision Keji" |
| KYC037 | ar | company_name | AL NOOR TRADING CO LTD | AL NOUR LILTIJARA ALMAHDUDA CO LTD | LLM transliterated Arabic company name instead of translating; 贸易→TRADING missed |
| KYC045 | ja | company_name | MITSUBISHI CORPORATION | MITSUBISHI SHOJI KK | LLM rendered 商事 (Shoji = commercial trading division) instead of the established English brand MITSUBISHI CORPORATION |
| KYC051 | ru | person_name | NATALYA VIKTOROVNA ORLOVA | NATALJA VIKTOROVNA ORLOVA | `transliterate` library uses `Ja` where BGN/PCGN mandates `Ya` for Я |
| KYC057 | ru | person_name | ANDREI YURYEVICH KOVALEV | ANDREJ JUREVICH KOVALEV | Same `Ju→Yu` and `J→Y` library convention difference |
| KYC060 | ru | alias | ALEXANDER NICKNAMED SASHA | ALEKSANDR PO PROZVISCHU SASHA | Descriptive phrase "по прозвищу" (meaning "nicknamed") not translated — TRANSLATE_ANALYST case |
| KYC065 | zh | company_name | SHENZHEN HUAXING ELECTRONICS CO LTD | SHENZHEN HUA XING DIANZI CO LTD | LLM transliterated 华兴电子 instead of resolving to known brand; Pinyin fallback |
| KYC069 | zh | address | 18 TIYU EAST ROAD TIANHE GUANGZHOU | 18 TIYU EAST ROAD, TIANHE DISTRICT, GUANGZHOU CITY | LLM added "DISTRICT" and "CITY" suffixes; expected form omits them — close miss |
| KYC070 | zh | alias | WANG QIANG ALSO KNOWN AS WANG XIAOQIANG | WANG QIANG YOU MING WANG XIAO QIANG | 又名 (yòu míng = "also known as") was transliterated rather than translated |
| KYC074 | el | company_name | ENERGY DEVELOPMENT SA | ANONIMI ETAIRIA ENERGEIAKIS ANAPTYXIS SA | LLM transliterated the Greek company name; "Ανώνυμη Εταιρεία" (=SA) should have been dropped |
| KYC080 | el | alias | KNOWN AS NIKOS | GNOSTOS OS NIKOS | Greek phrase γνωστός ως (= "known as") was transliterated rather than translated |
| KYC091 | zh | company_name | TAIWAN SEMICONDUCTOR MANUFACTURING CO LTD | TAIWAN JITI DIANLU ZHIZAO CO LTD | TSMC's Chinese name 台积电路 transliterated instead of resolved to established English brand name |
| KYC092 | zh | company_name | TENCENT TECHNOLOGY CO LTD | TENGXUN KEJI CO LTD | 腾讯 (Téngxùn) transliterated instead of resolved to established English "TENCENT" brand |

### Pattern analysis of failures

**Category A — Chinese company brand name resolution (5 cases: KYC018, KYC065, KYC091, KYC092, and partial KYC045)**
The LLM is correctly transliterating or partially translating but failing to recognise that a well-known Chinese company has an established English trade name. Fix: enrich the company name prompt with examples of Chinese-brand-name resolution, or add a brand lookup table.

**Category B — Descriptive alias phrases not translated (3 cases: KYC060, KYC070, KYC080)**
Aliases containing mixed identity + descriptor (по прозвищу/又名/γνωστός ως) require the LLM to translate the descriptive component while preserving the name component. The current prompt does not instruct on this. Fix: update alias prompts to explicitly handle mixed-descriptor patterns.

**Category C — Russian Ja/Ju library convention (2 cases: KYC051, KYC057)**
The `transliterate` library uses `Ja`/`Ju` where BGN/PCGN mandates `Ya`/`Yu`. Fix: post-process `ru` language output with `str.replace("Ja", "Ya").replace("Ju", "Yu")`.

**Category D — Greek company name LLM behaviour (1 case: KYC074)**
LLM transliterated the Greek company name instead of translating it. Fix: reinforce the Greek company name handling in the prompt.

**Category E — Address formatting suffix (1 case: KYC069)**
LLM added "DISTRICT" and "CITY" administrative suffixes that the expected form omits. Minor formatting — may be resolved by adjusting the address lenient matching or the prompt.

---

## 8. Image-Based Cases

In addition to text-only cases, the dataset supports image-based cases where `image_path` points to a scanned document. These exercise the full pipeline including the OCR extraction layer:

1. Image is uploaded to the Documents tab of the Streamlit app (or passed via `image_path` in the dataset).
2. For JPEG/PNG, the image is sent directly to GPT-4o Vision for OCR and field extraction.
3. For PDFs that contain embedded text, `pymupdf` (fitz) extracts the text layer directly — no vision model required.
4. For scanned PDFs (no embedded text), the first page is rendered to PNG and sent to GPT-4o Vision.
5. Extracted fields are passed through the standard text pipeline.

Image cases are identified by a populated `image_path` column. They exercise the full end-to-end pipeline including OCR and are evaluated against the same `expected_normalised` ground truth.

---

## 9. Test Suite

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

## 10. Output Artefacts

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

## 11. Performance Targets and Roadmap

| Target | Current | Gap | Planned fix |
|---|---|---|---|
| Overall accuracy ≥ 93% | 88.4% | −4.6pp | Fixes B (aliases) + C (Russian Ja→Ya) |
| Russian/Ukrainian ≥ 90% | 83.3% | −6.7pp | Post-process Ja→Ya/Ju→Yu |
| Chinese ≥ 90% | 80.0% | −10pp | Brand name table + alias prompt update |
| TRANSLATE_NORMALISE ≥ 85% | 72.4% | −12.6pp | Alias phrases + company brand names |
| TRANSLATE_ANALYST ≥ 0% | 0.0% | N/A | New descriptor-phrase handling |
| Theoretical ceiling (all known fixes) | ~98% | | All remaining 8 fixable cases corrected |

---

*Last updated: March 2026. Evaluation run: 20 March 2026, 112 cases, model gpt-4o.*
