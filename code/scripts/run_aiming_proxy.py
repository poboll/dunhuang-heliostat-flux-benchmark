#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dhf_rebuild.data_io import load_json
from dhf_rebuild.solar_proxy import compute_heliostat_features


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run receiver aiming proxy maps for representative layouts.")
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "server_full.json")
    parser.add_argument(
        "--layout-ids",
        default="baseline_all,historical_b,random_4675,random_2140,random_1485,random_3681",
    )
    return parser.parse_args()


def load_layout(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, header=None, names=["x_m", "y_m", "z_m"])
    df["radius_m"] = np.hypot(df["x_m"], df["y_m"])
    df["azimuth_rad"] = np.arctan2(df["x_m"], df["y_m"])
    return df


def key_frame(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["_key"] = (
        out["x_m"].round(6).astype(str)
        + "|"
        + out["y_m"].round(6).astype(str)
        + "|"
        + out["z_m"].round(6).astype(str)
    )
    return out


def circular_delta(a: np.ndarray, b: float) -> np.ndarray:
    return np.angle(np.exp(1j * (a - b)))


def make_groups(features: pd.DataFrame, sectors: int = 48, annuli: int = 8) -> pd.DataFrame:
    df = features.copy()
    df["sector"] = pd.cut(
        df["azimuth_rad"],
        bins=np.linspace(-np.pi, np.pi, sectors + 1),
        labels=False,
        include_lowest=True,
    )
    df["annulus"] = pd.cut(
        df["radius_m"],
        bins=np.linspace(df["radius_m"].min(), df["radius_m"].max(), annuli + 1),
        labels=False,
        include_lowest=True,
    )
    rows = []
    for (sector, annulus), grp in df.groupby(["sector", "annulus"], observed=True):
        weight = grp["optical_proxy"].to_numpy()
        if len(grp) == 0 or weight.sum() <= 0:
            continue
        angles = grp["azimuth_rad"].to_numpy()
        mean_angle = math.atan2(float(np.sum(np.sin(angles) * weight)), float(np.sum(np.cos(angles) * weight)))
        rows.append(
            {
                "sector": int(sector),
                "annulus": int(annulus),
                "mirror_count": len(grp),
                "power": float(weight.sum()),
                "theta": mean_angle,
                "radius_mean_m": float(np.average(grp["radius_m"], weights=weight)),
                "flux_risk": float(np.average(grp["flux_risk_raw"], weights=weight)),
            }
        )
    return pd.DataFrame(rows)


def offsets_for_strategy(groups: pd.DataFrame, strategy: str, receiver_height: float) -> pd.DataFrame:
    g = groups.copy()
    g["theta_offset"] = 0.0
    g["z_offset_m"] = 0.0
    if strategy == "equator":
        return g
    if strategy == "five_point":
        levels = np.array([-0.38, -0.19, 0.0, 0.19, 0.38]) * receiver_height
        g["z_offset_m"] = [levels[(int(row.sector) + int(row.annulus)) % len(levels)] for row in g.itertuples()]
        return g
    if strategy.startswith("staggered_levels"):
        _, level_text, amp_text, phase_text = strategy.split(":")
        level_count = int(level_text)
        amp = float(amp_text)
        phase = int(phase_text)
        levels = np.linspace(-amp * receiver_height, amp * receiver_height, level_count)
        g["z_offset_m"] = [
            levels[(int(row.sector) + int(row.annulus) + phase) % level_count] for row in g.itertuples()
        ]
        return g
    if strategy.startswith("balanced"):
        _, amp_text, theta_text = strategy.split(":")
        amp = float(amp_text)
        theta_amp = float(theta_text)
        power_norm = (g["power"] - g["power"].min()) / max(g["power"].max() - g["power"].min(), 1e-12)
        risk_norm = (g["flux_risk"] - g["flux_risk"].min()) / max(g["flux_risk"].max() - g["flux_risk"].min(), 1e-12)
        sign = np.where((g["sector"].to_numpy() + g["annulus"].to_numpy()) % 2 == 0, 1.0, -1.0)
        g["z_offset_m"] = sign * receiver_height * amp * (0.35 + 0.65 * np.maximum(power_norm, risk_norm))
        g["theta_offset"] = sign * theta_amp * (0.2 + 0.8 * risk_norm)
        return g
    raise ValueError(strategy)


def flux_map(
    groups: pd.DataFrame,
    receiver_height: float,
    receiver_diameter: float,
    theta_bins: int = 144,
    z_bins: int = 140,
    sigma_theta: float = 0.035,
    sigma_z_fraction: float = 0.065,
) -> tuple[np.ndarray, dict[str, float]]:
    theta_grid = np.linspace(-np.pi, np.pi, theta_bins, endpoint=False)
    z_grid = np.linspace(-receiver_height, receiver_height, z_bins)
    theta_mesh, z_mesh = np.meshgrid(theta_grid, z_grid)
    flux = np.zeros_like(theta_mesh, dtype=float)
    inside = np.abs(z_mesh) <= receiver_height / 2.0
    sigma_z = max(receiver_height * sigma_z_fraction, 0.8)
    total_power = 0.0
    inside_power = 0.0
    for row in groups.itertuples():
        center_theta = float(row.theta + row.theta_offset)
        center_z = float(row.z_offset_m)
        kernel = np.exp(
            -0.5 * (circular_delta(theta_mesh, center_theta) / sigma_theta) ** 2
            -0.5 * ((z_mesh - center_z) / sigma_z) ** 2
        )
        kernel_sum = float(kernel.sum())
        if kernel_sum <= 0:
            continue
        contribution = kernel / kernel_sum * float(row.power)
        flux += contribution
        total_power += float(row.power)
        inside_power += float(contribution[inside].sum())
    inside_flux = flux[inside]
    active = inside_flux[inside_flux > np.percentile(inside_flux, 55)]
    mean_active = float(active.mean()) if len(active) else float(inside_flux.mean())
    metrics = {
        "intercept_fraction_proxy": inside_power / max(total_power, 1e-12),
        "spillage_proxy": 1.0 - inside_power / max(total_power, 1e-12),
        "peak_flux_proxy": float(inside_flux.max()),
        "mean_active_flux_proxy": mean_active,
        "peak_to_mean_proxy": float(inside_flux.max() / max(mean_active, 1e-12)),
        "cv_active_proxy": float(active.std() / max(active.mean(), 1e-12)) if len(active) else 0.0,
    }
    return flux, metrics


def features_for_layout(layout: pd.DataFrame, all_features: pd.DataFrame | None, config: dict) -> pd.DataFrame:
    if all_features is not None:
        features = key_frame(all_features)
        layout_keys = key_frame(layout)["_key"]
        subset = features[features["_key"].isin(set(layout_keys))].copy()
        if len(subset) >= int(0.95 * len(layout)):
            return subset
    eval_config = json.loads(json.dumps(config))
    eval_config["solar_sampling"] = {
        **config["solar_sampling"],
        "day_step": max(9, int(config["solar_sampling"]["day_step"])),
        "hours": [8, 9, 10, 11, 12, 13, 14, 15, 16],
    }
    return compute_heliostat_features(layout, eval_config["plant"], eval_config["solar_sampling"])


def evaluate_layout(layout_id: str, layout: pd.DataFrame, all_features: pd.DataFrame | None, config: dict, out_dir: Path) -> list[dict[str, float | str | int]]:
    print(f"Evaluating receiver aiming proxy for {layout_id}", flush=True)
    subset = features_for_layout(layout, all_features, config)
    groups = make_groups(subset)
    receiver_height = float(config["plant"]["receiver_height_m"])
    receiver_diameter = float(config["plant"]["receiver_diameter_m"])
    strategies = ["equator", "five_point"]
    best_strategy = None
    best_objective = float("inf")
    best_metrics = None
    best_flux = None
    for level_count in [7, 9, 11, 13]:
        for amp in [0.34, 0.38, 0.42]:
            for phase in range(level_count):
                strategy = f"staggered_levels:{level_count:d}:{amp:.3f}:{phase:d}"
                aimed = offsets_for_strategy(groups, strategy, receiver_height)
                fmap, metrics = flux_map(aimed, receiver_height, receiver_diameter, theta_bins=72, z_bins=70)
                objective = (
                    metrics["peak_to_mean_proxy"]
                    + 0.85 * metrics["cv_active_proxy"]
                    + 8.0 * metrics["spillage_proxy"]
                )
                if objective < best_objective:
                    best_strategy = strategy
                    best_objective = objective
                    best_metrics = metrics
                    best_flux = fmap
    for amp in [0.24, 0.32, 0.40]:
        for theta_amp in [0.0, 0.015, 0.030]:
            strategy = f"balanced:{amp:.3f}:{theta_amp:.3f}"
            aimed = offsets_for_strategy(groups, strategy, receiver_height)
            fmap, metrics = flux_map(aimed, receiver_height, receiver_diameter, theta_bins=72, z_bins=70)
            objective = (
                metrics["peak_to_mean_proxy"]
                + 0.85 * metrics["cv_active_proxy"]
                + 8.0 * metrics["spillage_proxy"]
            )
            if objective < best_objective:
                best_strategy = strategy
                best_objective = objective
                best_metrics = metrics
                best_flux = fmap
    if best_strategy and best_strategy not in strategies:
        strategies.append(best_strategy)
    records = []
    plot_flux = {}
    for strategy in strategies:
        aimed = offsets_for_strategy(groups, strategy, receiver_height)
        fmap, metrics = flux_map(aimed, receiver_height, receiver_diameter)
        record = {
            "layout_id": layout_id,
            "strategy": strategy,
            "heliostat_count": len(subset),
            "group_count": len(groups),
            **metrics,
        }
        records.append(record)
        plot_flux[strategy] = fmap

    fig, axes = plt.subplots(1, len(strategies), figsize=(4.4 * len(strategies), 3.6), dpi=170)
    if len(strategies) == 1:
        axes = [axes]
    vmax = max(float(values.max()) for values in plot_flux.values())
    for ax, strategy in zip(axes, strategies):
        im = ax.imshow(plot_flux[strategy], origin="lower", aspect="auto", cmap="inferno", vmin=0.0, vmax=vmax)
        ax.set_title(strategy, fontsize=8)
        ax.set_xlabel("receiver azimuth bins")
        ax.set_ylabel("vertical bins")
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.suptitle(f"Receiver flux proxy: {layout_id}", fontweight="bold")
    fig.tight_layout()
    fig.savefig(out_dir / "figures" / f"aiming_flux_{layout_id}.png", bbox_inches="tight")
    plt.close(fig)
    return records


def main() -> int:
    args = parse_args()
    config = load_json(args.config)
    run = args.run
    out_dir = run / "aiming_proxy"
    (out_dir / "figures").mkdir(parents=True, exist_ok=True)
    features_path = run / "heliostat_features.csv"
    all_features = pd.read_csv(features_path) if features_path.exists() else None
    records = []
    for layout_id in [part.strip() for part in args.layout_ids.split(",") if part.strip()]:
        layout_path = run / "layouts" / f"{layout_id}.csv"
        if not layout_path.exists():
            print(f"Skipping missing layout {layout_id}")
            continue
        records.extend(evaluate_layout(layout_id, load_layout(layout_path), all_features, config, out_dir))
    df = pd.DataFrame.from_records(records)
    df.to_csv(out_dir / "aiming_metrics.csv", index=False)
    summary = df.sort_values(["layout_id", "peak_to_mean_proxy"]).groupby("layout_id").head(1)
    summary.to_csv(out_dir / "best_aiming_by_layout.csv", index=False)
    print(f"Wrote {out_dir / 'aiming_metrics.csv'}")
    print(f"Wrote {out_dir / 'best_aiming_by_layout.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
