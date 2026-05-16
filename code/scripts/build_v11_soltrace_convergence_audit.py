#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN = ROOT / "server_outputs" / "streamed_fullfield_20260511_205252"
DEFAULT_OUT = DEFAULT_RUN / "soltrace_v11_convergence_audit_20260514"

MATRICES = {
    "V8": {
        "dir": DEFAULT_RUN / "soltrace_allphase_27cond_20260512",
        "sampled_heliostats": 6000,
        "rays": 60000,
        "receiver_panels": 18,
        "receiver_grid": "20 x 60",
        "scope": "all 11 S9/visible/five-point strategies",
    },
    "V9": {
        "dir": DEFAULT_RUN / "soltrace_v9_confirm_highsample_20260512",
        "sampled_heliostats": 9000,
        "rays": 180000,
        "receiver_panels": 24,
        "receiver_grid": "24 x 72",
        "scope": "five verification-relevant strategies",
    },
    "V10": {
        "dir": DEFAULT_RUN / "soltrace_v10_seed_replicate_20260513",
        "sampled_heliostats": 9000,
        "rays": 180000,
        "receiver_panels": 24,
        "receiver_grid": "24 x 72",
        "scope": "V9 scale with independent stratified seed",
    },
}

ROLE_MAP = {
    "deform_1387": ("$L_{rob}$", "receiver-risk"),
    "deform_0893": ("$L_{nom}$", "nominal-proxy"),
    "deform_1822": ("$L_{ctrl}$", "default-flux-control"),
    "deform_0276": ("$L_{opt}$", "optical-upper"),
}
LAYOUT_ORDER = ["deform_1387", "deform_0893", "deform_1822", "deform_0276"]
MATRIX_ORDER = ["V8", "V9", "V10"]
PALETTE = {
    "deform_1387": "#0072B2",
    "deform_0893": "#009E73",
    "deform_1822": "#E69F00",
    "deform_0276": "#D55E00",
    "ink": "#0F172A",
    "muted": "#475569",
    "grid": "#CBD5E1",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a consolidated V8/V9/V10 reduced PySolTrace convergence and uncertainty audit."
    )
    parser.add_argument("--run", type=Path, default=DEFAULT_RUN)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def short_strategy(value: str) -> str:
    return (
        str(value)
        .replace("staggered_levels:9:0.380:", "S9-p")
        .replace("visible_equator", "visible")
        .replace("five_point", "five-point")
    )


def role_label(layout_id: str) -> str:
    return ROLE_MAP.get(layout_id, (layout_id, ""))[0]


def role_name(layout_id: str) -> str:
    return ROLE_MAP.get(layout_id, ("", ""))[1]


def load_matrix(matrix: str, directory: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    summary_path = directory / "tables" / "soltrace_sensitivity_summary.csv"
    relative_path = directory / "tables" / "soltrace_sensitivity_relative.csv"
    if not summary_path.exists() or not relative_path.exists():
        raise FileNotFoundError(f"Missing reduced SolTrace tables for {matrix}: {directory}")
    summary = pd.read_csv(summary_path)
    relative = pd.read_csv(relative_path)
    summary["matrix"] = matrix
    relative["matrix"] = matrix
    return summary, relative


def best_rows(summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for matrix in MATRIX_ORDER:
        sub = summary[summary["matrix"] == matrix].copy()
        best = (
            sub.sort_values(["layout_id", "mean_delta_peak_pct", "median_delta_peak_pct"])
            .groupby("layout_id", as_index=False)
            .head(1)
        )
        rows.append(best)
    out = pd.concat(rows, axis=0, ignore_index=True)
    out = out[out["layout_id"].isin(LAYOUT_ORDER)].copy()
    out["role_label"] = out["layout_id"].map(role_label)
    out["role_name"] = out["layout_id"].map(role_name)
    out["strategy_short"] = out["strategy"].map(short_strategy)
    out["layout_rank"] = out["layout_id"].map({layout: i for i, layout in enumerate(LAYOUT_ORDER)})
    out["matrix_rank"] = out["matrix"].map({matrix: i for i, matrix in enumerate(MATRIX_ORDER)})
    out["rank_within_matrix"] = (
        out.sort_values(["matrix", "mean_delta_peak_pct", "median_delta_peak_pct"])
        .groupby("matrix")
        .cumcount()
        + 1
    )
    return out.sort_values(["layout_rank", "matrix_rank"]).reset_index(drop=True)


def matrix_stats(relative: pd.DataFrame, summary: pd.DataFrame) -> pd.DataFrame:
    records = []
    for matrix in MATRIX_ORDER:
        rel = relative[relative["matrix"] == matrix]
        summ = summary[summary["matrix"] == matrix]
        meta = MATRICES[matrix]
        records.append(
            {
                "matrix": matrix,
                "rows": int(len(rel)),
                "layouts": int(rel["layout_id"].nunique()),
                "strategies": int(rel["strategy"].nunique()),
                "conditions": int(rel["condition_id"].nunique()),
                "sampled_heliostats": meta["sampled_heliostats"],
                "ray_hits": meta["rays"],
                "receiver_panels": meta["receiver_panels"],
                "receiver_grid": meta["receiver_grid"],
                "scope": meta["scope"],
                "intercept_min": float(rel["receiver_intercept_per_requested_ray"].min()),
                "intercept_max": float(rel["receiver_intercept_per_requested_ray"].max()),
                "mean_elapsed_s": float(rel["elapsed_s"].mean()),
                "max_elapsed_s": float(rel["elapsed_s"].max()),
                "summary_rows": int(len(summ)),
            }
        )
    return pd.DataFrame.from_records(records)


def best_stability_table(best: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for layout in LAYOUT_ORDER:
        sub = best[best["layout_id"] == layout].sort_values("matrix_rank")
        means = sub["mean_delta_peak_pct"].astype(float)
        rows.append(
            {
                "layout_id": layout,
                "role_label": role_label(layout),
                "role_name": role_name(layout),
                "v8_strategy": sub.loc[sub["matrix"] == "V8", "strategy_short"].iloc[0],
                "v8_mean_delta_pct": float(sub.loc[sub["matrix"] == "V8", "mean_delta_peak_pct"].iloc[0]),
                "v9_strategy": sub.loc[sub["matrix"] == "V9", "strategy_short"].iloc[0],
                "v9_mean_delta_pct": float(sub.loc[sub["matrix"] == "V9", "mean_delta_peak_pct"].iloc[0]),
                "v10_strategy": sub.loc[sub["matrix"] == "V10", "strategy_short"].iloc[0],
                "v10_mean_delta_pct": float(sub.loc[sub["matrix"] == "V10", "mean_delta_peak_pct"].iloc[0]),
                "best_mean_range_pct": float(means.max() - means.min()),
                "always_negative_best_row": bool((means < 0).all()),
            }
        )
    out = pd.DataFrame.from_records(rows)
    out["layout_rank"] = out["layout_id"].map({layout: i for i, layout in enumerate(LAYOUT_ORDER)})
    return out.sort_values("layout_rank").drop(columns=["layout_rank"])


def matched_shift_table(summary: pd.DataFrame, left: str, right: str) -> pd.DataFrame:
    key = ["layout_id", "strategy"]
    cols = key + ["mean_delta_peak_pct", "median_delta_peak_pct", "share_lower_peak"]
    a = summary[summary["matrix"] == left][cols].copy()
    b = summary[summary["matrix"] == right][cols].copy()
    merged = a.merge(b, on=key, suffixes=(f"_{left.lower()}", f"_{right.lower()}"), how="inner")
    merged = merged[merged["layout_id"].isin(LAYOUT_ORDER)].copy()
    merged["strategy_short"] = merged["strategy"].map(short_strategy)
    merged["mean_shift_pct"] = (
        merged[f"mean_delta_peak_pct_{right.lower()}"] - merged[f"mean_delta_peak_pct_{left.lower()}"]
    )
    merged["median_shift_pct"] = (
        merged[f"median_delta_peak_pct_{right.lower()}"] - merged[f"median_delta_peak_pct_{left.lower()}"]
    )
    merged["same_mean_sign"] = np.sign(merged[f"mean_delta_peak_pct_{right.lower()}"]) == np.sign(
        merged[f"mean_delta_peak_pct_{left.lower()}"]
    )
    return merged.sort_values(["layout_id", "strategy_short"])


def shift_summary(v8_v9: pd.DataFrame, v9_v10: pd.DataFrame) -> pd.DataFrame:
    records = []
    for label, df in [("V8_to_V9", v8_v9), ("V9_to_V10", v9_v10)]:
        records.append(
            {
                "comparison": label,
                "matched_rows": int(len(df)),
                "same_mean_sign_rows": int(df["same_mean_sign"].sum()),
                "same_mean_sign_fraction": float(df["same_mean_sign"].mean()),
                "median_abs_mean_shift_pct": float(df["mean_shift_pct"].abs().median()),
                "p90_abs_mean_shift_pct": float(np.percentile(df["mean_shift_pct"].abs(), 90)),
                "max_abs_mean_shift_pct": float(df["mean_shift_pct"].abs().max()),
            }
        )
    return pd.DataFrame.from_records(records)


def set_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
            "font.weight": "normal",
            "font.size": 8.3,
            "axes.titlesize": 9.0,
            "axes.titleweight": "normal",
            "axes.labelsize": 8.2,
            "xtick.labelsize": 7.4,
            "ytick.labelsize": 7.4,
            "legend.fontsize": 7.2,
            "figure.titlesize": 11.0,
            "axes.facecolor": "white",
            "figure.facecolor": "white",
            "savefig.facecolor": "white",
            "axes.edgecolor": "#334155",
            "axes.linewidth": 0.7,
            "axes.grid": True,
            "grid.color": PALETTE["grid"],
            "grid.linewidth": 0.55,
            "grid.alpha": 0.65,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def make_figure(best: pd.DataFrame, v9_v10: pd.DataFrame, out: Path) -> None:
    set_style()
    fig = plt.figure(figsize=(7.35, 5.65), dpi=360)
    gs = fig.add_gridspec(
        2,
        2,
        height_ratios=[1.0, 1.04],
        width_ratios=[1.05, 0.95],
        left=0.09,
        right=0.98,
        top=0.975,
        bottom=0.115,
        hspace=0.76,
        wspace=0.34,
    )
    ax0 = fig.add_subplot(gs[0, 0])
    ax1 = fig.add_subplot(gs[0, 1])
    ax2 = fig.add_subplot(gs[1, :])

    x = np.arange(len(MATRIX_ORDER))
    handles = []
    labels = []
    for layout in LAYOUT_ORDER:
        sub = best[best["layout_id"] == layout].sort_values("matrix_rank")
        y = sub["mean_delta_peak_pct"].to_numpy(dtype=float)
        label = f"{role_label(layout)} {role_name(layout)}"
        (handle,) = ax0.plot(
            x,
            y,
            marker="o",
            linewidth=1.65,
            markersize=4.8,
            color=PALETTE[layout],
            label=label,
        )
        handles.append(handle)
        labels.append(label)
    ax0.axhline(0.0, color=PALETTE["ink"], linewidth=0.8, linestyle="--")
    ax0.set_xticks(x)
    ax0.set_xticklabels(MATRIX_ORDER)
    ax0.set_ylabel("Best-row mean P/M change (%)")
    ax0.set_title("(a) Role-level best rows across audits", loc="left", pad=6)

    rank_grid = np.full((len(LAYOUT_ORDER), len(MATRIX_ORDER)), np.nan)
    for i, layout in enumerate(LAYOUT_ORDER):
        for j, matrix in enumerate(MATRIX_ORDER):
            row = best[(best["layout_id"] == layout) & (best["matrix"] == matrix)].iloc[0]
            rank_grid[i, j] = row["rank_within_matrix"]
    cmap = plt.matplotlib.colors.ListedColormap(["#2166AC", "#67A9CF", "#F4A582", "#B2182B"])
    ax1.imshow(rank_grid, cmap=cmap, vmin=1, vmax=4, aspect="auto")
    ax1.set_xticks(np.arange(len(MATRIX_ORDER)))
    ax1.set_xticklabels(MATRIX_ORDER)
    ax1.set_yticks(np.arange(len(LAYOUT_ORDER)))
    ax1.set_yticklabels([role_label(layout) for layout in LAYOUT_ORDER])
    ax1.grid(False)
    ax1.set_title("(b) Rank within each audit", loc="left", pad=6)
    for i in range(len(LAYOUT_ORDER)):
        for j in range(len(MATRIX_ORDER)):
            ax1.text(j, i, f"{int(rank_grid[i, j])}", ha="center", va="center", color="white")
    for spine in ax1.spines.values():
        spine.set_visible(False)

    rng = np.random.default_rng(20260514)
    for pos, layout in enumerate(LAYOUT_ORDER):
        sub = v9_v10[v9_v10["layout_id"] == layout].copy()
        shifts = sub["mean_shift_pct"].to_numpy(dtype=float)
        ax2.boxplot(
            shifts,
            positions=[pos],
            widths=0.48,
            patch_artist=True,
            showfliers=False,
            boxprops={"facecolor": "#E2E8F0", "edgecolor": "#475569", "linewidth": 0.8},
            medianprops={"color": PALETTE[layout], "linewidth": 1.4},
            whiskerprops={"color": "#64748B", "linewidth": 0.8},
            capprops={"color": "#64748B", "linewidth": 0.8},
        )
        jitter = rng.normal(0.0, 0.045, size=len(sub))
        colors = np.where(sub["same_mean_sign"].to_numpy(dtype=bool), PALETTE[layout], "#B2182B")
        ax2.scatter(
            np.full(len(sub), pos) + jitter,
            shifts,
            s=24,
            color=colors,
            edgecolor="white",
            linewidth=0.45,
            zorder=3,
        )
    ax2.axhline(0.0, color=PALETTE["ink"], linewidth=0.8, linestyle="--")
    ax2.set_xticks(np.arange(len(LAYOUT_ORDER)))
    ax2.set_xticklabels([f"{role_label(layout)}\n{role_name(layout)}" for layout in LAYOUT_ORDER])
    ax2.set_ylabel("V10 - V9 matched-strategy mean shift (%)")
    ax2.set_title("(c) Exact strategy rows remain seed-sensitive", loc="left", pad=6)
    fig.legend(
        handles,
        labels,
        frameon=False,
        ncol=4,
        loc="center",
        bbox_to_anchor=(0.50, 0.505),
        columnspacing=1.3,
        handlelength=1.7,
    )
    fig.savefig(out / "figures" / "fig_v11_soltrace_convergence_audit.png", bbox_inches="tight")
    plt.close(fig)


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


def write_report(
    stats: pd.DataFrame,
    best_stability: pd.DataFrame,
    shift_stats: pd.DataFrame,
    out: Path,
) -> None:
    report_best = best_stability[
        [
            "role_label",
            "role_name",
            "v8_strategy",
            "v8_mean_delta_pct",
            "v9_strategy",
            "v9_mean_delta_pct",
            "v10_strategy",
            "v10_mean_delta_pct",
            "best_mean_range_pct",
            "always_negative_best_row",
        ]
    ].copy()
    report_stats = stats[
        [
            "matrix",
            "rows",
            "strategies",
            "conditions",
            "sampled_heliostats",
            "ray_hits",
            "receiver_panels",
            "receiver_grid",
            "intercept_min",
            "intercept_max",
            "mean_elapsed_s",
        ]
    ].copy()
    lines = [
        "# V11 Reduced PySolTrace Convergence and Uncertainty Audit",
        "",
        "This report consolidates the V8 all-phase matrix, the V9 high-sample confirmation, and the V10 independent-seed replicate. It is a claim-boundary audit for the reduced direct-check layer, not a new plant-design optimization.",
        "",
        "## Matrix scale",
        "",
        markdown_table(report_stats),
        "",
        "## Best-row role stability",
        "",
        markdown_table(report_best),
        "",
        "## Matched-strategy shift statistics",
        "",
        markdown_table(shift_stats),
        "",
        "## Reviewer-facing interpretation",
        "",
        "- The role-level queue is more stable than exact aiming phase selection: the receiver-risk candidates remain ahead of the optical-upper layout across V8, V9, and V10.",
        "- Exact best strategies are not stable. This is reported as sampling, receiver-discretization, and seed sensitivity rather than hidden behind a single favorable phase.",
        "- V8-to-V9 and V9-to-V10 shifts mean that small peak-to-active-mean differences should not be described as final receiver-design improvements.",
        "- The defensible claim is a reproducible screening queue for future full-field annual custom-aimpoint studies.",
        "",
    ]
    (out / "V11_SOLTRACE_CONVERGENCE_AUDIT.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    run = resolve(args.run)
    out = resolve(args.out)
    (out / "tables").mkdir(parents=True, exist_ok=True)
    (out / "figures").mkdir(parents=True, exist_ok=True)

    summaries = []
    relatives = []
    for matrix, meta in MATRICES.items():
        directory = run / meta["dir"].relative_to(DEFAULT_RUN) if run != DEFAULT_RUN else meta["dir"]
        summary, relative = load_matrix(matrix, directory)
        summaries.append(summary)
        relatives.append(relative)
    summary = pd.concat(summaries, axis=0, ignore_index=True)
    relative = pd.concat(relatives, axis=0, ignore_index=True)

    best = best_rows(summary)
    stats = matrix_stats(relative, summary)
    best_stability = best_stability_table(best)
    v8_v9 = matched_shift_table(summary, "V8", "V9")
    v9_v10 = matched_shift_table(summary, "V9", "V10")
    shifts = shift_summary(v8_v9, v9_v10)

    summary.to_csv(out / "tables" / "v11_combined_summary_rows.csv", index=False)
    relative.to_csv(out / "tables" / "v11_combined_relative_rows.csv", index=False)
    best.to_csv(out / "tables" / "v11_best_rows_by_matrix.csv", index=False)
    stats.to_csv(out / "tables" / "v11_matrix_scale.csv", index=False)
    best_stability.to_csv(out / "tables" / "v11_role_stability.csv", index=False)
    v8_v9.to_csv(out / "tables" / "v11_matched_strategy_shift_v8_v9.csv", index=False)
    v9_v10.to_csv(out / "tables" / "v11_matched_strategy_shift_v9_v10.csv", index=False)
    shifts.to_csv(out / "tables" / "v11_shift_summary.csv", index=False)

    make_figure(best, v9_v10, out)
    write_report(stats, best_stability, shifts, out)
    print(f"Wrote V11 convergence audit to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
