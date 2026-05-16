#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN = ROOT / "server_outputs" / "streamed_fullfield_20260511_205252"
DEFAULT_V8 = DEFAULT_RUN / "soltrace_allphase_27cond_20260512"
DEFAULT_V9 = DEFAULT_RUN / "soltrace_v9_confirm_highsample_20260512"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare the V8 all-phase reduced SolTrace matrix with the V9 high-sample confirmation matrix."
    )
    parser.add_argument("--v8", type=Path, default=DEFAULT_V8)
    parser.add_argument("--v9", type=Path, default=DEFAULT_V9)
    parser.add_argument("--out", type=Path, default=None)
    return parser.parse_args()


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def set_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
            "font.weight": "normal",
            "font.size": 8.8,
            "axes.titlesize": 9.8,
            "axes.titleweight": "normal",
            "axes.labelsize": 8.8,
            "xtick.labelsize": 7.8,
            "ytick.labelsize": 7.8,
            "legend.fontsize": 7.6,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
            "axes.grid": True,
            "grid.color": "#D1D5DB",
            "grid.alpha": 0.55,
            "grid.linewidth": 0.55,
            "axes.edgecolor": "#374151",
            "axes.linewidth": 0.7,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def short_strategy(value: str) -> str:
    return (
        value.replace("staggered_levels:9:0.380:", "S9-p")
        .replace("visible_equator", "visible")
        .replace("five_point", "five-point")
    )


def short_layout(value: str) -> str:
    return value.replace("baseline_full", "baseline").replace("deform_", "D")


def load_summary(matrix: Path) -> pd.DataFrame:
    path = matrix / "tables" / "soltrace_sensitivity_summary.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing summary table: {path}")
    return pd.read_csv(path)


def load_relative(matrix: Path) -> pd.DataFrame:
    path = matrix / "tables" / "soltrace_sensitivity_relative.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing relative table: {path}")
    return pd.read_csv(path)


def best_rows(summary: pd.DataFrame) -> pd.DataFrame:
    nonbase = summary[summary["layout_id"] != "baseline_full"].copy()
    return (
        nonbase.sort_values(["mean_delta_peak_pct", "median_delta_peak_pct"])
        .groupby("layout_id", as_index=False)
        .head(1)
        .sort_values("mean_delta_peak_pct")
        .reset_index(drop=True)
    )


def make_comparison(v8_summary: pd.DataFrame, v9_summary: pd.DataFrame) -> pd.DataFrame:
    v8_best = best_rows(v8_summary)
    v9_best = best_rows(v9_summary)
    rows = []
    for layout_id in sorted(set(v8_best["layout_id"]) | set(v9_best["layout_id"])):
        row: dict[str, object] = {"layout_id": layout_id}
        b8 = v8_best[v8_best["layout_id"] == layout_id]
        b9 = v9_best[v9_best["layout_id"] == layout_id]
        if not b8.empty:
            r = b8.iloc[0]
            row.update(
                {
                    "v8_best_strategy": r["strategy"],
                    "v8_best_mean_delta_pct": float(r["mean_delta_peak_pct"]),
                    "v8_best_median_delta_pct": float(r["median_delta_peak_pct"]),
                    "v8_best_lower_frac": float(r["share_lower_peak"]),
                }
            )
            same = v9_summary[
                (v9_summary["layout_id"] == layout_id) & (v9_summary["strategy"] == r["strategy"])
            ]
            if not same.empty:
                sr = same.iloc[0]
                row.update(
                    {
                        "v9_same_strategy_mean_delta_pct": float(sr["mean_delta_peak_pct"]),
                        "v9_same_strategy_median_delta_pct": float(sr["median_delta_peak_pct"]),
                        "v9_same_strategy_lower_frac": float(sr["share_lower_peak"]),
                    }
                )
        if not b9.empty:
            r = b9.iloc[0]
            row.update(
                {
                    "v9_best_strategy": r["strategy"],
                    "v9_best_mean_delta_pct": float(r["mean_delta_peak_pct"]),
                    "v9_best_median_delta_pct": float(r["median_delta_peak_pct"]),
                    "v9_best_lower_frac": float(r["share_lower_peak"]),
                    "v9_best_intercept_median_pctpt": float(r["median_delta_intercept_pctpt"]),
                }
            )
        if "v8_best_strategy" in row and "v9_best_strategy" in row:
            row["same_best_strategy"] = row["v8_best_strategy"] == row["v9_best_strategy"]
        rows.append(row)
    out = pd.DataFrame(rows)
    if "v9_best_mean_delta_pct" in out:
        out = out.sort_values("v9_best_mean_delta_pct")
    return out


def matrix_stats(relative: pd.DataFrame, summary: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "relative_rows": int(len(relative)),
                "layouts": int(relative["layout_id"].nunique()),
                "strategies": int(relative["strategy"].nunique()),
                "conditions": int(relative["condition_id"].nunique()),
                "summary_rows": int(len(summary)),
                "intercept_min": float(relative["receiver_intercept_per_requested_ray"].min()),
                "intercept_max": float(relative["receiver_intercept_per_requested_ray"].max()),
                "mean_elapsed_s": float(relative["elapsed_s"].mean()) if "elapsed_s" in relative else float("nan"),
                "max_elapsed_s": float(relative["elapsed_s"].max()) if "elapsed_s" in relative else float("nan"),
            }
        ]
    )


def markdown_table(df: pd.DataFrame, floatfmt: str = ".3f") -> str:
    if df.empty:
        return "_No rows available._"
    lines = [
        "| " + " | ".join(df.columns) + " |",
        "| " + " | ".join(["---"] * len(df.columns)) + " |",
    ]
    for row in df.itertuples(index=False):
        cells = []
        for value in row:
            if isinstance(value, (float, np.floating)):
                cells.append(format(float(value), floatfmt))
            else:
                cells.append(str(value))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def plot_comparison(compare: pd.DataFrame, out: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.4), dpi=240)
    layouts = compare["layout_id"].tolist()
    labels = [short_layout(v) for v in layouts]
    x = np.arange(len(layouts))
    width = 0.34

    ax = axes[0]
    ax.bar(
        x - width / 2,
        compare["v8_best_mean_delta_pct"].astype(float),
        width=width,
        color="#7BAFD4",
        label="V8 best mean",
    )
    ax.bar(
        x + width / 2,
        compare["v9_best_mean_delta_pct"].astype(float),
        width=width,
        color="#1F77B4",
        label="V9 best mean",
    )
    ax.axhline(0.0, color="#111827", linewidth=0.8, linestyle="--")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Mean P/M change vs paired baseline (%)")
    ax.set_title("(a) Best-row mean change")
    ax.legend(frameon=False)

    ax = axes[1]
    ax.scatter(
        compare["v9_best_mean_delta_pct"].astype(float),
        compare["v9_best_median_delta_pct"].astype(float),
        s=72,
        color="#009E73",
        edgecolor="#0F172A",
        linewidth=0.6,
    )
    for row in compare.itertuples(index=False):
        ax.annotate(short_layout(row.layout_id), (row.v9_best_mean_delta_pct, row.v9_best_median_delta_pct), xytext=(4, 4), textcoords="offset points")
    ax.axhline(0.0, color="#111827", linewidth=0.8, linestyle="--")
    ax.axvline(0.0, color="#111827", linewidth=0.8, linestyle="--")
    ax.set_xlabel("V9 mean P/M change (%)")
    ax.set_ylabel("V9 median P/M change (%)")
    ax.set_title("(b) V9 mean-median consistency")

    for ax in axes:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    fig.suptitle("High-sample reduced PySolTrace confirmation", y=0.99)
    fig.tight_layout()
    fig.savefig(out / "figures" / "fig_v9_highsample_confirmation.png", bbox_inches="tight")
    plt.close(fig)


def write_report(compare: pd.DataFrame, v9_best: pd.DataFrame, stats: pd.DataFrame, out: Path) -> None:
    keep_compare = [
        "layout_id",
        "v8_best_strategy",
        "v8_best_mean_delta_pct",
        "v9_same_strategy_mean_delta_pct",
        "v9_best_strategy",
        "v9_best_mean_delta_pct",
        "v9_best_median_delta_pct",
        "v9_best_lower_frac",
        "v9_best_intercept_median_pctpt",
        "same_best_strategy",
    ]
    compare_out = compare.loc[:, [col for col in keep_compare if col in compare.columns]].copy()
    for col in ["v8_best_strategy", "v9_best_strategy"]:
        if col in compare_out:
            compare_out[col] = compare_out[col].map(short_strategy)
    best_out = v9_best.loc[
        :,
        [
            "layout_id",
            "strategy",
            "cases",
            "mean_delta_peak_pct",
            "median_delta_peak_pct",
            "share_lower_peak",
            "median_delta_intercept_pctpt",
        ],
    ].copy()
    best_out["strategy"] = best_out["strategy"].map(short_strategy)
    report = [
        "# V9 High-Sample Confirmation Report",
        "",
        "This report compares V8 all-phase reduced PySolTrace results with the V9 higher-sample confirmation matrix. V9 is used as a robustness check, not as a final annual custom-aimpoint certification.",
        "",
        "## V9 Matrix Scale",
        "",
        markdown_table(stats, floatfmt=".3f"),
        "",
        "## V8/V9 Best-Row Comparison",
        "",
        markdown_table(compare_out, floatfmt=".3f"),
        "",
        "## V9 Best Direct Rows",
        "",
        markdown_table(best_out, floatfmt=".3f"),
        "",
        "## Claim Boundary",
        "",
        "Use these results only to support or weaken the reduced direct-check evidence. If the V9 best strategies differ from V8, interpret the difference as sampling/discretization sensitivity at the reduced-check layer rather than as a final plant redesign or annual full-field custom-aimpoint performance.",
        "",
    ]
    (out / "V9_HIGHSAMPLE_CONFIRMATION_REPORT.md").write_text("\n".join(report), encoding="utf-8")


def main() -> int:
    args = parse_args()
    v8 = resolve(args.v8)
    v9 = resolve(args.v9)
    out = args.out or (v9 / "publication_v9_confirmation")
    out = resolve(out)
    (out / "tables").mkdir(parents=True, exist_ok=True)
    (out / "figures").mkdir(parents=True, exist_ok=True)

    set_style()
    v8_summary = load_summary(v8)
    v9_summary = load_summary(v9)
    v9_rel = load_relative(v9)
    v9_best = best_rows(v9_summary)
    compare = make_comparison(v8_summary, v9_summary)
    stats = matrix_stats(v9_rel, v9_summary)
    compare.to_csv(out / "tables" / "v8_v9_best_strategy_comparison.csv", index=False)
    v9_best.to_csv(out / "tables" / "v9_best_strategy_by_layout.csv", index=False)
    v9_rel.to_csv(out / "tables" / "v9_condition_level_relative.csv", index=False)
    stats.to_csv(out / "tables" / "v9_matrix_stats.csv", index=False)
    plot_comparison(compare, out)
    write_report(compare, v9_best, stats, out)
    print(f"Wrote V9 confirmation report to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
