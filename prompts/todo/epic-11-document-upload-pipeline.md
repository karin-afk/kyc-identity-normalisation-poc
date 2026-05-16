# Epic 11 — Document upload pipeline (v2)

**File location:** `prompts/todo/epic-11-document-upload-pipeline.md`
**Status:** Specification — not yet implemented
**Depends on:**
  - Phase 1 pipeline at 84% on 164-test diagnostic (paste tab, router, strategies A–H)
  - Pre-Epic-11 Fix 1 committed (router decoupled from Flask context)
  - Pre-Epic-11 Fix 2 committed (orchestrator owns response shape)
**Blocks:** AIG Phase 2 — full document-driven KYC

---

## 1. Context

The app today has two transports planned, both feeding the same router:

```
Paste tab           Document upload
    │                     │
    ▼                     ▼
GPT-4o-mini         Azure Document
classifier          Intelligence
(field_type +       (layout or
 language)          prebuilt-idDocument)
    │                     │
    ▼                     ▼
                    GPT-4o-mini extraction
                    (fills closed Pydantic schema:
                     {field_name, value, language, source})
                    one record per field
                          │
                          ▼
   ┌──────────────────────┴──────────────┐
   ▼                                     ▼
            router.route_field()
            (existing Strategies A–H)
                          │
                          ▼
            normalised output for analyst review
```

**Paste tab is live and passes 138/164 golden tests.** It uses GPT-4o-mini as a *classifier* (decide what field_type the text is). No DI involved.

**Document tab is what this epic builds.** It uses DI for structure extraction, then GPT-4o-mini as a *schema filler* (decide which records to emit against a closed taxonomy). Same model, different role, different prompt.

Both flows converge at `router.route_field()`. The router does not change in this epic. Every fix that landed during Phase 1 (Korean surname policy, German umlaut expansion, US date handler, NMT casing, etc.) automatically applies to document-driven fields.

`app/pipeline/orchestrator.py::process_document_file()` currently raises `NotImplementedError`. This epic implements it.

---

## 2. Key design principle

**The router does not change.** If at any point in this epic Copilot finds itself wanting to add a field_type to the router, modify a strategy module, or alter `route_field()`'s signature, **stop and flag it**. That's a scope creep signal. The router's contract is fixed at the 84%/138-of-164 line. New field types are out of scope and belong in their own ticket.

The corollary: GPT-4o-mini in the extraction step **must emit field names that the router already accepts**, plus a small explicit-freeform escape hatch (§4.5). If the canonical taxonomy below contains a name the router doesn't have, that name does not get used — drop it from the schema or open a router ticket.

---

## 3. Document types and Document Intelligence routing

| Dropdown option | DI model | Pydantic schema |
|---|---|---|
| Government-issued ID | `prebuilt-layout` | `government_id_v1.json` |
| Commercial registry extract | `prebuilt-layout` | `commercial_registry_extract_v1.json` |
| Business registration / proof of incorporation | `prebuilt-layout` | `business_registration_v1.json` |
| Articles of Association | `prebuilt-layout` | `articles_of_association_v1.json` |
| Financial / due-diligence document | `prebuilt-layout` | `financial_due_diligence_v1.json` |
| Supporting registry proof / ownership attachment | `prebuilt-layout` | `ownership_attachment_v1.json` |
| Other / don't know | `prebuilt-layout` | `generic_v1.json` |

**The layout path is the primary path, not a fallback.** Engineering effort lives there.

### What the dropdown actually selects

Primarily, the dropdown selects **which Pydantic schema GPT-4o-mini fills**, not which DI model runs (six of seven options share the same DI model). The schema is the dropdown's real product value. A registry extract schema looks different from an AOA schema looks different from a financial-statements schema.

The aggregator picks the schema from the dropdown choice (or `generic_v1` if none selected) and passes (schema + DI layout output) to GPT-4o-mini.

### Out of scope

- Custom-trained DI models
- All US-specific prebuilts: `prebuilt-tax.*`, `prebuilt-mortgage.us.*`, `prebuilt-bankStatement`, `prebuilt-payStub.us`, `prebuilt-check.us`, `prebuilt-marriageCertificate.us`, `prebuilt-healthInsuranceCard.us`
- `prebuilt-invoice`, `prebuilt-receipt`, `prebuilt-businessCard` (deprecated), `prebuilt-creditCard`, `prebuilt-contract`
- `prebuilt-read` (superseded by `prebuilt-layout`)
- Any non-DI Azure service (no Content Understanding, no custom OCR)

---

## 4. Canonical field taxonomy

GPT-4o-mini fills records into a **closed taxonomy**. Free-form labelling allowed only as an explicit escape hatch (§4.5 rule 2), tagged so the analyst UI can distinguish it.

### 4.1 Individual (Government-issued IDs)

**Core:** `full_name`, `date_of_birth`, `nationality`, `id_number`, `address`, `issuing_authority`, `issue_date`, `expiry_date`
**Additional (when present):** `place_of_birth`, `father_name`, `mother_name`, `locality_registry_info`

### 4.2 Company — registry / registration

**Core:** `entity_name`, `registration_number`, `date_of_incorporation`, `registered_address`, `mailing_address` (only if separate), `legal_form`, `nature_of_business`, `status` (only if explicit), `document_date`

### 4.3 Company — management / control

One record per director/officer with: `director_name`, `director_role`, `director_date_of_birth` (if present), `director_country_of_residence` (if present)

### 4.4 Company — ownership (when available)

One record per shareholder with: `shareholder_name`, `shareholder_address`, `shareholder_shares_held`, `shareholder_voting_rights`, `shareholder_ownership_percentage`

### 4.5 Company — capital

`share_capital`, `issued_shares_count`, `capital_changes` (only if explicit)

### 4.6 Articles of Association — limited scope

Only `entity_name` and `registered_address`, both only when explicitly stated. Do not extract anything else from AOA documents.

### 4.7 Financial / due-diligence supporting data

`total_assets`, `total_liabilities`, `net_assets`, `revenue`, `expenses`, `financial_period`, `accounting_policies` (only if relevant)

### 4.8 Free-text prose blobs

Sections of running prose (business descriptions, risk factors, accounting notes) are extracted as **blobs**, not records. They are not fields. They route to NMT (Strategy H, `field_type=free_text`) and render in the analyst UI's prose panel (§9.2), not the field table.

---

## 5. GPT-4o-mini extraction prompt rules

The extraction prompt enforces these in order:

1. **Closed-enum priority.** For every extractable piece of content: "Does this fit one of the canonical field names in §4? If yes, emit using that name verbatim." Primary path. The full taxonomy goes at the top of every schema prompt.

2. **Best-fit fallback for unmatched content.** If meaningful content does not fit any canonical field, emit it with a freeform label that is:
   - Lower snake_case
   - Semantic (describes what the content *is*, not where it sits on the page)
   - Tagged `"extracted_as_freeform": true`
   - Not a synonym of a canonical field. `full_legal_name` is forbidden (`full_name` exists). `previous_company_names` is allowed (no canonical covers it).

3. **Drop, don't invent.** Illegible or absent content is silent. `null` is acceptable for an expected-but-missing canonical field. Don't invent a label to fill a gap.

4. **No reformatting at extraction time.** GPT-4o-mini returns the value **exactly as it appears in the source**. Normalisation is the router's job. If GPT-4o-mini pre-normalises (transliterates a name, converts an era date, parses currency, uppercases) we lose visibility, the variant tracking, and the analyst review trail. The whole 138/164 result of the existing pipeline depends on the router being the only normalisation point.

### Output contract per record

```json
{
  "field_name": "date_of_incorporation",
  "value": "平成31年1月15日",
  "language": "ja",
  "source": {"page": 2, "bbox": [120, 340, 280, 360]},
  "confidence": 0.92,
  "extracted_as_freeform": false
}
```

Plus a parallel list of blobs (free-text prose):

```json
{
  "section_heading": "事業の内容",
  "text": "...",
  "language": "ja",
  "source": {"page": 2}
}
```

### Determinism note

GPT-4o-mini at temperature=0 shows ~2% test-flip rate on the paste-tab classifier (low-confidence inputs). For document extraction the closed enum substantially reduces variance — the model picks from ~35 fixed targets rather than open generation. Phase 0 still budgets a 3-run variance check against the JAL fixture. If canonical-field assignment varies >5% between runs, escalate (prompt issue, not model issue).

---

## 6.0 Pre-investigation — existing scaffolding audit

Before Phase 0's codebase mapping, read every file below in full and report:

1. **`app/pipeline/ingestion.py`** — file validation, type detection, DB record creation. Is it working? What does the DB record look like? Does it already have a doc-type field that maps to our seven dropdown options?
2. **`app/tasks/ocr_task.py`** — Celery task submitting documents to Document Intelligence. Is the DI client already wired? Which DI model does it use? Sync or async? Where does the result go?
3. **All seven files under `app/pipeline/field_extraction_rules/`** — `aoa.py`, `business_registration.py`, `company_registry.py`, `drivers_licence.py`, `financial_statement.py`, `national_id.py`, `shareholder_table.py`. For each: what fields does it extract? What's the output format? Is this deterministic rule-based extraction, or does it call an LLM?
4. **`app/pipeline/field_extraction.py`** — what does this top-level module do, and how does it relate to the rule files in `field_extraction_rules/`?
5. **`app/models/document.py` and `app/models/translation.py`** — what columns exist? Specifically: does `Document` have a `document_type` field? Does `NormalisedField` already have fields for `field_name`, `original`, `normalised`, `method`, `source` (bbox)? If yes, the JSON output contract in §9.4 needs to match the DB model.

Output this report **before** proceeding to Phase 0. Three outcomes possible:

- **A: Working scaffolding.** Epic 11 wires existing modules together. The new code is mostly glue, not new extraction logic. Update the epic to remove §7.1's proposed module layout and instead specify changes to existing files.
- **B: Half-built scaffolding.** Some files have real logic, some are stubs. Epic 11 finishes the half-built ones and adds the missing glue. Update §7.1 to map proposed modules to existing files where they overlap.
- **C: Stale scaffolding.** Files exist but were superseded by other approaches. Get user sign-off before deleting anything. If approved, delete in a single commit before any Epic 11 work begins.

The expected outcome is most likely **B**. Plan for it.

## 6. Phase 0 — Investigation (mandatory; do before any code)

Map the existing codebase. Output a report in chat. Wait for sign-off before proceeding.

1. **Orchestrator.** Read `app/pipeline/orchestrator.py` in full. Document `process_field_row()` signature and behaviour. Document `process_document_file()` current state.
2. **Router.** Read `app/pipeline/normalisation/router.py`. List every field_type accepted. Confirm `route_field()` return shape. Confirm Fix 1 has landed (no `current_app` in router).
3. **Paste classifier.** Read `app/pipeline/normalisation/field_type_detector.py` and `classifier_prompt.py`. Note that the **document extraction prompt is separate** — it's not a classifier, it's a schema filler. Different prompt, different output shape.
4. **NMT.** Read `app/pipeline/normalisation/nmt_translator.py`. Confirm `apply_nmt` works end-to-end (commit be8af30, `load_dotenv()` in diagnostic scripts, `.upper()` cast in place).
5. **Existing document scaffolding.** Search the repo for `document`, `pdf`, `ocr`, `document_intelligence`, `form_recognizer`. Report any partial work.
6. **DI SDK availability.** Confirm `azure-ai-documentintelligence` (current GA SDK) installs cleanly in the venv. Do NOT use `azure-ai-formrecognizer` (legacy). Flag any Python version conflicts.
7. **Configuration surface.** Check `.env`, `config/`, `app/config.py` for existing DI slots. Propose env vars: `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT`, `AZURE_DOCUMENT_INTELLIGENCE_KEY`. Confirm `load_dotenv()` is at the top of any script touching DI credentials.
8. **Test fixtures.** Look in `tests/fixtures/` for document samples. If `jal_2025_h1.pdf` is not committed, flag it.

---

## 7. Phase 1 — Design

After Phase 0 sign-off, produce:

### 7.1 Module layout

```
app/pipeline/document_extraction/
    __init__.py
    extractor.py              # Wraps DI SDK; returns LayoutResult or PrebuiltIdResult
    schema_loader.py          # Loads the right Pydantic schema per dropdown choice
    gpt_extractor.py          # Sends (schema + DI layout) to GPT-4o-mini; returns records + blobs
    aggregator.py             # Loops records through route_field; loops blobs through NMT; assembles final JSON
    schemas.py                # Pydantic models for records, blobs, and the aggregated output
config/extraction_schemas/
    government_id_v1.json
    commercial_registry_extract_v1.json
    business_registration_v1.json
    articles_of_association_v1.json
    financial_due_diligence_v1.json
    ownership_attachment_v1.json
    generic_v1.json
```

`process_document_file()` becomes the glue: `extractor.extract(file, dropdown_choice) → gpt_extractor.extract(layout, schema) → aggregator.aggregate(records, blobs)`. Three calls, no logic in the orchestrator beyond wiring.

app/pipeline/document_extraction/   <-- CHECK: may already partially exist as field_extraction.py + field_extraction_rules/
    ...

# Phase 0 sign-off required before fixing module layout.
# Most likely the right module layout reuses:
#   - app/pipeline/ingestion.py (file in, doc record out)
#   - app/tasks/ocr_task.py (DI call)
#   - app/pipeline/field_extraction.py + field_extraction_rules/ (per-type extraction)
# New module needed: a GPT-4o-mini schema-filling layer that sits between the rule files
# and the router. Possibly called app/pipeline/field_extraction_llm.py.
# Aggregator (loop records through route_field) is genuinely new.

### 7.2 Pydantic schema files

For each of the seven dropdown options, produce a draft schema listing:
- The DI model to call (per §3)
- Which canonical fields from §4 apply
- Which are required vs optional (most are optional — extract when present)
- A worked example: a real or hypothetical document → DI layout → schema fill → final record list

**Stop after the seven schemas are drafted. Do not implement the extractor until the schemas are reviewed and approved.** Schemas are cheap to iterate; extraction code built against the wrong schemas is expensive to redo.

### 7.3 Aggregator behaviour

For each record returned by GPT-4o-mini:
- Call `route_field(row, vocab_service=vocab_service)` with `field_type=record.field_name`, `original_text=record.value`, `language=record.language`
- If `record.extracted_as_freeform=true`, force `review_required=True` on the final output regardless of router output
- Otherwise, OR the router's `review_required` with `(record.confidence < 0.75)` — low-confidence extraction always needs a human

For each blob:
- Call `route_field` with `field_type="free_text"`, `language=blob.language`
- This hits Strategy H (NMT) via the existing path

### 7.4 Confidence aggregation

The analyst UI shows one combined confidence per row. Formula: `min(gpt_extraction_confidence, router_confidence, di_confidence_if_prebuilt)`. Lowest signal wins.

---

## 8. Phase 2 — Implementation order

One step at a time. Each step ends with its tests green before moving on. Commit per step. Do not bundle.

1. **Schemas** (`schemas.py` Pydantic models + the seven JSON schema files) + unit tests on round-trip and required-field validation
2. **`schema_loader.py`** + unit tests
3. **`extractor.py`** — DI SDK wrapper. Mock the SDK for unit tests; integration tests hit real Azure
4. **`gpt_extractor.py`** — the prompt template + schema-driven call + response parsing. Unit tests with mocked OpenAI; integration tests with real
5. **`aggregator.py`** — loops records through `route_field`, loops blobs through `route_field` with `field_type=free_text`. Unit tests with fixed inputs and asserted call patterns
6. **`process_document_file()`** — orchestrator glue. Two-line implementation
7. **Diagnostic** (§10)

---

## 9. Analyst review output

Three components, in this order in the UI: extraction summary header, extracted-fields table, translated-prose panel.

### 9.1 Extracted-fields table

Sortable, filterable. One row per record from §5's output contract (not per blob — blobs go in §9.2).

| Column | Source | Notes |
|---|---|---|
| **Field** | `field_name` (canonical or freeform) | Canonical and freeform displayed differently — freeform tagged visually |
| **Original** | `value` from GPT extraction | Original script preserved (right-to-left for ar/he) |
| **Normalised** | `route_field` → `normalised_form` | Monospace. The screening value. |
| **Method** | `route_field` → `processing_method` | Coloured tag: `PRESERVE`, `CALENDAR`, `NUMERIC`, `VOCABULARY`, `GEOGRAPHIC`, `TRANSLITERATE`, `CHARACTER_MAP`, `NMT`, `UNRESOLVED` |
| **Language** | record `language` | ISO 639-1 |
| **Variants** | `route_field` → `allowed_variants` | Comma-separated, "... +N more" if long. Critical for ko/ru/ar names. |
| **Review?** | `route_field.review_required` OR `extracted_as_freeform=true` OR `gpt_confidence < 0.75` | Sortable boolean |
| **Confidence** | `min(gpt_confidence, router_confidence, di_confidence)` | One number 0.00–1.00 |
| **Source** | record `source` | Page + clickable bbox link to PDF viewer |

Default sort: Review? descending, then Confidence ascending. Uncertain rows surface first.

Do not add columns for: raw classifier confidence vs router confidence broken out, latency, strategy module names, internal IDs. Those are diagnostic data, not analyst data.

### 9.2 Translated-prose panel

One collapsible section per blob. Collapsed by default — the analyst expands what they want.

```
▾ {section_heading or fallback} (page {N})
   ┌─ Original ({language}) ─────────┬─ English ──────────────┐
   │ [extracted prose, preserved]    │ [NMT output, uppercase] │
   └─────────────────────────────────┴─────────────────────────┘
```

Section heading comes from the nearest DI heading element above the blob; fallback to "Untitled section (page N)". Do not put blobs in the field table — a 200-word business description in a table cell ruins the layout.

### 9.3 Extraction summary

Compact header above the table:

```
Document: {filename}                       Uploaded: {timestamp}
Document type: {dropdown_choice or "Not specified"}
Fields extracted: {N}                      Review required: {M}
NMT blobs: {K}                             Avg confidence: {0.XX}
Canonical fields: {X}/{N}                  Freeform fields: {Y}
```

The last line matters for AIG — it shows what fraction of extracted content landed in the closed taxonomy vs needed an escape-hatch label.

### 9.4 Aggregator JSON output

The aggregator returns one object. UI renders all three components from it.

```json
{
  "document_id": "jal_2025_h1",
  "filename": "jal_2025_h1.pdf",
  "uploaded_at": "2026-05-15T10:05:04Z",
  "dropdown_choice": "financial_due_diligence",
  "summary": {
    "fields_extracted": 27,
    "review_required": 8,
    "nmt_blobs": 4,
    "avg_confidence": 0.87,
    "canonical_fields": 23,
    "freeform_fields": 4
  },
  "fields": [
    {
      "field_name": "entity_name",
      "original": "日本航空株式会社",
      "normalised": "JAPAN AIRLINES KK",
      "method": "VOCABULARY",
      "language": "ja",
      "variants": [],
      "review_required": false,
      "extracted_as_freeform": false,
      "confidence": 0.95,
      "source": {"page": 1, "bbox": [120, 340, 280, 360]}
    },
    {
      "field_name": "director_name",
      "original": "鳥取 三津子",
      "normalised": "TORI MITSUKO",
      "method": "TRANSLITERATE",
      "language": "ja",
      "variants": ["TOTTORI MITSUKO"],
      "review_required": true,
      "extracted_as_freeform": false,
      "confidence": 0.70,
      "source": {"page": 1, "bbox": [120, 480, 240, 500]}
    }
  ],
  "blobs": [
    {
      "section_heading": "事業の内容",
      "language": "ja",
      "original": "...",
      "translation": "...",
      "method": "NMT",
      "confidence": 0.80,
      "source": {"page": 2}
    }
  ]
}
```

`fields` array follows reading order in the document (top-to-bottom, left-to-right per DI's reading_order). Not alphabetical, not by field_type. The analyst is reading the document; the table matches.

---

## 10. Phase 3 — Tests

### 10.1 Unit tests (`tests/unit/document_extraction/`)

- `test_schemas.py` — Pydantic round-trip; required-field validation
- `test_schema_loader.py` — each dropdown choice loads the right schema; unknown choice → `generic_v1`
- `test_extractor.py` — mocked DI SDK: happy path, partial extraction, low confidence, DI error, network timeout, malformed response
- `test_gpt_extractor.py` — mocked OpenAI: closed-enum compliance (records emit only canonical names unless `extracted_as_freeform=true`), no-reformatting check (values come back exactly as in the layout input), null handling
- `test_aggregator.py` — fixed extraction inputs, assert the call pattern into `route_field` and `apply_nmt`; assert review flags propagate correctly (freeform → True, low-confidence → True, both → True)

No live Azure or OpenAI calls in unit tests.

### 10.2 Integration tests (`tests/integration/document_extraction/`)

- `test_jal_h1_extraction.py` — end-to-end on `jal_2025_h1.pdf` with `dropdown_choice="financial_due_diligence"`. Real DI, real GPT-4o-mini, real router, real NMT. Assertions:
  - Entity name normalised correctly via router
  - Director name transliterated with `review_required=True` (consistent with F-series)
  - Document date normalised to `2025-10-31`
  - At least one prose blob round-trips through NMT and returns non-empty English
  - Aggregated JSON validates against the Pydantic output model

Mark `@pytest.mark.integration`. Skip in normal CI. Run before AIG demos and before merging to main.

### 10.3 Regression guard

Run the existing 164-test diagnostic against the paste-tab path after Epic 11 lands. Assert count ≥ 138. If document-extraction work accidentally touched the router, this catches it.

---

## 11. Phase 4 — Diagnostic

Create `run_document_extraction_diagnostic.py` at repo root. Mirror the structure of `run_integration_diagnostic.py`.

1. **First line of the script:** `from dotenv import load_dotenv; load_dotenv()`. This is the bug that cost us H-series last week. Do not regress.
2. Load `tests/fixtures/documents/jal_2025_h1.pdf` (and any other fixtures we accumulate later)
3. Hold a golden expected output per fixture: list of `{record_location_or_id, expected_field_name, expected_normalised_form, expected_method, expected_freeform_flag}` rows
4. Run full pipeline: `process_document_file()` with each dropdown choice. Match returned records to golden rows by source location (bbox proximity) or by `field_name` if unambiguous
5. Emit `reports/document-extraction-report-latest.md` in the same shape as `reports/integration-report-latest.md`:
   - Summary table (Pass / Fail / Total / Freeform-but-acceptable)
   - Per-row breakdown showing: DI extraction step, GPT extraction step, router dispatch step, expected vs actual
   - Failure diagnosis text per row

Initial golden set for JAL: ~30 rows covering canonical fields from categories 2, 3, 5, 7 (entity, director, capital, financial) plus at least 3 blobs. Naming convention: `JAL.entity_name`, `JAL.director_1_name`, `JAL.blob_business_description`.

Add a **variance check**: run the diagnostic 3 times consecutively. Report the field-assignment delta between runs. If >5% of canonical-field rows flip between runs, prompt issue — escalate.

---

## 12. AIG framing

The story when this lands:

> "Document upload re-uses the Phase 1 normalisation pipeline. Every extracted field flows through the same router and strategy modules that pass 138/164 golden tests. Document-specific work is confined to two layers: Document Intelligence for structure, and GPT-4o-mini for closed-schema field labelling. The router does not change. Pipeline behaviour on the paste path is unchanged."

If at any point implementing Epic 11 requires modifying the router or any Strategy A–H module: **stop and flag it**. That's scope creep. Either the schema needs adjusting or there's a genuine Phase 1 gap that opens as its own ticket.

---

## 13. Open questions — surface in Phase 0 report

1. **PII logging.** Does the extracted output get logged? If yes, redact `full_name`, `father_name`, `mother_name`, `address`, `id_number`, all `shareholder_*` and `director_*` before logging. Confirm logging policy.
2. **Blob chunking.** Azure Translator has a per-request size limit. What is the max blob length we send before chunking? Propose a chunking strategy or accept truncation with a flag.
3. **Re-classification on extraction confidence.** When GPT-4o-mini returns a canonical field name with confidence < 0.6, do we trust the field name and pass it to the router as-is, or do we treat it as freeform? Default proposal: trust the name, but force `review_required=True`. Confirm.
4. **Shareholder table scope.** JAL has 10 shareholders with addresses and percentages. Do we extract all 10 as separate records, or only the entity-under-review? Default proposal: all 10 (the canonical taxonomy supports it). Confirm — this affects how the diagnostic golden set is sized.
5. **Multi-page documents and reading order.** DI returns reading_order across pages. Confirm the aggregator preserves this in the final `fields` array (so the analyst table reads top-to-bottom as the document does).
6. **Variance escalation path.** If the §11 variance check exceeds 5%, what's the rollback? Propose: ship at lower variance threshold by tightening the prompt, OR fall back to deterministic classifier for canonical fields. The former is preferred.

---

## 14. Definition of done

- [ ] Phase 0 investigation report posted and signed off
- [ ] Seven Pydantic schemas drafted, reviewed, committed under `config/extraction_schemas/`
- [ ] Module layout (§7.1) committed with all unit tests green
- [ ] Integration test on JAL fixture green
- [ ] `run_document_extraction_diagnostic.py` produces ≥ 80% pass on the JAL golden set
- [ ] Variance check shows ≤ 5% canonical-field flips across 3 consecutive runs
- [ ] `run_integration_diagnostic.py` still passes 138/164 (no Phase 1 regression)
- [ ] §12 AIG framing still true — no router or Strategy A–H module modified

---

## 15. What this epic does NOT do

- Add new field_types to the router (separate tickets, one per field)
- Add new strategies to the router (separate tickets)
- Train custom DI models
- Support document types outside the seven dropdown options
- Translate the analyst UI rendering work itself — that's a separate frontend ticket; §9 specifies the contract the frontend builds against
- Replace the paste-tab classifier
- Handle multi-document uploads (one file per request for now)
- Persist extraction results beyond the request (no DB write in Epic 11)