#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_QUEUE = ROOT / "server_outputs" / "strong_baseline_direct_promotion_queue_20260523"
DEFAULT_DIRECT = DEFAULT_QUEUE / "soltrace_core_27cond_20260524"
DEFAULT_PACKAGE = ROOT / "paper_submission" / "solar_energy_elsarticle_v8_strict_review_rescue"

ROLE_META = {
    "baseline_full": ("$L_0$", "reference", "baseline"),
    "deform_0893": ("$L_{nom}$", "held-out TS-FPDA nominal", "tsfpda"),
    "deform_1387": ("$L_{rob}$", "held-out TS-FPDA receiver-risk", "tsfpda"),
    "ctrl_radial_expand_015": ("$C_{rad+}$", "simple radial-control baseline", "control"),
    "joint_g04_0478": ("$J_{flux}$", "joint receiver-boundary", "joint"),
    "joint_g02_0333": ("$J_{bal}$", "joint balance candidate", "joint"),
    "sb_hy_energy": ("$B_{hy,E}$", "hybrid annual-positive strong baseline", "strong"),
    "sb_pf_flux": ("$B_{pf,R}$", "pattern-free receiver-pressure strong baseline", "strong"),
    "sb_hs_flux": ("$B_{hs,R}$", "slider-like receiver-pressure strong baseline", "strong"),
}

LAYOUT_ORDER = [
    "deform_0893",
    "deform_1387",
    "ctrl_radial_expand_015",
    "joint_g04_0478",
    "joint_g02_0333",
    "sb_hy_energy",
    "sb_pf_flux",
    "sb_hs_flux",
]

FAMILY_COLORS = {
    "baseline": "#64748B",
    "tsfpda": "#2563EB",
    "control": "#B7791F",
    "joint": "#0E7490",
    "strong": "#7C3AED",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Aggregate and gate the same-run reduced PySolTrace matrix for the strong-baseline "
            "direct-promotion queue."
        )
    )
    parser.add_argument("--queue", type=Path, default=DEFAULT_QUEUE)
    parser.add_argument("--direct", type=Path, default=DEFAULT_DIRECT)
    parser.add_argument("--package", type=Path, default=DEFAULT_PACKAGE)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--days", default="20,80,110,140,172,200,230,266,326")
    parser.add_argument("--hours", default="10,12,14")
    parser.add_argument("--bootstrap", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=20260524)
    parser.add_argument("--copy-to-package", action="store_true")
    return parser.parse_args()


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def parse_ints(value: str) -> list[int]:
    return [int(x.strip()) for x in value.split(",") if x.strip()]


def parse_floats(value: str) -> list[float]:
    return [float(x.strip()) for x in value.split(",") if x.strip()]


def fmt_hour(hour: float) -> str:
    if abs(hour - round(hour)) < 1e-9:
        return str(int(round(hour)))
    return str(hour).replace(".", "p")


def short_strategy(value: str) -> str:
    return (
        str(value)
        .replace("staggered_levels:9:0.380:", "S9-p")
        .replace("visible_equator", "visible")
        .replace("five_point", "five-point")
    )


def label_for(layout_id: str) -> str:
    return ROLE_META.get(layout_id, (layout_id, layout_id, "other"))[0]


def role_for(layout_id: str) -> str:
    return ROLE_META.get(layout_id, (layout_id, layout_id, "other"))[1]


def family_for(layout_id: str) -> str:
    return ROLE_META.get(layout_id, (layout_id, layout_id, "other"))[2]


def expected_conditions(days: list[int], hours: list[float]) -> list[str]:
    return [f"d{day}_h{fmt_hour(hour)}" for day in days for hour in hours]


def load_proxy_best(queue: Path) -> dict[str, str]:
    path = queue / "aiming_proxy" / "best_aiming_by_layout.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    return dict(zip(df["layout_id"].astype(str), df["strategy"].astype(str), strict=False))


def aggregate_condition_summaries(
    direct: Path,
    days: list[int],
    hours: list[float],
    proxy_best: dict[str, str],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, list[str]]:
    frames: list[pd.DataFrame] = []
    missing: list[str] = []
    for day in days:
        for hour in hours:
            condition_id = f"d{day}_h{fmt_hour(hour)}"
            path = direct / condition_id / "tables" / "soltrace_aimpoint_summary.csv"
            if not path.exists():
                missing.append(condition_id)
                continue
            df = pd.read_csv(path)
            df["condition_id"] = condition_id
            frames.append(df)

    tables_dir = direct / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)
    if not frames:
        empty = pd.DataFrame()
        return empty, empty, empty, missing

    all_df = pd.concat(frames, axis=0, ignore_index=True)
    all_df.to_csv(tables_dir / "soltrace_sensitivity_all.csv", index=False)

    baseline = all_df[all_df["layout_id"] == "baseline_full"].copy()
    baseline = baseline.rename(
        columns={
            "peak_to_active_mean": "baseline_peak_to_active_mean",
            "active_flux_cv": "baseline_active_flux_cv",
            "receiver_intercept_per_requested_ray": "baseline_receiver_intercept_per_requested_ray",
            "total_receiver_power_proxy_w": "baseline_total_receiver_power_proxy_w",
        }
    )
    rel = all_df.merge(
        baseline[
            [
                "sun_day",
                "sun_hour",
                "strategy",
                "baseline_peak_to_active_mean",
                "baseline_active_flux_cv",
                "baseline_receiver_intercept_per_requested_ray",
                "baseline_total_receiver_power_proxy_w",
            ]
        ],
        on=["sun_day", "sun_hour", "strategy"],
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
    rel.to_csv(tables_dir / "soltrace_sensitivity_relative.csv", index=False)

    nonbase = rel[rel["layout_id"] != "baseline_full"].copy()
    summary = (
        nonbase.groupby(["layout_id", "strategy"], as_index=False)
        .agg(
            cases=("delta_peak_to_active_mean_pct_vs_baseline_same_strategy", "count"),
            median_delta_peak_pct=("delta_peak_to_active_mean_pct_vs_baseline_same_strategy", "median"),
            mean_delta_peak_pct=("delta_peak_to_active_mean_pct_vs_baseline_same_strategy", "mean"),
            p10_delta_peak_pct=(
                "delta_peak_to_active_mean_pct_vs_baseline_same_strategy",
                lambda x: np.percentile(x, 10),
            ),
            p90_delta_peak_pct=(
                "delta_peak_to_active_mean_pct_vs_baseline_same_strategy",
                lambda x: np.percentile(x, 90),
            ),
            share_lower_peak=("delta_peak_to_active_mean_pct_vs_baseline_same_strategy", lambda x: float((x < 0).mean())),
            median_delta_cv_pct=("delta_active_cv_pct_vs_baseline_same_strategy", "median"),
            median_delta_intercept_pctpt=("delta_receiver_intercept_pctpt_vs_baseline_same_strategy", "median"),
        )
        .sort_values(["mean_delta_peak_pct", "median_delta_peak_pct"])
    )
    summary.to_csv(tables_dir / "soltrace_sensitivity_summary.csv", index=False)

    proxy_records: list[dict[str, object]] = []
    for layout_id, strategy in proxy_best.items():
        if layout_id == "baseline_full":
            continue
        subset = rel[(rel["layout_id"] == layout_id) & (rel["strategy"] == strategy)].copy()
        values = subset["delta_peak_to_active_mean_pct_vs_baseline_same_strategy"].dropna().to_numpy(dtype=float)
        if len(values) == 0:
            continue
        proxy_records.append(
            {
                "layout_id": layout_id,
                "proxy_best_strategy": strategy,
                "cases": int(len(values)),
                "median_delta_peak_pct": float(np.median(values)),
                "mean_delta_peak_pct": float(values.mean()),
                "p10_delta_peak_pct": float(np.percentile(values, 10)),
                "p90_delta_peak_pct": float(np.percentile(values, 90)),
                "share_lower_peak": float((values < 0).mean()),
                "best_condition_delta_pct": float(values.min()),
                "worst_condition_delta_pct": float(values.max()),
                "median_delta_intercept_pctpt": float(
                    subset["delta_receiver_intercept_pctpt_vs_baseline_same_strategy"].median()
                ),
            }
        )
    proxy = pd.DataFrame.from_records(proxy_records)
    if not proxy.empty:
        proxy = proxy.sort_values(["mean_delta_peak_pct", "median_delta_peak_pct"])
    proxy.to_csv(tables_dir / "soltrace_proxy_strategy_summary.csv", index=False)
    return all_df, rel, summary, missing


def build_best_rows(summary: pd.DataFrame) -> pd.DataFrame:
    if summary.empty or "layout_id" not in summary.columns:
        return pd.DataFrame()
    best = (
        summary[summary["layout_id"].isin(LAYOUT_ORDER)]
        .sort_values(["layout_id", "mean_delta_peak_pct", "median_delta_peak_pct"])
        .groupby("layout_id", as_index=False)
        .head(1)
        .copy()
    )
    best["view"] = "best-direct"
    best["selected_strategy"] = best["strategy"]
    return annotate_rows(best)


def build_proxy_rows(rel: pd.DataFrame, proxy_best: dict[str, str]) -> pd.DataFrame:
    if rel.empty or not {"layout_id", "strategy"}.issubset(rel.columns):
        return pd.DataFrame()
    records: list[dict[str, object]] = []
    for layout_id in LAYOUT_ORDER:
        strategy = proxy_best.get(layout_id)
        if not strategy:
            continue
        subset = rel[(rel["layout_id"] == layout_id) & (rel["strategy"] == strategy)].copy()
        values = subset["delta_peak_to_active_mean_pct_vs_baseline_same_strategy"].dropna().to_numpy(dtype=float)
        if len(values) == 0:
            continue
        records.append(
            {
                "layout_id": layout_id,
                "strategy": strategy,
                "selected_strategy": strategy,
                "view": "proxy-selected",
                "cases": int(len(values)),
                "mean_delta_peak_pct": float(values.mean()),
                "median_delta_peak_pct": float(np.median(values)),
                "p10_delta_peak_pct": float(np.percentile(values, 10)),
                "p90_delta_peak_pct": float(np.percentile(values, 90)),
                "share_lower_peak": float((values < 0).mean()),
                "median_delta_cv_pct": float(subset["delta_active_cv_pct_vs_baseline_same_strategy"].median()),
                "median_delta_intercept_pctpt": float(
                    subset["delta_receiver_intercept_pctpt_vs_baseline_same_strategy"].median()
                ),
            }
        )
    return annotate_rows(pd.DataFrame.from_records(records))


def annotate_rows(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    out["label"] = out["layout_id"].map(label_for)
    out["role"] = out["layout_id"].map(role_for)
    out["family"] = out["layout_id"].map(family_for)
    out["strategy_short"] = out["selected_strategy"].map(short_strategy)
    out["order"] = out["layout_id"].map({layout_id: i for i, layout_id in enumerate(LAYOUT_ORDER)})
    return out.sort_values(["order"]).drop(columns=["order"])


def bootstrap_ci(
    rel: pd.DataFrame,
    selected: pd.DataFrame,
    replicates: int,
    seed: int,
) -> pd.DataFrame:
    if selected.empty or "layout_id" not in selected.columns:
        return pd.DataFrame()
    rng = np.random.default_rng(seed)
    records: list[dict[str, object]] = []
    for row in selected.itertuples(index=False):
        subset = rel[(rel["layout_id"] == row.layout_id) & (rel["strategy"] == row.selected_strategy)]
        values = subset["delta_peak_to_active_mean_pct_vs_baseline_same_strategy"].dropna().to_numpy(dtype=float)
        if len(values) == 0:
            continue
        boot = rng.choice(values, size=(replicates, len(values)), replace=True).mean(axis=1)
        records.append(
            {
                "view": row.view,
                "layout_id": row.layout_id,
                "label": row.label,
                "role": row.role,
                "family": row.family,
                "strategy": row.selected_strategy,
                "strategy_short": row.strategy_short,
                "cases": int(len(values)),
                "mean_delta_peak_pct": float(values.mean()),
                "median_delta_peak_pct": float(np.median(values)),
                "ci95_low_pct": float(np.percentile(boot, 2.5)),
                "ci95_high_pct": float(np.percentile(boot, 97.5)),
                "share_lower_peak": float((values < 0).mean()),
                "p10_delta_peak_pct": float(np.percentile(values, 10)),
                "p90_delta_peak_pct": float(np.percentile(values, 90)),
                "median_delta_intercept_pctpt": float(
                    subset["delta_receiver_intercept_pctpt_vs_baseline_same_strategy"].median()
                ),
            }
        )
    out = pd.DataFrame.from_records(records)
    if out.empty:
        return out
    view_order = {"proxy-selected": 0, "best-direct": 1}
    out["order"] = out["layout_id"].map({layout_id: i for i, layout_id in enumerate(LAYOUT_ORDER)})
    out["view_order"] = out["view"].map(view_order)
    return out.sort_values(["order", "view_order"]).drop(columns=["order", "view_order"])


def load_prior_gate(package: Path) -> pd.DataFrame:
    path = package / "supplementary_data" / "strong_baseline_promotion_gate" / "tables" / "strong_baseline_promotion_gate_summary.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def build_gate(
    queue: Path,
    package: Path,
    ci: pd.DataFrame,
    missing: list[str],
    expected_count: int,
) -> tuple[pd.DataFrame, dict[str, object]]:
    queue_df = pd.read_csv(queue / "tables" / "direct_promotion_queue.csv")
    queue_df = queue_df[queue_df["layout_id"].isin(["baseline_full"] + LAYOUT_ORDER)].copy()
    queue_df["label"] = queue_df["layout_id"].map(label_for)
    queue_df["role_name"] = queue_df["layout_id"].map(role_for)
    queue_df["family"] = queue_df["layout_id"].map(family_for)
    prior = load_prior_gate(package)
    prior_cols = [
        "layout_id",
        "multiyear_mean_annual_delta_pct",
        "solarpilot_36_delta_peak_ratio_pct",
        "fluxday12_delta_peak_ratio_pct",
        "delta_aiming_proxy_pct",
        "direct_evidence_grade",
    ]
    if not prior.empty:
        queue_df = queue_df.merge(prior[[c for c in prior_cols if c in prior.columns]], on="layout_id", how="left")

    ci_columns = [
        "view",
        "layout_id",
        "strategy_short",
        "cases",
        "mean_delta_peak_pct",
        "ci95_low_pct",
        "ci95_high_pct",
        "share_lower_peak",
        "median_delta_intercept_pctpt",
    ]
    if ci.empty or "view" not in ci.columns:
        ci = pd.DataFrame(columns=ci_columns)
    proxy_ci = ci[ci["view"] == "proxy-selected"].copy()
    best_ci = ci[ci["view"] == "best-direct"].copy()
    proxy_ci = proxy_ci.add_prefix("proxy_")
    best_ci = best_ci.add_prefix("best_")
    for column in [
        "proxy_layout_id",
        "proxy_strategy_short",
        "proxy_cases",
        "proxy_mean_delta_peak_pct",
        "proxy_ci95_low_pct",
        "proxy_ci95_high_pct",
        "best_layout_id",
        "best_strategy_short",
        "best_cases",
        "best_mean_delta_peak_pct",
        "best_ci95_low_pct",
        "best_ci95_high_pct",
    ]:
        if column.startswith("proxy_") and column not in proxy_ci.columns:
            proxy_ci[column] = np.nan
        if column.startswith("best_") and column not in best_ci.columns:
            best_ci[column] = np.nan
    gate = queue_df.merge(proxy_ci, left_on="layout_id", right_on="proxy_layout_id", how="left")
    gate = gate.merge(best_ci, left_on="layout_id", right_on="best_layout_id", how="left")

    def numeric_or_zero(value: object) -> int:
        if pd.isna(value):
            return 0
        return int(value)

    def status(row: pd.Series) -> str:
        if row["layout_id"] == "baseline_full":
            return "paired_baseline"
        proxy_complete = numeric_or_zero(row.get("proxy_cases", 0)) >= expected_count and not missing
        best_complete = numeric_or_zero(row.get("best_cases", 0)) >= expected_count and not missing
        proxy_ci_high = row.get("proxy_ci95_high_pct", np.nan)
        best_ci_high = row.get("best_ci95_high_pct", np.nan)
        proxy_mean = row.get("proxy_mean_delta_peak_pct", np.nan)
        if proxy_complete and pd.notna(proxy_ci_high) and proxy_ci_high < 0.0:
            if str(row["layout_id"]).startswith("sb_"):
                return "new_same_run_direct_supported_strong_baseline"
            return "same_run_proxy_strategy_direct_supported"
        if best_complete and pd.notna(best_ci_high) and best_ci_high < 0.0:
            return "best_direct_supported_alternative_strategy"
        if pd.notna(proxy_mean) and proxy_mean < 0.0:
            return "directional_not_promoted"
        if pd.notna(proxy_mean):
            return "not_supported_or_adverse"
        return "not_yet_available"

    def writeback(row: pd.Series) -> str:
        state = status(row)
        if state == "new_same_run_direct_supported_strong_baseline":
            return "write_as_new_direct_supported_strong_baseline_role"
        if state == "same_run_proxy_strategy_direct_supported":
            return "write_as_same_run_direct_supported_context"
        if state == "best_direct_supported_alternative_strategy":
            return "write_strategy_sensitivity_not_proxy_promotion"
        if state == "directional_not_promoted":
            return "supplementary_directional_only"
        if state == "paired_baseline":
            return "reference_only"
        return "do_not_write_main_text"

    gate["direct_promotion_status"] = gate.apply(status, axis=1)
    gate["writeback_recommendation"] = gate.apply(writeback, axis=1)
    gate["complete_matrix"] = not missing
    gate["expected_conditions"] = expected_count
    strong_ids = {"sb_hy_energy", "sb_pf_flux", "sb_hs_flux"}
    newly_supported = gate[
        gate["layout_id"].isin(strong_ids)
        & gate["direct_promotion_status"].eq("new_same_run_direct_supported_strong_baseline")
    ]["layout_id"].tolist()
    adverse = gate[
        gate["layout_id"].isin(strong_ids)
        & gate["direct_promotion_status"].isin(["not_supported_or_adverse", "directional_not_promoted"])
    ]["layout_id"].tolist()
    decision = {
        "expected_conditions": expected_count,
        "completed_conditions": expected_count - len(missing),
        "missing_conditions": missing,
        "complete_matrix": not missing,
        "newly_supported_strong_baseline_rows": newly_supported,
        "nonpromoted_or_adverse_strong_baseline_rows": adverse,
        "main_text_writeback_allowed": bool(not missing and newly_supported),
        "safe_rule": (
            "Write new strong-baseline claims only when the complete same-run direct matrix gives a "
            "proxy-selected 95% bootstrap CI below zero. Otherwise keep rows as supplementary or internal evidence."
        ),
    }
    return gate, decision


def set_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
            "font.size": 8.2,
            "axes.titlesize": 9.2,
            "axes.labelsize": 8.2,
            "xtick.labelsize": 7.2,
            "ytick.labelsize": 7.2,
            "legend.fontsize": 7.1,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
            "axes.edgecolor": "#334155",
            "axes.linewidth": 0.7,
            "axes.grid": True,
            "grid.color": "#D7DEE8",
            "grid.alpha": 0.70,
            "grid.linewidth": 0.5,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def plot_ci_panel(ax: plt.Axes, df: pd.DataFrame, title: str) -> None:
    plot = df[df["layout_id"].isin(LAYOUT_ORDER)].copy()
    if plot.empty:
        ax.text(0.5, 0.5, "No direct rows yet", ha="center", va="center", transform=ax.transAxes)
        ax.set_axis_off()
        return
    plot["order"] = plot["layout_id"].map({layout_id: i for i, layout_id in enumerate(LAYOUT_ORDER)})
    plot = plot.sort_values("order", ascending=False)
    y = np.arange(len(plot))
    x = plot["mean_delta_peak_pct"].to_numpy(dtype=float)
    xerr = np.vstack(
        [
            x - plot["ci95_low_pct"].to_numpy(dtype=float),
            plot["ci95_high_pct"].to_numpy(dtype=float) - x,
        ]
    )
    colors = plot["family"].map(FAMILY_COLORS).fillna("#64748B").tolist()
    ax.errorbar(x, y, xerr=xerr, fmt="none", ecolor="#94A3B8", elinewidth=1.0, capsize=2.6, zorder=1)
    ax.scatter(x, y, s=34, color=colors, edgecolor="white", linewidth=0.7, zorder=2)
    for xi, yi, strategy in zip(x, y, plot["strategy_short"], strict=False):
        ax.annotate(strategy, (xi, yi), xytext=(4, 0), textcoords="offset points", va="center", fontsize=6.8)
    ax.axvline(0.0, color="#111827", linewidth=0.8)
    ax.axvline(-1.0, color="#DC2626", linewidth=0.8, linestyle="--")
    ax.set_yticks(y)
    ax.set_yticklabels(plot["label"])
    ax.set_xlabel("Peak / active-mean change vs paired baseline (%)")
    ax.set_title(title, loc="left")


def write_figure(ci: pd.DataFrame, gate: pd.DataFrame, out: Path) -> None:
    set_style()
    if ci.empty or "view" not in ci.columns:
        ci = pd.DataFrame(columns=["view", "layout_id"])
    fig, axes = plt.subplots(1, 3, figsize=(14.2, 4.45), dpi=240)
    plot_ci_panel(axes[0], ci[ci["view"] == "proxy-selected"], "(a) Proxy-selected direct row")
    plot_ci_panel(axes[1], ci[ci["view"] == "best-direct"], "(b) Best direct row")

    ax = axes[2]
    plot = gate[gate["layout_id"].isin(LAYOUT_ORDER)].copy()
    if {"multiyear_mean_annual_delta_pct", "proxy_mean_delta_peak_pct"}.issubset(plot.columns):
        colors = plot["family"].map(FAMILY_COLORS).fillna("#64748B")
        ax.scatter(
            plot["multiyear_mean_annual_delta_pct"],
            plot["proxy_mean_delta_peak_pct"],
            s=48,
            c=colors,
            edgecolor="white",
            linewidth=0.7,
            zorder=3,
        )
        for row in plot.itertuples(index=False):
            if pd.notna(row.multiyear_mean_annual_delta_pct) and pd.notna(row.proxy_mean_delta_peak_pct):
                ax.annotate(
                    label_for(row.layout_id),
                    (row.multiyear_mean_annual_delta_pct, row.proxy_mean_delta_peak_pct),
                    xytext=(3, 3),
                    textcoords="offset points",
                    fontsize=7,
                )
        ax.axhline(0.0, color="#111827", linewidth=0.8)
        ax.axvline(0.0, color="#111827", linewidth=0.8)
        ax.set_xlabel("Multi-year annual optical-proxy delta (%)")
        ax.set_ylabel("Proxy-selected direct peak-ratio delta (%)")
        ax.set_title("(c) Annual vs direct gate", loc="left")
    else:
        ax.text(0.5, 0.5, "Prior annual gate unavailable", ha="center", va="center", transform=ax.transAxes)
        ax.set_axis_off()

    handles = [
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=color, markeredgecolor="white", markersize=7, label=family)
        for family, color in FAMILY_COLORS.items()
        if family != "baseline"
    ]
    fig.legend(handles=handles, loc="upper center", ncol=4, frameon=False, bbox_to_anchor=(0.54, 1.02))
    fig.tight_layout(w_pad=1.8)
    fig.savefig(out / "figures" / "fig_strong_baseline_direct_promotion.png", bbox_inches="tight")
    fig.savefig(out / "figures" / "fig_strong_baseline_direct_promotion.pdf", bbox_inches="tight")
    plt.close(fig)


def markdown_table(df: pd.DataFrame, cols: list[str]) -> str:
    if df.empty:
        return "_No rows available._"
    view = df.loc[:, [c for c in cols if c in df.columns]].copy()
    lines = [
        "| " + " | ".join(view.columns) + " |",
        "| " + " | ".join(["---"] * len(view.columns)) + " |",
    ]
    for row in view.itertuples(index=False):
        cells: list[str] = []
        for value in row:
            if isinstance(value, (float, np.floating)):
                cells.append(f"{float(value):.3f}")
            elif pd.isna(value):
                cells.append("n/a")
            else:
                cells.append(str(value))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def write_report(gate: pd.DataFrame, ci: pd.DataFrame, decision: dict[str, object], out: Path) -> None:
    report = [
        "# Strong-Baseline Same-Run Direct SolTrace Audit",
        "",
        "This report aggregates the same-run reduced PySolTrace matrix for the strong-baseline direct-promotion queue.",
        "It is a writeback gate: a result is promoted only when the complete matrix supports the proxy-selected layout--aiming row.",
        "",
        "## Completion",
        "",
        f"- Completed conditions: {decision['completed_conditions']} / {decision['expected_conditions']}.",
        f"- Missing conditions: `{decision['missing_conditions']}`.",
        f"- Complete matrix: `{decision['complete_matrix']}`.",
        "",
        "## Gate Decision",
        "",
        f"- Newly supported strong-baseline rows: `{decision['newly_supported_strong_baseline_rows']}`.",
        f"- Non-promoted or adverse strong-baseline rows: `{decision['nonpromoted_or_adverse_strong_baseline_rows']}`.",
        f"- Main-text writeback allowed: `{decision['main_text_writeback_allowed']}`.",
        f"- Safe rule: {decision['safe_rule']}",
        "",
        "## Gate Summary",
        "",
        markdown_table(
            gate,
            [
                "symbol",
                "layout_id",
                "role",
                "tier",
                "multiyear_mean_annual_delta_pct",
                "proxy_strategy_short",
                "proxy_cases",
                "proxy_mean_delta_peak_pct",
                "proxy_ci95_low_pct",
                "proxy_ci95_high_pct",
                "best_strategy_short",
                "best_mean_delta_peak_pct",
                "best_ci95_low_pct",
                "best_ci95_high_pct",
                "direct_promotion_status",
                "writeback_recommendation",
            ],
        ),
        "",
        "## Bootstrap Rows",
        "",
        markdown_table(
            ci,
            [
                "view",
                "label",
                "layout_id",
                "strategy_short",
                "cases",
                "mean_delta_peak_pct",
                "ci95_low_pct",
                "ci95_high_pct",
                "share_lower_peak",
                "median_delta_intercept_pctpt",
            ],
        ),
        "",
        "## Manuscript Use",
        "",
        "- If the matrix is incomplete, do not write new claims into the manuscript.",
        "- If a strong-baseline proxy-selected row has a complete 95% CI below zero, it can be written as a same-run direct-supported role, not as a final plant redesign.",
        "- If only a best-direct alternative strategy passes, write it as strategy sensitivity and keep the proxy-selected queue claim bounded.",
        "- Weak, adverse, or incomplete rows should remain supplementary/internal and should not be used to inflate novelty.",
        "",
    ]
    (out / "STRONG_BASELINE_DIRECT_SOLTRACE_AUDIT.md").write_text("\n".join(report), encoding="utf-8")


def copy_outputs(out: Path, package: Path) -> None:
    target = package / "supplementary_data" / "strong_baseline_direct_soltrace_tables"
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(out, target)


def main() -> int:
    args = parse_args()
    queue = resolve(args.queue)
    direct = resolve(args.direct)
    package = resolve(args.package)
    out = resolve(args.out) if args.out else direct / "analysis"
    (out / "tables").mkdir(parents=True, exist_ok=True)
    (out / "figures").mkdir(parents=True, exist_ok=True)

    days = parse_ints(args.days)
    hours = parse_floats(args.hours)
    expected = expected_conditions(days, hours)
    proxy_best = load_proxy_best(queue)
    _all_df, rel, summary, missing = aggregate_condition_summaries(direct, days, hours, proxy_best)
    best_rows = build_best_rows(summary)
    proxy_rows = build_proxy_rows(rel, proxy_best)
    ci = pd.concat(
        [
            bootstrap_ci(rel, proxy_rows, args.bootstrap, args.seed),
            bootstrap_ci(rel, best_rows, args.bootstrap, args.seed + 29),
        ],
        axis=0,
        ignore_index=True,
    )
    if not ci.empty:
        ci.to_csv(out / "tables" / "strong_direct_bootstrap_ci.csv", index=False)
    best_rows.to_csv(out / "tables" / "strong_direct_best_rows.csv", index=False)
    proxy_rows.to_csv(out / "tables" / "strong_direct_proxy_selected_rows.csv", index=False)

    gate, decision = build_gate(queue, package, ci, missing, len(expected))
    gate.to_csv(out / "tables" / "strong_direct_gate_summary.csv", index=False)
    (out / "gate_decision.json").write_text(json.dumps(decision, indent=2) + "\n", encoding="utf-8")
    write_figure(ci, gate, out)
    write_report(gate, ci, decision, out)
    if args.copy_to_package:
        copy_outputs(out, package)

    print(f"Wrote {out}")
    print(json.dumps(decision, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
