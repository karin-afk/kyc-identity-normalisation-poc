import pytest
from evaluation.evaluator import run_evaluation, load_golden_dataset
from evaluation.metrics import accuracy, accuracy_by_language, accuracy_by_treatment


def test_golden_dataset_loads():
    rows = load_golden_dataset()
    assert len(rows) >= 30, f"Expected at least 30 rows, got {len(rows)}"
    assert "original_text" in rows[0]
    assert "expected_normalised" in rows[0]


def test_evaluation_runs_without_error():
    results = run_evaluation()
    expected_count = len(load_golden_dataset())
    assert len(results) == expected_count
    assert all("match" in r for r in results)
    assert all("processing_method" in r for r in results)


def test_accuracy_metric():
    mock = [{"match": True}, {"match": True}, {"match": False}]
    assert accuracy(mock) == pytest.approx(2 / 3)


def test_accuracy_empty():
    assert accuracy([]) == 0.0


def test_preserve_cases_are_100_percent_accurate():
    """PRESERVE fields (passport_no, email, id_no) require perfect accuracy."""
    results = run_evaluation()
    preserve_results = [r for r in results if r["expected_treatment"] == "PRESERVE"]
    assert len(preserve_results) > 0, "Golden dataset must contain PRESERVE cases"
    assert accuracy(preserve_results) == 1.0, (
        f"PRESERVE accuracy should be 100%, got {accuracy(preserve_results):.1%}. "
        f"Failing: {[r['case_id'] for r in preserve_results if not r['match']]}"
    )


def test_accuracy_by_language_keys():
    results = run_evaluation()
    by_lang = accuracy_by_language(results)
    # All languages in the golden dataset should appear
    for lang in ("ar", "el", "en", "ja", "ru", "zh"):
        assert lang in by_lang, f"Language '{lang}' missing from accuracy breakdown"


def test_accuracy_by_treatment_keys():
    results = run_evaluation()
    by_treatment = accuracy_by_treatment(results)
    for treatment in ("PRESERVE", "TRANSLITERATE", "TRANSLATE_NORMALISE"):
        assert treatment in by_treatment
