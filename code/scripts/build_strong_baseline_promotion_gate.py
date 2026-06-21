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
PACKAGE = ROOT / "paper_submission" / "solar_energy_elsarticle_v8_strict_review_rescue"
QUEUE = ROOT / "server_outputs" / "strong_baseline_direct_promotion_queue_20260523"


DISPLAY_LABELS = {
    "baseline_full": r"$L_0$",
    "deform_0276": r"$L_{opt}$",
    "deform_0893": r"$L_{nom}$",
    "deform_1387": r"$L_{rob}$",
    "ctrl_radial_expand_015": r"$C_{rad+}$",
    "joint_g02_0333": r"$J_{bal}$",
    "joint_g04_0478": r"$J_{flux}$",
    "joint_g02_0303": r"$J_{gain}$",
    "sb_hy_energy": r"$B_{hy,E}$",
    "sb_pf_flux": r"$B_{pf,R}$",
    "sb_hs_flux": r"$B_{hs,R}$",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build a conservative promotion gate for the strong-baseline direct queue. "
            "The gate merges annual, SolarPILOT default-flux, aiming-proxy, geometry, "
            "and completed reduced-direct evidence, then decides what can be written."
        )
    )
    parser.add_argument("--package", type=Path, default=PACKAGE)
    parser.add_argument("--queue", type=Path, default=QUEUE)
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "server_outputs" / "strong_baseline_promotion_gate_20260524",
    )
    return parser.parse_args()


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def merge_tables(package: Path, queue: Path) -> pd.DataFrame:
    queue_df = read_csv(queue / "tables/direct_promotion_queue.csv")
    constrained = read_csv(
        package
        / "supplementary_data/geometry_explainability_advantage/tables/constrained_advantage_summary.csv"
    )
    annual = read_csv(
        package / "supplementary_data/multiyear_annual_proxy_gate/tables/multiyear_annual_proxy_summary.csv"
    )
    interp = read_csv(
        package
        / "supplementary_data/annual_interpolation_robustness_gate/tables/annual_interpolation_robustness_summary.csv"
    )
    flux_res = read_csv(
        package / "supplementary_data/flux_resolution_gate/tables/flux_resolution_selected_comparison.csv"
    )
    flux_day = read_csv(
        package / "supplementary_data/flux_day_sampling_gate/tables/flux_day_sampling_selected_comparison.csv"
    )
    aiming = read_csv(queue / "aiming_proxy/best_aiming_by_layout.csv")

    table = queue_df.merge(
        constrained[
            [
                "layout_id",
                "label",
                "family",
                "delta_annual_thermal_proxy_mwh_reported_tmy_scaled_pct",
                "delta_default_flux_ratio_pct",
                "delta_aiming_proxy_pct",
                "direct_mean_delta_peak_pct",
                "direct_ci95_low_pct",
                "direct_ci95_high_pct",
                "direct_ci",
                "direct_evidence_grade",
                "delta_active_frac_above_baseline_p99_pct_pctpt",
                "mean_displacement_m",
                "p95_displacement_m",
                "nearest_neighbor_p05_m",
                "sector_l1_shift_pct_of_field",
                "constrained_interpretation",
            ]
        ],
        on="layout_id",
        how="left",
    )
    table["label"] = table["label"].fillna(table["symbol"])
    table = table.merge(
        annual[
            [
                "layout_id",
                "mean_delta_annual_pct",
                "min_delta_annual_pct",
                "max_delta_annual_pct",
                "sign_positive_fraction",
                "median_rank",
            ]
        ],
        on="layout_id",
        how="left",
    )
    table = table.merge(
        interp[["layout_id", "method_year_delta_spread_pctpt"]],
        on="layout_id",
        how="left",
    )
    table = table.merge(
        flux_res[
            [
                "layout_id",
                "delta_opteff_mean_pct_highres",
                "delta_peak_to_active_mean_pct_highres",
                "delta_p99_to_active_mean_pct_highres",
                "delta_peak_to_active_mean_pct_shift_highres_minus_baseline",
                "delta_p99_to_active_mean_pct_shift_highres_minus_baseline",
            ]
        ],
        on="layout_id",
        how="left",
    )
    table = table.merge(
        flux_day[
            [
                "layout_id",
                "delta_opteff_mean_pct_extended",
                "delta_peak_to_active_mean_pct_extended",
                "delta_p99_to_active_mean_pct_extended",
                "delta_peak_to_active_mean_pct_shift_extended_minus_baseline8",
                "delta_p99_to_active_mean_pct_shift_extended_minus_baseline8",
            ]
        ],
        on="layout_id",
        how="left",
    )
    table = table.merge(
        aiming[["layout_id", "strategy", "peak_to_mean_proxy", "cv_active_proxy"]],
        on="layout_id",
        how="left",
    )
    table = table.rename(
        columns={
            "strategy": "proxy_best_strategy",
            "delta_annual_thermal_proxy_mwh_reported_tmy_scaled_pct": "single_year_annual_delta_pct",
            "mean_delta_annual_pct": "multiyear_mean_annual_delta_pct",
            "delta_opteff_mean_pct_highres": "solarpilot_36_delta_opteff_pct",
            "delta_peak_to_active_mean_pct_highres": "solarpilot_36_delta_peak_ratio_pct",
            "delta_p99_to_active_mean_pct_highres": "solarpilot_36_delta_p99_ratio_pct",
            "delta_peak_to_active_mean_pct_extended": "fluxday12_delta_peak_ratio_pct",
            "delta_p99_to_active_mean_pct_extended": "fluxday12_delta_p99_ratio_pct",
        }
    )
    return table


def add_gate_columns(table: pd.DataFrame) -> pd.DataFrame:
    df = table.copy()
    df["has_completed_direct_ci"] = df["direct_ci95_high_pct"].notna()
    df["direct_ci_below_zero"] = df["direct_ci95_high_pct"] < 0.0
    df["direct_directional_negative"] = df["direct_mean_delta_peak_pct"] < 0.0
    df["annual_positive_all_years"] = df["sign_positive_fraction"] >= 1.0
    df["annual_headline_rank_stable"] = df["median_rank"] <= 4.0
    df["annual_interpolation_tight"] = df["method_year_delta_spread_pctpt"] <= 0.20
    df["aiming_proxy_reduction_ge4pct"] = df["delta_aiming_proxy_pct"] <= -4.0
    df["default_flux_nonworse_36"] = df["solarpilot_36_delta_peak_ratio_pct"] <= 0.0
    df["flux_resolution_stable"] = (
        df["delta_peak_to_active_mean_pct_shift_highres_minus_baseline"].abs() <= 0.50
    ) & (df["delta_p99_to_active_mean_pct_shift_highres_minus_baseline"].abs() <= 0.25)
    df["flux_day_sampling_stable"] = (
        df["delta_peak_to_active_mean_pct_shift_extended_minus_baseline8"].abs() <= 0.10
    ) & (df["delta_p99_to_active_mean_pct_shift_extended_minus_baseline8"].abs() <= 0.10)

    def status(row: pd.Series) -> str:
        layout_id = str(row["layout_id"])
        if layout_id == "baseline_full":
            return "paired_baseline"
        if bool(row["direct_ci_below_zero"]) and bool(row["annual_positive_all_years"]):
            return "direct_supported_annual_positive_boundary"
        if bool(row["direct_ci_below_zero"]):
            return "direct_supported_receiver_boundary"
        if bool(row["has_completed_direct_ci"]) and bool(row["direct_directional_negative"]):
            return "directional_direct_only"
        if layout_id == "deform_0276":
            return "optical_stress_case_not_winner"
        if (
            bool(row["annual_positive_all_years"])
            and bool(row["aiming_proxy_reduction_ge4pct"])
            and not bool(row["has_completed_direct_ci"])
        ):
            return "screening_only_annual_positive_needs_direct"
        if (
            bool(row["default_flux_nonworse_36"])
            and bool(row["aiming_proxy_reduction_ge4pct"])
            and not bool(row["annual_positive_all_years"])
        ):
            return "screening_only_receiver_pressure_needs_direct"
        return "control_or_context_only"

    def recommendation(row: pd.Series) -> str:
        state = status(row)
        if state in {"direct_supported_annual_positive_boundary", "direct_supported_receiver_boundary"}:
            return "may_write_as_existing_direct_supported_role"
        if state == "directional_direct_only":
            return "write_directional_or_keep_secondary"
        if state in {
            "screening_only_annual_positive_needs_direct",
            "screening_only_receiver_pressure_needs_direct",
        }:
            return "do_not_headline_keep_in_direct_promotion_queue"
        if state == "optical_stress_case_not_winner":
            return "write_as_optical_stress_case_only"
        if state == "paired_baseline":
            return "reference_only"
        return "secondary_context_only"

    df["promotion_status"] = df.apply(status, axis=1)
    df["writeback_recommendation"] = df.apply(recommendation, axis=1)
    flag_cols = [
        "annual_positive_all_years",
        "annual_headline_rank_stable",
        "annual_interpolation_tight",
        "aiming_proxy_reduction_ge4pct",
        "default_flux_nonworse_36",
        "flux_resolution_stable",
        "flux_day_sampling_stable",
        "direct_ci_below_zero",
    ]
    df["favourable_gate_count"] = df[flag_cols].fillna(False).sum(axis=1).astype(int)
    return df


def fmt(value: object, digits: int = 2) -> str:
    if pd.isna(value):
        return "n/a"
    if isinstance(value, (float, np.floating)):
        return f"{float(value):+.{digits}f}"
    return str(value)


def markdown_table(df: pd.DataFrame) -> str:
    cols = [
        "symbol",
        "layout_id",
        "tier",
        "multiyear_mean_annual_delta_pct",
        "solarpilot_36_delta_peak_ratio_pct",
        "fluxday12_delta_peak_ratio_pct",
        "delta_aiming_proxy_pct",
        "direct_ci",
        "promotion_status",
        "writeback_recommendation",
    ]
    view = df.loc[:, cols].copy()
    view.columns = [
        "Role",
        "Layout",
        "Tier",
        "Annual mean delta (%)",
        "36-bin peak delta (%)",
        "12-day peak delta (%)",
        "Aiming proxy delta (%)",
        "Direct CI",
        "Gate status",
        "Writeback",
    ]
    lines = [
        "| " + " | ".join(view.columns) + " |",
        "| " + " | ".join(["---"] * len(view.columns)) + " |",
    ]
    for row in view.itertuples(index=False):
        cells: list[str] = []
        for value in row:
            if isinstance(value, (float, np.floating)):
                cells.append(fmt(value, 2))
            else:
                cells.append("n/a" if pd.isna(value) else str(value))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def write_figure(df: pd.DataFrame, out: Path) -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
            "font.size": 8.6,
            "axes.titlesize": 9.6,
            "axes.labelsize": 8.6,
            "xtick.labelsize": 7.5,
            "ytick.labelsize": 7.5,
            "legend.fontsize": 7.3,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
            "axes.edgecolor": "#334155",
            "axes.linewidth": 0.7,
            "axes.grid": True,
            "grid.color": "#D7DEE8",
            "grid.linewidth": 0.5,
            "grid.alpha": 0.7,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )
    plot = df[df["layout_id"] != "baseline_full"].copy()
    status_colors = {
        "direct_supported_annual_positive_boundary": "#0E7490",
        "direct_supported_receiver_boundary": "#0E7490",
        "directional_direct_only": "#F97316",
        "screening_only_annual_positive_needs_direct": "#2563EB",
        "screening_only_receiver_pressure_needs_direct": "#7C3AED",
        "optical_stress_case_not_winner": "#DC2626",
        "control_or_context_only": "#64748B",
    }

    fig, axes = plt.subplots(1, 3, figsize=(13.6, 3.85), dpi=220)

    ax = axes[0]
    sizes = 26 + 10 * plot["favourable_gate_count"].fillna(0).to_numpy()
    colors = plot["promotion_status"].map(status_colors).fillna("#64748B")
    ax.scatter(
        plot["multiyear_mean_annual_delta_pct"],
        plot["solarpilot_36_delta_peak_ratio_pct"],
        s=sizes,
        c=colors,
        edgecolor="white",
        linewidth=0.7,
        zorder=3,
    )
    for row in plot.itertuples(index=False):
        ax.annotate(
            DISPLAY_LABELS.get(row.layout_id, row.symbol),
            (row.multiyear_mean_annual_delta_pct, row.solarpilot_36_delta_peak_ratio_pct),
            xytext=(3, 3),
            textcoords="offset points",
            fontsize=7.1,
        )
    ax.axhline(0.0, color="#111827", linewidth=0.8)
    ax.axvline(0.0, color="#111827", linewidth=0.8)
    ax.set_xlabel("Multi-year annual optical-proxy delta (%)")
    ax.set_ylabel("36-bin default peak-ratio delta (%)")
    ax.set_title("(a) Annual/receiver triage")

    ax = axes[1]
    order = plot.sort_values("favourable_gate_count", ascending=True)
    y = np.arange(len(order))
    ax.barh(y, order["favourable_gate_count"], color="#4C78A8")
    ax.set_yticks(y)
    ax.set_yticklabels([DISPLAY_LABELS.get(x, x) for x in order["layout_id"]])
    ax.set_xlabel("Favourable gate count (0-8)")
    ax.set_title("(b) Evidence-gate count")
    ax.set_xlim(0, 8)

    ax = axes[2]
    ci = plot[plot["has_completed_direct_ci"]].copy()
    ci = ci.sort_values("direct_mean_delta_peak_pct", ascending=True)
    y = np.arange(len(ci))
    x = ci["direct_mean_delta_peak_pct"].to_numpy(float)
    xerr = np.vstack(
        [
            x - ci["direct_ci95_low_pct"].to_numpy(float),
            ci["direct_ci95_high_pct"].to_numpy(float) - x,
        ]
    )
    ax.errorbar(
        x,
        y,
        xerr=xerr,
        fmt="o",
        color="#0E7490",
        ecolor="#94A3B8",
        elinewidth=1.2,
        capsize=2.8,
    )
    ax.axvline(0.0, color="#111827", linewidth=0.8)
    ax.axvline(-1.0, color="#DC2626", linewidth=0.8, linestyle="--")
    ax.set_yticks(y)
    ax.set_yticklabels([DISPLAY_LABELS.get(xid, xid) for xid in ci["layout_id"]])
    ax.set_xlabel("Reduced-direct delta peak ratio (%)")
    ax.set_title("(c) Completed direct evidence")

    fig.tight_layout(w_pad=1.6)
    fig.savefig(out / "figures/fig_strong_baseline_promotion_gate.png", bbox_inches="tight")
    fig.savefig(out / "figures/fig_strong_baseline_promotion_gate.pdf", bbox_inches="tight")
    plt.close(fig)


def write_report(df: pd.DataFrame, gate: dict[str, object], out: Path) -> None:
    rows_direct = df[df["writeback_recommendation"] == "may_write_as_existing_direct_supported_role"]
    rows_queue = df[df["writeback_recommendation"] == "do_not_headline_keep_in_direct_promotion_queue"]
    lines = [
        "# Strong-Baseline Promotion Gate",
        "",
        "This report is a conservative writeback gate for the prepared strong-baseline direct-promotion queue.",
        "It merges annual-proxy, interpolation, 36-bin SolarPILOT default-flux, 12-flux-day sampling, aiming-proxy,",
        "geometry, and already completed reduced-direct evidence. It does not claim that the queued strong-baseline",
        "rows have been direct-promoted; rows without completed direct confidence intervals remain queue-only.",
        "",
        "## Gate Decision",
        "",
        f"- Overall recommendation: `{gate['overall_recommendation']}`.",
        f"- Newly promoted strong-baseline rows: `{gate['newly_promoted_strong_baseline_rows']}`.",
        f"- Queue-only strong-baseline rows: `{gate['queue_only_strong_baseline_rows']}`.",
        f"- Server direct matrix status: `{gate['server_direct_matrix_status']}`.",
        "",
        "## Promotion Table",
        "",
        markdown_table(df),
        "",
        "## Interpretation",
        "",
        "- Existing direct-supported rows can still be discussed as direct-supported role boundaries, not final engineering winners.",
        "- `B_hy,E` remains the strongest annual-positive strong-baseline screening row, but it has no completed same-run direct CI.",
        "- `B_pf,R` and `B_hs,R` remain receiver-pressure screening rows: they reduce aiming proxy and are stable in the default-flux gates, but they are not annual optical headline rows.",
        "- `L_opt` remains an optical stress case because its annual optical signal persists while default-flux and hotspot penalties persist.",
        "- The next real scientific upgrade remains the same-run reduced direct promotion matrix or a true same-aimpoint cross-code/custom-aiming check.",
        "",
        "## Direct-Supported Rows Already Available",
        "",
        markdown_table(rows_direct) if not rows_direct.empty else "None.",
        "",
        "## Queue-Only Rows",
        "",
        markdown_table(rows_queue) if not rows_queue.empty else "None.",
    ]
    (out / "STRONG_BASELINE_PROMOTION_GATE_REPORT.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def copy_to_package(out: Path, package: Path) -> None:
    target = package / "supplementary_data/strong_baseline_promotion_gate"
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(out, target)


def main() -> int:
    args = parse_args()
    package = resolve(args.package)
    queue = resolve(args.queue)
    out = resolve(args.out)
    (out / "tables").mkdir(parents=True, exist_ok=True)
    (out / "figures").mkdir(parents=True, exist_ok=True)

    table = add_gate_columns(merge_tables(package, queue))
    table = table.sort_values(["tier", "favourable_gate_count", "layout_id"], ascending=[True, False, True])
    table.to_csv(out / "tables/strong_baseline_promotion_gate_summary.csv", index=False)
    table[table["tier"] == "core"].to_csv(out / "tables/strong_baseline_promotion_gate_core.csv", index=False)

    strong_ids = {"sb_hy_energy", "sb_pf_flux", "sb_hs_flux"}
    newly_promoted = table[
        table["layout_id"].isin(strong_ids) & table["writeback_recommendation"].eq("may_write_as_existing_direct_supported_role")
    ]["layout_id"].tolist()
    queue_only = table[
        table["layout_id"].isin(strong_ids)
        & table["writeback_recommendation"].eq("do_not_headline_keep_in_direct_promotion_queue")
    ]["layout_id"].tolist()
    gate = {
        "overall_recommendation": "write_supplementary_gate_and_short_boundary_sentence_only",
        "newly_promoted_strong_baseline_rows": newly_promoted,
        "queue_only_strong_baseline_rows": queue_only,
        "server_direct_matrix_status": "not_completed_ssh_auth_failed_this_turn",
        "write_main_text_new_positive_claim": False,
        "safe_main_text_claim": (
            "The strong-baseline rows remain screening and direct-promotion-queue candidates; "
            "no undirect-tested strong-baseline row should be promoted to a headline result."
        ),
    }
    (out / "gate_decision.json").write_text(json.dumps(gate, indent=2) + "\n", encoding="utf-8")
    write_figure(table, out)
    write_report(table, gate, out)
    copy_to_package(out, package)
    print(f"Wrote {out}")
    print(f"Copied to {package / 'supplementary_data/strong_baseline_promotion_gate'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
