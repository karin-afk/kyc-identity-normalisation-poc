from dotenv import load_dotenv; load_dotenv()

import ast
import csv
import os
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
from typing import Any


def to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def safe_upper(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().upper()


def method_as_list(expected_method: Any) -> list[str]:
    if isinstance(expected_method, list):
        return [safe_upper(x) for x in expected_method]
    return [safe_upper(expected_method)]


def classify_failure_category(
    test_id: str,
    notes: str,
    field_type_match: bool,
    language_match: bool,
    unstable_ids: set[str],
) -> str:
    note_lower = (notes or "").lower()
    phase2_markers = [
        "tier 7",
        "strategy e",
        "invoice",
        "structured extraction",
        "phase 2",
    ]
    if any(marker in note_lower for marker in phase2_markers):
        return "phase_2_scope"
    if test_id.startswith("E."):
        return "phase_2_scope"
    if (not field_type_match) or (not language_match):
        return "classifier_edge_case"
    if test_id in unstable_ids:
        return "llm_nondeterminism"
    return "genuine_bug"


def summarise_pass_rate(rows: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for row in rows:
        group = str(row.get(key, "") or "unknown")
        if group not in grouped:
            grouped[group] = {"total": 0, "passed": 0}
        grouped[group]["total"] += 1
        if to_bool(row.get("passed")):
            grouped[group]["passed"] += 1

    out = []
    for group, counts in sorted(grouped.items()):
        total = counts["total"]
        passed = counts["passed"]
        failed = total - passed
        out.append(
            {
                key: group,
                "total": total,
                "passed": passed,
                "failed": failed,
                "pass_rate": round((passed / total) if total else 0.0, 6),
            }
        )
    return out


def run_single_diagnostic(
    run_label: str,
    test_cases: list[tuple[Any, ...]],
    detect_field_type,
    process_field_row,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    for (
        test_id,
        description,
        paste_text,
        expected_field_type,
        expected_language,
        expected_normalised,
        expected_method,
        notes,
    ) in test_cases:
        c0 = time.perf_counter()
        got_field_type = ""
        got_language = ""
        classification_confidence = 0.0
        classifier_error = ""
        try:
            got_field_type, classification_confidence, got_language = detect_field_type(paste_text)
        except Exception as exc:
            classifier_error = f"{type(exc).__name__}: {exc}"
            got_field_type = ""
            got_language = ""
            classification_confidence = 0.0
        classification_latency = time.perf_counter() - c0
        time.sleep(1.5)  # pace to stay under 200K TPM

        r0 = time.perf_counter()
        router_error = ""
        result = {}
        try:
            result = process_field_row(
                {
                    "original_text": paste_text,
                    "field_type": got_field_type,
                    "language": got_language,
                }
            )
        except Exception as exc:
            router_error = f"{type(exc).__name__}: {exc}"
            result = {}
        router_latency = time.perf_counter() - r0

        actual_method = safe_upper(result.get("processing_method", "UNRESOLVED"))
        actual_normalised = result.get("normalised_form")
        router_confidence = to_float(result.get("confidence", 0.0))
        review_required = to_bool(result.get("review_required", False))

        expected_methods = method_as_list(expected_method)
        method_match = actual_method in expected_methods

        if expected_normalised is None:
            form_match = actual_normalised is None or actual_method == "UNRESOLVED"
        else:
            form_match = safe_upper(actual_normalised) == safe_upper(expected_normalised)

        passed = bool(method_match and form_match and not classifier_error and not router_error)
        field_type_match = safe_upper(got_field_type) == safe_upper(expected_field_type)
        language_match = safe_upper(got_language) == safe_upper(expected_language)

        rows.append(
            {
                "run": run_label,
                "test_id": test_id,
                "description": description,
                "original_text": paste_text,
                "expected_field_type": expected_field_type,
                "expected_language": expected_language,
                "expected_normalised": expected_normalised,
                "expected_method": "|".join(expected_methods),
                "notes": notes,
                "got_field_type": got_field_type,
                "got_language": got_language,
                "field_type_match": field_type_match,
                "language_match": language_match,
                "classification_confidence": round(classification_confidence, 6),
                "classification_latency_s": round(classification_latency, 6),
                "method": actual_method,
                "normalised_form": actual_normalised,
                "router_confidence": round(router_confidence, 6),
                "router_latency_s": round(router_latency, 6),
                "total_latency_s": round(classification_latency + router_latency, 6),
                "review_required": review_required,
                "allowed_variants": "|".join(result.get("allowed_variants", []) or []),
                "pass_fail": "PASS" if passed else "FAIL",
                "passed": passed,
                "classifier_error": classifier_error,
                "router_error": router_error,
                "input_chars": len(paste_text or ""),
            }
        )

    return rows


def run_dataset_once(
    dataset_path: Path,
    detect_field_type,
    process_field_row,
) -> list[dict[str, Any]]:
    out_rows: list[dict[str, Any]] = []
    with dataset_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            original_text = row.get("original_text", "")
            language_hint = row.get("language", "")

            c0 = time.perf_counter()
            classifier_error = ""
            got_field_type = ""
            got_language = ""
            classification_confidence = 0.0
            try:
                got_field_type, classification_confidence, got_language = detect_field_type(
                    original_text,
                    language_hint=language_hint,
                )
            except Exception as exc:
                classifier_error = f"{type(exc).__name__}: {exc}"
            classification_latency = time.perf_counter() - c0
            time.sleep(1.5)  # pace to stay under 200K TPM

            r0 = time.perf_counter()
            router_error = ""
            result = {}
            try:
                result = process_field_row(
                    {
                        "original_text": original_text,
                        "field_type": got_field_type,
                        "language": got_language,
                        "country": row.get("country", ""),
                    }
                )
            except Exception as exc:
                router_error = f"{type(exc).__name__}: {exc}"
            router_latency = time.perf_counter() - r0

            normalised_form = result.get("normalised_form")
            method = safe_upper(result.get("processing_method", "UNRESOLVED"))
            confidence = to_float(result.get("confidence", 0.0))
            review_required = to_bool(result.get("review_required", False))
            allowed_variants = result.get("allowed_variants", []) or []

            expected = row.get("expected_normalised", "")
            pass_fail = "UNKNOWN"
            if expected:
                pass_fail = "PASS" if safe_upper(expected) == safe_upper(normalised_form) else "FAIL"

            enriched = dict(row)
            enriched.update(
                {
                    "detected_field_type": got_field_type,
                    "detected_language": got_language,
                    "classification_confidence": round(classification_confidence, 6),
                    "normalised_form": normalised_form,
                    "method": method,
                    "confidence": round(confidence, 6),
                    "review_required": review_required,
                    "classification_latency_s": round(classification_latency, 6),
                    "router_latency_s": round(router_latency, 6),
                    "pass_fail": pass_fail,
                    "allowed_variants": "|".join(allowed_variants),
                    "variant_count": len(allowed_variants),
                    "classifier_error": classifier_error,
                    "router_error": router_error,
                    "input_chars": len(original_text or ""),
                }
            )
            out_rows.append(enriched)

    return out_rows


def parse_pytest_counts(stdout: str) -> dict[str, int]:
    counts = {"passed": 0, "failed": 0, "errors": 0, "skipped": 0}
    summary_lines = [line.strip() for line in stdout.splitlines() if " in " in line and "=" in line]
    if not summary_lines:
        return counts

    last = summary_lines[-1]
    patterns = {
        "passed": r"(\d+)\s+passed",
        "failed": r"(\d+)\s+failed",
        "errors": r"(\d+)\s+error",
        "skipped": r"(\d+)\s+skipped",
    }
    for key, pattern in patterns.items():
        m = re.search(pattern, last)
        if m:
            counts[key] = int(m.group(1))
    return counts


def collect_test_file_metadata(tests_dir: Path) -> dict[str, dict[str, Any]]:
    metadata: dict[str, dict[str, Any]] = {}
    for path in sorted(tests_dir.glob("test_*.py")):
        src = path.read_text(encoding="utf-8-sig")
        tree = ast.parse(src)
        test_count = sum(
            1
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_")
        )

        stem = path.stem
        module_tested = stem.replace("test_", "", 1)
        integration_tokens = ["integration", "e2e", "route", "frontend", "evaluator", "router"]
        test_type = "integration" if any(tok in stem for tok in integration_tokens) else "unit"

        metadata[path.name] = {
            "test_file": path.name,
            "module_tested": module_tested,
            "test_type": test_type,
            "total_tests": test_count,
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "skipped": 0,
        }
    return metadata


def update_test_stats_from_junit(xml_path: Path, file_stats: dict[str, dict[str, Any]]) -> None:
    if not xml_path.exists():
        return

    tree = ET.parse(xml_path)
    root = tree.getroot()

    for tc in root.findall(".//testcase"):
        classname = tc.attrib.get("classname", "")
        file_key = ""
        if classname.startswith("tests."):
            file_key = classname.split(".")[-1] + ".py"

        if not file_key or file_key not in file_stats:
            continue

        if tc.find("failure") is not None:
            file_stats[file_key]["failed"] += 1
        elif tc.find("error") is not None:
            file_stats[file_key]["errors"] += 1
        elif tc.find("skipped") is not None:
            file_stats[file_key]["skipped"] += 1
        else:
            file_stats[file_key]["passed"] += 1


def main() -> int:
    start_time = time.perf_counter()

    root = Path(__file__).resolve().parent
    reports_dir = root / "reports" / "aig"
    reports_dir.mkdir(parents=True, exist_ok=True)

    # Import after cwd/path setup so app modules resolve the same way as diagnostics.
    sys.path.insert(0, str(root))
    sys.path.insert(0, str(root / "src"))

    os.environ["CLASSIFIER_MODE"] = "llm"

    from app import create_app
    from app.pipeline.normalisation.field_type_detector import detect_field_type
    from app.pipeline.orchestrator import process_field_row
    import run_integration_diagnostic as rid

    all_csv_paths: list[Path] = []

    # Step 1: run diagnostic exactly 3 times.
    app = create_app("development")
    with app.app_context():
        diagnostic_runs: list[list[dict[str, Any]]] = []
        for idx in range(1, 4):
            run_rows = run_single_diagnostic(
                run_label=f"run{idx}",
                test_cases=rid.TEST_CASES,
                detect_field_type=detect_field_type,
                process_field_row=process_field_row,
            )
            diagnostic_runs.append(run_rows)

    run1_rows = diagnostic_runs[0]

    # Step 2 + Step 3: full datasets once each.
    with app.app_context():
        golden_rows = run_dataset_once(root / "data" / "golden_dataset.csv", detect_field_type, process_field_row)
        test_rows = run_dataset_once(root / "data" / "test_dataset.csv", detect_field_type, process_field_row)

    # Step 4: pytest once.
    pytest_xml = reports_dir / "pytest_junit.xml"
    pytest_cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/",
        "--tb=line",
        "-q",
        "--no-header",
        f"--junitxml={pytest_xml}",
    ]
    proc = subprocess.run(pytest_cmd, cwd=root, capture_output=True, text=True)
    pytest_stdout = (proc.stdout or "") + "\n" + (proc.stderr or "")
    pytest_counts = parse_pytest_counts(pytest_stdout)

    # Step 5: generate CSVs from saved data only.

    # Section A
    tests_dir = root / "tests"
    file_stats = collect_test_file_metadata(tests_dir)
    update_test_stats_from_junit(pytest_xml, file_stats)

    suite_rows = []
    for name in sorted(file_stats):
        row = file_stats[name]
        total = row["total_tests"]
        passed = row["passed"]
        row["pass_rate"] = round((passed / total) if total else 0.0, 6)
        suite_rows.append(row)

    section_a_path = reports_dir / "test_suite_health.csv"
    write_csv(
        section_a_path,
        suite_rows,
        [
            "test_file",
            "module_tested",
            "test_type",
            "total_tests",
            "passed",
            "failed",
            "errors",
            "skipped",
            "pass_rate",
        ],
    )
    all_csv_paths.append(section_a_path)

    # Section B
    by_language = summarise_pass_rate(
        [{"language": r.get("got_language") or r.get("expected_language"), "passed": r.get("passed")} for r in run1_rows],
        "language",
    )
    by_field_type = summarise_pass_rate(
        [{"field_type": r.get("got_field_type") or r.get("expected_field_type"), "passed": r.get("passed")} for r in run1_rows],
        "field_type",
    )
    by_method = summarise_pass_rate(
        [{"method": r.get("method"), "passed": r.get("passed")} for r in run1_rows],
        "method",
    )

    p = reports_dir / "diagnostic_by_language.csv"
    write_csv(p, by_language, ["language", "total", "passed", "failed", "pass_rate"])
    all_csv_paths.append(p)

    p = reports_dir / "diagnostic_by_field_type.csv"
    write_csv(p, by_field_type, ["field_type", "total", "passed", "failed", "pass_rate"])
    all_csv_paths.append(p)

    p = reports_dir / "diagnostic_by_method.csv"
    write_csv(p, by_method, ["method", "total", "passed", "failed", "pass_rate"])
    all_csv_paths.append(p)

    # Nondeterminism prep for failure classification.
    by_test_all_runs: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for run_rows in diagnostic_runs:
        for row in run_rows:
            by_test_all_runs[row["test_id"]].append(row)

    nondeterminism_rows: list[dict[str, Any]] = []
    unstable_ids: set[str] = set()
    for test_id, items in sorted(by_test_all_runs.items()):
        if len(items) != 3:
            continue
        i1, i2, i3 = items
        r1 = i1["pass_fail"]
        r2 = i2["pass_fail"]
        r3 = i3["pass_fail"]
        n1 = i1.get("normalised_form")
        n2 = i2.get("normalised_form")
        n3 = i3.get("normalised_form")
        stable = (r1 == r2 == r3) and (safe_upper(n1) == safe_upper(n2) == safe_upper(n3))
        if not stable:
            unstable_ids.add(test_id)
        nondeterminism_rows.append(
            {
                "test_id": test_id,
                "run1_result": r1,
                "run2_result": r2,
                "run3_result": r3,
                "run1_normalised": n1,
                "run2_normalised": n2,
                "run3_normalised": n3,
                "stable": stable,
            }
        )

    failures_rows = []
    confidence_rows = []
    class_acc_rows = []
    latency_rows = []

    review_group: dict[tuple[str, str], dict[str, int]] = defaultdict(lambda: {"total": 0, "review": 0})

    for row in run1_rows:
        language = row.get("got_language") or row.get("expected_language") or ""
        field_type = row.get("got_field_type") or row.get("expected_field_type") or ""

        confidence_rows.append(
            {
                "test_id": row["test_id"],
                "passed": row["passed"],
                "classification_confidence": row["classification_confidence"],
                "router_confidence": row["router_confidence"],
            }
        )

        class_acc_rows.append(
            {
                "test_id": row["test_id"],
                "expected_field_type": row["expected_field_type"],
                "got_field_type": row["got_field_type"],
                "field_type_match": row["field_type_match"],
                "expected_language": row["expected_language"],
                "got_language": row["got_language"],
                "language_match": row["language_match"],
            }
        )

        latency_rows.append(
            {
                "test_id": row["test_id"],
                "method": row["method"],
                "classification_latency_s": row["classification_latency_s"],
                "router_latency_s": row["router_latency_s"],
                "total_latency_s": row["total_latency_s"],
            }
        )

        k = (language, field_type)
        review_group[k]["total"] += 1
        if row["review_required"]:
            review_group[k]["review"] += 1

        if not row["passed"]:
            failures_rows.append(
                {
                    "test_id": row["test_id"],
                    "description": row["description"],
                    "field_type": field_type,
                    "language": language,
                    "expected": row["expected_normalised"],
                    "actual": row["normalised_form"],
                    "failure_category": classify_failure_category(
                        test_id=row["test_id"],
                        notes=row.get("notes", ""),
                        field_type_match=to_bool(row.get("field_type_match")),
                        language_match=to_bool(row.get("language_match")),
                        unstable_ids=unstable_ids,
                    ),
                }
            )

    review_rows = []
    for (language, field_type), counts in sorted(review_group.items()):
        total = counts["total"]
        review_count = counts["review"]
        review_rows.append(
            {
                "language": language,
                "field_type": field_type,
                "total": total,
                "review_required_count": review_count,
                "review_rate": round((review_count / total) if total else 0.0, 6),
            }
        )

    p = reports_dir / "diagnostic_failures.csv"
    write_csv(p, failures_rows, ["test_id", "description", "field_type", "language", "expected", "actual", "failure_category"])
    all_csv_paths.append(p)

    p = reports_dir / "diagnostic_confidence.csv"
    write_csv(p, confidence_rows, ["test_id", "passed", "classification_confidence", "router_confidence"])
    all_csv_paths.append(p)

    p = reports_dir / "diagnostic_classification_accuracy.csv"
    write_csv(
        p,
        class_acc_rows,
        [
            "test_id",
            "expected_field_type",
            "got_field_type",
            "field_type_match",
            "expected_language",
            "got_language",
            "language_match",
        ],
    )
    all_csv_paths.append(p)

    p = reports_dir / "diagnostic_review_rate.csv"
    write_csv(p, review_rows, ["language", "field_type", "total", "review_required_count", "review_rate"])
    all_csv_paths.append(p)

    p = reports_dir / "diagnostic_latency.csv"
    write_csv(p, latency_rows, ["test_id", "method", "classification_latency_s", "router_latency_s", "total_latency_s"])
    all_csv_paths.append(p)

    # Section C
    golden_path = reports_dir / "golden_dataset_results.csv"
    test_path = reports_dir / "test_dataset_results.csv"

    base_columns = list(golden_rows[0].keys() if golden_rows else test_rows[0].keys() if test_rows else [])
    write_csv(golden_path, golden_rows, base_columns)
    write_csv(test_path, test_rows, list(test_rows[0].keys()) if test_rows else base_columns)
    all_csv_paths.extend([golden_path, test_path])

    combined_dataset_rows = golden_rows + test_rows

    coverage_group: dict[tuple[str, str], dict[str, int]] = defaultdict(lambda: {"count": 0, "passed": 0, "known": 0})
    for row in combined_dataset_rows:
        language = row.get("language", "")
        field_type = row.get("field_type", "")
        k = (language, field_type)
        coverage_group[k]["count"] += 1
        if row.get("pass_fail") != "UNKNOWN":
            coverage_group[k]["known"] += 1
            if row.get("pass_fail") == "PASS":
                coverage_group[k]["passed"] += 1

    coverage_rows = []
    for (language, field_type), counts in sorted(coverage_group.items()):
        denom = counts["known"] if counts["known"] else counts["count"]
        coverage_rows.append(
            {
                "language": language,
                "field_type": field_type,
                "count": counts["count"],
                "passed": counts["passed"],
                "pass_rate": round((counts["passed"] / denom) if denom else 0.0, 6),
            }
        )

    p = reports_dir / "coverage_matrix.csv"
    write_csv(p, coverage_rows, ["language", "field_type", "count", "passed", "pass_rate"])
    all_csv_paths.append(p)

    translit_languages = {"ko", "ja", "zh", "ar", "ru", "el"}
    variant_rows = []
    for row in combined_dataset_rows:
        if row.get("language") not in translit_languages:
            continue
        if row.get("field_type") not in {"person_name", "alias"}:
            continue
        variants = [v for v in str(row.get("allowed_variants", "")).split("|") if v]
        variant_rows.append(
            {
                "test_id": row.get("case_id", ""),
                "language": row.get("language", ""),
                "field_type": row.get("field_type", ""),
                "normalised_form": row.get("normalised_form", ""),
                "variant_count": len(variants),
                "variants": "|".join(variants),
            }
        )

    p = reports_dir / "variant_stats.csv"
    write_csv(p, variant_rows, ["test_id", "language", "field_type", "normalised_form", "variant_count", "variants"])
    all_csv_paths.append(p)

    # Section D
    # Pricing assumptions:
    # GPT-4o-mini classifier input: $0.15 / 1M tokens, tokens ~= chars / 4
    # Azure Translator: $10 / 1M characters
    batch_rows = run1_rows + combined_dataset_rows

    total_fields = len(batch_rows)
    total_input_chars = sum(int(r.get("input_chars", 0) or 0) for r in batch_rows)
    total_input_tokens = total_input_chars / 4.0
    classifier_total_cost = (total_input_tokens / 1_000_000.0) * 0.15

    nmt_methods = {"NMT", "TRANSLATE_NORMALISE"}
    nmt_rows = [r for r in batch_rows if safe_upper(r.get("method", "")) in nmt_methods]
    nmt_chars = sum(int(r.get("input_chars", 0) or 0) for r in nmt_rows)
    nmt_total_cost = (nmt_chars / 1_000_000.0) * 10.0

    deterministic_methods = {
        "PRESERVE",
        "CALENDAR",
        "NUMERIC",
        "VOCABULARY",
        "GEOGRAPHIC",
        "TRANSLITERATION",
        "TRANSLITERATE",
        "CHARACTER_MAP",
        "UNRESOLVED",
    }
    deterministic_rows = [r for r in batch_rows if safe_upper(r.get("method", "")) in deterministic_methods]

    cost_rows = [
        {
            "method": "FREE_DETERMINISTIC",
            "avg_cost_per_field_usd": 0.0,
            "fields_in_sample": len(deterministic_rows),
            "total_cost_usd": 0.0,
        },
        {
            "method": "CLASSIFIER",
            "avg_cost_per_field_usd": round((classifier_total_cost / total_fields) if total_fields else 0.0, 10),
            "fields_in_sample": total_fields,
            "total_cost_usd": round(classifier_total_cost, 10),
        },
        {
            "method": "NMT",
            "avg_cost_per_field_usd": round((nmt_total_cost / len(nmt_rows)) if nmt_rows else 0.0, 10),
            "fields_in_sample": len(nmt_rows),
            "total_cost_usd": round(nmt_total_cost, 10),
        },
    ]

    p = reports_dir / "cost_estimates.csv"
    write_csv(p, cost_rows, ["method", "avg_cost_per_field_usd", "fields_in_sample", "total_cost_usd"])
    all_csv_paths.append(p)

    method_latency: dict[str, list[float]] = defaultdict(list)
    for row in run1_rows:
        method_latency[safe_upper(row.get("method", "UNRESOLVED"))].append(to_float(row.get("total_latency_s"), 0.0))
    for row in combined_dataset_rows:
        total_latency = to_float(row.get("classification_latency_s"), 0.0) + to_float(row.get("router_latency_s"), 0.0)
        method_latency[safe_upper(row.get("method", "UNRESOLVED"))].append(total_latency)

    throughput_rows = []
    for method, latencies in sorted(method_latency.items()):
        avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
        throughput_rows.append(
            {
                "method": method,
                "avg_latency_s": round(avg_latency, 6),
                "estimated_fields_per_minute": round((60.0 / avg_latency) if avg_latency > 0 else 0.0, 6),
            }
        )

    p = reports_dir / "throughput.csv"
    write_csv(p, throughput_rows, ["method", "avg_latency_s", "estimated_fields_per_minute"])
    all_csv_paths.append(p)

    p = reports_dir / "nondeterminism.csv"
    write_csv(
        p,
        nondeterminism_rows,
        [
            "test_id",
            "run1_result",
            "run2_result",
            "run3_result",
            "run1_normalised",
            "run2_normalised",
            "run3_normalised",
            "stable",
        ],
    )
    all_csv_paths.append(p)

    # Persist pytest summary for reproducibility (derived data, no API).
    pytest_meta_path = reports_dir / "pytest_summary.csv"
    write_csv(
        pytest_meta_path,
        [
            {
                "passed": pytest_counts["passed"],
                "failed": pytest_counts["failed"],
                "errors": pytest_counts["errors"],
                "skipped": pytest_counts["skipped"],
                "command_exit_code": proc.returncode,
            }
        ],
        ["passed", "failed", "errors", "skipped", "command_exit_code"],
    )

    # Report summary to stdout.
    total_rows_written = 0
    for csv_path in all_csv_paths:
        with csv_path.open("r", encoding="utf-8", newline="") as f:
            total_rows_written += max(sum(1 for _ in f) - 1, 0)

    elapsed = time.perf_counter() - start_time
    print(f"CSV files generated: {len(all_csv_paths)}")
    print(f"Total rows across generated CSVs: {total_rows_written}")
    print(f"Wall-clock time (s): {elapsed:.2f}")
    print(f"Output directory: {reports_dir}")

    # Non-zero pytest should not abort analytics generation; caller can inspect CSV outputs.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
