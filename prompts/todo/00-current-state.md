# KYC Identity Normalisation — Current State

## What exists today

The repository (`kyc-identity-normalisation-poc`) is a Python proof of concept for KYC identity normalisation. It processes pre-labelled identity field rows and produces normalised Latin-script output suitable for screening. It currently includes both a Streamlit web UI (`app.py`) and Python CLI runners (`src/main.py`, `src/run_ocr.py`).

### What it does well

**Deterministic normalisation for Latin-script languages** is fully implemented and production-quality. German umlaut expansion (Ä→AE, ß→SS), French accent stripping, Spanish accent stripping with ñ variants, Italian accent stripping and apostrophe particle handling, English Mac/Mc/St/apostrophe variant generation, and Korean Revised Romanisation with hard-coded surname variant tables all work correctly and are covered by tests.

**Cyrillic transliteration** (Russian, Ukrainian, Bulgarian, Belarusian) via the `transliterate` library with BGN/PCGN post-processing corrections is implemented and tested. Ukrainian-exclusive character detection (Є, І, Ї) auto-switches language mode.

**Japanese transliteration** via `pykakasi` with a Kanji ambiguity lookup table (`kanji_lookup.py`) and Cantonese/Wade-Giles variant generation for HK/TW documents is implemented.

**Chinese Pinyin** via `pypinyin` with given-name fusion (Wang Xiaoming not Wang Xiao Ming) and Cantonese surname variants is implemented.

**Greek transliteration** via the `transliterate` library with ου→ou post-processing correction is implemented.

**Arabic basic consonant mapping** exists as a fallback but is flagged `review_required=True` by design, because short vowel insertion requires the LLM.

**Date and calendar normalisation** via `calendar_utils.py` handles Japanese era-year (Meiji through Reiwa), Hijri calendar conversion, Eastern Arabic numeral conversion, and ISO 8601 output.

**LLM integration** via OpenAI GPT-4o handles Arabic person names (with BGN/PCGN structured JSON output and variants), non-Latin-script addresses (translated to English), and company names. Prompts are in `prompts/`.

**Variant generation** (`allowed_variants` list) is implemented for all languages — enabling downstream screening to match any plausible romanisation.

**Confidence and review flagging** are implemented inline in `rules_engine.py`, `transliteration_engine.py`, and `llm_layer.py`. There is no standalone `confidence_calibrator.py` module in the current repo.

**Evaluation framework** with a golden dataset, regression gate, and CSV/JSON output is in place.

**UI** The tool has a Streamlit web interface (`app.py`) with three tabs: KYC Normalise (single field), Documents (file upload), and Batch CSV. `src/main.py` is a separate CLI entry point for evaluation/batch execution.

**Document ingestion** The Documents tab accepts jpg, jpeg, png, pdf, docx, and txt files (max 10 MB). For images and scanned PDFs, GPT-4o Vision performs OCR and field extraction. For PDFs with embedded text, `pymupdf` extracts text which is then passed to GPT-4o for field identification. For docx and txt, text is extracted and passed to GPT-4o. The Batch CSV tab accepts CSV files with `original_text`, `field_type`, and `language` columns.

**OCR** OCR is implemented via GPT-4o Vision (src/pipeline/ocr_gate.py and app.py). There is no Tesseract integration — all image-to-text extraction uses GPT-4o Vision. src/utils/script_detection.py provides a Unicode script range detector but is not used for OCR engine selection.

**Language auto-detect** There is no local language detection library. The UI offers an 'Auto-detect' option which passes an empty language string to the pipeline. In the Documents tab, GPT-4o assigns a language code to each extracted field as part of its extraction response. If language is empty for name/alias transliteration, the engine uses a unidecode fallback and flags `review_required=True`. For `address` and `company_name`, the pipeline routes to the LLM path (not unidecode fallback). `script_detection.py` provides dominant-script detection and Belarusian detection (`detect_belarusian` via the exclusive `Ў` character). Ukrainian character detection is implemented directly in `transliteration_engine.py`, not in `script_detection.py`.

### What it does not do

- There is no Flask interface — the current UI is Streamlit.
- A 'Translate' tab is referenced in UI copy but was never built.
- There is no MRZ or barcode parsing.
- There is no deterministic local language-detection library at ingestion time. In the Documents tab, GPT-4o supplies language codes during extraction; in Batch CSV, language may be blank but behavior then depends on field routing (fallback transliteration for name/alias, LLM route for address/company_name).
- There is no verified translation repository. Every input is processed from scratch every time.
- There is no geographic name lookup (countries, cities, place names).
- There is no finite vocabulary lookup for legal forms, company status terms, or role/designation titles.
- There is no analyst review workflow. Flagged fields are marked in the output but there is no mechanism to route them to a reviewer.
- There is no native speaker registry or escalation workflow.
- There is no email notification system.
- There is no user authentication or access control.
- There is no audit logging.
- There is no database. All state is in flat files (CSV, JSON).
- The LLM (GPT-4o) is used for all Arabic person names, all non-Latin addresses, and all company names regardless of whether a deterministic answer exists.

### Technology stack today

- **Application:** Streamlit web app + Python CLI runners
- **Language/runtime:** Python (project intent 3.13; local environment currently runs 3.14)
- **Interface:** Streamlit
- **LLM:** OpenAI GPT-4o via `openai` Python SDK
- **Key libraries:** `transliterate`, `pykakasi`, `pypinyin`, `unidecode`, `pymupdf`, `python-docx`, `Pillow`, `hijri-converter`, `korean-romanizer` (optional)
- **Storage:** Flat files (CSV input, CSV/JSON output)
- **Tests:** `pytest`
- **CI:** GitHub Actions regression gate

### Repository structure (key files)

```
src/
  main.py                          # CLI entry point
  pipeline/
    pipeline.py                    # Field routing logic
    rules_engine.py                # PRESERVE and NORMALISE_NUMERIC handling
    transliteration_engine.py      # All script-to-Latin conversion
    llm_layer.py                   # OpenAI integration
    field_classifier.py            # Composite alias detection
    analyst_handler.py             # Composite alias routing
    matcher.py                     # Match helper for evaluator
    ocr_gate.py                    # OCR via GPT-4o Vision
  config/
    rules.py                       # Field type → treatment mapping
    language_normalisation_tables.py  # Character maps, Korean surname table
    kanji_lookup.py                # Kanji reading ambiguity table
    cantonese_surname_map.py       # HK/TW surname variants
  utils/
    calendar_utils.py              # Date/era conversion
    script_detection.py            # Script/language detection helpers
    normalisation.py               # Unicode helpers
  evaluation/
    evaluator.py
    metrics.py
    regression_gate.py
prompts/
  prompt_address.txt
  prompt_company.txt
  prompt_person_name.txt
  prompt_person_name_ar.txt
data/
  golden_dataset.csv
  test_dataset.csv
tests/
```


# Repository-wide validation notes (added after full code review)
1. There is no `src/pipeline/confidence_calibrator.py` in the current codebase. Confidence is currently assigned inside rule/transliteration/LLM outputs.
2. `src/pipeline/matcher.py` and `src/utils/logging_utils.py` exist and are relevant; they were missing from the structure summary.
3. `src/utils/input_validator.py` does not exist, but `src/utils/__pycache__/input_validator.cpython-313.pyc` exists, indicating it existed previously and was removed.
4. `requirements.txt` includes `hijri-converter`, `korean-romanizer` (optional fallback note), and `Pillow`; these are part of the current runtime dependency set.
5. The `documentation/` folder is substantial and already includes linguistic, governance, evaluation, and EU AI Act technical documents; this should be treated as active project assets.
6. The repository includes real sample documents under `data/images/` (passport, ID, proof of address, company documents), plus `prompts/for_copilot/` prompt assets.
7. CI workflow currently invokes `python src/main.py --regression-gate`, but `src/main.py` does not parse CLI flags, so the documented regression-gate invocation is inconsistent with runtime entrypoint behavior.
8. Current local test run status in this environment: most tests pass, but LLM-dependent tests fail when API quota is exhausted (`openai.RateLimitError: insufficient_quota`). This is an environment/runtime constraint, not a deterministic layer regression.