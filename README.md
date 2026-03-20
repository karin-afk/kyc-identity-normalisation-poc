# KYC Identity Normalisation POC

Multi-language identity field normalisation for KYC/AML workflows. Covers Arabic, Japanese, Russian, Chinese, and Greek.

## Quick start

```bash
pip install -r requirements.txt
pytest                   # run unit tests
python src/main.py       # run full evaluation against the golden dataset
```

## API keys

Copy `.env.example` to `.env` and fill in your keys:

```
cp .env.example .env
```

| Key | Purpose | Required for |
|-----|---------|-------------|
| `OPENAI_API_KEY` | LLM calls (address/company translation) | `src/pipeline/llm_layer.py` |
| `OPENAI_API_KEY` + GPT-4o Vision | OCR extraction (Phase 2) | `src/pipeline/ocr_gate.py` |
| `AZURE_DOCUMENT_INTELLIGENCE_*` | Azure DI OCR alternative (Phase 2) | `src/pipeline/ocr_gate.py` |

If no API key is set, the LLM layer stubs gracefully and flags fields as `review_required=True`.

## Where the API connections live

| File | Connection |
|------|-----------|
| `src/pipeline/llm_layer.py` | OpenAI / Azure OpenAI — translate addresses and company names |
| `src/pipeline/ocr_gate.py` | **Phase 2** — GPT-4o Vision or Azure Document Intelligence for OCR |

## Phase 1 vs Phase 2

| Phase | What runs |
|-------|-----------|
| **1 (now)** | Transliteration pipeline + LLM for addresses. Input = pre-extracted text rows. |
| **2 (next)** | Add OCR gate (`ocr_gate.py`) to accept raw document images. |

## Language coverage

| Language | Script | Method | Notes |
|----------|--------|--------|-------|
| Russian / Ukrainian | Cyrillic | `transliterate` lib | BGN/PCGN-ish |
| Greek | Greek | `transliterate` lib | ISO 843-ish |
| Japanese | Kana / Kanji | `pykakasi` | Katakana accurate; Kanji flagged for review |
| Chinese (Mandarin) | Han | `pypinyin` | Pinyin; name order flagged for review |
| Arabic | Arabic | Consonant map | Vowel ambiguity — requires LLM for accuracy |

## Golden dataset

`data/golden_dataset.csv` — 30 cases across all 5 languages + Latin preserve cases.

Columns: `case_id, language, script, country, document_type, field_type, original_text, expected_treatment, expected_transliteration, expected_allowed_variants, expected_english, expected_normalised, should_flag_review, is_negative_case, risk_notes`

## Project structure

```
src/
  main.py                     ← entry point / evaluator runner
  config/rules.py             ← field treatment configuration
  pipeline/
    pipeline.py               ← orchestrates the layers
    rules_engine.py           ← PRESERVE deterministic rules
    transliteration_engine.py ← script-to-Latin (5 languages)
    llm_layer.py              ← OpenAI translation (+ API connection)
    ocr_gate.py               ← Phase 2 OCR stub (+ API connection)
    field_classifier.py       ← field_type → treatment mapping
    matcher.py                ← normalised-form matching
  utils/
    normalisation.py          ← ASCII normalisation helper
    script_detection.py       ← Unicode script detection
    logging_utils.py          ← logger factory
  evaluation/
    evaluator.py              ← runs pipeline over golden dataset
    metrics.py                ← accuracy / per-language breakdown
tests/
  test_rules.py               ← PRESERVE field tests
  test_transliteration.py     ← per-language transliteration tests
  test_pipeline.py            ← end-to-end layer routing tests
  test_evaluator.py           ← golden dataset evaluation tests
prompts/
  prompt_person_name.txt      ← LLM prompt: name transliteration
  prompt_address.txt          ← LLM prompt: address translation
  prompt_company.txt          ← LLM prompt: company name translation
data/
  golden_dataset.csv          ← 30-row ground-truth evaluation set
```
