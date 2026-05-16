#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MATRIX = (
    ROOT
    / "server_outputs"
    / "streamed_fullfield_20260511_205252"
    / "soltrace_allphase_27cond_20260512"
)

PALETTE = {
    "negative": "#0072B2",
    "positive": "#D55E00",
    "green": "#009E73",
    "ink": "#111827",
    "muted": "#4B5563",
    "grid": "#D1D5DB",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build publication-facing summaries for the all-phase reduced SolTrace matrix."
    )
    parser.add_argument("--matrix", type=Path, default=DEFAULT_MATRIX)
    parser.add_argument("--run", type=Path, default=ROOT / "server_outputs" / "streamed_fullfield_20260511_205252")
    parser.add_argument("--out", type=Path, default=None)
    return parser.parse_args()


def set_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
            "font.size": 8.2,
            "axes.titlesize": 8.9,
            "axes.labelsize": 8.0,
            "xtick.labelsize": 7.1,
            "ytick.labelsize": 7.1,
            "legend.fontsize": 7.0,
            "figure.titlesize": 11.0,
            "axes.facecolor": "white",
            "figure.facecolor": "white",
            "savefig.facecolor": "white",
            "axes.edgecolor": "#374151",
            "axes.linewidth": 0.7,
            "axes.grid": True,
            "grid.color": PALETTE["grid"],
            "grid.linewidth": 0.55,
            "grid.alpha": 0.62,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def short_layout(value: str) -> str:
    return value.replace("baseline_full", "baseline").replace("deform_", "D")


def clean_strategy(value: str) -> str:
    return (
        value.replace("staggered_levels:9:0.380:", "S9-p")
        .replace("visible_equator", "visible")
        .replace("five_point", "five-point")
    )


def markdown_table(df: pd.DataFrame, floatfmt: str = ".3f") -> str:
    if df.empty:
        return "_No rows available._"
    headers = list(df.columns)
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in df.itertuples(index=False):
        cells = []
        for value in row:
            if isinstance(value, (float, np.floating)):
                cells.append(format(float(value), floatfmt))
            else:
                cells.append(str(value))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def load_outputs(matrix: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    summary_path = matrix / "tables" / "soltrace_sensitivity_summary.csv"
    rel_path = matrix / "tables" / "soltrace_sensitivity_relative.csv"
    all_path = matrix / "tables" / "soltrace_sensitivity_all.csv"
    missing = [path for path in [summary_path, rel_path, all_path] if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing matrix tables: " + ", ".join(str(path) for path in missing))
    return pd.read_csv(summary_path), pd.read_csv(rel_path), pd.read_csv(all_path)


def build_tables(matrix: Path, run: Path, out: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    summary, rel, all_df = load_outputs(matrix)
    nonbase = summary[summary["layout_id"] != "baseline_full"].copy()
    best = (
        nonbase.sort_values(["mean_delta_peak_pct", "median_delta_peak_pct"])
        .groupby("layout_id", as_index=False)
        .head(1)
        .sort_values("mean_delta_peak_pct")
    )
    best.to_csv(out / "tables" / "allphase_best_strategy_by_layout.csv", index=False)

    proxy_path = run / "aiming_proxy" / "best_aiming_by_layout.csv"
    proxy_rows = []
    if proxy_path.exists():
        proxy = pd.read_csv(proxy_path)
        for row in proxy.itertuples(index=False):
            if row.layout_id == "baseline_full":
                continue
            subset = summary[(summary["layout_id"] == row.layout_id) & (summary["strategy"] == row.strategy)]
            if subset.empty:
                continue
            srow = subset.iloc[0].to_dict()
            proxy_rows.append(
                {
                    "layout_id": row.layout_id,
                    "proxy_strategy": row.strategy,
                    "direct_mean_delta_peak_pct": srow["mean_delta_peak_pct"],
                    "direct_median_delta_peak_pct": srow["median_delta_peak_pct"],
                    "direct_share_lower_peak": srow["share_lower_peak"],
                }
            )
    proxy_direct = pd.DataFrame(proxy_rows).sort_values("direct_mean_delta_peak_pct") if proxy_rows else pd.DataFrame()
    proxy_direct.to_csv(out / "tables" / "allphase_proxy_strategy_direct_check.csv", index=False)

    intercept = (
        all_df.groupby(["layout_id", "strategy"], as_index=False)["receiver_intercept_per_requested_ray"]
        .median()
        .sort_values("receiver_intercept_per_requested_ray", ascending=False)
    )
    intercept.to_csv(out / "tables" / "allphase_median_intercept_by_strategy.csv", index=False)

    rel.to_csv(out / "tables" / "allphase_condition_level_relative.csv", index=False)
    return best, proxy_direct


def build_figure(matrix: Path, run: Path, out: Path, best: pd.DataFrame, proxy_direct: pd.DataFrame) -> None:
    summary, rel, all_df = load_outputs(matrix)
    nonbase = summary[summary["layout_id"] != "baseline_full"].copy()
    nonbase["layout_label"] = nonbase["layout_id"].map(short_layout)
    nonbase["strategy_label"] = nonbase["strategy"].map(clean_strategy)

    layout_order = ["deform_1387", "deform_0893", "deform_1822", "deform_0276"]
    role_labels = {
        "deform_1387": "receiver-risk queue",
        "deform_0893": "nominal proxy",
        "deform_1822": "balanced control",
        "deform_0276": "optical upper",
    }
    heat = nonbase.pivot_table(
        index="layout_label",
        columns="strategy_label",
        values="mean_delta_peak_pct",
        aggfunc="mean",
    )
    strategy_order = ["visible", "five-point"] + [f"S9-p{i}" for i in range(9)]
    heat = heat.reindex(columns=[col for col in strategy_order if col in heat.columns])
    heat = heat.reindex([short_layout(v) for v in layout_order if short_layout(v) in heat.index])

    fig = plt.figure(figsize=(7.35, 4.92), dpi=360)
    gs = fig.add_gridspec(
        2,
        2,
        height_ratios=[1.0, 1.22],
        width_ratios=[1.0, 1.0],
        hspace=0.54,
        wspace=0.30,
        left=0.112,
        right=0.925,
        top=0.955,
        bottom=0.105,
    )
    ax0 = fig.add_subplot(gs[0, 0])
    ax1 = fig.add_subplot(gs[0, 1])
    ax2 = fig.add_subplot(gs[1, :])

    plot_best = best.copy()
    plot_best["layout_rank"] = plot_best["layout_id"].map({v: i for i, v in enumerate(layout_order)})
    plot_best = plot_best.sort_values("layout_rank")
    y = np.arange(len(plot_best))
    means = plot_best["mean_delta_peak_pct"].to_numpy(dtype=float)
    medians = plot_best["median_delta_peak_pct"].to_numpy(dtype=float)
    p10 = plot_best["p10_delta_peak_pct"].to_numpy(dtype=float)
    p90 = plot_best["p90_delta_peak_pct"].to_numpy(dtype=float)
    ax0.hlines(y, p10, p90, color="#9CA3AF", linewidth=4.2, alpha=0.55, zorder=1)
    ax0.scatter(means, y, s=70, color=PALETTE["negative"], edgecolor="white", linewidth=0.7, label="mean", zorder=3)
    ax0.scatter(medians, y, s=44, marker="D", color="#111827", edgecolor="white", linewidth=0.5, label="median", zorder=4)
    ax0.axvline(0, color=PALETTE["ink"], linestyle="--", linewidth=0.75)
    ax0.set_yticks(y)
    ax0.set_yticklabels(
        [f"{short_layout(row.layout_id)} | {clean_strategy(row.strategy)}" for row in plot_best.itertuples()]
    )
    ax0.invert_yaxis()
    ax0.set_xlabel("Mean P/M change (%)")
    ax0.set_title("(a) Best direct row with P10--P90 spread", loc="left", pad=8)
    ax0.legend(
        frameon=False,
        loc="upper center",
        bbox_to_anchor=(0.58, -0.17),
        ncol=2,
        handlelength=1.15,
        columnspacing=1.4,
    )

    best_map = {
        row.layout_id: row.mean_delta_peak_pct for row in best.itertuples(index=False)
    }
    if not proxy_direct.empty:
        proxy_plot = proxy_direct[proxy_direct["layout_id"].isin(layout_order)].copy()
        proxy_plot["layout_rank"] = proxy_plot["layout_id"].map({v: i for i, v in enumerate(layout_order)})
        proxy_plot = proxy_plot.sort_values("layout_rank")
        y = np.arange(len(proxy_plot))
        proxy_vals = proxy_plot["direct_mean_delta_peak_pct"].to_numpy(dtype=float)
        best_vals = np.array([best_map.get(row.layout_id, np.nan) for row in proxy_plot.itertuples(index=False)])
        ax1.barh(y - 0.17, proxy_vals, height=0.28, color="#94A3B8", label="proxy-selected row")
        ax1.barh(y + 0.17, best_vals, height=0.28, color=PALETTE["negative"], label="best direct row")
        ax1.set_yticks(y)
        ax1.set_yticklabels(
            [f"{short_layout(row.layout_id)} | {role_labels[row.layout_id]}" for row in proxy_plot.itertuples()]
        )
        ax1.invert_yaxis()
    ax1.axvline(0, color=PALETTE["ink"], linestyle="--", linewidth=0.75)
    ax1.set_xlabel("Mean P/M change (%)")
    ax1.set_title("(b) Screening transfer check", loc="left", pad=8)
    ax1.legend(
        frameon=False,
        loc="upper center",
        bbox_to_anchor=(0.58, -0.17),
        ncol=2,
        handlelength=1.15,
        columnspacing=1.4,
    )

    values = heat.to_numpy(dtype=float)
    vmax = max(6.0, float(np.nanpercentile(np.abs(values), 95))) if np.isfinite(values).any() else 6.0
    norm = TwoSlopeNorm(vmin=-vmax, vcenter=0.0, vmax=vmax)
    im = ax2.imshow(values, aspect="auto", cmap="RdBu_r", norm=norm)
    ax2.set_yticks(np.arange(len(heat.index)))
    ax2.set_yticklabels(
        [
            f"{short_layout(layout)}\n{role_labels[layout]}"
            for layout in layout_order
            if short_layout(layout) in heat.index
        ]
    )
    ax2.set_xticks(np.arange(len(heat.columns)))
    ax2.set_xticklabels(heat.columns)
    ax2.set_title("(c) Layout--aiming response surface", loc="left", pad=8)
    ax2.set_xticks(np.arange(-0.5, len(heat.columns), 1), minor=True)
    ax2.set_yticks(np.arange(-0.5, len(heat.index), 1), minor=True)
    ax2.grid(which="minor", color="white", linewidth=1.25)
    ax2.tick_params(which="minor", bottom=False, left=False)

    best_lookup = {
        (short_layout(row.layout_id), clean_strategy(row.strategy)): "B" for row in best.itertuples(index=False)
    }
    proxy_lookup = {
        (short_layout(row.layout_id), clean_strategy(row.proxy_strategy)): "P"
        for row in proxy_direct.itertuples(index=False)
    } if not proxy_direct.empty else {}
    for i in range(heat.shape[0]):
        for j in range(heat.shape[1]):
            key = (heat.index[i], heat.columns[j])
            marker = ""
            if key in best_lookup and key in proxy_lookup:
                marker = "B/P"
            elif key in best_lookup:
                marker = "B"
            elif key in proxy_lookup:
                marker = "P"
            if marker:
                value = heat.iloc[i, j]
                color = "white" if np.isfinite(value) and abs(value) > 0.55 * vmax else PALETTE["ink"]
                ax2.text(j, i, marker, ha="center", va="center", fontsize=7.2, fontweight="bold", color=color)
    cbar = fig.colorbar(im, ax=ax2, fraction=0.018, pad=0.012)
    cbar.set_label("Mean P/M change vs paired baseline (%)")

    intercept_min = all_df["receiver_intercept_per_requested_ray"].min()
    intercept_max = all_df["receiver_intercept_per_requested_ray"].max()
    ax2.text(
        0.995,
        1.025,
        f"receiver-intercept sanity: {intercept_min:.3f}--{intercept_max:.3f}",
        transform=ax2.transAxes,
        ha="right",
        va="bottom",
        fontsize=7.0,
        color=PALETTE["muted"],
    )

    for ax in [ax0, ax1, ax2]:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    fig.savefig(out / "figures" / "fig_soltrace_allphase_direct_panel.png", bbox_inches="tight")
    plt.close(fig)


def condition_sort_key(value: str) -> tuple[int, float]:
    day, hour = value.split("_h", maxsplit=1)
    return int(day.removeprefix("d")), float(hour)


def write_report(matrix: Path, out: Path, best: pd.DataFrame, proxy_direct: pd.DataFrame) -> None:
    _, rel, all_df = load_outputs(matrix)
    run_config_path = matrix / "run_config.json"
    run_config = run_config_path.read_text(encoding="utf-8") if run_config_path.exists() else "{}"
    condition_ids = sorted(rel["condition_id"].dropna().unique().tolist(), key=condition_sort_key)
    days = sorted(int(v) for v in rel["sun_day"].dropna().unique().tolist())
    hours = sorted(float(v) for v in rel["sun_hour"].dropna().unique().tolist())
    strategies = sorted(rel["strategy"].dropna().unique().tolist())
    layouts = sorted(rel["layout_id"].dropna().unique().tolist())
    sanity = pd.DataFrame(
        [
            {
                "matrix_rows": len(rel),
                "layouts": len(layouts),
                "strategies": len(strategies),
                "conditions": len(condition_ids),
                "sampled_heliostats": int(rel["sampled_heliostat_count"].median()),
                "rays_per_case": int(rel["ray_count_requested"].median()),
                "intercept_min": float(all_df["receiver_intercept_per_requested_ray"].min()),
                "intercept_max": float(all_df["receiver_intercept_per_requested_ray"].max()),
            }
        ]
    )
    best_cols = ["layout_id", "strategy", "cases", "median_delta_peak_pct", "mean_delta_peak_pct", "share_lower_peak", "median_delta_intercept_pctpt"]
    proxy_cols = ["layout_id", "proxy_strategy", "direct_median_delta_peak_pct", "direct_mean_delta_peak_pct", "direct_share_lower_peak"]
    report = [
        "# All-Phase Reduced SolTrace Matrix Report",
        "",
        "This report summarizes the all-phase direct PySolTrace check layer. It tests visible-equator, five-point, and all nine S9 staggered phases under paired baseline comparisons.",
        "",
        "## Detected Matrix Scope",
        "",
        markdown_table(sanity, floatfmt=".3f"),
        "",
        f"Detected condition IDs: {', '.join(condition_ids)}.",
        "",
        f"Detected solar days: {', '.join(str(v) for v in days)}; detected hours: {', '.join(format(v, '.1f') for v in hours)}.",
        "",
        "## Best Direct Strategy by Layout",
        "",
        markdown_table(best.loc[:, [col for col in best_cols if col in best.columns]], floatfmt=".3f"),
        "",
        "## Proxy-Selected Strategies Under Direct Tracing",
        "",
        markdown_table(proxy_direct.loc[:, [col for col in proxy_cols if col in proxy_direct.columns]], floatfmt=".3f") if not proxy_direct.empty else "_No proxy-direct rows matched._",
        "",
        "## Run Config",
        "",
        "The stored run configuration below may correspond to the final tail-acceleration job. The detected matrix scope above is computed from the merged output tables and is the authoritative scope used for manuscript claims.",
        "",
        "```json",
        run_config,
        "```",
        "",
        "## Claim Boundary",
        "",
        "This remains reduced direct ray tracing, not full-field annual custom-aimpoint certification. Its role is to test whether the direct-aiming conclusion depends on testing only proxy-selected staggered phases.",
        "",
    ]
    (out / "ALLPHASE_SOLTRACE_REPORT.md").write_text("\n".join(report), encoding="utf-8")


def main() -> int:
    args = parse_args()
    matrix = args.matrix if args.matrix.is_absolute() else ROOT / args.matrix
    run = args.run if args.run.is_absolute() else ROOT / args.run
    out = args.out or (matrix / "publication_allphase")
    out = out if out.is_absolute() else ROOT / out
    (out / "tables").mkdir(parents=True, exist_ok=True)
    (out / "figures").mkdir(parents=True, exist_ok=True)

    set_style()
    best, proxy_direct = build_tables(matrix, run, out)
    build_figure(matrix, run, out, best, proxy_direct)
    write_report(matrix, out, best, proxy_direct)
    print(f"Wrote all-phase SolTrace summaries to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
