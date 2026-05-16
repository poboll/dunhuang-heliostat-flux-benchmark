#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build weather/DNI anchoring tables for the Dunhuang manuscript.")
    parser.add_argument("--weather", type=Path, default=ROOT / "data/weather/dunhuang_nasa_power_2023_sam.csv")
    parser.add_argument(
        "--solarpilot-summary",
        type=Path,
        default=ROOT
        / "server_outputs/streamed_fullfield_20260511_205252/solarpilot_highres_key/tables/solarpilot_summary.csv",
    )
    parser.add_argument("--reported-dni", type=float, default=1883.0)
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "server_outputs/streamed_fullfield_20260511_205252/weather_dni_sensitivity",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out = args.out if args.out.is_absolute() else ROOT / args.out
    (out / "tables").mkdir(parents=True, exist_ok=True)
    (out / "figures").mkdir(parents=True, exist_ok=True)

    weather = pd.read_csv(args.weather, skiprows=2)
    monthly = weather.groupby("Month", as_index=False)["DNI"].sum()
    monthly["dni_kwh_m2"] = monthly["DNI"] / 1000.0
    annual_dni = float(monthly["dni_kwh_m2"].sum())
    scale = float(args.reported_dni / annual_dni)
    monthly["scaled_to_reported_tmy_kwh_m2"] = monthly["dni_kwh_m2"] * scale
    monthly.to_csv(out / "tables" / "monthly_dni_sensitivity.csv", index=False)

    sol = pd.read_csv(args.solarpilot_summary)
    base = sol[sol["layout_id"] == "baseline_full"].iloc[0]
    base_eta = float(base["opteff_mean"])
    base_flux = float(base["flux_peak_to_active_mean"])
    rows = []
    for row in sol.itertuples():
        rows.append(
            {
                "layout_id": row.layout_id,
                "opteff_mean": float(row.opteff_mean),
                "opteff_change_pct": (float(row.opteff_mean) / base_eta - 1.0) * 100.0,
                "flux_peak_value_nasa_weather": float(row.flux_peak_value),
                "flux_peak_value_scaled_to_reported_tmy": float(row.flux_peak_value) * scale,
                "flux_peak_to_active_mean": float(row.flux_peak_to_active_mean),
                "flux_peak_to_active_mean_change_pct": (float(row.flux_peak_to_active_mean) / base_flux - 1.0)
                * 100.0,
            }
        )
    sensitivity = pd.DataFrame(rows)
    sensitivity.to_csv(out / "tables" / "solarpilot_dni_scaled_flux_summary.csv", index=False)

    fig, ax = plt.subplots(figsize=(7.0, 3.8), dpi=180)
    ax.bar(monthly["Month"] - 0.18, monthly["dni_kwh_m2"], width=0.36, label="NASA POWER 2023")
    ax.bar(
        monthly["Month"] + 0.18,
        monthly["scaled_to_reported_tmy_kwh_m2"],
        width=0.36,
        label=f"Scaled to {args.reported_dni:.0f} kWh/m$^2$/y",
    )
    ax.set_xlabel("Month")
    ax.set_ylabel("Monthly DNI (kWh/m$^2$)")
    ax.set_xticks(range(1, 13))
    ax.grid(True, axis="y", alpha=0.22)
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(out / "figures" / "monthly_dni_sensitivity.png", bbox_inches="tight")
    plt.close(fig)

    report = f"""# Weather and DNI Sensitivity

The manuscript uses a public NASA POWER 2023 weather file for reproducibility. The public Dunhuang plant report gives corrected TMY DNI of approximately {args.reported_dni:.0f} kWh m^-2 y^-1.

- NASA POWER 2023 annual DNI in the SAM file: {annual_dni:.1f} kWh m^-2 y^-1.
- Uniform scale factor to match the reported corrected TMY DNI: {scale:.4f}.
- Relative SolarPILOT optical-efficiency changes and peak-to-active-mean flux ratios are unchanged by uniform DNI scaling.
- Absolute flux values scale approximately linearly with DNI under the same optical geometry.

Main tables:

- `tables/monthly_dni_sensitivity.csv`
- `tables/solarpilot_dni_scaled_flux_summary.csv`

Main figure:

- `figures/monthly_dni_sensitivity.png`
"""
    (out / "WEATHER_DNI_SENSITIVITY_REPORT.md").write_text(report, encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
