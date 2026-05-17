Here's the prompt:

---

I need to generate a performance report for the AIG board meeting on Tuesday. This report covers functional accuracy, test suite health, and operational performance across the full pipeline.

Work through the tasks below in order. One task per turn. Stop after each and wait for sign-off.

---

**Task 0 — Branch and prepare.**

```
git checkout dev
git checkout -b report/aig-performance-analytics
```

Read the following files to understand the data sources available:
- `run_integration_diagnostic.py` — understand the output format and what data each test row contains
- `data/golden_dataset.csv` — understand the columns and row count
- `data/test_dataset.csv` — understand the columns and row count
- `reports/integration-report-latest.md` — understand the most recent diagnostic output
- `tests/` — scan all test files and count: how many unit tests, how many integration tests, what do they cover

Report back: how many rows in each dataset, what columns are available, how many tests exist in pytest and what categories they fall into. Stop. Wait for sign-off.

---

**Task 1 — Propose the analytics plan.**

Before writing any code, propose the full set of analytics. Organise into four sections:

### Section A — Test suite health

This covers pytest unit and integration tests. For every test file in `tests/`:
- List the test file, what module/strategy it tests, how many test functions it contains, and whether it's unit or integration
- Run `pytest tests/ --tb=no -q` and capture the pass/fail/error/skip counts
- Group results by: strategy module tested, test type (unit vs integration), pass/fail

The board needs to see: "X unit tests covering Y strategies, Z% passing. N integration tests covering the end-to-end flow, M% passing." Plus a breakdown of what the failures are (pre-existing vs new).

### Section B — Integration diagnostic (164-test suite)

Run `run_integration_diagnostic.py` once with `CLASSIFIER_MODE=llm`. Parse the output. Produce analytics sliced by:
- **Language** — pass rate per ISO 639-1 code (ar, ja, zh, ko, ru, uk, el, de, fr, es, it, pt, pl, no, tr, he, fa, th, en)
- **Field type** — pass rate per field_type (person_name, company_name, date_of_birth, address, phone_number, nationality, city, legal_form, status, role, share_capital, total_assets, id_number, alias, free_text, etc.)
- **Strategy/method** — pass rate per processing_method (PRESERVE, CALENDAR, NUMERIC, VOCABULARY, GEOGRAPHIC, TRANSLITERATE, CHARACTER_MAP, NMT, UNRESOLVED)
- **Failure categorisation** — group every failing test into one of: Phase 2 scope (Tier 7 composition, Strategy E confusable detection, invoice structured extraction), classifier prompt edge case, LLM non-determinism, genuine bug
- **Confidence distribution** — histogram of confidence scores for passing vs failing tests
- **Classification accuracy** — how often the classifier's field_type and language matched the expected values (separate from pipeline accuracy)
- **Review-required rate** — percentage of outputs flagged review_required=True, sliced by language and field_type
- **Latency** — per-strategy latency (classification latency + router latency), grouped by strategy. Show that deterministic strategies (A–G) are near-zero and LLM/NMT strategies add 1–2 seconds.

### Section C — Full dataset runs (golden + test datasets)

Run the pipeline against:
- `data/golden_dataset.csv` (all rows)
- `data/test_dataset.csv` (all rows)

For each dataset, produce the same slices as Section B (language, field_type, strategy, confidence, latency). Additionally:
- **Coverage matrix** — language × field_type heatmap showing how many test cases exist per cell and what the pass rate is per cell
- **Variant generation stats** — for transliterated names (Korean, Japanese, Chinese, Arabic, Russian, Greek), report the average number of variants generated per name

### Section D — Operational metrics

- **Estimated cost per field** — based on actual API calls observed during the diagnostic run. Classify by: free (deterministic strategies A–G), classifier cost (GPT-4o-mini per call), NMT cost (Azure Translator per call). Produce an estimated cost per document assuming an average of 15–25 fields per document.
- **Throughput estimate** — fields per minute based on observed latencies
- **LLM non-determinism measurement** — run the 164-test diagnostic 3 times. For each test, record whether the result (pass/fail and normalised_form) was identical across all 3 runs. Report the flip rate as a percentage.

Present the full analytics plan in chat as a table of: metric name, data source, chart type (bar/pie/histogram/heatmap/table), which section of the report it belongs to. Stop. Wait for sign-off. Do not write code yet.

---

**Task 2 — Write `generate_aig_analytics.py`.**

Create `generate_aig_analytics.py` at the repo root. This script:

1. **First line:** `from dotenv import load_dotenv; load_dotenv()` — non-negotiable.

2. **Section A: Test suite health.**
   - Runs `pytest tests/ --tb=line -q --no-header` programmatically (via subprocess) and parses the output
   - For each test file, extracts: filename, module tested, test count, pass count, fail count, error count, skip count
   - Writes `reports/aig/test_suite_health.csv` with columns: `test_file, module_tested, test_type, total_tests, passed, failed, errors, skipped, pass_rate`

3. **Section B: Integration diagnostic.**
   - Runs the 164-test diagnostic (import and call directly — do not shell out). Capture all per-test data.
   - Writes `reports/aig/diagnostic_by_language.csv` — columns: `language, total, passed, failed, pass_rate`
   - Writes `reports/aig/diagnostic_by_field_type.csv` — columns: `field_type, total, passed, failed, pass_rate`
   - Writes `reports/aig/diagnostic_by_method.csv` — columns: `method, total, passed, failed, pass_rate`
   - Writes `reports/aig/diagnostic_failures.csv` — columns: `test_id, description, field_type, language, expected, actual, failure_category` (failure_category is one of: phase_2_scope, classifier_edge_case, llm_nondeterminism, genuine_bug)
   - Writes `reports/aig/diagnostic_confidence.csv` — columns: `test_id, passed, classification_confidence, router_confidence`
   - Writes `reports/aig/diagnostic_classification_accuracy.csv` — columns: `test_id, expected_field_type, got_field_type, field_type_match, expected_language, got_language, language_match`
   - Writes `reports/aig/diagnostic_review_rate.csv` — columns: `language, field_type, total, review_required_count, review_rate`
   - Writes `reports/aig/diagnostic_latency.csv` — columns: `test_id, method, classification_latency_s, router_latency_s, total_latency_s`

4. **Section C: Full dataset runs.**
   - Loads `data/golden_dataset.csv` and `data/test_dataset.csv`
   - Runs each row through `process_field_row()` (inside a Flask app context)
   - Writes `reports/aig/golden_dataset_results.csv` — all input columns plus: `normalised_form, method, confidence, review_required, classification_latency_s, router_latency_s, pass_fail` (compare against expected if available)
   - Writes `reports/aig/test_dataset_results.csv` — same format
   - Writes `reports/aig/coverage_matrix.csv` — columns: `language, field_type, count, passed, pass_rate`
   - Writes `reports/aig/variant_stats.csv` — columns: `test_id, language, field_type, normalised_form, variant_count, variants`

5. **Section D: Operational metrics.**
   - Computes cost estimates from latency and method data (use: GPT-4o-mini ≈ $0.15/1M input tokens, Azure Translator ≈ $10/1M characters; estimate tokens/chars per field from actual inputs)
   - Writes `reports/aig/cost_estimates.csv` — columns: `method, avg_cost_per_field_usd, fields_in_sample, total_cost_usd`
   - Writes `reports/aig/throughput.csv` — columns: `method, avg_latency_s, estimated_fields_per_minute`
   - Runs the 164-test diagnostic 3 times and writes `reports/aig/nondeterminism.csv` — columns: `test_id, run1_result, run2_result, run3_result, run1_normalised, run2_normalised, run3_normalised, stable` (stable=True if all three runs identical)

6. **All CSVs go under `reports/aig/`.** Create the directory if it doesn't exist.

7. **Print a summary to stdout** after all CSVs are written: total CSVs generated, total rows across all datasets, wall-clock time for the full run.

Show me the script in chat. Stop. Wait for sign-off before running it.

---

**Task 3 — Run the analytics script.**

```
python generate_aig_analytics.py
```

Report: which CSVs were produced, row counts per CSV, wall-clock time, any errors. If any section failed, diagnose and fix before proceeding.

Stop. Wait for sign-off.

---

**Task 4 — Write `visualise_aig_analytics.py`.**

Create `visualise_aig_analytics.py` at the repo root. This script reads the CSVs from `reports/aig/` and produces charts in `reports/aig/charts/`.

Use `matplotlib` and `seaborn`. If not installed, `pip install matplotlib seaborn --break-system-packages`. All charts saved as PNG at 300 DPI with white background.

Produce these charts:

**Section A — Test suite health:**
- `test_suite_summary.png` — horizontal stacked bar: pass/fail/error per test file. Green/red/orange.

**Section B — Integration diagnostic:**
- `pass_rate_by_language.png` — horizontal bar chart, sorted by pass rate descending. Include count labels.
- `pass_rate_by_field_type.png` — horizontal bar chart, sorted by pass rate descending.
- `pass_rate_by_method.png` — horizontal bar chart, sorted by pass rate descending.
- `failure_categorisation.png` — pie chart or donut showing Phase 2 scope / classifier edge case / LLM non-determinism / genuine bug.
- `confidence_distribution.png` — two overlaid histograms: passing tests (green) vs failing tests (red).
- `classification_accuracy.png` — grouped bar chart: field_type match rate and language match rate side by side.
- `review_rate_by_language.png` — bar chart showing review-required percentage per language.
- `latency_by_method.png` — box plot or bar chart: latency per strategy, clearly showing deterministic (< 50ms) vs LLM/NMT (1–2s).

**Section C — Full dataset:**
- `coverage_heatmap.png` — language × field_type heatmap, cells coloured by pass rate, annotated with count.
- `variant_generation.png` — bar chart: average variants per name by language.

**Section D — Operational:**
- `cost_per_field.png` — bar chart by method: cost per field in USD.
- `nondeterminism_rate.png` — single number or small bar: percentage of tests that flipped across 3 runs.
- `throughput_by_method.png` — bar chart: fields per minute by method.

**Style:**
- Use a consistent colour palette throughout (not the matplotlib defaults — something clean and professional for a board deck)
- Title every chart clearly. No jargon in titles — "Pass Rate by Language" not "Diagnostic Accuracy per ISO 639-1 Code"
- Include the total count in chart titles where relevant, e.g. "Pass Rate by Language (164 tests)"
- Remove chart clutter: no gridlines behind bars, no box around legend, concise axis labels

Show me the script in chat. Stop. Wait for sign-off before running it.

---

**Task 5 — Run the visualisation script.**

```
python visualise_aig_analytics.py
```

Report: which charts were produced, any rendering issues. Open 3–4 of them to spot-check quality. If any chart looks wrong (empty, mislabelled, truncated), fix before proceeding.

Stop. Wait for sign-off.

---

**Task 6 — Generate the summary markdown.**

Create `reports/aig/AIG_PERFORMANCE_REPORT.md`. This is a one-page narrative with embedded chart references that can be pasted into a slide deck.

Structure:

```markdown
# KYC Identity Normalisation — Performance Report
**Date:** {today}
**Diagnostic baseline:** {pass}/{total} ({percentage}%)
**Datasets evaluated:** 164-test diagnostic, golden dataset ({N} rows), test dataset ({M} rows)

## Test Suite Health
{1-2 sentences summarising unit/integration test coverage and pass rates}
![Test Suite Summary](charts/test_suite_summary.png)

## Functional Accuracy
{2-3 sentences: headline pass rate, strongest languages, strongest field types}
![Pass Rate by Language](charts/pass_rate_by_language.png)
![Pass Rate by Field Type](charts/pass_rate_by_field_type.png)

## Failure Analysis
{2-3 sentences: how the 16% gap decomposes, that it's scope not bugs}
![Failure Categorisation](charts/failure_categorisation.png)

## Classification Performance
{1-2 sentences on classifier accuracy}
![Classification Accuracy](charts/classification_accuracy.png)

## Confidence and Review
{1-2 sentences: most outputs are high confidence, review rate is manageable}
![Confidence Distribution](charts/confidence_distribution.png)

## Operational Performance
{2-3 sentences: latency, cost, determinism}
![Latency by Method](charts/latency_by_method.png)
![Non-determinism](charts/nondeterminism_rate.png)

## Coverage
![Coverage Heatmap](charts/coverage_heatmap.png)

## Summary
{3-sentence conclusion: pipeline is accurate where it covers, the gap is scope not quality, operational cost is minimal}
```

Fill in the narrative sentences from the actual CSV data — do not guess or use placeholder numbers. Every number in the text must come from the CSVs.

Show me the draft in chat. Stop. Wait for sign-off.

---

**Task 7 — Commit.**

Single commit on the `report/aig-performance-analytics` branch. Message:

```
report: AIG performance analytics — scripts + charts + summary

- generate_aig_analytics.py: runs diagnostic, pytest, full dataset evaluation
- visualise_aig_analytics.py: produces board-ready charts from CSV outputs
- reports/aig/: CSVs, charts, and narrative summary
- Covers: accuracy by language/field_type/method, failure decomposition,
  classification accuracy, latency, cost estimates, LLM non-determinism
```

Do not merge to dev yet — I'll review the charts and narrative first.

---

**Rules throughout:**

- `from dotenv import load_dotenv; load_dotenv()` at the top of every script that touches Azure or OpenAI
- Run the 164-test diagnostic only the planned number of times (once for Sections B/C, three times for Section D non-determinism). Do not run it extra times — each run costs API calls
- All CSV and chart files go under `reports/aig/`. Do not scatter them
- If any dataset column doesn't exist or doesn't match what you expect, stop and ask. Do not fabricate data columns
- Charts are for a board deck. Professional, clean, no matplotlib defaults. If in doubt, simpler is better
- One task per turn. Stop after each.

Begin with Task 0.

---