"""
evaluate_copilot_output.py

Evaluates data/copilot_output.csv against expected values from
data/golden_dataset.csv and data/test_dataset.csv, using the same
multi-pass matching logic as the pipeline evaluator.

Usage:
    python evaluate_copilot_output.py
"""
import csv
import re
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).parent

# ---------------------------------------------------------------------------
# Load datasets
# ---------------------------------------------------------------------------

def _load(path: Path) -> dict[str, dict]:
    with open(path, encoding="utf-8") as fh:
        return {r["case_id"]: r for r in csv.DictReader(fh)}


copilot  = _load(BASE / "data" / "copilot_output.csv")
golden   = _load(BASE / "data" / "golden_dataset.csv")
test_ds  = _load(BASE / "data" / "test_dataset.csv")
expected = {**golden, **test_ds}   # 212 rows; golden takes precedence on overlap

# ---------------------------------------------------------------------------
# Matching helpers  (mirrors src/evaluation/evaluator.py)
# ---------------------------------------------------------------------------

_ARABIC_VARIANT_MAP = {
    "MOHAMMED": "MUHAMMAD", "MOHAMED": "MUHAMMAD", "MOHAMMAD": "MUHAMMAD",
    "MUHAMMED": "MUHAMMAD", "MUHAMAD": "MUHAMMAD",
    "HASAN": "HASSAN", "HUSSEIN": "HUSSAIN", "HUSAIN": "HUSSAIN",
}

def _arabic_canonical(text: str) -> str:
    tokens = re.split(r"[\s\-]+", text.upper())
    out = []
    for tok in tokens:
        tok = re.sub(r"^(AL|EL)-?", "", tok)
        tok = _ARABIC_VARIANT_MAP.get(tok, tok)
        if tok:
            out.append(tok)
    return " ".join(out)


def _address_normalise(text: str) -> str:
    t = re.sub(r"[,\-]", " ", text.upper())
    return re.sub(r"\s+", " ", t).strip()


_LEGAL_SUFFIX_TOKENS = frozenset({
    "LLC", "LTD", "PLC", "INC", "SA", "NV", "BV", "AG", "GMBH",
    "KK", "GK", "OOO", "AO", "JSC", "SPA", "SARL", "SAS", "LP",
    "LLP", "CO", "CORP", "SE", "AS", "AB", "PTY", "SDN", "BHD",
    "PVT", "PJSC", "OAO", "PAO",
})

_SUFFIX_SYNONYMS = {
    "CORPORATION": "CORP", "LIMITED": "LTD",
    "INCORPORATED": "INC", "COMPANY": "CO",
}

def _company_name_normalise(text: str) -> str:
    t = re.sub(r'(?<=[A-Z])\.', '', text.upper())
    t = t.replace(',', ' ')
    tokens = [_SUFFIX_SYNONYMS.get(tok, tok) for tok in t.split()]
    return ' '.join(tokens)

def _company_core(text: str) -> str:
    tokens = _company_name_normalise(text).split()
    while tokens and tokens[-1] in _LEGAL_SUFFIX_TOKENS:
        tokens.pop()
    return ' '.join(tokens)


def match_passes(actual_norm: str, expected_norm: str, copilot_variants: str,
                 dataset_variants: str, language: str, field_type: str) -> tuple[bool, str]:
    """Return (match, pass_name)."""
    actual_up = actual_norm.strip().upper()
    expected_up = expected_norm.strip().upper()

    # Pass 1 — exact
    if actual_up == expected_up:
        return True, "exact"

    # Pass 2 — copilot variant list contains expected
    if copilot_variants:
        cop_vars = [v.strip().upper() for v in copilot_variants.split("|") if v.strip()]
        if expected_up in cop_vars:
            return True, "copilot_variant"

    # Pass 3 — actual is in dataset variant list
    if dataset_variants:
        ds_vars = [v.strip().upper() for v in dataset_variants.split("|") if v.strip()]
        if actual_up in ds_vars:
            return True, "dataset_variant"

    # Pass 4 — Arabic canonical
    if language == "ar":
        actual_can = _arabic_canonical(actual_up)
        if actual_can == _arabic_canonical(expected_up):
            return True, "arabic_canonical"
        if dataset_variants:
            for v in dataset_variants.split("|"):
                if v.strip() and _arabic_canonical(v.strip()) == actual_can:
                    return True, "arabic_canonical_variant"

    # Pass 5 — company lenient
    if field_type == "company_name":
        actual_co = _company_name_normalise(actual_up)
        candidates_co = [_company_name_normalise(expected_up)] + (
            [_company_name_normalise(v) for v in dataset_variants.split("|") if v.strip()]
            if dataset_variants else []
        )
        if actual_co in candidates_co:
            return True, "company_lenient_normalised"
        actual_core = _company_core(actual_up)
        if actual_core:
            all_cands = [expected_up] + ([v.strip() for v in dataset_variants.split("|") if v.strip()] if dataset_variants else [])
            for cand in all_cands:
                if actual_core == _company_core(cand):
                    return True, "company_lenient_core"

    # Pass 6 — address lenient
    if field_type == "address":
        actual_addr = _address_normalise(actual_up)
        candidates_addr = [_address_normalise(expected_up)] + (
            [_address_normalise(v) for v in dataset_variants.split("|") if v.strip()]
            if dataset_variants else []
        )
        if actual_addr in candidates_addr:
            return True, "address_comma_strip"
        actual_tokens = frozenset(actual_addr.split())
        for cand in candidates_addr:
            if frozenset(cand.split()) == actual_tokens:
                return True, "address_token_set"

    return False, "no_match"


# ---------------------------------------------------------------------------
# Run evaluation
# ---------------------------------------------------------------------------

results = []
skipped = []

for case_id, cop_row in sorted(copilot.items()):
    if case_id not in expected:
        skipped.append(case_id)
        continue

    exp_row = expected[case_id]
    actual_norm    = cop_row.get("normalised", "").strip()
    expected_norm  = exp_row.get("expected_normalised", "").strip()
    cop_variants   = cop_row.get("variants", "")
    ds_variants    = exp_row.get("expected_allowed_variants", "")
    language       = exp_row.get("language", "")
    field_type     = exp_row.get("field_type", "")
    treatment      = exp_row.get("expected_treatment", "")
    is_negative    = exp_row.get("is_negative_case", "false").lower() == "true"
    source         = "golden" if case_id in golden else "test"

    matched, pass_name = match_passes(
        actual_norm, expected_norm, cop_variants, ds_variants, language, field_type
    )

    results.append({
        "case_id":    case_id,
        "source":     source,
        "language":   language,
        "field_type": field_type,
        "treatment":  treatment,
        "is_negative": is_negative,
        "expected":   expected_norm,
        "actual":     actual_norm,
        "match":      matched,
        "pass":       pass_name,
    })

# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def pct(ok, n): return ok / n if n else 0.0

total   = len(results)
matched = sum(r["match"] for r in results)
print(f"\nCopilot output evaluation — {total} cases")
print("=" * 60)
print(f"Overall accuracy : {pct(matched,total):.1%}  ({matched}/{total})")

# by source (golden vs test)
print("\nBy source dataset:")
for src in ("golden", "test"):
    sub = [r for r in results if r["source"] == src]
    ok  = sum(r["match"] for r in sub)
    print(f"  {src:6s}  {pct(ok,len(sub)):.1%}  ({ok}/{len(sub)})")

# by language
print("\nBy language:")
langs = sorted({r["language"] for r in results})
lang_stats = {}
for lang in langs:
    sub = [r for r in results if r["language"] == lang]
    ok  = sum(r["match"] for r in sub)
    lang_stats[lang] = (ok, len(sub))
    print(f"  {lang:4s}  {pct(ok,len(sub)):.1%}  ({ok}/{len(sub)})")

# by treatment
print("\nBy treatment:")
treatments = sorted({r["treatment"] for r in results})
treat_stats = {}
for tx in treatments:
    sub = [r for r in results if r["treatment"] == tx]
    ok  = sum(r["match"] for r in sub)
    treat_stats[tx] = (ok, len(sub))
    print(f"  {tx:22s}  {pct(ok,len(sub)):.1%}  ({ok}/{len(sub)})")

# by language x field_type
print("\nBy language × field type:")
lf_stats = defaultdict(lambda: [0, 0])
for r in results:
    key = (r["language"], r["field_type"])
    lf_stats[key][1] += 1
    if r["match"]:
        lf_stats[key][0] += 1
for (lang, ft), (ok, n) in sorted(lf_stats.items()):
    print(f"  {lang:4s}  {ft:20s}  {pct(ok,n):.1%}  ({ok}/{n})")

# failing cases
print("\nFailed cases:")
fails = [r for r in results if not r["match"]]
for r in fails:
    print(f"  {r['case_id']} [{r['language']}] {r['field_type']}: "
          f"expected=\"{r['expected']}\"  got=\"{r['actual']}\"")
print(f"\nTotal failed: {len(fails)}")
if skipped:
    print(f"Skipped (case_id not in datasets): {skipped}")

# ---------------------------------------------------------------------------
# Save CSV
# ---------------------------------------------------------------------------
out_path = BASE / "data" / "output" / "copilot_eval_results.csv"
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, "w", encoding="utf-8", newline="") as fh:
    writer = csv.DictWriter(fh, fieldnames=list(results[0].keys()))
    writer.writeheader()
    writer.writerows(results)
print(f"\nDetailed results saved to: {out_path}")
