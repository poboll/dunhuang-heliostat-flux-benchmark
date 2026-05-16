#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
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
from dhf_rebuild.optimizer import build_calibration, layout_quality, normalized_score
from dhf_rebuild.solar_proxy import compute_heliostat_features
from dhf_rebuild.terrain import attach_terrain_features, load_terrain, terrain_relative_layout

PARAM_KEYS = [
    "x_scale",
    "y_scale",
    "radial_scale",
    "radial_wave",
    "twist",
    "az_wave",
    "petal_amp",
    "petal_order",
    "petal_phase",
    "petal_twist",
    "north_bias",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate full-field geometry-preserving deformation candidates.")
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "server_full.json")
    parser.add_argument("--out", type=Path, default=ROOT / "outputs" / "fullfield_deformation")
    parser.add_argument("--random-candidates", type=int, default=240)
    parser.add_argument("--seed", type=int, default=20260511)
    return parser.parse_args()


def transform_layout(base: pd.DataFrame, params: dict[str, float]) -> pd.DataFrame:
    x = base["x_m"].to_numpy(dtype=float)
    y = base["y_m"].to_numpy(dtype=float)
    z = base["z_m"].to_numpy(dtype=float)
    r = np.hypot(x, y)
    theta = np.arctan2(x, y)
    rmax = max(r.max(), 1.0)
    rn = r / rmax

    petal_order = int(params.get("petal_order", 0))
    petal_phase = float(params.get("petal_phase", 0.0))
    if petal_order > 0:
        petal = np.cos(petal_order * (theta - petal_phase))
    else:
        petal = 0.0
    north_bias = params.get("north_bias", 0.0) * np.cos(theta) * rn

    theta2 = (
        theta
        + params.get("twist", 0.0) * rn**1.25
        + params.get("az_wave", 0.0) * np.sin(2.0 * theta) * rn
        + params.get("petal_twist", 0.0) * np.sin(petal_order * (theta - petal_phase)) * rn**1.15
        if petal_order > 0
        else theta + params.get("twist", 0.0) * rn**1.25 + params.get("az_wave", 0.0) * np.sin(2.0 * theta) * rn
    )
    radial_factor = (
        1.0
        + params.get("radial_scale", 0.0)
        + params.get("radial_wave", 0.0) * np.cos(2.0 * theta) * rn
        + params.get("petal_amp", 0.0) * petal * rn**1.4
        + north_bias
    )
    r2 = r * radial_factor
    x2 = r2 * np.sin(theta2) * params["x_scale"]
    y2 = r2 * np.cos(theta2) * params["y_scale"]

    out = pd.DataFrame({"x_m": x2, "y_m": y2, "z_m": z})
    out["radius_m"] = np.hypot(out["x_m"], out["y_m"])
    out["azimuth_rad"] = np.arctan2(out["x_m"], out["y_m"])
    return out


def min_neighbor(layout: pd.DataFrame) -> float:
    tree = cKDTree(layout.loc[:, ["x_m", "y_m"]].to_numpy(dtype=float))
    d, _ = tree.query(layout.loc[:, ["x_m", "y_m"]].to_numpy(dtype=float), k=2)
    return float(np.min(d[:, 1]))


def evaluate_candidate(
    cid: str,
    layout: pd.DataFrame,
    base_layout: pd.DataFrame,
    base_proxy_sum: float,
    base_flux_p99: float,
    calibration,
    config: dict,
    terrain: pd.DataFrame,
) -> tuple[dict[str, float | str | int], pd.DataFrame]:
    features = compute_heliostat_features(layout, config["plant"], config["solar_sampling"])
    if "terrain_elevation_m" not in features or "terrain_slope_pct" not in features:
        features = attach_terrain_features(features, terrain)
    energy_ratio = float(features["optical_proxy"].sum() / base_proxy_sum)
    annual_energy = calibration.baseline_energy_gwh * energy_ratio
    terrain_range = float(features["terrain_elevation_m"].max() - features["terrain_elevation_m"].min())
    slope_p95 = float(np.percentile(features["terrain_slope_pct"], 95))
    slope_mean = float(features["terrain_slope_pct"].mean())
    quality = layout_quality(features, base_layout, keep_fraction=1.0)
    flux_index = float(np.percentile(features["flux_risk_raw"], 99) / base_flux_p99)
    min_nn = min_neighbor(features)

    # Full-field deformation preserves heliostat count; cost changes are represented only
    # by a small terrain/earthwork and field-extents proxy rather than mirror-count savings.
    earthwork_penalty = max(0.0, terrain_range - 35.0) * 0.04 + max(0.0, slope_p95 - 1.3) * 1.5
    extent_penalty = max(0.0, quality["ellipse_axis_ratio"] - 1.25) * 4.0
    capex = calibration.baseline_capex_musd + earthwork_penalty + extent_penalty
    lcoe = calibration.baseline_lcoe_cent_kwh * (capex / calibration.baseline_capex_musd) / max(energy_ratio, 1e-9)

    realism = config.get("realism_constraints", {})
    publishable = (
        quality["layout_quality_score"] >= float(realism.get("min_layout_quality_score", 0.0))
        and slope_p95 <= float(realism.get("max_terrain_slope_p95_pct", 99.0))
        and terrain_range <= float(realism.get("max_terrain_elevation_range_m", 999.0))
        and min_nn >= 7.0
        and 0.94 <= energy_ratio <= 1.08
    )
    record = {
        "candidate_id": cid,
        "heliostat_count": len(features),
        "annual_energy_proxy_gwh": annual_energy,
        "energy_ratio_vs_baseline": energy_ratio,
        "capex_proxy_musd": capex,
        "lcoe_proxy_cent_kwh": lcoe,
        "flux_risk_index": flux_index,
        "min_neighbor_m": min_nn,
        "terrain_elevation_range_m": terrain_range,
        "terrain_slope_p95_pct": slope_p95,
        "terrain_slope_mean_pct": slope_mean,
        "layout_quality_score": quality["layout_quality_score"],
        "sector_coverage_ratio": quality["sector_coverage_ratio"],
        "annular_coverage_ratio": quality["annular_coverage_ratio"],
        "ellipse_axis_ratio": quality["ellipse_axis_ratio"],
        "extent_x_ratio": quality["extent_x_ratio"],
        "extent_y_ratio": quality["extent_y_ratio"],
        "is_publishable_geometry": int(publishable),
    }
    return record, features


def parameter_set(random_candidates: int, seed: int) -> list[dict[str, float]]:
    rng = np.random.default_rng(seed)
    params = [
        {
            "x_scale": 1.0,
            "y_scale": 1.0,
            "radial_scale": 0.0,
            "radial_wave": 0.0,
            "twist": 0.0,
            "az_wave": 0.0,
            "petal_amp": 0.0,
            "petal_order": 0.0,
            "petal_phase": 0.0,
            "petal_twist": 0.0,
            "north_bias": 0.0,
        }
    ]
    for x_scale in [0.97, 0.99, 1.01, 1.03]:
        for y_scale in [0.97, 0.99, 1.01, 1.03]:
            params.append(
                {
                    "x_scale": x_scale,
                    "y_scale": y_scale,
                    "radial_scale": 0.0,
                    "radial_wave": 0.0,
                    "twist": 0.0,
                    "az_wave": 0.0,
                    "petal_amp": 0.0,
                    "petal_order": 0.0,
                    "petal_phase": 0.0,
                    "petal_twist": 0.0,
                    "north_bias": 0.0,
                }
            )
    for order in [4, 6, 8]:
        for amp in [-0.020, -0.012, 0.012, 0.020]:
            for phase in [0.0, np.pi / order]:
                params.append(
                    {
                        "x_scale": 1.0,
                        "y_scale": 1.0,
                        "radial_scale": 0.0,
                        "radial_wave": 0.0,
                        "twist": 0.0,
                        "az_wave": 0.0,
                        "petal_amp": amp,
                        "petal_order": float(order),
                        "petal_phase": float(phase),
                        "petal_twist": 0.0,
                        "north_bias": 0.0,
                    }
                )
    for _ in range(random_candidates):
        order = int(rng.choice([0, 4, 6, 8], p=[0.45, 0.25, 0.20, 0.10]))
        params.append(
            {
                "x_scale": float(rng.uniform(0.965, 1.035)),
                "y_scale": float(rng.uniform(0.965, 1.035)),
                "radial_scale": float(rng.uniform(-0.025, 0.025)),
                "radial_wave": float(rng.uniform(-0.018, 0.018)),
                "twist": float(rng.uniform(-0.035, 0.035)),
                "az_wave": float(rng.uniform(-0.020, 0.020)),
                "petal_amp": float(rng.uniform(-0.026, 0.026)) if order else 0.0,
                "petal_order": float(order),
                "petal_phase": float(rng.uniform(-np.pi, np.pi)) if order else 0.0,
                "petal_twist": float(rng.uniform(-0.012, 0.012)) if order else 0.0,
                "north_bias": float(rng.uniform(-0.012, 0.012)),
            }
        )
    return params


def select_representatives(df: pd.DataFrame, count: int = 8) -> pd.DataFrame:
    pool = df[df["is_publishable_geometry"] == 1].copy()
    if pool.empty:
        pool = df.copy()
    pool["_energy"] = normalized_score(pool, "annual_energy_proxy_gwh", True)
    pool["_lcoe"] = normalized_score(pool, "lcoe_proxy_cent_kwh", False)
    pool["_flux"] = normalized_score(pool, "flux_risk_index", False)
    pool["_terrain"] = normalized_score(pool, "terrain_slope_p95_pct", False)
    pool["_quality"] = normalized_score(pool, "layout_quality_score", True)
    pool["_balanced"] = pool[["_energy", "_lcoe", "_flux", "_terrain", "_quality"]].mean(axis=1)
    picks: list[int] = []
    roles_by_idx: dict[int, str] = {}

    baseline_matches = df.index[df["candidate_id"] == "baseline_full"].tolist()
    if baseline_matches:
        idx = baseline_matches[0]
        picks.append(idx)
        roles_by_idx[idx] = "baseline_control"

    def pick_sorted(column: str, ascending: bool, role: str) -> None:
        for idx in pool.sort_values(column, ascending=ascending).index:
            if idx not in roles_by_idx:
                picks.append(idx)
                roles_by_idx[idx] = role
                return

    pick_sorted("annual_energy_proxy_gwh", False, "max_energy")
    pick_sorted("lcoe_proxy_cent_kwh", True, "min_lcoe")
    pick_sorted("flux_risk_index", True, "min_flux")
    pick_sorted("_balanced", False, "balanced")
    for idx in pool.sort_values("_balanced", ascending=False).index:
        if len(picks) >= count:
            break
        if idx not in roles_by_idx:
            picks.append(idx)
            roles_by_idx[idx] = "balanced_extra"
    reps = df.loc[picks].copy()
    reps["representative_role"] = [roles_by_idx[idx] for idx in picks]
    return reps


def plot_review(out: Path, base: pd.DataFrame, reps: pd.DataFrame, layouts: dict[str, pd.DataFrame]) -> None:
    fig, axes = plt.subplots(2, 4, figsize=(14, 7.2), dpi=170)
    axes = axes.ravel()
    for ax, (_, row) in zip(axes, reps.iterrows()):
        cid = row["candidate_id"]
        layout = layouts[cid]
        ax.scatter(base["x_m"], base["y_m"], s=0.12, color="#cccccc", alpha=0.4)
        ax.scatter(layout["x_m"], layout["y_m"], s=0.20, color="#006d77", alpha=0.72)
        ax.scatter([0], [0], marker="^", color="#d62728", s=28)
        ax.set_aspect("equal")
        ax.set_xlim(-2200, 2200)
        ax.set_ylim(-2200, 2200)
        ax.set_title(f"{cid} | {row['representative_role']}", fontsize=8, loc="left", fontweight="bold")
        ax.text(
            0.02,
            0.02,
            f"E={row['annual_energy_proxy_gwh']:.1f} GWh\naxis={row['ellipse_axis_ratio']:.2f}\nNN={row['min_neighbor_m']:.1f} m",
            transform=ax.transAxes,
            fontsize=7,
            bbox={"facecolor": "white", "alpha": 0.72, "edgecolor": "none", "pad": 2},
        )
        ax.grid(True, alpha=0.15)
    for ax in axes[len(reps):]:
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(out / "figures" / "fullfield_deformation_review.png", bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    args = parse_args()
    config = load_json(args.config)
    out = args.out if args.out.is_absolute() else ROOT / args.out
    (out / "tables").mkdir(parents=True, exist_ok=True)
    (out / "layouts").mkdir(parents=True, exist_ok=True)
    (out / "figures").mkdir(parents=True, exist_ok=True)
    (out / "run_config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")

    base_flat = load_layout(ROOT / config["data"]["layout_a"], remove_origin=True)
    terrain = load_terrain(ROOT / config["data"]["terrain_grid"])
    base = terrain_relative_layout(base_flat, terrain)
    eval_config = json.loads(json.dumps(config))
    eval_config["solar_sampling"] = {
        **config["solar_sampling"],
        "day_step": max(9, int(config["solar_sampling"]["day_step"])),
        "hours": [8, 9, 10, 11, 12, 13, 14, 15, 16],
    }
    base_features = compute_heliostat_features(base, eval_config["plant"], eval_config["solar_sampling"])
    base_features = attach_terrain_features(base_features, terrain)
    calibration = build_calibration(eval_config, n_a=len(base), n_b=9532)
    base_sum = float(base_features["optical_proxy"].sum())
    base_flux_p99 = float(np.percentile(base_features["flux_risk_raw"], 99))

    records = []
    params_list = parameter_set(args.random_candidates, args.seed)
    total_candidates = len(params_list)
    for i, params in enumerate(params_list):
        cid = "baseline_full" if i == 0 else f"deform_{i:04d}"
        layout = terrain_relative_layout(transform_layout(base_flat, params), terrain)
        record, features = evaluate_candidate(
            cid, layout, base, base_sum, base_flux_p99, calibration, eval_config, terrain
        )
        record.update(params)
        records.append(record)
        if i % 25 == 0:
            print(f"evaluated {i + 1}/{total_candidates}", flush=True)
    df = pd.DataFrame.from_records(records)
    df.to_csv(out / "tables" / "fullfield_candidates.csv", index=False)
    reps = select_representatives(df, count=8)
    reps.to_csv(out / "tables" / "fullfield_representatives.csv", index=False)

    # Recompute only the selected representatives. Earlier versions retained the
    # full feature table for every candidate, which made large searches memory
    # bound on the shared paper server.
    layouts = {}
    for cid in reps["candidate_id"]:
        row = reps.loc[reps["candidate_id"] == cid].iloc[0]
        params = {key: float(row[key]) for key in PARAM_KEYS}
        layout = terrain_relative_layout(transform_layout(base_flat, params), terrain)
        _, features = evaluate_candidate(
            cid, layout, base, base_sum, base_flux_p99, calibration, eval_config, terrain
        )
        layouts[cid] = features
        write_layout(out / "layouts" / f"{cid}.csv", layouts[cid])
    plot_review(out, base, reps, layouts)
    report = f"""# Full-Field Deformation Run

This run preserves the full heliostat count instead of deleting mirrors. It applies small geometry-preserving transformations to the corrected reference field, projects heliostat z coordinates onto the cached SRTM90m terrain surface relative to the tower base, and evaluates terrain, spacing, shape, energy, LCOE, and flux-risk proxies.

- Candidates evaluated: {len(df):,}
- Publishable full-field candidates: {int(df['is_publishable_geometry'].sum()):,}
- Representative layouts exported: {len(reps):,}

Main use: provide a non-pruning research route for the revised paper.
"""
    (out / "FULLFIELD_REPORT.md").write_text(report, encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
