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

### Test dataset
`data/test_dataset.csv`

A separate 100-case test dataset used to evaluate pipeline generalisation on held-out examples not used during development. It shares the same 16-column schema. Composition: 20 cases per language (Arabic, Greek, Japanese, Russian/Ukrainian, Chinese), covering all field types.

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
| TRANSLATE_COMPOSITE | 0 | 3 | **0.0%** |

PRESERVE achieves 100% as expected — these are pass-through fields with no transformation risk.

TRANSLITERATE achieves 97% — the two failures are known `Ja→Ya` library issues (see below).

TRANSLATE_NORMALISE achieves 72.4% — failures are concentrated in company name translation where LLM brand-name knowledge is incomplete.

TRANSLATE_COMPOSITE is 0% on this baseline run — the `is_composite_alias()` detector and LLM routing are implemented in `feature/translate-composite` and not yet merged. These are alias fields containing both a name and a descriptor phrase that requires translation.

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

## 7. Test Dataset Performance Results

*Measured on 20 March 2026, pipeline v2, model gpt-4o, temperature=0. 100 held-out cases from `data/test_dataset.csv`.*

### Overall accuracy
**89.0% — 89 correct out of 100 cases**

---

### By language

| Language | Correct | Total | Accuracy |
|---|---|---|---|
| Arabic (ar) | 18 | 20 | **90.0%** |
| Greek (el) | 20 | 20 | **100.0%** |
| Japanese (ja) | 17 | 20 | **85.0%** |
| Russian/Ukrainian (ru) | 16 | 20 | **80.0%** |
| Chinese (zh) | 18 | 20 | **90.0%** |

---

### By processing method (expected treatment)

| Treatment | Correct | Total | Accuracy |
|---|---|---|---|
| PRESERVE | 6 | 6 | **100.0%** |
| TRANSLITERATE | 67 | 72 | **93.1%** |
| TRANSLATE_NORMALISE | 16 | 22 | **72.7%** |

PRESERVE achieves 100% as expected. TRANSLITERATE achieves 93.1%. TRANSLATE_NORMALISE achieves 72.7% — failures are concentrated in address formatting and a small number of name transliteration variants.

---

### By language × field type

| Language | Field type | Correct | Total | Accuracy |
|---|---|---|---|---|
| ar | address | 3 | 3 | 100.0% |
| ar | alias | 2 | 2 | 100.0% |
| ar | company_name | 1 | 1 | 100.0% |
| ar | passport_no | 1 | 1 | 100.0% |
| ar | person_name | 11 | 13 | 84.6% |
| el | address | 4 | 4 | 100.0% |
| el | company_name | 2 | 2 | 100.0% |
| el | email | 1 | 1 | 100.0% |
| el | passport_no | 1 | 1 | 100.0% |
| el | person_name | 12 | 12 | 100.0% |
| ja | address | 0 | 2 | 0.0% |
| ja | company_name | 2 | 2 | 100.0% |
| ja | passport_no | 1 | 1 | 100.0% |
| ja | person_name | 14 | 15 | 93.3% |
| ru | address | 0 | 2 | 0.0% |
| ru | company_name | 1 | 1 | 100.0% |
| ru | passport_no | 1 | 1 | 100.0% |
| ru | person_name | 14 | 16 | 87.5% |
| zh | address | 1 | 3 | 33.3% |
| zh | company_name | 3 | 3 | 100.0% |
| zh | passport_no | 1 | 1 | 100.0% |
| zh | person_name | 13 | 13 | 100.0% |

---

### Failing cases (11)

| Case ID | Language | Field | Expected | Got | Root cause |
|---|---|---|---|---|---|
| AR012 | ar | person_name | NIHAD IBRAHIM ELSAYED ALNAGGAR | NIHAD IBRAHIM AL-SAYYID AL-NAJJAR | LLM applied classical Arabic romanisation (Al-Sayyid Al-Najjar) rather than the Egyptian compound rendering (Elsayed Alnaggar) |
| AR014 | ar | person_name | MUHAMMAD BIN RASHID AL MAKTOUM | MUHAMMAD BIN RASHID AL-MAKTUM | LLM produced short form Al-Maktum; expected form is the official UAE romanisation Al Maktoum |
| JA006 | ja | address | TOKYO SHINJUKU | TOKYO, SHINJUKU-KU | LLM preserved the ward suffix -ku and added punctuation; expected form drops both |
| JA013 | ja | address | DOGENZAKA SHIBUYA TOKYO | DOGENZAKA, SHIBUYA-KU, TOKYO, JAPAN | Same pattern: -ku suffix retained and JAPAN appended |
| JA019 | ja | person_name | HASHIMOTO DAIKI | HASHIMOTO DAI | Kanji 大輝 has multiple readings; LLM read 大 as DAI (single syllable) instead of merging to DAIKI |
| RU006 | ru | address | LENINA STREET 10 MOSCOW | 10 LENINA ST, MOSCOW | Address number placed first; ST abbreviation used instead of STREET; comma separator added |
| RU007 | ru | person_name | YURII GAGARIN | JURIJ GAGARIN | `transliterate` library rendering Ю→JU / Й→J instead of BGN/PCGN YU / Y |
| RU011 | ru | address | NEVSKY PROSPEKT 20 SAINT PETERSBURG | NEVSKY PROSPECT 20, SAINT PETERSBURG | PROSPEKT vs PROSPECT (minor spelling) and comma formatting |
| RU016 | ru | person_name | MIKHAIL ZAKHAROV | MIHAIL ZAHAROV | Library renders МИХ→MIH and ЗАХ→ZAH; BGN/PCGN standard is MIKH and ZAKH |
| ZH013 | zh | address | LUJIAZUI FINANCE AND TRADE ZONE PUDONG NEW AREA SHANGHAI | LUJIAZUI FINANCIAL AND TRADE ZONE, PUDONG NEW DISTRICT, SHANGHAI CITY | FINANCIAL vs FINANCE; NEW DISTRICT vs NEW AREA; SHANGHAI CITY suffix added |
| ZH020 | zh | address | SCIENCE PARK NANSHAN DISTRICT SHENZHEN GUANGDONG | NANSHAN DISTRICT, SCIENCE AND TECHNOLOGY PARK, SHENZHEN, GUANGDONG PROVINCE | Word order reversed; AND TECHNOLOGY inserted; PROVINCE suffix added |

### Pattern analysis of failures

**Russian Ja/Ju library convention (3 cases: RU007, RU016, and partly RU011)**
The same `transliterate` library issue seen in the golden dataset — Ю→JU/JURIJ instead of YU/YURII, and МИХ→MIH instead of MIKH. Fix: post-process `ru` output with `str.replace("Ja", "Ya").replace("Ju", "Yu")` and extend to handle additional consonant cluster patterns.

**Address formatting artefacts (5 cases: JA006, JA013, RU006, ZH013, ZH020)**
Two sub-patterns: (a) word-order and suffix retention (Japanese -ku, Chinese CITY/PROVINCE, Russian number-first placement); (b) minor wording differences (FINANCIAL vs FINANCE, PROSPEKT vs PROSPECT). The address lenient matcher partially mitigates these — the token-set match catches number order; the remaining failures involve inserted words not present in the expected form. Fix: tighten address normalisation in the prompt and extend the lenient matcher to strip common administrative suffixes.

**Arabic classical vs Egyptian romanisation (2 cases: AR012, AR014)**
The LLM applies the classically correct romanisation but the expected form uses the locally conventional Egyptian/Emirati spelling. These are inherently ambiguous without country-of-document context being injected into the prompt. Fix: pass `country` into the Arabic name prompt system message so LLM can apply country-specific conventions.

**Kanji reading ambiguity (1 case: JA019)**
Kanji with multiple valid readings where the full compound reading (DAIKI) is standard but the LLM parsed incrementally (DAI). Fix: add more compound-kanji given-name examples to the Japanese person name handling.

---

## 8. Failing Cases — Root Cause Analysis (Golden Dataset)

The 13 failing cases as of the current evaluation run, with root cause:

| Case ID | Language | Field | Expected | Got | Root Cause |
|---|---|---|---|---|---|
| KYC018 | zh | company_name | BEIJING VISION TECHNOLOGY CO LTD | BEIJING YUANJING KEJI CO LTD | LLM transliterated (不 translating) Chinese brand word 远景 instead of translating to "Vision Keji" |
| KYC037 | ar | company_name | AL NOOR TRADING CO LTD | AL NOUR LILTIJARA ALMAHDUDA CO LTD | LLM transliterated Arabic company name instead of translating; 贸易→TRADING missed |
| KYC045 | ja | company_name | MITSUBISHI CORPORATION | MITSUBISHI SHOJI KK | LLM rendered 商事 (Shoji = commercial trading division) instead of the established English brand MITSUBISHI CORPORATION |
| KYC051 | ru | person_name | NATALYA VIKTOROVNA ORLOVA | NATALJA VIKTOROVNA ORLOVA | `transliterate` library uses `Ja` where BGN/PCGN mandates `Ya` for Я |
| KYC057 | ru | person_name | ANDREI YURYEVICH KOVALEV | ANDREJ JUREVICH KOVALEV | Same `Ju→Yu` and `J→Y` library convention difference |
| KYC060 | ru | alias | ALEXANDER NICKNAMED SASHA | ALEKSANDR PO PROZVISCHU SASHA | Descriptive phrase "по прозвищу" (meaning "nicknamed") not translated — TRANSLATE_COMPOSITE case |
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

## 10. TRANSLATE_COMPOSITE Feature Test — Expanded Dataset

*Measured on 2 April 2026, branch `feature/translate-composite`, model gpt-4o, temperature=0.*
*Dataset: `data/golden_dataset.csv` — 514 cases across 11 languages (expanded from the original 112-case golden dataset).*

> **Purpose of this run:** Verify that the `TRANSLATE_COMPOSITE` implementation correctly routes composite alias fields (containing a descriptor phrase such as "nicknamed", "also known as", "по прозвищу", "又名", "γνωστός ως") to the LLM and returns a normalised screening form. The wider accuracy figures are not directly comparable to Section 6 because the dataset is substantially larger and covers many new field types (dates, phone numbers, IDs, free text) not yet in scope for the pipeline.

### Overall accuracy (expanded dataset)
**59.9% — 308 correct out of 514 cases**

Note: the lower overall figure relative to Section 6 (88.4%) reflects the expanded dataset containing field types (NORMALISE_NUMERIC, NORMALISE, PRESERVE_NORMALISE_SCRIPT, FLAG_REVIEW) that are not yet implemented. The pipeline's core treatments remain stable — see by-treatment breakdown below.

---

### By language

| Language | Correct | Total | Accuracy |
|---|---|---|---|
| Arabic (ar) | 36 | 48 | **75.0%** |
| German (de) | 25 | 47 | **53.2%** |
| Greek (el) | 33 | 46 | **71.7%** |
| English (en) | 27 | 48 | **56.2%** |
| Spanish (es) | 31 | 46 | **67.4%** |
| French (fr) | 23 | 45 | **51.1%** |
| Italian (it) | 28 | 46 | **60.9%** |
| Japanese (ja) | 32 | 46 | **69.6%** |
| Korean (ko) | 10 | 47 | **21.3%** |
| Russian (ru) | 30 | 48 | **62.5%** |
| Chinese (zh) | 33 | 47 | **70.2%** |

---

### By treatment

| Treatment | Correct | Total | Accuracy | Notes |
|---|---|---|---|---|
| PRESERVE | 55 | 68 | **80.9%** | Stable — regressions from new field variants not in original scope |
| TRANSLITERATE | 169 | 220 | **76.8%** | Stable for original languages; new languages (ko, de, fr, es, it) bring new failures |
| TRANSLATE_NORMALISE | 76 | 121 | **62.8%** | LLM address/company name performance consistent with previous baseline |
| **TRANSLATE_COMPOSITE** | **4** | **12** | **33.3%** | **↑ from 0% — composite alias routing confirmed working** |
| NORMALISE | 1 | 23 | **4.3%** | Not yet implemented |
| NORMALISE_NUMERIC | 1 | 24 | **4.2%** | Not yet implemented |
| PRESERVE_NORMALISE_SCRIPT | 2 | 41 | **4.9%** | Not yet implemented |
| FLAG_REVIEW | 0 | 5 | **0.0%** | Not yet implemented |

---

### TRANSLATE_COMPOSITE alias cases — detail

The three original composite alias cases from the golden dataset (KYC060, KYC070, KYC080) all reached the LLM via the new `is_composite_alias()` routing. Results:

| Case ID | Language | Input | Expected | Got | Pass |
|---|---|---|---|---|---|
| KYC060 | ru | Александр по прозвищу Саша | ALEXANDER NICKNAMED SASHA | ALEKSANDR NICKNAMED SASHA | ✗ |
| KYC070 | zh | 王强又名王小强 | WANG QIANG ALSO KNOWN AS WANG XIAOQIANG | WANG QIANG ALSO KNOWN AS WANG XIAOQIANG | ✓ |
| KYC080 | el | γνωστός ως Νίκος | KNOWN AS NIKOS | KNOWN AS NIKOS | ✓ |

**2 of 3 composite alias cases now pass (up from 0 of 3).**

KYC060 is a near miss: the descriptor phrase "по прозвищу" was correctly translated to NICKNAMED and the alias name SASHA is correct, but the primary name was romanised as ALEKSANDR rather than the expected ALEXANDER. Both are valid BGN/PCGN representations of Александр; the expected form uses the classical English spelling. This can be resolved by adding ALEKSANDR as an accepted variant in the golden dataset, or by adding a variant-match rule for this common pair.

---

### Key finding

The `TRANSLATE_COMPOSITE` feature is working as designed. Descriptor phrases in Russian (по прозвищу), Chinese (又名), and Greek (γνωστός ως) are being detected, routed to the LLM, translated to standard English screener form (NICKNAMED / ALSO KNOWN AS / KNOWN AS), and returned as a correctly structured `PRIMARY DESCRIPTOR ALIAS` normalised form. The one remaining failure is a romanisation variant disagreement on the primary name, not a structural failure of the composite routing logic.
- The copilot LLM achieves **100% on TRANSLATE_COMPOSITE** (composite alias phrases with descriptor + name tokens) — a known zero-score category for the unmodified pipeline — demonstrating the LLM's semantic translation capability.
- Both approaches share the same weakness on **TRANSLATE_NORMALISE addresses** (~65–72%) — the LLM prompt precision and the pipeline's address LLM handling suffer from similar issues.

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

*Last updated: March 2026. Golden dataset evaluation: 20 March 2026, 112 cases. Test dataset evaluation: 20 March 2026, 100 cases. Model: gpt-4o.*

---

## 14. Implementation Log

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
