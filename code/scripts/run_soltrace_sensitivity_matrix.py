#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def parse_csv(text: str, cast=str) -> list:
    values = []
    for part in text.split(","):
        part = part.strip()
        if part:
            values.append(cast(part))
    return values


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run and aggregate a reduced PySolTrace layout--aimpoint sensitivity matrix."
    )
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "server_full.json")
    parser.add_argument("--pysoltrace-dir", type=Path, required=True)
    parser.add_argument(
        "--layout-ids",
        default="baseline_full,deform_0276,deform_0893,deform_1387,deform_1822",
    )
    parser.add_argument("--days", default="80,172,266")
    parser.add_argument("--hours", default="10,12,14")
    parser.add_argument("--base-strategies", default="visible_equator,five_point")
    parser.add_argument(
        "--include-proxy-union",
        action="store_true",
        help="Add all unique proxy-best staggered strategies so every layout can be paired with baseline under the same strategy.",
    )
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--max-heliostats", type=int, default=2400)
    parser.add_argument("--rays", type=int, default=300000)
    parser.add_argument("--threads", type=int, default=10)
    parser.add_argument("--receiver-panels", type=int, default=14)
    parser.add_argument("--receiver-nx", type=int, default=16)
    parser.add_argument("--receiver-ny", type=int, default=48)
    parser.add_argument("--seed", type=int, default=2026051202)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def fmt_hour(hour: float) -> str:
    if abs(hour - round(hour)) < 1e-9:
        return str(int(round(hour)))
    return str(hour).replace(".", "p")


def load_proxy_best(run: Path) -> dict[str, str]:
    path = run / "aiming_proxy" / "best_aiming_by_layout.csv"
    if not path.exists():
        return {}
    df = pd.read_csv(path)
    return dict(zip(df["layout_id"].astype(str), df["strategy"].astype(str), strict=False))


def unique_preserve_order(values: list[str]) -> list[str]:
    return list(dict.fromkeys([value for value in values if value]))


def markdown_table(df: pd.DataFrame, floatfmt: str = ".3f") -> str:
    if df.empty:
        return ""
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


def run_condition(args: argparse.Namespace, out: Path, day: int, hour: float, strategies: list[str]) -> None:
    condition_dir = out / f"d{day}_h{fmt_hour(hour)}"
    summary_path = condition_dir / "tables" / "soltrace_aimpoint_summary.csv"
    if summary_path.exists() and not args.force:
        print(f"Skipping existing condition d{day} h{hour}: {summary_path}", flush=True)
        return
    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "run_soltrace_aimpoint_pilot.py"),
        "--run",
        str(args.run),
        "--config",
        str(args.config),
        "--pysoltrace-dir",
        str(args.pysoltrace_dir),
        "--layout-ids",
        args.layout_ids,
        "--out",
        str(condition_dir),
        "--max-heliostats",
        str(args.max_heliostats),
        "--rays",
        str(args.rays),
        "--threads",
        str(args.threads),
        "--receiver-panels",
        str(args.receiver_panels),
        "--receiver-nx",
        str(args.receiver_nx),
        "--receiver-ny",
        str(args.receiver_ny),
        "--sun-day",
        str(day),
        "--sun-hour",
        str(hour),
        "--seed",
        str(args.seed + day * 100 + int(round(hour * 10))),
        "--strategies",
        ",".join(strategies),
    ]
    print("Running condition:", " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=ROOT, check=True)


def aggregate(out: Path, days: list[int], hours: list[float], proxy_best: dict[str, str]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    frames = []
    for day in days:
        for hour in hours:
            condition_dir = out / f"d{day}_h{fmt_hour(hour)}"
            path = condition_dir / "tables" / "soltrace_aimpoint_summary.csv"
            if not path.exists():
                continue
            df = pd.read_csv(path)
            df["condition_id"] = f"d{day}_h{fmt_hour(hour)}"
            frames.append(df)
    if not frames:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    all_df = pd.concat(frames, axis=0, ignore_index=True)
    all_df.to_csv(out / "tables" / "soltrace_sensitivity_all.csv", index=False)

    baseline = all_df[all_df["layout_id"] == "baseline_full"].copy()
    baseline = baseline.rename(
        columns={
            "peak_to_active_mean": "baseline_peak_to_active_mean",
            "active_flux_cv": "baseline_active_flux_cv",
            "receiver_intercept_per_requested_ray": "baseline_receiver_intercept_per_requested_ray",
            "total_receiver_power_proxy_w": "baseline_total_receiver_power_proxy_w",
        }
    )
    key_cols = ["sun_day", "sun_hour", "strategy"]
    rel = all_df.merge(
        baseline[
            key_cols
            + [
                "baseline_peak_to_active_mean",
                "baseline_active_flux_cv",
                "baseline_receiver_intercept_per_requested_ray",
                "baseline_total_receiver_power_proxy_w",
            ]
        ],
        on=key_cols,
        how="left",
    )
    rel["delta_peak_to_active_mean_pct_vs_baseline_same_strategy"] = (
        (rel["peak_to_active_mean"] - rel["baseline_peak_to_active_mean"])
        / rel["baseline_peak_to_active_mean"].replace(0.0, np.nan)
        * 100.0
    )
    rel["delta_active_cv_pct_vs_baseline_same_strategy"] = (
        (rel["active_flux_cv"] - rel["baseline_active_flux_cv"])
        / rel["baseline_active_flux_cv"].replace(0.0, np.nan)
        * 100.0
    )
    rel["delta_receiver_intercept_pctpt_vs_baseline_same_strategy"] = (
        rel["receiver_intercept_per_requested_ray"] - rel["baseline_receiver_intercept_per_requested_ray"]
    ) * 100.0
    rel.to_csv(out / "tables" / "soltrace_sensitivity_relative.csv", index=False)

    nonbase = rel[rel["layout_id"] != "baseline_full"].copy()
    summary = (
        nonbase.groupby(["layout_id", "strategy"], as_index=False)
        .agg(
            cases=("delta_peak_to_active_mean_pct_vs_baseline_same_strategy", "count"),
            median_delta_peak_pct=("delta_peak_to_active_mean_pct_vs_baseline_same_strategy", "median"),
            mean_delta_peak_pct=("delta_peak_to_active_mean_pct_vs_baseline_same_strategy", "mean"),
            p10_delta_peak_pct=("delta_peak_to_active_mean_pct_vs_baseline_same_strategy", lambda x: np.percentile(x, 10)),
            p90_delta_peak_pct=("delta_peak_to_active_mean_pct_vs_baseline_same_strategy", lambda x: np.percentile(x, 90)),
            share_lower_peak=("delta_peak_to_active_mean_pct_vs_baseline_same_strategy", lambda x: float((x < 0).mean())),
            median_delta_cv_pct=("delta_active_cv_pct_vs_baseline_same_strategy", "median"),
            median_delta_intercept_pctpt=(
                "delta_receiver_intercept_pctpt_vs_baseline_same_strategy",
                "median",
            ),
        )
        .sort_values(["mean_delta_peak_pct", "median_delta_peak_pct"])
    )
    summary.to_csv(out / "tables" / "soltrace_sensitivity_summary.csv", index=False)

    proxy_records = []
    for layout_id, strategy in proxy_best.items():
        if layout_id == "baseline_full":
            continue
        subset = rel[(rel["layout_id"] == layout_id) & (rel["strategy"] == strategy)].copy()
        if subset.empty:
            continue
        d = subset["delta_peak_to_active_mean_pct_vs_baseline_same_strategy"].dropna()
        proxy_records.append(
            {
                "layout_id": layout_id,
                "proxy_best_strategy": strategy,
                "cases": int(len(d)),
                "median_delta_peak_pct": float(d.median()),
                "mean_delta_peak_pct": float(d.mean()),
                "p10_delta_peak_pct": float(np.percentile(d, 10)),
                "p90_delta_peak_pct": float(np.percentile(d, 90)),
                "share_lower_peak": float((d < 0).mean()),
                "best_condition_delta_pct": float(d.min()),
                "worst_condition_delta_pct": float(d.max()),
            }
        )
    proxy_summary = pd.DataFrame.from_records(proxy_records)
    if not proxy_summary.empty:
        proxy_summary = proxy_summary.sort_values(["mean_delta_peak_pct", "median_delta_peak_pct"])
    proxy_summary.to_csv(out / "tables" / "soltrace_proxy_strategy_summary.csv", index=False)
    return all_df, rel, proxy_summary


def plot_outputs(out: Path, rel: pd.DataFrame, proxy_summary: pd.DataFrame, proxy_best: dict[str, str]) -> None:
    if rel.empty:
        return
    out_fig = out / "figures"
    out_fig.mkdir(parents=True, exist_ok=True)

    nonbase = rel[rel["layout_id"] != "baseline_full"].copy()
    fig, ax = plt.subplots(figsize=(9.2, 4.6), dpi=190)
    order = (
        nonbase.groupby("strategy")["delta_peak_to_active_mean_pct_vs_baseline_same_strategy"]
        .mean()
        .sort_values()
        .index.tolist()
    )
    data = [
        nonbase.loc[nonbase["strategy"] == strategy, "delta_peak_to_active_mean_pct_vs_baseline_same_strategy"].dropna()
        for strategy in order
    ]
    ax.boxplot(data, labels=[s.replace("_", " ") for s in order], showfliers=False)
    ax.axhline(0.0, color="#222222", linewidth=0.9)
    ax.set_ylabel("Delta peak / active mean vs paired baseline (%)")
    ax.set_title("Reduced SolTrace sensitivity by aiming strategy", fontweight="bold")
    ax.tick_params(axis="x", rotation=25, labelsize=8)
    ax.grid(True, axis="y", alpha=0.18)
    fig.tight_layout()
    fig.savefig(out_fig / "soltrace_strategy_sensitivity_boxplot.png", bbox_inches="tight")
    plt.close(fig)

    proxy_rows = []
    for layout_id, strategy in proxy_best.items():
        if layout_id == "baseline_full":
            continue
        subset = nonbase[(nonbase["layout_id"] == layout_id) & (nonbase["strategy"] == strategy)]
        if subset.empty:
            continue
        for row in subset.itertuples(index=False):
            proxy_rows.append(
                {
                    "layout_id": layout_id,
                    "condition_id": row.condition_id,
                    "delta": row.delta_peak_to_active_mean_pct_vs_baseline_same_strategy,
                }
            )
    proxy_df = pd.DataFrame.from_records(proxy_rows)
    if not proxy_df.empty:
        pivot = proxy_df.pivot(index="layout_id", columns="condition_id", values="delta")
        fig_w = max(8.8, 0.46 * len(pivot.columns) + 2.4)
        fig_h = max(3.4, 0.55 * len(pivot.index) + 1.4)
        fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=190)
        vmax = float(np.nanmax(np.abs(pivot.to_numpy()))) if np.isfinite(pivot.to_numpy()).any() else 1.0
        im = ax.imshow(pivot.to_numpy(), cmap="RdBu_r", vmin=-vmax, vmax=vmax, aspect="auto")
        ax.set_xticks(range(len(pivot.columns)))
        ax.set_xticklabels(pivot.columns, rotation=45, ha="right", fontsize=7)
        ax.set_yticks(range(len(pivot.index)))
        ax.set_yticklabels(pivot.index, fontsize=8)
        ax.set_title("Proxy-best staggered strategies under direct reduced SolTrace", fontweight="bold")
        for i in range(len(pivot.index)):
            for j in range(len(pivot.columns)):
                val = pivot.iloc[i, j]
                if np.isfinite(val):
                    ax.text(j, i, f"{val:+.1f}", ha="center", va="center", fontsize=6, color="#111111")
        cbar = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
        cbar.set_label("Delta peak / active mean (%)")
        fig.tight_layout()
        fig.savefig(out_fig / "soltrace_proxy_strategy_heatmap.png", bbox_inches="tight")
        plt.close(fig)

    if not proxy_summary.empty:
        fig, ax = plt.subplots(figsize=(7.2, 3.8), dpi=190)
        x = np.arange(len(proxy_summary))
        ax.bar(x, proxy_summary["mean_delta_peak_pct"], color="#4c78a8")
        ax.scatter(x, proxy_summary["median_delta_peak_pct"], color="#f58518", zorder=3, label="median")
        ax.axhline(0.0, color="#222222", linewidth=0.9)
        ax.set_xticks(x)
        ax.set_xticklabels(proxy_summary["layout_id"], rotation=20, ha="right")
        ax.set_ylabel("Delta peak / active mean (%)")
        ax.set_title("Proxy-best strategies: mean and median reduced SolTrace change", fontweight="bold")
        ax.legend(frameon=False, fontsize=8)
        ax.grid(True, axis="y", alpha=0.18)
        fig.tight_layout()
        fig.savefig(out_fig / "soltrace_proxy_strategy_summary.png", bbox_inches="tight")
        plt.close(fig)


def write_report(
    out: Path,
    args: argparse.Namespace,
    days: list[int],
    hours: list[float],
    strategies: list[str],
    summary: pd.DataFrame,
    proxy_summary: pd.DataFrame,
) -> None:
    report = [
        "# Enlarged Reduced SolTrace Sensitivity Matrix",
        "",
        "This run extends the first reduced PySolTrace pilot by testing each explicit aiming strategy across multiple representative solar conditions. It is still a reduced checks layer, not a full-field annual flux certification.",
        "",
        f"- Days: {days}",
        f"- Hours: {hours}",
        f"- Layouts: `{args.layout_ids}`",
        f"- Strategies: `{', '.join(strategies)}`",
        f"- Sampled heliostats per layout: {args.max_heliostats}",
        f"- Requested rays per case: {args.rays}",
        f"- Receiver panels/bins: {args.receiver_panels} panels, {args.receiver_nx} x {args.receiver_ny} bins each",
        "",
        "## Strategy Summary",
        "",
    ]
    if not summary.empty:
        cols = [
            "layout_id",
            "strategy",
            "cases",
            "median_delta_peak_pct",
            "mean_delta_peak_pct",
            "p10_delta_peak_pct",
            "p90_delta_peak_pct",
            "share_lower_peak",
        ]
        report.append(markdown_table(summary.loc[:, cols], floatfmt=".3f"))
    report.extend(["", "## Proxy-Best Staggered Strategy Summary", ""])
    if not proxy_summary.empty:
        report.append(markdown_table(proxy_summary, floatfmt=".3f"))
    else:
        report.append("No proxy-best rows were available for aggregation.")
    report.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "The matrix strengthens the direct evidence for selected layout--aiming pairs, but it remains sampled. It should be described as an enlarged reduced SolTrace numerical check. Full-field annual custom-aimpoint numerical checking remains future work.",
            "",
        ]
    )
    (out / "SOLTRACE_SENSITIVITY_MATRIX_REPORT.md").write_text("\n".join(report), encoding="utf-8")


def main() -> int:
    args = parse_args()
    args.run = args.run if args.run.is_absolute() else ROOT / args.run
    args.config = args.config if args.config.is_absolute() else ROOT / args.config
    out = args.out or (args.run / "soltrace_aimpoint_sensitivity_extended")
    out = out if out.is_absolute() else ROOT / out
    (out / "tables").mkdir(parents=True, exist_ok=True)
    (out / "figures").mkdir(parents=True, exist_ok=True)

    days = parse_csv(args.days, int)
    hours = parse_csv(args.hours, float)
    proxy_best = load_proxy_best(args.run)
    strategies = parse_csv(args.base_strategies, str)
    if args.include_proxy_union:
        strategies.extend(sorted(set(proxy_best.values())))
    strategies = unique_preserve_order(strategies)

    run_config = {
        "run": str(args.run),
        "config": str(args.config),
        "pysoltrace_dir": str(args.pysoltrace_dir),
        "layout_ids": args.layout_ids,
        "days": days,
        "hours": hours,
        "strategies": strategies,
        "proxy_best": proxy_best,
        "max_heliostats": args.max_heliostats,
        "rays": args.rays,
        "threads": args.threads,
        "receiver_panels": args.receiver_panels,
        "receiver_nx": args.receiver_nx,
        "receiver_ny": args.receiver_ny,
        "seed": args.seed,
    }
    (out / "run_config.json").write_text(json.dumps(run_config, indent=2), encoding="utf-8")

    for day in days:
        for hour in hours:
            run_condition(args, out, day, hour, strategies)

    _all_df, rel, proxy_summary = aggregate(out, days, hours, proxy_best)
    summary = pd.read_csv(out / "tables" / "soltrace_sensitivity_summary.csv") if (out / "tables" / "soltrace_sensitivity_summary.csv").exists() else pd.DataFrame()
    plot_outputs(out, rel, proxy_summary, proxy_best)
    write_report(out, args, days, hours, strategies, summary, proxy_summary)
    print(f"Wrote enlarged SolTrace sensitivity matrix to {out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
