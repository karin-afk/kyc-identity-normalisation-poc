# KYC Identity Normalisation POC

Multi-language identity field normalisation for KYC/AML screening workflows. Converts non-Latin identity fields (names, aliases, addresses, company names) from Arabic, Japanese, Russian/Ukrainian, Chinese, and Greek into normalised Latin-script forms suitable for sanctions screening.

**Live demo:** [Streamlit app](https://karin-afk-kyc-identity-normalisation-poc.streamlit.app) — upload a document or enter a field directly.

**Current accuracy: 88.4% (99/112 golden-dataset cases)** — see [Evaluation Results](#evaluation-results) below.

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run unit tests (no API key required)
PYTHONPATH=src pytest tests/ -q

# Run full evaluation against the golden dataset
# (requires OPENAI_API_KEY for LLM fields: Arabic names, addresses, company names)
cp .env.example .env          # then add your key
PYTHONPATH=src python src/main.py
```

---

## API Keys

| Key | Purpose | Required for |
|-----|---------|-------------|
| `OPENAI_API_KEY` | Arabic name transliteration, address/company translation via GPT-4o | `src/pipeline/llm_layer.py` |
| `OPENAI_API_KEY` (Vision) | OCR extraction from scanned documents | `app.py` Documents tab |

If no API key is set, the LLM layer stubs gracefully — fields are returned with `confidence=0.0` and `review_required=True`. All deterministic fields (Cyrillic, Greek, Japanese, Chinese person names) still process correctly without a key.

For **Streamlit Cloud deployment**, set `OPENAI_API_KEY` in the app's Secrets panel as:
```toml
OPENAI_API_KEY = "sk-proj-..."
```

---

## How the Pipeline Works

The pipeline applies three layers in order — LLM is only used when deterministic methods are insufficient:

```
Input field
    │
    ▼
Layer 1: RULE ENGINE        ← passport_no, id_no, email → preserved exactly
    │ (no match → continue)
    ▼
Layer 2: TRANSLITERATION    ← person_name, alias (non-Arabic) → deterministic
    │   Russian/Ukrainian: transliterate lib (BGN/PCGN)
    │   Greek:             transliterate lib (ISO 843)
    │   Japanese:          pykakasi (Hepburn) + kanji lookup table
    │   Chinese:           pypinyin (Pinyin) + given-name fusion
    │ (Arabic names or address/company → continue)
    ▼
Layer 3: LLM (GPT-4o)       ← Arabic names (vowel ambiguity requires world-knowledge)
                            ← addresses (semantic translation required)
                            ← company names (brand-name resolution required)
```

Every result carries: `processing_method`, `confidence`, `review_required`, `review_reason`, `allowed_variants`.

---

## Language Coverage

| Language | Script | Layer | Standard | Notes |
|----------|--------|-------|----------|-------|
| Arabic (ar) | Arabic | LLM | BGN/PCGN | Short vowels absent from text — LLM supplies them; returns primary + variants as JSON |
| Russian (ru) | Cyrillic | Transliterate | BGN/PCGN | Soft sign stripped; `Ja/Ju` known issue vs `Ya/Yu` |
| Ukrainian (uk) | Cyrillic | Transliterate | CMU 2010 | Ukrainian-char detection auto-switches from `ru` mode |
| Bulgarian (bg) | Cyrillic | Transliterate | BGN/PCGN | Handled via same library as Russian |
| Greek (el) | Greek | Transliterate | ISO 843 | `ου→ou` post-processed |
| Japanese (ja) | Kana/Kanji | Transliterate | Hepburn (ICAO 9303) | Kanji uses curated reading lookup; all readings added to `allowed_variants` |
| Chinese (zh) | Han | Transliterate | Pinyin (ICAO 9303) | Surname-first; given-name syllables fused |
| Addresses | Any | LLM | — | Translated to English; not phonetically transliterated |
| Company names | Any | LLM | — | Brand-name resolution; Cyrillic companies transliterated, others translated |

---

## Evaluation Results

*Measured 20 March 2026, 112 golden-dataset cases, model: gpt-4o, temperature=0.*

### Overall: 88.4% (99 / 112)

| By language | Accuracy |
|---|---|
| English (en) | 100.0% (2/2) |
| Japanese (ja) | 96.0% (24/25) |
| Arabic (ar) | 94.7% (18/19) |
| Greek (el) | 88.9% (16/18) |
| Russian/Ukrainian (ru) | 83.3% (15/18) |
| Chinese (zh) | 80.0% (24/30) |

| By processing method | Accuracy |
|---|---|
| PRESERVE | 100.0% (13/13) |
| TRANSLITERATE | 97.0% (65/67) |
| TRANSLATE_NORMALISE | 72.4% (21/29) |
| TRANSLATE_ANALYST | 0.0% (0/3) — not yet implemented |

The 13 currently failing cases fall into four categories: (A) Chinese brand-name LLM resolution, (B) descriptive alias phrases (e.g. "nicknamed"), (C) Russian `Ja→Ya` library convention, (D) minor address suffix formatting. See [`documentation/03-evaluation-framework.md`](documentation/03-evaluation-framework.md) for full root-cause analysis.

---

## Streamlit App (3 tabs)

| Tab | Function |
|---|---|
| 🆔 KYC Normalise | Single-field normalisation — paste any name, address, or company name |
| 📄 Documents | Upload JPG/PNG/PDF/DOCX/TXT → GPT-4o Vision OCR → extract KYC fields → normalise all |
| 📊 Batch CSV | Upload CSV of fields → validate → run normalisation → download results |

Upload limits: documents ≤ 10 MB, CSV ≤ 5 MB.

---

## Documentation

| Document | Description |
|---|---|
| [`documentation/01-linguistic-approach.md`](documentation/01-linguistic-approach.md) | Linguistic analysis: writing systems, transliteration standards, ambiguities, and pipeline decisions for each language |
| [`documentation/02-ai-governance.md`](documentation/02-ai-governance.md) | AI governance and responsible use: minimal-LLM design, determinism strategy, confidence flags, audit trail, residual risks |
| [`documentation/03-evaluation-framework.md`](documentation/03-evaluation-framework.md) | Evaluation framework: golden dataset structure, matching algorithm, full performance results, failing-case root-cause analysis |

---

## Project Structure

```
app.py                        ← Streamlit frontend (3 tabs)
src/
  main.py                     ← CLI entry point / evaluation runner
  config/
    rules.py                  ← field treatment configuration (PRESERVE / TRANSLITERATE / TRANSLATE)
    kanji_lookup.py           ← curated kanji reading ambiguity table
  pipeline/
    pipeline.py               ← layer orchestration (Rule → Transliterate → LLM)
    rules_engine.py           ← Layer 1: PRESERVE deterministic rules
    transliteration_engine.py ← Layer 2: script-to-Latin (5 languages + fallback)
    llm_layer.py              ← Layer 3: GPT-4o for Arabic names / addresses / companies
    matcher.py                ← normalised-form matching (exact + variant)
    field_classifier.py       ← field_type → treatment mapping
  evaluation/
    evaluator.py              ← multi-pass matching (exact, variants, canonical, lenient)
    metrics.py                ← accuracy / per-language / per-field-type breakdown
  utils/
    normalisation.py          ← ASCII normalisation helper
    script_detection.py       ← Unicode script detection
    logging_utils.py          ← logger factory
tests/
  test_rules.py               ← PRESERVE field tests
  test_transliteration.py     ← per-language transliteration tests
  test_pipeline.py            ← end-to-end layer routing tests
  test_evaluator.py           ← golden dataset evaluation tests
prompts/
  prompt_person_name_ar.txt   ← Arabic name: BGN/PCGN + JSON variants output
  prompt_person_name.txt      ← General name transliteration (ICAO conventions)
  prompt_address.txt          ← Address translation and normalisation
  prompt_company.txt          ← Company name translation (Cyrillic vs other scripts)
data/
  golden_dataset.csv          ← 112-row ground-truth evaluation set (16 columns)
  output/                     ← Evaluation run artefacts (JSON + CSV, gitignored)
documentation/
  01-linguistic-approach.md   ← Per-language linguistic analysis
  02-ai-governance.md         ← Responsible AI and governance framework
  03-evaluation-framework.md  ← Evaluation methodology and results
```
