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
            "Compare SolarPILOT default-flux role labels between the original 8-flux-day "
            "sampling and an enlarged flux-day rerun. The gate is intentionally conservative: "
            "it only supports a short sampling-robustness sentence if the role interpretation is stable."
        )
    )
    parser.add_argument(
        "--baseline-run",
        type=Path,
        default=ROOT / "server_outputs/same_anchor_strong_baselines_20260523/solarpilot_strong_baseline",
    )
    parser.add_argument(
        "--extended-run",
        type=Path,
        required=True,
        help="SolarPILOT run with enlarged flux-day sampling, e.g. 12 flux days.",
    )
    parser.add_argument("--out", type=Path, default=ROOT / "server_outputs/flux_day_sampling_gate_20260524")
    parser.add_argument("--package", type=Path, default=PACKAGE)
    parser.add_argument("--selected-layouts", default=",".join(SELECTED.keys()))
    parser.add_argument("--shift-threshold-pctpt", type=float, default=1.50)
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


def load_summary_mean(run: Path, layout_id: str) -> float | None:
    summary_path = run / "tables/solarpilot_summary.csv"
    if not summary_path.exists():
        return None
    summary = pd.read_csv(summary_path)
    match = summary[summary["layout_id"] == layout_id]
    if match.empty or "opteff_mean" not in match:
        return None
    return float(match.iloc[0]["opteff_mean"])


def opteff_mean(run: Path, layout_id: str) -> float:
    from_summary = load_summary_mean(run, layout_id)
    if from_summary is not None:
        return from_summary
    opteff_path = run / "tables" / f"opteff_{layout_id}.csv"
    opteff = pd.read_csv(opteff_path)
    return float(opteff["optical_efficiency"].mean())


def flux_metrics(run: Path, tag: str, selected_ids: list[str]) -> pd.DataFrame:
    tables = run / "tables"
    records: list[dict[str, float | str | int]] = []
    missing: list[str] = []
    for layout_id in selected_ids:
        path = tables / f"flux_table_{layout_id}.csv"
        if not path.exists():
            missing.append(layout_id)
            continue
        cube = load_flux_table(path)
        flat = cube.reshape(-1)
        active = active_values(flat)
        records.append(
            {
                "sampling_tag": tag,
                "layout_id": layout_id,
                "label": SELECTED.get(layout_id, layout_id),
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
                "opteff_mean": opteff_mean(run, layout_id),
            }
        )
    if missing:
        raise FileNotFoundError(f"Missing flux tables in {run}: {', '.join(missing)}")
    df = pd.DataFrame.from_records(records)
    if df.empty:
        raise FileNotFoundError(f"No selected flux tables found in {tables}")
    base = df[df["layout_id"] == "baseline_full"].iloc[0]
    for col in ["opteff_mean", "peak_to_active_mean", "p95_to_active_mean", "p99_to_active_mean", "active_cv"]:
        df[f"delta_{col}_pct"] = 100.0 * (df[col].astype(float) / float(base[col]) - 1.0)
    return df


def summarize(combined: pd.DataFrame, threshold: float) -> tuple[pd.DataFrame, dict[str, object]]:
    pivot = combined.pivot_table(
        index=["layout_id", "label"],
        columns="sampling_tag",
        values=[
            "flux_map_count",
            "delta_peak_to_active_mean_pct",
            "delta_p99_to_active_mean_pct",
            "delta_opteff_mean_pct",
        ],
        aggfunc="first",
    )
    pivot.columns = [f"{a}_{b}" for a, b in pivot.columns]
    pivot = pivot.reset_index()

    for metric in ["delta_peak_to_active_mean_pct", "delta_p99_to_active_mean_pct", "delta_opteff_mean_pct"]:
        low = f"{metric}_baseline8"
        high = f"{metric}_extended"
        if low in pivot.columns and high in pivot.columns:
            pivot[f"{metric}_shift_extended_minus_baseline8"] = pivot[high] - pivot[low]

    nonbase = pivot[pivot["layout_id"] != "baseline_full"].copy()
    peak_shift = "delta_peak_to_active_mean_pct_shift_extended_minus_baseline8"
    p99_shift = "delta_p99_to_active_mean_pct_shift_extended_minus_baseline8"
    max_peak_shift = float(nonbase[peak_shift].abs().max())
    max_p99_shift = float(nonbase[p99_shift].abs().max())

    lopt = pivot[pivot["layout_id"] == "deform_0276"]
    lopt_still_flux_penalty = bool(
        (not lopt.empty)
        and float(lopt.iloc[0]["delta_peak_to_active_mean_pct_extended"]) > 0.0
        and float(lopt.iloc[0]["delta_p99_to_active_mean_pct_extended"]) > 0.0
    )
    receiver_rows = pivot[pivot["layout_id"].isin(["joint_g04_0478", "sb_pf_flux", "sb_hs_flux"])]
    receiver_rows_not_optical_headline = bool(
        (not receiver_rows.empty)
        and (receiver_rows["delta_opteff_mean_pct_extended"].astype(float) <= 0.5).all()
    )
    shifts_ok = bool(max_peak_shift <= threshold and max_p99_shift <= threshold)
    passes = shifts_ok and lopt_still_flux_penalty and receiver_rows_not_optical_headline
    gate = {
        "writeback_recommendation": "write_short_flux_day_sampling_sentence" if passes else "do_not_write_main_text",
        "max_abs_peak_ratio_delta_shift_pctpt": max_peak_shift,
        "max_abs_p99_ratio_delta_shift_pctpt": max_p99_shift,
        "shift_threshold_pctpt": threshold,
        "lopt_still_flux_penalty": lopt_still_flux_penalty,
        "receiver_rows_not_optical_headline": receiver_rows_not_optical_headline,
        "interpretation": (
            "The enlarged SolarPILOT flux-day sample preserves the manuscript's default-flux role interpretation."
            if passes
            else "The enlarged SolarPILOT flux-day sample shifts at least one role enough that it should not be used as a main-text robustness claim."
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
    order = [layout_id for layout_id in selected_ids if layout_id in set(plot["layout_id"]) and layout_id != "baseline_full"]
    labels = [SELECTED.get(layout_id, layout_id) for layout_id in order]
    x = np.arange(len(order))
    width = 0.34
    fig, axes = plt.subplots(1, 3, figsize=(13.0, 3.85), dpi=220)

    for ax, metric, title, ylabel in [
        (axes[0], "delta_peak_to_active_mean_pct", "(a) Peak-ratio sampling check", "Delta peak/active mean (%)"),
        (axes[1], "delta_p99_to_active_mean_pct", "(b) High-percentile sampling check", "Delta p99/active mean (%)"),
    ]:
        for offset, tag, color, name in [
            (-width / 2, "baseline8", "#4C78A8", "8 flux days"),
            (width / 2, "extended", "#F58518", "12 flux days"),
        ]:
            rows = []
            for layout_id in order:
                match = plot[(plot["layout_id"] == layout_id) & (plot["sampling_tag"] == tag)]
                rows.append(float(match.iloc[0][metric]) if not match.empty else np.nan)
            ax.bar(x + offset, rows, width=width, color=color, label=name)
        ax.axhline(0.0, color="#111827", linewidth=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=32, ha="right")
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid(True, axis="y", alpha=0.25)
    axes[0].legend(frameon=False, fontsize=7.2)

    shifts = pivot[pivot["layout_id"].isin(order)].copy()
    y = np.arange(len(shifts))
    axes[2].barh(
        y - 0.16,
        shifts["delta_peak_to_active_mean_pct_shift_extended_minus_baseline8"],
        height=0.3,
        color="#4C78A8",
        label="peak ratio shift",
    )
    axes[2].barh(
        y + 0.16,
        shifts["delta_p99_to_active_mean_pct_shift_extended_minus_baseline8"],
        height=0.3,
        color="#F58518",
        label="p99 ratio shift",
    )
    axes[2].axvline(0.0, color="#111827", linewidth=0.8)
    axes[2].set_yticks(y)
    axes[2].set_yticklabels(shifts["label"])
    axes[2].set_xlabel("12-day minus 8-day delta (pct-pt)")
    axes[2].set_title("(c) Sampling-induced shift")
    axes[2].legend(frameon=False, fontsize=7.0)
    axes[2].grid(True, axis="x", alpha=0.25)

    fig.tight_layout(w_pad=1.7)
    fig.savefig(out / "figures/fig_flux_day_sampling_gate.png", bbox_inches="tight")
    fig.savefig(out / "figures/fig_flux_day_sampling_gate.pdf", bbox_inches="tight")
    plt.close(fig)


def markdown_table(df: pd.DataFrame) -> str:
    cols = [
        "label",
        "layout_id",
        "delta_peak_to_active_mean_pct_baseline8",
        "delta_peak_to_active_mean_pct_extended",
        "delta_peak_to_active_mean_pct_shift_extended_minus_baseline8",
        "delta_p99_to_active_mean_pct_baseline8",
        "delta_p99_to_active_mean_pct_extended",
        "delta_p99_to_active_mean_pct_shift_extended_minus_baseline8",
    ]
    table = df.loc[:, cols].copy()
    table.columns = [
        "Role",
        "Layout",
        "Peak delta 8-day (%)",
        "Peak delta 12-day (%)",
        "Peak shift (pct-pt)",
        "P99 delta 8-day (%)",
        "P99 delta 12-day (%)",
        "P99 shift (pct-pt)",
    ]
    return table.to_markdown(index=False, floatfmt=".3f")


def write_report(pivot: pd.DataFrame, gate: dict[str, object], out: Path) -> None:
    lines = [
        "# SolarPILOT Flux-Day Sampling Robustness Gate",
        "",
        "## Scope",
        "",
        "This audit compares the original eight-flux-day SolarPILOT default-flux tables with an",
        "enlarged twelve-flux-day rerun for the selected direct-promotion layouts. It checks",
        "whether receiver-flux role labels are artifacts of the flux-day sampling density.",
        "It remains a default-aiming SolarPILOT audit, not custom-aimpoint, annual, or thermal certification.",
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
        f"- Pre-set shift threshold: {float(gate['shift_threshold_pctpt']):.3f} pct-pt.",
        f"- L_opt still has a 12-day default-flux penalty: `{gate['lopt_still_flux_penalty']}`.",
        f"- Receiver-pressure rows are not optical headline rows: `{gate['receiver_rows_not_optical_headline']}`.",
        f"- Interpretation: {gate['interpretation']}",
        "",
        "## Boundary",
        "",
        "Write this into the manuscript only as a short flux-day-sampling robustness sentence if the gate passes.",
        "Do not cite it as receiver thermal safety, annual custom aiming, or same-aimpoint cross-code validation.",
    ]
    (out / "FLUX_DAY_SAMPLING_GATE_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def copy_to_package(out: Path, package: Path, gate: dict[str, object]) -> None:
    sup = package / "supplementary_data" / "flux_day_sampling_gate"
    if sup.exists():
        shutil.rmtree(sup)
    shutil.copytree(out, sup)
    code_dst = package / "code/scripts/build_flux_day_sampling_gate.py"
    code_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(Path(__file__), code_dst)
    if gate["writeback_recommendation"] != "do_not_write_main_text":
        fig_src = out / "figures/fig_flux_day_sampling_gate.png"
        fig_dst = package / "latex/figures/fig_flux_day_sampling_gate.png"
        fig_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(fig_src, fig_dst)


def main() -> int:
    args = parse_args()
    out = resolve(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "tables").mkdir(exist_ok=True)
    (out / "figures").mkdir(exist_ok=True)
    baseline_run = resolve(args.baseline_run)
    extended_run = resolve(args.extended_run)
    selected_ids = [part.strip() for part in args.selected_layouts.split(",") if part.strip()]

    baseline = flux_metrics(baseline_run, "baseline8", selected_ids)
    extended = flux_metrics(extended_run, "extended", selected_ids)
    combined = pd.concat([baseline, extended], ignore_index=True)
    pivot, gate = summarize(combined, args.shift_threshold_pctpt)

    combined.to_csv(out / "tables/flux_day_sampling_metrics_all.csv", index=False)
    pivot.to_csv(out / "tables/flux_day_sampling_selected_comparison.csv", index=False)
    (out / "gate_decision.json").write_text(json.dumps(gate, indent=2), encoding="utf-8")
    (out / "run_config.json").write_text(
        json.dumps(
            {
                "baseline_run": str(baseline_run),
                "extended_run": str(extended_run),
                "selected_layouts": selected_ids,
                "shift_threshold_pctpt": args.shift_threshold_pctpt,
                "claim_boundary": "SolarPILOT default-flux sampling robustness only",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    write_figure(combined, pivot, selected_ids, out)
    write_report(pivot, gate, out)
    copy_to_package(out, resolve(args.package), gate)
    print(f"Wrote flux-day sampling gate to {out}")
    print(f"Recommendation: {gate['writeback_recommendation']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
