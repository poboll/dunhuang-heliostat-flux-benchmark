#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
SCRIPTS = ROOT / "scripts"
for path in (SRC, SCRIPTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from dhf_rebuild.data_io import load_json, load_layout, write_layout
from dhf_rebuild.optimizer import build_calibration
from dhf_rebuild.solar_proxy import compute_heliostat_features
from dhf_rebuild.terrain import attach_terrain_features, load_terrain, terrain_relative_layout
from run_fullfield_deformation import PARAM_KEYS, evaluate_candidate, transform_layout


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ablate deformation components for selected full-field layout candidates."
    )
    parser.add_argument("--run", type=Path, required=True, help="Full-field run directory.")
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "server_full.json")
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument(
        "--layout-ids",
        default="deform_0276,deform_0893,deform_1387,deform_1822",
        help="Comma-separated representative layout ids to ablate.",
    )
    parser.add_argument("--export-layouts", action="store_true", help="Write ablation layout CSV files.")
    return parser.parse_args()


def baseline_params() -> dict[str, float]:
    return {
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


def clean_id(text: str) -> str:
    return text.replace("deform_", "d").replace("baseline_", "base").replace("-", "_")


def variants_for(params: dict[str, float]) -> dict[str, dict[str, float]]:
    base = baseline_params()
    full = {key: float(params.get(key, base[key])) for key in PARAM_KEYS}

    def copy_with(**overrides: float) -> dict[str, float]:
        out = dict(full)
        out.update(overrides)
        return out

    scale_only = dict(base)
    scale_only.update({"x_scale": full["x_scale"], "y_scale": full["y_scale"]})

    radial_only = dict(base)
    radial_only.update(
        {
            "radial_scale": full["radial_scale"],
            "radial_wave": full["radial_wave"],
            "north_bias": full["north_bias"],
        }
    )

    twist_only = dict(base)
    twist_only.update({"twist": full["twist"], "az_wave": full["az_wave"]})

    petal_only = dict(base)
    petal_only.update(
        {
            "petal_amp": full["petal_amp"],
            "petal_order": full["petal_order"],
            "petal_phase": full["petal_phase"],
            "petal_twist": full["petal_twist"],
        }
    )

    return {
        "full": full,
        "scale_only": scale_only,
        "radial_north_only": radial_only,
        "twist_wave_only": twist_only,
        "petal_only": petal_only,
        "no_scale": copy_with(x_scale=1.0, y_scale=1.0),
        "no_radial_north": copy_with(radial_scale=0.0, radial_wave=0.0, north_bias=0.0),
        "no_twist_wave": copy_with(twist=0.0, az_wave=0.0, petal_twist=0.0),
        "no_petal": copy_with(petal_amp=0.0, petal_order=0.0, petal_phase=0.0, petal_twist=0.0),
        "no_north_bias": copy_with(north_bias=0.0),
    }


def setup_evaluator(config: dict) -> tuple[pd.DataFrame, pd.DataFrame, float, float, object, dict, pd.DataFrame]:
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
    return base_flat, base, base_sum, base_flux_p99, calibration, eval_config, terrain


def write_markdown_summary(df: pd.DataFrame, out: Path) -> None:
    full = df[df["variant"] == "full"].set_index("source_layout")
    rows = []
    for source_layout, group in df.groupby("source_layout"):
        if source_layout == "baseline_full" or source_layout not in full.index:
            continue
        baseline_energy = float(df[(df["source_layout"] == "baseline_full") & (df["variant"] == "full")]["energy_ratio_vs_baseline"].iloc[0])
        best_energy = group.sort_values("energy_ratio_vs_baseline", ascending=False).iloc[0]
        best_flux = group.sort_values("flux_risk_index", ascending=True).iloc[0]
        rows.append(
            {
                "Layout": source_layout,
                "Full energy ratio": f"{float(full.loc[source_layout, 'energy_ratio_vs_baseline']):.6f}",
                "Full flux index": f"{float(full.loc[source_layout, 'flux_risk_index']):.3f}",
                "Best energy variant": f"{best_energy['variant']} ({float(best_energy['energy_ratio_vs_baseline'] - baseline_energy):+.6f})",
                "Best flux variant": f"{best_flux['variant']} ({float(best_flux['flux_risk_index']):.3f})",
            }
        )
    summary = pd.DataFrame(rows)
    if summary.empty:
        table = "_No ablation rows._"
    else:
        header = "| " + " | ".join(summary.columns) + " |"
        rule = "| " + " | ".join(["---"] * len(summary.columns)) + " |"
        body = [
            "| " + " | ".join(str(row[col]) for col in summary.columns) + " |"
            for _, row in summary.iterrows()
        ]
        table = "\n".join([header, rule, *body])
    report = f"""# Deformation Component Ablation

This ablation decomposes each selected full-field deformation into scale, radial/north-bias, twist/wave, and petal components. It is a proxy-level diagnostic, not a replacement for SolarPILOT numerical checking.

The purpose is reviewer-facing: to show that the deformation family is not a black-box perturbation and to identify which components produce optical gain or flux-risk reduction before expensive numerical checks.

{table}

Main table: `tables/deformation_ablation.csv`
"""
    (out / "DEFORMATION_ABLATION_REPORT.md").write_text(report, encoding="utf-8")


def main() -> int:
    args = parse_args()
    config = load_json(args.config)
    run = args.run if args.run.is_absolute() else ROOT / args.run
    out = args.out or (run / "deformation_ablation")
    out = out if out.is_absolute() else ROOT / out
    (out / "tables").mkdir(parents=True, exist_ok=True)
    if args.export_layouts:
        (out / "layouts").mkdir(parents=True, exist_ok=True)

    reps_path = run / "tables" / "fullfield_representatives.csv"
    reps = pd.read_csv(reps_path)
    selected = ["baseline_full"] + [part.strip() for part in args.layout_ids.split(",") if part.strip()]
    reps = reps[reps["candidate_id"].isin(selected)].copy()
    if reps.empty:
        raise SystemExit(f"No requested representatives found in {reps_path}")

    base_flat, base, base_sum, base_flux_p99, calibration, eval_config, terrain = setup_evaluator(config)
    records = []
    for _, row in reps.iterrows():
        source_layout = str(row["candidate_id"])
        source_role = str(row.get("representative_role", ""))
        params = baseline_params() if source_layout == "baseline_full" else {key: float(row[key]) for key in PARAM_KEYS}
        for variant, variant_params in variants_for(params).items():
            if source_layout == "baseline_full" and variant != "full":
                continue
            ablation_id = f"{clean_id(source_layout)}_{variant}"
            layout = terrain_relative_layout(transform_layout(base_flat, variant_params), terrain)
            record, _ = evaluate_candidate(
                ablation_id, layout, base, base_sum, base_flux_p99, calibration, eval_config, terrain
            )
            record.update(
                {
                    "source_layout": source_layout,
                    "source_role": source_role,
                    "variant": variant,
                    "ablation_id": ablation_id,
                }
            )
            record.update({f"param_{key}": variant_params[key] for key in PARAM_KEYS})
            records.append(record)
            if args.export_layouts:
                write_layout(out / "layouts" / f"{ablation_id}.csv", layout)

    df = pd.DataFrame.from_records(records)
    baseline_row = df[(df["source_layout"] == "baseline_full") & (df["variant"] == "full")].iloc[0]
    df["delta_energy_ratio_vs_baseline"] = df["energy_ratio_vs_baseline"] - float(
        baseline_row["energy_ratio_vs_baseline"]
    )
    df["delta_flux_index_vs_baseline"] = df["flux_risk_index"] - float(baseline_row["flux_risk_index"])
    full_lookup = df[df["variant"] == "full"].set_index("source_layout")
    df["delta_energy_ratio_vs_full"] = [
        row.energy_ratio_vs_baseline - float(full_lookup.loc[row.source_layout, "energy_ratio_vs_baseline"])
        if row.source_layout in full_lookup.index
        else 0.0
        for row in df.itertuples()
    ]
    df["delta_flux_index_vs_full"] = [
        row.flux_risk_index - float(full_lookup.loc[row.source_layout, "flux_risk_index"])
        if row.source_layout in full_lookup.index
        else 0.0
        for row in df.itertuples()
    ]
    df.to_csv(out / "tables" / "deformation_ablation.csv", index=False)
    write_markdown_summary(df, out)
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
