#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dhf_rebuild.data_io import load_json, sha256
from dhf_rebuild.solar_proxy import solar_vector


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a reduced PySolTrace custom-aimpoint pilot for representative full-field layouts."
    )
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "server_full.json")
    parser.add_argument("--pysoltrace-dir", type=Path, required=True)
    parser.add_argument(
        "--layout-ids",
        default="baseline_full,deform_0276,deform_0893,deform_1387,deform_1822",
    )
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--max-heliostats", type=int, default=1200)
    parser.add_argument("--rays", type=int, default=240000)
    parser.add_argument("--threads", type=int, default=8)
    parser.add_argument("--receiver-panels", type=int, default=14)
    parser.add_argument("--receiver-nx", type=int, default=16)
    parser.add_argument("--receiver-ny", type=int, default=48)
    parser.add_argument("--sun-day", type=int, default=172)
    parser.add_argument("--sun-hour", type=float, default=12.0)
    parser.add_argument("--seed", type=int, default=20260512)
    parser.add_argument("--strategies", default="visible_equator,five_point,proxy_best")
    return parser.parse_args()


def load_layout(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, header=None, names=["x_m", "y_m", "z_m"])
    df["radius_m"] = np.hypot(df["x_m"], df["y_m"])
    df["azimuth_rad"] = np.arctan2(df["x_m"], df["y_m"])
    return df


def stratified_sample(layout: pd.DataFrame, max_heliostats: int, seed: int) -> pd.DataFrame:
    if len(layout) <= max_heliostats:
        return layout.copy().reset_index(drop=True)
    rng = np.random.default_rng(seed)
    df = layout.copy()
    sectors = max(24, int(round(math.sqrt(max_heliostats) * 1.6)))
    annuli = max(6, int(round(math.sqrt(max_heliostats) / 2.2)))
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
    groups = list(df.groupby(["sector", "annulus"], observed=True))
    quotas = []
    for key, grp in groups:
        quota = max(1, int(round(len(grp) / len(df) * max_heliostats)))
        quotas.append([key, grp, min(quota, len(grp))])
    while sum(item[2] for item in quotas) > max_heliostats:
        candidates = [item for item in quotas if item[2] > 1]
        if candidates:
            max(candidates, key=lambda item: item[2])[2] -= 1
        else:
            active = [ix for ix, item in enumerate(quotas) if item[2] > 0]
            if not active:
                break
            quotas[int(rng.choice(active))][2] = 0
    while sum(item[2] for item in quotas) < max_heliostats:
        candidates = [item for item in quotas if item[2] < len(item[1])]
        if not candidates:
            break
        max(candidates, key=lambda item: len(item[1]) - item[2])[2] += 1
    pieces = []
    for _key, grp, quota in quotas:
        picked = rng.choice(grp.index.to_numpy(), size=quota, replace=False)
        pieces.append(df.loc[picked])
    sampled = pd.concat(pieces, axis=0).sort_values("radius_m").reset_index(drop=True)
    return sampled.drop(columns=["sector", "annulus"], errors="ignore")


def assign_bins(layout: pd.DataFrame, sectors: int = 48, annuli: int = 8) -> pd.DataFrame:
    df = layout.copy()
    df["sector"] = pd.cut(
        df["azimuth_rad"],
        bins=np.linspace(-np.pi, np.pi, sectors + 1),
        labels=False,
        include_lowest=True,
    ).astype(int)
    df["annulus"] = pd.cut(
        df["radius_m"],
        bins=np.linspace(df["radius_m"].min(), df["radius_m"].max(), annuli + 1),
        labels=False,
        include_lowest=True,
    ).astype(int)
    return df


def load_proxy_best(run: Path) -> dict[str, str]:
    best_path = run / "aiming_proxy" / "best_aiming_by_layout.csv"
    if not best_path.exists():
        return {}
    df = pd.read_csv(best_path)
    return dict(zip(df["layout_id"].astype(str), df["strategy"].astype(str), strict=False))


def offsets_for_strategy(layout: pd.DataFrame, strategy: str, receiver_height: float) -> tuple[np.ndarray, np.ndarray]:
    df = assign_bins(layout)
    theta_offset = np.zeros(len(df), dtype=float)
    z_offset = np.zeros(len(df), dtype=float)
    if strategy in {"visible_equator", "equator", "proxy_best_missing"}:
        return theta_offset, z_offset
    if strategy == "five_point":
        levels = np.array([-0.38, -0.19, 0.0, 0.19, 0.38], dtype=float) * receiver_height
        idx = (df["sector"].to_numpy() + df["annulus"].to_numpy()) % len(levels)
        return theta_offset, levels[idx]
    if strategy.startswith("staggered_levels"):
        _, level_text, amp_text, phase_text = strategy.split(":")
        level_count = int(level_text)
        amp = float(amp_text)
        phase = int(phase_text)
        levels = np.linspace(-amp * receiver_height, amp * receiver_height, level_count)
        idx = (df["sector"].to_numpy() + df["annulus"].to_numpy() + phase) % level_count
        return theta_offset, levels[idx]
    if strategy.startswith("balanced"):
        _, amp_text, theta_text = strategy.split(":")
        amp = float(amp_text)
        theta_amp = float(theta_text)
        sign = np.where((df["sector"].to_numpy() + df["annulus"].to_numpy()) % 2 == 0, 1.0, -1.0)
        radius_norm = (df["radius_m"].to_numpy() - df["radius_m"].min()) / max(
            df["radius_m"].max() - df["radius_m"].min(), 1e-12
        )
        z_offset = sign * receiver_height * amp * (0.35 + 0.65 * radius_norm)
        theta_offset = sign * theta_amp * (0.25 + 0.75 * radius_norm)
        return theta_offset, z_offset
    raise ValueError(f"Unsupported aiming strategy: {strategy}")


def point_from_array(point_cls, values: np.ndarray):
    return point_cls(float(values[0]), float(values[1]), float(values[2]))


def receiver_panel_zrot(pt, normal: np.ndarray) -> float:
    best_gamma = 0.0
    best_score = float("inf")
    origin = np.array([0.0, 0.0, 0.0])
    aim = normal.astype(float)
    for gamma in np.linspace(-180.0, 180.0, 721):
        euler = pt.util_calc_euler_angles(origin, aim, gamma)
        rloctoref = pt.util_calc_transforms(euler)["rloctoref"]
        local_y_global = rloctoref @ np.array([0.0, 1.0, 0.0])
        score = float(np.linalg.norm(local_y_global - np.array([0.0, 0.0, 1.0])))
        if score < best_score:
            best_score = score
            best_gamma = float(gamma)
    return best_gamma


def build_case(
    pysoltrace_dir: Path,
    layout: pd.DataFrame,
    plant: dict,
    strategy: str,
    sun_day: int,
    sun_hour: float,
    rays: int,
    seed: int,
    receiver_panels: int,
):
    sys.path.insert(0, str(pysoltrace_dir))
    from pysoltrace import Point, PySolTrace

    pt = PySolTrace()
    pt.dni = 950.0

    opt_ref = pt.add_optic("heliostat_reflector")
    reflectivity = float(plant.get("heliostat_reflectivity_clean", 0.94))
    slope_mrad = float(plant.get("heliostat_tracking_accuracy_mrad", 2.0))
    for face in [opt_ref.front, opt_ref.back]:
        face.reflectivity = reflectivity
        face.slope_error = slope_mrad
        face.spec_error = 0.2

    opt_abs = pt.add_optic("receiver_absorber")
    for face in [opt_abs.front, opt_abs.back]:
        face.reflectivity = 0.0
        face.transmissivity = 0.0
        face.slope_error = 0.0
        face.spec_error = 0.0

    sx, sy, sz = solar_vector(float(plant["latitude_deg"]), sun_day, sun_hour)
    sun = pt.add_sun()
    sun.position = Point(100.0 * sx, 100.0 * sy, 100.0 * sz)
    sun.sigma = 4.65

    receiver_center_z = float(plant["receiver_center_height_m"])
    receiver_height = float(plant["receiver_height_m"])
    receiver_radius = float(plant["receiver_diameter_m"]) / 2.0
    mirror_width = float(plant.get("heliostat_width_m", math.sqrt(float(plant["heliostat_mirror_area_m2"]))))
    mirror_height = float(plant.get("heliostat_height_m", math.sqrt(float(plant["heliostat_mirror_area_m2"]))))
    heliostat_center_above_ground = float(plant.get("heliostat_center_above_ground_m", 5.0))

    panel_width = 2.0 * receiver_radius * math.sin(math.pi / receiver_panels)
    panel_angles = np.linspace(-np.pi, np.pi, receiver_panels, endpoint=False) + math.pi / receiver_panels

    # SolTrace traces stages in order. Heliostats must be the first stage so
    # rays are reflected before they encounter the receiver panels.
    heliostat_stage = pt.add_stage()
    theta_offset, z_offset = offsets_for_strategy(layout, strategy, receiver_height)
    for idx, row in enumerate(layout.itertuples(index=False)):
        pos = np.array([float(row.x_m), float(row.y_m), float(row.z_m) + heliostat_center_above_ground])
        theta = math.atan2(pos[0], pos[1]) + float(theta_offset[idx])
        target = np.array(
            [
                receiver_radius * math.sin(theta),
                receiver_radius * math.cos(theta),
                receiver_center_z + float(z_offset[idx]),
            ],
            dtype=float,
        )
        el = heliostat_stage.add_element()
        el.optic = opt_ref
        el.position = point_from_array(Point, pos)
        receiver_vec = (target - pos)
        receiver_vec = receiver_vec / max(np.linalg.norm(receiver_vec), 1e-12)
        sun_vec = np.array([sx, sy, sz], dtype=float)
        aim_vec = receiver_vec + sun_vec
        aim_vec = aim_vec / max(np.linalg.norm(aim_vec), 1e-12)
        el.aim = point_from_array(Point, pos + aim_vec * 100.0)
        el.zrot = pt.util_calc_zrot_azel([float(aim_vec[0]), float(aim_vec[1]), float(aim_vec[2])])
        el.surface_flat()
        el.aperture_rectangle(mirror_width, mirror_height)

    receiver_stage = pt.add_stage()
    panel_elements = []
    for theta in panel_angles:
        outward = np.array([math.sin(theta), math.cos(theta), 0.0], dtype=float)
        center = np.array(
            [receiver_radius * outward[0], receiver_radius * outward[1], receiver_center_z],
            dtype=float,
        )
        el = receiver_stage.add_element()
        el.optic = opt_abs
        el.position = point_from_array(Point, center)
        el.aim = point_from_array(Point, center + outward * 10.0)
        el.zrot = receiver_panel_zrot(pt, outward)
        el.surface_flat()
        el.aperture_rectangle(panel_width, receiver_height)
        panel_elements.append(el)

    pt.num_ray_hits = int(rays)
    pt.max_rays_traced = int(rays * 80)
    pt.is_sunshape = True
    pt.is_surface_errors = True
    return pt, panel_elements, {"sun_x": sx, "sun_y": sy, "sun_z": sz, "seed": seed}


def bin_flat_panel(pt, panel, nx: int, ny: int) -> tuple[np.ndarray, set[int]]:
    st_id = panel.stage_id + 1
    el_id = panel.id + 1
    dfr = pt.raydata[(pt.raydata.stage == st_id) & (pt.raydata.element == -el_id)].copy()
    flux = np.zeros((ny, nx), dtype=float)
    if dfr.empty:
        return flux, set()
    width, height = panel.aperture_params[0:2]
    euler = pt.util_calc_euler_angles(
        np.array(panel.position.as_list()),
        np.array(panel.aim.as_list()),
        panel.zrot,
    )
    transforms = pt.util_calc_transforms(euler)
    loc = dfr[["loc_x", "loc_y", "loc_z"]].to_numpy(dtype=float)
    panel_pos = np.array(panel.position.as_list(), dtype=float)
    pos_t = pt.util_transform_to_local(loc, np.array([0.0, 0.0, 1.0]), panel_pos, transforms["rreftoloc"])[
        "posloc"
    ]
    raybins_x = np.floor((pos_t[:, 0] + width / 2.0) / width * nx).astype(int)
    raybins_y = np.floor((pos_t[:, 1] + height / 2.0) / height * ny).astype(int)
    valid = (raybins_x >= 0) & (raybins_x < nx) & (raybins_y >= 0) & (raybins_y < ny)
    if not np.any(valid):
        return flux, set()
    ppr = pt.powerperray / max((width / nx) * (height / ny), 1e-12)
    np.add.at(flux, (raybins_y[valid], raybins_x[valid]), ppr)
    return flux, set(dfr.loc[valid, "number"].astype(int).tolist())


def flux_metrics(pt, panel_elements: list, nx: int, ny: int) -> tuple[dict[str, float], np.ndarray]:
    panel_maps = []
    receiver_unique_rays = set()
    for panel in panel_elements:
        fmap, hits = bin_flat_panel(pt, panel, nx=nx, ny=ny)
        panel_maps.append(fmap)
        receiver_unique_rays.update(hits)
    unwrapped = np.concatenate(panel_maps, axis=1)
    active = unwrapped[unwrapped > np.percentile(unwrapped, 55)] if unwrapped.size else np.array([])
    active_mean = float(active.mean()) if len(active) else 0.0
    peak = float(unwrapped.max()) if unwrapped.size else 0.0
    total_power = float(unwrapped.sum())
    metrics = {
        "receiver_absorbed_unique_rays": float(len(receiver_unique_rays)),
        "receiver_intercept_per_requested_ray": float(len(receiver_unique_rays) / max(float(pt.num_ray_hits), 1.0)),
        "peak_flux_w_m2": peak,
        "mean_active_flux_w_m2": active_mean,
        "peak_to_active_mean": float(peak / max(active_mean, 1e-12)),
        "active_flux_cv": float(active.std() / max(active.mean(), 1e-12)) if len(active) else 0.0,
        "total_receiver_power_proxy_w": total_power,
    }
    return metrics, unwrapped


def plot_layout_flux(layout_id: str, maps: dict[str, np.ndarray], out_dir: Path) -> None:
    strategies = list(maps)
    vmax = max(float(m.max()) for m in maps.values()) if maps else 1.0
    fig, axes = plt.subplots(1, len(strategies), figsize=(4.8 * len(strategies), 3.8), dpi=190)
    if len(strategies) == 1:
        axes = [axes]
    for ax, strategy in zip(axes, strategies):
        im = ax.imshow(maps[strategy], origin="lower", aspect="auto", cmap="inferno", vmin=0.0, vmax=vmax)
        ax.set_title(strategy.replace("_", " "), fontsize=8, fontweight="bold")
        ax.set_xlabel("unwrapped receiver panel bins")
        ax.set_ylabel("receiver height bins")
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
    fig.suptitle(f"Reduced SolTrace receiver maps: {layout_id}", fontweight="bold")
    fig.tight_layout()
    fig.savefig(out_dir / "figures" / f"soltrace_flux_{layout_id}.png", bbox_inches="tight")
    plt.close(fig)


def plot_summary(summary: pd.DataFrame, out_dir: Path) -> None:
    if summary.empty:
        return
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.1), dpi=190)
    metrics = [
        ("peak_to_active_mean", "Peak / active mean"),
        ("active_flux_cv", "Active flux CV"),
        ("receiver_intercept_per_requested_ray", "Receiver intercept / requested ray"),
    ]
    for ax, (metric, title) in zip(axes, metrics):
        for strategy, grp in summary.groupby("strategy"):
            ax.plot(grp["layout_id"], grp[metric], marker="o", linewidth=1.6, label=strategy.replace("_", " "))
        ax.set_title(title, fontsize=9, fontweight="bold")
        ax.tick_params(axis="x", rotation=35, labelsize=7)
        ax.grid(True, alpha=0.18)
    axes[0].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out_dir / "figures" / "soltrace_aimpoint_summary.png", bbox_inches="tight")
    plt.close(fig)


def markdown_table(df: pd.DataFrame, floatfmt: str = ".4g") -> str:
    if df.empty:
        return ""
    headers = list(df.columns)
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in df.itertuples(index=False):
        cells = []
        for value in row:
            if isinstance(value, float):
                cells.append(format(value, floatfmt))
            else:
                cells.append(str(value))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    run = args.run if args.run.is_absolute() else ROOT / args.run
    config_path = args.config if args.config.is_absolute() else ROOT / args.config
    config = load_json(config_path)
    pysoltrace_dir = args.pysoltrace_dir.resolve()
    out = args.out or (run / "soltrace_aimpoint_pilot")
    out = out if out.is_absolute() else ROOT / out
    (out / "tables").mkdir(parents=True, exist_ok=True)
    (out / "figures").mkdir(parents=True, exist_ok=True)
    (out / "maps").mkdir(parents=True, exist_ok=True)

    if not (pysoltrace_dir / "pysoltrace.py").exists():
        raise FileNotFoundError(f"Missing pysoltrace.py under {pysoltrace_dir}")
    if not (pysoltrace_dir / "coretrace_api.so").exists():
        raise FileNotFoundError(f"Missing coretrace_api.so under {pysoltrace_dir}")

    os.chdir(pysoltrace_dir)
    proxy_best = load_proxy_best(run)
    requested_strategies = [part.strip() for part in args.strategies.split(",") if part.strip()]
    records: list[dict[str, float | str | int]] = []
    run_config = {
        "run": str(run),
        "config": str(config_path),
        "pysoltrace_dir": str(pysoltrace_dir),
        "layout_ids": args.layout_ids,
        "max_heliostats": args.max_heliostats,
        "rays": args.rays,
        "threads": args.threads,
        "receiver_panels": args.receiver_panels,
        "receiver_nx": args.receiver_nx,
        "receiver_ny": args.receiver_ny,
        "sun_day": args.sun_day,
        "sun_hour": args.sun_hour,
        "seed": args.seed,
        "strategies": requested_strategies,
    }
    (out / "run_config.json").write_text(json.dumps(run_config, indent=2), encoding="utf-8")

    for layout_ix, layout_id in enumerate([part.strip() for part in args.layout_ids.split(",") if part.strip()]):
        layout_path = run / "layouts" / f"{layout_id}.csv"
        if not layout_path.exists():
            print(f"Skipping missing layout: {layout_id}", flush=True)
            continue
        full_layout = load_layout(layout_path)
        sample = stratified_sample(full_layout, args.max_heliostats, args.seed + layout_ix)
        sample_path = out / "tables" / f"sample_{layout_id}.csv"
        sample.loc[:, ["x_m", "y_m", "z_m"]].to_csv(sample_path, index=False)
        strategy_names = []
        for strategy in requested_strategies:
            if strategy == "proxy_best":
                strategy_names.append(proxy_best.get(layout_id, "proxy_best_missing"))
            else:
                strategy_names.append(strategy)
        strategy_names = list(dict.fromkeys(strategy_names))
        maps: dict[str, np.ndarray] = {}
        for strategy in strategy_names:
            print(f"Running SolTrace pilot: layout={layout_id} strategy={strategy}", flush=True)
            started = time.time()
            pt, panels, sun_meta = build_case(
                pysoltrace_dir=pysoltrace_dir,
                layout=sample,
                plant=config["plant"],
                strategy=strategy,
                sun_day=args.sun_day,
                sun_hour=args.sun_hour,
                rays=args.rays,
                seed=args.seed + 1000 * layout_ix + len(records),
                receiver_panels=args.receiver_panels,
            )
            pt.run(args.seed + 1000 * layout_ix + len(records), True, args.threads, no_callback=True)
            metrics, fmap = flux_metrics(pt, panels, args.receiver_nx, args.receiver_ny)
            maps[strategy] = fmap
            records.append(
                {
                    "layout_id": layout_id,
                    "strategy": strategy,
                    "layout_sha256": sha256(layout_path),
                    "sample_sha256": sha256(sample_path),
                    "full_heliostat_count": int(len(full_layout)),
                    "sampled_heliostat_count": int(len(sample)),
                    "ray_count_requested": int(args.rays),
                    "raydata_rows": int(len(pt.raydata)),
                    "sun_day": int(args.sun_day),
                    "sun_hour": float(args.sun_hour),
                    "sun_x": float(sun_meta["sun_x"]),
                    "sun_y": float(sun_meta["sun_y"]),
                    "sun_z": float(sun_meta["sun_z"]),
                    "elapsed_s": float(time.time() - started),
                    **metrics,
                }
            )
        if maps:
            plot_layout_flux(layout_id, maps, out)
            np.savez_compressed(out / "maps" / f"soltrace_flux_{layout_id}.npz", **maps)

    summary = pd.DataFrame.from_records(records)
    summary.to_csv(out / "tables" / "soltrace_aimpoint_summary.csv", index=False)
    plot_summary(summary, out)
    if not summary.empty:
        best = summary.sort_values(["peak_to_active_mean", "active_flux_cv"]).groupby("layout_id").head(1)
        best.to_csv(out / "tables" / "soltrace_best_by_layout.csv", index=False)
    report = [
        "# Reduced SolTrace Custom-Aimpoint Pilot",
        "",
        "This run uses PySolTrace with the native `coretrace_api.so` backend to test whether the proxy-selected aimpoint patterns remain directionally plausible under direct ray tracing.",
        "",
        "Scope guard: this is a reduced checks pilot, not a final plant redesign. The run uses stratified samples of the full field, a faceted flat-panel approximation of the cylindrical receiver, and one representative solar condition.",
        "",
        f"- Layouts requested: `{args.layout_ids}`",
        f"- Sampled heliostats per layout: {args.max_heliostats}",
        f"- Requested rays per case: {args.rays}",
        f"- Receiver panel approximation: {args.receiver_panels} flat panels, {args.receiver_nx} x {args.receiver_ny} bins each",
        f"- Solar condition: day {args.sun_day}, hour {args.sun_hour}",
        f"- Strategies: `{', '.join(requested_strategies)}`",
        "- Stage order: heliostat reflector stage first, receiver absorber stage second.",
        "",
    ]
    if not summary.empty:
        display_cols = [
            "layout_id",
            "strategy",
            "sampled_heliostat_count",
            "receiver_intercept_per_requested_ray",
            "peak_to_active_mean",
            "active_flux_cv",
            "elapsed_s",
        ]
        report.append(markdown_table(summary.loc[:, display_cols], floatfmt=".4g"))
    (out / "SOLTRACE_AIMPOINT_PILOT_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"Wrote SolTrace pilot outputs to {out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
