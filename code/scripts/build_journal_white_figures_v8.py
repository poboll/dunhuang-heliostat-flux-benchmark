#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import shutil
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle
import numpy as np
import pandas as pd
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dhf_rebuild.data_io import load_json
from dhf_rebuild.solar_proxy import compute_heliostat_features

PACKAGE = ROOT / "paper_submission" / "solar_energy_elsarticle_v8_strict_review_rescue"
STREAMED_RUN = ROOT / "server_outputs" / "streamed_fullfield_20260511_205252"
SOLTRACE_MATRIX = STREAMED_RUN / "soltrace_corrected_stage_order_matrix"
FIG_DIR = PACKAGE / "latex" / "figures"
SUBMISSION_DIR = PACKAGE / "submission_materials"
AERIAL_CANDIDATES = [
    Path("/Users/Apple/Downloads/官方主题/175354060700-675.webp"),
    Path(
        "/Users/Apple/Downloads/官方主题/Dunhuang_Heliostat_Benchmark_Dataset/"
        "manuscript/figures/Figure_1_Aerial_View.png"
    ),
]
AERIAL = next((path for path in AERIAL_CANDIDATES if path.exists()), AERIAL_CANDIDATES[-1])
CHINA_JSON_CANDIDATES = [
    ROOT / "data" / "spatial" / "china_echarts_4_9_0.json",
    Path(
        "/Users/Apple/Developer/art/眼智医/👀forntend/node_modules/.pnpm/"
        "echarts@4.9.0/node_modules/echarts/map/json/china.json"
    ),
]

PALETTE = {
    "baseline_full": "#64748B",
    "deform_0276": "#2563EB",
    "deform_0893": "#7C3AED",
    "deform_1387": "#0E7490",
    "deform_1822": "#9333EA",
    "accent": "#F97316",
    "ink": "#0F172A",
    "muted": "#475569",
    "grid": "#D5DEE8",
    "field": "#536A86",
    "direct": "#7C3AED",
    "default_flux": "#F97316",
}

PROVINCE_LABELS = {
    "620000": ("Gansu", 100.8, 38.9, "#9A3412"),
    "710000": ("Taiwan", 121.0, 23.7, "#334155"),
    "460000": ("Hainan", 109.7, 19.2, "#334155"),
}

ROLE_LABELS = {
    "baseline_full": "baseline",
    "deform_0276": "optical upper",
    "deform_0893": "nominal proxy leader",
    "deform_1387": "robust proxy",
    "deform_1822": "direct-ray leader",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build white-background journal figures for the Solar Energy draft.")
    parser.add_argument("--run", type=Path, default=STREAMED_RUN)
    parser.add_argument("--matrix", type=Path, default=SOLTRACE_MATRIX)
    parser.add_argument("--package", type=Path, default=PACKAGE)
    return parser.parse_args()


def set_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
            "font.weight": "normal",
            "font.size": 9.0,
            "axes.titlesize": 9.8,
            "axes.titleweight": "normal",
            "axes.labelsize": 8.8,
            "xtick.labelsize": 7.8,
            "ytick.labelsize": 7.8,
            "legend.fontsize": 7.8,
            "figure.titlesize": 11,
            "axes.facecolor": "white",
            "figure.facecolor": "white",
            "savefig.facecolor": "white",
            "axes.edgecolor": "#374151",
            "axes.linewidth": 0.7,
            "axes.grid": True,
            "grid.color": PALETTE["grid"],
            "grid.linewidth": 0.55,
            "grid.alpha": 0.65,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def short_layout(value: str) -> str:
    return value.replace("baseline_full", "baseline").replace("deform_", "D")


def role_marker_label(value: str) -> str:
    return {
        "baseline_full": "baseline",
        "deform_0276": r"$L_{opt}$",
        "deform_0893": r"$L_{nom}$",
        "deform_1387": r"$L_{rob}$",
        "deform_1822": r"$L_{ctrl}$",
    }.get(value, short_layout(value))


def clean_strategy(value: str) -> str:
    return (
        value.replace("staggered_levels:9:0.380:", "S9-p")
        .replace("staggered_levels:7:0.380:", "S7-p")
        .replace("staggered_levels:7:0.340:", "S7a-p")
        .replace("visible_equator", "visible")
        .replace("five_point", "five-point")
        .replace("equator", "equator")
    )


def annotate_panel(ax, label: str) -> None:
    ax.text(
        0.010,
        0.988,
        label,
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=7.4,
        fontweight="normal",
        color=PALETTE["ink"],
        bbox={"boxstyle": "round,pad=0.12", "facecolor": "white", "edgecolor": "#D1D5DB", "linewidth": 0.45},
    )


def panel_label(ax: plt.Axes, label: str, *, x: float = 0.010, y: float = 0.988) -> None:
    ax.text(
        x,
        y,
        label,
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=8.0,
        fontweight="normal",
        color=PALETTE["ink"],
        bbox={"boxstyle": "round,pad=0.10", "facecolor": "white", "edgecolor": "#D1D5DB", "linewidth": 0.40, "alpha": 0.92},
        zorder=12,
    )


def crop_to_aspect(
    img: np.ndarray,
    target_aspect: float,
    *,
    x_anchor: float = 0.58,
    y_anchor: float = 0.54,
) -> np.ndarray:
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


def decode_echarts_ring(encoded: str, offset: list[float]) -> np.ndarray:
    points = []
    prev_x = int(offset[0])
    prev_y = int(offset[1])
    for idx in range(0, len(encoded), 2):
        x = ord(encoded[idx]) - 64
        y = ord(encoded[idx + 1]) - 64
        x = (x >> 1) ^ (-(x & 1))
        y = (y >> 1) ^ (-(y & 1))
        x += prev_x
        y += prev_y
        prev_x = x
        prev_y = y
        points.append((x / 1024.0, y / 1024.0))
    return np.asarray(points, dtype=float)


def ring_to_array(ring, offset=None) -> np.ndarray | None:
    if isinstance(ring, str):
        if offset is None:
            return None
        return decode_echarts_ring(ring, offset)
    arr = np.asarray(ring, dtype=float)
    if arr.ndim == 2 and arr.shape[1] >= 2:
        return arr[:, :2]
    return None


def iter_geo_rings(geometry: dict) -> list[np.ndarray]:
    rings: list[np.ndarray] = []
    offsets = geometry.get("encodeOffsets", [])
    if geometry.get("type") == "Polygon":
        for idx, ring in enumerate(geometry.get("coordinates", [])):
            offset = offsets[idx] if idx < len(offsets) else None
            arr = ring_to_array(ring, offset)
            if arr is not None:
                rings.append(arr)
    elif geometry.get("type") == "MultiPolygon":
        for pidx, polygon in enumerate(geometry.get("coordinates", [])):
            polygon_offsets = offsets[pidx] if pidx < len(offsets) else []
            for ridx, ring in enumerate(polygon):
                offset = polygon_offsets[ridx] if ridx < len(polygon_offsets) else None
                arr = ring_to_array(ring, offset)
                if arr is not None:
                    rings.append(arr)
    return rings


def project_china_lambert(lon: np.ndarray | float, lat: np.ndarray | float) -> tuple[np.ndarray, np.ndarray]:
    """Lambert conformal conic projection tuned for a compact China locator map."""
    lon_arr = np.asarray(lon, dtype=float)
    lat_arr = np.asarray(lat, dtype=float)
    lon0 = math.radians(105.0)
    lat0 = math.radians(35.0)
    phi1 = math.radians(25.0)
    phi2 = math.radians(47.0)
    lam = np.radians(lon_arr)
    phi = np.radians(lat_arr)
    n = math.log(math.cos(phi1) / math.cos(phi2)) / math.log(
        math.tan(math.pi / 4.0 + phi2 / 2.0) / math.tan(math.pi / 4.0 + phi1 / 2.0)
    )
    f = math.cos(phi1) * math.tan(math.pi / 4.0 + phi1 / 2.0) ** n / n
    rho = f / np.tan(math.pi / 4.0 + phi / 2.0) ** n
    rho0 = f / math.tan(math.pi / 4.0 + lat0 / 2.0) ** n
    theta = n * (lam - lon0)
    return rho * np.sin(theta), rho0 - rho * np.cos(theta)


def projected_ring_extent(rings: list[np.ndarray]) -> tuple[float, float, float, float]:
    xs: list[np.ndarray] = []
    ys: list[np.ndarray] = []
    for ring in rings:
        x, y = project_china_lambert(ring[:, 0], ring[:, 1])
        xs.append(x)
        ys.append(y)
    if not xs:
        return -1.0, 1.0, -1.0, 1.0
    x_all = np.concatenate(xs)
    y_all = np.concatenate(ys)
    return float(x_all.min()), float(x_all.max()), float(y_all.min()), float(y_all.max())


def draw_projected_graticule(ax: plt.Axes, expanded: bool) -> None:
    if not expanded:
        return
    for lon in [80, 100, 120]:
        lat_line = np.linspace(18, 54, 140)
        lon_line = np.full_like(lat_line, lon, dtype=float)
        x, y = project_china_lambert(lon_line, lat_line)
        ax.plot(x, y, color="#E2E8F0", linewidth=0.45, zorder=0)
    for lat in [20, 30, 40, 50]:
        lon_line = np.linspace(73, 136, 180)
        lat_line = np.full_like(lon_line, lat, dtype=float)
        x, y = project_china_lambert(lon_line, lat_line)
        ax.plot(x, y, color="#E2E8F0", linewidth=0.45, zorder=0)


def draw_site_locator(ax: plt.Axes, expanded: bool = False) -> None:
    ax.set_facecolor("#FFFFFF")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    if not expanded:
        ax.text(
            0.04,
            0.94,
            "site locator",
            transform=ax.transAxes,
            ha="left",
            va="top",
            fontsize=5.6,
            fontweight="normal",
            color=PALETTE["ink"],
            zorder=8,
        )
    site_lon, site_lat = 94.426, 40.063
    china_json = next((path for path in CHINA_JSON_CANDIDATES if path.exists()), None)
    if china_json is not None:
        with china_json.open(encoding="utf-8") as fh:
            china = json.load(fh)
        feature_rings: list[tuple[dict, list[np.ndarray]]] = [
            (feature, iter_geo_rings(feature.get("geometry", {}))) for feature in china.get("features", [])
        ]
        all_rings = [ring for _, rings in feature_rings for ring in rings]
        draw_projected_graticule(ax, expanded)
        for feature in china.get("features", []):
            props = feature.get("properties", {})
            is_gansu = props.get("id") == "620000"
            is_island_or_sar = props.get("id") in {"710000", "460000", "810000", "820000"}
            face = "#F7FAFC" if expanded else "#FFFFFF"
            edge = "#94A3B8" if expanded else "#AEBFD3"
            lw = 0.42 if expanded else 0.24
            z = 1
            if is_gansu:
                face = "#FED7AA"
                edge = "#EA580C"
                lw = 0.95 if expanded else 0.66
                z = 3
            elif is_island_or_sar:
                face = "#EFF6FF"
                edge = "#334155"
                lw = 0.62 if expanded else 0.34
                z = 2
            for ring in iter_geo_rings(feature.get("geometry", {})):
                x, y = project_china_lambert(ring[:, 0], ring[:, 1])
                ax.fill(x, y, facecolor=face, edgecolor=edge, linewidth=lw, zorder=z)
        if expanded:
            for code, (label, lon, lat, color) in PROVINCE_LABELS.items():
                if code != "620000":
                    continue
                lx_arr, ly_arr = project_china_lambert(lon, lat)
                ax.text(
                    float(lx_arr),
                    float(ly_arr),
                    label,
                    fontsize=5.4,
                    color=color,
                    ha="center",
                    va="center",
                    zorder=7,
                    bbox={
                        "boxstyle": "round,pad=0.12",
                        "facecolor": "white",
                        "edgecolor": "none",
                        "alpha": 0.78,
                    },
                )
            inset = ax.inset_axes([0.685, 0.045, 0.285, 0.330])
            inset.set_facecolor("#FFFFFF")
            inset.set_xticks([])
            inset.set_yticks([])
            for spine in inset.spines.values():
                spine.set_color("#CBD5E1")
                spine.set_linewidth(0.55)
            inset.set_xlim(105, 125)
            inset.set_ylim(3, 25)
            for feature, rings in feature_rings:
                props = feature.get("properties", {})
                if props.get("id") not in {"460000", "710000", "810000", "820000"}:
                    continue
                for ring in rings:
                    inset.fill(
                        ring[:, 0],
                        ring[:, 1],
                        facecolor="#EFF6FF",
                        edgecolor="#334155",
                        linewidth=0.55,
                        zorder=2,
                    )
            island_lons = [112.3, 114.1, 116.4, 118.8, 111.2, 119.5]
            island_lats = [16.8, 14.7, 12.2, 10.4, 8.8, 6.6]
            inset.scatter(island_lons, island_lats, s=6.0, color="#2563EB", alpha=0.85, zorder=3)
            inset.scatter([121.0, 110.0], [23.7, 19.2], s=10.0, color="#2563EB", alpha=0.95, zorder=4)
            inset.text(121.3, 23.2, "Taiwan", fontsize=4.6, color="#334155", ha="left", va="center")
            inset.text(110.3, 18.8, "Hainan", fontsize=4.6, color="#334155", ha="left", va="center")
            inset.text(
                105.6,
                4.4,
                "South China Sea\nisland inset",
                fontsize=4.4,
                color=PALETTE["muted"],
                ha="left",
                va="bottom",
            )
        site_x_arr, site_y_arr = project_china_lambert(site_lon, site_lat)
        site_x = float(site_x_arr)
        site_y = float(site_y_arr)
        ax.scatter(
            [site_x],
            [site_y],
            s=32 if expanded else 14,
            marker="o",
            color="#B91C1C",
            edgecolor="white",
            linewidth=0.65,
            zorder=5,
        )
        ax.annotate(
            "Dunhuang",
            xy=(site_x, site_y),
            xytext=(10, 8),
            textcoords="offset points",
            fontsize=7.6 if expanded else 5.1,
            color=PALETTE["ink"],
            ha="left",
            va="bottom",
            arrowprops={"arrowstyle": "-", "color": "#475569", "linewidth": 0.62},
            clip_on=True,
            zorder=6,
        )
        x_min, x_max, y_min, y_max = projected_ring_extent(all_rings)
        pad_x = (x_max - x_min) * (0.085 if expanded else 0.100)
        pad_y = (y_max - y_min) * (0.090 if expanded else 0.120)
        ax.set_xlim(x_min - pad_x, x_max + pad_x)
        ax.set_ylim(y_min - pad_y, y_max + pad_y)
        ax.set_aspect("equal", adjustable="box")
    else:
        ax.text(0.5, 0.55, "Dunhuang site", transform=ax.transAxes, ha="center", va="center", fontsize=6.0)
        ax.text(0.5, 0.35, "40.063 N, 94.426 E", transform=ax.transAxes, ha="center", va="center", fontsize=5.4, color=PALETTE["muted"])
    if not expanded:
        ax.text(
            0.04,
            0.04,
            "Gansu, NW China",
            transform=ax.transAxes,
            ha="left",
            va="bottom",
            fontsize=5.2,
            color=PALETTE["muted"],
        )


def add_context_metric(ax: plt.Axes, y: float, label: str, value: str, color: str) -> None:
    ax.text(0.08, y, label, transform=ax.transAxes, ha="left", va="center", fontsize=7.3, color=PALETTE["muted"])
    ax.text(0.92, y, value, transform=ax.transAxes, ha="right", va="center", fontsize=8.2, color=color)
    ax.plot([0.08, 0.92], [y - 0.052, y - 0.052], transform=ax.transAxes, color="#E2E8F0", linewidth=0.6)


def draw_site_context_panel(ax: plt.Axes) -> None:
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    panel = FancyBboxPatch(
        (0.02, 0.02),
        0.96,
        0.96,
        boxstyle="round,pad=0.012,rounding_size=0.026",
        facecolor="#FFFFFF",
        edgecolor="#CBD5E1",
        linewidth=0.8,
    )
    ax.add_patch(panel)
    locator = ax.inset_axes([0.07, 0.48, 0.86, 0.43])
    draw_site_locator(locator)
    ax.text(
        0.08,
        0.405,
        "Dunhuang 100 MW tower benchmark",
        transform=ax.transAxes,
        ha="left",
        va="center",
        fontsize=9.8,
        color=PALETTE["ink"],
    )
    ax.text(
        0.08,
        0.350,
        "fallback site context panel for photo-free submissions",
        transform=ax.transAxes,
        ha="left",
        va="center",
        fontsize=6.8,
        color=PALETTE["muted"],
    )
    add_context_metric(ax, 0.270, "Reported plant count", "11,935", PALETTE["ink"])
    add_context_metric(ax, 0.195, "Audited coordinate pool", "11,915", PALETTE["field"])
    add_context_metric(ax, 0.120, "Candidate queue", "1,841", PALETTE["deform_0276"])
    ax.text(
        0.08,
        0.060,
        "All candidate layouts preserve the audited coordinate count.",
        transform=ax.transAxes,
        ha="left",
        va="center",
        fontsize=6.6,
        color=PALETTE["muted"],
    )


def load_summary(run: Path) -> pd.DataFrame:
    reps = pd.read_csv(run / "tables" / "fullfield_representatives.csv")
    sp = pd.read_csv(run / "solarpilot_highres_key" / "tables" / "solarpilot_summary.csv")
    aim = pd.read_csv(run / "aiming_proxy" / "best_aiming_by_layout.csv")
    df = reps.merge(
        sp[
            [
                "layout_id",
                "opteff_mean",
                "flux_peak_to_active_mean",
                "flux_active_cv",
                "max_radius_m",
                "x_span_p99_m",
                "y_span_p99_m",
            ]
        ],
        left_on="candidate_id",
        right_on="layout_id",
        how="inner",
    ).merge(
        aim[["layout_id", "strategy", "peak_to_mean_proxy", "intercept_fraction_proxy"]],
        on="layout_id",
        how="left",
    )
    base = df.loc[df["layout_id"] == "baseline_full"].iloc[0]
    df["opteff_delta_pct"] = (df["opteff_mean"] / base["opteff_mean"] - 1.0) * 100.0
    df["default_flux_delta_pct"] = (
        df["flux_peak_to_active_mean"] / base["flux_peak_to_active_mean"] - 1.0
    ) * 100.0
    df["aim_proxy_delta_pct"] = (df["peak_to_mean_proxy"] / base["peak_to_mean_proxy"] - 1.0) * 100.0
    return df


def figure_layout_panel(run: Path, out: Path) -> None:
    baseline = pd.read_csv(run / "layouts" / "baseline_full.csv", header=None, names=["x_m", "y_m", "z_m"])
    selected = ["deform_0276", "deform_0893", "deform_1387", "deform_1822"]
    variant_frames = {
        layout_id: pd.read_csv(run / "layouts" / f"{layout_id}.csv", header=None, names=["x_m", "y_m", "z_m"])
        for layout_id in selected
    }

    if AERIAL.exists():
        shutil.copy2(AERIAL, out / "fig1_author_aerial_original.webp")
        photo = ImageOps.exif_transpose(Image.open(AERIAL)).convert("RGB")
        # Lossless format conversion only: no crop, color adjustment, annotation, or resampling.
        photo.save(out / "fig1_author_aerial_fullframe.png", compress_level=0)
    else:
        photo = None

    fig = plt.figure(figsize=(7.25, 6.70), dpi=320)
    gs = fig.add_gridspec(
        2,
        2,
        width_ratios=[1.02, 0.98],
        height_ratios=[1.60, 1.0],
        left=0.055,
        right=0.985,
        bottom=0.070,
        top=0.985,
        wspace=0.18,
        hspace=0.12,
    )
    ax_photo = fig.add_subplot(gs[0, :])
    ax_locator = fig.add_subplot(gs[1, 0])
    ax_overlay = fig.add_subplot(gs[1, 1])

    if photo is not None:
        ax_photo.imshow(np.asarray(photo))
    else:
        ax_photo.text(
            0.5,
            0.5,
            "author-captured aerial photograph missing",
            transform=ax_photo.transAxes,
            ha="center",
            va="center",
            fontsize=8.0,
            color=PALETTE["muted"],
        )
    ax_photo.set_axis_off()
    ax_photo.text(
        0.010,
        0.970,
        "(a)",
        transform=ax_photo.transAxes,
        ha="left",
        va="top",
        fontsize=7.4,
        fontweight="normal",
        color=PALETTE["ink"],
        bbox={"boxstyle": "round,pad=0.12", "facecolor": "white", "edgecolor": "#D1D5DB", "linewidth": 0.45, "alpha": 0.92},
    )

    draw_site_locator(ax_locator, expanded=True)
    annotate_panel(ax_locator, "(b)")

    stride = max(1, len(baseline) // 9000)
    ax_overlay.scatter(
        baseline.iloc[::stride]["x_m"],
        baseline.iloc[::stride]["y_m"],
        color="#B8C4D6",
        s=0.32,
        alpha=0.40,
        linewidths=0,
        label="baseline",
        rasterized=True,
    )
    overlay_colors = {
        "deform_0276": PALETTE["deform_0276"],
        "deform_0893": PALETTE["deform_0893"],
        "deform_1387": PALETTE["deform_1387"],
        "deform_1822": PALETTE["deform_1822"],
    }
    for layout_id, df in variant_frames.items():
        subset = df.iloc[:: max(1, len(df) // 720)]
        ax_overlay.scatter(
            subset["x_m"],
            subset["y_m"],
            facecolors="none",
            edgecolors=overlay_colors[layout_id],
            s=4.0,
            alpha=0.48,
            linewidths=0.42,
            rasterized=True,
            label=role_marker_label(layout_id),
        )
    ax_overlay.scatter([0], [0], marker="^", s=46, color="#B91C1C", edgecolor="white", linewidth=0.55, zorder=5)
    annotate_panel(ax_overlay, "(c)")
    ax_overlay.legend(
        frameon=False,
        loc="lower center",
        bbox_to_anchor=(0.50, -0.18),
        ncol=5,
        fontsize=6.4,
        handletextpad=0.25,
        columnspacing=0.70,
    )
    ax_overlay.set_aspect("equal", adjustable="box")
    ax_overlay.set_xlim(-2150, 2150)
    ax_overlay.set_ylim(-2150, 2150)
    ax_overlay.set_xlabel("x coordinate (m)", fontsize=6.8, labelpad=2)
    ax_overlay.set_ylabel("y coordinate (m)", fontsize=6.8, labelpad=2)
    ax_overlay.tick_params(axis="both", labelsize=6.2, length=2.2, width=0.65)
    ax_overlay.grid(True)
    ax_overlay.spines["top"].set_visible(False)
    ax_overlay.spines["right"].set_visible(False)

    fig.savefig(out / "fig_journal_layout_realism_panel.png", bbox_inches="tight")
    plt.close(fig)

    bottom = plt.figure(figsize=(7.25, 3.85), dpi=360)
    bgs = bottom.add_gridspec(
        1,
        2,
        width_ratios=[1.10, 0.90],
        left=0.026,
        right=0.992,
        bottom=0.215,
        top=0.975,
        wspace=0.170,
    )
    ax_b = bottom.add_subplot(bgs[0, 0])
    ax_c = bottom.add_subplot(bgs[0, 1])
    draw_site_locator(ax_b, expanded=True)
    panel_label(ax_b, "(b)")

    ax_c.scatter(
        baseline.iloc[::stride]["x_m"],
        baseline.iloc[::stride]["y_m"],
        color="#9AA8BB",
        s=0.30,
        alpha=0.30,
        linewidths=0,
        label="baseline",
        rasterized=True,
    )
    for layout_id, df in variant_frames.items():
        subset = df.iloc[:: max(1, len(df) // 720)]
        ax_c.scatter(
            subset["x_m"],
            subset["y_m"],
            facecolors="none",
            edgecolors=overlay_colors[layout_id],
            s=4.5,
            alpha=0.56,
            linewidths=0.44,
            rasterized=True,
            label=role_marker_label(layout_id),
        )
    ax_c.scatter([0], [0], marker="^", s=52, color="#B91C1C", edgecolor="white", linewidth=0.58, zorder=5)
    panel_label(ax_c, "(c)")
    ax_c.set_aspect("equal", adjustable="box")
    ax_c.set_xlim(-2050, 2050)
    ax_c.set_ylim(-2050, 2050)
    ax_c.set_xlabel("x coordinate (m)", fontsize=7.4, labelpad=2)
    ax_c.set_ylabel("y coordinate (m)", fontsize=7.4, labelpad=2)
    ax_c.tick_params(axis="both", labelsize=6.8, length=2.2, width=0.65)
    ax_c.grid(True)
    ax_c.spines["top"].set_visible(False)
    ax_c.spines["right"].set_visible(False)
    handles, labels = ax_c.get_legend_handles_labels()
    bottom.legend(
        handles,
        labels,
        frameon=False,
        loc="lower center",
        bbox_to_anchor=(0.52, 0.055),
        ncol=5,
        fontsize=7.0,
        handletextpad=0.28,
        columnspacing=1.10,
    )
    bottom.savefig(out / "fig1_locator_geometry_audit.png", bbox_inches="tight", pad_inches=0.03)
    plt.close(bottom)


def figure_workflow(out: Path) -> None:
    nodes = [
        ("1", "Plant audit", "public Dunhuang anchors\n11,915-coordinate pool", PALETTE["baseline_full"]),
        ("2", "Terrain audit", "SRTM90m elevation\nslope and envelope gates", "#64748B"),
        ("3", "TFPDA search", "bounded full-field\nsector/petal deformation", PALETTE["deform_0276"]),
        ("4", "Queue and screen", "geometry, proxy optics\nand flux-risk roles", PALETTE["default_flux"]),
        ("5", "Numerical checks", "SolarPILOT defaults\nPySolTrace direct aimpoints", PALETTE["direct"]),
    ]
    fig, ax = plt.subplots(figsize=(7.15, 3.15), dpi=360)
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    positions = [(0.10, 0.55), (0.30, 0.55), (0.50, 0.55), (0.70, 0.55), (0.90, 0.55)]
    band_y = 0.80
    band_labels = [
        (0.20, "audited inputs"),
        (0.50, "field-complete generation"),
        (0.80, "receiver-risk checks"),
    ]
    for x, label in band_labels:
        ax.text(
            x,
            band_y,
            label,
            ha="center",
            va="center",
            fontsize=6.8,
            color=PALETTE["muted"],
            bbox={"boxstyle": "round,pad=0.20,rounding_size=0.018", "facecolor": "#F8FAFC", "edgecolor": "#CBD5E1", "linewidth": 0.75},
        )

    for idx, (number, title, body, accent) in enumerate(nodes):
        x, y = positions[idx]
        ax.plot(
            [x - 0.068, x + 0.068],
            [y + 0.155, y + 0.155],
            color=accent,
            linewidth=2.2,
            solid_capstyle="round",
            zorder=3,
        )
        circ = plt.Circle((x, y + 0.095), 0.026, facecolor=accent, edgecolor="white", linewidth=0.8, zorder=4)
        ax.add_patch(circ)
        ax.text(x, y + 0.095, number, ha="center", va="center", fontsize=6.6, color="white", zorder=5)
        box = FancyBboxPatch(
            (x - 0.078, y - 0.117),
            0.156,
            0.245,
            boxstyle="round,pad=0.010,rounding_size=0.014",
            linewidth=0.85,
            edgecolor="#CBD5E1",
            facecolor="#F8FAFC",
        )
        ax.add_patch(box)
        ax.text(x, y + 0.020, title, ha="center", va="center", fontsize=7.35, color=PALETTE["ink"])
        ax.text(x, y - 0.062, body, ha="center", va="center", fontsize=5.95, color=PALETTE["muted"], linespacing=1.12)
        if idx < len(nodes) - 1:
            x1, y1 = positions[idx + 1]
            arrow = FancyArrowPatch(
                (x + 0.082, y),
                (x1 - 0.082, y1),
                arrowstyle="-|>",
                mutation_scale=9.5,
                linewidth=0.82,
                color="#64748B",
                connectionstyle="arc3,rad=0.0",
            )
            ax.add_patch(arrow)
    loop = FancyArrowPatch(
        (positions[-1][0] - 0.055, 0.260),
        (positions[3][0] + 0.050, 0.260),
        arrowstyle="-|>",
        mutation_scale=8.5,
        linewidth=0.74,
        color="#94A3B8",
        connectionstyle="arc3,rad=-0.22",
    )
    ax.add_patch(loop)
    ax.text(
        (positions[-1][0] + positions[3][0]) / 2,
        0.195,
        "direct checks can reorder the queue",
        ha="center",
        va="center",
        fontsize=6.4,
        color=PALETTE["muted"],
    )
    ax.text(
        0.5,
        0.935,
        "Plant-anchored full-field generation with receiver-flux-aware checks",
        ha="center",
        va="center",
        fontsize=9.2,
        color=PALETTE["ink"],
    )
    ax.text(
        0.5,
        0.060,
        "Claim boundary: reproducible benchmark and candidate queue, not a final commercial redesign.",
        ha="center",
        va="center",
        fontsize=7.1,
        color=PALETTE["muted"],
    )
    fig.savefig(out / "fig_journal_workflow_pipeline.png", bbox_inches="tight")
    plt.close(fig)


def figure_tradeoff(df: pd.DataFrame, out: Path) -> None:
    selected = df[df["layout_id"].isin(["baseline_full", "deform_0276", "deform_0893", "deform_1387", "deform_1822"])].copy()
    fig, ax = plt.subplots(figsize=(7.7, 5.1), dpi=260)
    ax.axhspan(0, selected["default_flux_delta_pct"].max() + 1.0, color="#FEF2F2", zorder=0, alpha=0.75)
    ax.axhspan(selected["default_flux_delta_pct"].min() - 1.0, 0, color="#F5F3FF", zorder=0, alpha=0.85)
    ax.axhline(0, color="#374151", linestyle="--", linewidth=0.8)
    ax.axvline(0, color="#374151", linestyle="--", linewidth=0.8)
    offsets = {
        "baseline_full": (10, -16),
        "deform_0276": (10, 8),
        "deform_0893": (10, -15),
        "deform_1387": (10, 7),
        "deform_1822": (-70, -16),
    }
    for row in selected.itertuples():
        color = PALETTE.get(row.layout_id, "#111827")
        ax.scatter(
            row.opteff_delta_pct,
            row.default_flux_delta_pct,
            s=118 if row.layout_id != "baseline_full" else 88,
            color=color,
            edgecolor="white",
            linewidth=0.8,
            zorder=3,
        )
        ax.annotate(
            f"{short_layout(row.layout_id)}\n{ROLE_LABELS[row.layout_id]}",
            (row.opteff_delta_pct, row.default_flux_delta_pct),
            xytext=offsets[row.layout_id],
            textcoords="offset points",
            ha="left",
            va="center",
            fontsize=7.7,
            color=PALETTE["ink"],
            bbox={"boxstyle": "round,pad=0.16", "facecolor": "white", "edgecolor": "#E5E7EB", "linewidth": 0.5, "alpha": 0.92},
            arrowprops={"arrowstyle": "-", "color": "#9CA3AF", "linewidth": 0.65},
        )
    ax.set_xlabel("Mean optical-efficiency change vs baseline (%)")
    ax.set_ylabel("Default peak/active-mean flux change vs baseline (%)")
    ax.set_title("SolarPILOT default aiming: optical gain and flux concentration diverge")
    ax.set_xlim(selected["opteff_delta_pct"].min() - 0.9, selected["opteff_delta_pct"].max() + 0.8)
    ax.set_ylim(selected["default_flux_delta_pct"].min() - 1.2, selected["default_flux_delta_pct"].max() + 1.0)
    ax.text(
        0.03,
        0.06,
        "lower half: lower default flux concentration",
        transform=ax.transAxes,
        fontsize=7.7,
        color=PALETTE["direct"],
    )
    ax.text(
        0.60,
        0.93,
        "optical gain can move with higher receiver concentration",
        transform=ax.transAxes,
        fontsize=7.7,
        color="#991B1B",
        ha="center",
        bbox={"boxstyle": "round,pad=0.18", "facecolor": "white", "edgecolor": "#FCA5A5", "linewidth": 0.5, "alpha": 0.9},
    )
    fig.tight_layout()
    fig.savefig(out / "fig_journal_tradeoff_clean.png", bbox_inches="tight")
    plt.close(fig)


def figure_dni(run: Path, out: Path) -> None:
    df = pd.read_csv(run / "weather_dni_sensitivity" / "tables" / "monthly_dni_sensitivity.csv")
    fig, ax = plt.subplots(figsize=(7.2, 3.85), dpi=260)
    x = np.arange(len(df))
    ax.bar(x, df["dni_kwh_m2"], color="#9ECAE1", edgecolor="#2B6C9C", linewidth=0.55, label="NASA POWER 2023")
    ax.plot(x, df["scaled_to_reported_tmy_kwh_m2"], color="#D55E00", marker="o", markersize=3.8, linewidth=1.45, label="scaled to reported TMY")
    ax.set_xticks(x)
    ax.set_xticklabels([str(int(v)) for v in df["Month"]])
    ax.set_xlabel("Month")
    ax.set_ylabel("Monthly DNI (kWh m$^{-2}$)")
    ax.set_title("Weather audit: public monthly DNI and reported-TMY scaling")
    ax.legend(frameon=False, ncol=2, loc="upper left")
    ax.text(
        0.98,
        0.10,
        "uniform scale factor = 1.022",
        transform=ax.transAxes,
        ha="right",
        va="center",
        fontsize=7.8,
        color=PALETTE["muted"],
        bbox={"boxstyle": "round,pad=0.18", "facecolor": "white", "edgecolor": "#E5E7EB", "linewidth": 0.5},
    )
    fig.tight_layout()
    fig.savefig(out / "monthly_dni_sensitivity.png", bbox_inches="tight")
    plt.close(fig)


def peak_flux_map(path: Path, bins: int = 24) -> np.ndarray:
    values = pd.read_csv(path, header=None).to_numpy(dtype=float)
    count = int(len(values) / bins)
    if count <= 0:
        return np.zeros((bins, bins), dtype=float)
    cube = values.reshape(count, bins, bins)
    return cube[int(cube.max(axis=(1, 2)).argmax())]


def figure_flux_panel(run: Path, out: Path) -> None:
    selected = ["baseline_full", "deform_0276", "deform_0893", "deform_1387", "deform_1822"]
    sp = pd.read_csv(run / "solarpilot_highres_key" / "tables" / "solarpilot_summary.csv").set_index("layout_id")
    maps = {
        layout_id: peak_flux_map(run / "solarpilot_highres_key" / "tables" / f"flux_table_{layout_id}.csv")
        for layout_id in selected
    }
    vmax = max(float(v.max()) for v in maps.values())
    spread = np.ptp(np.stack([maps[layout_id] for layout_id in selected], axis=0), axis=0)
    fig, axes = plt.subplots(2, 3, figsize=(9.7, 5.95), dpi=260)
    axes_flat = axes.ravel()
    for ax, layout_id, panel in zip(axes_flat[:5], selected, ["(a)", "(b)", "(c)", "(d)", "(e)"]):
        im = ax.imshow(maps[layout_id], origin="lower", cmap="YlOrRd", vmin=0.0, vmax=vmax, aspect="equal")
        metric = sp.loc[layout_id, "flux_peak_to_active_mean"]
        ax.set_title(f"{role_marker_label(layout_id)}\nP/M={metric:.3f}", fontsize=8.8, pad=6)
        ax.set_xlabel("receiver azimuth bin")
        if ax is axes_flat[0] or ax is axes_flat[3]:
            ax.set_ylabel("receiver height bin")
        else:
            ax.set_ylabel("")
        ax.set_xticks([0, 8, 16, 23])
        ax.set_yticks([0, 8, 16, 23])
        annotate_panel(ax, panel)
    im_spread = axes_flat[5].imshow(
        spread,
        origin="lower",
        cmap="YlOrRd",
        vmin=0.0,
        vmax=max(float(spread.max()), 1e-9),
        aspect="equal",
    )
    axes_flat[5].set_title("layout-induced spread\nmax--min across panels", fontsize=8.8, pad=6)
    axes_flat[5].set_xlabel("receiver azimuth bin")
    axes_flat[5].set_ylabel("")
    axes_flat[5].set_xticks([0, 8, 16, 23])
    axes_flat[5].set_yticks([0, 8, 16, 23])
    annotate_panel(axes_flat[5], "(f)")
    fig.subplots_adjust(left=0.07, right=0.88, bottom=0.098, top=0.835, wspace=0.28, hspace=0.47)
    cax = fig.add_axes([0.905, 0.38, 0.018, 0.38])
    cbar = fig.colorbar(im, cax=cax)
    cbar.set_label("flux-table value (panels a--e)")
    cax2 = fig.add_axes([0.905, 0.16, 0.018, 0.14])
    cbar2 = fig.colorbar(im_spread, cax=cax2)
    cbar2.set_label("spread (f)")
    fig.suptitle("Default-aiming receiver-flux snapshots under a common color scale", y=0.975)
    fig.savefig(out / "fig_journal_flux_peak_panel.png", bbox_inches="tight")
    plt.close(fig)


def load_layout(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, header=None, names=["x_m", "y_m", "z_m"])
    df["radius_m"] = np.hypot(df["x_m"], df["y_m"])
    df["azimuth_rad"] = np.arctan2(df["x_m"], df["y_m"])
    return df


def key_frame(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["_key"] = (
        out["x_m"].round(6).astype(str)
        + "|"
        + out["y_m"].round(6).astype(str)
        + "|"
        + out["z_m"].round(6).astype(str)
    )
    return out


def circular_delta(a: np.ndarray, b: float) -> np.ndarray:
    return np.angle(np.exp(1j * (a - b)))


def make_groups(features: pd.DataFrame, sectors: int = 48, annuli: int = 8) -> pd.DataFrame:
    df = features.copy()
    df["sector"] = pd.cut(df["azimuth_rad"], bins=np.linspace(-np.pi, np.pi, sectors + 1), labels=False, include_lowest=True)
    df["annulus"] = pd.cut(
        df["radius_m"],
        bins=np.linspace(df["radius_m"].min(), df["radius_m"].max(), annuli + 1),
        labels=False,
        include_lowest=True,
    )
    rows = []
    for (sector, annulus), grp in df.groupby(["sector", "annulus"], observed=True):
        weight = grp["optical_proxy"].to_numpy()
        if len(grp) == 0 or weight.sum() <= 0:
            continue
        angles = grp["azimuth_rad"].to_numpy()
        mean_angle = math.atan2(float(np.sum(np.sin(angles) * weight)), float(np.sum(np.cos(angles) * weight)))
        rows.append(
            {
                "sector": int(sector),
                "annulus": int(annulus),
                "power": float(weight.sum()),
                "theta": mean_angle,
                "radius_mean_m": float(np.average(grp["radius_m"], weights=weight)),
                "flux_risk": float(np.average(grp["flux_risk_raw"], weights=weight)),
            }
        )
    return pd.DataFrame(rows)


def offsets_for_strategy(groups: pd.DataFrame, strategy: str, receiver_height: float) -> pd.DataFrame:
    g = groups.copy()
    g["theta_offset"] = 0.0
    g["z_offset_m"] = 0.0
    if strategy == "equator":
        return g
    if strategy == "five_point":
        levels = np.array([-0.38, -0.19, 0.0, 0.19, 0.38]) * receiver_height
        g["z_offset_m"] = [levels[(int(row.sector) + int(row.annulus)) % len(levels)] for row in g.itertuples()]
        return g
    if strategy.startswith("staggered_levels"):
        _, level_text, amp_text, phase_text = strategy.split(":")
        levels = np.linspace(-float(amp_text) * receiver_height, float(amp_text) * receiver_height, int(level_text))
        phase = int(phase_text)
        g["z_offset_m"] = [levels[(int(row.sector) + int(row.annulus) + phase) % len(levels)] for row in g.itertuples()]
        return g
    raise ValueError(strategy)


def flux_map(
    groups: pd.DataFrame,
    receiver_height: float,
    theta_bins: int = 144,
    z_bins: int = 140,
    sigma_theta: float = 0.035,
    sigma_z_fraction: float = 0.065,
) -> tuple[np.ndarray, dict[str, float]]:
    theta_grid = np.linspace(-np.pi, np.pi, theta_bins, endpoint=False)
    z_grid = np.linspace(-receiver_height, receiver_height, z_bins)
    theta_mesh, z_mesh = np.meshgrid(theta_grid, z_grid)
    flux = np.zeros_like(theta_mesh, dtype=float)
    inside = np.abs(z_mesh) <= receiver_height / 2.0
    sigma_z = max(receiver_height * sigma_z_fraction, 0.8)
    total_power = 0.0
    inside_power = 0.0
    for row in groups.itertuples():
        kernel = np.exp(
            -0.5 * (circular_delta(theta_mesh, float(row.theta + row.theta_offset)) / sigma_theta) ** 2
            -0.5 * ((z_mesh - float(row.z_offset_m)) / sigma_z) ** 2
        )
        kernel_sum = float(kernel.sum())
        if kernel_sum <= 0:
            continue
        contribution = kernel / kernel_sum * float(row.power)
        flux += contribution
        total_power += float(row.power)
        inside_power += float(contribution[inside].sum())
    inside_flux = flux[inside]
    active = inside_flux[inside_flux > np.percentile(inside_flux, 55)]
    mean_active = float(active.mean()) if len(active) else float(inside_flux.mean())
    return flux, {
        "intercept_fraction_proxy": inside_power / max(total_power, 1e-12),
        "peak_to_mean_proxy": float(inside_flux.max() / max(mean_active, 1e-12)),
        "cv_active_proxy": float(active.std() / max(active.mean(), 1e-12)) if len(active) else 0.0,
    }


def features_for_layout(layout: pd.DataFrame, all_features: pd.DataFrame | None, config: dict) -> pd.DataFrame:
    if all_features is not None:
        features = key_frame(all_features)
        layout_keys = key_frame(layout)["_key"]
        subset = features[features["_key"].isin(set(layout_keys))].copy()
        if len(subset) >= int(0.95 * len(layout)):
            return subset
    eval_config = json.loads(json.dumps(config))
    eval_config["solar_sampling"] = {
        **config["solar_sampling"],
        "day_step": max(9, int(config["solar_sampling"]["day_step"])),
        "hours": [8, 9, 10, 11, 12, 13, 14, 15, 16],
    }
    return compute_heliostat_features(layout, eval_config["plant"], eval_config["solar_sampling"])


def figure_aiming_proxy(run: Path, out: Path) -> None:
    config = load_json(ROOT / "configs" / "server_full.json")
    layout_id = "deform_0893"
    layout = load_layout(run / "layouts" / f"{layout_id}.csv")
    features_path = run / "heliostat_features.csv"
    all_features = pd.read_csv(features_path) if features_path.exists() else None
    groups = make_groups(features_for_layout(layout, all_features, config))
    receiver_height = float(config["plant"]["receiver_height_m"])
    strategies = ["equator", "five_point", "staggered_levels:9:0.380:2"]
    maps: dict[str, np.ndarray] = {}
    metrics: dict[str, dict[str, float]] = {}
    for strategy in strategies:
        fmap, met = flux_map(offsets_for_strategy(groups, strategy, receiver_height), receiver_height)
        maps[strategy] = fmap
        metrics[strategy] = met
    vmax = max(float(v.max()) for v in maps.values())
    fig, axes = plt.subplots(1, 3, figsize=(10.8, 3.95), dpi=260)
    for ax, strategy, panel in zip(axes, strategies, ["(a)", "(b)", "(c)"]):
        im = ax.imshow(maps[strategy], origin="lower", aspect="auto", cmap="YlOrRd", vmin=0.0, vmax=vmax)
        ax.axhline(maps[strategy].shape[0] * 0.25, color="#374151", linewidth=0.7, linestyle="--", alpha=0.6)
        ax.axhline(maps[strategy].shape[0] * 0.75, color="#374151", linewidth=0.7, linestyle="--", alpha=0.6)
        met = metrics[strategy]
        ax.set_title(
            f"{clean_strategy(strategy)}\nP/M={met['peak_to_mean_proxy']:.2f}, intercept={met['intercept_fraction_proxy']:.3f}",
            fontsize=8.8,
            pad=6,
        )
        ax.set_xlabel("receiver azimuth bin")
        ax.set_ylabel("vertical bin")
        annotate_panel(ax, panel)
    for idx, ax in enumerate(axes):
        if idx > 0:
            ax.set_ylabel("")
    fig.subplots_adjust(left=0.055, right=0.91, bottom=0.16, top=0.76, wspace=0.30)
    cax = fig.add_axes([0.93, 0.19, 0.014, 0.55])
    cbar = fig.colorbar(im, cax=cax)
    cbar.set_label("proxy flux intensity (common scale)")
    fig.suptitle(r"Receiver-aiming proxy for $L_{nom}$ under comparable maps", y=0.96)
    fig.savefig(out / "aiming_flux_deform_0893.png", bbox_inches="tight")
    plt.close(fig)


def figure_aiming_sensitivity(run: Path, out: Path) -> None:
    df = pd.read_csv(run / "aiming_sensitivity" / "tables" / "aiming_sensitivity_summary.csv").copy()
    df = df.sort_values("median_delta_peak_to_mean_pct")
    y = np.arange(len(df))
    fig, ax = plt.subplots(figsize=(6.9, 3.8), dpi=240)
    xerr = np.vstack(
        [
            df["median_delta_peak_to_mean_pct"] - df["p10_delta_peak_to_mean_pct"],
            df["p90_delta_peak_to_mean_pct"] - df["median_delta_peak_to_mean_pct"],
        ]
    )
    colors = [PALETTE.get(row.layout_id, "#374151") for row in df.itertuples()]
    ax.errorbar(
        df["median_delta_peak_to_mean_pct"],
        y,
        xerr=xerr,
        fmt="o",
        color=PALETTE["ink"],
        ecolor="#9CA3AF",
        elinewidth=1.1,
        capsize=3,
        markersize=0,
        zorder=2,
    )
    ax.scatter(df["median_delta_peak_to_mean_pct"], y, s=70, color=colors, edgecolor="white", linewidth=0.8, zorder=3)
    ax.axvline(0, color="#374151", linestyle="--", linewidth=0.8)
    ax.set_yticks(y)
    ax.set_yticklabels([short_layout(v) for v in df["layout_id"]])
    ax.set_xlabel("Best proxy peak/mean change vs paired baseline (%)")
    ax.set_title("Aiming-proxy sensitivity across 81 grouping, spot-width, and phase assumptions")
    for i, row in enumerate(df.itertuples()):
        ax.text(
            row.p90_delta_peak_to_mean_pct + 0.35,
            i,
            f"improved {row.improved_peak_to_mean_fraction:.0%}",
            va="center",
            fontsize=7.2,
            color=PALETTE["muted"],
        )
    fig.tight_layout()
    fig.savefig(out / "aiming_sensitivity_boxplot.png", bbox_inches="tight")
    plt.close(fig)


def figure_soltrace(matrix: Path, out: Path) -> None:
    proxy = pd.read_csv(matrix / "tables" / "soltrace_proxy_strategy_summary.csv")
    summary = pd.read_csv(matrix / "tables" / "soltrace_sensitivity_summary.csv")
    rel = pd.read_csv(matrix / "tables" / "soltrace_sensitivity_relative.csv")
    all_df = pd.read_csv(matrix / "tables" / "soltrace_sensitivity_all.csv")
    proxy = proxy.sort_values("mean_delta_peak_pct")
    best = (
        summary[summary["layout_id"] != "baseline_full"]
        .sort_values("mean_delta_peak_pct")
        .groupby("layout_id", as_index=False)
        .head(1)
        .sort_values("mean_delta_peak_pct")
    )

    fig = plt.figure(figsize=(12.2, 8.35), dpi=260)
    gs = fig.add_gridspec(2, 3, height_ratios=[0.88, 1.55], width_ratios=[1.0, 1.0, 0.72], hspace=0.36, wspace=0.34)
    ax0 = fig.add_subplot(gs[0, 0])
    ax1 = fig.add_subplot(gs[0, 1])
    ax2 = fig.add_subplot(gs[0, 2])
    ax3 = fig.add_subplot(gs[1, :])

    def bar_panel(ax, frame: pd.DataFrame, strategy_col: str, title: str, panel: str) -> None:
        labels = [f"{short_layout(row.layout_id)}\n{clean_strategy(getattr(row, strategy_col))}" for row in frame.itertuples()]
        y = np.arange(len(frame))
        values = frame["mean_delta_peak_pct"].to_numpy(dtype=float)
        colors = [PALETTE["deform_0276"] if v < 0 else PALETTE["default_flux"] for v in values]
        ax.barh(y, values, color=colors, alpha=0.88)
        ax.axvline(0, color="#374151", linestyle="--", linewidth=0.75)
        ax.set_yticks(y)
        ax.set_yticklabels(labels)
        ax.invert_yaxis()
        ax.set_xlabel("Mean P/M change (%)")
        ax.set_title(title)
        annotate_panel(ax, panel)

    bar_panel(ax0, proxy, "proxy_best_strategy", "Proxy-best staggered strategy", "(a)")
    bar_panel(ax1, best, "strategy", "Best explicit strategy in direct matrix", "(b)")

    intercept_values = all_df["receiver_intercept_per_requested_ray"].to_numpy(dtype=float)
    ax2.boxplot(
        intercept_values,
        vert=False,
        widths=0.42,
        patch_artist=True,
        boxprops={"facecolor": "#F5F3FF", "edgecolor": PALETTE["direct"], "linewidth": 0.9},
        medianprops={"color": PALETTE["direct"], "linewidth": 1.3},
        whiskerprops={"color": PALETTE["direct"], "linewidth": 0.9},
        capprops={"color": PALETTE["direct"], "linewidth": 0.9},
        flierprops={
            "marker": ".",
            "markersize": 2,
            "markerfacecolor": PALETTE["direct"],
            "markeredgecolor": PALETTE["direct"],
            "alpha": 0.35,
        },
    )
    ax2.set_yticks([])
    ax2.set_xlim(0.60, 0.78)
    ax2.set_xlabel("receiver hits / requested rays")
    ax2.set_title("Stage-order sanity check")
    annotate_panel(ax2, "(c)")

    pairs: list[tuple[str, str, str]] = []
    for row in proxy.itertuples():
        pairs.append((row.layout_id, row.proxy_best_strategy, "proxy"))
    for row in best.itertuples():
        pair = (row.layout_id, row.strategy, "best")
        if not any(row.layout_id == a and row.strategy == b for a, b, _ in pairs):
            pairs.append(pair)

    heat_rows = []
    for layout_id, strategy, role in pairs:
        subset = rel[(rel["layout_id"] == layout_id) & (rel["strategy"] == strategy)].copy()
        subset["row_label"] = f"{short_layout(layout_id)} {role} {clean_strategy(strategy)}"
        subset["condition"] = "d" + subset["sun_day"].astype(int).astype(str) + " h" + subset["sun_hour"].astype(int).astype(str)
        heat_rows.append(subset)
    heat_df = pd.concat(heat_rows, ignore_index=True)
    heat = heat_df.pivot_table(
        index="row_label",
        columns="condition",
        values="delta_peak_to_active_mean_pct_vs_baseline_same_strategy",
        aggfunc="mean",
    )
    heat = heat.loc[[f"{short_layout(a)} {c} {clean_strategy(b)}" for a, b, c in pairs]]
    vmax = max(8.0, float(np.nanpercentile(np.abs(heat.to_numpy(dtype=float)), 95)))
    norm = TwoSlopeNorm(vmin=-vmax, vcenter=0.0, vmax=vmax)
    im = ax3.imshow(heat.to_numpy(dtype=float), aspect="auto", cmap="RdBu_r", norm=norm)
    ax3.set_yticks(np.arange(len(heat.index)))
    ax3.set_yticklabels(heat.index, fontsize=7.5)
    ax3.set_xticks(np.arange(len(heat.columns)))
    ax3.set_xticklabels(heat.columns, fontsize=7.3)
    ax3.set_title("Condition-level paired changes for selected direct-aiming strategies")
    for i in range(heat.shape[0]):
        for j in range(heat.shape[1]):
            value = heat.iloc[i, j]
            if np.isfinite(value):
                color = "white" if abs(value) > 0.68 * vmax else PALETTE["ink"]
                ax3.text(j, i, f"{value:+.1f}", ha="center", va="center", fontsize=6.8, color=color)
    cbar = fig.colorbar(im, ax=ax3, fraction=0.018, pad=0.012)
    cbar.set_label("P/M change vs paired baseline (%)")
    annotate_panel(ax3, "(d)")

    fig.suptitle("Reduced PySolTrace direct-aiming checks with verified stage ordering", y=0.99)
    fig.savefig(out / "fig_soltrace_corrected_stage_order_panel.png", bbox_inches="tight")
    plt.close(fig)


def figure_graphical_abstract(run: Path, out: Path) -> None:
    import importlib.util

    script = ROOT / "scripts" / "build_graphical_abstract.py"
    spec = importlib.util.spec_from_file_location("build_graphical_abstract", script)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load graphical abstract builder: {script}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    old_argv = sys.argv[:]
    try:
        sys.argv = [
            str(script),
            "--run",
            str(run),
            "--out",
            str(out / "graphical_abstract.png"),
        ]
        module.main()
    finally:
        sys.argv = old_argv


def write_style_note(package: Path) -> None:
    note = package / "FIGURE_STYLE_GUIDE.md"
    note.write_text(
        "\n".join(
            [
                "# Figure Style Guide",
                "",
                "- Manuscript figures use a white background, Times New Roman/Times-first serif font fallback, and a consistent blue/orange/purple accent system.",
                "- TikZ figures inherit the manuscript Times-style `elsarticle` font; PingFang is not used in active manuscript figures.",
                "- Finished figure lettering should stay near Elsevier's legibility rule of thumb: about 7 pt for normal text and not below 6 pt for subscripts/superscripts.",
                "- Blue denotes optical or layout-generation evidence, orange denotes default receiver-flux concentration, and purple denotes direct aimpoint checks; cyan-blue is reserved for the robust receiver-risk layout role.",
                "- Figure-internal text uses normal weight by default; bold is reserved for LaTeX figure labels/captions rather than embedded annotations.",
                "- Heatmaps use white-page backgrounds; intensity maps use light-to-warm scales so low values are light rather than black.",
                "- Figure 8 is intentionally restricted to proxy-best and best-explicit direct-aiming rows, with short labels and enlarged heatmap cells, to avoid the compressed all-strategy heatmap problem.",
                "- Figure 1 uses the Zengye Su/DJI Mavic 3 Pro aerial photograph at its original full-frame aspect ratio, followed by a China-wide projected locator and a separate coordinate geometry audit.",
                "- Figure 5 uses a six-panel white-background warm heatmap design: five comparable SolarPILOT flux maps plus one layout-induced spread audit panel.",
                "- Dark editorial graphics are not used in the manuscript draft; the graphical abstract is regenerated as a white-background, photo-led figure with a compact evidence chain and blue/orange/purple checking bands.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> int:
    args = parse_args()
    run = args.run if args.run.is_absolute() else ROOT / args.run
    matrix = args.matrix if args.matrix.is_absolute() else ROOT / args.matrix
    package = args.package if args.package.is_absolute() else ROOT / args.package
    out = package / "latex" / "figures"
    submission = package / "submission_materials"
    out.mkdir(parents=True, exist_ok=True)
    submission.mkdir(parents=True, exist_ok=True)

    set_style()
    summary = load_summary(run)
    figure_layout_panel(run, out)
    figure_workflow(out)
    figure_tradeoff(summary, out)
    figure_dni(run, out)
    figure_flux_panel(run, out)
    figure_aiming_proxy(run, out)
    figure_aiming_sensitivity(run, out)
    figure_soltrace(matrix, out)
    figure_graphical_abstract(run, submission)
    write_style_note(package)
    print(f"Wrote white-background journal figures to {out}")
    print(f"Wrote white-background graphical abstract to {submission / 'graphical_abstract.png'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
