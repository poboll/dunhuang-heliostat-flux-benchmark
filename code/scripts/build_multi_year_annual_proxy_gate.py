#!/usr/bin/env python3
from __future__ import annotations

import argparse
import glob
import json
import shutil
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "paper_submission" / "solar_energy_elsarticle_v8_strict_review_rescue"
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from build_fast_annual_proxy_and_sanity import (  # noqa: E402
    idw_interpolate_opteff,
    load_weather,
)


SELECTED_LAYOUTS = {
    "baseline_full": "L0",
    "deform_0276": "L_opt",
    "deform_0893": "L_nom",
    "deform_1387": "L_rob",
    "joint_g02_0333": "J_bal",
    "joint_g04_0478": "J_flux",
    "sb_hy_energy": "B_hy,E",
    "sb_pf_flux": "B_pf,R",
    "sb_hs_flux": "B_hs,R",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build a multi-year annual-proxy robustness gate from NASA POWER SAM weather files "
            "and the existing SolarPILOT optical-efficiency tables."
        )
    )
    parser.add_argument(
        "--weather-glob",
        default=str(ROOT / "data/weather/dunhuang_nasa_power_*_sam.csv"),
        help="Glob for SAM weather files. The year is inferred from the filename.",
    )
    parser.add_argument(
        "--solarpilot-tables",
        type=Path,
        default=ROOT / "server_outputs/same_anchor_strong_baselines_20260523/solarpilot_strong_baseline/tables",
    )
    parser.add_argument("--out", type=Path, default=ROOT / "server_outputs/multiyear_annual_proxy_gate_20260524")
    parser.add_argument("--package", type=Path, default=PACKAGE)
    parser.add_argument("--mirror-area-m2", type=float, default=115.72)
    parser.add_argument("--heliostat-count", type=int, default=11915)
    parser.add_argument(
        "--selected-layouts",
        default=",".join(SELECTED_LAYOUTS.keys()),
        help="Comma-separated layout ids to show in the manuscript-facing figure.",
    )
    return parser.parse_args()


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def infer_year(path: Path) -> int:
    for token in path.stem.split("_"):
        if token.isdigit() and len(token) == 4:
            return int(token)
    raise ValueError(f"Cannot infer year from {path}")


def annual_proxy_for_weather(
    weather_path: Path,
    solarpilot_tables: Path,
    heliostat_count: int,
    mirror_area_m2: float,
) -> pd.DataFrame:
    weather = load_weather(weather_path)
    aperture_area_m2 = float(heliostat_count) * float(mirror_area_m2)
    records: list[dict[str, float | str | int]] = []
    for opteff_path in sorted(solarpilot_tables.glob("opteff_*.csv")):
        layout_id = opteff_path.stem.replace("opteff_", "")
        opteff = pd.read_csv(opteff_path)
        eta = idw_interpolate_opteff(opteff, weather)
        dni = weather["DNI"].to_numpy(float)
        daylight = weather["is_daylight"].to_numpy(bool)
        thermal_mwh = dni * aperture_area_m2 * eta / 1_000_000.0
        weights = np.where(daylight, dni, 0.0)
        weighted_eta = float(np.sum(eta * weights) / max(np.sum(weights), 1e-12))
        records.append(
            {
                "year": infer_year(weather_path),
                "weather_file": str(weather_path),
                "layout_id": layout_id,
                "annual_dni_kwh_m2": float(weather["DNI"].sum() / 1000.0),
                "positive_dni_hours": int(daylight.sum()),
                "annual_dni_weighted_eta": weighted_eta,
                "annual_thermal_proxy_mwh": float(np.sum(thermal_mwh)),
                "opteff_table_mean": float(opteff["optical_efficiency"].mean()),
            }
        )
    df = pd.DataFrame.from_records(records)
    if df.empty:
        raise FileNotFoundError(f"No opteff_*.csv tables found in {solarpilot_tables}")
    base = df[df["layout_id"] == "baseline_full"].loc[:, ["year", "annual_thermal_proxy_mwh", "annual_dni_weighted_eta"]]
    base = base.rename(
        columns={
            "annual_thermal_proxy_mwh": "baseline_annual_thermal_proxy_mwh",
            "annual_dni_weighted_eta": "baseline_annual_dni_weighted_eta",
        }
    )
    df = df.merge(base, on="year", how="left")
    df["delta_annual_thermal_proxy_pct"] = 100.0 * (
        df["annual_thermal_proxy_mwh"] / df["baseline_annual_thermal_proxy_mwh"] - 1.0
    )
    df["delta_annual_dni_weighted_eta_pct"] = 100.0 * (
        df["annual_dni_weighted_eta"] / df["baseline_annual_dni_weighted_eta"] - 1.0
    )
    df["annual_rank"] = df.groupby("year")["annual_thermal_proxy_mwh"].rank(method="min", ascending=False)
    return df


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    nonbase = df[df["layout_id"] != "baseline_full"].copy()
    summary = (
        nonbase.groupby("layout_id", as_index=False)
        .agg(
            years=("year", "nunique"),
            mean_delta_annual_pct=("delta_annual_thermal_proxy_pct", "mean"),
            min_delta_annual_pct=("delta_annual_thermal_proxy_pct", "min"),
            max_delta_annual_pct=("delta_annual_thermal_proxy_pct", "max"),
            std_delta_annual_pct=("delta_annual_thermal_proxy_pct", "std"),
            sign_positive_fraction=("delta_annual_thermal_proxy_pct", lambda x: float((x > 0.0).mean())),
            best_rank=("annual_rank", "min"),
            median_rank=("annual_rank", "median"),
            worst_rank=("annual_rank", "max"),
        )
        .sort_values(["mean_delta_annual_pct"], ascending=False)
    )
    summary["label"] = summary["layout_id"].map(lambda x: SELECTED_LAYOUTS.get(x, x))
    return summary


def gate_decision(summary: pd.DataFrame, selected_ids: list[str]) -> dict[str, object]:
    selected = summary[summary["layout_id"].isin([x for x in selected_ids if x != "baseline_full"])].copy()
    annual_positive_ids = {"deform_0276", "deform_0893", "deform_1387", "joint_g02_0333", "sb_hy_energy"}
    pressure_ids = {"joint_g04_0478", "sb_pf_flux", "sb_hs_flux"}

    positive = selected[selected["layout_id"].isin(annual_positive_ids)]
    positive_stable = bool((positive["sign_positive_fraction"] >= 1.0).all()) if not positive.empty else False
    lopt = summary[summary["layout_id"] == "deform_0276"]
    lopt_top3 = bool((not lopt.empty) and float(lopt.iloc[0]["worst_rank"]) <= 3.0)
    pressure = selected[selected["layout_id"].isin(pressure_ids)]
    pressure_boundary_ok = bool((pressure["mean_delta_annual_pct"] <= 0.5).all()) if not pressure.empty else False

    passes = positive_stable and lopt_top3 and pressure_boundary_ok
    return {
        "writeback_recommendation": "write_short_robustness_sentence" if passes else "do_not_write_main_text",
        "positive_rows_all_years_positive": positive_stable,
        "lopt_remains_top3_all_years": lopt_top3,
        "receiver_pressure_rows_not_annual_headline": pressure_boundary_ok,
        "interpretation": (
            "Annual-proxy role signs are stable across the available NASA POWER weather years."
            if passes
            else "Multi-year annual proxy does not clear the conservative main-text robustness gate."
        ),
    }


def write_figure(df: pd.DataFrame, summary: pd.DataFrame, selected_ids: list[str], out: Path) -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
            "font.size": 8.5,
            "axes.titlesize": 9.4,
            "axes.labelsize": 8.5,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )
    plot = df[df["layout_id"].isin(selected_ids)].copy()
    plot["label"] = plot["layout_id"].map(lambda x: SELECTED_LAYOUTS.get(x, x))
    years = sorted(plot["year"].unique())
    labels = [SELECTED_LAYOUTS.get(x, x) for x in selected_ids if x in set(plot["layout_id"])]

    fig, axes = plt.subplots(1, 3, figsize=(13.0, 3.9), dpi=220)
    ax = axes[0]
    for layout_id in selected_ids:
        if layout_id == "baseline_full":
            continue
        frame = plot[plot["layout_id"] == layout_id].sort_values("year")
        if frame.empty:
            continue
        ax.plot(
            frame["year"],
            frame["delta_annual_thermal_proxy_pct"],
            marker="o",
            linewidth=1.35,
            markersize=3.8,
            label=SELECTED_LAYOUTS.get(layout_id, layout_id),
        )
    ax.axhline(0.0, color="#111827", linewidth=0.8)
    ax.set_xticks(years)
    ax.set_ylabel("Annual proxy change vs L0 (%)")
    ax.set_title("(a) Weather-year robustness")
    ax.grid(True, axis="y", alpha=0.25)
    ax.legend(frameon=False, fontsize=7.0, ncol=2)

    ax = axes[1]
    selected_summary = summary[summary["layout_id"].isin([x for x in selected_ids if x != "baseline_full"])].copy()
    selected_summary = selected_summary.sort_values("mean_delta_annual_pct")
    y = np.arange(len(selected_summary))
    ax.barh(y, selected_summary["mean_delta_annual_pct"], color="#4C78A8", alpha=0.88)
    ax.errorbar(
        selected_summary["mean_delta_annual_pct"],
        y,
        xerr=[
            selected_summary["mean_delta_annual_pct"] - selected_summary["min_delta_annual_pct"],
            selected_summary["max_delta_annual_pct"] - selected_summary["mean_delta_annual_pct"],
        ],
        fmt="none",
        ecolor="#1F2937",
        elinewidth=0.75,
        capsize=2.0,
    )
    ax.axvline(0.0, color="#111827", linewidth=0.8)
    ax.set_yticks(y)
    ax.set_yticklabels(selected_summary["label"])
    ax.set_xlabel("Mean and min-max annual change (%)")
    ax.set_title("(b) Multi-year spread")
    ax.grid(True, axis="x", alpha=0.25)

    ax = axes[2]
    matrix = (
        plot.pivot_table(index="label", columns="year", values="annual_rank", aggfunc="first")
        .reindex(labels)
        .dropna(how="all")
    )
    im = ax.imshow(matrix.to_numpy(float), cmap="YlGnBu_r", aspect="auto")
    ax.set_xticks(np.arange(len(matrix.columns)))
    ax.set_xticklabels(matrix.columns.astype(str))
    ax.set_yticks(np.arange(len(matrix.index)))
    ax.set_yticklabels(matrix.index)
    ax.set_title("(c) Annual-proxy rank")
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            value = matrix.iloc[i, j]
            if pd.notna(value):
                ax.text(j, i, f"{int(value)}", ha="center", va="center", fontsize=7.0, color="#111827")
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
    cbar.set_label("Rank")

    fig.tight_layout(w_pad=1.8)
    fig.savefig(out / "figures/fig_multiyear_annual_proxy_gate.png", bbox_inches="tight")
    fig.savefig(out / "figures/fig_multiyear_annual_proxy_gate.pdf", bbox_inches="tight")
    plt.close(fig)


def markdown_table(df: pd.DataFrame) -> str:
    cols = [
        "label",
        "layout_id",
        "mean_delta_annual_pct",
        "min_delta_annual_pct",
        "max_delta_annual_pct",
        "sign_positive_fraction",
        "best_rank",
        "worst_rank",
    ]
    table = df.loc[:, cols].copy()
    table.columns = [
        "Role",
        "Layout",
        "Mean annual delta (%)",
        "Min annual delta (%)",
        "Max annual delta (%)",
        "Positive-year fraction",
        "Best rank",
        "Worst rank",
    ]
    return table.to_markdown(index=False, floatfmt=".3f")


def write_report(df: pd.DataFrame, summary: pd.DataFrame, gate: dict[str, object], selected_ids: list[str], out: Path) -> None:
    weather = df.groupby("year", as_index=False).agg(
        annual_dni_kwh_m2=("annual_dni_kwh_m2", "first"),
        positive_dni_hours=("positive_dni_hours", "first"),
    )
    selected_summary = summary[summary["layout_id"].isin([x for x in selected_ids if x != "baseline_full"])].copy()
    lines = [
        "# Multi-Year Annual-Proxy Robustness Gate",
        "",
        "## Scope",
        "",
        "This is a weather-year robustness audit for the fast annual proxy. It reuses the same",
        "SolarPILOT default-aiming optical-efficiency tables and reweights them over each available",
        "NASA POWER SAM weather year. It is not full annual custom-aimpoint validation.",
        "",
        "## Weather Years",
        "",
        weather.to_markdown(index=False, floatfmt=".2f"),
        "",
        "## Selected Roles",
        "",
        markdown_table(selected_summary),
        "",
        "## Gate Decision",
        "",
        f"- Recommendation: `{gate['writeback_recommendation']}`.",
        f"- Positive annual rows all positive: `{gate['positive_rows_all_years_positive']}`.",
        f"- L_opt remains top-three in all years: `{gate['lopt_remains_top3_all_years']}`.",
        f"- Receiver-pressure rows do not become annual headline rows: `{gate['receiver_pressure_rows_not_annual_headline']}`.",
        f"- Interpretation: {gate['interpretation']}",
        "",
        "## Boundary",
        "",
        "Do not cite this audit as bankable annual yield or annual custom-aimpoint verification.",
        "If written into the manuscript, it should be a short robustness sentence or a supplementary",
        "artifact describing weather-year sign/rank stability.",
    ]
    (out / "MULTIYEAR_ANNUAL_PROXY_GATE_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def copy_to_package(out: Path, package: Path, gate: dict[str, object]) -> None:
    sup = package / "supplementary_data" / "multiyear_annual_proxy_gate"
    if sup.exists():
        shutil.rmtree(sup)
    shutil.copytree(out, sup)
    code_dst = package / "code/scripts/build_multi_year_annual_proxy_gate.py"
    code_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(Path(__file__), code_dst)
    if gate["writeback_recommendation"] != "do_not_write_main_text":
        fig_src = out / "figures/fig_multiyear_annual_proxy_gate.png"
        fig_dst = package / "latex/figures/fig_multiyear_annual_proxy_gate.png"
        fig_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(fig_src, fig_dst)


def main() -> int:
    args = parse_args()
    out = resolve(args.out)
    package = resolve(args.package)
    tables = resolve(args.solarpilot_tables)
    (out / "tables").mkdir(parents=True, exist_ok=True)
    (out / "figures").mkdir(parents=True, exist_ok=True)
    weather_paths = [Path(path).resolve() for path in sorted(glob.glob(args.weather_glob))]
    if not weather_paths:
        raise FileNotFoundError(f"No weather files matched {args.weather_glob}")

    frames = [
        annual_proxy_for_weather(path, tables, args.heliostat_count, args.mirror_area_m2)
        for path in weather_paths
    ]
    all_df = pd.concat(frames, ignore_index=True)
    summary = summarize(all_df)
    selected_ids = [part.strip() for part in args.selected_layouts.split(",") if part.strip()]
    gate = gate_decision(summary, selected_ids)

    all_df.to_csv(out / "tables/multiyear_annual_proxy_all.csv", index=False)
    summary.to_csv(out / "tables/multiyear_annual_proxy_summary.csv", index=False)
    (out / "gate_decision.json").write_text(json.dumps(gate, indent=2), encoding="utf-8")
    (out / "run_config.json").write_text(
        json.dumps(
            {
                "weather_files": [str(path) for path in weather_paths],
                "solarpilot_tables": str(tables),
                "selected_layouts": selected_ids,
                "claim_boundary": "multi-year weather robustness for default-aiming annual proxy only",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    write_figure(all_df, summary, selected_ids, out)
    write_report(all_df, summary, gate, selected_ids, out)
    copy_to_package(out, package, gate)
    print(f"Wrote multi-year annual proxy gate to {out}")
    print(f"Recommendation: {gate['writeback_recommendation']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
