#!/usr/bin/env python3
"""
Test Dataset Diagnostic Runner
==============================

Same structure and pipeline as run_integration_diagnostic.py, but reads test
cases from data/test_dataset.csv instead of the inline TEST_CASES list.

CSV columns expected (in this order):
    case_id, image_path, language, script, country, document_type,
    field_type, original_text, expected_treatment, expected_transliteration,
    expected_allowed_variants, expected_english, expected_normalised,
    should_flag_review, is_negative_case, risk_notes

The script:
  - Uses original_text as the paste input
  - Uses field_type as expected_field_type
  - Uses language as expected_language
  - Uses expected_normalised as expected_normalised_form
  - Derives expected_method from expected_treatment (mapping below)
  - Uses risk_notes as the notes field

Output saved to: reports/test_dataset-report-<timestamp>.md
                 reports/test_dataset-report-latest.md

Usage (from repo root):
    python run_test_dataset_diagnostic.py

Requirements:
    OPENAI_API_KEY must be set in .env
    Flask app dependencies installed (pip install -r requirements.txt)
    data/test_dataset.csv must exist

A few things worth flagging:

1. The TREATMENT_TO_METHOD map is a judgement call, not a fixed truth. The golden dataset's expected_treatment vocabulary (TRANSLITERATE, TRANSLATE_NORMALISE, PRESERVE_NORMALISE_SCRIPT, etc.) doesn't map 1:1 to the pipeline's processing_method values. I've been generous — TRANSLATE_NORMALISE for example accepts NMT or transliteration or vocabulary or composition, because addresses and company names can resolve through any of those depending on field type and language. Tighten the map as the pipeline matures.
2. The script uses expected_normalised from the CSV as the expected normalised form, not expected_english or expected_transliteration. That matches the integration diagnostic's behaviour: the normalised_form in the pipeline output is the uppercase, diacritic-stripped screening form. If you'd rather compare against expected_english, change the relevant line in load_test_cases.
3. Comparison is case-insensitive and whitespace-stripped (same as the integration diagnostic). Differences in capitalisation, surrounding spaces, etc. will not fail tests.
4. Allowed variants aren't asserted yet. Your golden has expected_allowed_variants populated for most rows — this script reads them but doesn't check them, mirroring the integration diagnostic. Worth a follow-up addition.
5. Rows with unknown expected_treatment are skipped with a warning, not failed. If your CSV has values I haven't mapped, you'll see them listed at the start of the run; add them to TREATMENT_TO_METHOD as needed.
6. Expect this to be slow. ~600 rows × one GPT-4o-mini call each is roughly 5–15 minutes depending on rate limits. If you want a quick filtered run for one language, add a --language ar flag — happy to draft that if useful.
"""

import csv
import sys
import os
import time
import traceback
from datetime import datetime
from pathlib import Path

# ── Path setup ─────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env", override=True)
except ImportError:
    pass

os.environ.setdefault("FLASK_ENV", "development")

# ── Configuration ──────────────────────────────────────────────────────────────
TEST_DATASET_CSV = ROOT / "data" / "test_dataset.csv"

# Map golden-format expected_treatment values to pipeline processing_method
# values. A list means any of those methods passes.
TREATMENT_TO_METHOD: dict[str, list[str]] = {
    "PRESERVE":                  ["PRESERVE"],
    "PRESERVE_NORMALISE_SCRIPT": ["PRESERVE"],
    "TRANSLITERATE":             ["TRANSLITERATE", "TRANSLITERATION"],
    "TRANSLATE_NORMALISE":       ["NMT", "TRANSLITERATE", "TRANSLITERATION",
                                  "VOCABULARY", "COMPOSITION"],
    "TRANSLATE_ANALYST":         ["NMT", "TRANSLATE_ANALYST", "UNRESOLVED"],
    "NORMALISE":                 ["NUMERIC", "CALENDAR", "PRESERVE", "RULE"],
    "NORMALISE_NUMERIC":         ["NUMERIC", "CALENDAR"],
    "FLAG_REVIEW":               ["UNRESOLVED"],
}

# ── ANSI colours ───────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
GREY   = "\033[90m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

PASS_MARK = "✓"
FAIL_MARK = "✗"
WARN_MARK = "⚠"


def ok(text):   return f"{GREEN}{PASS_MARK} {text}{RESET}"
def fail(text): return f"{RED}{FAIL_MARK} {text}{RESET}"
def warn(text): return f"{YELLOW}{WARN_MARK} {text}{RESET}"
def info(text): return f"{CYAN}{text}{RESET}"
def grey(text): return f"{GREY}{text}{RESET}"


def md_pass(text): return f"✅ {text}"
def md_fail(text): return f"❌ {text}"
def md_warn(text): return f"⚠️ {text}"


# ── CSV loader ─────────────────────────────────────────────────────────────────

def _coerce_bool(value: str) -> bool:
    return (value or "").strip().lower() in {"true", "1", "yes", "y"}


def load_test_cases(csv_path: Path) -> list:
    """Load test cases from the golden CSV format.

    Returns a list of tuples in the same shape used by the integration
    diagnostic:
        (test_id, description, paste_text,
         expected_field_type, expected_language,
         expected_normalised_form, expected_method, notes)

    Rows with empty original_text are skipped (no input to test).
    Rows where expected_treatment isn't in TREATMENT_TO_METHOD are skipped
    with a warning printed to stderr.
    """
    if not csv_path.exists():
        print(fail(f"Test dataset CSV not found at {csv_path}"))
        sys.exit(1)

    test_cases: list = []
    skipped: list = []

    with csv_path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            case_id = (row.get("case_id") or "").strip()
            paste_text = (row.get("original_text") or "").strip()
            language = (row.get("language") or "").strip()
            field_type = (row.get("field_type") or "").strip()
            treatment = (row.get("expected_treatment") or "").strip().upper()
            expected_normalised = (row.get("expected_normalised") or "").strip()
            notes = (row.get("risk_notes") or "").strip()
            is_negative = _coerce_bool(row.get("is_negative_case", ""))

            if not case_id or not paste_text:
                continue

            description_bits = []
            if row.get("document_type"):
                description_bits.append(row["document_type"].strip())
            description_bits.append(field_type or "field")
            description_bits.append(f"({language})")
            if is_negative:
                description_bits.append("[negative]")
            description = " / ".join(description_bits)

            if treatment not in TREATMENT_TO_METHOD:
                skipped.append((case_id, treatment or "<empty>"))
                continue

            expected_methods = TREATMENT_TO_METHOD[treatment]
            # If the dataset says FLAG_REVIEW / TRANSLATE_ANALYST and provides
            # no normalised form, treat as None (expect UNRESOLVED path).
            if treatment in {"FLAG_REVIEW"} and not expected_normalised:
                expected_normalised_form = None
            else:
                expected_normalised_form = expected_normalised or None

            test_cases.append((
                case_id,
                description,
                paste_text,
                field_type,
                language,
                expected_normalised_form,
                expected_methods if len(expected_methods) > 1 else expected_methods[0],
                notes,
            ))

    if skipped:
        print(warn(f"Skipped {len(skipped)} rows with unknown expected_treatment:"))
        for case_id, treatment in skipped[:10]:
            print(f"    {case_id}: '{treatment}'")
        if len(skipped) > 10:
            print(f"    ... and {len(skipped) - 10} more")

    return test_cases


# ── Diagnosis helpers ──────────────────────────────────────────────────────────

def _diagnose_method_failure(got_method, exp_methods, actual_field_type,
                              actual_language, got_field_type, exp_field_type):
    if got_method == "UNRESOLVED" and "UNRESOLVED" not in exp_methods:
        if actual_field_type != exp_field_type:
            return (
                f"GPT-4o-mini classified as '{actual_field_type}' instead of "
                f"'{exp_field_type}'. Router received the wrong field type."
            )
        return (
            f"Strategy for field_type='{actual_field_type}' language='{actual_language}' "
            f"returned None. Check the relevant strategy module."
        )

    if got_method == "PRESERVE" and "PRESERVE" not in exp_methods:
        return (
            f"Field type '{actual_field_type}' is being preserved but the dataset "
            f"expects further normalisation. Check PRESERVE_FIELDS membership."
        )

    if "VOCABULARY" in exp_methods and got_method != "VOCABULARY":
        return (
            f"Expected VOCABULARY but got {got_method}. Check the lookup table "
            f"for field_type='{actual_field_type}' language='{actual_language}'."
        )

    if "CALENDAR" in exp_methods and got_method != "CALENDAR":
        return (
            f"Expected CALENDAR but got {got_method}. Check calendar_rules.py "
            f"detection for language '{actual_language}'."
        )

    if "CHARACTER_MAP" in exp_methods and got_method != "CHARACTER_MAP":
        return (
            f"Expected CHARACTER_MAP but got {got_method}. Check "
            f"character_map_normaliser.py for language '{actual_language}'."
        )

    if any(m in exp_methods for m in ["TRANSLITERATION", "TRANSLITERATE"]) and \
       got_method not in ["TRANSLITERATION", "TRANSLITERATE"]:
        return (
            f"Expected TRANSLITERATE but got {got_method}. Check "
            f"transliteration.py for language '{actual_language}'."
        )

    if "NMT" in exp_methods and got_method != "NMT":
        return (
            f"Expected NMT but got {got_method}. Check nmt_translator.py — "
            f"is field_type='{actual_field_type}' in PROSE_FIELDS?"
        )

    return f"Got '{got_method}', expected one of {exp_methods}. Check router wiring."


def _diagnose_form_failure(got_form, exp_form, got_method, original_text):
    if got_form is None:
        return "normalised_form is None — the strategy ran but returned an empty result."

    got_upper = (got_form or "").strip().upper()
    exp_upper = (exp_form or "").strip().upper()

    if got_upper == exp_upper.replace(" ", "") and " " in exp_upper:
        return (
            f"Got '{got_form}' — word boundary/space missing. Expected '{exp_form}'."
        )

    if got_method == "CHARACTER_MAP" and got_upper != exp_upper:
        return (
            f"Character map produced '{got_form}' instead of '{exp_form}'. "
            f"Check the language map covers all characters in '{original_text}'."
        )

    if got_method == "CALENDAR" and got_form != exp_form:
        return (
            f"Calendar conversion produced '{got_form}' instead of '{exp_form}'. "
            f"Check the epoch calculation."
        )

    if got_method == "VOCABULARY":
        return (
            f"Vocabulary lookup returned '{got_form}' instead of '{exp_form}'. "
            f"Check the JSON lookup table entry for '{original_text}'."
        )

    if got_method in ("TRANSLITERATE", "TRANSLITERATION"):
        return (
            f"Transliteration produced '{got_form}' instead of '{exp_form}'. "
            f"Check the language-specific handler and any BGN/PCGN post-processing."
        )

    return f"Got '{got_form}', expected '{exp_form}'. Inspect the strategy module output."


# ── Main runner ────────────────────────────────────────────────────────────────

def run():
    print(f"\n{BOLD}KYC Test Dataset Diagnostic Runner{RESET}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Dataset: {TEST_DATASET_CSV}")

    test_cases = load_test_cases(TEST_DATASET_CSV)
    print(f"Examples: {len(test_cases)}\n")
    print("=" * 70)

    try:
        from app import create_app
        flask_app = create_app("development")
        ctx = flask_app.app_context()
        ctx.push()
        print(ok("Flask app context created"))
    except Exception as e:
        print(fail(f"Failed to create Flask app context: {e}"))
        print(traceback.format_exc())
        sys.exit(1)

    try:
        from app.pipeline.normalisation.field_type_detector import detect_field_type
        from app.pipeline.orchestrator import process_field_row
        print(ok("Pipeline modules imported"))
    except Exception as e:
        print(fail(f"Failed to import pipeline modules: {e}"))
        print(traceback.format_exc())
        sys.exit(1)

    print("=" * 70 + "\n")

    report_lines = []
    report_lines.append("# KYC Test Dataset Diagnostic Report")
    report_lines.append(f"\n**Run date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"**Dataset:** `{TEST_DATASET_CSV.relative_to(ROOT)}`")
    report_lines.append(f"**Examples:** {len(test_cases)}")
    report_lines.append(f"**Pipeline:** `detect_field_type()` → `process_field_row()` → `route_field()` → strategy")
    report_lines.append(f"**Mocks:** None — all calls are real\n")
    report_lines.append("---\n")

    summary = []  # (id, description, overall_pass)

    for (test_id, description, paste_text,
         exp_field_type, exp_language,
         exp_normalised, exp_method, notes) in test_cases:

        exp_methods = [exp_method] if isinstance(exp_method, str) else exp_method

        print(f"{BOLD}{'─' * 70}{RESET}")
        print(f"{BOLD}{test_id} — {description}{RESET}")
        print(f"  Input:    {info(repr(paste_text))}")
        print(f"  Expected: field_type={exp_field_type}, language={exp_language}")
        print(f"  Expected: normalised={repr(exp_normalised)}, method={exp_method}")
        if notes:
            print(f"  Note:     {grey(notes)}")
        print()

        report_lines.append(f"## {test_id} — {description}\n")
        report_lines.append(f"| | |")
        report_lines.append(f"|---|---|")
        report_lines.append(f"| **Input** | `{paste_text}` |")
        report_lines.append(f"| **Expected field type** | `{exp_field_type}` |")
        report_lines.append(f"| **Expected language** | `{exp_language}` |")
        report_lines.append(f"| **Expected normalised form** | `{exp_normalised}` |")
        report_lines.append(f"| **Expected method** | `{exp_method}` |")
        if notes:
            report_lines.append(f"| **Notes** | {notes} |")
        report_lines.append("")

        overall_pass = True

        # Step 1: GPT-4o-mini classification
        report_lines.append("### Step 1 — GPT-4o-mini classification\n")
        print(f"  {BOLD}Step 1:{RESET} GPT-4o-mini classification")

        t0 = time.time()
        try:
            got_field_type, got_confidence, got_language = detect_field_type(paste_text)
            elapsed = time.time() - t0

            ft_ok = got_field_type == exp_field_type
            lang_ok = got_language == exp_language

            ft_mark = ok if ft_ok else warn
            lang_mark = ok if lang_ok else warn

            print(f"    field_type:  {ft_mark(got_field_type)} (expected: {exp_field_type})")
            print(f"    language:    {lang_mark(got_language)} (expected: {exp_language})")
            print(f"    confidence:  {got_confidence:.2f}")
            print(f"    time:        {elapsed:.2f}s")

            report_lines.append(f"| | Expected | Got | Status |")
            report_lines.append(f"|---|---|---|---|")
            report_lines.append(f"| **field_type** | `{exp_field_type}` | `{got_field_type}` | {md_pass('match') if ft_ok else md_warn('mismatch')} |")
            report_lines.append(f"| **language** | `{exp_language}` | `{got_language}` | {md_pass('match') if lang_ok else md_warn('mismatch')} |")
            report_lines.append(f"| **confidence** | — | `{got_confidence:.2f}` | — |")
            report_lines.append(f"| **latency** | — | `{elapsed:.2f}s` | — |")
            report_lines.append("")

            if not ft_ok:
                report_lines.append(f"> ⚠️ **Classification mismatch on field_type.** GPT-4o-mini returned `{got_field_type}` but expected `{exp_field_type}`.\n")
            if not lang_ok:
                report_lines.append(f"> ⚠️ **Classification mismatch on language.** GPT-4o-mini returned `{got_language}` but expected `{exp_language}`.\n")

            actual_field_type = got_field_type
            actual_language = got_language

        except Exception as e:
            print(f"    {fail(f'EXCEPTION: {e}')}")
            print(traceback.format_exc())
            report_lines.append(md_fail(f"**EXCEPTION in detect_field_type:** `{e}`\n"))
            report_lines.append(f"```\n{traceback.format_exc()}\n```\n")
            summary.append((test_id, description, False))
            report_lines.append("---\n")
            continue

        print()

        # Step 2: Orchestrator + Router
        report_lines.append("### Step 2 — Orchestrator + Router\n")
        print(f"  {BOLD}Step 2:{RESET} Orchestrator → Router")

        row = {
            "original_text": paste_text,
            "field_type":    actual_field_type,
            "language":      actual_language,
        }

        print(f"    Row passed to orchestrator:")
        print(f"      original_text: {repr(paste_text)}")
        print(f"      field_type:    {actual_field_type}")
        print(f"      language:      {actual_language}")

        report_lines.append("**Row passed to orchestrator:**\n")
        report_lines.append("```json")
        report_lines.append(f'{{"original_text": "{paste_text}", "field_type": "{actual_field_type}", "language": "{actual_language}"}}')
        report_lines.append("```\n")

        t1 = time.time()
        try:
            result = process_field_row(row)
            elapsed2 = time.time() - t1

            got_normalised = result.get("normalised_form")
            got_method = result.get("processing_method", "")
            got_review = result.get("review_required", False)
            got_confidence = result.get("confidence", 0.0)
            got_variants = result.get("allowed_variants", [])

            print(f"    processing_method: {info(got_method)}")
            print(f"    normalised_form:   {info(repr(got_normalised))}")
            print(f"    confidence:        {got_confidence:.2f}")
            print(f"    review_required:   {got_review}")
            if got_variants:
                print(f"    allowed_variants:  {got_variants}")
            print(f"    time:              {elapsed2:.2f}s")

            report_lines.append("**Router result:**\n")
            report_lines.append(f"| Field | Value |")
            report_lines.append(f"|---|---|")
            report_lines.append(f"| processing_method | `{got_method}` |")
            report_lines.append(f"| normalised_form | `{got_normalised}` |")
            report_lines.append(f"| confidence | `{got_confidence:.2f}` |")
            report_lines.append(f"| review_required | `{got_review}` |")
            if got_variants:
                report_lines.append(f"| allowed_variants | {', '.join(f'`{v}`' for v in got_variants)} |")
            report_lines.append(f"| latency | `{elapsed2:.2f}s` |")
            report_lines.append("")

        except Exception as e:
            print(f"    {fail(f'EXCEPTION: {e}')}")
            print(traceback.format_exc())
            report_lines.append(md_fail(f"**EXCEPTION in process_field_row:** `{e}`\n"))
            report_lines.append(f"```\n{traceback.format_exc()}\n```\n")
            summary.append((test_id, description, False))
            report_lines.append("---\n")
            continue

        print()

        # Step 3: Comparison
        report_lines.append("### Step 3 — Expected vs Actual\n")
        print(f"  {BOLD}Step 3:{RESET} Comparison")

        method_pass = got_method in exp_methods
        if exp_normalised is None:
            form_pass = got_normalised is None or got_method == "UNRESOLVED"
        else:
            form_pass = (got_normalised or "").strip().upper() == exp_normalised.strip().upper()

        method_mark = ok if method_pass else fail
        form_mark = ok if form_pass else fail

        print(f"    method:     {method_mark(got_method)} (expected: {'/'.join(exp_methods)})")
        print(f"    normalised: {form_mark(repr(got_normalised))} (expected: {repr(exp_normalised)})")

        example_pass = method_pass and form_pass

        report_lines.append(f"| | Expected | Got | Status |")
        report_lines.append(f"|---|---|---|---|")
        report_lines.append(f"| **method** | `{'` or `'.join(exp_methods)}` | `{got_method}` | {md_pass('PASS') if method_pass else md_fail('FAIL')} |")
        report_lines.append(f"| **normalised_form** | `{exp_normalised}` | `{got_normalised}` | {md_pass('PASS') if form_pass else md_fail('FAIL')} |")
        report_lines.append("")

        if not method_pass:
            diagnosis = _diagnose_method_failure(
                got_method, exp_methods, actual_field_type, actual_language,
                got_field_type, exp_field_type
            )
            print(f"    {warn('Diagnosis: ' + diagnosis)}")
            report_lines.append(f"> ❌ **Method failure diagnosis:** {diagnosis}\n")

        if not form_pass and method_pass:
            diagnosis = _diagnose_form_failure(
                got_normalised, exp_normalised, got_method, paste_text
            )
            print(f"    {warn('Diagnosis: ' + diagnosis)}")
            report_lines.append(f"> ❌ **Form failure diagnosis:** {diagnosis}\n")

        result_line = f"### Overall: {'✅ PASS' if example_pass else '❌ FAIL'}\n"
        report_lines.append(result_line)
        print(f"\n  {'=' * 30}")
        print(f"  {ok('PASS') if example_pass else fail('FAIL')} — {test_id} {description}")
        print()

        summary.append((test_id, description, example_pass))
        report_lines.append("---\n")

    # ── Summary ────────────────────────────────────────────────────────────────
    passed = sum(1 for _, _, p in summary if p)
    failed = len(summary) - passed

    print(f"\n{'=' * 70}")
    print(f"{BOLD}SUMMARY{RESET}")
    print(f"{'=' * 70}")
    print(f"  Total:  {len(summary)}")
    print(f"  {ok(f'Passed: {passed}')}")
    if failed:
        print(f"  {fail(f'Failed: {failed}')}")
    print()

    for test_id, description, passed_flag in summary:
        mark = ok(f"PASS  {test_id}  {description}") if passed_flag else fail(f"FAIL  {test_id}  {description}")
        print(f"  {mark}")

    # Insert summary at top of markdown
    report_lines.insert(6, f"\n## Summary\n")
    report_lines.insert(7, f"| Result | Count |")
    report_lines.insert(8, f"|---|---|")
    report_lines.insert(9, f"| ✅ Pass | {passed} |")
    report_lines.insert(10, f"| ❌ Fail | {failed} |")
    report_lines.insert(11, f"| Total | {len(summary)} |")
    report_lines.insert(12, f"\n| ID | Description | Result |")
    report_lines.insert(13, f"|---|---|---|")
    for i, (test_id, description, p) in enumerate(summary):
        report_lines.insert(14 + i, f"| {test_id} | {description} | {'✅ PASS' if p else '❌ FAIL'} |")
    report_lines.insert(14 + len(summary), "\n---\n")

    # Write report
    reports_dir = ROOT / "reports"
    reports_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%SZ")
    report_path = reports_dir / f"test_dataset-report-{timestamp}.md"
    latest_path = reports_dir / "test_dataset-report-latest.md"

    report_text = "\n".join(report_lines)
    report_path.write_text(report_text, encoding="utf-8")
    latest_path.write_text(report_text, encoding="utf-8")

    print(f"\n{'=' * 70}")
    print(f"Report saved to:")
    print(f"  {report_path}")
    print(f"  {latest_path}  (always the latest run)")
    print(f"{'=' * 70}\n")

    ctx.pop()
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(run())