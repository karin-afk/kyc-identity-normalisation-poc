# KYC Identity Normalisation — Target State

## Purpose of this document

This document describes where we are going and why. It gives context for the individual epic files that follow. Each epic file contains the detailed specification for that piece of work.

## target languages
Before building the file, let me confirm the target languages based on everything we have discussed.

---

## Languages confirmed for the full pipeline

**Non-Latin scripts — transliteration required:**

| Code | Language | Jurisdictions |
|---|---|---|
| `ar` | Arabic | UAE, Saudi Arabia, Egypt, Kuwait, Qatar, Bahrain, Jordan, Iraq, Libya, Morocco, Tunisia, Algeria, Oman, Yemen |
| `ja` | Japanese | Japan |
| `zh` | Chinese (Mandarin) | China, Taiwan (Minguo calendar), Singapore |
| `ko` | Korean | South Korea |
| `ru` | Russian | Russia |
| `uk` | Ukrainian | Ukraine |
| `bg` | Bulgarian | Bulgaria |
| `be` | Belarusian | Belarus |
| `el` | Greek | Greece, Cyprus |
| `he` | Hebrew | Israel |
| `fa` | Persian / Farsi | Iran |
| `th` | Thai | Thailand |

**Latin-script — character mapping only:**

| Code | Language | Jurisdictions |
|---|---|---|
| `de` | German | Germany, Austria, Switzerland |
| `fr` | French | France, Belgium, Switzerland, Luxembourg |
| `it` | Italian | Italy |
| `es` | Spanish | Spain, Latin America |
| `pt` | Portuguese | Portugal, Brazil |
| `nl` | Dutch | Netherlands, Belgium |
| `pl` | Polish | Poland |
| `sv` | Swedish | Sweden |
| `no` | Norwegian | Norway |
| `da` | Danish | Denmark |
| `tr` | Turkish | Turkey |
| `en` | English | UK, Ireland, India, Singapore, US |

---

## What we are building

A Flask web application that allows KYC analysts to upload identity and corporate documents in any script and language and receive structured, normalised, English-language field extractions suitable for sanctions screening — with no AI involved at any point.

The tool is called **KYC Identity Normalisation**. The name is deliberate: the tool does not translate documents. It normalises identity fields — dates, names, legal forms, addresses, company names — into a single consistent format that downstream screening systems can reliably work with, regardless of what language or script the source document was written in.

---

## Why no AI in Phase 1

The EU AI Act classifies automated processing of personal data in KYC/AML contexts as high-risk. Using a generative LLM (GPT-4o or equivalent) would require a conformity assessment and AI Governance Board approval before deployment, which would delay the tool significantly.

Phase 1 is therefore designed to contain **no AI components**. All processing is either deterministic (rule-based, library-based, or lookup-based) or routed to a human native speaker for review. This means the tool can be deployed immediately without governance approval.

Phase 2 — which adds LLM for a narrow set of residual cases (primarily Arabic vowel insertion and novel company name resolution) — is subject to a separate governance submission and is documented separately.

---

## The normalisation pipeline

Every extracted field passes through the following strategies in order. The pipeline stops at the first strategy that produces a confident result.

| Strategy | Name | What it does |
|---|---|---|
| A | Preserve | Returns structured identifiers (document numbers, registration numbers) exactly as found. Never altered. |
| B | Calendar and numeric rules | Converts dates across calendar systems (Japanese era-year, Hijri, Solar Hijri, Hebrew, Thai Buddhist, Minguo) and normalises numeric formats (Eastern Arabic-Indic digits, full-width digits, number separators, currency symbols, parenthetical negatives). |
| C | Vocabulary lookup | Matches against pre-built dictionaries of finite sets: legal forms (GmbH, 株式会社, ООО…), company status terms, role titles, share class types, industry codes, issuing authority names, document type labels. |
| D | Geographic lookup | Resolves country names, nationality demonyms, and place names against ISO databases and GeoNames. Covers country level fully and town/village level via the full GeoNames dataset. |
| E | Verified repository | Checks the growing library of human-confirmed translations. Whole-value match first, then token-level match. Returns instantly with no further processing. Grows with every native speaker review. |
| F | Transliteration libraries | Converts non-Latin scripts to Latin using established international standards: BGN/PCGN for Cyrillic and Arabic consonant skeleton, Hepburn for Japanese kana, Pinyin for Chinese, Revised Romanisation for Korean, ISO 843 for Greek, ISO 259 for Hebrew, Royal Thai General System for Thai. Generates allowed_variants list for all outputs. |
| G | Character mapping tables | Substitutes special characters in Latin-script languages using fixed lookup tables: German umlauts (Ä→AE), French accents (é→E), Spanish ñ (→N and NY variant), Italian grave accents, Turkish special characters, Dutch digraphs, Scandinavian characters, Polish characters, Portuguese characters. |
| H | Azure Translator NMT | Translates prose fields into readable English using Microsoft's Neural Machine Translation service (not a generative AI). Applied only to free-text descriptive fields: nature of business, accounting policies, narrative text blobs. Never applied to names, identifiers, or any field requiring KYC-formatted output. Private endpoint enforces NMT-only mode. |
| I | Native speaker review | When no strategy above resolves a field with confidence, it is flagged and routed to a registered native speaker for that language. The native speaker sees the original document image, confirms or corrects the output, and submits. The confirmed result is saved to the verified repository (Strategy E) permanently. The original analyst is notified by email when review is complete. |

---

## Two user-facing modes

### Document upload
An analyst uploads a PDF or image file. The system sends it to Azure Document Intelligence for OCR and structure extraction, segments the document by type if it contains multiple document types, extracts all KYC fields using regex templates and Document Intelligence's prebuilt models, passes each field through the normalisation pipeline, and presents results on screen showing original-language text alongside the English normalised form. The analyst can download results as a Word document or CSV, or email results to themselves.

### Text paste
An analyst pastes raw text (copied from an email, system, or document). The analyst selects the field type from a dropdown. The system detects the language automatically using the `lingua` library and routes the text through the same normalisation pipeline. Results are shown inline. Unresolved fields can be escalated to native speaker review via the same workflow as the document upload mode. Limited to 2,000 characters — longer content should be uploaded as a file.

---

## Document types supported

1. Government-issued ID — national ID
2. Government-issued ID — driver's licence
3. Company registry extract — local
4. Company registry extract — foreign
5. Business registration certificate
6. Articles of Association (limited scope: entity name and registered address only)
7. Financial and due-diligence supporting documents
8. Shareholder / ownership determination attachment

A single upload may contain multiple document types. Azure Document Intelligence's custom classifier identifies page ranges per type and routes each section to the correct extraction logic.

---

## Fields extracted and normalised

**Individual (government-issued IDs):** full name, date of birth, nationality, ID/document number (preserved), address, issuing authority, issue date, expiry date, place of birth, parent names, locality/registry information.

**Company — core:** entity name, registration number (preserved), date of incorporation, registered address, mailing address, legal form, nature of business/purpose, status, document/registry date.

**Company — management:** director/officer name, role/designation, date of birth, country of residence.

**Company — ownership:** shareholder name, shareholder address, number of shares, voting rights, ownership percentage, relationship/classification.

**Company — capital:** share capital, number of issued shares, capital changes.

**AoA (limited):** entity name, registered/office address (only if explicitly stated).

**Financial:** total assets, total liabilities, net assets, revenue/income, expenses, financial period, accounting policies.

---

## Human review workflow

Fields that cannot be resolved by strategies A–H are flagged and routed to native speakers:

1. A `ReviewTask` record is created and assigned round-robin to registered native speakers for that language.
2. An email is sent to the assigned native speaker via Azure Communication Services.
3. The native speaker logs in, sees the original document image alongside the flagged field, and confirms or corrects the output.
4. The confirmed translation is written to the verified repository and a JSON backup is created.
5. The original analyst receives an email notification with a link to the completed results.

Native speakers are registered by system administrators and assigned to one or more languages. A user can be both an analyst and a native speaker.

---

## Audit and compliance

Every action taken in the system is recorded in an append-only audit log with a chain hash for tamper evidence: document uploads, field extractions, strategy decisions, review task lifecycle events, repository writes, exports, and email actions. This log is queryable by admins and exportable for regulatory review. It is the primary evidence for the AI Governance Board that no LLM was used in Phase 1.

---

## Tech stack

### Azure infrastructure

**Available now (already deployed, called remotely from localhost)**
- **Azure Document Intelligence** — OCR and structure extraction. `prebuilt-idDocument` for identity documents, `prebuilt-layout` for all other document types, custom classifier for page segmentation.
- **Azure AI Translator** — NMT for prose fields only. Private endpoint enforces NMT-only (no LLM mode).

**Later — when moving to the bank**
- **Azure App Service** — Flask application host. Linux plan, private VNet, private endpoints. Replaces localhost.
- **Azure Database for PostgreSQL Flexible Server** — primary database for all runtime state. Replaces local PostgreSQL.
- **Azure Blob Storage** — uploaded document files. UUID-named blobs, private endpoint. Replaces local `uploads/` folder.
- **Azure Cache for Redis** — Celery task broker for async processing. Replaces local Redis.
- **Azure Communication Services** — email to native speakers and analysts.
- **Azure Entra ID** — SSO and MFA. Wired in as part of bank deployment (Epic 12).

**Running locally for now (Docker)**
- PostgreSQL — `docker run -e POSTGRES_PASSWORD=pass -p 5432:5432 postgres`
- Redis — `docker run -p 6379:6379 redis`
- Flask — `flask run` on localhost

### Application
- **Flask 3.x** — web framework, application factory pattern, blueprints per feature area.
- **SQLAlchemy** — ORM. PostgreSQL via psycopg2-binary.
- **Alembic** — database migrations.
- **Celery** — async task queue for document processing, email, and backups.
- **HTMX** — dynamic UI updates without a JS framework.
- **Jinja2** — server-side HTML templates.

### Document processing
- `azure-ai-documentintelligence` — Document Intelligence SDK.
- `azure-ai-translation-text` — Azure Translator SDK.
- `azure-communication-email` — Azure Communication Services SDK. Not wired until bank deployment.
- `azure-storage-blob` — Blob Storage SDK. Not wired until bank deployment; local `uploads/` folder used in the meantime.
- `lingua-language-detector` — language detection on extracted text.
- `pymupdf` (fitz) — PDF text extraction before Document Intelligence call.
- `python-docx` — Word document generation for results download.
- `Pillow` — image preprocessing.

### Normalisation libraries (existing pipeline, carried forward)
- `transliterate` — Cyrillic, Greek, Hebrew, Persian, Thai (BGN/PCGN, ISO standards).
- `pykakasi` — Japanese kana to Latin (Hepburn).
- `pypinyin` — Chinese Pinyin with given-name fusion.
- `korean-romanizer` — Korean Revised Romanisation with surname variant table.
- `unidecode` — last-resort Latin fallback for unrecognised scripts.
- `convertdate` — calendar conversions: Hijri, Hebrew, Solar Hijri/Persian, Thai Buddhist, Minguo.
- `hijri-converter` — Hijri conversion (already in codebase).

### Reference data libraries
- `pycountry` — ISO 3166 countries, ISO 639 languages, ISO 4217 currencies.
- `babel` — country and territory names in any locale/script, used to build non-Latin country name index.
- `geonamescache` — ~25,000 cities bundled locally.
- `countryinfo` — nationality demonyms.
- Full GeoNames dataset — downloaded at build time for village-level place of birth lookups.

### Testing and CI
- `pytest` — test framework. Golden dataset and regression gate carried forward from existing repo.
- GitHub Actions — CI pipeline. Regression gate runs on every commit.

---

## Epics summary

The work is organised into twelve epics, in delivery order.

**Epic 1 — Normalisation artefacts and rules (A–G)**
All static reference data: character mapping tables for all Latin-script languages, vocabulary lookup tables (legal forms, status, roles, industry codes, issuing authorities), calendar conversion rules for all calendar systems, numeric script normalisation, geographic reference data including full GeoNames dataset, and seed data for the verified repository. All stored as versioned files in the repository. No infrastructure needed — fully testable in isolation.

**Epic 2 — Database schema and initialisation**
All PostgreSQL tables defined as SQLAlchemy models and Alembic migration generated: users and native speaker language assignments, documents and processing jobs, processing results with per-field strategy audit trail, verified translations and token entries, review tasks, paste sessions, and the audit log with chain hash.

**Epic 3 — Prepopulate tables**
Seed data loaded into the live database: common person name tokens across Arabic, Japanese, Russian, Chinese, Korean, and Greek; vocabulary lookup tables; and the non-Latin country name index built from `babel`.

**Epic 4 — Normalisation router and orchestrator**
The central normalisation router wired with all artefacts from Epic 1, routing each field through strategies A–I in order. The orchestrator coordinates the full pipeline end to end: receives a document job, calls Document Intelligence, segments pages, extracts fields, passes each through the router, writes results to the database, creates review tasks for unresolved fields, and writes an audit log entry for every step. Testable via CLI and pytest against the golden dataset — no UI yet.

**Epic 5 — Azure Document Intelligence integration**
Document upload to Blob Storage, routing to `prebuilt-idDocument` or `prebuilt-layout`, custom classifier for page segmentation of multi-document uploads, regex field extraction templates for all eight document types, and `lingua` language detection on extracted text. Plugged into the orchestrator from Epic 4.

**Epic 6 — Azure Translator NMT integration**
Azure Translator NMT connected for prose field types only (nature of business, accounting policies, address rendering, narrative text blobs). Field type gate ensures NMT is never called for names or identifiers. Plugged into the normalisation router as strategy H.

**Epic 7 — Human review loop and email**
Review task creation for unresolved fields, round-robin assignment to native speakers, Azure Communication Services email notifications, native speaker review dashboard (original document image + flagged field + confirm/correct interface), confirmed result written to verified repository, analyst notification email on completion, and admin interface for user management and task oversight.

**Epic 8 — Document upload UI and results**
Upload form, async processing with HTMX status polling, results screen (original + English side by side with per-field provenance), Word and CSV download, email-to-self, and document history page.

**Epic 9 — Text paste tab** - done
Paste interface with field type dropdown and language hint, same normalisation router as the document pipeline, inline results, escalate-to-review button, 2,000-character limit, paste session recorded for audit.

**Epic 10 — Audit logging**
`log_action()` wired into every route, pipeline step, and background task. Chain hash for tamper evidence. Admin query, filter, and export UI. Per-document audit trail visible to the uploading analyst. CLI integrity check command.

**Epic 11 — Testing, regression gate, and CI**
Golden dataset expanded to cover all new field types, languages, and strategies. Integration tests for Document Intelligence and Azure Translator using recorded fixtures. Regression gate wired into GitHub Actions. Processing method statistics dashboard in admin showing zero LLM calls — the live evidence for the AI Governance Board.

**Epic 12 — Flask foundation and authentication scaffold**
Proper Flask application structure formalised, all blueprints and configurations cleaned up, and Azure Entra ID SSO wired in. Done last so the application shape is fully known before the auth layer is built around it.
