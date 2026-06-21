#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
V12_DIR = ROOT / "supplementary_data" / "soltrace_v12_seed240k_tables"
RELATIVE = V12_DIR / "soltrace_sensitivity_relative.csv"
SUMMARY = V12_DIR / "soltrace_sensitivity_summary.csv"
PROXY = V12_DIR / "soltrace_proxy_strategy_summary.csv"
OUT_CSV = V12_DIR / "v12_bootstrap_ci.csv"
OUT_MD = V12_DIR / "V12_BOOTSTRAP_CI_REPORT.md"

ROLE_MAP = {
    "deform_0893": ("$L_{nom}$", "nominal-proxy"),
    "deform_1822": ("$L_{ctrl}$", "default-flux-control"),
    "deform_0276": ("$L_{opt}$", "optical-upper"),
    "deform_1387": ("$L_{rob}$", "receiver-risk"),
}


def short_strategy(value: str) -> str:
    return (
        str(value)
        .replace("staggered_levels:9:0.380:", "S9-p")
        .replace("visible_equator", "visible")
        .replace("five_point", "five-point")
    )


def evidence_grade(mean_delta: float, ci_high: float, lower_frac: float) -> str:
    if ci_high < 0 and lower_frac >= 0.67:
        return "CI-supported reduction"
    if mean_delta < 0 and lower_frac >= 0.56:
        return "directional reduction"
    if mean_delta < 0:
        return "weak reduction"
    return "not supported"


def bootstrap(values: np.ndarray, rng: np.random.Generator, n: int = 10000) -> tuple[float, float]:
    draws = rng.choice(values, size=(n, values.size), replace=True)
    means = draws.mean(axis=1)
    return tuple(np.percentile(means, [2.5, 97.5]))


def main() -> None:
    rel = pd.read_csv(RELATIVE)
    summary = pd.read_csv(SUMMARY)
    proxy = pd.read_csv(PROXY)
    rng = np.random.default_rng(20260522)

    rows: list[dict[str, object]] = []
    for (layout_id, strategy), group in rel.groupby(["layout_id", "strategy"], sort=False):
        if layout_id == "baseline_full":
            continue
        values = group["delta_peak_to_active_mean_pct_vs_baseline_same_strategy"].to_numpy(float)
        ci_low, ci_high = bootstrap(values, rng)
        rows.append(
            {
                "layout_id": layout_id,
                "role": ROLE_MAP.get(layout_id, ("", ""))[1],
                "role_label": ROLE_MAP.get(layout_id, ("", ""))[0],
                "strategy": strategy,
                "strategy_short": short_strategy(strategy),
                "cases": int(values.size),
                "mean_delta_peak_pct": float(values.mean()),
                "median_delta_peak_pct": float(np.median(values)),
                "ci95_low_mean_delta_pct": float(ci_low),
                "ci95_high_mean_delta_pct": float(ci_high),
                "share_lower_peak": float((values < 0).mean()),
            }
        )

    ci = pd.DataFrame(rows)
    ci["evidence_grade"] = [
        evidence_grade(row.mean_delta_peak_pct, row.ci95_high_mean_delta_pct, row.share_lower_peak)
        for row in ci.itertuples()
    ]
    ci.to_csv(OUT_CSV, index=False)

    best = (
        ci.sort_values(["layout_id", "mean_delta_peak_pct"], ascending=[True, True])
        .groupby("layout_id", as_index=False)
        .head(1)
        .copy()
    )
    proxy_rows = proxy.merge(
        ci,
        left_on=["layout_id", "proxy_best_strategy"],
        right_on=["layout_id", "strategy"],
        suffixes=("_proxy", ""),
    )

    lines = [
        "# V12 Bootstrap Confidence Audit",
        "",
        "This report bootstraps the condition-level V12 reduced PySolTrace peak-to-active-mean deltas.",
        "It is used as a reviewer-facing uncertainty check, not as a new optimization pass.",
        "",
        "## Best direct row by layout",
        "",
        "| Layout | Role | Strategy | Mean % | 95% bootstrap CI | Lower fraction | Evidence grade |",
        "|---|---|---|---:|---:|---:|---|",
    ]
    for row in best.sort_values("mean_delta_peak_pct").itertuples():
        lines.append(
            f"| {row.role_label} | {row.role} | {row.strategy_short} | "
            f"{row.mean_delta_peak_pct:.2f} | "
            f"[{row.ci95_low_mean_delta_pct:.2f}, {row.ci95_high_mean_delta_pct:.2f}] | "
            f"{row.share_lower_peak:.2f} | {row.evidence_grade} |"
        )

    lines.extend(
        [
            "",
            "## Proxy-selected rows",
            "",
            "| Layout | Role | Strategy | Mean % | 95% bootstrap CI | Lower fraction | Evidence grade |",
            "|---|---|---|---:|---:|---:|---|",
        ]
    )
    for row in proxy_rows.sort_values("layout_id").itertuples():
        lines.append(
            f"| {row.role_label} | {row.role} | {row.strategy_short} | "
            f"{row.mean_delta_peak_pct:.2f} | "
            f"[{row.ci95_low_mean_delta_pct:.2f}, {row.ci95_high_mean_delta_pct:.2f}] | "
            f"{row.share_lower_peak:.2f} | {row.evidence_grade} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The best direct V12 rows support directional reductions for $L_{nom}$ and $L_{ctrl}$, but their bootstrap confidence intervals still cross zero.",
            "- $L_{opt}$ remains weak at the V12 scale and should not be described as a receiver-risk-safe optical winner.",
            "- $L_{rob}$ is nearly neutral in V12, so its earlier receiver-risk role should be kept as a queue member rather than a headline winner.",
            "- The correct manuscript claim is role-level screening usefulness, not final aiming-phase optimality.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
