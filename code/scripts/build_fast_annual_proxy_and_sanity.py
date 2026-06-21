#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import shutil
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "paper_submission" / "solar_energy_elsarticle_v8_strict_review_rescue"

PUBLIC_PLANT_ANNUAL_GENERATION_MWH = 351_600.0
RATED_POWER_MW = 100.0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build a conservative fast-annual proxy and public-plant sanity check from "
            "hourly NASA POWER DNI and SolarPILOT optical-efficiency tables."
        )
    )
    parser.add_argument("--weather", type=Path, default=ROOT / "data/weather/dunhuang_nasa_power_2023_sam.csv")
    parser.add_argument(
        "--solarpilot-tables",
        type=Path,
        default=ROOT / "server_outputs/same_anchor_strong_baselines_20260523/solarpilot_strong_baseline/tables",
    )
    parser.add_argument(
        "--package",
        type=Path,
        default=PACKAGE,
        help="Submission package directory to receive supplementary copies.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "server_outputs/fast_annual_proxy_sanity_20260524",
    )
    parser.add_argument("--reported-dni", type=float, default=1883.0)
    parser.add_argument("--mirror-area-m2", type=float, default=115.72)
    parser.add_argument("--heliostat-count", type=int, default=11915)
    parser.add_argument("--rated-power-mw", type=float, default=RATED_POWER_MW)
    parser.add_argument("--reference-generation-mwh", type=float, default=PUBLIC_PLANT_ANNUAL_GENERATION_MWH)
    parser.add_argument("--reference-source-key", default="huang2024dunhuang_design_generation")
    return parser.parse_args()


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def solar_position_approx(latitude_deg: float, day_of_year: np.ndarray, hour: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    lat = np.deg2rad(latitude_deg)
    decl = np.deg2rad(23.45) * np.sin(2 * np.pi * (284 + day_of_year) / 365.0)
    hour_angle = np.deg2rad(15.0 * (hour - 12.0))
    sx = -np.cos(decl) * np.sin(hour_angle)
    sy = np.cos(lat) * np.sin(decl) - np.sin(lat) * np.cos(decl) * np.cos(hour_angle)
    sz = np.sin(lat) * np.sin(decl) + np.cos(lat) * np.cos(decl) * np.cos(hour_angle)
    sz = np.clip(sz, -1.0, 1.0)
    zenith = np.rad2deg(np.arccos(sz))
    # SolarPILOT opteff tables use an azimuth axis that is 0 at solar south and
    # positive to the west/east symmetry used by the imported field checks.
    azimuth = np.rad2deg(np.arctan2(sx, -sy))
    return azimuth, zenith


def load_weather(weather_path: Path) -> pd.DataFrame:
    weather = pd.read_csv(weather_path, skiprows=2)
    required = {"Year", "Month", "Day", "Hour", "DNI"}
    missing = required.difference(weather.columns)
    if missing:
        raise ValueError(f"Missing weather columns: {sorted(missing)}")
    timestamps = pd.to_datetime(
        {
            "year": weather["Year"].astype(int),
            "month": weather["Month"].astype(int),
            "day": weather["Day"].astype(int),
            "hour": weather["Hour"].astype(int),
        },
        errors="coerce",
    )
    weather = weather.copy()
    weather["day_of_year"] = timestamps.dt.dayofyear.astype(int)
    weather["solar_hour"] = weather["Hour"].astype(float) + 0.5
    az, zen = solar_position_approx(40.063, weather["day_of_year"].to_numpy(float), weather["solar_hour"].to_numpy(float))
    weather["solar_azimuth_deg"] = az
    weather["solar_zenith_deg"] = zen
    weather["is_daylight"] = (weather["DNI"].astype(float) > 0.0) & (weather["solar_zenith_deg"] < 90.0)
    return weather


def idw_interpolate_opteff(opteff: pd.DataFrame, weather: pd.DataFrame, k: int = 6) -> np.ndarray:
    pts = opteff.loc[:, ["azimuth_deg", "zenith_deg"]].to_numpy(float)
    values = opteff["optical_efficiency"].to_numpy(float)
    query = weather.loc[:, ["solar_azimuth_deg", "solar_zenith_deg"]].to_numpy(float)
    diff = query[:, None, :] - pts[None, :, :]
    dist = np.sqrt(np.sum(diff * diff, axis=2))
    order = np.argpartition(dist, kth=min(k, len(values) - 1), axis=1)[:, :k]
    chosen_dist = np.take_along_axis(dist, order, axis=1)
    chosen_values = values[order]
    weights = 1.0 / np.maximum(chosen_dist, 1e-6) ** 2
    interpolated = np.sum(weights * chosen_values, axis=1) / np.sum(weights, axis=1)
    interpolated[~weather["is_daylight"].to_numpy(bool)] = 0.0
    return interpolated


def annual_proxy_for_layout(
    layout_id: str,
    opteff_path: Path,
    weather: pd.DataFrame,
    args: argparse.Namespace,
    dni_scale: float,
) -> dict[str, float | str]:
    opteff = pd.read_csv(opteff_path)
    eta_hourly = idw_interpolate_opteff(opteff, weather)
    dni = weather["DNI"].to_numpy(float)
    aperture_area_m2 = float(args.heliostat_count) * float(args.mirror_area_m2)
    thermal_mwh = dni * aperture_area_m2 * eta_hourly / 1_000_000.0
    thermal_mwh_scaled = dni * dni_scale * aperture_area_m2 * eta_hourly / 1_000_000.0
    daylight = weather["is_daylight"].to_numpy(bool)
    weights = np.where(daylight, dni, 0.0)
    weighted_eta = float(np.sum(eta_hourly * weights) / max(np.sum(weights), 1e-12))
    return {
        "layout_id": layout_id,
        "opteff_table": opteff_path.name,
        "opteff_table_mean": float(opteff["optical_efficiency"].mean()),
        "annual_dni_weighted_eta": weighted_eta,
        "annual_thermal_proxy_mwh_nasa": float(np.sum(thermal_mwh)),
        "annual_thermal_proxy_mwh_reported_tmy_scaled": float(np.sum(thermal_mwh_scaled)),
        "max_hourly_thermal_proxy_mw": float(np.max(thermal_mwh)),
        "positive_dni_hours": int(daylight.sum()),
        "interp_min_eta": float(np.min(eta_hourly[daylight])) if np.any(daylight) else 0.0,
        "interp_p10_eta": float(np.quantile(eta_hourly[daylight], 0.10)) if np.any(daylight) else 0.0,
        "interp_p90_eta": float(np.quantile(eta_hourly[daylight], 0.90)) if np.any(daylight) else 0.0,
    }


def build_summary(args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, float | str]]:
    weather = load_weather(resolve(args.weather))
    annual_dni = float(weather["DNI"].sum() / 1000.0)
    dni_scale = float(args.reported_dni / annual_dni)
    tables_dir = resolve(args.solarpilot_tables)
    records = []
    for path in sorted(tables_dir.glob("opteff_*.csv")):
        layout_id = path.stem.replace("opteff_", "")
        records.append(annual_proxy_for_layout(layout_id, path, weather, args, dni_scale))
    if not records:
        raise FileNotFoundError(f"No opteff_*.csv files found in {tables_dir}")
    summary = pd.DataFrame(records)
    base = summary.loc[summary["layout_id"] == "baseline_full"].iloc[0]
    for col in ["opteff_table_mean", "annual_dni_weighted_eta", "annual_thermal_proxy_mwh_nasa", "annual_thermal_proxy_mwh_reported_tmy_scaled"]:
        summary[f"delta_{col}_pct"] = 100.0 * (summary[col].astype(float) / float(base[col]) - 1.0)
    calibrated_eff = float(args.reference_generation_mwh / float(base["annual_thermal_proxy_mwh_reported_tmy_scaled"]))
    summary["electric_proxy_mwh_calibrated_to_public_generation"] = (
        summary["annual_thermal_proxy_mwh_reported_tmy_scaled"].astype(float) * calibrated_eff
    )
    summary["delta_electric_proxy_pct"] = 100.0 * (
        summary["electric_proxy_mwh_calibrated_to_public_generation"].astype(float) / args.reference_generation_mwh - 1.0
    )
    summary = summary.sort_values("annual_thermal_proxy_mwh_reported_tmy_scaled", ascending=False).reset_index(drop=True)

    monthly = weather.groupby("Month", as_index=False)["DNI"].sum()
    monthly["dni_kwh_m2_nasa"] = monthly["DNI"] / 1000.0
    monthly["dni_kwh_m2_reported_tmy_scaled"] = monthly["dni_kwh_m2_nasa"] * dni_scale
    monthly = monthly.drop(columns=["DNI"])

    sanity = {
        "weather_annual_dni_kwh_m2": annual_dni,
        "reported_corrected_tmy_dni_kwh_m2": args.reported_dni,
        "dni_scale_factor": dni_scale,
        "baseline_annual_thermal_proxy_mwh_reported_tmy_scaled": float(
            base["annual_thermal_proxy_mwh_reported_tmy_scaled"]
        ),
        "public_reference_annual_generation_mwh": float(args.reference_generation_mwh),
        "calibrated_net_electric_conversion_factor": calibrated_eff,
        "public_design_capacity_factor_pct": float(
            100.0 * args.reference_generation_mwh / (float(args.rated_power_mw) * 8760.0)
        ),
        "reference_source_key": args.reference_source_key,
    }
    return summary, monthly, sanity


def write_figure(summary: pd.DataFrame, monthly: pd.DataFrame, sanity: dict[str, float | str], out: Path) -> None:
    top = summary.head(10).copy()
    colors = ["#244C74" if v == "baseline_full" else "#4C78A8" for v in top["layout_id"]]
    fig, axes = plt.subplots(1, 3, figsize=(12.6, 3.8), dpi=220)

    x = np.arange(len(top))
    axes[0].bar(x, top["delta_annual_thermal_proxy_mwh_reported_tmy_scaled_pct"], color=colors, edgecolor="#ffffff", linewidth=0.5)
    axes[0].axhline(0, color="#222222", linewidth=0.8)
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(top["layout_id"], rotation=38, ha="right", fontsize=7)
    axes[0].set_ylabel("Annual proxy change (%)")
    axes[0].set_title("(a) Fast annual thermal proxy", fontsize=9)
    axes[0].grid(True, axis="y", alpha=0.22)

    axes[1].plot(monthly["Month"], monthly["dni_kwh_m2_nasa"], color="#4C78A8", marker="o", linewidth=1.6, label="NASA POWER 2023")
    axes[1].plot(
        monthly["Month"],
        monthly["dni_kwh_m2_reported_tmy_scaled"],
        color="#E45756",
        marker="s",
        linewidth=1.4,
        label="Scaled to public TMY DNI",
    )
    axes[1].set_xticks(range(1, 13))
    axes[1].set_xlabel("Month")
    axes[1].set_ylabel("DNI (kWh m$^{-2}$)")
    axes[1].set_title("(b) Weather anchoring", fontsize=9)
    axes[1].grid(True, axis="y", alpha=0.22)
    axes[1].legend(frameon=False, fontsize=7)

    baseline_generation = float(sanity["public_reference_annual_generation_mwh"])
    calibrated_generation = baseline_generation
    calibrated_eff = float(sanity["calibrated_net_electric_conversion_factor"])
    axes[2].bar([0, 1], [baseline_generation / 1000.0, calibrated_generation / 1000.0], color=["#244C74", "#72B7B2"])
    axes[2].set_xticks([0, 1])
    axes[2].set_xticklabels(["Public design\nreference", "Calibrated\nbaseline proxy"], fontsize=7)
    axes[2].set_ylabel("Annual electric energy (GWh)")
    axes[2].set_title("(c) Plant-scale sanity check", fontsize=9)
    axes[2].grid(True, axis="y", alpha=0.22)
    ymax = max(baseline_generation, calibrated_generation) / 1000.0 * 1.18
    axes[2].set_ylim(0, ymax)
    for idx, val in enumerate([baseline_generation / 1000.0, calibrated_generation / 1000.0]):
        axes[2].text(idx, val + ymax * 0.015, f"{val:.1f}", ha="center", va="bottom", fontsize=7)
    axes[2].text(
        0.02,
        0.98,
        f"proxy conversion factor: {calibrated_eff:.3f}",
        transform=axes[2].transAxes,
        ha="left",
        va="top",
        fontsize=7,
        color="#333333",
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.82, "pad": 1.6},
    )

    fig.tight_layout(w_pad=2.0)
    fig.savefig(out / "figures/fig_fast_annual_proxy_sanity.png", bbox_inches="tight")
    fig.savefig(out / "figures/fig_fast_annual_proxy_sanity.pdf", bbox_inches="tight")
    plt.close(fig)


def write_report(summary: pd.DataFrame, sanity: dict[str, float | str], out: Path) -> None:
    base = summary.loc[summary["layout_id"] == "baseline_full"].iloc[0]
    leaders = summary.head(6)
    lines = [
        "# Fast Annual Proxy and Public Plant Sanity Check",
        "",
        "## Scope",
        "",
        "This audit is a conservative annualization bridge, not full-field annual custom-aimpoint validation. "
        "It interpolates each SolarPILOT optical-efficiency table over the 8760-hour NASA POWER 2023 weather file, "
        "weights daylight hours by DNI, uniformly scales DNI to the public Dunhuang corrected-TMY annual DNI, and "
        "uses the reported public annual generation only as a plant-scale sanity anchor.",
        "",
        "## Weather and Plant-Scale Anchors",
        "",
        f"- NASA POWER 2023 annual DNI: {float(sanity['weather_annual_dni_kwh_m2']):.1f} kWh m^-2 y^-1.",
        f"- Public corrected-TMY annual DNI: {float(sanity['reported_corrected_tmy_dni_kwh_m2']):.1f} kWh m^-2 y^-1.",
        f"- Uniform DNI scale factor: {float(sanity['dni_scale_factor']):.4f}.",
        f"- Public annual-generation reference used for sanity checking: {float(sanity['public_reference_annual_generation_mwh']):,.0f} MWh y^-1.",
        f"- Baseline annual thermal proxy after DNI scaling: {float(base['annual_thermal_proxy_mwh_reported_tmy_scaled']):,.0f} MWh_th y^-1.",
        f"- Calibrated net electric conversion factor needed to match the public design-generation reference: {float(sanity['calibrated_net_electric_conversion_factor']):.3f}.",
        f"- The public design generation corresponds to a {float(sanity['public_design_capacity_factor_pct']):.2f}% capacity factor for a 100 MW plant.",
        "",
        "## Ranking Signal",
        "",
        "Top rows by the reported-TMY-scaled thermal proxy:",
        "",
        "| Layout | Annual thermal proxy (MWh_th/y) | Change vs baseline (%) | Calibrated electric proxy (GWh_e/y) |",
        "| --- | ---: | ---: | ---: |",
    ]
    for row in leaders.itertuples(index=False):
        lines.append(
            f"| `{row.layout_id}` | {float(row.annual_thermal_proxy_mwh_reported_tmy_scaled):,.0f} | "
            f"{float(row.delta_annual_thermal_proxy_mwh_reported_tmy_scaled_pct):+.2f} | "
            f"{float(row.electric_proxy_mwh_calibrated_to_public_generation)/1000.0:.1f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The audit links representative SolarPILOT optical tables to the full public-weather year, so it is stronger than a single design-point comparison.",
            "- It still uses SolarPILOT default aiming and interpolated optical-efficiency tables, not custom annual ray tracing.",
            "- The public-generation sanity check shows that the baseline annual proxy is in the right plant-scale order after a plausible net electric conversion calibration.",
            "- Percentage changes from this table may be cited as annual-proxy ranking evidence, but not as bankable annual generation or final plant redesign evidence.",
        ]
    )
    (out / "FAST_ANNUAL_PROXY_AND_PLANT_SANITY_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def copy_to_package(out: Path, package: Path) -> None:
    sup = package / "supplementary_data" / "fast_annual_proxy_sanity"
    if sup.exists():
        shutil.rmtree(sup)
    shutil.copytree(out, sup)
    fig_src = out / "figures/fig_fast_annual_proxy_sanity.png"
    fig_dst = package / "latex/figures/fig_fast_annual_proxy_sanity.png"
    fig_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(fig_src, fig_dst)
    code_dst = package / "code/scripts/build_fast_annual_proxy_and_sanity.py"
    code_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(Path(__file__), code_dst)


def main() -> int:
    args = parse_args()
    out = resolve(args.out)
    package = resolve(args.package)
    (out / "tables").mkdir(parents=True, exist_ok=True)
    (out / "figures").mkdir(parents=True, exist_ok=True)
    summary, monthly, sanity = build_summary(args)
    summary.to_csv(out / "tables/fast_annual_proxy_summary.csv", index=False)
    monthly.to_csv(out / "tables/fast_annual_proxy_monthly_dni.csv", index=False)
    (out / "tables/plant_sanity.json").write_text(json.dumps(sanity, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "run_config.json").write_text(
        json.dumps(
            {
                "weather": str(resolve(args.weather)),
                "solarpilot_tables": str(resolve(args.solarpilot_tables)),
                "reported_dni": args.reported_dni,
                "heliostat_count": args.heliostat_count,
                "mirror_area_m2": args.mirror_area_m2,
                "rated_power_mw": args.rated_power_mw,
                "reference_generation_mwh": args.reference_generation_mwh,
                "aperture_energy_formula": "sum(DNI_hour * heliostat_count * mirror_area * interpolated_SolarPILOT_eta) / 1e6",
                "claim_boundary": "fast annual proxy and public plant sanity check, not annual custom-aimpoint validation",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    write_figure(summary, monthly, sanity, out)
    write_report(summary, sanity, out)
    copy_to_package(out, package)
    print(f"Wrote fast annual proxy and plant sanity check to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
