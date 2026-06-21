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
from scipy.interpolate import LinearNDInterpolator
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "paper_submission" / "solar_energy_elsarticle_v8_strict_review_rescue"
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from build_fast_annual_proxy_and_sanity import load_weather  # noqa: E402


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

ANNUAL_POSITIVE_IDS = {"deform_0276", "deform_0893", "deform_1387", "joint_g02_0333", "sb_hy_energy"}
RECEIVER_PRESSURE_IDS = {"joint_g04_0478", "sb_pf_flux", "sb_hs_flux"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Check whether the fast annual proxy is stable to interpolation choices used to "
            "map discrete SolarPILOT optical-efficiency tables to hourly weather."
        )
    )
    parser.add_argument("--weather-glob", default=str(ROOT / "data/weather/dunhuang_nasa_power_*_sam.csv"))
    parser.add_argument(
        "--solarpilot-tables",
        type=Path,
        default=ROOT / "server_outputs/same_anchor_strong_baselines_20260523/solarpilot_strong_baseline/tables",
    )
    parser.add_argument("--out", type=Path, default=ROOT / "server_outputs/annual_interpolation_robustness_gate_20260524")
    parser.add_argument("--package", type=Path, default=PACKAGE)
    parser.add_argument("--mirror-area-m2", type=float, default=115.72)
    parser.add_argument("--heliostat-count", type=int, default=11915)
    parser.add_argument("--spread-threshold-pctpt", type=float, default=0.20)
    parser.add_argument(
        "--selected-layouts",
        default=",".join(SELECTED_LAYOUTS.keys()),
        help="Comma-separated layout ids shown in the manuscript-facing figure/report.",
    )
    return parser.parse_args()


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def infer_year(path: Path) -> int:
    for token in path.stem.split("_"):
        if token.isdigit() and len(token) == 4:
            return int(token)
    raise ValueError(f"Cannot infer year from {path}")


def interpolate_values(opteff: pd.DataFrame, weather: pd.DataFrame, method: str) -> np.ndarray:
    pts = opteff.loc[:, ["azimuth_deg", "zenith_deg"]].to_numpy(float)
    values = opteff["optical_efficiency"].to_numpy(float)
    query = weather.loc[:, ["solar_azimuth_deg", "solar_zenith_deg"]].to_numpy(float)
    daylight = weather["is_daylight"].to_numpy(bool)

    tree = cKDTree(pts)
    if method == "nearest":
        _, idx = tree.query(query, k=1)
        eta = values[idx]
    elif method.startswith("idw"):
        k = int(method.replace("idw", ""))
        k = max(1, min(k, len(values)))
        dist, idx = tree.query(query, k=k)
        if k == 1:
            dist = dist[:, None]
            idx = idx[:, None]
        weights = 1.0 / np.maximum(dist, 1e-6) ** 2
        eta = np.sum(weights * values[idx], axis=1) / np.sum(weights, axis=1)
    elif method == "linear_nearest":
        interp = LinearNDInterpolator(pts, values, rescale=True)
        eta = np.asarray(interp(query), dtype=float)
        missing = ~np.isfinite(eta)
        if np.any(missing):
            _, idx = tree.query(query[missing], k=1)
            eta[missing] = values[idx]
    else:
        raise ValueError(f"Unknown interpolation method: {method}")

    eta = np.asarray(eta, dtype=float)
    eta[~daylight] = 0.0
    return eta


def annual_proxy_for_weather_method(
    weather_path: Path,
    solarpilot_tables: Path,
    method: str,
    heliostat_count: int,
    mirror_area_m2: float,
) -> pd.DataFrame:
    weather = load_weather(weather_path)
    aperture_area_m2 = float(heliostat_count) * float(mirror_area_m2)
    dni = weather["DNI"].to_numpy(float)
    daylight = weather["is_daylight"].to_numpy(bool)
    weights = np.where(daylight, dni, 0.0)
    records: list[dict[str, float | str | int]] = []
    for opteff_path in sorted(solarpilot_tables.glob("opteff_*.csv")):
        layout_id = opteff_path.stem.replace("opteff_", "")
        opteff = pd.read_csv(opteff_path)
        eta = interpolate_values(opteff, weather, method)
        thermal_mwh = dni * aperture_area_m2 * eta / 1_000_000.0
        records.append(
            {
                "year": infer_year(weather_path),
                "weather_file": str(weather_path),
                "interpolation_method": method,
                "layout_id": layout_id,
                "annual_dni_kwh_m2": float(dni.sum() / 1000.0),
                "positive_dni_hours": int(daylight.sum()),
                "annual_dni_weighted_eta": float(np.sum(eta * weights) / max(np.sum(weights), 1e-12)),
                "annual_thermal_proxy_mwh": float(np.sum(thermal_mwh)),
                "opteff_table_mean": float(opteff["optical_efficiency"].mean()),
            }
        )
    df = pd.DataFrame.from_records(records)
    base = df[df["layout_id"] == "baseline_full"].loc[
        :, ["year", "interpolation_method", "annual_thermal_proxy_mwh", "annual_dni_weighted_eta"]
    ]
    base = base.rename(
        columns={
            "annual_thermal_proxy_mwh": "baseline_annual_thermal_proxy_mwh",
            "annual_dni_weighted_eta": "baseline_annual_dni_weighted_eta",
        }
    )
    df = df.merge(base, on=["year", "interpolation_method"], how="left")
    df["delta_annual_thermal_proxy_pct"] = 100.0 * (
        df["annual_thermal_proxy_mwh"] / df["baseline_annual_thermal_proxy_mwh"] - 1.0
    )
    df["delta_annual_dni_weighted_eta_pct"] = 100.0 * (
        df["annual_dni_weighted_eta"] / df["baseline_annual_dni_weighted_eta"] - 1.0
    )
    df["annual_rank"] = df.groupby(["year", "interpolation_method"])["annual_thermal_proxy_mwh"].rank(
        method="min", ascending=False
    )
    return df


def summarize(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    nonbase = df[df["layout_id"] != "baseline_full"].copy()
    summary = (
        nonbase.groupby("layout_id", as_index=False)
        .agg(
            cases=("delta_annual_thermal_proxy_pct", "count"),
            mean_delta_annual_pct=("delta_annual_thermal_proxy_pct", "mean"),
            min_delta_annual_pct=("delta_annual_thermal_proxy_pct", "min"),
            max_delta_annual_pct=("delta_annual_thermal_proxy_pct", "max"),
            std_delta_annual_pct=("delta_annual_thermal_proxy_pct", "std"),
            sign_positive_fraction=("delta_annual_thermal_proxy_pct", lambda x: float((x > 0.0).mean())),
            best_rank=("annual_rank", "min"),
            median_rank=("annual_rank", "median"),
            worst_rank=("annual_rank", "max"),
        )
        .sort_values("mean_delta_annual_pct", ascending=False)
    )
    summary["method_year_delta_spread_pctpt"] = summary["max_delta_annual_pct"] - summary["min_delta_annual_pct"]
    summary["label"] = summary["layout_id"].map(lambda x: SELECTED_LAYOUTS.get(x, x))

    method_means = (
        nonbase.groupby(["layout_id", "interpolation_method"], as_index=False)
        .agg(mean_delta_annual_pct=("delta_annual_thermal_proxy_pct", "mean"), median_rank=("annual_rank", "median"))
        .sort_values(["layout_id", "interpolation_method"])
    )
    return summary, method_means


def gate_decision(summary: pd.DataFrame, selected_ids: list[str], threshold: float) -> dict[str, object]:
    selected = summary[summary["layout_id"].isin([x for x in selected_ids if x != "baseline_full"])].copy()
    annual_positive = selected[selected["layout_id"].isin(ANNUAL_POSITIVE_IDS)]
    pressure = selected[selected["layout_id"].isin(RECEIVER_PRESSURE_IDS)]
    positive_stable = bool((not annual_positive.empty) and (annual_positive["sign_positive_fraction"] >= 1.0).all())
    pressure_not_headline = bool((not pressure.empty) and (pressure["mean_delta_annual_pct"] <= 0.5).all())
    lopt = summary[summary["layout_id"] == "deform_0276"]
    lopt_top3 = bool((not lopt.empty) and float(lopt.iloc[0]["worst_rank"]) <= 3.0)
    selected_spread = selected[selected["layout_id"].isin(ANNUAL_POSITIVE_IDS.union(RECEIVER_PRESSURE_IDS))]
    max_spread = float(selected_spread["method_year_delta_spread_pctpt"].max()) if not selected_spread.empty else float("inf")
    spread_ok = bool(max_spread <= threshold)
    passes = positive_stable and pressure_not_headline and lopt_top3 and spread_ok
    return {
        "writeback_recommendation": "write_short_interpolation_robustness_sentence" if passes else "do_not_write_main_text",
        "positive_rows_all_methods_years_positive": positive_stable,
        "receiver_pressure_rows_not_annual_headline": pressure_not_headline,
        "lopt_remains_top3_all_methods_years": lopt_top3,
        "max_selected_delta_spread_pctpt": max_spread,
        "spread_threshold_pctpt": threshold,
        "spread_within_threshold": spread_ok,
        "interpretation": (
            "Annual-proxy signs and role ranks are stable across tested interpolation methods and weather years."
            if passes
            else "Annual-proxy interpolation sensitivity is too large for an additional main-text robustness claim."
        ),
    }


def markdown_table(df: pd.DataFrame) -> str:
    cols = [
        "label",
        "layout_id",
        "mean_delta_annual_pct",
        "min_delta_annual_pct",
        "max_delta_annual_pct",
        "method_year_delta_spread_pctpt",
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
        "Spread (pct-pt)",
        "Positive fraction",
        "Best rank",
        "Worst rank",
    ]
    return table.to_markdown(index=False, floatfmt=".3f")


def write_figure(df: pd.DataFrame, summary: pd.DataFrame, method_means: pd.DataFrame, selected_ids: list[str], out: Path) -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
            "font.size": 8.3,
            "axes.titlesize": 9.2,
            "axes.labelsize": 8.3,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )
    plot_ids = [x for x in selected_ids if x != "baseline_full"]
    selected = summary[summary["layout_id"].isin(plot_ids)].copy()
    selected = selected.sort_values("mean_delta_annual_pct")
    fig, axes = plt.subplots(1, 3, figsize=(13.2, 3.95), dpi=220)

    ax = axes[0]
    y = np.arange(len(selected))
    ax.barh(y, selected["mean_delta_annual_pct"], color="#4C78A8", alpha=0.88)
    ax.errorbar(
        selected["mean_delta_annual_pct"],
        y,
        xerr=[
            selected["mean_delta_annual_pct"] - selected["min_delta_annual_pct"],
            selected["max_delta_annual_pct"] - selected["mean_delta_annual_pct"],
        ],
        fmt="none",
        ecolor="#1F2937",
        elinewidth=0.75,
        capsize=2.0,
    )
    ax.axvline(0, color="#111827", linewidth=0.85)
    ax.set_yticks(y)
    ax.set_yticklabels(selected["label"])
    ax.set_xlabel("Annual proxy change vs L0 (%)")
    ax.set_title("(a) Method-year envelope")
    ax.grid(True, axis="x", alpha=0.24)

    ax = axes[1]
    heat = method_means[method_means["layout_id"].isin(plot_ids)].copy()
    heat["label"] = heat["layout_id"].map(lambda x: SELECTED_LAYOUTS.get(x, x))
    labels = [SELECTED_LAYOUTS.get(x, x) for x in plot_ids if x in set(heat["layout_id"])]
    methods = ["nearest", "idw3", "idw6", "idw12", "linear_nearest"]
    matrix = (
        heat.pivot_table(index="label", columns="interpolation_method", values="mean_delta_annual_pct", aggfunc="first")
        .reindex(labels)
        .reindex(columns=methods)
    )
    im = ax.imshow(matrix.to_numpy(float), cmap="RdBu_r", aspect="auto", vmin=-4, vmax=4)
    ax.set_xticks(np.arange(len(matrix.columns)))
    ax.set_xticklabels([m.replace("_", "\n") for m in matrix.columns], fontsize=7)
    ax.set_yticks(np.arange(len(matrix.index)))
    ax.set_yticklabels(matrix.index)
    ax.set_title("(b) Interpolation-method means")
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            value = matrix.iloc[i, j]
            if pd.notna(value):
                ax.text(j, i, f"{value:+.2f}", ha="center", va="center", fontsize=6.4, color="#111827")
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
    cbar.set_label("Delta (%)")

    ax = axes[2]
    selected_sorted = selected.sort_values("method_year_delta_spread_pctpt", ascending=True)
    y = np.arange(len(selected_sorted))
    colors = np.where(selected_sorted["method_year_delta_spread_pctpt"] <= 0.20, "#72B7B2", "#E45756")
    ax.barh(y, selected_sorted["method_year_delta_spread_pctpt"], color=colors, alpha=0.92)
    ax.axvline(0.20, color="#111827", linewidth=0.85, linestyle="--")
    ax.set_yticks(y)
    ax.set_yticklabels(selected_sorted["label"])
    ax.set_xlabel("Delta spread across methods and years (pct-pt)")
    ax.set_title("(c) Interpolation sensitivity")
    ax.grid(True, axis="x", alpha=0.24)

    fig.tight_layout(w_pad=1.8)
    fig.savefig(out / "figures/fig_annual_interpolation_robustness_gate.png", bbox_inches="tight")
    fig.savefig(out / "figures/fig_annual_interpolation_robustness_gate.pdf", bbox_inches="tight")
    plt.close(fig)


def write_report(
    df: pd.DataFrame,
    summary: pd.DataFrame,
    method_means: pd.DataFrame,
    gate: dict[str, object],
    selected_ids: list[str],
    out: Path,
) -> None:
    weather = df.groupby("year", as_index=False).agg(
        annual_dni_kwh_m2=("annual_dni_kwh_m2", "first"),
        positive_dni_hours=("positive_dni_hours", "first"),
    )
    selected = summary[summary["layout_id"].isin([x for x in selected_ids if x != "baseline_full"])].copy()
    methods = ", ".join(sorted(df["interpolation_method"].unique()))
    lines = [
        "# Annual-Proxy Interpolation Robustness Gate",
        "",
        "## Scope",
        "",
        "This audit checks whether the fast annual proxy depends on a single interpolation",
        "choice when discrete SolarPILOT default-aiming optical-efficiency tables are mapped",
        "to hourly public weather files. It is not annual custom-aimpoint validation.",
        "",
        f"Tested interpolation methods: `{methods}`.",
        "",
        "## Weather Years",
        "",
        weather.to_markdown(index=False, floatfmt=".2f"),
        "",
        "## Selected Roles",
        "",
        markdown_table(selected),
        "",
        "## Method Means",
        "",
        method_means[method_means["layout_id"].isin([x for x in selected_ids if x != "baseline_full"])]
        .assign(label=lambda x: x["layout_id"].map(lambda y: SELECTED_LAYOUTS.get(y, y)))
        .loc[:, ["label", "layout_id", "interpolation_method", "mean_delta_annual_pct", "median_rank"]]
        .rename(
            columns={
                "label": "Role",
                "layout_id": "Layout",
                "interpolation_method": "Method",
                "mean_delta_annual_pct": "Mean annual delta (%)",
                "median_rank": "Median rank",
            }
        )
        .to_markdown(index=False, floatfmt=".3f"),
        "",
        "## Gate Decision",
        "",
        f"- Recommendation: `{gate['writeback_recommendation']}`.",
        f"- Positive annual rows positive across all tested method-year pairs: `{gate['positive_rows_all_methods_years_positive']}`.",
        f"- L_opt remains top-three across all tested method-year pairs: `{gate['lopt_remains_top3_all_methods_years']}`.",
        f"- Receiver-pressure rows do not become annual headline rows: `{gate['receiver_pressure_rows_not_annual_headline']}`.",
        f"- Max selected delta spread: {float(gate['max_selected_delta_spread_pctpt']):.3f} pct-pt; threshold: {float(gate['spread_threshold_pctpt']):.3f} pct-pt.",
        f"- Interpretation: {gate['interpretation']}",
        "",
        "## Boundary",
        "",
        "If written into the manuscript, this audit should be a short interpolation-robustness",
        "statement for the annual proxy. It must not be cited as measured annual operation,",
        "bankable generation, dispatch simulation, or full-field annual custom aiming.",
    ]
    (out / "ANNUAL_INTERPOLATION_ROBUSTNESS_GATE_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def copy_to_package(out: Path, package: Path, gate: dict[str, object]) -> None:
    sup = package / "supplementary_data" / "annual_interpolation_robustness_gate"
    if sup.exists():
        shutil.rmtree(sup)
    shutil.copytree(out, sup)
    code_dst = package / "code/scripts/build_annual_interpolation_robustness_gate.py"
    code_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(Path(__file__), code_dst)
    if gate["writeback_recommendation"] != "do_not_write_main_text":
        fig_src = out / "figures/fig_annual_interpolation_robustness_gate.png"
        fig_dst = package / "latex/figures/fig_annual_interpolation_robustness_gate.png"
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

    methods = ["nearest", "idw3", "idw6", "idw12", "linear_nearest"]
    frames = []
    for weather_path in weather_paths:
        for method in methods:
            frames.append(
                annual_proxy_for_weather_method(
                    weather_path, tables, method, args.heliostat_count, args.mirror_area_m2
                )
            )
    all_df = pd.concat(frames, ignore_index=True)
    summary, method_means = summarize(all_df)
    selected_ids = [part.strip() for part in args.selected_layouts.split(",") if part.strip()]
    gate = gate_decision(summary, selected_ids, args.spread_threshold_pctpt)

    all_df.to_csv(out / "tables/annual_interpolation_robustness_all.csv", index=False)
    summary.to_csv(out / "tables/annual_interpolation_robustness_summary.csv", index=False)
    method_means.to_csv(out / "tables/annual_interpolation_method_means.csv", index=False)
    (out / "gate_decision.json").write_text(json.dumps(gate, indent=2), encoding="utf-8")
    (out / "run_config.json").write_text(
        json.dumps(
            {
                "weather_files": [str(path) for path in weather_paths],
                "solarpilot_tables": str(tables),
                "interpolation_methods": methods,
                "selected_layouts": selected_ids,
                "spread_threshold_pctpt": args.spread_threshold_pctpt,
                "claim_boundary": "interpolation robustness for default-aiming annual proxy only",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    write_figure(all_df, summary, method_means, selected_ids, out)
    write_report(all_df, summary, method_means, gate, selected_ids, out)
    copy_to_package(out, package, gate)
    print(f"Wrote annual interpolation robustness gate to {out}")
    print(f"Recommendation: {gate['writeback_recommendation']}")
    print(f"Max selected delta spread pct-pt: {float(gate['max_selected_delta_spread_pctpt']):.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
