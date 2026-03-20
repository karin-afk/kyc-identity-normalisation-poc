# AI Governance and Responsible AI — KYC Identity Normalisation

## 1. Why Governance Matters in This Context

KYC (Know Your Customer) identity screening is one of the highest-stakes use cases for automated identity processing. The pipeline operates in the context of:

- **Anti-money laundering (AML)** — identifying individuals and entities on sanctions and watchlists
- **Counter-terrorism financing (CTF)** — matching names against terrorist designation lists
- **Sanctions compliance** — screening against OFAC SDN, EU Consolidated List, UN list, and others

In this context, **an incorrect or incomplete normalisation can directly cause a false negative**: a sanctioned individual fails to match a list entry because the names were romanised differently. The reputational, regulatory, and criminal consequences for the institution are severe.

This document describes the governance framework embedded in the pipeline's design — specifically, how the use of AI/LLM is minimised, where it is used, how determinism is enforced wherever possible, and what review mechanisms exist.

---

## 2. Core Governance Principle — Minimal LLM Use

The pipeline is designed around a **hard hierarchy of processing layers**, applied in order of decreasing determinism:

```
Layer 1: RULE        — deterministic, no AI, output is exact
Layer 2: TRANSLITERATE — deterministic, no AI, output is rule-derived
Layer 3: LLM         — probabilistic, AI, used only when layers 1 and 2 cannot produce
                         a reliable output
```

LLM is used **only when deterministic methods are structurally insufficient** — not as a convenience, and not as a default. The specific conditions that trigger LLM use are described in Section 4.

### Why determinism matters for KYC

| Property | Deterministic pipeline | LLM pipeline |
|---|---|---|
| Same input always produces same output | ✅ Yes | ❌ Not guaranteed |
| Output can be audited against a rule | ✅ Yes | ❌ Rules are implicit in model weights |
| Output is explainable to a regulator | ✅ Yes | ⚠ Requires chain-of-thought logging |
| Output changes when model is retrained | ✅ No | ❌ Yes — silent regressions possible |
| API dependency / availability risk | ✅ None | ⚠ Requires API uptime |

For regulators and internal audit, a deterministic pipeline is strongly preferred. The pipeline therefore applies the LLM layer as narrowly as possible.

### Model pinning
The LLM model is pinned at definition time:

```python
MODEL = "gpt-4o"  # Pin model version for reproducibility
```

This ensures that pipeline output does not silently change when a new model version is deployed by the API provider. Any model upgrade requires an explicit code change and regression testing against the golden dataset.

### Temperature = 0
All LLM calls use `temperature=0`:

```python
response = client.chat.completions.create(
    model=MODEL,
    temperature=0,     # deterministic decoding
    max_tokens=300,
    ...
)
```

Temperature 0 instructs the model to always select the highest-probability token at each step, making the output **maximally deterministic** within the model's decoding algorithm. This is a necessary but not sufficient condition for true determinism (greedy decoding can still be affected by floating-point non-determinism across hardware), but it substantially reduces variability.

---

## 3. Processing Layer Architecture — What Each Layer Does

### Layer 1: Rules Engine (`src/pipeline/rules_engine.py`)

Handles field types that must be **preserved exactly** as received:

| Field type | Governance rationale |
|---|---|
| `passport_no` | Document numbers are opaque identifiers; any normalisation would corrupt the data |
| `id_no` | Same as above |
| `email` | Standardised structure; no transliteration needed |

These fields are returned with `confidence=1.0` and `review_required=False`. No AI involvement.

### Layer 2: Transliteration Engine (`src/pipeline/transliteration_engine.py`)

Handles **person names and aliases** using deterministic, library-based script-to-Latin conversion. Each language uses a specific, published, internationally recognised standard:

| Language | Library | Standard |
|---|---|---|
| Russian (ru) | `transliterate` | BGN/PCGN-influenced |
| Ukrainian (uk) | `transliterate` + manual pre-processing | Cabinet of Ministers of Ukraine (2010) |
| Bulgarian (bg) | `transliterate` | BGN/PCGN-influenced |
| Greek (el) | `transliterate` | ISO 843 |
| Japanese (ja) | `pykakasi` | Hepburn (ICAO Doc 9303) |
| Chinese (zh) | `pypinyin` | Hànyǔ Pīnyīn (ICAO Doc 9303) |

These libraries apply fixed character-mapping tables. Given the same input string, they always return the same output. No API call is made. No model weights are involved.

**Exception**: Japanese Kanji characters have multiple valid readings. The `KANJI_AMBIGUITY` lookup table (`src/config/kanji_lookup.py`) provides explicitly curated lists of readings, maintained as source code. This is an expert-curated deterministic lookup — not AI.

### Layer 3: LLM Layer (`src/pipeline/llm_layer.py`)

Used only for the field types and languages described in Section 4. All LLM calls:
- Use `temperature=0` (maximum determinism)
- Use a pinned model version (`gpt-4o`)
- Use structured prompts stored in version-controlled files (`prompts/`)
- Request structured JSON output for Arabic names (to guarantee parseable variants)
- Return `processing_method="LLM"` and `model_version` in every result for auditability

---

## 4. When and Why LLM Is Used — Field-by-Field Rationale

### 4.1 Arabic Person Names and Aliases — LLM Required

**Why deterministic transliteration is impossible for Arabic names:**

Arabic standard text omits short vowels (harakat). The name محمد is written with four consonants: M-H-M-D. Without knowing which vowels belong between them, a rule-based system cannot determine whether the name should be Muhammad, Mohammed, Mohamed, Mohammad, or Muhammed — all of which are legitimate romanisations used in real documents.

A character-by-character consonant map produces `mhmd`, which is not a usable screening term.

The LLM is given world-knowledge of real Arabic names and can supply the correct vowels from the name lexicon. This is the only technically viable approach.

**Governance controls for Arabic LLM use:**
- The prompt mandates **BGN/PCGN as the primary romanisation standard** — not the model's own preference.
- The prompt mandates JSON output with explicit `primary` and `variants` keys.
- The `variants` array must cover the Mohammed/Mohamed/Mohammad family and the Al-/El- prefix family at minimum.
- All Arabic LLM results return `confidence=0.85` rather than 1.0, reflecting residual model uncertainty.
- The `allowed_variants` list is used at matching time, so no single romanisation choice can cause a false negative.

The basic consonant-map transliterator (`_transliterate_arabic`) is available as a fallback when no API key is set, but its output is always marked `review_required=True` precisely because it cannot supply vowels.

### 4.2 Addresses (all languages) — LLM Required

Addresses are **not transliterated — they are translated and normalised**. Phonetic transliteration of addresses is inappropriate because:
- Street names, city names, district names have official English equivalents (SHEIKH ZAYED ROAD, not SHARIK ASH-SHAKH ZAYD).
- Numbers and administrative units (区 = District, 市 = City, ул. = Street) require semantic interpretation.
- Transliterated addresses are unusable for analyst verification against maps and databases.

**Governance controls for address LLM use:**
- The prompt explicitly prohibits inventing or omitting any address component.
- All address results carry the processing method `LLM` for auditability.
- Lenient matching is applied at evaluation time: comma/hyphen stripping and token-set matching handle minor LLM formatting variations without requiring model output to be bitwise identical.

### 4.3 Company Names (all languages) — LLM Required

Company names contain:
- Descriptive words that have English equivalents (科技 = Technology, πενεργειακής = Energy)
- Legal form suffixes that must be mapped to standard English equivalents (ООО → LLC, 株式会社 → Co Ltd)
- Established brand names that have canonical English forms regardless of literal translation (三菱 → MITSUBISHI, 腾讯 → TENCENT, ソニー → SONY)

The LLM prompt contains explicit rules distinguishing **Cyrillic company names** (transliterate the root words, do not translate their meaning) from **all other scripts** (translate generic words, preserve known brand names).

**Known limitation**: Brand-name resolution relies on the LLM's world knowledge. Lesser-known brands may not be resolved correctly. This is flagged in failing cases (KYC018, KYC065, KYC091, KYC092).

### 4.4 Cyrillic Person Names — LLM Not Used

For Russian, Ukrainian, and Bulgarian person names, the deterministic transliteration library is sufficient and is always used. The LLM is never called for these names. The library produces consistent BGN/PCGN-compliant output with known, documented behaviour.

### 4.5 Japanese Person Names — LLM Not Used

Person names in hiragana and katakana are handled deterministically. Kanji names use the curated `KANJI_AMBIGUITY` lookup table in source code. The LLM is never called for Japanese person names.

### 4.6 Chinese Person Names — LLM Not Used

Chinese person names are converted to Pinyin deterministically using `pypinyin`. The LLM is never called for Chinese person names.

### 4.7 Greek Person Names — LLM Not Used

Greek person names are transliterated deterministically using the `transliterate` library. The LLM is never called for Greek person names.

---

## 5. Variant Generation — Reducing False Negatives

A key risk in KYC screening is the **false negative**: the same individual appears on a list under a different romanisation and the system fails to flag a match. The pipeline addresses this with a multi-layered variant strategy:

### 5.1 Primary + variants from LLM (Arabic)
The Arabic LLM prompt returns structured JSON:
```json
{
  "primary": "MUHAMMAD ALI HASSAN",
  "variants": ["MOHAMMED ALI HASSAN", "MOHAMED ALI HASAN", "MOHAMMAD ALI HASSAN"]
}
```
All variants are stored in `allowed_variants` and tested at match time.

### 5.2 Kanji reading variants (Japanese)
For every kanji token with multiple valid readings, all readings are combined into full-name variant strings stored in `allowed_variants`. Example: 佐藤 健 → primary `SATO KEN`, variants include `SATO TAKESHI`, `SATO MASARU`.

### 5.3 Golden dataset variants
The golden dataset includes an `expected_allowed_variants` column with pipe-separated accepted forms. At evaluation time, a match is also accepted if the actual output matches any dataset-listed variant. This models the real-world requirement that screening should accept any valid romanisation.

### 5.4 Canonical matching (Arabic)
A post-processing canonical matching step strips Al-/El- prefixes and normalises known variant spellings (MOHAMMED→MUHAMMAD, HASAN→HASSAN) before comparison, ensuring that romanisation-family differences do not cause false negatives.

### 5.5 Company name lenient matching
Three-pass matching for company names:
1. Exact match after removing dots from acronym suffixes (S.A.→SA) and mapping verbose synonyms (CORPORATION→CORP)
2. Core match: strip all trailing legal-suffix tokens (LTD, PLC, LLC, INC, etc.) and compare the bare company root

---

## 6. Confidence and Review Flags

Every pipeline result carries explicit governance metadata:

| Field | Type | Purpose |
|---|---|---|
| `processing_method` | `RULE` / `TRANSLITERATE` / `LLM` | Which layer produced this result |
| `confidence` | 0.0–1.0 | Reliability estimate |
| `review_required` | bool | Whether an analyst must verify before using |
| `review_reason` | string | Specific reason for flagging |
| `should_use_in_screening` | bool | Whether output is safe for automated screening |
| `model_version` | string / null | Model used (LLM results only) |

### Confidence levels by layer

| Layer | Confidence | Rationale |
|---|---|---|
| RULE | 1.0 | Exact preservation — no uncertainty |
| TRANSLITERATE (no review) | 0.9 | Deterministic but variant ambiguity possible |
| TRANSLITERATE (review flagged) | 0.7 | Deterministic but reading or script ambiguity present |
| LLM | 0.85 | Model has world knowledge but residual uncertainty |
| LLM (stub — no key) | 0.0 | No processing performed |

### Automatic review triggers

| Condition | Flag | Reason |
|---|---|---|
| Ukrainian/Russian script ambiguity | `review_required=True` | Script detection cannot distinguish with certainty |
| Japanese Kanji | `review_required=True` | Reading ambiguity; furigana or MRZ required |
| Chinese name order | `review_required=True` | Surname-first ordering; analyst confirms |
| Any Arabic without LLM key | `review_required=True` | Vowel ambiguity unresolved |
| LLM stub active | `review_required=True` | No normalisation performed |

---

## 7. Graceful Degradation — No API Key Scenario

When `OPENAI_API_KEY` is not set, the pipeline does not fail or raise an error. Instead:
- The LLM stub returns `confidence=0.0`
- `review_required=True`
- `should_use_in_screening=False`
- A descriptive `review_reason` explains the situation

This ensures operational continuity: the system can ingest documents and produce results even without API access, with every unprocesed field clearly marked for analyst review. An analyst can then apply their own judgement rather than the system producing silently incorrect output.

---

## 8. Prompt Version Control and Auditability

All LLM prompts are stored as plain-text files in the `prompts/` directory and are version-controlled in git:

```
prompts/
  prompt_person_name.txt       — general person name (non-Arabic)
  prompt_person_name_ar.txt    — Arabic person name (BGN/PCGN + JSON output)
  prompt_address.txt           — address translation
  prompt_company.txt           — company name translation/normalisation
```

This ensures:
- Every prompt change is tracked, attributed, and reversible in the git log
- Prompt changes can be cross-referenced with evaluation score changes
- Regulators or auditors can verify exactly what instructions were given to the model

---

## 9. Streamlit Frontend — Input Validation and Size Limits

The Streamlit web application enforces upload limits as an additional control:

| Upload type | Limit | Rationale |
|---|---|---|
| Document images (JPG, PNG, PDF, DOCX, TXT) | 10 MB | Prevents processing of excessively large files that could contain non-KYC content |
| Batch CSV | 5 MB | Limits batch size to a manageable volume for review |

File type is validated against an accepted extensions list (`ACCEPTED_DOC_EXTENSIONS`). The OCR extraction path validates the MIME type before passing content to the vision model.

---

## 10. What This Pipeline Does Not Do

To be explicit about the scope boundaries:

| This pipeline does NOT | Reason |
|---|---|
| Make a match/no-match screening decision | That is the responsibility of the downstream screening system |
| Assess whether an individual is sanctioned | Out of scope — the pipeline normalises, it does not screen |
| Store or log personal data | The Streamlit app is stateless; no PII is persisted |
| Generate speculative variants beyond the defined rules | All variant generation follows documented, auditable rules |
| Use LLM for transliteration when deterministic methods exist | LLM is only used when no deterministic solution is available |

---

## 11. Residual Risks and Known Limitations

| Risk | Description | Mitigation |
|---|---|---|
| LLM model update | OpenAI may change model behaviour silently | Model is pinned; any upgrade requires explicit regression test |
| Chinese brand name coverage | LLM may not know lesser-known brand names | Flag in evaluation; analyst review for company_name fields |
| Russian Ja/Ju vs Ya/Yu | `transliterate` library uses Ja/Ju where BGN/PCGN mandates Ya/Yu | Known issue; `allowed_variants` on golden dataset covers expected forms |
| TRANSLATE_ANALYST fields | Alias fields containing descriptive phrases (e.g. "NICKNAMED SASHA") are not yet handled deterministically | 0% on current TRANSLATE_ANALYST category; under development |
| Cantonese names | `zh` handler uses Mandarin Pinyin | Separate language code needed for HK documents |
| Handwritten documents | OCR quality affects input text quality | Field-level `review_required` flags propagate from input uncertainty |

---

*Last updated: March 2026. Pipeline version: v2.*
