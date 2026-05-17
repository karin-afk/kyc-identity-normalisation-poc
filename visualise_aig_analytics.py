import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


ROOT = Path(__file__).resolve().parent
AIG_DIR = ROOT / "reports" / "aig"
CHARTS_DIR = AIG_DIR / "charts"


COLORS = {
    "ink": "#12263A",
    "muted": "#5C6B73",
    "pass": "#2E8B57",
    "fail": "#D1495B",
    "error": "#F4A259",
    "accent": "#2A9D8F",
    "accent2": "#E9C46A",
    "accent3": "#457B9D",
    "bg": "#FFFFFF",
}

FAILURE_LABELS = {
    "phase_2_scope": "Phase 2 Scope",
    "classifier_edge_case": "Classifier Edge Case",
    "llm_nondeterminism": "LLM Non-Determinism",
    "genuine_bug": "Genuine Bug",
}


def setup_style() -> None:
    sns.set_theme(style="white", context="talk")
    plt.rcParams.update(
        {
            "figure.facecolor": COLORS["bg"],
            "axes.facecolor": COLORS["bg"],
            "savefig.facecolor": COLORS["bg"],
            "axes.edgecolor": "#D8DEE3",
            "axes.labelcolor": COLORS["ink"],
            "xtick.color": COLORS["ink"],
            "ytick.color": COLORS["ink"],
            "text.color": COLORS["ink"],
            "font.size": 11,
            "axes.titleweight": "bold",
            "axes.titlesize": 14,
            "axes.labelsize": 11,
            "legend.frameon": False,
            "legend.fontsize": 10,
        }
    )


def save_figure(fig: plt.Figure, name: str) -> Path:
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    out = CHARTS_DIR / name
    fig.tight_layout()
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return out


def read_csv(name: str) -> pd.DataFrame:
    path = AIG_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Missing required CSV: {path}")
    return pd.read_csv(path)


def normalise_bool(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.lower().isin(["true", "1", "yes", "y"]) 


def pct_text(value: float) -> str:
    return f"{value * 100:.1f}%"


def chart_test_suite_summary() -> Path:
    df = read_csv("test_suite_health.csv").copy()
    for col in ["passed", "failed", "errors"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df = df.sort_values("passed", ascending=True)

    fig, ax = plt.subplots(figsize=(12, max(6, 0.45 * len(df))))
    y = np.arange(len(df))
    ax.barh(y, df["passed"], color=COLORS["pass"], label="Passed")
    ax.barh(y, df["failed"], left=df["passed"], color=COLORS["fail"], label="Failed")
    ax.barh(
        y,
        df["errors"],
        left=df["passed"] + df["failed"],
        color=COLORS["error"],
        label="Errors",
    )

    ax.set_yticks(y)
    ax.set_yticklabels(df["test_file"])
    ax.set_xlabel("Test Count")
    ax.set_title(f"Test Suite Summary ({int(df[['passed','failed','errors']].sum().sum())} outcomes)")
    ax.legend(loc="lower right")
    ax.grid(False)

    return save_figure(fig, "test_suite_summary.png")


def _bar_pass_rate(
    csv_name: str,
    key_col: str,
    title: str,
    filename: str,
    count_col: str = "total",
) -> Path:
    df = read_csv(csv_name).copy()
    df["pass_rate"] = pd.to_numeric(df["pass_rate"], errors="coerce").fillna(0)
    df[count_col] = pd.to_numeric(df[count_col], errors="coerce").fillna(0)
    df = df.sort_values("pass_rate", ascending=True)

    fig, ax = plt.subplots(figsize=(11, max(6, 0.35 * len(df))))
    ax.barh(df[key_col], df["pass_rate"], color=COLORS["accent3"])
    ax.set_xlim(0, 1.0)
    ax.set_xlabel("Pass Rate")
    ax.set_title(f"{title} ({int(df[count_col].sum())} tests)")
    ax.grid(False)

    for i, row in enumerate(df.itertuples(index=False)):
        ax.text(
            min(row.pass_rate + 0.01, 0.98),
            i,
            f"{row.pass_rate * 100:.1f}% (n={int(getattr(row, count_col))})",
            va="center",
            fontsize=9,
            color=COLORS["muted"],
        )

    return save_figure(fig, filename)


def chart_failure_categorisation() -> Path:
    df = read_csv("diagnostic_failures.csv").copy()
    if df.empty:
        values = pd.Series([1], index=["No Failures"]) 
    else:
        values = df["failure_category"].map(FAILURE_LABELS).fillna(df["failure_category"]).value_counts()

    fig, ax = plt.subplots(figsize=(8, 8))
    palette = [COLORS["accent"], COLORS["accent2"], COLORS["accent3"], COLORS["fail"]]
    wedges, _texts, _autotexts = ax.pie(
        values.values,
        labels=values.index,
        autopct="%1.1f%%",
        startangle=90,
        colors=palette[: len(values)],
        wedgeprops={"width": 0.45, "edgecolor": "white"},
        textprops={"color": COLORS["ink"], "fontsize": 10},
    )
    ax.add_artist(plt.Circle((0, 0), 0.35, color="white"))
    ax.set_title(f"Failure Categorisation ({int(values.sum())} failures)")
    ax.legend(wedges, values.index, loc="center left", bbox_to_anchor=(1.0, 0.5))

    return save_figure(fig, "failure_categorisation.png")


def chart_confidence_distribution() -> Path:
    df = read_csv("diagnostic_confidence.csv").copy()
    df["classification_confidence"] = pd.to_numeric(df["classification_confidence"], errors="coerce").fillna(0)
    df["passed"] = normalise_bool(df["passed"])

    pass_vals = df.loc[df["passed"], "classification_confidence"]
    fail_vals = df.loc[~df["passed"], "classification_confidence"]

    fig, ax = plt.subplots(figsize=(10, 6))
    bins = np.linspace(0, 1, 21)
    ax.hist(pass_vals, bins=bins, alpha=0.7, color=COLORS["pass"], label=f"Passing (n={len(pass_vals)})")
    ax.hist(fail_vals, bins=bins, alpha=0.7, color=COLORS["fail"], label=f"Failing (n={len(fail_vals)})")
    ax.set_xlabel("Classification Confidence")
    ax.set_ylabel("Count")
    ax.set_title(f"Confidence Distribution ({len(df)} tests)")
    ax.legend(loc="upper left")
    ax.grid(False)

    return save_figure(fig, "confidence_distribution.png")


def chart_classification_accuracy() -> Path:
    df = read_csv("diagnostic_classification_accuracy.csv").copy()
    df["field_type_match"] = normalise_bool(df["field_type_match"])
    df["language_match"] = normalise_bool(df["language_match"])

    metrics = pd.DataFrame(
        {
            "Metric": ["Field Type Match", "Language Match"],
            "Rate": [df["field_type_match"].mean(), df["language_match"].mean()],
        }
    )

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(metrics["Metric"], metrics["Rate"], color=[COLORS["accent3"], COLORS["accent"]])
    ax.set_ylim(0, 1.0)
    ax.set_ylabel("Accuracy Rate")
    ax.set_title(f"Classification Accuracy ({len(df)} tests)")
    ax.grid(False)

    for b, r in zip(bars, metrics["Rate"]):
        ax.text(b.get_x() + b.get_width() / 2, r + 0.02, pct_text(float(r)), ha="center", fontsize=10)

    return save_figure(fig, "classification_accuracy.png")


def chart_review_rate_by_language() -> Path:
    df = read_csv("diagnostic_review_rate.csv").copy()
    for col in ["total", "review_required_count"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    lang = df.groupby("language", as_index=False)[["total", "review_required_count"]].sum()
    lang["review_rate"] = np.where(lang["total"] > 0, lang["review_required_count"] / lang["total"], 0.0)
    lang = lang.sort_values("review_rate", ascending=False)

    fig, ax = plt.subplots(figsize=(13, 6))
    ax.bar(lang["language"], lang["review_rate"], color=COLORS["accent2"])
    ax.set_ylim(0, 1.0)
    ax.set_ylabel("Review Required Rate")
    ax.set_xlabel("Language")
    ax.set_title(f"Review Required Rate by Language ({int(lang['total'].sum())} tests)")
    ax.grid(False)
    plt.setp(ax.get_xticklabels(), rotation=25, ha="right")

    for idx, (_, row) in enumerate(lang.iterrows()):
        ax.text(idx, row["review_rate"] + 0.02, pct_text(float(row["review_rate"])), ha="center", fontsize=9)

    return save_figure(fig, "review_rate_by_language.png")


def chart_latency_by_method() -> Path:
    df = read_csv("diagnostic_latency.csv").copy()
    df["total_latency_s"] = pd.to_numeric(df["total_latency_s"], errors="coerce")
    df = df.dropna(subset=["method", "total_latency_s"])

    order = (
        df.groupby("method", as_index=False)["total_latency_s"]
        .median()
        .sort_values("total_latency_s", ascending=True)["method"]
        .tolist()
    )

    fig, ax = plt.subplots(figsize=(11, 6))
    sns.boxplot(
        data=df,
        x="method",
        y="total_latency_s",
        order=order,
        color=COLORS["accent3"],
        fliersize=2,
        linewidth=1,
        ax=ax,
    )
    ax.set_xlabel("Method")
    ax.set_ylabel("Latency (seconds)")
    ax.set_title(f"Latency by Method ({len(df)} tests)")
    ax.grid(False)
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

    return save_figure(fig, "latency_by_method.png")


def chart_coverage_heatmap() -> Path:
    df = read_csv("coverage_matrix.csv").copy()
    for col in ["count", "pass_rate"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    rate_pivot = df.pivot(index="language", columns="field_type", values="pass_rate").fillna(0)
    count_pivot = df.pivot(index="language", columns="field_type", values="count").fillna(0).astype(int)

    annot = count_pivot.astype(str)
    fig_w = max(11, 0.42 * rate_pivot.shape[1] + 4)
    fig_h = max(7, 0.32 * rate_pivot.shape[0] + 2)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    sns.heatmap(
        rate_pivot,
        cmap=sns.color_palette(["#D1495B", "#F4A259", "#E9C46A", "#2A9D8F", "#2E8B57"], as_cmap=True),
        vmin=0,
        vmax=1,
        annot=annot,
        fmt="",
        cbar_kws={"label": "Pass Rate"},
        linewidths=0.3,
        linecolor="#F1F3F5",
        ax=ax,
    )
    ax.set_title(f"Coverage Heatmap (counts annotated, n={int(df['count'].sum())})")
    ax.set_xlabel("Field Type")
    ax.set_ylabel("Language")

    return save_figure(fig, "coverage_heatmap.png")


def chart_variant_generation() -> Path:
    df = read_csv("variant_stats.csv").copy()
    df["variant_count"] = pd.to_numeric(df["variant_count"], errors="coerce").fillna(0)

    agg = (
        df.groupby("language", as_index=False)["variant_count"]
        .mean()
        .sort_values("variant_count", ascending=False)
    )

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(agg["language"], agg["variant_count"], color=COLORS["accent"]) 
    ax.set_ylabel("Average Variants per Name")
    ax.set_xlabel("Language")
    ax.set_title(f"Variant Generation by Language (n={len(df)} names)")
    ax.grid(False)

    for idx, (_, row) in enumerate(agg.iterrows()):
        ax.text(idx, row["variant_count"] + 0.02, f"{row['variant_count']:.2f}", ha="center", fontsize=9)

    return save_figure(fig, "variant_generation.png")


def chart_cost_per_field() -> Path:
    df = read_csv("cost_estimates.csv").copy()
    df["avg_cost_per_field_usd"] = pd.to_numeric(df["avg_cost_per_field_usd"], errors="coerce").fillna(0)

    df = df.sort_values("avg_cost_per_field_usd", ascending=False)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(df["method"], df["avg_cost_per_field_usd"], color=[COLORS["accent3"], COLORS["accent2"], COLORS["accent"]])
    ax.set_ylabel("USD per Field")
    ax.set_xlabel("Method")
    ax.set_title("Cost per Field by Method")
    ax.grid(False)

    for idx, (_, row) in enumerate(df.iterrows()):
        ax.text(idx, row["avg_cost_per_field_usd"] * 1.02 + 1e-8, f"${row['avg_cost_per_field_usd']:.6f}", ha="center", fontsize=9)

    return save_figure(fig, "cost_per_field.png")


def chart_nondeterminism_rate() -> Path:
    df = read_csv("nondeterminism.csv").copy()
    df["stable"] = normalise_bool(df["stable"])

    total = len(df)
    unstable = int((~df["stable"]).sum())
    flip_rate = (unstable / total) if total else 0.0

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(["Flip Rate"], [flip_rate], color=COLORS["fail"], width=0.5)
    ax.set_ylim(0, 1.0)
    ax.set_ylabel("Rate")
    ax.set_title(f"LLM Non-Determinism Rate ({unstable}/{total} tests flipped)")
    ax.grid(False)
    ax.text(0, flip_rate + 0.03, pct_text(flip_rate), ha="center", fontsize=12, weight="bold")

    return save_figure(fig, "nondeterminism_rate.png")


def chart_throughput_by_method() -> Path:
    df = read_csv("throughput.csv").copy()
    df["estimated_fields_per_minute"] = pd.to_numeric(df["estimated_fields_per_minute"], errors="coerce").fillna(0)
    df = df.sort_values("estimated_fields_per_minute", ascending=False)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(df["method"], df["estimated_fields_per_minute"], color=COLORS["accent3"]) 
    ax.set_ylabel("Fields per Minute")
    ax.set_xlabel("Method")
    ax.set_title("Throughput by Method")
    ax.grid(False)
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

    for i, row in df.iterrows():
        ax.text(i, row["estimated_fields_per_minute"] + 0.7, f"{row['estimated_fields_per_minute']:.1f}", ha="center", fontsize=9)

    return save_figure(fig, "throughput_by_method.png")


def main() -> int:
    setup_style()

    created: list[Path] = []
    created.append(chart_test_suite_summary())

    created.append(
        _bar_pass_rate(
            csv_name="diagnostic_by_language.csv",
            key_col="language",
            title="Pass Rate by Language",
            filename="pass_rate_by_language.png",
        )
    )
    created.append(
        _bar_pass_rate(
            csv_name="diagnostic_by_field_type.csv",
            key_col="field_type",
            title="Pass Rate by Field Type",
            filename="pass_rate_by_field_type.png",
        )
    )
    created.append(
        _bar_pass_rate(
            csv_name="diagnostic_by_method.csv",
            key_col="method",
            title="Pass Rate by Method",
            filename="pass_rate_by_method.png",
        )
    )

    created.append(chart_failure_categorisation())
    created.append(chart_confidence_distribution())
    created.append(chart_classification_accuracy())
    created.append(chart_review_rate_by_language())
    created.append(chart_latency_by_method())

    created.append(chart_coverage_heatmap())
    created.append(chart_variant_generation())

    created.append(chart_cost_per_field())
    created.append(chart_nondeterminism_rate())
    created.append(chart_throughput_by_method())

    print(f"Charts generated: {len(created)}")
    for p in created:
        print(f"- {p}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
