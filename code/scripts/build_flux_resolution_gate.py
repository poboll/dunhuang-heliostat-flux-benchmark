#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "paper_submission" / "solar_energy_elsarticle_v8_strict_review_rescue"


SELECTED = {
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
            "Compare SolarPILOT default-flux rankings across receiver flux-bin resolutions "
            "and decide whether a high-resolution rerun should be written into the manuscript."
        )
    )
    parser.add_argument("--baseline-run", type=Path, default=ROOT / "server_outputs/same_anchor_strong_baselines_20260523/solarpilot_strong_baseline")
    parser.add_argument("--highres-run", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=ROOT / "server_outputs/flux_resolution_gate_20260524")
    parser.add_argument("--package", type=Path, default=PACKAGE)
    parser.add_argument("--selected-layouts", default=",".join(SELECTED.keys()))
    return parser.parse_args()


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def active_values(flat: np.ndarray) -> np.ndarray:
    threshold = float(np.percentile(flat, 55.0))
    active = flat[flat > threshold]
    return active if active.size else flat


def load_flux_table(path: Path) -> np.ndarray:
    raw = pd.read_csv(path, header=None).to_numpy(float)
    bins = raw.shape[1]
    if bins <= 0 or raw.shape[0] % bins != 0:
        raise ValueError(f"Malformed flux table: {path}")
    return raw.reshape(raw.shape[0] // bins, bins, bins)


def flux_metrics(run: Path, tag: str) -> pd.DataFrame:
    tables = run / "tables"
    summary = pd.read_csv(tables / "solarpilot_summary.csv")
    records: list[dict[str, float | str | int]] = []
    for path in sorted(tables.glob("flux_table_*.csv")):
        layout_id = path.stem.replace("flux_table_", "")
        cube = load_flux_table(path)
        flat = cube.reshape(-1)
        active = active_values(flat)
        records.append(
            {
                "resolution_tag": tag,
                "layout_id": layout_id,
                "flux_bins": int(cube.shape[1]),
                "flux_map_count": int(cube.shape[0]),
                "active_mean": float(active.mean()),
                "active_p95": float(np.percentile(active, 95.0)),
                "active_p99": float(np.percentile(active, 99.0)),
                "active_peak": float(active.max()),
                "p95_to_active_mean": float(np.percentile(active, 95.0) / max(active.mean(), 1e-12)),
                "p99_to_active_mean": float(np.percentile(active, 99.0) / max(active.mean(), 1e-12)),
                "peak_to_active_mean": float(active.max() / max(active.mean(), 1e-12)),
                "active_cv": float(active.std() / max(active.mean(), 1e-12)),
            }
        )
    df = pd.DataFrame.from_records(records)
    if df.empty:
        raise FileNotFoundError(f"No flux_table_*.csv in {tables}")
    df = df.merge(summary.loc[:, ["layout_id", "opteff_mean", "flux_peak_to_active_mean"]], on="layout_id", how="left")

    base = df[df["layout_id"] == "baseline_full"].iloc[0]
    for col in ["opteff_mean", "peak_to_active_mean", "p95_to_active_mean", "p99_to_active_mean", "active_cv"]:
        df[f"delta_{col}_pct"] = 100.0 * (df[col].astype(float) / float(base[col]) - 1.0)
    df["label"] = df["layout_id"].map(lambda x: SELECTED.get(x, x))
    return df


def summarize(combined: pd.DataFrame, selected_ids: list[str]) -> tuple[pd.DataFrame, dict[str, object]]:
    selected = combined[combined["layout_id"].isin(selected_ids)].copy()
    pivot = selected.pivot_table(
        index=["layout_id", "label"],
        columns="resolution_tag",
        values=["delta_peak_to_active_mean_pct", "delta_p99_to_active_mean_pct", "delta_opteff_mean_pct"],
        aggfunc="first",
    )
    pivot.columns = [f"{a}_{b}" for a, b in pivot.columns]
    pivot = pivot.reset_index()
    for metric in ["delta_peak_to_active_mean_pct", "delta_p99_to_active_mean_pct", "delta_opteff_mean_pct"]:
        low = f"{metric}_baseline"
        high = f"{metric}_highres"
        if low in pivot.columns and high in pivot.columns:
            pivot[f"{metric}_shift_highres_minus_baseline"] = pivot[high] - pivot[low]

    nonbase = pivot[pivot["layout_id"] != "baseline_full"].copy()
    max_peak_shift = float(nonbase["delta_peak_to_active_mean_pct_shift_highres_minus_baseline"].abs().max())
    max_p99_shift = float(nonbase["delta_p99_to_active_mean_pct_shift_highres_minus_baseline"].abs().max())

    stress = pivot[pivot["layout_id"] == "deform_0276"]
    lopt_still_flux_penalty = bool(
        (not stress.empty)
        and float(stress.iloc[0]["delta_peak_to_active_mean_pct_highres"]) > 0.0
        and float(stress.iloc[0]["delta_p99_to_active_mean_pct_highres"]) > 0.0
    )
    receiver_rows = pivot[pivot["layout_id"].isin(["joint_g04_0478", "sb_pf_flux", "sb_hs_flux"])]
    receiver_rows_not_annual_headline = bool(
        (not receiver_rows.empty)
        and (receiver_rows["delta_opteff_mean_pct_highres"].astype(float) <= 0.5).all()
    )
    stable_enough = max_peak_shift <= 1.75 and max_p99_shift <= 1.75 and lopt_still_flux_penalty

    gate = {
        "writeback_recommendation": "write_short_resolution_robustness_sentence" if stable_enough else "do_not_write_main_text",
        "max_abs_peak_ratio_delta_shift_pctpt": max_peak_shift,
        "max_abs_p99_ratio_delta_shift_pctpt": max_p99_shift,
        "lopt_still_flux_penalty": lopt_still_flux_penalty,
        "receiver_rows_not_annual_headline": receiver_rows_not_annual_headline,
        "interpretation": (
            "High-resolution flux maps preserve the manuscript's default-flux role interpretation."
            if stable_enough
            else "High-resolution flux maps shift at least one key default-flux role too much for main-text writeback."
        ),
    }
    return pivot, gate


def write_figure(combined: pd.DataFrame, pivot: pd.DataFrame, selected_ids: list[str], out: Path) -> None:
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
    plot = combined[combined["layout_id"].isin(selected_ids)].copy()
    order = [x for x in selected_ids if x in set(plot["layout_id"])]
    labels = [SELECTED.get(x, x) for x in order if x != "baseline_full"]

    fig, axes = plt.subplots(1, 3, figsize=(13.0, 3.85), dpi=220)
    ax = axes[0]
    width = 0.34
    x = np.arange(len(labels))
    for offset, tag, color in [(-width / 2, "baseline", "#4C78A8"), (width / 2, "highres", "#F58518")]:
        rows = []
        for layout_id in [xid for xid in order if xid != "baseline_full"]:
            match = plot[(plot["layout_id"] == layout_id) & (plot["resolution_tag"] == tag)]
            rows.append(float(match.iloc[0]["delta_peak_to_active_mean_pct"]) if not match.empty else np.nan)
        ax.bar(x + offset, rows, width=width, color=color, label=tag)
    ax.axhline(0.0, color="#111827", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=32, ha="right")
    ax.set_ylabel("Delta peak/active mean (%)")
    ax.set_title("(a) Peak-ratio resolution check")
    ax.legend(frameon=False)
    ax.grid(True, axis="y", alpha=0.25)

    ax = axes[1]
    for offset, tag, color in [(-width / 2, "baseline", "#4C78A8"), (width / 2, "highres", "#F58518")]:
        rows = []
        for layout_id in [xid for xid in order if xid != "baseline_full"]:
            match = plot[(plot["layout_id"] == layout_id) & (plot["resolution_tag"] == tag)]
            rows.append(float(match.iloc[0]["delta_p99_to_active_mean_pct"]) if not match.empty else np.nan)
        ax.bar(x + offset, rows, width=width, color=color, label=tag)
    ax.axhline(0.0, color="#111827", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=32, ha="right")
    ax.set_ylabel("Delta p99/active mean (%)")
    ax.set_title("(b) High-percentile resolution check")
    ax.grid(True, axis="y", alpha=0.25)

    ax = axes[2]
    shifts = pivot[pivot["layout_id"].isin([xid for xid in order if xid != "baseline_full"])].copy()
    y = np.arange(len(shifts))
    ax.barh(y - 0.16, shifts["delta_peak_to_active_mean_pct_shift_highres_minus_baseline"], height=0.3, color="#4C78A8", label="peak ratio shift")
    ax.barh(y + 0.16, shifts["delta_p99_to_active_mean_pct_shift_highres_minus_baseline"], height=0.3, color="#F58518", label="p99 ratio shift")
    ax.axvline(0.0, color="#111827", linewidth=0.8)
    ax.set_yticks(y)
    ax.set_yticklabels(shifts["label"])
    ax.set_xlabel("Highres minus baseline delta (pct-pt)")
    ax.set_title("(c) Resolution-induced shift")
    ax.legend(frameon=False, fontsize=7.0)
    ax.grid(True, axis="x", alpha=0.25)

    fig.tight_layout(w_pad=1.7)
    fig.savefig(out / "figures/fig_flux_resolution_gate.png", bbox_inches="tight")
    fig.savefig(out / "figures/fig_flux_resolution_gate.pdf", bbox_inches="tight")
    plt.close(fig)


def markdown_table(df: pd.DataFrame) -> str:
    cols = [
        "label",
        "layout_id",
        "delta_peak_to_active_mean_pct_baseline",
        "delta_peak_to_active_mean_pct_highres",
        "delta_peak_to_active_mean_pct_shift_highres_minus_baseline",
        "delta_p99_to_active_mean_pct_baseline",
        "delta_p99_to_active_mean_pct_highres",
        "delta_p99_to_active_mean_pct_shift_highres_minus_baseline",
    ]
    table = df.loc[:, cols].copy()
    table.columns = [
        "Role",
        "Layout",
        "Peak delta baseline (%)",
        "Peak delta highres (%)",
        "Peak shift (pct-pt)",
        "P99 delta baseline (%)",
        "P99 delta highres (%)",
        "P99 shift (pct-pt)",
    ]
    return table.to_markdown(index=False, floatfmt=".3f")


def write_report(pivot: pd.DataFrame, gate: dict[str, object], out: Path) -> None:
    lines = [
        "# SolarPILOT Flux-Resolution Robustness Gate",
        "",
        "## Scope",
        "",
        "This audit compares the existing 24 x 24 SolarPILOT default-flux tables with a higher-resolution",
        "rerun. It checks whether receiver-flux role labels are artifacts of the receiver-bin discretization.",
        "It remains a default-aiming SolarPILOT audit, not custom-aimpoint or thermal certification.",
        "",
        "## Selected Roles",
        "",
        markdown_table(pivot[pivot["layout_id"] != "baseline_full"]),
        "",
        "## Gate Decision",
        "",
        f"- Recommendation: `{gate['writeback_recommendation']}`.",
        f"- Max absolute peak-ratio delta shift: {float(gate['max_abs_peak_ratio_delta_shift_pctpt']):.3f} pct-pt.",
        f"- Max absolute p99-ratio delta shift: {float(gate['max_abs_p99_ratio_delta_shift_pctpt']):.3f} pct-pt.",
        f"- L_opt still has a high-resolution flux penalty: `{gate['lopt_still_flux_penalty']}`.",
        f"- Receiver-pressure rows are not annual headline rows: `{gate['receiver_rows_not_annual_headline']}`.",
        f"- Interpretation: {gate['interpretation']}",
        "",
        "## Boundary",
        "",
        "Write this into the manuscript only as a short discretization-robustness sentence if the gate passes.",
        "Do not cite it as receiver thermal safety or same-aimpoint cross-code validation.",
    ]
    (out / "FLUX_RESOLUTION_GATE_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def copy_to_package(out: Path, package: Path, gate: dict[str, object]) -> None:
    sup = package / "supplementary_data" / "flux_resolution_gate"
    if sup.exists():
        shutil.rmtree(sup)
    shutil.copytree(out, sup)
    code_dst = package / "code/scripts/build_flux_resolution_gate.py"
    code_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(Path(__file__), code_dst)
    if gate["writeback_recommendation"] != "do_not_write_main_text":
        fig_src = out / "figures/fig_flux_resolution_gate.png"
        fig_dst = package / "latex/figures/fig_flux_resolution_gate.png"
        fig_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(fig_src, fig_dst)


def main() -> int:
    args = parse_args()
    out = resolve(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "tables").mkdir(exist_ok=True)
    (out / "figures").mkdir(exist_ok=True)
    baseline_run = resolve(args.baseline_run)
    highres_run = resolve(args.highres_run)
    selected_ids = [part.strip() for part in args.selected_layouts.split(",") if part.strip()]

    baseline = flux_metrics(baseline_run, "baseline")
    highres = flux_metrics(highres_run, "highres")
    combined = pd.concat([baseline, highres], ignore_index=True)
    pivot, gate = summarize(combined, selected_ids)

    combined.to_csv(out / "tables/flux_resolution_metrics_all.csv", index=False)
    pivot.to_csv(out / "tables/flux_resolution_selected_comparison.csv", index=False)
    (out / "gate_decision.json").write_text(json.dumps(gate, indent=2), encoding="utf-8")
    (out / "run_config.json").write_text(
        json.dumps(
            {
                "baseline_run": str(baseline_run),
                "highres_run": str(highres_run),
                "selected_layouts": selected_ids,
                "claim_boundary": "SolarPILOT default-flux discretization robustness only",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    write_figure(combined, pivot, selected_ids, out)
    write_report(pivot, gate, out)
    copy_to_package(out, resolve(args.package), gate)
    print(f"Wrote flux-resolution gate to {out}")
    print(f"Recommendation: {gate['writeback_recommendation']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
