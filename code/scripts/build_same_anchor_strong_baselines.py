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
class BaselineSpec:
    candidate_id: str
    family: str
    role: str
    description: str
    params: dict[str, float]


REFERENCE_LAYOUTS = {
    "baseline_full": (
        "L0",
        "reference",
        "Audited available Dunhuang coordinate pool.",
        None,
    ),
    "deform_0276": (
        "L_opt",
        "TS-FPDA representative",
        "Optical-upper representative from the existing TS-FPDA queue.",
        ROOT / "server_outputs" / "streamed_fullfield_20260511_205252" / "layouts" / "deform_0276.csv",
    ),
    "deform_0893": (
        "L_nom",
        "TS-FPDA representative",
        "Nominal proxy leader from the existing TS-FPDA queue.",
        ROOT / "server_outputs" / "streamed_fullfield_20260511_205252" / "layouts" / "deform_0893.csv",
    ),
    "deform_1387": (
        "L_rob",
        "TS-FPDA representative",
        "Receiver-risk representative from the existing TS-FPDA queue.",
        ROOT / "server_outputs" / "streamed_fullfield_20260511_205252" / "layouts" / "deform_1387.csv",
    ),
    "ctrl_radial_expand_015": (
        "C_rad+",
        "low-complexity control",
        "Simple radial expansion control carried from the earlier baseline audit.",
        ROOT / "server_outputs" / "baseline_strengthening_20260522" / "layouts" / "ctrl_radial_expand_015.csv",
    ),
    "joint_g02_0333": (
        "J_bal",
        "joint representative",
        "No-energy-loss joint layout--aiming hypothesis from the existing joint queue.",
        ROOT / "server_outputs" / "joint_layout_aiming_20260523" / "layouts" / "joint_g02_0333.csv",
    ),
    "joint_g04_0478": (
        "J_flux",
        "joint representative",
        "Receiver-boundary joint layout--aiming candidate from the existing joint queue.",
        ROOT / "server_outputs" / "joint_layout_aiming_20260523" / "layouts" / "joint_g04_0478.csv",
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build literature-inspired same-anchor strong baseline approximations for the "
            "Dunhuang full-field layout benchmark."
        )
    )
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "server_full.json")
    parser.add_argument("--out", type=Path, default=ROOT / "server_outputs" / "same_anchor_strong_baselines_20260523")
    parser.add_argument("--random-per-family", type=int, default=42)
    parser.add_argument("--seed", type=int, default=20260523)
    return parser.parse_args()


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def base_eval_config(config: dict) -> dict:
    out = json.loads(json.dumps(config))
    out["solar_sampling"] = {
        **config["solar_sampling"],
        "day_step": max(9, int(config["solar_sampling"]["day_step"])),
        "hours": [8, 9, 10, 11, 12, 13, 14, 15, 16],
    }
    return out


def load_csv_layout(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, header=None, names=["x_m", "y_m", "z_m"])
    df["radius_m"] = np.hypot(df["x_m"], df["y_m"])
    df["azimuth_rad"] = np.arctan2(df["x_m"], df["y_m"])
    return df


def nearest_neighbor_min(layout: pd.DataFrame) -> float:
    xy = layout.loc[:, ["x_m", "y_m"]].to_numpy(dtype=float)
    tree = cKDTree(xy)
    distances, _ = tree.query(xy, k=2)
    return float(distances[:, 1].min())


def transform_layout(base: pd.DataFrame, base_features: pd.DataFrame, spec: BaselineSpec) -> pd.DataFrame:
    p = spec.params
    x = base["x_m"].to_numpy(dtype=float)
    y = base["y_m"].to_numpy(dtype=float)
    z = base["z_m"].to_numpy(dtype=float)
    r = np.hypot(x, y)
    theta = np.arctan2(x, y)
    rn = r / max(float(r.max()), 1.0)

    radial_scale = p.get("radial_scale", 0.0)
    x_scale = p.get("x_scale", 1.0)
    y_scale = p.get("y_scale", 1.0)
    theta_shift = np.zeros_like(theta)
    radial_shape = np.zeros_like(theta)

    if spec.family == "pattern-free approximation":
        radial_shape = (
            p["a1"] * np.cos(theta - p["phi1"])
            + p["a2"] * np.cos(2.0 * theta - p["phi2"])
            + p["a3"] * np.cos(3.0 * theta - p["phi3"])
            + p["ring_amp"] * np.sin(p["ring_order"] * math.pi * rn + p["ring_phase"])
        )
        theta_shift = p["twist"] * rn**1.25 + p["az_amp"] * np.sin(2.0 * theta + p["az_phase"]) * rn
    elif spec.family == "slider-like approximation":
        slide = p["slide_amp"] * np.sin(p["ring_order"] * math.pi * rn + p["ring_phase"])
        theta_shift = slide * (0.35 + 0.65 * rn) + p["az_amp"] * np.sin(p["az_order"] * theta + p["az_phase"]) * rn
        radial_shape = p["ring_amp"] * np.cos(p["ring_order"] * math.pi * rn + p["ring_phase"])
    elif spec.family == "terrain-aware approximation":
        slope = base_features["terrain_slope_pct"].to_numpy(dtype=float)
        elev = base_features["terrain_elevation_m"].to_numpy(dtype=float)
        slope_norm = (slope - np.median(slope)) / max(float(np.std(slope)), 1e-9)
        elev_norm = (elev - np.median(elev)) / max(float(np.std(elev)), 1e-9)
        terrain_term = np.clip(0.70 * slope_norm + 0.30 * elev_norm, -2.0, 2.0)
        radial_shape = -p["terrain_amp"] * np.maximum(terrain_term, 0.0) + p["north_bias"] * np.cos(theta) * rn
        theta_shift = p["terrain_slide"] * np.tanh(terrain_term) * np.sin(theta) * rn + p["twist"] * rn**1.1
    elif spec.family == "hybrid pressure approximation":
        petal = np.cos(int(p["petal_order"]) * (theta - p["petal_phase"]))
        radial_shape = (
            p["petal_amp"] * petal * rn**1.35
            + p["ring_amp"] * np.sin(p["ring_order"] * math.pi * rn + p["ring_phase"])
            + p["north_bias"] * np.cos(theta) * rn
        )
        theta_shift = (
            p["twist"] * rn**1.2
            + p["petal_twist"] * np.sin(int(p["petal_order"]) * (theta - p["petal_phase"])) * rn
        )
    else:
        raise ValueError(f"Unknown family: {spec.family}")

    radial_factor = 1.0 + radial_scale + radial_shape
    theta2 = theta + theta_shift
    r2 = r * radial_factor
    out = pd.DataFrame({"x_m": r2 * np.sin(theta2) * x_scale, "y_m": r2 * np.cos(theta2) * y_scale, "z_m": z})
    out["radius_m"] = np.hypot(out["x_m"], out["y_m"])
    out["azimuth_rad"] = np.arctan2(out["x_m"], out["y_m"])
    return out


def random_specs(rng: np.random.Generator, random_per_family: int) -> list[BaselineSpec]:
    specs: list[BaselineSpec] = []
    for i in range(random_per_family):
        specs.append(
            BaselineSpec(
                candidate_id=f"pf_{i:04d}",
                family="pattern-free approximation",
                role="candidate",
                description="Low-frequency sector/ring free-form pressure baseline inspired by pattern-free layout searches.",
                params={
                    "x_scale": float(rng.uniform(0.975, 1.025)),
                    "y_scale": float(rng.uniform(0.975, 1.025)),
                    "radial_scale": float(rng.uniform(-0.014, 0.014)),
                    "a1": float(rng.uniform(-0.008, 0.008)),
                    "a2": float(rng.uniform(-0.008, 0.008)),
                    "a3": float(rng.uniform(-0.006, 0.006)),
                    "phi1": float(rng.uniform(-math.pi, math.pi)),
                    "phi2": float(rng.uniform(-math.pi, math.pi)),
                    "phi3": float(rng.uniform(-math.pi, math.pi)),
                    "ring_amp": float(rng.uniform(-0.008, 0.008)),
                    "ring_order": float(rng.integers(2, 6)),
                    "ring_phase": float(rng.uniform(-math.pi, math.pi)),
                    "twist": float(rng.uniform(-0.018, 0.018)),
                    "az_amp": float(rng.uniform(-0.010, 0.010)),
                    "az_phase": float(rng.uniform(-math.pi, math.pi)),
                },
            )
        )
    for i in range(random_per_family):
        specs.append(
            BaselineSpec(
                candidate_id=f"hs_{i:04d}",
                family="slider-like approximation",
                role="candidate",
                description="Ringwise azimuthal sliding pressure baseline inspired by collision/shadow-projection layout design.",
                params={
                    "x_scale": float(rng.uniform(0.985, 1.020)),
                    "y_scale": float(rng.uniform(0.985, 1.020)),
                    "radial_scale": float(rng.uniform(-0.010, 0.012)),
                    "slide_amp": float(rng.uniform(-0.020, 0.020)),
                    "ring_amp": float(rng.uniform(-0.007, 0.007)),
                    "ring_order": float(rng.integers(2, 7)),
                    "ring_phase": float(rng.uniform(-math.pi, math.pi)),
                    "az_amp": float(rng.uniform(-0.008, 0.008)),
                    "az_order": float(rng.choice([2, 4, 6])),
                    "az_phase": float(rng.uniform(-math.pi, math.pi)),
                },
            )
        )
    for i in range(random_per_family):
        specs.append(
            BaselineSpec(
                candidate_id=f"ta_{i:04d}",
                family="terrain-aware approximation",
                role="candidate",
                description="Terrain-relief-aware pressure baseline that redistributes the full field away from higher public-terrain slope/elevation cells.",
                params={
                    "x_scale": float(rng.uniform(0.985, 1.018)),
                    "y_scale": float(rng.uniform(0.985, 1.018)),
                    "radial_scale": float(rng.uniform(-0.010, 0.014)),
                    "terrain_amp": float(rng.uniform(0.002, 0.008)),
                    "terrain_slide": float(rng.uniform(-0.006, 0.006)),
                    "north_bias": float(rng.uniform(-0.008, 0.010)),
                    "twist": float(rng.uniform(-0.010, 0.010)),
                },
            )
        )
    for i in range(random_per_family):
        order = int(rng.choice([4, 6, 8], p=[0.40, 0.40, 0.20]))
        specs.append(
            BaselineSpec(
                candidate_id=f"hy_{i:04d}",
                family="hybrid pressure approximation",
                role="candidate",
                description="Hybrid petal/slider pressure baseline combining bounded petal modulation with ring sliding.",
                params={
                    "x_scale": float(rng.uniform(0.975, 1.025)),
                    "y_scale": float(rng.uniform(0.975, 1.025)),
                    "radial_scale": float(rng.uniform(-0.014, 0.014)),
                    "petal_order": float(order),
                    "petal_phase": float(rng.uniform(-math.pi, math.pi)),
                    "petal_amp": float(rng.uniform(-0.014, 0.014)),
                    "petal_twist": float(rng.uniform(-0.006, 0.006)),
                    "ring_amp": float(rng.uniform(-0.007, 0.007)),
                    "ring_order": float(rng.integers(2, 6)),
                    "ring_phase": float(rng.uniform(-math.pi, math.pi)),
                    "north_bias": float(rng.uniform(-0.008, 0.010)),
                    "twist": float(rng.uniform(-0.014, 0.014)),
                },
            )
        )
    return specs


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
    quality = layout_quality(features, base_features, keep_fraction=1.0)
    energy_ratio = float(features["optical_proxy"].sum() / base_proxy_sum)
    flux_index = float(np.percentile(features["flux_risk_raw"], 99) / base_flux_p99)
    min_nn = nearest_neighbor_min(features)
    publishable = (
        len(features) == len(base_features)
        and quality["layout_quality_score"] >= 0.78
        and min_nn >= 7.0
        and quality["ellipse_axis_ratio"] <= 1.35
        and float(np.percentile(features["terrain_slope_pct"], 95)) <= 3.0
        and float(features["terrain_elevation_m"].max() - features["terrain_elevation_m"].min()) <= 80.0
        and 0.94 <= energy_ratio <= 1.08
    )
    return {
        "layout_id": layout_id,
        "role": role,
        "family": family,
        "description": description,
        "heliostat_count": int(len(features)),
        "energy_ratio_proxy": energy_ratio,
        "delta_proxy_energy_pct": 100.0 * (energy_ratio - 1.0),
        "flux_risk_index_proxy": flux_index,
        "delta_proxy_flux_index_pct": 100.0 * (flux_index - 1.0),
        "min_neighbor_m": min_nn,
        "terrain_elevation_range_m": float(features["terrain_elevation_m"].max() - features["terrain_elevation_m"].min()),
        "terrain_slope_p95_pct": float(np.percentile(features["terrain_slope_pct"], 95)),
        "x_span_p99_m": float(features["x_m"].quantile(0.995) - features["x_m"].quantile(0.005)),
        "y_span_p99_m": float(features["y_m"].quantile(0.995) - features["y_m"].quantile(0.005)),
        "ellipse_axis_ratio": quality["ellipse_axis_ratio"],
        "layout_quality_score": quality["layout_quality_score"],
        "sector_coverage_ratio": quality["sector_coverage_ratio"],
        "annular_coverage_ratio": quality["annular_coverage_ratio"],
        "is_publishable_geometry": int(publishable),
    }


def normalized(values: pd.Series, higher: bool) -> pd.Series:
    v = values.astype(float)
    lo, hi = float(v.min()), float(v.max())
    if abs(hi - lo) < 1e-12:
        out = pd.Series(np.ones(len(v)), index=v.index)
    else:
        out = (v - lo) / (hi - lo)
    return out if higher else 1.0 - out


def select_pressure_representatives(candidates: pd.DataFrame) -> pd.DataFrame:
    pool = candidates[candidates["is_publishable_geometry"].astype(int) == 1].copy()
    if pool.empty:
        pool = candidates.copy()
    pool["_energy"] = normalized(pool["energy_ratio_proxy"], True)
    pool["_flux"] = normalized(pool["flux_risk_index_proxy"], False)
    pool["_terrain"] = normalized(pool["terrain_slope_p95_pct"], False)
    pool["_quality"] = normalized(pool["layout_quality_score"], True)
    pool["_spacing"] = normalized(pool["min_neighbor_m"], True)
    pool["_balanced"] = pool[["_energy", "_flux", "_terrain", "_quality", "_spacing"]].mean(axis=1)

    selected: list[int] = []
    role_by_index: dict[int, str] = {}
    for family, prefix in [
        ("pattern-free approximation", "SB_pf"),
        ("slider-like approximation", "SB_hs"),
        ("terrain-aware approximation", "SB_ta"),
        ("hybrid pressure approximation", "SB_hy"),
    ]:
        fam = pool[pool["family"] == family]
        if fam.empty:
            continue
        selectors = [
            (fam["energy_ratio_proxy"].idxmax(), f"{prefix}_energy"),
            (fam["flux_risk_index_proxy"].idxmin(), f"{prefix}_flux"),
        ]
        for idx, role in selectors:
            if idx not in role_by_index:
                selected.append(idx)
                role_by_index[idx] = role
    for idx in pool.sort_values("_balanced", ascending=False).index:
        if len(selected) >= 9:
            break
        if idx not in role_by_index:
            selected.append(idx)
            role_by_index[idx] = "SB_balanced"

    out = candidates.loc[selected].copy()
    out["selected_role"] = [role_by_index[idx] for idx in selected]
    return out.reset_index(drop=False).rename(columns={"index": "candidate_row_index"})


def generate_candidates(args: argparse.Namespace, config: dict, out: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(args.seed)
    terrain = load_terrain(ROOT / config["data"]["terrain_grid"])
    base_flat = load_layout(ROOT / config["data"]["layout_a"], remove_origin=True)
    base = terrain_relative_layout(base_flat, terrain)
    eval_config = base_eval_config(config)
    base_features = compute_heliostat_features(base, eval_config["plant"], eval_config["solar_sampling"])
    base_features = attach_terrain_features(base_features, terrain)
    base_proxy_sum = float(base_features["optical_proxy"].sum())
    base_flux_p99 = float(np.percentile(base_features["flux_risk_raw"], 99))

    records: list[dict[str, float | int | str]] = []
    specs = random_specs(rng, args.random_per_family)
    spec_by_id = {spec.candidate_id: spec for spec in specs}
    for spec in specs:
        layout = terrain_relative_layout(transform_layout(base_flat, base_features, spec), terrain)
        row = proxy_row(
            spec.candidate_id,
            spec.role,
            spec.family,
            spec.description,
            layout,
            base_features,
            base_proxy_sum,
            base_flux_p99,
            eval_config,
            terrain,
        )
        row["params_json"] = json.dumps(spec.params, sort_keys=True)
        records.append(row)

    candidates = pd.DataFrame.from_records(records)
    selected = select_pressure_representatives(candidates)

    layouts_dir = out / "layouts"
    tables_dir = out / "tables"
    layouts_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)
    write_layout(layouts_dir / "baseline_full.csv", base)

    reference_rows = [
        proxy_row(
            "baseline_full",
            "L0",
            "reference",
            REFERENCE_LAYOUTS["baseline_full"][2],
            base,
            base_features,
            base_proxy_sum,
            base_flux_p99,
            eval_config,
            terrain,
        )
    ]
    for layout_id, (role, family, description, src) in REFERENCE_LAYOUTS.items():
        if layout_id == "baseline_full" or src is None or not Path(src).exists():
            continue
        dst = layouts_dir / f"{layout_id}.csv"
        shutil.copy2(src, dst)
        reference_rows.append(
            proxy_row(
                layout_id,
                role,
                family,
                description,
                load_csv_layout(dst),
                base_features,
                base_proxy_sum,
                base_flux_p99,
                eval_config,
                terrain,
            )
        )

    exported_rows = []
    for n, row in selected.iterrows():
        src_id = str(row["layout_id"])
        spec = spec_by_id[src_id]
        stable_id = str(row["selected_role"]).lower()
        if stable_id in {r["layout_id"] for r in exported_rows}:
            stable_id = f"{stable_id}_{n}"
        layout = terrain_relative_layout(transform_layout(base_flat, base_features, spec), terrain)
        write_layout(layouts_dir / f"{stable_id}.csv", layout)
        exported = proxy_row(
            stable_id,
            str(row["selected_role"]),
            str(row["family"]),
            str(row["description"]),
            layout,
            base_features,
            base_proxy_sum,
            base_flux_p99,
            eval_config,
            terrain,
        )
        exported["source_candidate_id"] = src_id
        exported["params_json"] = row["params_json"]
        exported_rows.append(exported)

    candidates.to_csv(tables_dir / "strong_baseline_all_candidates.csv", index=False)
    selected.to_csv(tables_dir / "strong_baseline_selected_candidates.csv", index=False)
    proxy = pd.DataFrame.from_records(reference_rows + exported_rows)
    proxy.to_csv(tables_dir / "strong_baseline_proxy_geometry.csv", index=False)
    layout_ids = proxy["layout_id"].tolist()
    (tables_dir / "selected_layout_ids.txt").write_text(",".join(layout_ids), encoding="utf-8")
    return candidates, proxy


def merge_results(out: Path, proxy: pd.DataFrame) -> pd.DataFrame | None:
    tables_dir = out / "tables"
    solarpilot_path = out / "solarpilot_strong_baseline" / "tables" / "solarpilot_summary.csv"
    aiming_path = out / "aiming_proxy" / "best_aiming_by_layout.csv"
    if not solarpilot_path.exists() or not aiming_path.exists():
        return None
    sp = pd.read_csv(solarpilot_path)
    aim = pd.read_csv(aiming_path)
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
    merged["pressure_score"] = (
        merged["delta_opteff_pct"].astype(float)
        - 0.45 * np.maximum(merged["delta_default_flux_ratio_pct"].astype(float), 0.0)
        - 0.35 * np.maximum(merged["delta_aiming_proxy_pct"].astype(float), 0.0)
    )
    merged = merged.sort_values(["family", "role", "layout_id"]).reset_index(drop=True)
    merged.to_csv(tables_dir / "strong_baseline_integrated.csv", index=False)
    write_figure(merged, out)
    write_report(merged, out)
    return merged


def display_label(role: str) -> str:
    mapping = {
        "L0": r"$L_0$",
        "L_opt": r"$L_{\mathrm{opt}}$",
        "L_nom": r"$L_{\mathrm{nom}}$",
        "L_rob": r"$L_{\mathrm{rob}}$",
        "C_rad+": r"$C_{\mathrm{rad}+}$",
        "J_bal": r"$J_{\mathrm{bal}}$",
        "J_flux": r"$J_{\mathrm{flux}}$",
        "SB_pf_energy": r"$B_{\mathrm{pf,E}}$",
        "SB_pf_flux": r"$B_{\mathrm{pf,R}}$",
        "SB_hs_energy": r"$B_{\mathrm{hs,E}}$",
        "SB_hs_flux": r"$B_{\mathrm{hs,R}}$",
        "SB_ta_energy": r"$B_{\mathrm{ta,E}}$",
        "SB_ta_flux": r"$B_{\mathrm{ta,R}}$",
        "SB_hy_energy": r"$B_{\mathrm{hy,E}}$",
        "SB_hy_flux": r"$B_{\mathrm{hy,R}}$",
        "SB_balanced": r"$B_{\mathrm{bal}}$",
    }
    return mapping.get(role, role.replace("_", r"\_"))


def family_color(family: str) -> str:
    return {
        "reference": "#6E6E6E",
        "low-complexity control": "#D49A2A",
        "TS-FPDA representative": "#3B6EA8",
        "joint representative": "#7B5EA7",
        "pattern-free approximation": "#2A9D8F",
        "slider-like approximation": "#E76F51",
        "terrain-aware approximation": "#59A14F",
        "hybrid pressure approximation": "#4E79A7",
    }.get(family, "#999999")


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
    plot_df = df.copy()
    plot_df["color"] = plot_df["family"].map(family_color)
    plot_df["label"] = plot_df["role"].map(display_label)
    non_base = plot_df[plot_df["layout_id"] != "baseline_full"].copy()
    top_pressure = non_base.sort_values("pressure_score", ascending=False).head(10)

    fig = plt.figure(figsize=(7.5, 6.7), dpi=230)
    gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.05], hspace=0.43, wspace=0.30)
    ax0 = fig.add_subplot(gs[0, 0])
    ax1 = fig.add_subplot(gs[0, 1])
    ax2 = fig.add_subplot(gs[1, :])

    for _, row in non_base.iterrows():
        marker = "D" if "approximation" in row["family"] else "o"
        ax0.scatter(
            row["delta_opteff_pct"],
            row["delta_default_flux_ratio_pct"],
            s=52,
            c=row["color"],
            marker=marker,
            edgecolor="white",
            linewidth=0.6,
            zorder=3,
        )
        if row["role"] in {"L_opt", "L_nom", "L_rob", "J_flux", "J_bal", "SB_pf_energy", "SB_hs_energy", "SB_ta_flux", "SB_hy_energy"}:
            ax0.text(row["delta_opteff_pct"] + 0.04, row["delta_default_flux_ratio_pct"] + 0.08, row["label"], fontsize=7)
    ax0.axhline(0, color="#777777", lw=0.8)
    ax0.axvline(0, color="#777777", lw=0.8)
    ax0.grid(True, color="#DDDDDD", lw=0.45)
    ax0.set_xlabel(r"SolarPILOT $\Delta\eta_{opt}$ (%)")
    ax0.set_ylabel(r"Default $\Delta R_{flux}$ (%)")
    ax0.set_title("Default bridge pressure test", loc="left", fontweight="bold")
    ax0.text(0.01, 0.97, "(a)", transform=ax0.transAxes, ha="left", va="top", fontweight="bold")

    order = non_base.sort_values("delta_aiming_proxy_pct").head(12)
    ax1.barh(np.arange(len(order)), order["delta_aiming_proxy_pct"], color=order["color"])
    ax1.axvline(0, color="#777777", lw=0.8)
    ax1.set_yticks(np.arange(len(order)))
    ax1.set_yticklabels(order["label"].tolist())
    ax1.invert_yaxis()
    ax1.grid(True, axis="x", color="#DDDDDD", lw=0.45)
    ax1.set_xlabel(r"Best proxy $\Delta R_{aim}$ (%)")
    ax1.set_title("Best aiming-proxy rows", loc="left", fontweight="bold")
    ax1.text(0.01, 0.97, "(b)", transform=ax1.transAxes, ha="left", va="top", fontweight="bold")

    x = np.arange(len(top_pressure))
    width = 0.27
    ax2.bar(x - width, top_pressure["delta_opteff_pct"], width=width, color="#4C78A8", label=r"$\Delta\eta_{opt}$")
    ax2.bar(x, top_pressure["delta_default_flux_ratio_pct"], width=width, color="#E15759", label=r"$\Delta R_{flux}$")
    ax2.bar(x + width, top_pressure["delta_aiming_proxy_pct"], width=width, color="#59A14F", label=r"$\Delta R_{aim}$")
    ax2.axhline(0, color="#777777", lw=0.8)
    ax2.set_xticks(x)
    ax2.set_xticklabels(top_pressure["label"].tolist(), rotation=20, ha="right")
    ax2.set_ylabel("Relative change vs. baseline (%)")
    ax2.set_title("Top pressure-score rows under the same anchor", loc="left", fontweight="bold")
    ax2.legend(ncol=3, frameon=False, loc="upper left")
    ax2.grid(True, axis="y", color="#DDDDDD", lw=0.45)
    ax2.text(0.006, 0.96, "(c)", transform=ax2.transAxes, ha="left", va="top", fontweight="bold")

    handles = []
    labels = []
    for family in [
        "TS-FPDA representative",
        "joint representative",
        "pattern-free approximation",
        "slider-like approximation",
        "terrain-aware approximation",
        "hybrid pressure approximation",
        "low-complexity control",
    ]:
        handles.append(plt.Line2D([0], [0], marker="o", lw=0, color=family_color(family), markersize=6))
        labels.append(family)
    fig.legend(handles, labels, ncol=3, frameon=False, loc="lower center", bbox_to_anchor=(0.52, 0.005))
    fig.subplots_adjust(bottom=0.20)
    fig.savefig(out / "figures" / "fig_same_anchor_strong_baselines.png", bbox_inches="tight")
    plt.close(fig)


def write_report(df: pd.DataFrame, out: Path) -> None:
    non_base = df[df["layout_id"] != "baseline_full"].copy()
    families = non_base.groupby("family").agg(
        layout_count=("layout_id", "count"),
        best_delta_opteff_pct=("delta_opteff_pct", "max"),
        best_delta_aiming_proxy_pct=("delta_aiming_proxy_pct", "min"),
        best_pressure_score=("pressure_score", "max"),
    )
    top = non_base.sort_values("pressure_score", ascending=False).head(8)
    report = [
        "# Same-Anchor Strong Baseline Pressure Test",
        "",
        "This report adds literature-inspired baseline approximations under the same Dunhuang coordinate anchor.",
        "The approximation families are not complete reproductions of HelioSliders, HeFAAL, modified ABC, or other named methods.",
        "They are pressure tests that preserve the 11,915 available heliostats and reuse the same SolarPILOT/default-aiming and aiming-proxy pipeline.",
        "",
        "## Family summary",
        "",
        families.to_markdown(floatfmt=".3f"),
        "",
        "## Top pressure-score rows",
        "",
        top.loc[
            :,
            [
                "role",
                "layout_id",
                "family",
                "delta_opteff_pct",
                "delta_default_flux_ratio_pct",
                "delta_aiming_proxy_pct",
                "pressure_score",
            ],
        ].to_markdown(index=False, floatfmt=".3f"),
        "",
        "## Interpretation",
        "",
        "- These baselines are stronger than the earlier low-complexity controls because they test sector/ring free-form, slider-like, terrain-aware, and hybrid deformation families.",
        "- They still do not justify a SOTA claim, because they are local same-anchor approximations and not complete literature algorithm reimplementations.",
        "- The manuscript should use them to show whether the Dunhuang benchmark has discriminative power under stronger pressure, not to overstate final engineering superiority.",
    ]
    (out / "SAME_ANCHOR_STRONG_BASELINE_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    config = load_json(resolve(args.config))
    out = resolve(args.out)
    (out / "tables").mkdir(parents=True, exist_ok=True)
    (out / "figures").mkdir(parents=True, exist_ok=True)
    (out / "run_config.json").write_text(
        json.dumps(
            {
                "config": str(args.config),
                "out": str(out),
                "random_per_family": args.random_per_family,
                "seed": args.seed,
                "claim_boundary": "literature-inspired same-anchor approximations, not full reimplementations",
                "families": [
                    "pattern-free approximation",
                    "slider-like approximation",
                    "terrain-aware approximation",
                    "hybrid pressure approximation",
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    _, proxy = generate_candidates(args, config, out)
    merged = merge_results(out, proxy)
    if merged is None:
        layout_ids = (out / "tables" / "selected_layout_ids.txt").read_text(encoding="utf-8")
        print(f"Wrote strong-baseline layouts to {out}")
        print("Next commands:")
        print(
            f"  conda run --no-capture-output -n uu python scripts/run_solarpilot_validation.py --run {out} "
            f"--out {out / 'solarpilot_strong_baseline'} --layout-ids {layout_ids} --flux-days 8 --flux-bins 24"
        )
        print(
            f"  conda run --no-capture-output -n uu python scripts/run_aiming_proxy.py --run {out} --layout-ids {layout_ids}"
        )
        print(f"  conda run --no-capture-output -n uu python {Path(__file__).relative_to(ROOT)} --out {out}")
    else:
        print(f"Wrote same-anchor strong baseline pressure report to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
