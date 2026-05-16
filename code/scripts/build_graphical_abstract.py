#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from matplotlib import patheffects as pe


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "server_outputs" / "streamed_fullfield_20260511_205252"
PACKAGE = ROOT / "paper_submission" / "solar_energy_elsarticle_v7_balanced_full_submission"
AERIAL_CANDIDATES = [
    Path("/Users/Apple/Downloads/官方主题/175354060700-675.webp"),
    Path(
        "/Users/Apple/Downloads/官方主题/Dunhuang_Heliostat_Benchmark_Dataset/"
        "manuscript/figures/Figure_1_Aerial_View.png"
    ),
]
AERIAL = next((path for path in AERIAL_CANDIDATES if path.exists()), AERIAL_CANDIDATES[-1])
COLORS = {
    "ink": "#0F172A",
    "muted": "#475569",
    "line": "#CBD5E1",
    "soft_line": "#E2E8F0",
    "paper": "#FFFFFF",
    "fill": "#F8FAFC",
    "blue": "#2563EB",
    "orange": "#F97316",
    "purple": "#7C3AED",
    "teal": "#0891B2",
    "red": "#DC2626",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a photo-led graphical abstract for the manuscript.")
    parser.add_argument("--run", type=Path, default=RUN)
    parser.add_argument(
        "--out",
        type=Path,
        default=PACKAGE / "submission_materials" / "graphical_abstract.png",
    )
    parser.add_argument("--aerial", type=Path, default=AERIAL)
    return parser.parse_args()


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def set_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
            "font.size": 9.2,
            "figure.facecolor": "white",
            "savefig.facecolor": "white",
            "axes.facecolor": "white",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def crop_to_aspect(
    img: np.ndarray,
    target_aspect: float,
    *,
    x_anchor: float = 0.58,
    y_anchor: float = 0.54,
) -> np.ndarray:
    """Crop an image to a target width/height ratio while keeping the tower in frame."""
    h, w = img.shape[:2]
    aspect = w / h
    if abs(aspect - target_aspect) < 1e-3:
        return img
    if aspect > target_aspect:
        new_w = int(round(h * target_aspect))
        center = int(round(w * x_anchor))
        x0 = max(0, min(w - new_w, center - new_w // 2))
        return img[:, x0 : x0 + new_w]
    new_h = int(round(w / target_aspect))
    center = int(round(h * y_anchor))
    y0 = max(0, min(h - new_h, center - new_h // 2))
    return img[y0 : y0 + new_h, :]


def load_direct_best(run: Path, pick_ids: list[str]) -> pd.DataFrame:
    v9_best_path = (
        run
        / "soltrace_v9_confirm_highsample_20260512"
        / "publication_v9_confirmation"
        / "tables"
        / "v9_best_strategy_by_layout.csv"
    )
    if v9_best_path.exists():
        return pd.read_csv(v9_best_path)
    direct = pd.read_csv(
        run / "soltrace_allphase_27cond_20260512" / "tables" / "soltrace_sensitivity_summary.csv"
    )
    return (
        direct[direct["layout_id"].isin(pick_ids)]
        .sort_values(["layout_id", "mean_delta_peak_pct", "median_delta_peak_pct"])
        .groupby("layout_id", as_index=False)
        .head(1)
    )


def load_metrics(run: Path) -> tuple[pd.DataFrame, str]:
    pick_ids = ["deform_0276", "deform_0893", "deform_1387", "deform_1822"]
    solarpilot = pd.read_csv(run / "solarpilot_highres_key" / "tables" / "solarpilot_summary.csv")
    base = solarpilot.loc[solarpilot["layout_id"] == "baseline_full"].iloc[0]
    sp = solarpilot[solarpilot["layout_id"].isin(pick_ids)].copy()
    sp["delta_optical_pct"] = (sp["opteff_mean"] / float(base["opteff_mean"]) - 1.0) * 100.0
    sp["delta_default_flux_pct"] = (
        sp["flux_peak_to_active_mean"] / float(base["flux_peak_to_active_mean"]) - 1.0
    ) * 100.0
    direct = load_direct_best(run, pick_ids)
    merged = sp[["layout_id", "delta_optical_pct", "delta_default_flux_pct"]].merge(
        direct[["layout_id", "strategy", "mean_delta_peak_pct"]], on="layout_id", how="left"
    )
    merged = merged.set_index("layout_id").loc[pick_ids].reset_index()
    source = "high-sample reduced PySolTrace" if "soltrace_v9_confirm" in str(direct) else "reduced PySolTrace"
    return merged, source


def load_layouts(run: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    base = pd.read_csv(run / "layouts" / "baseline_full.csv", header=None, names=["x_m", "y_m", "z_m"])
    cand = pd.read_csv(run / "layouts" / "deform_0276.csv", header=None, names=["x_m", "y_m", "z_m"])
    return base, cand


def draw_badge(ax: plt.Axes, x: float, y: float, text: str, color: str) -> None:
    ax.text(
        x,
        y,
        text,
        transform=ax.transAxes,
        ha="left",
        va="center",
        fontsize=7.0,
        weight="bold",
        color=color,
        bbox={
            "boxstyle": "round,pad=0.24,rounding_size=0.14",
            "facecolor": "white",
            "edgecolor": "#E2E8F0",
            "linewidth": 0.7,
            "alpha": 0.96,
        },
    )


def workflow_spine(ax: plt.Axes) -> None:
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.text(
        0.00,
        0.98,
        "Algorithmic story",
        ha="left",
        va="top",
        fontsize=11.6,
        weight="bold",
        color=COLORS["ink"],
    )
    ax.text(
        0.00,
        0.91,
        "A real surround-field benchmark is turned into a bounded candidate queue, then re-ranked by receiver-risk numerical checks.",
        ha="left",
        va="top",
        fontsize=7.6,
        color=COLORS["muted"],
        linespacing=1.14,
    )
    nodes = [
        ("01", "Audit", "plant anchors\n+ field count", COLORS["teal"]),
        ("02", "Generate", "bounded full-field\nTFPDA variants", COLORS["blue"]),
        ("03", "Check", "SolarPILOT optical\nand default flux", COLORS["orange"]),
        ("04", "Re-rank", "direct aimpoint\nPySolTrace queue", COLORS["purple"]),
    ]
    xs = [0.08, 0.365, 0.650, 0.930]
    y = 0.58
    ax.plot([xs[0], xs[-1]], [y, y], color=COLORS["soft_line"], linewidth=5.0, solid_capstyle="round", zorder=1)
    ax.plot([xs[0], xs[-1]], [y, y], color="#64748B", linewidth=0.85, solid_capstyle="round", zorder=2)
    for idx, (number, title, body, color) in enumerate(nodes):
        x = xs[idx]
        ax.add_patch(plt.Circle((x, y), 0.033, facecolor="white", edgecolor=color, linewidth=1.35, zorder=3))
        ax.text(x, y, number, ha="center", va="center", fontsize=6.2, weight="bold", color=color, zorder=4)
        ax.plot([x, x], [y - 0.048, y - 0.112], color=color, linewidth=1.05, alpha=0.75)
        ax.text(x, y - 0.152, title, ha="center", va="top", fontsize=8.2, weight="bold", color=COLORS["ink"])
        ax.text(x, y - 0.224, body, ha="center", va="top", fontsize=6.45, color=COLORS["muted"], linespacing=1.10)
    ax.add_patch(
        FancyArrowPatch(
            (xs[-1] - 0.015, y - 0.335),
            (xs[1] + 0.015, y - 0.335),
            arrowstyle="-|>",
            mutation_scale=9,
            linewidth=0.9,
            color=COLORS["purple"],
            connectionstyle="arc3,rad=-0.18",
        )
    )
    ax.text(
        0.65,
        y - 0.400,
        "direct checks can reorder the queue",
        ha="center",
        va="top",
        fontsize=7.0,
        weight="bold",
        color=COLORS["purple"],
    )


def layout_anchor_panel(ax: plt.Axes, baseline: pd.DataFrame, candidate: pd.DataFrame) -> None:
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.add_patch(
        FancyBboxPatch(
            (0.00, 0.00),
            1.0,
            1.0,
            boxstyle="round,pad=0.008,rounding_size=0.025",
            facecolor="#F8FAFC",
            edgecolor="#CBD5E1",
            linewidth=0.8,
        )
    )
    ax.text(0.055, 0.935, "Full-field geometry anchor", ha="left", va="top", fontsize=11.6, weight="bold", color=COLORS["ink"])
    ax.text(
        0.055,
        0.875,
        "Coordinate fallback schematic for submissions that request no photographs.",
        ha="left",
        va="top",
        fontsize=7.4,
        color=COLORS["muted"],
    )
    plot_ax = ax.inset_axes([0.055, 0.160, 0.890, 0.650])
    stride = max(1, len(baseline) // 7000)
    plot_ax.scatter(
        baseline.iloc[::stride]["x_m"],
        baseline.iloc[::stride]["y_m"],
        s=0.38,
        color="#8EA0B8",
        alpha=0.55,
        linewidths=0,
        rasterized=True,
        label="baseline pool",
    )
    subset = candidate.iloc[:: max(1, len(candidate) // 850)]
    plot_ax.scatter(
        subset["x_m"],
        subset["y_m"],
        s=5.2,
        facecolors="none",
        edgecolors=COLORS["blue"],
        alpha=0.65,
        linewidths=0.45,
        rasterized=True,
        label="bounded candidate",
    )
    plot_ax.scatter([0], [0], marker="^", s=56, color=COLORS["red"], edgecolor="white", linewidth=0.6, zorder=5)
    plot_ax.set_aspect("equal", adjustable="box")
    plot_ax.set_xlim(-2150, 2150)
    plot_ax.set_ylim(-2150, 2150)
    plot_ax.set_xticks([-2000, 0, 2000])
    plot_ax.set_yticks([-2000, 0, 2000])
    plot_ax.tick_params(labelsize=6.4, length=2.0, width=0.6)
    plot_ax.grid(True, color="#D5DEE8", linewidth=0.55, alpha=0.70)
    plot_ax.spines["top"].set_visible(False)
    plot_ax.spines["right"].set_visible(False)
    plot_ax.set_xlabel("x coordinate (m)", fontsize=6.8, labelpad=1)
    plot_ax.set_ylabel("y coordinate (m)", fontsize=6.8, labelpad=1)
    plot_ax.legend(frameon=False, loc="lower left", fontsize=6.3, handletextpad=0.3)
    draw_badge(ax, 0.055, 0.090, "11,915 coordinates retained", COLORS["teal"])
    draw_badge(ax, 0.430, 0.090, "1,841 candidates screened", COLORS["blue"])


def evidence_bar(
    ax: plt.Axes,
    y: float,
    label: str,
    value: str,
    body: str,
    color: str,
    fraction: float,
) -> None:
    ax.text(0.00, y + 0.044, label, ha="left", va="center", fontsize=8.2, weight="bold", color=COLORS["ink"])
    ax.text(0.96, y + 0.044, value, ha="right", va="center", fontsize=9.2, weight="bold", color=color)
    ax.add_patch(
        FancyBboxPatch(
            (0.00, y - 0.002),
            0.96,
            0.026,
            boxstyle="round,pad=0.003,rounding_size=0.012",
            facecolor="#EEF2F7",
            edgecolor="none",
        )
    )
    ax.add_patch(
        FancyBboxPatch(
            (0.00, y - 0.002),
            0.96 * np.clip(fraction, 0.05, 1.0),
            0.026,
            boxstyle="round,pad=0.003,rounding_size=0.012",
            facecolor=color,
            edgecolor="none",
            alpha=0.95,
        )
    )
    ax.text(0.00, y - 0.053, body, ha="left", va="top", fontsize=7.0, color=COLORS["muted"])


def evidence_panel(ax: plt.Axes, metrics: pd.DataFrame) -> None:
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.text(0.00, 0.99, "Cross-layer evidence", ha="left", va="top", fontsize=11.6, weight="bold", color=COLORS["ink"])
    d0276 = metrics.loc[metrics["layout_id"] == "deform_0276"].iloc[0]
    d1387 = metrics.loc[metrics["layout_id"] == "deform_1387"].iloc[0]
    d1822 = metrics.loc[metrics["layout_id"] == "deform_1822"].iloc[0]
    evidence_bar(
        ax,
        0.75,
        "Optical upper case",
        f"D0276 +{d0276['delta_optical_pct']:.2f}%",
        "SolarPILOT efficiency improves; receiver loading is not ignored.",
        COLORS["blue"],
        float(d0276["delta_optical_pct"]) / 3.4,
    )
    evidence_bar(
        ax,
        0.49,
        "Default flux penalty",
        f"D0276 +{d0276['delta_default_flux_pct']:.2f}%",
        "The same optical candidate raises default peak/active-mean flux.",
        COLORS["orange"],
        float(d0276["delta_default_flux_pct"]) / 5.0,
    )
    evidence_bar(
        ax,
        0.23,
        "Direct aimpoint check",
        f"D1387 {d1387['mean_delta_peak_pct']:.2f}%",
        "High-sample reduced PySolTrace shifts the receiver-risk queue.",
        COLORS["purple"],
        abs(float(d1387["mean_delta_peak_pct"])) / 3.6,
    )
    ax.text(
        0.00,
        0.045,
        f"Control role: D1822 remains conservative ({d1822['mean_delta_peak_pct']:.2f}% direct P/M).",
        ha="left",
        va="bottom",
        fontsize=7.0,
        color=COLORS["muted"],
    )


def main() -> int:
    args = parse_args()
    set_style()
    run = resolve(args.run)
    out = resolve(args.out)
    aerial = resolve(args.aerial)
    out.parent.mkdir(parents=True, exist_ok=True)

    metrics, _ = load_metrics(run)
    image = plt.imread(aerial)

    fig = plt.figure(figsize=(13.8, 5.2), dpi=300)
    fig.patch.set_facecolor(COLORS["paper"])

    title_ax = fig.add_axes([0.045, 0.885, 0.91, 0.095])
    title_ax.set_axis_off()
    title_ax.text(
        0.00,
        0.72,
        "Dunhuang full-field heliostat benchmark with receiver-risk checks",
        ha="left",
        va="center",
        fontsize=17.0,
        weight="bold",
        color=COLORS["ink"],
    )
    title_ax.text(
        0.00,
        0.20,
        "Author-captured aerial context anchors a full-field layout algorithm; numerical-check layers turn candidates into a defensible queue.",
        ha="left",
        va="center",
        fontsize=9.1,
        color=COLORS["muted"],
    )

    photo_ax = fig.add_axes([0.045, 0.115, 0.465, 0.725])
    photo_ax.set_axis_off()
    target_aspect = (0.465 * 13.8) / (0.725 * 5.2)
    cropped = crop_to_aspect(image, target_aspect, x_anchor=0.61, y_anchor=0.56)
    photo_ax.imshow(cropped)
    rounded = FancyBboxPatch(
        (0, 0),
        1,
        1,
        transform=photo_ax.transAxes,
        boxstyle="round,pad=0,rounding_size=0.030",
        facecolor="none",
        edgecolor="white",
        linewidth=0.0,
    )
    photo_ax.add_patch(rounded)
    photo_ax.images[0].set_clip_path(rounded)
    photo_ax.add_patch(
        FancyBboxPatch(
            (0.022, 0.062),
            0.540,
            0.145,
            transform=photo_ax.transAxes,
            boxstyle="round,pad=0.014,rounding_size=0.018",
            facecolor=(1, 1, 1, 0.90),
            edgecolor=(1, 1, 1, 0.65),
            linewidth=0.8,
        )
    )
    photo_ax.text(
        0.045,
        0.166,
        "Real Dunhuang surround field",
        transform=photo_ax.transAxes,
        ha="left",
        va="center",
        fontsize=9.3,
        weight="bold",
        color=COLORS["ink"],
        path_effects=[pe.withStroke(linewidth=1.2, foreground="white")],
    )
    photo_ax.text(
        0.045,
        0.112,
        "author-captured aerial photograph",
        transform=photo_ax.transAxes,
        ha="left",
        va="center",
        fontsize=6.6,
        color=COLORS["muted"],
        linespacing=1.10,
    )
    draw_badge(photo_ax, 0.045, 0.077, "full-field benchmark, not mirror deletion", COLORS["teal"])

    spine_ax = fig.add_axes([0.555, 0.485, 0.400, 0.345])
    workflow_spine(spine_ax)

    evidence_ax = fig.add_axes([0.555, 0.120, 0.400, 0.330])
    evidence_panel(evidence_ax, metrics)

    fig.text(
        0.955,
        0.065,
        "Claim boundary: reproducible benchmark and numerical-checking queue, not a final commercial redesign.",
        ha="right",
        va="center",
        fontsize=7.0,
        color=COLORS["muted"],
    )
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote graphical abstract to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
