# EU AI Act — Technical Requirements for Translation Tool

This document lists plain-English technical requirements for your translation tool, mapped to specific EU AI Act articles. For each, it states whether the requirement is currently implemented in the codebase, based on current inspection.

---

## Article 9 — Risk Management
**Requirement:**
- Maintain a risk register documenting known failure modes (e.g., OCR errors, weak language pairs, degraded documents), with a named owner and review cadence. Must be updated as failures occur or the system changes.

**Status:**
- **Not implemented.** No risk register or owner/review process found in code or docs.

---

## Article 10 — Data Governance
**Requirement:**
- Obtain accuracy metrics from the translation vendor, broken down by language pair and document type. If unavailable, commission independent evaluation using real analyst queue samples before go-live.

**Status:**
- **Partially implemented.** Evaluation scripts and datasets exist (e.g., `evaluate_copilot_output.py`, `test_dataset.csv`, `golden_dataset.csv`), but no evidence of vendor-supplied metrics or formal independent evaluation process.

---

## Article 11 — Technical Documentation
**Requirement:**
- Annex IV-compliant technical documentation must be supplied by the vendor or produced internally, covering system function, limitations, testing, and update process.

**Status:**
- **Partially implemented.** Documentation exists in `documentation/` (e.g., `01-linguistic-approach.md`, `02-ai-governance.md`, `03-evaluation-framework.md`), but not explicitly Annex IV-compliant or contractually required.

---

## Article 12 — Logging
**Requirement:**
- Every translation event must log: document reference, source language, analyst ID, timestamp, confidence score, and output reference/hash. Logs must be retained for 5+ years and be queryable for audit.

**Status:**
- **Not implemented.** No evidence of structured logging or log retention policy in codebase.

---

## Article 13 — Transparency
**Requirement:**
- Provide a one-page operational brief for analysts, stating reliable languages, known underperformance, and that output is AI-generated/unverified. Analysts must sign acknowledgement before use; document must be attached to each translation in CRM.

**Status:**
- **Not implemented.** No such brief or analyst acknowledgement workflow found.

---

## Article 14 — Human Oversight
**Requirement:**
- Escalate translations with low confidence or flagged languages to a certified human translator before KYC progression. CRM must enforce this rule.

**Status:**
- **Partially implemented.** The pipeline outputs a `confidence` score and `review_required` flag, and escalates ambiguous cases to LLM or analyst, but no CRM enforcement or certified human translation workflow is present.

---

## Article 15 — Accuracy
**Requirement:**
- Set minimum accuracy thresholds per language pair, approved by risk committee. System must surface a confidence score on every output. Vendor must provide per-output confidence scoring.

**Status:**
- **Partially implemented.** Confidence scores are output for each translation, but no evidence of risk committee-approved thresholds or vendor-supplied scoring.

---

## Article 16 / 26 — Provider and Deployer Obligations
**Requirement:**
- Contractual addendum assigning responsibility for documentation and incident reporting. Assign internal system owner for monitoring, incident logging, and annual review. Document in AI system register.

**Status:**
- **Not implemented.** No evidence of contractual addendum, system owner assignment, or AI system register.

---

## Article 49 — Registration
**Requirement:**
- Register deployment in the EU AI Act database before go-live. Assign ownership of the registration record. Update registration on material changes.

**Status:**
- **Not implemented.** No evidence of registration or ownership assignment.

---

## GDPR Article 22 — Automated Decision-Making
**Requirement:**
- Obtain legal opinion on whether AI-translated KYC documents constitute automated processing with material effect. If yes, update privacy notices and inform customers before processing.

**Status:**
- **Not implemented.** No legal opinion or privacy notice update process found.

---

# Output and Confidence in the Tool
- The tool outputs a `confidence` score and a `review_required` flag for each translation event.
- Escalation to LLM or analyst is based on ambiguity or low confidence, but there is no explicit CRM enforcement or human translation workflow implemented.
- Confidence scores are surfaced in the output, but not currently used for formal escalation or audit logging.

---

*This document should be updated as implementation progresses.*
