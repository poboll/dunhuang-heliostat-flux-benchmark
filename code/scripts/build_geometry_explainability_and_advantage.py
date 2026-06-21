#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "paper_submission" / "solar_energy_elsarticle_v8_strict_review_rescue"


@dataclass(frozen=True)
class LayoutSpec:
    layout_id: str
    label: str
    family: str
    role: str
    path: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build geometry explainability and constrained-advantage audit tables for the "
            "Dunhuang layout--aiming benchmark."
        )
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "server_outputs" / "geometry_explainability_advantage_20260524",
    )
    parser.add_argument("--package", type=Path, default=PACKAGE)
    return parser.parse_args()


def set_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
            "font.size": 8.8,
            "axes.titlesize": 9.6,
            "axes.labelsize": 8.6,
            "xtick.labelsize": 7.6,
            "ytick.labelsize": 7.6,
            "legend.fontsize": 7.5,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
            "axes.edgecolor": "#334155",
            "axes.linewidth": 0.7,
            "axes.grid": True,
            "grid.color": "#D7DEE8",
            "grid.linewidth": 0.5,
            "grid.alpha": 0.70,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


COLORS = {
    "L0": "#64748B",
    "L_opt": "#2563EB",
    "L_nom": "#7C3AED",
    "L_rob": "#0E7490",
    "C_rad+": "#F97316",
    "J_bal": "#059669",
    "J_flux": "#DC2626",
    "B_hy,E": "#0891B2",
    "B_pf,R": "#A16207",
    "B_hs,R": "#9333EA",
}


DISPLAY_LABELS = {
    "L0": r"$L_0$",
    "L_opt": r"$L_{opt}$",
    "L_nom": r"$L_{nom}$",
    "L_rob": r"$L_{rob}$",
    "L_ctrl": r"$L_{ctrl}$",
    "C_rad+": r"$C_{rad+}$",
    "J_bal": r"$J_{bal}$",
    "J_flux": r"$J_{flux}$",
    "B_hy,E": r"$B_{hy,E}$",
    "B_pf,R": r"$B_{pf,R}$",
    "B_hs,R": r"$B_{hs,R}$",
}


def display_label(label: str) -> str:
    return DISPLAY_LABELS.get(label, label)


def layout_specs() -> list[LayoutSpec]:
    strong = ROOT / "server_outputs" / "same_anchor_strong_baselines_20260523" / "layouts"
    base_strength = ROOT / "server_outputs" / "baseline_strengthening_20260522" / "layouts"
    return [
        LayoutSpec("baseline_full", "L0", "reference", "baseline", strong / "baseline_full.csv"),
        LayoutSpec("deform_0276", "L_opt", "TS-FPDA", "optical stress case", strong / "deform_0276.csv"),
        LayoutSpec("deform_0893", "L_nom", "TS-FPDA", "nominal proxy leader", strong / "deform_0893.csv"),
        LayoutSpec("deform_1387", "L_rob", "TS-FPDA", "receiver-risk candidate", strong / "deform_1387.csv"),
        LayoutSpec(
            "ctrl_radial_expand_015",
            "C_rad+",
            "control",
            "simple radial flux-control row",
            strong / "ctrl_radial_expand_015.csv",
        ),
        LayoutSpec("joint_g02_0333", "J_bal", "joint", "no-energy-loss balance candidate", strong / "joint_g02_0333.csv"),
        LayoutSpec("joint_g04_0478", "J_flux", "joint", "receiver-boundary candidate", strong / "joint_g04_0478.csv"),
        LayoutSpec("sb_hy_energy", "B_hy,E", "hybrid approximation", "annual-positive strong baseline", strong / "sb_hy_energy.csv"),
        LayoutSpec("sb_pf_flux", "B_pf,R", "pattern-free approximation", "receiver-pressure strong baseline", strong / "sb_pf_flux.csv"),
        LayoutSpec("sb_hs_flux", "B_hs,R", "slider-like approximation", "receiver-pressure strong baseline", strong / "sb_hs_flux.csv"),
        LayoutSpec("deform_1822", "L_ctrl", "TS-FPDA", "default-flux-control representative", base_strength / "deform_1822.csv"),
    ]


def load_layout(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path, header=None, names=["x_m", "y_m", "z_m"])
    for col in ["x_m", "y_m", "z_m"]:
        df[col] = pd.to_numeric(df[col], errors="raise")
    df["radius_m"] = np.hypot(df["x_m"], df["y_m"])
    df["azimuth_rad"] = np.arctan2(df["x_m"], df["y_m"])
    return df


def wrap_angle(values: np.ndarray) -> np.ndarray:
    return (values + np.pi) % (2.0 * np.pi) - np.pi


def nearest_neighbor(layout: pd.DataFrame) -> np.ndarray:
    xy = layout[["x_m", "y_m"]].to_numpy(dtype=float)
    tree = cKDTree(xy)
    distances, _ = tree.query(xy, k=2)
    return distances[:, 1]


def radial_density(layout: pd.DataFrame, bins: np.ndarray) -> pd.DataFrame:
    counts, _ = np.histogram(layout["radius_m"].to_numpy(dtype=float), bins=bins)
    area = math.pi * (bins[1:] ** 2 - bins[:-1] ** 2)
    density = counts / np.maximum(area, 1e-9)
    return pd.DataFrame(
        {
            "radius_inner_m": bins[:-1],
            "radius_outer_m": bins[1:],
            "radius_mid_m": 0.5 * (bins[:-1] + bins[1:]),
            "heliostat_count": counts,
            "count_density_per_m2": density,
            "count_share": counts / max(int(counts.sum()), 1),
        }
    )


def sector_counts(layout: pd.DataFrame, sector_edges: np.ndarray) -> pd.DataFrame:
    counts, _ = np.histogram(layout["azimuth_rad"].to_numpy(dtype=float), bins=sector_edges)
    centers = 0.5 * (sector_edges[:-1] + sector_edges[1:])
    return pd.DataFrame(
        {
            "sector_center_rad": centers,
            "sector_center_deg": np.degrees(centers),
            "heliostat_count": counts,
            "count_share": counts / max(int(counts.sum()), 1),
        }
    )


def read_metric_tables() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    strong = pd.read_csv(ROOT / "server_outputs" / "same_anchor_strong_baselines_20260523" / "tables" / "strong_baseline_integrated.csv")
    annual = pd.read_csv(ROOT / "server_outputs" / "fast_annual_proxy_sanity_20260524" / "tables" / "fast_annual_proxy_summary.csv")
    formal = pd.read_csv(PACKAGE / "supplementary_data" / "formal_paired_statistics" / "tables" / "formal_paired_statistics_key_rows.csv")
    afd = pd.read_csv(PACKAGE / "supplementary_data" / "afd_style_flux_proxy" / "tables" / "afd_flux_proxy_selected.csv")
    return strong, annual, formal, afd


def direct_summary(formal: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    priority = {"CI-supported reduction": 0, "directional practical reduction": 1, "weak directional reduction": 2}
    for layout_id, group in formal.groupby("layout_id", sort=False):
        best = group.copy()
        best["priority"] = best["evidence_grade"].map(priority).fillna(9)
        best["abs_mean"] = best["mean_delta_peak_pct"].abs()
        best = best.sort_values(["priority", "ci95_high_mean_pct", "mean_delta_peak_pct", "abs_mean"], ascending=[True, True, True, False]).iloc[0]
        rows.append(
            {
                "layout_id": layout_id,
                "direct_matrix": best["matrix"],
                "direct_view": best["view"],
                "direct_strategy": best["strategy_short"],
                "direct_mean_delta_peak_pct": float(best["mean_delta_peak_pct"]),
                "direct_ci95_low_pct": float(best["ci95_low_mean_pct"]),
                "direct_ci95_high_pct": float(best["ci95_high_mean_pct"]),
                "direct_evidence_grade": best["evidence_grade"],
                "direct_ci": f"{best['mean_delta_peak_pct']:+.2f} [{best['ci95_low_mean_pct']:+.2f}, {best['ci95_high_mean_pct']:+.2f}]",
            }
        )
    return pd.DataFrame(rows)


def constrained_table(layouts: list[LayoutSpec], geometry: pd.DataFrame) -> pd.DataFrame:
    strong, annual, formal, afd = read_metric_tables()
    afd = (
        afd.assign(_baseline_rank=(afd["cohort"] != "baseline_controls").astype(int))
        .sort_values(["layout_id", "_baseline_rank"])
        .drop_duplicates("layout_id", keep="first")
        .drop(columns=["_baseline_rank"])
    )
    direct = direct_summary(formal)
    selected = pd.DataFrame([spec.__dict__ | {"path": str(spec.path)} for spec in layouts])
    table = selected.merge(strong, on="layout_id", how="left", suffixes=("", "_strong"))
    table = table.merge(
        annual[
            [
                "layout_id",
                "delta_annual_thermal_proxy_mwh_reported_tmy_scaled_pct",
                "electric_proxy_mwh_calibrated_to_public_generation",
            ]
        ],
        on="layout_id",
        how="left",
    )
    table = table.merge(
        direct[
            [
                "layout_id",
                "direct_mean_delta_peak_pct",
                "direct_ci95_low_pct",
                "direct_ci95_high_pct",
                "direct_evidence_grade",
                "direct_ci",
            ]
        ],
        on="layout_id",
        how="left",
    )
    table = table.merge(
        afd[
            [
                "layout_id",
                "delta_active_frac_above_baseline_p99_pct_pctpt",
                "delta_p99_to_active_mean_pctpt",
                "delta_peak_to_active_mean_pctpt",
            ]
        ],
        on="layout_id",
        how="left",
    )
    table = table.merge(
        geometry[
            [
                "layout_id",
                "mean_displacement_m",
                "p95_displacement_m",
                "mean_radial_shift_m",
                "nearest_neighbor_p05_m",
                "sector_l1_shift_pct_of_field",
                "radial_density_l1_shift_pct_of_field",
            ]
        ],
        on="layout_id",
        how="left",
    )

    def interpret(row: pd.Series) -> str:
        annual_delta = row.get("delta_annual_thermal_proxy_mwh_reported_tmy_scaled_pct")
        default_flux = row.get("delta_default_flux_ratio_pct")
        aiming = row.get("delta_aiming_proxy_pct")
        direct_hi = row.get("direct_ci95_high_pct")
        if pd.notna(direct_hi) and direct_hi < 0:
            if pd.notna(annual_delta) and annual_delta >= 0:
                return "direct-supported annual-positive receiver-risk row"
            return "direct-supported receiver-boundary row"
        if pd.notna(annual_delta) and annual_delta >= 1.0 and pd.notna(aiming) and aiming <= -4.0:
            return "annual-positive strong screening candidate"
        if pd.notna(default_flux) and default_flux <= 0 and pd.notna(aiming) and aiming <= -5.0:
            return "receiver-pressure screening candidate"
        if row["layout_id"] == "deform_0276":
            return "annual optical stress case with receiver penalty"
        if row["layout_id"] == "baseline_full":
            return "paired baseline"
        return "screening/support row"

    table["constrained_interpretation"] = table.apply(interpret, axis=1)
    table["annual_nonnegative"] = table["delta_annual_thermal_proxy_mwh_reported_tmy_scaled_pct"] >= 0
    table["aiming_proxy_reduction_4pct"] = table["delta_aiming_proxy_pct"] <= -4
    table["default_flux_nonworse"] = table["delta_default_flux_ratio_pct"] <= 0
    table["direct_ci_below_zero"] = table["direct_ci95_high_pct"] < 0
    ordered = [
        "layout_id",
        "label",
        "family",
        "role",
        "delta_annual_thermal_proxy_mwh_reported_tmy_scaled_pct",
        "delta_opteff_pct",
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
        "radial_density_l1_shift_pct_of_field",
        "constrained_interpretation",
        "annual_nonnegative",
        "aiming_proxy_reduction_4pct",
        "default_flux_nonworse",
        "direct_ci_below_zero",
    ]
    return table[[col for col in ordered if col in table.columns]]


def build_geometry_tables(layouts: list[LayoutSpec], out: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, pd.DataFrame]]:
    loaded = {spec.layout_id: load_layout(spec.path) for spec in layouts}
    base = loaded["baseline_full"]
    rmax = float(np.percentile(base["radius_m"], 99.8) * 1.035)
    radial_bins = np.linspace(0, rmax, 19)
    sector_edges = np.linspace(-np.pi, np.pi, 37)

    base_density = radial_density(base, radial_bins).rename(
        columns={"count_density_per_m2": "baseline_density_per_m2", "count_share": "baseline_count_share"}
    )
    base_sector = sector_counts(base, sector_edges).rename(
        columns={"heliostat_count": "baseline_sector_count", "count_share": "baseline_sector_share"}
    )

    nn_rows: list[pd.DataFrame] = []
    radial_rows: list[pd.DataFrame] = []
    sector_rows: list[pd.DataFrame] = []
    summary_rows: list[dict[str, object]] = []
    displacement_cache: dict[str, pd.DataFrame] = {}

    x0 = base["x_m"].to_numpy(dtype=float)
    y0 = base["y_m"].to_numpy(dtype=float)
    r0 = base["radius_m"].to_numpy(dtype=float)
    phi0 = base["azimuth_rad"].to_numpy(dtype=float)
    n = len(base)

    for spec in layouts:
        df = loaded[spec.layout_id]
        if len(df) != n:
            raise ValueError(f"{spec.layout_id} has {len(df)} rows; expected {n}")
        nn = nearest_neighbor(df)
        nn_rows.append(
            pd.DataFrame(
                {
                    "layout_id": spec.layout_id,
                    "label": spec.label,
                    "nearest_neighbor_m": nn,
                }
            )
        )
        dens = radial_density(df, radial_bins)
        dens = dens.merge(base_density[["radius_mid_m", "baseline_density_per_m2", "baseline_count_share"]], on="radius_mid_m", how="left")
        dens["layout_id"] = spec.layout_id
        dens["label"] = spec.label
        dens["delta_density_pct"] = 100.0 * (dens["count_density_per_m2"] - dens["baseline_density_per_m2"]) / dens["baseline_density_per_m2"].replace(0, np.nan)
        dens["delta_count_share_pctpt"] = 100.0 * (dens["count_share"] - dens["baseline_count_share"])
        radial_rows.append(dens)

        sectors = sector_counts(df, sector_edges)
        sectors = sectors.merge(base_sector, on=["sector_center_rad", "sector_center_deg"], how="left")
        sectors["layout_id"] = spec.layout_id
        sectors["label"] = spec.label
        sectors["delta_sector_count"] = sectors["heliostat_count"] - sectors["baseline_sector_count"]
        sectors["delta_sector_share_pctpt"] = 100.0 * (sectors["count_share"] - sectors["baseline_sector_share"])
        sector_rows.append(sectors)

        dx = df["x_m"].to_numpy(dtype=float) - x0
        dy = df["y_m"].to_numpy(dtype=float) - y0
        mag = np.hypot(dx, dy)
        phi = df["azimuth_rad"].to_numpy(dtype=float)
        r = df["radius_m"].to_numpy(dtype=float)
        dphi = wrap_angle(phi - phi0)
        displacement = pd.DataFrame(
            {
                "layout_id": spec.layout_id,
                "label": spec.label,
                "dx_m": dx,
                "dy_m": dy,
                "displacement_m": mag,
                "movement_angle_rad": np.arctan2(dy, dx),
                "radial_shift_m": r - r0,
                "tangential_shift_m": r0 * dphi,
            }
        )
        displacement_cache[spec.layout_id] = displacement
        sector_l1 = float(100.0 * sectors["delta_sector_count"].abs().sum() / (2.0 * n))
        radial_l1 = float(dens["delta_count_share_pctpt"].abs().sum() / 2.0)
        summary_rows.append(
            {
                "layout_id": spec.layout_id,
                "label": spec.label,
                "family": spec.family,
                "role": spec.role,
                "heliostat_count": n,
                "mean_displacement_m": float(mag.mean()),
                "median_displacement_m": float(np.median(mag)),
                "p95_displacement_m": float(np.percentile(mag, 95)),
                "p99_displacement_m": float(np.percentile(mag, 99)),
                "mean_radial_shift_m": float((r - r0).mean()),
                "median_radial_shift_m": float(np.median(r - r0)),
                "p05_radial_shift_m": float(np.percentile(r - r0, 5)),
                "p95_radial_shift_m": float(np.percentile(r - r0, 95)),
                "mean_abs_tangential_shift_m": float(np.mean(np.abs(r0 * dphi))),
                "nearest_neighbor_min_m": float(nn.min()),
                "nearest_neighbor_p05_m": float(np.percentile(nn, 5)),
                "nearest_neighbor_median_m": float(np.median(nn)),
                "nearest_neighbor_p95_m": float(np.percentile(nn, 95)),
                "sector_max_abs_delta_count": int(sectors["delta_sector_count"].abs().max()),
                "sector_l1_shift_pct_of_field": sector_l1,
                "radial_density_l1_shift_pct_of_field": radial_l1,
            }
        )

    nn_table = pd.concat(nn_rows, ignore_index=True)
    radial_table = pd.concat(radial_rows, ignore_index=True)
    sector_table = pd.concat(sector_rows, ignore_index=True)
    summary = pd.DataFrame(summary_rows)
    tables = out / "tables"
    tables.mkdir(parents=True, exist_ok=True)
    summary.to_csv(tables / "geometry_explainability_summary.csv", index=False)
    radial_table.to_csv(tables / "radial_density_change.csv", index=False)
    sector_table.to_csv(tables / "sector_population_change.csv", index=False)
    nn_table.groupby(["layout_id", "label"])["nearest_neighbor_m"].describe(percentiles=[0.01, 0.05, 0.5, 0.95, 0.99]).reset_index().to_csv(
        tables / "nearest_neighbor_summary.csv", index=False
    )
    return summary, radial_table, sector_table, nn_table, displacement_cache


def plot_figure(
    out: Path,
    radial: pd.DataFrame,
    nn: pd.DataFrame,
    displacements: dict[str, pd.DataFrame],
    constrained: pd.DataFrame,
) -> None:
    set_style()
    fig = plt.figure(figsize=(14.5, 9.7), constrained_layout=True)
    gs = fig.add_gridspec(2, 3, width_ratios=[1.16, 1.0, 1.08])
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[0, 2])
    ax_d = fig.add_subplot(gs[1, 0], projection="polar")
    ax_e = fig.add_subplot(gs[1, 1])
    ax_f = fig.add_subplot(gs[1, 2])

    show_labels = ["L_opt", "L_rob", "J_bal", "J_flux", "B_hy,E", "B_pf,R", "B_hs,R"]
    for label in show_labels:
        subset = radial[radial["label"] == label].sort_values("radius_mid_m")
        if subset.empty:
            continue
        ax_a.plot(
            subset["radius_mid_m"] / 1000.0,
            subset["delta_count_share_pctpt"],
            label=display_label(label),
            linewidth=1.7,
            color=COLORS.get(label, "#334155"),
        )
    ax_a.axhline(0, color="#475569", linewidth=0.75)
    ax_a.set_title("(a) Radial population shift")
    ax_a.set_xlabel("Radius from tower (km)")
    ax_a.set_ylabel("Bin share change (percentage points)")
    ax_a.legend(ncol=2, frameon=False, loc="upper left")

    nn_labels = ["L0", "L_opt", "L_rob", "J_bal", "B_hy,E", "B_hs,R"]
    bins = np.linspace(8, 34, 90)
    for label in nn_labels:
        vals = nn.loc[nn["label"] == label, "nearest_neighbor_m"].to_numpy(dtype=float)
        if vals.size == 0:
            continue
        hist, edges = np.histogram(vals, bins=bins, density=True)
        centers = 0.5 * (edges[:-1] + edges[1:])
        ax_b.plot(centers, hist, linewidth=1.6, label=label, color=COLORS.get(label, "#334155"))
    ax_b.set_title("(b) Nearest-neighbour spacing")
    ax_b.set_xlabel("Nearest-neighbour distance (m)")
    ax_b.set_ylabel("Density")
    ax_b.legend(frameon=False, loc="upper right")

    box_labels = ["L_opt", "L_rob", "J_bal", "J_flux", "B_hy,E", "B_pf,R", "B_hs,R"]
    box_data = [displacements[row_id]["displacement_m"].to_numpy(dtype=float) for row_id in label_to_layout_ids(box_labels, constrained)]
    bp = ax_c.boxplot(
        box_data,
        vert=False,
        tick_labels=[display_label(label) for label in box_labels],
        patch_artist=True,
        showfliers=False,
    )
    for patch, label in zip(bp["boxes"], box_labels):
        patch.set_facecolor(COLORS.get(label, "#94A3B8"))
        patch.set_alpha(0.32)
        patch.set_edgecolor(COLORS.get(label, "#334155"))
    for median in bp["medians"]:
        median.set_color("#0F172A")
        median.set_linewidth(1.2)
    ax_c.set_title("(c) Count-preserving movement scale")
    ax_c.set_xlabel("Per-heliostat displacement (m)")

    theta_bins = np.linspace(-np.pi, np.pi, 25)
    for label in ["L_opt", "J_bal", "B_hy,E", "B_hs,R"]:
        layout_id = constrained.loc[constrained["label"] == label, "layout_id"]
        if layout_id.empty:
            continue
        disp = displacements[layout_id.iloc[0]]
        weights = disp["displacement_m"].to_numpy(dtype=float)
        hist, edges = np.histogram(disp["movement_angle_rad"].to_numpy(dtype=float), bins=theta_bins, weights=weights)
        hist = hist / max(float(hist.max()), 1e-12)
        centers = 0.5 * (edges[:-1] + edges[1:])
        ax_d.plot(
            np.r_[centers, centers[0]],
            np.r_[hist, hist[0]],
            linewidth=1.6,
            label=display_label(label),
            color=COLORS.get(label, "#334155"),
        )
    ax_d.set_title("(d) Movement-direction rose", va="bottom")
    ax_d.set_yticklabels([])
    ax_d.set_theta_zero_location("N")
    ax_d.set_theta_direction(-1)
    ax_d.legend(frameon=False, loc="lower left", bbox_to_anchor=(-0.17, -0.18))

    scatter_df = constrained[constrained["layout_id"] != "baseline_full"].copy()
    xcol = "delta_annual_thermal_proxy_mwh_reported_tmy_scaled_pct"
    ycol = "delta_aiming_proxy_pct"
    ccol = "delta_default_flux_ratio_pct"
    norm = TwoSlopeNorm(vmin=-1.5, vcenter=0, vmax=5.0)
    sc = ax_e.scatter(
        scatter_df[xcol],
        scatter_df[ycol],
        c=scatter_df[ccol],
        s=82,
        cmap="coolwarm",
        norm=norm,
        edgecolor="#1F2937",
        linewidth=0.55,
        zorder=3,
    )
    for _, row in scatter_df.iterrows():
        ax_e.annotate(
            display_label(str(row["label"])),
            (row[xcol], row[ycol]),
            xytext=(4, 4),
            textcoords="offset points",
            fontsize=7.2,
            color="#0F172A",
        )
    ax_e.axhline(0, color="#475569", linewidth=0.7)
    ax_e.axvline(0, color="#475569", linewidth=0.7)
    ax_e.fill_between([0, max(3.8, float(scatter_df[xcol].max()) + 0.3)], -9.2, 0, color="#DCFCE7", alpha=0.26, zorder=0)
    ax_e.set_title("(e) Annual proxy versus receiver proxy")
    ax_e.set_xlabel("Fast annual thermal-proxy change (%)")
    ax_e.set_ylabel("Best aiming-proxy concentration change (%)")
    cbar = fig.colorbar(sc, ax=ax_e, fraction=0.046, pad=0.02)
    cbar.set_label("Default flux-ratio change (%)", fontsize=7.5)

    heat_labels = ["L_opt", "L_rob", "J_bal", "J_flux", "B_hy,E", "B_pf,R", "B_hs,R", "C_rad+"]
    heat_df = constrained.set_index("label").reindex(heat_labels)
    score_cols = [
        ("Annual", heat_df[xcol].fillna(0) / 3.5),
        ("Default flux", -heat_df["delta_default_flux_ratio_pct"].fillna(0) / 5.0),
        ("Aiming proxy", -heat_df["delta_aiming_proxy_pct"].fillna(0) / 8.0),
        ("Direct", -heat_df["direct_mean_delta_peak_pct"] / 4.0),
    ]
    heat = np.vstack([np.clip(values.to_numpy(dtype=float), -1, 1) for _, values in score_cols]).T
    heat_masked = np.ma.masked_invalid(heat)
    cmap = plt.colormaps["RdYlGn"].copy()
    cmap.set_bad(color="#E5E7EB")
    im = ax_f.imshow(heat_masked, cmap=cmap, vmin=-1, vmax=1, aspect="auto")
    ax_f.set_xticks(np.arange(len(score_cols)), [name for name, _ in score_cols], rotation=25, ha="right")
    ax_f.set_yticks(np.arange(len(heat_labels)), [display_label(label) for label in heat_labels])
    ax_f.set_title("(f) Favourable normalized scores")
    for i in range(heat.shape[0]):
        for j in range(heat.shape[1]):
            text = "NA" if np.isnan(heat[i, j]) else f"{heat[i, j]:+.2f}"
            ax_f.text(j, i, text, ha="center", va="center", fontsize=6.8, color="#111827")
    cbar2 = fig.colorbar(im, ax=ax_f, fraction=0.046, pad=0.02)
    cbar2.set_label("Favourable score", fontsize=7.5)

    for ax in [ax_a, ax_b, ax_c, ax_e, ax_f]:
        for spine in ax.spines.values():
            spine.set_linewidth(0.7)
            spine.set_color("#334155")

    fig.suptitle("Geometry explainability and constrained advantage audit", fontsize=12.0, fontweight="normal")
    fig_dir = out / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(fig_dir / "fig_geometry_explainability_advantage.png", dpi=300, bbox_inches="tight")
    fig.savefig(fig_dir / "fig_geometry_explainability_advantage.pdf", bbox_inches="tight")
    plt.close(fig)


def label_to_layout_ids(labels: list[str], constrained: pd.DataFrame) -> list[str]:
    out = []
    for label in labels:
        match = constrained.loc[constrained["label"] == label, "layout_id"]
        if match.empty:
            raise KeyError(label)
        out.append(match.iloc[0])
    return out


def write_report(out: Path, constrained: pd.DataFrame, geometry: pd.DataFrame) -> None:
    tables = out / "tables"
    top = constrained.copy()
    top = top[top["layout_id"] != "baseline_full"]
    top_annual = top.sort_values("delta_annual_thermal_proxy_mwh_reported_tmy_scaled_pct", ascending=False).iloc[0]
    best_proxy = top.sort_values("delta_aiming_proxy_pct", ascending=True).iloc[0]
    direct_supported = top[top["direct_ci_below_zero"].fillna(False)]
    largest_move = geometry[geometry["layout_id"] != "baseline_full"].sort_values("p95_displacement_m", ascending=False).iloc[0]
    modest_move = geometry[geometry["layout_id"] != "baseline_full"].sort_values("p95_displacement_m", ascending=True).iloc[0]

    lines = [
        "# Geometry Explainability and Constrained Advantage Audit",
        "",
        "This audit addresses the reviewer concern that the manuscript needs to show how the layouts actually move and where the advantage is constrained.",
        "",
        "## Main findings",
        "",
        f"- The strongest annualized optical row remains `{top_annual['label']}` (`{top_annual['layout_id']}`), with a fast annual thermal-proxy change of {top_annual['delta_annual_thermal_proxy_mwh_reported_tmy_scaled_pct']:+.2f}%. It is therefore an optical stress case, not a final winner.",
        f"- The strongest aiming-proxy reduction among the selected rows is `{best_proxy['label']}` (`{best_proxy['layout_id']}`), with {best_proxy['delta_aiming_proxy_pct']:+.2f}%. Its interpretation still depends on direct promotion.",
        f"- Direct confidence intervals below zero are available for: {', '.join(direct_supported['label'].astype(str).tolist()) if not direct_supported.empty else 'none'}. These rows form the strongest current receiver-risk evidence boundary.",
        f"- The largest p95 movement scale in the audited set is `{largest_move['label']}` at {largest_move['p95_displacement_m']:.1f} m; the smallest non-baseline p95 movement scale is `{modest_move['label']}` at {modest_move['p95_displacement_m']:.1f} m. This confirms that the search is a local count-preserving deformation, not mirror deletion.",
        "",
        "## Claim boundary",
        "",
        "The constrained table should not be read as a SOTA ranking. It identifies role-level rows: annual optical stress cases, annual-positive screening candidates, receiver-pressure screening candidates, and direct-supported receiver-boundary rows. Strong-baseline rows without reduced direct evidence remain candidates for the prepared direct-promotion queue.",
        "",
        "## Generated artifacts",
        "",
        f"- `{(tables / 'geometry_explainability_summary.csv').relative_to(out)}`",
        f"- `{(tables / 'radial_density_change.csv').relative_to(out)}`",
        f"- `{(tables / 'sector_population_change.csv').relative_to(out)}`",
        f"- `{(tables / 'nearest_neighbor_summary.csv').relative_to(out)}`",
        f"- `{(tables / 'constrained_advantage_summary.csv').relative_to(out)}`",
        "- `figures/fig_geometry_explainability_advantage.png`",
        "- `figures/fig_geometry_explainability_advantage.pdf`",
    ]
    (out / "GEOMETRY_EXPLAINABILITY_ADVANTAGE_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def sync_to_package(out: Path, package: Path) -> None:
    supp = package / "supplementary_data" / "geometry_explainability_advantage"
    if supp.exists():
        shutil.rmtree(supp)
    shutil.copytree(out, supp)
    fig_src = out / "figures" / "fig_geometry_explainability_advantage.png"
    fig_pdf = out / "figures" / "fig_geometry_explainability_advantage.pdf"
    fig_dst = package / "latex" / "figures"
    fig_dst.mkdir(parents=True, exist_ok=True)
    shutil.copy2(fig_src, fig_dst / fig_src.name)
    shutil.copy2(fig_pdf, fig_dst / fig_pdf.name)
    code_dir = package / "code" / "scripts"
    code_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(Path(__file__), code_dir / Path(__file__).name)


def main() -> int:
    args = parse_args()
    out = args.out if args.out.is_absolute() else ROOT / args.out
    package = args.package if args.package.is_absolute() else ROOT / args.package
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)

    specs = layout_specs()
    summary, radial, sector, nn, displacements = build_geometry_tables(specs, out)
    constrained = constrained_table(specs, summary)
    constrained.to_csv(out / "tables" / "constrained_advantage_summary.csv", index=False)
    plot_figure(out, radial, nn, displacements, constrained)
    write_report(out, constrained, summary)
    (out / "run_config.json").write_text(
        json.dumps(
            {
                "script": "build_geometry_explainability_and_advantage.py",
                "layout_count": len(specs),
                "layouts": [spec.__dict__ | {"path": str(spec.path)} for spec in specs],
                "claim_boundary": "geometry explainability and role-level constrained advantage audit; not SOTA ranking",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    sync_to_package(out, package)
    print(f"Wrote geometry explainability audit to {out}")
    print(f"Synced package artifacts to {package}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
