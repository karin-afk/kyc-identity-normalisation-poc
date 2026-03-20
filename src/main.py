"""
Entry point for the KYC Identity Normalisation POC.

Runs the evaluation pipeline against the golden dataset, prints
accuracy by language and by treatment type, and saves results to
  data/output/results.json
  data/output/results.csv
"""

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from evaluation.evaluator import run_evaluation
from evaluation.metrics import (
    accuracy,
    accuracy_by_language,
    accuracy_by_treatment,
    accuracy_by_language_and_field_type,
)

_OUTPUT_DIR = Path(__file__).parent.parent / "data" / "output"


def _save_results(results: list[dict]) -> None:
    _OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    # ── JSON (full detail) ────────────────────────────────────────────────
    json_path = _OUTPUT_DIR / f"results_{timestamp}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # ── CSV (flat, easy to open in Excel) ─────────────────────────────────
    csv_path = _OUTPUT_DIR / f"results_{timestamp}.csv"
    if results:
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)

    print(f"\nOutput saved to:")
    print(f"  {json_path}")
    print(f"  {csv_path}")


def main() -> None:
    print("KYC Identity Normalisation POC — Evaluation")
    print("=" * 56)

    results = run_evaluation()

    total = len(results)
    matched = sum(r["match"] for r in results)
    print(f"\nOverall accuracy : {accuracy(results):.1%}  ({matched}/{total} cases)")

    print("\nBy language:")
    for lang, acc in accuracy_by_language(results).items():
        n = sum(1 for r in results if r["language"] == lang)
        ok = sum(1 for r in results if r["language"] == lang and r["match"])
        print(f"  {lang:4s}  {acc:.1%}  ({ok}/{n})")

    print("\nBy treatment:")
    for treatment, acc in accuracy_by_treatment(results).items():
        n = sum(1 for r in results if r["expected_treatment"] == treatment)
        ok = sum(1 for r in results if r["expected_treatment"] == treatment and r["match"])
        print(f"  {treatment:22s}  {acc:.1%}  ({ok}/{n})")

    print("\nBy language × field type:")
    for lang, ft_map in accuracy_by_language_and_field_type(results).items():
        for ft, (ok, n) in ft_map.items():
            pct = ok / n if n else 0.0
            print(f"  {lang:4s}  {ft:20s}  {pct:.1%}  ({ok}/{n})")

    print("\nFailed cases:")
    for r in results:
        if not r["match"]:
            print(
                f"  {r['case_id']} [{r['language']}] {r['field_type']}: "
                f"expected='{r['expected']}' got='{r['actual']}'"
            )

    _save_results(results)


if __name__ == "__main__":
    main()
