#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN = ROOT / "server_outputs" / "streamed_fullfield_20260511_205252"
DEFAULT_V9 = DEFAULT_RUN / "soltrace_v9_confirm_highsample_20260512"
DEFAULT_V10 = DEFAULT_RUN / "soltrace_v10_seed_replicate_20260513"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare V9 and V10 high-sample reduced SolTrace matrices as an independent-seed stability audit."
    )
    parser.add_argument("--v9", type=Path, default=DEFAULT_V9)
    parser.add_argument("--v10", type=Path, default=DEFAULT_V10)
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
        str(value)
        .replace("staggered_levels:9:0.380:", "S9-p")
        .replace("visible_equator", "visible")
        .replace("five_point", "five-point")
    )


def short_layout(value: str) -> str:
    return str(value).replace("baseline_full", "baseline").replace("deform_", "D")


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


def matrix_stats(relative: pd.DataFrame, summary: pd.DataFrame, label: str) -> dict[str, object]:
    return {
        "matrix": label,
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


def make_best_comparison(v9_summary: pd.DataFrame, v10_summary: pd.DataFrame) -> pd.DataFrame:
    v9_best = best_rows(v9_summary)
    v10_best = best_rows(v10_summary)
    rows: list[dict[str, object]] = []
    for layout_id in sorted(set(v9_best["layout_id"]) | set(v10_best["layout_id"])):
        row: dict[str, object] = {"layout_id": layout_id}
        b9 = v9_best[v9_best["layout_id"] == layout_id]
        b10 = v10_best[v10_best["layout_id"] == layout_id]
        if not b9.empty:
            r = b9.iloc[0]
            row.update(
                {
                    "v9_best_strategy": r["strategy"],
                    "v9_best_mean_delta_pct": float(r["mean_delta_peak_pct"]),
                    "v9_best_median_delta_pct": float(r["median_delta_peak_pct"]),
                    "v9_best_lower_frac": float(r["share_lower_peak"]),
                }
            )
            same = v10_summary[
                (v10_summary["layout_id"] == layout_id) & (v10_summary["strategy"] == r["strategy"])
            ]
            if not same.empty:
                sr = same.iloc[0]
                row.update(
                    {
                        "v10_same_strategy_mean_delta_pct": float(sr["mean_delta_peak_pct"]),
                        "v10_same_strategy_median_delta_pct": float(sr["median_delta_peak_pct"]),
                        "v10_same_strategy_lower_frac": float(sr["share_lower_peak"]),
                    }
                )
        if not b10.empty:
            r = b10.iloc[0]
            row.update(
                {
                    "v10_best_strategy": r["strategy"],
                    "v10_best_mean_delta_pct": float(r["mean_delta_peak_pct"]),
                    "v10_best_median_delta_pct": float(r["median_delta_peak_pct"]),
                    "v10_best_lower_frac": float(r["share_lower_peak"]),
                    "v10_best_intercept_median_pctpt": float(r["median_delta_intercept_pctpt"]),
                }
            )
        if "v9_best_strategy" in row and "v10_best_strategy" in row:
            row["same_best_strategy"] = row["v9_best_strategy"] == row["v10_best_strategy"]
            row["best_mean_shift_pct"] = row["v10_best_mean_delta_pct"] - row["v9_best_mean_delta_pct"]
        rows.append(row)
    return pd.DataFrame(rows).sort_values("v10_best_mean_delta_pct")


def make_matched_strategy_comparison(v9_summary: pd.DataFrame, v10_summary: pd.DataFrame) -> pd.DataFrame:
    key = ["layout_id", "strategy"]
    cols = key + [
        "cases",
        "mean_delta_peak_pct",
        "median_delta_peak_pct",
        "share_lower_peak",
        "median_delta_intercept_pctpt",
    ]
    merged = v9_summary[cols].merge(
        v10_summary[cols],
        on=key,
        suffixes=("_v9", "_v10"),
        how="inner",
    )
    merged["mean_shift_pct"] = merged["mean_delta_peak_pct_v10"] - merged["mean_delta_peak_pct_v9"]
    merged["median_shift_pct"] = merged["median_delta_peak_pct_v10"] - merged["median_delta_peak_pct_v9"]
    merged["same_mean_sign"] = np.sign(merged["mean_delta_peak_pct_v10"]) == np.sign(
        merged["mean_delta_peak_pct_v9"]
    )
    return merged.sort_values(["layout_id", "mean_delta_peak_pct_v10"])


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


def plot_seed_comparison(best: pd.DataFrame, matched: pd.DataFrame, out: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 4.4), dpi=240)
    layouts = best["layout_id"].tolist()
    labels = [short_layout(v) for v in layouts]
    x = np.arange(len(layouts))
    width = 0.34

    ax = axes[0]
    ax.bar(
        x - width / 2,
        best["v9_best_mean_delta_pct"].astype(float),
        width=width,
        color="#86BBD8",
        label="V9 best mean",
    )
    ax.bar(
        x + width / 2,
        best["v10_best_mean_delta_pct"].astype(float),
        width=width,
        color="#33658A",
        label="V10 best mean",
    )
    ax.axhline(0.0, color="#111827", linewidth=0.8, linestyle="--")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Mean P/M change vs paired baseline (%)")
    ax.set_title("(a) Independent-seed best rows")
    ax.legend(frameon=False)

    ax = axes[1]
    nonbase = matched[matched["layout_id"] != "baseline_full"].copy()
    ax.scatter(
        nonbase["mean_delta_peak_pct_v9"].astype(float),
        nonbase["mean_delta_peak_pct_v10"].astype(float),
        s=46,
        c=np.where(nonbase["same_mean_sign"], "#009E73", "#D55E00"),
        edgecolor="#0F172A",
        linewidth=0.45,
        alpha=0.88,
    )
    lim = float(
        np.nanmax(
            np.abs(
                pd.concat(
                    [nonbase["mean_delta_peak_pct_v9"], nonbase["mean_delta_peak_pct_v10"]],
                    ignore_index=True,
                )
            )
        )
    )
    lim = max(lim, 1.0) * 1.08
    ax.plot([-lim, lim], [-lim, lim], color="#111827", linewidth=0.8, linestyle="--")
    ax.axhline(0.0, color="#6B7280", linewidth=0.6)
    ax.axvline(0.0, color="#6B7280", linewidth=0.6)
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_xlabel("V9 matched-strategy mean change (%)")
    ax.set_ylabel("V10 matched-strategy mean change (%)")
    ax.set_title("(b) Matched strategy stability")

    for ax in axes:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    fig.suptitle("Independent-seed reduced PySolTrace stability audit", y=0.99)
    fig.tight_layout()
    fig.savefig(out / "figures" / "fig_v10_seed_replicate_stability.png", bbox_inches="tight")
    plt.close(fig)


def write_report(best: pd.DataFrame, matched: pd.DataFrame, stats: pd.DataFrame, out: Path) -> None:
    best_out = best.copy()
    for col in ["v9_best_strategy", "v10_best_strategy"]:
        if col in best_out:
            best_out[col] = best_out[col].map(short_strategy)
    matched_out = matched.copy()
    matched_out["strategy"] = matched_out["strategy"].map(short_strategy)
    matched_out = matched_out.loc[
        matched_out["layout_id"] != "baseline_full",
        [
            "layout_id",
            "strategy",
            "mean_delta_peak_pct_v9",
            "mean_delta_peak_pct_v10",
            "mean_shift_pct",
            "median_shift_pct",
            "same_mean_sign",
        ],
    ].sort_values("mean_delta_peak_pct_v10")

    report = [
        "# V10 Independent-Seed Stability Audit",
        "",
        "This report compares the V9 high-sample reduced PySolTrace matrix with an independent-seed V10 replicate using the same layouts, solar conditions, strategies, sampled-field size, receiver discretization, and requested ray count. It is a robustness audit for the reduced-check layer, not a final annual full-field certification.",
        "",
        "## Matrix Scale",
        "",
        markdown_table(stats, floatfmt=".3f"),
        "",
        "## Best-Row Comparison",
        "",
        markdown_table(best_out, floatfmt=".3f"),
        "",
        "## Matched-Strategy Stability",
        "",
        markdown_table(matched_out, floatfmt=".3f"),
        "",
        "## Interpretation Rule",
        "",
        "If V9 and V10 preserve the same receiver-risk candidate queue but disagree on individual aiming phases, the manuscript should keep the present conservative claim boundary: robust candidate roles are defensible, exact reduced-SolTrace aiming phases are not final design prescriptions.",
        "",
    ]
    (out / "V10_SEED_REPLICATE_STABILITY_REPORT.md").write_text("\n".join(report), encoding="utf-8")


def main() -> int:
    args = parse_args()
    v9 = resolve(args.v9)
    v10 = resolve(args.v10)
    out = args.out or (v10 / "publication_v10_seed_replicate")
    out = resolve(out)
    (out / "tables").mkdir(parents=True, exist_ok=True)
    (out / "figures").mkdir(parents=True, exist_ok=True)

    set_style()
    v9_summary = load_summary(v9)
    v10_summary = load_summary(v10)
    v9_rel = load_relative(v9)
    v10_rel = load_relative(v10)

    stats = pd.DataFrame(
        [
            matrix_stats(v9_rel, v9_summary, "V9"),
            matrix_stats(v10_rel, v10_summary, "V10"),
        ]
    )
    best = make_best_comparison(v9_summary, v10_summary)
    matched = make_matched_strategy_comparison(v9_summary, v10_summary)

    stats.to_csv(out / "tables" / "v9_v10_matrix_stats.csv", index=False)
    best.to_csv(out / "tables" / "v9_v10_best_row_comparison.csv", index=False)
    matched.to_csv(out / "tables" / "v9_v10_matched_strategy_comparison.csv", index=False)
    plot_seed_comparison(best, matched, out)
    write_report(best, matched, stats, out)
    print(f"Wrote V10 seed-replicate stability report to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
