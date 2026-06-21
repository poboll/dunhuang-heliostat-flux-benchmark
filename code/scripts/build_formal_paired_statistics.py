#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKAGE = ROOT / "paper_submission" / "solar_energy_elsarticle_v8_strict_review_rescue"

DELTA_COL = "delta_peak_to_active_mean_pct_vs_baseline_same_strategy"
PRACTICAL_THRESHOLD_PCT = 1.0

ROLE_META = {
    "ctrl_radial_compact_015": ("$C_{rad-}$", "same-condition control"),
    "ctrl_radial_expand_015": ("$C_{rad+}$", "same-condition control"),
    "ctrl_ring_wave_012": ("$C_{wave}$", "same-condition control"),
    "deform_0276": ("$L_{opt}$", "TS-FPDA optical-upper"),
    "deform_0893": ("$L_{nom}$", "TS-FPDA nominal-proxy"),
    "deform_1387": ("$L_{rob}$", "TS-FPDA receiver-risk"),
    "deform_1822": ("$L_{ctrl}$", "TS-FPDA default-flux-control"),
    "joint_g02_0333": ("$J_{bal}$", "joint no-energy-loss balance"),
    "joint_g02_0303": ("$J_{gain}$", "joint energy-gated receiver candidate"),
    "joint_g04_0478": ("$J_{flux}$", "joint receiver-risk boundary"),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build formal paired statistics for the manuscript-facing reduced direct matrices."
    )
    parser.add_argument("--package", type=Path, default=DEFAULT_PACKAGE)
    parser.add_argument("--bootstrap", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=20260523)
    parser.add_argument("--threshold-pct", type=float, default=PRACTICAL_THRESHOLD_PCT)
    return parser.parse_args()


def short_strategy(value: str) -> str:
    return (
        str(value)
        .replace("staggered_levels:9:0.380:", "S9-p")
        .replace("visible_equator", "visible")
        .replace("five_point", "five-point")
    )


def label_for(layout_id: str, fallback: str | None = None) -> str:
    return ROLE_META.get(layout_id, (fallback or layout_id, ""))[0]


def role_for(layout_id: str, fallback: str | None = None) -> str:
    return ROLE_META.get(layout_id, ("", fallback or ""))[1] or (fallback or "")


def hodges_lehmann(values: np.ndarray) -> float:
    values = np.asarray(values, dtype=float)
    pairs = (values[:, None] + values[None, :]) / 2.0
    upper = pairs[np.triu_indices(values.size)]
    return float(np.median(upper))


def bootstrap_mean_ci(values: np.ndarray, rng: np.random.Generator, replicates: int) -> tuple[float, float]:
    draws = rng.choice(values, size=(replicates, values.size), replace=True)
    means = draws.mean(axis=1)
    low, high = np.percentile(means, [2.5, 97.5])
    return float(low), float(high)


def sign_test(values: np.ndarray) -> tuple[int, int, float]:
    nonzero = values[np.abs(values) > 1e-12]
    if nonzero.size == 0:
        return 0, 0, math.nan
    lower = int((nonzero < 0).sum())
    p_value = stats.binomtest(lower, n=int(nonzero.size), p=0.5, alternative="greater").pvalue
    return lower, int(nonzero.size), float(p_value)


def wilcoxon_less(values: np.ndarray) -> float:
    try:
        if np.allclose(values, 0.0):
            return math.nan
        return float(stats.wilcoxon(values, alternative="less", zero_method="wilcox").pvalue)
    except ValueError:
        return math.nan


def evidence_grade(mean_delta: float, ci_low: float, ci_high: float, lower_frac: float, threshold: float) -> str:
    if ci_high < -threshold:
        return "practical CI-supported reduction"
    if ci_high < 0.0:
        return "CI-supported reduction"
    if mean_delta < -threshold and lower_frac >= 2.0 / 3.0:
        return "directional practical reduction"
    if abs(mean_delta) < threshold and ci_low < 0.0 < ci_high:
        return "engineering-indistinguishable/uncertain"
    if mean_delta < 0.0:
        return "weak directional reduction"
    return "not supported or adverse"


def selected_values(relative: pd.DataFrame, layout_id: str, strategy: str) -> np.ndarray:
    subset = relative[(relative["layout_id"].astype(str) == layout_id) & (relative["strategy"].astype(str) == strategy)]
    values = subset[DELTA_COL].dropna().to_numpy(dtype=float)
    if values.size == 0:
        raise ValueError(f"No paired rows for {layout_id} / {strategy}")
    return values


def compute_row(
    matrix: str,
    view: str,
    layout_id: str,
    strategy: str,
    relative: pd.DataFrame,
    rng: np.random.Generator,
    replicates: int,
    threshold: float,
    role_hint: str | None = None,
    label_hint: str | None = None,
) -> dict[str, object]:
    values = selected_values(relative, layout_id, strategy)
    ci_low, ci_high = bootstrap_mean_ci(values, rng, replicates)
    sign_lower, sign_n, sign_p = sign_test(values)
    wilcoxon_p = wilcoxon_less(values)
    std = float(values.std(ddof=1)) if values.size > 1 else math.nan
    mean = float(values.mean())
    lower_frac = float((values < 0.0).mean())
    return {
        "matrix": matrix,
        "view": view,
        "layout_id": layout_id,
        "label": label_for(layout_id, label_hint),
        "role": role_for(layout_id, role_hint),
        "strategy": strategy,
        "strategy_short": short_strategy(strategy),
        "cases": int(values.size),
        "mean_delta_peak_pct": mean,
        "median_delta_peak_pct": float(np.median(values)),
        "hodges_lehmann_pct": hodges_lehmann(values),
        "std_delta_peak_pct": std,
        "cohen_dz": float(mean / std) if std and not math.isnan(std) and std > 0 else math.nan,
        "ci95_low_mean_pct": ci_low,
        "ci95_high_mean_pct": ci_high,
        "lower_fraction": lower_frac,
        "sign_lower_count": sign_lower,
        "sign_nonzero_count": sign_n,
        "sign_test_p_lower": sign_p,
        "wilcoxon_p_lower": wilcoxon_p,
        "practical_threshold_pct": threshold,
        "evidence_grade": evidence_grade(mean, ci_low, ci_high, lower_frac, threshold),
    }


def add_baseline_rows(pkg: Path, rng: np.random.Generator, replicates: int, threshold: float) -> list[dict[str, object]]:
    base = pkg / "supplementary_data" / "baseline_direct_soltrace_tables"
    rel = pd.read_csv(base / "tables" / "soltrace_sensitivity_relative.csv")
    best = pd.read_csv(base / "analysis" / "tables" / "baseline_direct_best_rows.csv")
    proxy = pd.read_csv(base / "analysis" / "tables" / "baseline_direct_proxy_selected_rows.csv")

    rows = []
    for row in best.itertuples(index=False):
        rows.append(
            compute_row(
                "baseline-control direct",
                "best-direct",
                str(row.layout_id),
                str(row.strategy),
                rel,
                rng,
                replicates,
                threshold,
                role_hint=getattr(row, "role", ""),
                label_hint=getattr(row, "label", ""),
            )
        )
    for row in proxy.itertuples(index=False):
        rows.append(
            compute_row(
                "baseline-control direct",
                "proxy-selected",
                str(row.layout_id),
                str(row.proxy_best_strategy),
                rel,
                rng,
                replicates,
                threshold,
                role_hint=getattr(row, "role", ""),
                label_hint=getattr(row, "label", ""),
            )
        )
    return rows


def add_joint_rows(pkg: Path, rng: np.random.Generator, replicates: int, threshold: float) -> list[dict[str, object]]:
    base = pkg / "supplementary_data" / "joint_direct_soltrace_tables"
    rel = pd.read_csv(base / "tables" / "soltrace_sensitivity_relative.csv")
    best = pd.read_csv(base / "analysis" / "tables" / "joint_direct_best_rows.csv")
    proxy = pd.read_csv(base / "analysis" / "tables" / "joint_direct_proxy_rows.csv")

    rows = []
    for row in best.itertuples(index=False):
        rows.append(
            compute_row(
                "joint direct promotion",
                "best-direct",
                str(row.layout_id),
                str(row.strategy),
                rel,
                rng,
                replicates,
                threshold,
                role_hint=getattr(row, "role_name", ""),
                label_hint=getattr(row, "label", ""),
            )
        )
    for row in proxy.itertuples(index=False):
        rows.append(
            compute_row(
                "joint direct promotion",
                "proxy-selected",
                str(row.layout_id),
                str(row.strategy),
                rel,
                rng,
                replicates,
                threshold,
                role_hint=getattr(row, "role_name", ""),
                label_hint=getattr(row, "label", ""),
            )
        )
    return rows


def add_v12_rows(pkg: Path, rng: np.random.Generator, replicates: int, threshold: float) -> list[dict[str, object]]:
    base = pkg / "supplementary_data" / "soltrace_v12_seed240k_tables"
    rel = pd.read_csv(base / "soltrace_sensitivity_relative.csv")
    proxy = pd.read_csv(base / "soltrace_proxy_strategy_summary.csv")
    nonbase = rel[rel["layout_id"] != "baseline_full"].copy()
    summary = (
        nonbase.groupby(["layout_id", "strategy"], as_index=False)
        .agg(mean_delta=(DELTA_COL, "mean"), median_delta=(DELTA_COL, "median"))
        .sort_values(["layout_id", "mean_delta", "median_delta"])
    )
    best = summary.groupby("layout_id", as_index=False).head(1)

    rows = []
    for row in best.itertuples(index=False):
        rows.append(
            compute_row(
                "V12 240k reduced direct",
                "best-direct",
                str(row.layout_id),
                str(row.strategy),
                rel,
                rng,
                replicates,
                threshold,
            )
        )
    for row in proxy.itertuples(index=False):
        rows.append(
            compute_row(
                "V12 240k reduced direct",
                "proxy-selected",
                str(row.layout_id),
                str(row.proxy_best_strategy),
                rel,
                rng,
                replicates,
                threshold,
            )
        )
    return rows


def markdown_table(df: pd.DataFrame, columns: list[str]) -> str:
    out = df.loc[:, columns].copy()
    renamed = {
        "matrix": "Matrix",
        "view": "View",
        "label": "Candidate",
        "strategy_short": "Strategy",
        "mean_delta_peak_pct": "Mean %",
        "ci": "95% CI %",
        "hodges_lehmann_pct": "HL %",
        "lower_fraction": "Lower frac.",
        "wilcoxon_p_lower": "Wilcoxon p",
        "evidence_grade": "Evidence",
    }
    out = out.rename(columns=renamed)
    headers = list(out.columns)
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in out.itertuples(index=False):
        cells = []
        for value in row:
            if isinstance(value, (float, np.floating)):
                if math.isnan(float(value)):
                    cells.append("n/a")
                elif abs(float(value)) < 0.001:
                    cells.append(f"{float(value):.2e}")
                else:
                    cells.append(f"{float(value):.3f}")
            else:
                cells.append(str(value))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def plot_key_rows(key: pd.DataFrame, out: Path) -> None:
    if key.empty:
        return
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
            "axes.unicode_minus": False,
        }
    )
    plot_df = key.copy()
    plot_df["plot_label"] = (
        plot_df["matrix"].str.replace(" reduced direct", "", regex=False)
        + " | "
        + plot_df["label"]
        + " | "
        + plot_df["strategy_short"]
        + " | "
        + plot_df["view"]
    )
    plot_df = plot_df.sort_values(["matrix", "view", "mean_delta_peak_pct"], ascending=[True, True, True])
    y = np.arange(len(plot_df))
    colors = np.where(plot_df["ci95_high_mean_pct"] < 0.0, "#2166AC", "#B7791F")
    fig_h = max(4.8, 0.34 * len(plot_df) + 1.0)
    fig, ax = plt.subplots(figsize=(8.4, fig_h), dpi=190)
    xerr = np.vstack(
        [
            plot_df["mean_delta_peak_pct"] - plot_df["ci95_low_mean_pct"],
            plot_df["ci95_high_mean_pct"] - plot_df["mean_delta_peak_pct"],
        ]
    )
    ax.errorbar(
        plot_df["mean_delta_peak_pct"],
        y,
        xerr=xerr,
        fmt="none",
        ecolor="#334155",
        elinewidth=0.9,
        capsize=2.5,
        zorder=1,
    )
    ax.scatter(plot_df["mean_delta_peak_pct"], y, s=28, color=colors, edgecolor="white", linewidth=0.5, zorder=2)
    ax.axvline(0.0, color="#111827", linewidth=0.8)
    ax.axvspan(-PRACTICAL_THRESHOLD_PCT, PRACTICAL_THRESHOLD_PCT, color="#E5E7EB", alpha=0.55, zorder=0)
    ax.set_yticks(y)
    ax.set_yticklabels(plot_df["plot_label"], fontsize=7.2)
    ax.invert_yaxis()
    ax.set_xlabel("Paired change in peak-to-active-mean concentration vs baseline (%)")
    ax.set_title("Formal paired statistics for reduced direct checks", fontsize=10.5)
    ax.grid(True, axis="x", color="#CBD5E1", linewidth=0.5, alpha=0.8)
    ax.text(
        0.99,
        0.02,
        "Grey band: +/-1% practical indistinguishability threshold",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=7.2,
        color="#475569",
    )
    fig.tight_layout()
    fig.savefig(out / "figures" / "fig_formal_paired_statistics.png", bbox_inches="tight")
    fig.savefig(out / "figures" / "fig_formal_paired_statistics.pdf", bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    args = parse_args()
    pkg = args.package if args.package.is_absolute() else ROOT / args.package
    out = pkg / "supplementary_data" / "formal_paired_statistics"
    (out / "tables").mkdir(parents=True, exist_ok=True)
    (out / "figures").mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    rows: list[dict[str, object]] = []
    rows.extend(add_baseline_rows(pkg, rng, args.bootstrap, args.threshold_pct))
    rows.extend(add_joint_rows(pkg, rng, args.bootstrap, args.threshold_pct))
    rows.extend(add_v12_rows(pkg, rng, args.bootstrap, args.threshold_pct))
    stats_df = pd.DataFrame.from_records(rows)
    stats_df["ci"] = stats_df.apply(
        lambda row: f"[{row.ci95_low_mean_pct:+.2f}, {row.ci95_high_mean_pct:+.2f}]", axis=1
    )
    stats_df.to_csv(out / "tables" / "formal_paired_statistics_all_selected.csv", index=False)

    key_mask = (
        ((stats_df["matrix"] == "baseline-control direct") & (stats_df["view"] == "best-direct"))
        | (stats_df["matrix"] == "joint direct promotion")
        | ((stats_df["matrix"] == "V12 240k reduced direct") & (stats_df["view"] == "best-direct"))
    )
    key = stats_df.loc[key_mask].copy()
    key.to_csv(out / "tables" / "formal_paired_statistics_key_rows.csv", index=False)
    plot_key_rows(key, out)

    supported = stats_df[stats_df["ci95_high_mean_pct"] < 0.0].copy()
    practical = stats_df[stats_df["ci95_high_mean_pct"] < -args.threshold_pct].copy()

    lines = [
        "# Formal Paired Statistics Audit",
        "",
        "This report treats each reduced direct matrix as a paired condition-level experiment. ",
        "For each selected layout--strategy row, the paired sample is the condition-level ",
        "change in peak-to-active-mean receiver concentration relative to the same baseline ",
        "under the same day, hour, and aiming strategy.",
        "",
        f"- Bootstrap replicates for mean confidence intervals: {args.bootstrap:,}",
        f"- Practical indistinguishability threshold: +/-{args.threshold_pct:.1f} percentage point",
        "- Sign and Wilcoxon tests use the one-sided alternative that the paired change is lower than zero.",
        "- The audit formalizes uncertainty for the existing reduced matrices; it is not a new full-field annual run.",
        "",
        "## Key Rows",
        "",
        markdown_table(
            key.sort_values(["matrix", "view", "mean_delta_peak_pct"]),
            [
                "matrix",
                "view",
                "label",
                "strategy_short",
                "mean_delta_peak_pct",
                "ci",
                "hodges_lehmann_pct",
                "lower_fraction",
                "wilcoxon_p_lower",
                "evidence_grade",
            ],
        ),
        "",
        "## CI-Supported Rows",
        "",
    ]
    if supported.empty:
        lines.append("No selected row has a bootstrap mean confidence interval entirely below zero.")
    else:
        lines.append(
            markdown_table(
                supported.sort_values(["ci95_high_mean_pct", "mean_delta_peak_pct"]).head(12),
                [
                    "matrix",
                    "view",
                    "label",
                    "strategy_short",
                    "mean_delta_peak_pct",
                    "ci",
                    "hodges_lehmann_pct",
                    "lower_fraction",
                    "wilcoxon_p_lower",
                    "evidence_grade",
                ],
            )
        )
    lines.extend(["", "## Practical-Threshold Rows", ""])
    if practical.empty:
        lines.append(
            "No selected row has its 95% bootstrap mean confidence interval entirely below the -1% practical threshold. "
            "The evidence is therefore best written as screening-level promotion rather than final engineering superiority."
        )
    else:
        lines.append(
            markdown_table(
                practical.sort_values(["ci95_high_mean_pct", "mean_delta_peak_pct"]),
                [
                    "matrix",
                    "view",
                    "label",
                    "strategy_short",
                    "mean_delta_peak_pct",
                    "ci",
                    "hodges_lehmann_pct",
                    "lower_fraction",
                    "wilcoxon_p_lower",
                    "evidence_grade",
                ],
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The formal statistics support the manuscript's conservative wording: role-level promotion is stronger than a single best-row claim.",
            "- Rows whose confidence intervals cross zero should remain directional or hypothesis-generating, even when their mean change is negative.",
            "- `J_flux` and `L_rob` are the clearest receiver-risk rows in the current direct evidence; `J_bal`, `J_gain`, and several V12 rows remain strategy- or sample-sensitive.",
            "- The +/-1% threshold is intentionally conservative: reductions smaller than this band should be treated as engineering-indistinguishable in the absence of plant-grade thermal validation.",
            "",
        ]
    )
    (out / "FORMAL_PAIRED_STATISTICS_REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
