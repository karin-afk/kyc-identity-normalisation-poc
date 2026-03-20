from collections import defaultdict


def accuracy(results: list[dict]) -> float:
    """Fraction of results where match == True."""
    if not results:
        return 0.0
    return sum(1 for r in results if r["match"]) / len(results)


def accuracy_by_language(results: list[dict]) -> dict[str, float]:
    """Per-language accuracy breakdown."""
    by_lang: dict[str, list[bool]] = defaultdict(list)
    for r in results:
        by_lang[r["language"]].append(r["match"])
    return {lang: sum(m) / len(m) for lang, m in sorted(by_lang.items())}


def accuracy_by_treatment(results: list[dict]) -> dict[str, float]:
    """Per-treatment-type accuracy breakdown."""
    by_treatment: dict[str, list[bool]] = defaultdict(list)
    for r in results:
        by_treatment[r["expected_treatment"]].append(r["match"])
    return {t: sum(m) / len(m) for t, m in sorted(by_treatment.items())}


def accuracy_by_language_and_field_type(
    results: list[dict],
) -> dict[str, dict[str, tuple[int, int]]]:
    """Cross-tab of (correct, total) keyed by language then field_type."""
    counts: dict[str, dict[str, list[bool]]] = defaultdict(lambda: defaultdict(list))
    for r in results:
        counts[r["language"]][r["field_type"]].append(r["match"])
    return {
        lang: {ft: (sum(m), len(m)) for ft, m in sorted(ft_map.items())}
        for lang, ft_map in sorted(counts.items())
    }
