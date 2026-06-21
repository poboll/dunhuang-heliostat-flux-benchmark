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
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dhf_rebuild.data_io import load_json, load_layout, write_layout
from dhf_rebuild.optimizer import layout_quality
from dhf_rebuild.solar_proxy import compute_heliostat_features
from dhf_rebuild.terrain import attach_terrain_features, load_terrain, terrain_relative_layout


@dataclass(frozen=True)
class ControlLayout:
    layout_id: str
    role: str
    description: str
    x_scale: float = 1.0
    y_scale: float = 1.0
    radial_scale: float = 0.0
    north_bias: float = 0.0
    radial_wave: float = 0.0
    az_stagger: float = 0.0
    stagger_order: int = 6


CONTROL_LAYOUTS = [
    ControlLayout(
        layout_id="ctrl_radial_compact_015",
        role="C_rad-",
        description="Uniform 1.5% radial compaction around the tower.",
        radial_scale=-0.015,
    ),
    ControlLayout(
        layout_id="ctrl_radial_expand_015",
        role="C_rad+",
        description="Uniform 1.5% radial expansion around the tower.",
        radial_scale=0.015,
    ),
    ControlLayout(
        layout_id="ctrl_ellipse_xwide_015",
        role="C_ell",
        description="Simple anisotropic ellipse control: east-west expanded, north-south compressed.",
        x_scale=1.015,
        y_scale=0.985,
    ),
    ControlLayout(
        layout_id="ctrl_north_bias_012",
        role="C_nb",
        description="Smooth north/south radial redistribution with 1.2% amplitude.",
        north_bias=0.012,
    ),
    ControlLayout(
        layout_id="ctrl_ring_wave_012",
        role="C_wave",
        description="Two-lobe radial wave control with 1.2% amplitude.",
        radial_wave=0.012,
    ),
    ControlLayout(
        layout_id="ctrl_azimuth_stagger_018",
        role="C_stag",
        description="Pure azimuthal stagger control with 0.018 rad amplitude and no radial scaling.",
        az_stagger=0.018,
    ),
]

REFERENCE_LAYOUTS = {
    "baseline_full": ("L0", "Audited available full-field baseline."),
    "deform_0276": ("L_opt", "TS-FPDA optical-upper representative."),
    "deform_0893": ("L_nom", "TS-FPDA nominal proxy leader."),
    "deform_1387": ("L_rob", "TS-FPDA receiver-risk representative."),
    "deform_1822": ("L_ctrl", "TS-FPDA default-flux-control representative."),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build same-condition low-complexity baseline controls and aggregate SolarPILOT/aiming-proxy comparisons."
    )
    parser.add_argument("--source-run", type=Path, default=ROOT / "server_outputs" / "streamed_fullfield_20260511_205252")
    parser.add_argument("--out", type=Path, default=ROOT / "server_outputs" / "baseline_strengthening_20260522")
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "server_full.json")
    parser.add_argument("--make-only", action="store_true", help="Only generate layouts and proxy geometry tables.")
    return parser.parse_args()


def simple_transform(base: pd.DataFrame, control: ControlLayout) -> pd.DataFrame:
    x = base["x_m"].to_numpy(dtype=float)
    y = base["y_m"].to_numpy(dtype=float)
    z = base["z_m"].to_numpy(dtype=float)
    r = np.hypot(x, y)
    theta = np.arctan2(x, y)
    rn = r / max(float(r.max()), 1.0)
    radial_factor = (
        1.0
        + control.radial_scale
        + control.north_bias * np.cos(theta) * rn
        + control.radial_wave * np.cos(2.0 * theta) * rn
    )
    theta2 = theta + control.az_stagger * np.sin(control.stagger_order * theta) * rn
    r2 = r * radial_factor
    out = pd.DataFrame(
        {
            "x_m": r2 * np.sin(theta2) * control.x_scale,
            "y_m": r2 * np.cos(theta2) * control.y_scale,
            "z_m": z,
        }
    )
    out["radius_m"] = np.hypot(out["x_m"], out["y_m"])
    out["azimuth_rad"] = np.arctan2(out["x_m"], out["y_m"])
    return out


def nearest_neighbor_min(layout: pd.DataFrame) -> float:
    xy = layout.loc[:, ["x_m", "y_m"]].to_numpy(dtype=float)
    tree = cKDTree(xy)
    distances, _ = tree.query(xy, k=2)
    return float(distances[:, 1].min())


def load_csv_layout(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, header=None, names=["x_m", "y_m", "z_m"])
    df["radius_m"] = np.hypot(df["x_m"], df["y_m"])
    df["azimuth_rad"] = np.arctan2(df["x_m"], df["y_m"])
    return df


def proxy_row(
    layout_id: str,
    role: str,
    family: str,
    description: str,
    layout: pd.DataFrame,
    base_features: pd.DataFrame,
    base_proxy_sum: float,
    base_flux_p99: float,
    config: dict,
    terrain: pd.DataFrame,
) -> dict[str, float | int | str]:
    features = compute_heliostat_features(layout, config["plant"], config["solar_sampling"])
    features = attach_terrain_features(features, terrain)
    energy_ratio = float(features["optical_proxy"].sum() / base_proxy_sum)
    flux_index = float(np.percentile(features["flux_risk_raw"], 99) / base_flux_p99)
    quality = layout_quality(features, base_features, keep_fraction=1.0)
    return {
        "layout_id": layout_id,
        "role": role,
        "family": family,
        "description": description,
        "heliostat_count": int(len(features)),
        "energy_ratio_proxy": energy_ratio,
        "flux_risk_index_proxy": flux_index,
        "min_neighbor_m": nearest_neighbor_min(features),
        "terrain_elevation_range_m": float(features["terrain_elevation_m"].max() - features["terrain_elevation_m"].min()),
        "terrain_slope_p95_pct": float(np.percentile(features["terrain_slope_pct"], 95)),
        "x_span_p99_m": float(features["x_m"].quantile(0.995) - features["x_m"].quantile(0.005)),
        "y_span_p99_m": float(features["y_m"].quantile(0.995) - features["y_m"].quantile(0.005)),
        "ellipse_axis_ratio": quality["ellipse_axis_ratio"],
        "layout_quality_score": quality["layout_quality_score"],
        "sector_coverage_ratio": quality["sector_coverage_ratio"],
        "annular_coverage_ratio": quality["annular_coverage_ratio"],
    }


def generate_layouts(args: argparse.Namespace, config: dict, out: Path) -> pd.DataFrame:
    layouts_dir = out / "layouts"
    tables_dir = out / "tables"
    figures_dir = out / "figures"
    layouts_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    terrain = load_terrain(ROOT / config["data"]["terrain_grid"])
    base_flat = load_layout(ROOT / config["data"]["layout_a"], remove_origin=True)
    base = terrain_relative_layout(base_flat, terrain)
    eval_config = json.loads(json.dumps(config))
    eval_config["solar_sampling"] = {
        **config["solar_sampling"],
        "day_step": max(9, int(config["solar_sampling"]["day_step"])),
        "hours": [8, 9, 10, 11, 12, 13, 14, 15, 16],
    }
    base_features = compute_heliostat_features(base, eval_config["plant"], eval_config["solar_sampling"])
    base_features = attach_terrain_features(base_features, terrain)
    base_proxy_sum = float(base_features["optical_proxy"].sum())
    base_flux_p99 = float(np.percentile(base_features["flux_risk_raw"], 99))

    rows = []
    write_layout(layouts_dir / "baseline_full.csv", base)
    rows.append(
        proxy_row(
            "baseline_full",
            "L0",
            "reference",
            REFERENCE_LAYOUTS["baseline_full"][1],
            base,
            base_features,
            base_proxy_sum,
            base_flux_p99,
            eval_config,
            terrain,
        )
    )

    for control in CONTROL_LAYOUTS:
        layout = terrain_relative_layout(simple_transform(base_flat, control), terrain)
        write_layout(layouts_dir / f"{control.layout_id}.csv", layout)
        rows.append(
            proxy_row(
                control.layout_id,
                control.role,
                "same-condition control",
                control.description,
                layout,
                base_features,
                base_proxy_sum,
                base_flux_p99,
                eval_config,
                terrain,
            )
        )

    source_layout_dir = args.source_run / "layouts"
    for layout_id, (role, description) in REFERENCE_LAYOUTS.items():
        if layout_id == "baseline_full":
            continue
        src = source_layout_dir / f"{layout_id}.csv"
        if not src.exists():
            continue
        dst = layouts_dir / src.name
        shutil.copy2(src, dst)
        layout = load_csv_layout(dst)
        rows.append(
            proxy_row(
                layout_id,
                role,
                "TS-FPDA representative",
                description,
                layout,
                base_features,
                base_proxy_sum,
                base_flux_p99,
                eval_config,
                terrain,
            )
        )

    layout_manifest = pd.DataFrame.from_records(rows)
    layout_manifest.to_csv(tables_dir / "baseline_proxy_geometry.csv", index=False)
    (out / "baseline_controls_manifest.json").write_text(
        json.dumps(
            {
                "source_run": str(args.source_run),
                "control_layouts": [control.__dict__ for control in CONTROL_LAYOUTS],
                "reference_layouts": REFERENCE_LAYOUTS,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return layout_manifest


def merge_results(out: Path, proxy: pd.DataFrame) -> pd.DataFrame | None:
    solarpilot = out / "solarpilot_baseline_comparison" / "tables" / "solarpilot_summary.csv"
    aiming = out / "aiming_proxy" / "best_aiming_by_layout.csv"
    if not solarpilot.exists() or not aiming.exists():
        return None

    sp = pd.read_csv(solarpilot)
    aim = pd.read_csv(aiming)
    merged = proxy.merge(sp, on="layout_id", how="left", suffixes=("", "_sp"))
    merged = merged.merge(
        aim.loc[:, ["layout_id", "strategy", "intercept_fraction_proxy", "peak_to_mean_proxy", "cv_active_proxy"]],
        on="layout_id",
        how="left",
    )
    base = merged.loc[merged["layout_id"] == "baseline_full"].iloc[0]
    merged["delta_opteff_pct"] = 100.0 * (merged["opteff_mean"].astype(float) / float(base["opteff_mean"]) - 1.0)
    merged["delta_default_flux_ratio_pct"] = 100.0 * (
        merged["flux_peak_to_active_mean"].astype(float) / float(base["flux_peak_to_active_mean"]) - 1.0
    )
    merged["delta_aiming_proxy_pct"] = 100.0 * (
        merged["peak_to_mean_proxy"].astype(float) / float(base["peak_to_mean_proxy"]) - 1.0
    )
    merged["delta_proxy_energy_pct"] = 100.0 * (merged["energy_ratio_proxy"].astype(float) - 1.0)
    merged["is_simple_control"] = (merged["family"] == "same-condition control").astype(int)
    columns = [
        "layout_id",
        "role",
        "family",
        "heliostat_count",
        "delta_proxy_energy_pct",
        "delta_opteff_pct",
        "delta_default_flux_ratio_pct",
        "delta_aiming_proxy_pct",
        "flux_risk_index_proxy",
        "min_neighbor_m",
        "terrain_elevation_range_m",
        "terrain_slope_p95_pct",
        "layout_quality_score",
        "strategy",
        "description",
    ]
    integrated = merged.loc[:, columns].sort_values(["family", "layout_id"]).reset_index(drop=True)
    integrated.to_csv(out / "tables" / "baseline_comparison_integrated.csv", index=False)
    publication = integrated.copy()
    publication["paper_label"] = publication["role"]
    publication.to_csv(out / "tables" / "baseline_comparison_publication.csv", index=False)
    write_figure(integrated, out)
    write_report(integrated, out)
    return integrated


def write_figure(df: pd.DataFrame, out: Path) -> None:
    plt.rcParams.update(
        {
            "font.family": "Times New Roman",
            "font.size": 8,
            "axes.titlesize": 9,
            "axes.labelsize": 8,
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
            "legend.fontsize": 7,
        }
    )
    order = [
        "L0",
        "C_rad-",
        "C_rad+",
        "C_ell",
        "C_nb",
        "C_wave",
        "C_stag",
        "L_opt",
        "L_nom",
        "L_rob",
        "L_ctrl",
    ]
    role_display = {
        "L0": r"$L_0$",
        "C_rad-": r"$C_{\mathrm{rad}-}$",
        "C_rad+": r"$C_{\mathrm{rad}+}$",
        "C_ell": r"$C_{\mathrm{ell}}$",
        "C_nb": r"$C_{\mathrm{nb}}$",
        "C_wave": r"$C_{\mathrm{wave}}$",
        "C_stag": r"$C_{\mathrm{stag}}$",
        "L_opt": r"$L_{\mathrm{opt}}$",
        "L_nom": r"$L_{\mathrm{nom}}$",
        "L_rob": r"$L_{\mathrm{rob}}$",
        "L_ctrl": r"$L_{\mathrm{ctrl}}$",
    }
    plot_df = df.copy()
    plot_df["_order"] = plot_df["role"].map({role: i for i, role in enumerate(order)}).fillna(99)
    plot_df = plot_df.sort_values("_order")
    colors = np.where(plot_df["family"].eq("TS-FPDA representative"), "#3B6EA8", "#D49A2A")
    colors = np.where(plot_df["role"].eq("L0"), "#6E6E6E", colors)

    fig = plt.figure(figsize=(7.4, 5.0), dpi=220)
    grid = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.05], hspace=0.38, wspace=0.28)
    ax0 = fig.add_subplot(grid[0, 0])
    ax1 = fig.add_subplot(grid[0, 1])
    ax2 = fig.add_subplot(grid[1, :])

    ax0.scatter(
        plot_df["delta_opteff_pct"],
        plot_df["delta_default_flux_ratio_pct"],
        s=48,
        c=colors,
        edgecolor="white",
        linewidth=0.6,
        zorder=3,
    )
    label_offsets = {
        "C_rad-": (0.05, 0.13),
        "C_rad+": (0.05, -0.12),
        "C_ell": (0.05, 0.17),
        "C_nb": (0.05, -0.16),
        "C_wave": (0.05, 0.05),
        "C_stag": (0.05, -0.05),
        "L_opt": (-0.45, 0.17),
        "L_nom": (0.05, 0.12),
        "L_rob": (0.05, 0.17),
        "L_ctrl": (0.05, -0.14),
    }
    for row in plot_df.itertuples():
        if row.role != "L0":
            dx, dy = label_offsets.get(row.role, (0.04, 0.06))
            ax0.text(
                row.delta_opteff_pct + dx,
                row.delta_default_flux_ratio_pct + dy,
                role_display.get(row.role, row.role),
                fontsize=7.2,
            )
    ax0.axhline(0, color="#808080", lw=0.8)
    ax0.axvline(0, color="#808080", lw=0.8)
    ax0.set_xlim(float(plot_df["delta_opteff_pct"].min()) - 0.35, float(plot_df["delta_opteff_pct"].max()) + 0.40)
    ax0.set_ylim(float(plot_df["delta_default_flux_ratio_pct"].min()) - 0.55, float(plot_df["delta_default_flux_ratio_pct"].max()) + 0.70)
    ax0.set_xlabel(r"SolarPILOT $\Delta\eta_{opt}$ (%)")
    ax0.set_ylabel(r"Default $\Delta R_{flux}$ (%)")
    ax0.set_title("Default-aiming trade-off", loc="left", fontweight="bold")
    ax0.grid(True, color="#D9D9D9", linewidth=0.45, alpha=0.8)
    ax0.text(0.01, 0.97, "(a)", transform=ax0.transAxes, va="top", ha="left", fontweight="bold")

    x = np.arange(len(plot_df))
    ax1.bar(x, plot_df["delta_aiming_proxy_pct"], color=colors, width=0.72)
    ax1.axhline(0, color="#808080", lw=0.8)
    ax1.set_xticks(x)
    ax1.set_xticklabels([role_display.get(role, role) for role in plot_df["role"]], rotation=35, ha="right")
    ax1.set_ylabel(r"Best proxy $\Delta R_{aim}$ (%)")
    ax1.set_title("Aiming-proxy control", loc="left", fontweight="bold")
    ax1.grid(True, axis="y", color="#D9D9D9", linewidth=0.45, alpha=0.8)
    ax1.text(0.01, 0.97, "(b)", transform=ax1.transAxes, va="top", ha="left", fontweight="bold")

    width = 0.27
    ax2.bar(x - width, plot_df["delta_opteff_pct"], width=width, color="#4C78A8", label=r"$\Delta\eta_{opt}$")
    ax2.bar(x, plot_df["delta_default_flux_ratio_pct"], width=width, color="#E15759", label=r"$\Delta R_{flux}$")
    ax2.bar(x + width, plot_df["delta_aiming_proxy_pct"], width=width, color="#59A14F", label=r"$\Delta R_{aim}$")
    ax2.axhline(0, color="#808080", lw=0.8)
    ax2.set_xticks(x)
    ax2.set_xticklabels([role_display.get(role, role) for role in plot_df["role"]], rotation=28, ha="right")
    ax2.set_ylabel("Relative change vs. L0 (%)")
    ax2.set_title("Same-condition controls and TS-FPDA representatives", loc="left", fontweight="bold")
    ax2.legend(ncol=3, frameon=False, loc="upper left", bbox_to_anchor=(0.055, 1.0), borderaxespad=0.0)
    ax2.grid(True, axis="y", color="#D9D9D9", linewidth=0.45, alpha=0.8)
    ax2.text(0.006, 0.96, "(c)", transform=ax2.transAxes, va="top", ha="left", fontweight="bold")

    fig.text(0.012, 0.012, "Gold: low-complexity controls; blue: TS-FPDA representatives; grey: baseline.", fontsize=7)
    fig.savefig(out / "figures" / "fig_baseline_controls_summary.png", bbox_inches="tight")
    plt.close(fig)


def fmt_pct(value: float) -> str:
    return f"{value:+.2f}%"


def write_report(df: pd.DataFrame, out: Path) -> None:
    simple = df[df["family"] == "same-condition control"].copy()
    reps = df[df["family"] == "TS-FPDA representative"].copy()
    best_simple_opt = simple.sort_values("delta_opteff_pct", ascending=False).iloc[0]
    best_simple_flux = simple.sort_values("delta_default_flux_ratio_pct", ascending=True).iloc[0]
    best_simple_aim = simple.sort_values("delta_aiming_proxy_pct", ascending=True).iloc[0]
    report = f"""# Same-Condition Baseline Strengthening Report

This experiment adds low-complexity controls to test whether the TS-FPDA representatives merely reproduce simple global field transformations.

## Controls

- `C_rad-`: uniform 1.5% radial compaction.
- `C_rad+`: uniform 1.5% radial expansion.
- `C_ell`: simple east-west/west-east ellipse scaling.
- `C_nb`: smooth north/south radial redistribution.
- `C_wave`: two-lobe radial wave.
- `C_stag`: pure azimuthal stagger.

All controls preserve the 11,915 available heliostats and are evaluated with the same public terrain layer, the same SolarPILOT bridge, and the same aiming-proxy search used for the representative layouts.

## Main observations

- Best simple-control SolarPILOT optical gain: `{best_simple_opt.role}` / `{best_simple_opt.layout_id}` at {fmt_pct(float(best_simple_opt.delta_opteff_pct))}, with default flux-ratio change {fmt_pct(float(best_simple_opt.delta_default_flux_ratio_pct))}.
- Best simple-control default-flux ratio: `{best_simple_flux.role}` / `{best_simple_flux.layout_id}` at {fmt_pct(float(best_simple_flux.delta_default_flux_ratio_pct))}, with SolarPILOT optical change {fmt_pct(float(best_simple_flux.delta_opteff_pct))}.
- Best simple-control aiming-proxy ratio: `{best_simple_aim.role}` / `{best_simple_aim.layout_id}` at {fmt_pct(float(best_simple_aim.delta_aiming_proxy_pct))}, with SolarPILOT optical change {fmt_pct(float(best_simple_aim.delta_opteff_pct))}.
- TS-FPDA representatives remain interpretable as role-based candidates rather than a single winner. The comparison should be written as a claim-boundary check, not as a state-of-the-art superiority claim.

Main tables:

- `tables/baseline_proxy_geometry.csv`
- `tables/baseline_comparison_integrated.csv`
- `tables/baseline_comparison_publication.csv`

Main figure:

- `figures/fig_baseline_controls_summary.png`
"""
    (out / "BASELINE_COMPARISON_REPORT.md").write_text(report, encoding="utf-8")


def main() -> int:
    args = parse_args()
    config = load_json(args.config)
    out = args.out if args.out.is_absolute() else ROOT / args.out
    out.mkdir(parents=True, exist_ok=True)
    (out / "run_config.json").write_text(
        json.dumps(
            {
                "source_run": str(args.source_run),
                "out": str(out),
                "config": str(args.config),
                "make_only": args.make_only,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    proxy = generate_layouts(args, config, out)
    if args.make_only:
        print(f"Wrote baseline layouts and proxy geometry table to {out}")
        return 0
    integrated = merge_results(out, proxy)
    if integrated is None:
        print(
            "Generated layouts and proxy geometry. Run SolarPILOT and aiming proxy, then rerun this script to aggregate.",
            flush=True,
        )
    else:
        print(f"Wrote integrated baseline comparison to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
