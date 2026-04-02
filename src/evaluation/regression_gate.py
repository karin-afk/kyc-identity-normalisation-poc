"""Automated regression gate for the KYC normalisation pipeline.

This module belongs to the **evaluation layer** and is intended to be run as
part of CI/CD (via GitHub Actions) or as a pre-merge script.  It compares
pipeline accuracy results against ``ACCURACY_THRESHOLDS`` and raises
``RegressionGateFailure`` when any threshold is breached (in strict mode).

Usage (from the repo root)::

    PYTHONPATH=src python src/main.py --regression-gate

The gate loads ``data/golden_dataset.csv`` (or the path passed in), runs the
full evaluation, and checks seven categories:

* Overall accuracy
* Accuracy per language (ISO 639-1 code)
* Accuracy per processing method (PRESERVE, TRANSLITERATE, etc.)
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ACCURACY_THRESHOLDS: dict[str, float] = {
    # Overall
    "overall": 0.85,
    # Per-language
    "ar": 0.90,
    "ru": 0.80,
    "zh": 0.78,
    "ja": 0.93,
    "el": 0.85,
    "de": 0.90,
    "fr": 0.90,
    "es": 0.90,
    "it": 0.90,
    "ko": 0.88,
    "en": 0.95,
    # Per-processing-method
    "PRESERVE": 1.00,
    "TRANSLITERATE": 0.93,
    "TRANSLATE_NORMALISE": 0.70,
    "TRANSLATE_ANALYST": 0.50,
}

# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class RegressionGateFailure(Exception):
    """Raised when one or more accuracy thresholds are breached.

    Attributes:
        report: The full regression report dict, including the ``breaches`` list.
    """

    def __init__(self, message: str, report: dict) -> None:
        super().__init__(message)
        self.report = report


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _compute_per_language(results: list[dict]) -> dict[str, float]:
    """Compute per-language accuracy from *results*.

    Args:
        results: List of per-case result dicts, each with ``language`` and
            ``match`` keys.

    Returns:
        Dict mapping ISO 639-1 language code → accuracy (float 0–1).
    """
    from collections import defaultdict

    totals: dict[str, int] = defaultdict(int)
    correct: dict[str, int] = defaultdict(int)
    for r in results:
        lang = r.get("language", "")
        totals[lang] += 1
        if r.get("match"):
            correct[lang] += 1
    return {
        lang: correct[lang] / totals[lang]
        for lang in totals
        if totals[lang] > 0
    }


def _compute_per_method(results: list[dict]) -> dict[str, float]:
    """Compute per-processing-method accuracy from *results*.

    Args:
        results: List of per-case result dicts, each with
            ``expected_treatment`` and ``match`` keys.

    Returns:
        Dict mapping treatment name → accuracy (float 0–1).
    """
    from collections import defaultdict

    totals: dict[str, int] = defaultdict(int)
    correct: dict[str, int] = defaultdict(int)
    for r in results:
        method = r.get("expected_treatment", "")
        totals[method] += 1
        if r.get("match"):
            correct[method] += 1
    return {
        method: correct[method] / totals[method]
        for method in totals
        if totals[method] > 0
    }


def _check_thresholds(
    overall: float,
    per_language: dict[str, float],
    per_method: dict[str, float],
    thresholds: dict[str, float],
) -> list[str]:
    """Compare computed accuracies against *thresholds*.

    Args:
        overall: Overall pipeline accuracy.
        per_language: Per-language accuracy dict.
        per_method: Per-processing-method accuracy dict.
        thresholds: Dict mapping category key → minimum required accuracy.

    Returns:
        List of human-readable breach descriptions (empty if all pass).
    """
    breaches: list[str] = []

    if "overall" in thresholds:
        if overall < thresholds["overall"]:
            breaches.append(
                f"overall accuracy {overall:.1%} < threshold {thresholds['overall']:.1%}"
            )

    for lang, acc in per_language.items():
        if lang in thresholds and acc < thresholds[lang]:
            breaches.append(
                f"language '{lang}' accuracy {acc:.1%} < threshold {thresholds[lang]:.1%}"
            )

    for method, acc in per_method.items():
        if method in thresholds and acc < thresholds[method]:
            breaches.append(
                f"method '{method}' accuracy {acc:.1%} < threshold {thresholds[method]:.1%}"
            )

    return breaches


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def run_regression_gate(
    results: list[dict],
    golden_dataset_path: str,
    thresholds: dict = ACCURACY_THRESHOLDS,
    strict: bool = True,
) -> dict:
    """Run the full regression gate against *results*.

    Computes overall, per-language, and per-method accuracy then compares them
    against ``thresholds``.  In strict mode a ``RegressionGateFailure`` is raised
    if any threshold is breached; otherwise the report is returned with
    ``passed=False``.

    Args:
        results: List of per-case result dicts from ``run_evaluation()``.
            Each dict must have ``language``, ``expected_treatment``, and
            ``match`` keys.
        golden_dataset_path: Path to the golden dataset CSV (used for metadata
            only — the evaluation has already been run).
        thresholds: Accuracy threshold dict.  Defaults to
            ``ACCURACY_THRESHOLDS``.
        strict: If ``True`` (default), raise ``RegressionGateFailure`` when any
            threshold is breached.  If ``False``, return the report dict without
            raising.

    Returns:
        Report dict with keys:
        * ``passed`` (bool)
        * ``overall_accuracy`` (float)
        * ``per_language`` (dict[str, float])
        * ``per_method`` (dict[str, float])
        * ``breaches`` (list[str])
        * ``timestamp`` (str, ISO 8601)
        * ``total_cases`` (int)
        * ``passed_cases`` (int)

    Raises:
        RegressionGateFailure: When ``strict=True`` and at least one threshold
            is breached.  The exception's ``.report`` attribute contains the
            full report dict.
    """
    total = len(results)
    passed_cases = sum(1 for r in results if r.get("match"))
    overall = passed_cases / total if total else 0.0

    per_language = _compute_per_language(results)
    per_method = _compute_per_method(results)
    breaches = _check_thresholds(overall, per_language, per_method, thresholds)

    report: dict = {
        "passed": len(breaches) == 0,
        "overall_accuracy": overall,
        "per_language": per_language,
        "per_method": per_method,
        "breaches": breaches,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_cases": total,
        "passed_cases": passed_cases,
    }

    if strict and breaches:
        breach_summary = "; ".join(breaches)
        raise RegressionGateFailure(
            f"Regression gate failed: {breach_summary}",
            report=report,
        )

    return report


def save_regression_report(report: dict, output_dir: str = "data/output") -> str:
    """Save *report* as a JSON file in *output_dir*.

    The file is named ``regression_report_{timestamp}.json`` where timestamp
    is taken from ``report["timestamp"]``.

    Args:
        report: The regression report dict returned by ``run_regression_gate()``.
        output_dir: Directory path (relative to cwd or absolute).  Created if it
            does not exist.

    Returns:
        Absolute path to the saved file as a string.
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    ts = report["timestamp"].replace(":", "").replace("-", "").replace("+", "")
    filename = f"regression_report_{ts}.json"
    path = out / filename
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
    return str(path.resolve())
