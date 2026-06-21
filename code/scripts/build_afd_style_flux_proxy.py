#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "paper_submission" / "solar_energy_elsarticle_v8_strict_review_rescue"


LABELS = {
    "baseline_full": r"$L_0$",
    "ctrl_radial_compact_015": r"$C_{rad-}$",
    "ctrl_radial_expand_015": r"$C_{rad+}$",
    "ctrl_ellipse_xwide_015": r"$C_{ell}$",
    "ctrl_north_bias_012": r"$C_{nb}$",
    "ctrl_ring_wave_012": r"$C_{wave}$",
    "ctrl_azimuth_stagger_018": r"$C_{stag}$",
    "deform_0276": r"$L_{opt}$",
    "deform_0893": r"$L_{nom}$",
    "deform_1387": r"$L_{rob}$",
    "deform_1822": r"$L_{ctrl}$",
    "joint_g02_0333": r"$J_{bal}$",
    "joint_g02_0303": r"$J_{gain}$",
    "joint_g04_0478": r"$J_{flux}$",
    "joint_g00_0097": r"$J_{Emax}$",
    "joint_g01_0254": r"$J_{spill}$",
    "joint_g03_0355": r"$J_{aux1}$",
    "joint_g04_0444": r"$J_{aux2}$",
}


FIGURE_SELECTION = {
    "baseline_controls": [
        "ctrl_radial_compact_015",
        "ctrl_radial_expand_015",
        "ctrl_ring_wave_012",
        "deform_0276",
        "deform_0893",
        "deform_1387",
        "deform_1822",
    ],
    "joint_default": [
        "joint_g02_0333",
        "joint_g02_0303",
        "joint_g04_0478",
    ],
}


@dataclass(frozen=True)
class Cohort:
    name: str
    tables_dir: Path
    summary_csv: Path
    description: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build relative AFD-style receiver-flux proxy metrics from SolarPILOT flux tables."
    )
    parser.add_argument("--package", type=Path, default=PACKAGE)
    return parser.parse_args()


def set_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
            "font.size": 8.8,
            "axes.titlesize": 9.6,
            "axes.labelsize": 8.6,
            "xtick.labelsize": 7.8,
            "ytick.labelsize": 7.8,
            "legend.fontsize": 7.6,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
            "axes.edgecolor": "#334155",
            "axes.linewidth": 0.7,
            "axes.grid": True,
            "grid.color": "#D8E0EA",
            "grid.linewidth": 0.55,
            "grid.alpha": 0.75,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def pct_change(value: float, base: float) -> float:
    return (float(value) / max(float(base), 1e-12) - 1.0) * 100.0


def load_flux_table(path: Path) -> np.ndarray:
    arr = pd.read_csv(path, header=None).to_numpy(dtype=float)
    if arr.ndim != 2 or arr.size == 0:
        raise ValueError(f"Flux table is empty or malformed: {path}")
    bins = arr.shape[1]
    if bins <= 0 or arr.shape[0] % bins != 0:
        raise ValueError(f"Flux table rows are not divisible by bins ({bins}): {path}")
    return arr.reshape(arr.shape[0] // bins, bins, bins)


def active_values(flat: np.ndarray) -> np.ndarray:
    threshold = float(np.percentile(flat, 55.0))
    active = flat[flat > threshold]
    if active.size == 0:
        return flat
    return active


def summarize_layout(cohort: str, layout_id: str, cube: np.ndarray, base_stats: dict[str, float]) -> dict[str, float | str]:
    flat = cube.reshape(-1)
    active = active_values(flat)
    active_mean = float(active.mean())
    p95 = float(np.percentile(active, 95.0))
    p99 = float(np.percentile(active, 99.0))
    peak = float(active.max())
    base_p95 = base_stats["active_p95"]
    base_p99 = base_stats["active_p99"]
    base_mean = base_stats["active_mean"]

    excess_p95 = np.maximum(flat - base_p95, 0.0)
    excess_p99 = np.maximum(flat - base_p99, 0.0)

    return {
        "cohort": cohort,
        "layout_id": layout_id,
        "label": LABELS.get(layout_id, layout_id.replace("_", "\\_")),
        "map_count": int(cube.shape[0]),
        "bins_x": int(cube.shape[2]),
        "bins_y": int(cube.shape[1]),
        "active_threshold_p55": float(np.percentile(flat, 55.0)),
        "active_mean": active_mean,
        "active_p95": p95,
        "active_p99": p99,
        "active_peak": peak,
        "p95_to_active_mean": p95 / max(active_mean, 1e-12),
        "p99_to_active_mean": p99 / max(active_mean, 1e-12),
        "peak_to_active_mean": peak / max(active_mean, 1e-12),
        "active_cv": float(active.std() / max(active_mean, 1e-12)),
        "area_frac_above_baseline_p95_pct": float((flat > base_p95).mean() * 100.0),
        "area_frac_above_baseline_p99_pct": float((flat > base_p99).mean() * 100.0),
        "active_frac_above_baseline_p95_pct": float((active > base_p95).mean() * 100.0),
        "active_frac_above_baseline_p99_pct": float((active > base_p99).mean() * 100.0),
        "mean_excess_over_baseline_p95_norm": float(excess_p95.mean() / max(base_mean, 1e-12)),
        "mean_excess_over_baseline_p99_norm": float(excess_p99.mean() / max(base_mean, 1e-12)),
    }


def cohort_metrics(cohort: Cohort) -> pd.DataFrame:
    summary = pd.read_csv(cohort.summary_csv)
    paths = sorted(cohort.tables_dir.glob("flux_table_*.csv"))
    if not paths:
        raise FileNotFoundError(f"No flux tables found in {cohort.tables_dir}")

    cubes: dict[str, np.ndarray] = {}
    for path in paths:
        layout_id = path.stem.replace("flux_table_", "")
        cubes[layout_id] = load_flux_table(path)

    if "baseline_full" not in cubes:
        raise FileNotFoundError(f"Missing baseline flux table in {cohort.tables_dir}")

    base_flat = cubes["baseline_full"].reshape(-1)
    base_active = active_values(base_flat)
    base_stats = {
        "active_mean": float(base_active.mean()),
        "active_p95": float(np.percentile(base_active, 95.0)),
        "active_p99": float(np.percentile(base_active, 99.0)),
    }

    records = [summarize_layout(cohort.name, layout_id, cube, base_stats) for layout_id, cube in cubes.items()]
    df = pd.DataFrame.from_records(records)
    df = df.merge(
        summary.loc[:, ["layout_id", "opteff_mean", "flux_peak_to_active_mean", "flux_active_cv"]],
        on="layout_id",
        how="left",
        suffixes=("", "_summary"),
    )

    baseline = df.loc[df["layout_id"] == "baseline_full"].iloc[0]
    for col in [
        "opteff_mean",
        "p95_to_active_mean",
        "p99_to_active_mean",
        "peak_to_active_mean",
        "active_cv",
        "area_frac_above_baseline_p95_pct",
        "area_frac_above_baseline_p99_pct",
        "active_frac_above_baseline_p95_pct",
        "active_frac_above_baseline_p99_pct",
        "mean_excess_over_baseline_p95_norm",
        "mean_excess_over_baseline_p99_norm",
    ]:
        if col == "opteff_mean":
            df[f"delta_{col}_pct"] = df[col].map(lambda x: pct_change(x, baseline[col]))
        else:
            df[f"delta_{col}_pctpt"] = df[col] - float(baseline[col])

    df["source_description"] = cohort.description
    order = {layout: i for i, layout in enumerate(["baseline_full", *FIGURE_SELECTION.get(cohort.name, [])])}
    df["plot_order"] = df["layout_id"].map(lambda value: order.get(value, 1000))
    return df.sort_values(["plot_order", "layout_id"]).drop(columns=["plot_order"])


def write_figure(selected: pd.DataFrame, out_dir: Path) -> None:
    set_style()
    fig, axes = plt.subplots(1, 3, figsize=(12.0, 3.65), dpi=220)
    colors = {
        "baseline_controls": "#2563EB",
        "joint_default": "#7C3AED",
    }
    selected = selected.copy()
    selected["group_label"] = selected["cohort"].map({"baseline_controls": "baseline/control cohort", "joint_default": "joint cohort"})

    ax = axes[0]
    for cohort, frame in selected.groupby("cohort", sort=False):
        frame = frame.sort_values("label")
        ax.barh(
            frame["label"],
            frame["delta_p99_to_active_mean_pctpt"],
            color=colors.get(cohort, "#64748B"),
            alpha=0.88,
            label=frame["group_label"].iloc[0],
        )
    ax.axvline(0, color="#0F172A", linewidth=0.8)
    ax.set_xlabel(r"$\Delta$(p99 / active mean)")
    ax.set_title("High-percentile concentration")
    ax.legend(frameon=False, loc="lower right")

    ax = axes[1]
    plot = selected.sort_values("active_frac_above_baseline_p99_pct")
    ax.barh(
        plot["label"],
        plot["active_frac_above_baseline_p99_pct"],
        color=[colors.get(c, "#64748B") for c in plot["cohort"]],
        alpha=0.88,
    )
    ax.axvline(
        float(selected.loc[selected["layout_id"] == "baseline_full", "active_frac_above_baseline_p99_pct"].mean())
        if (selected["layout_id"] == "baseline_full").any()
        else 0,
        color="#0F172A",
        linewidth=0.8,
        linestyle="--",
    )
    ax.set_xlabel("Active cells above baseline p99 (%)")
    ax.set_title("Relative hot-area proxy")

    ax = axes[2]
    for cohort, frame in selected.groupby("cohort", sort=False):
        ax.scatter(
            frame["delta_opteff_mean_pct"],
            frame["delta_active_frac_above_baseline_p99_pct_pctpt"],
            s=52,
            color=colors.get(cohort, "#64748B"),
            edgecolor="white",
            linewidth=0.8,
            label=frame["group_label"].iloc[0],
            zorder=3,
        )
        for row in frame.itertuples():
            if row.layout_id != "baseline_full":
                ax.annotate(
                    row.label,
                    (row.delta_opteff_mean_pct, row.delta_active_frac_above_baseline_p99_pct_pctpt),
                    xytext=(3, 3),
                    textcoords="offset points",
                    fontsize=7.0,
                )
    ax.axhline(0, color="#0F172A", linewidth=0.75)
    ax.axvline(0, color="#0F172A", linewidth=0.75)
    ax.set_xlabel(r"$\Delta$ mean optical efficiency (%)")
    ax.set_ylabel(r"$\Delta$ active hot-area proxy (pct-pt)")
    ax.set_title("Optical gain vs hot-area change")
    ax.legend(frameon=False, loc="upper left")

    for axis in axes:
        axis.grid(True, axis="both", alpha=0.55)

    fig.tight_layout(w_pad=1.2)
    fig.savefig(out_dir / "fig_afd_style_flux_proxy.png", bbox_inches="tight")
    fig.savefig(out_dir / "fig_afd_style_flux_proxy.pdf", bbox_inches="tight")
    plt.close(fig)


def markdown_table(df: pd.DataFrame) -> str:
    cols = [
        "label",
        "cohort",
        "delta_opteff_mean_pct",
        "delta_p99_to_active_mean_pctpt",
        "active_frac_above_baseline_p99_pct",
        "delta_active_frac_above_baseline_p99_pct_pctpt",
        "peak_to_active_mean",
    ]
    renamed = df.loc[:, cols].copy()
    renamed.columns = [
        "Candidate",
        "Cohort",
        "Delta optical (%)",
        "Delta p99/active-mean",
        "Active > baseline p99 (%)",
        "Delta active hot-area (pct-pt)",
        "Peak/active-mean",
    ]
    return renamed.to_markdown(index=False, floatfmt=".3f")


def write_report(all_df: pd.DataFrame, selected: pd.DataFrame, out_dir: Path) -> None:
    base_control = selected[selected["cohort"] == "baseline_controls"].copy()
    joint = selected[selected["cohort"] == "joint_default"].copy()

    def row(layout_id: str, frame: pd.DataFrame) -> pd.Series:
        match = frame[frame["layout_id"] == layout_id]
        if match.empty:
            return pd.Series(dtype=object)
        return match.iloc[0]

    lopt = row("deform_0276", base_control)
    lrob = row("deform_1387", base_control)
    jgain = row("joint_g02_0303", joint)
    jflux = row("joint_g04_0478", joint)

    report = [
        "# Relative AFD-style Receiver-Flux Proxy Audit",
        "",
        "This audit converts the existing SolarPILOT default-aiming flux tables into relative",
        "allowable-flux-density-style screening metrics. It does not claim certified receiver",
        "tube safety or a plant-grade thermal model. Instead, it asks whether high-percentile",
        "receiver loading and hotspot-area proxies tell the same story as the simpler",
        "peak-to-active-mean ratio already reported in the manuscript.",
        "",
        "Definitions:",
        "",
        "- Active cells are cells above the 55th percentile of the layout-specific flux table,",
        "  matching the active-zone convention used in the SolarPILOT summary scripts.",
        "- Baseline p95 and p99 thresholds are computed separately within each SolarPILOT cohort.",
        "- Hot-area proxies report the fraction of active cells above the corresponding baseline",
        "  p95 or p99 threshold. These are relative exceedance metrics, not absolute AFD limits.",
        "",
        "## Selected manuscript rows",
        "",
        markdown_table(selected),
        "",
        "## Main interpretation",
        "",
    ]
    if not lopt.empty:
        report.append(
            f"- {lopt['label']} remains a stress-test layout: it improves default optical "
            f"efficiency by {lopt['delta_opteff_mean_pct']:+.2f}% but increases the active "
            f"p99 hot-area proxy by {lopt['delta_active_frac_above_baseline_p99_pct_pctpt']:+.2f} "
            "percentage points relative to the baseline-control cohort."
        )
    if not lrob.empty:
        report.append(
            f"- {lrob['label']} is still not thermally certified. Under default aiming its active "
            f"p99 hot-area proxy changes by {lrob['delta_active_frac_above_baseline_p99_pct_pctpt']:+.2f} "
            "percentage points, so its stronger receiver-risk role still comes from the direct "
            "custom-aimpoint audits rather than from default aiming alone."
        )
    if not jgain.empty:
        report.append(
            f"- {jgain['label']} reinforces the bridge/direct split: default SolarPILOT optical "
            f"efficiency improves by {jgain['delta_opteff_mean_pct']:+.2f}%, but the active p99 "
            f"hot-area proxy changes by {jgain['delta_active_frac_above_baseline_p99_pct_pctpt']:+.2f} "
            "percentage points, so it cannot be claimed as receiver-safe without custom-aimpoint promotion."
        )
    if not jflux.empty:
        report.append(
            f"- {jflux['label']} remains a receiver-boundary candidate because of the reduced direct "
            "promotion audit, not because of default aiming. Its default-aiming active p99 hot-area "
            f"proxy changes by {jflux['delta_active_frac_above_baseline_p99_pct_pctpt']:+.2f} percentage points."
        )
    report.extend(
        [
            "",
            "## Full CSV outputs",
            "",
            "- `tables/afd_flux_proxy_summary.csv`: all layouts in both SolarPILOT cohorts.",
            "- `tables/afd_flux_proxy_selected.csv`: manuscript-facing selected rows.",
            "- `figures/fig_afd_style_flux_proxy.png`: compact figure for the manuscript.",
            "",
        ]
    )
    (out_dir / "AFD_STYLE_FLUX_PROXY_REPORT.md").write_text("\n".join(report), encoding="utf-8")


def main() -> int:
    args = parse_args()
    package = args.package.resolve()
    sup = package / "supplementary_data"
    out_dir = sup / "afd_style_flux_proxy"
    table_dir = out_dir / "tables"
    fig_dir = out_dir / "figures"
    table_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    cohorts = [
        Cohort(
            name="baseline_controls",
            tables_dir=sup / "baseline_strengthening_tables" / "solarpilot_tables",
            summary_csv=sup / "baseline_strengthening_tables" / "solarpilot_tables" / "solarpilot_summary.csv",
            description="Same-condition SolarPILOT default-aiming bridge for controls and TS-FPDA representatives.",
        ),
        Cohort(
            name="joint_default",
            tables_dir=sup / "joint_solarpilot_default_tables" / "tables",
            summary_csv=sup / "joint_solarpilot_default_tables" / "tables" / "solarpilot_summary.csv",
            description="SolarPILOT default-aiming bridge for the joint layout--aiming candidate queue.",
        ),
    ]

    frames = [cohort_metrics(cohort) for cohort in cohorts]
    all_df = pd.concat(frames, ignore_index=True)
    all_df.to_csv(table_dir / "afd_flux_proxy_summary.csv", index=False)

    selected_rows = []
    for cohort_name, layout_ids in FIGURE_SELECTION.items():
        selected_rows.append(all_df[(all_df["cohort"] == cohort_name) & (all_df["layout_id"].isin(["baseline_full", *layout_ids]))])
    selected = pd.concat(selected_rows, ignore_index=True)
    selected.to_csv(table_dir / "afd_flux_proxy_selected.csv", index=False)

    write_figure(selected, fig_dir)
    write_report(all_df, selected, out_dir)

    latex_fig_dir = package / "latex" / "figures"
    latex_fig_dir.mkdir(parents=True, exist_ok=True)
    for suffix in ["png", "pdf"]:
        src = fig_dir / f"fig_afd_style_flux_proxy.{suffix}"
        dst = latex_fig_dir / f"fig_afd_style_flux_proxy.{suffix}"
        dst.write_bytes(src.read_bytes())

    code_dir = package / "code" / "scripts"
    code_dir.mkdir(parents=True, exist_ok=True)
    dst_script = code_dir / Path(__file__).name
    dst_script.write_text(Path(__file__).read_text(encoding="utf-8"), encoding="utf-8")

    print(f"Wrote {table_dir / 'afd_flux_proxy_summary.csv'}")
    print(f"Wrote {fig_dir / 'fig_afd_style_flux_proxy.png'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
