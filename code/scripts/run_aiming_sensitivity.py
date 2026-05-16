#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
SCRIPTS = ROOT / "scripts"
for path in (SRC, SCRIPTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from dhf_rebuild.data_io import load_json
from run_aiming_proxy import (
    features_for_layout,
    flux_map,
    load_layout,
    make_groups,
    offsets_for_strategy,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run sensitivity checks for the receiver aiming proxy."
    )
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "server_full.json")
    parser.add_argument(
        "--layout-ids",
        default="baseline_full,deform_0276,deform_0893,deform_1822,deform_1387",
    )
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument(
        "--profile",
        choices=["standard", "deep"],
        default="standard",
        help="standard is the manuscript-facing 24-condition sweep; deep is the 81-condition stress sweep.",
    )
    return parser.parse_args()


def strategy_grid(profile: str = "standard") -> list[str]:
    strategies = ["equator", "five_point"]
    level_counts = [7, 9] if profile == "standard" else [7, 9, 11]
    theta_amps = [0.0] if profile == "standard" else [0.0, 0.020]
    for level_count in level_counts:
        for amp in [0.34, 0.38, 0.42]:
            for phase in range(level_count):
                strategies.append(f"staggered_levels:{level_count:d}:{amp:.3f}:{phase:d}")
    for amp in [0.24, 0.32, 0.40]:
        for theta_amp in theta_amps:
            strategies.append(f"balanced:{amp:.3f}:{theta_amp:.3f}")
    return strategies


def conditions(profile: str = "standard") -> list[dict[str, float | int]]:
    rows = []
    sector_values = [36, 48, 60]
    annulus_values = [6, 8] if profile == "standard" else [6, 8, 10]
    sigma_theta_values = [0.030, 0.042] if profile == "standard" else [0.030, 0.035, 0.042]
    sigma_z_values = [0.055, 0.080] if profile == "standard" else [0.055, 0.065, 0.080]
    for sectors in sector_values:
        for annuli in annulus_values:
            for sigma_theta in sigma_theta_values:
                for sigma_z_fraction in sigma_z_values:
                    rows.append(
                        {
                            "sectors": sectors,
                            "annuli": annuli,
                            "sigma_theta": sigma_theta,
                            "sigma_z_fraction": sigma_z_fraction,
                        }
                    )
    return rows


def best_for_condition(
    features: pd.DataFrame,
    config: dict,
    condition: dict[str, float | int],
    strategies: list[str],
) -> dict[str, float | str | int]:
    receiver_height = float(config["plant"]["receiver_height_m"])
    receiver_diameter = float(config["plant"]["receiver_diameter_m"])
    groups = make_groups(features, sectors=int(condition["sectors"]), annuli=int(condition["annuli"]))
    best: dict[str, float | str | int] | None = None
    for strategy in strategies:
        aimed = offsets_for_strategy(groups, strategy, receiver_height)
        _, metrics = flux_map(
            aimed,
            receiver_height,
            receiver_diameter,
            theta_bins=72,
            z_bins=70,
            sigma_theta=float(condition["sigma_theta"]),
            sigma_z_fraction=float(condition["sigma_z_fraction"]),
        )
        objective = (
            metrics["peak_to_mean_proxy"]
            + 0.85 * metrics["cv_active_proxy"]
            + 8.0 * metrics["spillage_proxy"]
        )
        record: dict[str, float | str | int] = {
            **condition,
            "strategy": strategy,
            "group_count": len(groups),
            "objective": float(objective),
            **metrics,
        }
        if best is None or float(record["objective"]) < float(best["objective"]):
            best = record
    assert best is not None
    return best


def write_summary(records: pd.DataFrame, out: Path) -> pd.DataFrame:
    baseline = records[records["layout_id"] == "baseline_full"].copy()
    key_cols = ["sectors", "annuli", "sigma_theta", "sigma_z_fraction"]
    merged = records.merge(
        baseline[key_cols + ["peak_to_mean_proxy", "cv_active_proxy", "intercept_fraction_proxy"]],
        on=key_cols,
        how="left",
        suffixes=("", "_baseline"),
    )
    merged["delta_peak_to_mean_pct"] = (
        merged["peak_to_mean_proxy"] / merged["peak_to_mean_proxy_baseline"] - 1.0
    ) * 100.0
    merged["delta_cv_pct"] = (merged["cv_active_proxy"] / merged["cv_active_proxy_baseline"] - 1.0) * 100.0
    merged["delta_intercept_pctpt"] = (
        merged["intercept_fraction_proxy"] - merged["intercept_fraction_proxy_baseline"]
    ) * 100.0
    merged.to_csv(out / "tables" / "aiming_sensitivity_records.csv", index=False)

    rows = []
    for layout_id, group in merged[merged["layout_id"] != "baseline_full"].groupby("layout_id"):
        rows.append(
            {
                "layout_id": layout_id,
                "condition_count": len(group),
                "improved_peak_to_mean_fraction": float((group["delta_peak_to_mean_pct"] < 0).mean()),
                "median_delta_peak_to_mean_pct": float(group["delta_peak_to_mean_pct"].median()),
                "p10_delta_peak_to_mean_pct": float(group["delta_peak_to_mean_pct"].quantile(0.10)),
                "p90_delta_peak_to_mean_pct": float(group["delta_peak_to_mean_pct"].quantile(0.90)),
                "median_delta_cv_pct": float(group["delta_cv_pct"].median()),
                "median_delta_intercept_pctpt": float(group["delta_intercept_pctpt"].median()),
                "most_common_strategy": str(group["strategy"].mode().iloc[0]),
            }
        )
    summary = pd.DataFrame(rows).sort_values("median_delta_peak_to_mean_pct")
    summary.to_csv(out / "tables" / "aiming_sensitivity_summary.csv", index=False)
    return summary


def write_figures(records: pd.DataFrame, summary: pd.DataFrame, out: Path) -> None:
    plot_df = records[records["layout_id"] != "baseline_full"].copy()
    order = summary["layout_id"].tolist()
    fig, ax = plt.subplots(figsize=(7.6, 4.1), dpi=180)
    data = [plot_df.loc[plot_df["layout_id"] == layout, "delta_peak_to_mean_pct"].to_numpy() for layout in order]
    ax.boxplot(data, labels=order, showfliers=False, patch_artist=True)
    ax.axhline(0.0, color="#333333", linewidth=0.9)
    ax.set_ylabel("Best aiming proxy peak/mean change vs baseline (%)")
    ax.set_xlabel("Layout")
    ax.grid(True, axis="y", alpha=0.22)
    ax.set_title("Aiming-proxy sensitivity across grouping, spot width, and phase assumptions", fontsize=10, fontweight="bold")
    fig.tight_layout()
    fig.savefig(out / "figures" / "aiming_sensitivity_boxplot.png", bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.2, 4.6), dpi=180)
    for layout in order:
        subset = plot_df[plot_df["layout_id"] == layout]
        ax.scatter(
            subset["delta_intercept_pctpt"],
            subset["delta_peak_to_mean_pct"],
            s=22,
            alpha=0.72,
            label=layout,
        )
    ax.axhline(0.0, color="#333333", linewidth=0.9)
    ax.axvline(0.0, color="#333333", linewidth=0.9)
    ax.set_xlabel("Intercept change vs baseline (percentage points)")
    ax.set_ylabel("Peak/mean change vs baseline (%)")
    ax.grid(True, alpha=0.2)
    ax.legend(fontsize=7, frameon=False, ncol=2)
    fig.tight_layout()
    fig.savefig(out / "figures" / "aiming_sensitivity_intercept_tradeoff.png", bbox_inches="tight")
    plt.close(fig)


def write_report(summary: pd.DataFrame, out: Path) -> None:
    header = "| Layout | Conditions | Fraction lower peak/mean | Median change (%) | P10/P90 change (%) | Median intercept change (pct-pt) |"
    rule = "| --- | ---: | ---: | ---: | ---: | ---: |"
    lines = [header, rule]
    for row in summary.itertuples():
        lines.append(
            f"| `{row.layout_id}` | {int(row.condition_count)} | "
            f"{row.improved_peak_to_mean_fraction:.2f} | "
            f"{row.median_delta_peak_to_mean_pct:+.2f} | "
            f"{row.p10_delta_peak_to_mean_pct:+.2f}/{row.p90_delta_peak_to_mean_pct:+.2f} | "
            f"{row.median_delta_intercept_pctpt:+.3f} |"
        )
    report = f"""# Aiming Proxy Sensitivity

This run tests whether the proxy aiming conclusion depends on one arbitrary discretization. It perturbs sector count, annular count, azimuthal spot width, vertical spot width, and staggered phase, then re-optimizes the best proxy aiming strategy for each layout and condition.

{chr(10).join(lines)}

Interpretation rule: this remains a proxy-level robustness test. It strengthens the candidate queue only if a layout improves peak-to-active-mean concentration across many assumptions without large intercept loss. It does not replace CoPylot/SolarPILOT or SolTrace custom-aimpoint numerical checking.

Main tables:

- `tables/aiming_sensitivity_records.csv`
- `tables/aiming_sensitivity_summary.csv`

Main figures:

- `figures/aiming_sensitivity_boxplot.png`
- `figures/aiming_sensitivity_intercept_tradeoff.png`
"""
    (out / "AIMING_SENSITIVITY_REPORT.md").write_text(report, encoding="utf-8")


def main() -> int:
    args = parse_args()
    config = load_json(args.config)
    run = args.run if args.run.is_absolute() else ROOT / args.run
    out = args.out or (run / "aiming_sensitivity")
    out = out if out.is_absolute() else ROOT / out
    (out / "tables").mkdir(parents=True, exist_ok=True)
    (out / "figures").mkdir(parents=True, exist_ok=True)

    feature_path = run / "heliostat_features.csv"
    all_features = pd.read_csv(feature_path) if feature_path.exists() else None
    strategies = strategy_grid(args.profile)
    condition_grid = conditions(args.profile)
    records: list[dict[str, float | str | int]] = []
    for layout_id in [part.strip() for part in args.layout_ids.split(",") if part.strip()]:
        layout_path = run / "layouts" / f"{layout_id}.csv"
        if not layout_path.exists():
            print(f"Skipping missing layout {layout_id}", flush=True)
            continue
        print(f"Loading features for {layout_id}", flush=True)
        features = features_for_layout(load_layout(layout_path), all_features, config)
        for i, condition in enumerate(condition_grid, start=1):
            best = best_for_condition(features, config, condition, strategies)
            best["layout_id"] = layout_id
            records.append(best)
            if i % 8 == 0:
                print(f"  {layout_id}: {i}/{len(condition_grid)} conditions", flush=True)

    df = pd.DataFrame.from_records(records)
    summary = write_summary(df, out)
    merged = pd.read_csv(out / "tables" / "aiming_sensitivity_records.csv")
    write_figures(merged, summary, out)
    write_report(summary, out)
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
