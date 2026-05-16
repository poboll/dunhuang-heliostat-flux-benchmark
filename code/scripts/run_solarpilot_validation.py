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
from scipy.spatial import ConvexHull

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dhf_rebuild.data_io import load_json, sha256


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run preliminary PySAM SolarPILOT numerical checking on exported full-field layouts.")
    parser.add_argument("--run", type=Path, default=ROOT / "server_outputs" / "fullfield_deformation_20260511_153850")
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "server_full.json")
    parser.add_argument("--weather", type=Path, default=ROOT / "data" / "weather" / "dunhuang_nasa_power_2023_sam.csv")
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--layout-ids", default="baseline_full,deform_0202,deform_0229,deform_0168")
    parser.add_argument("--flux-days", type=int, default=8)
    parser.add_argument("--flux-bins", type=int, default=24)
    parser.add_argument("--skip-fluxmaps", action="store_true")
    parser.add_argument("--verbosity", type=int, default=0)
    return parser.parse_args()


def load_layout(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, header=None, names=["x_m", "y_m", "z_m"])
    df["radius_m"] = np.hypot(df["x_m"], df["y_m"])
    return df


def solarpilot_inputs(
    layout: pd.DataFrame,
    config: dict,
    weather: Path,
    flux_days: int,
    flux_bins: int,
    calc_fluxmaps: bool,
) -> dict[str, float | str | tuple]:
    plant = config["plant"]
    mirror_area = float(plant.get("heliostat_mirror_area_m2", 115.72))
    heliostat_width = float(plant.get("heliostat_width_m", math.sqrt(mirror_area)))
    heliostat_height = float(plant.get("heliostat_height_m", math.sqrt(mirror_area)))
    active_area = max(heliostat_width * heliostat_height, 1e-12)
    active_fraction = min(1.0, mirror_area / active_area)
    receiver_diameter = float(plant.get("receiver_diameter_m", 15.13))
    receiver_height = float(plant.get("receiver_height_m", 18.67))
    receiver_center = float(
        plant.get(
            "receiver_center_height_m",
            float(plant.get("tower_height_m", 229.3)) + receiver_height / 2.0,
        )
    )
    receiver_area = math.pi * receiver_diameter * receiver_height
    return {
        "solar_resource_file": str(weather),
        "helio_positions_in": tuple((float(row.x_m), float(row.y_m)) for row in layout.itertuples()),
        "is_optimize": 0.0,
        "calc_fluxmaps": 1.0 if calc_fluxmaps else 0.0,
        "check_max_flux": 0.0,
        "dni_des": 950.0,
        "q_design": float(plant.get("receiver_rated_input_mw", 630.0)),
        "receiver_type": 0.0,
        "h_tower": receiver_center,
        "rec_height": receiver_height,
        "rec_aspect": receiver_height / receiver_diameter,
        "rec_absorptance": 0.94,
        "rec_hl_perm2": 20.0,
        "helio_width": heliostat_width,
        "helio_height": heliostat_height,
        "helio_active_fraction": active_fraction,
        "helio_reflectance": float(plant.get("heliostat_reflectivity_clean", 0.94)),
        "helio_optical_error": float(plant.get("heliostat_optical_error_rad", 0.0029)),
        "dens_mirror": 0.97,
        "n_facet_x": float(plant.get("heliostat_facet_x", 5)),
        "n_facet_y": float(plant.get("heliostat_facet_y", 7)),
        "cant_type": 0.0,
        "focus_type": 0.0,
        "land_min": 0.5,
        "land_max": 10.0,
        "n_flux_x": float(flux_bins),
        "n_flux_y": float(flux_bins),
        "n_flux_days": float(flux_days),
        "delta_flux_hrs": 1.0,
        "flux_max": 1000.0,
        "opt_flux_penalty": 0.25,
        "heliostat_spec_cost": 120.0,
        "cost_sf_fixed": 0.0,
        "land_spec_cost": 10000.0,
        "site_spec_cost": 10.0,
        "csp_pt_sf_fixed_land_area": 0.0,
        "csp_pt_sf_land_overhead_factor": 1.0,
        "tower_fixed_cost": 3000000.0,
        "tower_exp": 0.0113,
        "rec_ref_cost": 100000000.0,
        "rec_ref_area": receiver_area,
        "rec_cost_exp": 0.7,
        "contingency_rate": 7.0,
        "sales_tax_frac": 80.0,
        "sales_tax_rate": 5.0,
    }


def run_layout(layout_id: str, layout_path: Path, config: dict, weather: Path, out: Path, args: argparse.Namespace) -> dict[str, float | str | int]:
    import PySAM.Solarpilot as sp

    layout = load_layout(layout_path)
    model = sp.new()
    inputs = solarpilot_inputs(layout, config, weather, args.flux_days, args.flux_bins, not args.skip_fluxmaps)
    model.SolarPILOT.assign(inputs)
    model.execute(args.verbosity)
    exported = model.Outputs.export()

    opteff = pd.DataFrame(exported["opteff_table"], columns=["azimuth_deg", "zenith_deg", "optical_efficiency"])
    opteff.to_csv(out / "tables" / f"opteff_{layout_id}.csv", index=False)

    bins = int(args.flux_bins)
    flux = np.asarray(exported.get("flux_table", []), dtype=float)
    if args.skip_fluxmaps:
        flux = np.empty((0, bins), dtype=float)
    if flux.size:
        pd.DataFrame(flux).to_csv(out / "tables" / f"flux_table_{layout_id}.csv", index=False, header=False)
        map_count = int(len(flux) / bins) if bins > 0 else 0
        cube = flux.reshape(map_count, bins, bins) if map_count > 0 else np.empty((0, bins, bins))
        map_peaks = cube.max(axis=(1, 2)) if len(cube) else np.array([0.0])
        peak_idx = int(map_peaks.argmax()) if len(cube) else 0
        peak_map = cube[peak_idx] if len(cube) else np.zeros((bins, bins))
        active = flux[flux > np.percentile(flux, 55)] if flux.size else np.array([0.0])
        if len(active) == 0:
            active = np.array([0.0])

        fig, ax = plt.subplots(figsize=(5.4, 4.2), dpi=170)
        im = ax.imshow(peak_map, origin="lower", cmap="inferno", aspect="auto")
        ax.set_title(f"SolarPILOT flux table peak map: {layout_id}")
        ax.set_xlabel("receiver x bins")
        ax.set_ylabel("receiver y bins")
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        fig.tight_layout()
        fig.savefig(out / "figures" / f"solarpilot_flux_peak_{layout_id}.png", bbox_inches="tight")
        plt.close(fig)
    else:
        map_count = 0
        active = np.array([0.0])

    mirror_area = float(config["plant"].get("heliostat_mirror_area_m2", 115.72))
    aperture = len(layout) * mirror_area
    xy = layout.loc[:, ["x_m", "y_m"]].to_numpy(dtype=float)
    hull_area = float(ConvexHull(xy).volume) if len(xy) >= 3 else 0.0
    return {
        "layout_id": layout_id,
        "layout_sha256": sha256(layout_path),
        "weather_file": str(weather),
        "weather_sha256": sha256(weather),
        "heliostat_count": len(layout),
        "reported_number_heliostats": float(exported.get("number_heliostats", len(layout))),
        "aperture_area_m2_input": aperture,
        "max_radius_m": float(layout["radius_m"].max()),
        "x_span_p99_m": float(layout["x_m"].quantile(0.995) - layout["x_m"].quantile(0.005)),
        "y_span_p99_m": float(layout["y_m"].quantile(0.995) - layout["y_m"].quantile(0.005)),
        "convex_hull_area_m2": hull_area,
        "area_sf_output_m2": float(exported.get("area_sf", 0.0) or 0.0),
        "land_area_output_m2": float(exported.get("land_area", 0.0) or 0.0),
        "base_land_area_output_m2": float(exported.get("base_land_area", 0.0) or 0.0),
        "opteff_mean": float(opteff["optical_efficiency"].mean()),
        "opteff_min": float(opteff["optical_efficiency"].min()),
        "opteff_max": float(opteff["optical_efficiency"].max()),
        "opteff_p10": float(opteff["optical_efficiency"].quantile(0.10)),
        "opteff_p90": float(opteff["optical_efficiency"].quantile(0.90)),
        "flux_table_rows": int(flux.shape[0]),
        "flux_table_cols": int(flux.shape[1]) if flux.ndim == 2 else 0,
        "flux_map_count": map_count,
        "flux_peak_value": float(flux.max()) if flux.size else 0.0,
        "flux_mean_active": float(active.mean()) if len(active) else 0.0,
        "flux_peak_to_active_mean": float(flux.max() / max(active.mean(), 1e-12)) if flux.size else 0.0,
        "flux_active_cv": float(active.std() / max(active.mean(), 1e-12)) if len(active) else 0.0,
        "note": "PySAM Solarpilot helio_positions_in uses x/y positions; terrain z and custom staggered aiming are not represented in this preliminary run.",
    }


def write_comparison_plot(df: pd.DataFrame, out: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(12.5, 3.8), dpi=170)
    x = np.arange(len(df))
    labels = df["layout_id"].tolist()
    metrics = [
        ("opteff_mean", "Mean optical efficiency"),
        ("flux_peak_to_active_mean", "Peak / active mean flux"),
        ("convex_hull_area_m2", "Coordinate convex hull area"),
    ]
    for ax, (col, title) in zip(axes, metrics):
        ax.bar(x, df[col].astype(float), color="#2a9d8f")
        ax.set_title(title, fontsize=9, fontweight="bold")
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=35, ha="right", fontsize=7)
        ax.grid(True, axis="y", alpha=0.18)
    fig.tight_layout()
    fig.savefig(out / "figures" / "solarpilot_validation_comparison.png", bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    args = parse_args()
    run = args.run if args.run.is_absolute() else ROOT / args.run
    config = load_json(args.config)
    weather = args.weather if args.weather.is_absolute() else ROOT / args.weather
    out = args.out or (run / "solarpilot_validation")
    out = out if out.is_absolute() else ROOT / out
    (out / "tables").mkdir(parents=True, exist_ok=True)
    (out / "figures").mkdir(parents=True, exist_ok=True)
    (out / "run_config.json").write_text(
        json.dumps(
            {
                "run": str(run),
                "config": str(args.config),
                "weather": str(weather),
                "layout_ids": args.layout_ids,
                "flux_days": args.flux_days,
                "flux_bins": args.flux_bins,
                "skip_fluxmaps": args.skip_fluxmaps,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    records = []
    for layout_id in [part.strip() for part in args.layout_ids.split(",") if part.strip()]:
        layout_path = run / "layouts" / f"{layout_id}.csv"
        if not layout_path.exists():
            print(f"Skipping missing layout {layout_id}")
            continue
        print(f"Running PySAM SolarPILOT for {layout_id}", flush=True)
        records.append(run_layout(layout_id, layout_path, config, weather, out, args))
    summary = pd.DataFrame.from_records(records)
    summary.to_csv(out / "tables" / "solarpilot_summary.csv", index=False)
    if not summary.empty:
        write_comparison_plot(summary, out)
    report = f"""# Preliminary PySAM SolarPILOT Numerical Check

This run imports exported full-field layout coordinates into `PySAM.Solarpilot`.

Important limitation: `helio_positions_in` accepts x/y field coordinates through the current PySAM wrapper. Terrain-relative z coordinates and custom staggered receiver aiming are not represented in this run. Use these outputs as preliminary layout-level SolarPILOT checks, not as final high-fidelity terrain or aiming verification.

- Layouts evaluated: {len(summary)}
- Weather file: `{weather}`
- Flux days: {args.flux_days}
- Flux bins: {args.flux_bins} x {args.flux_bins}
- Receiver center height: {float(config["plant"].get("receiver_center_height_m", 0.0)):.1f} m
- Receiver diameter/height: {float(config["plant"].get("receiver_diameter_m", 0.0)):.2f} m / {float(config["plant"].get("receiver_height_m", 0.0)):.2f} m
- Heliostat aperture and dimensions: {float(config["plant"].get("heliostat_mirror_area_m2", 0.0)):.2f} m2; {float(config["plant"].get("heliostat_width_m", 0.0)):.2f} m x {float(config["plant"].get("heliostat_height_m", 0.0)):.2f} m

Main table: `tables/solarpilot_summary.csv`
"""
    (out / "SOLARPILOT_VALIDATION_REPORT.md").write_text(report, encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
