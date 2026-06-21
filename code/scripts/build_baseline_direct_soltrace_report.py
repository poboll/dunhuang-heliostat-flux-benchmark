#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN = ROOT / "server_outputs" / "baseline_strengthening_20260522"
DEFAULT_DIRECT = DEFAULT_RUN / "soltrace_baseline_controls_direct_27cond_20260523"
DEFAULT_OUT = DEFAULT_DIRECT / "analysis"

ROLE_META = {
    "baseline_full": ("$L_0$", "reference", "reference"),
    "ctrl_radial_compact_015": ("$C_{rad-}$", "same-condition control", "control"),
    "ctrl_radial_expand_015": ("$C_{rad+}$", "same-condition control", "control"),
    "ctrl_ring_wave_012": ("$C_{wave}$", "same-condition control", "control"),
    "deform_0276": ("$L_{opt}$", "TS-FPDA optical-upper", "tsfpda"),
    "deform_0893": ("$L_{nom}$", "TS-FPDA nominal-proxy", "tsfpda"),
    "deform_1387": ("$L_{rob}$", "TS-FPDA receiver-risk", "tsfpda"),
    "deform_1822": ("$L_{ctrl}$", "TS-FPDA default-flux-control", "tsfpda"),
}

LAYOUT_ORDER = [
    "ctrl_radial_compact_015",
    "ctrl_radial_expand_015",
    "ctrl_ring_wave_012",
    "deform_0276",
    "deform_0893",
    "deform_1387",
    "deform_1822",
]

PALETTE = {
    "control": "#B7791F",
    "tsfpda": "#2563EB",
    "reference": "#64748B",
    "ink": "#111827",
    "grid": "#CBD5E1",
    "negative": "#2166AC",
    "positive": "#B2182B",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build manuscript-facing summaries for the baseline-control reduced PySolTrace direct matrix."
    )
    parser.add_argument("--run", type=Path, default=DEFAULT_RUN)
    parser.add_argument("--direct", type=Path, default=DEFAULT_DIRECT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--bootstrap", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=20260523)
    return parser.parse_args()


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def short_strategy(value: str) -> str:
    return (
        str(value)
        .replace("staggered_levels:9:0.380:", "S9-p")
        .replace("visible_equator", "visible")
        .replace("five_point", "five-point")
    )


def label_for(layout_id: str) -> str:
    return ROLE_META.get(layout_id, (layout_id, "", ""))[0]


def role_for(layout_id: str) -> str:
    return ROLE_META.get(layout_id, ("", layout_id, ""))[1]


def family_for(layout_id: str) -> str:
    return ROLE_META.get(layout_id, ("", "", "other"))[2]


def load_inputs(run: Path, direct: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    summary_path = direct / "tables" / "soltrace_sensitivity_summary.csv"
    relative_path = direct / "tables" / "soltrace_sensitivity_relative.csv"
    proxy_path = direct / "tables" / "soltrace_proxy_strategy_summary.csv"
    integrated_path = run / "tables" / "baseline_comparison_integrated.csv"
    missing = [p for p in [summary_path, relative_path, proxy_path, integrated_path] if not p.exists()]
    if missing:
        raise FileNotFoundError("Missing required tables:\n" + "\n".join(str(p) for p in missing))
    return (
        pd.read_csv(summary_path),
        pd.read_csv(relative_path),
        pd.read_csv(proxy_path),
        pd.read_csv(integrated_path),
    )


def build_best_rows(summary: pd.DataFrame) -> pd.DataFrame:
    best = (
        summary[summary["layout_id"].isin(LAYOUT_ORDER)]
        .sort_values(["layout_id", "mean_delta_peak_pct", "median_delta_peak_pct"])
        .groupby("layout_id", as_index=False)
        .head(1)
        .copy()
    )
    best["label"] = best["layout_id"].map(label_for)
    best["role"] = best["layout_id"].map(role_for)
    best["family"] = best["layout_id"].map(family_for)
    best["strategy_short"] = best["strategy"].map(short_strategy)
    best["order"] = best["layout_id"].map({layout: i for i, layout in enumerate(LAYOUT_ORDER)})
    return best.sort_values("order").drop(columns=["order"])


def build_proxy_rows(proxy: pd.DataFrame) -> pd.DataFrame:
    out = proxy[proxy["layout_id"].isin(LAYOUT_ORDER)].copy()
    out["label"] = out["layout_id"].map(label_for)
    out["role"] = out["layout_id"].map(role_for)
    out["family"] = out["layout_id"].map(family_for)
    out["strategy_short"] = out["proxy_best_strategy"].map(short_strategy)
    out["order"] = out["layout_id"].map({layout: i for i, layout in enumerate(LAYOUT_ORDER)})
    return out.sort_values("order").drop(columns=["order"])


def bootstrap_rows(
    relative: pd.DataFrame,
    best: pd.DataFrame,
    proxy_rows: pd.DataFrame,
    replicates: int,
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    wanted = []
    for _, row in best.iterrows():
        wanted.append((row["layout_id"], row["strategy"], "best-direct"))
    for _, row in proxy_rows.iterrows():
        wanted.append((row["layout_id"], row["proxy_best_strategy"], "proxy-selected"))

    records = []
    for layout_id, strategy, view in wanted:
        sub = relative[(relative["layout_id"] == layout_id) & (relative["strategy"] == strategy)].copy()
        values = sub["delta_peak_to_active_mean_pct_vs_baseline_same_strategy"].dropna().to_numpy(dtype=float)
        if len(values) == 0:
            continue
        boot = rng.choice(values, size=(replicates, len(values)), replace=True).mean(axis=1)
        records.append(
            {
                "layout_id": layout_id,
                "label": label_for(layout_id),
                "role": role_for(layout_id),
                "family": family_for(layout_id),
                "view": view,
                "strategy": strategy,
                "strategy_short": short_strategy(strategy),
                "cases": int(len(values)),
                "mean_delta_peak_pct": float(values.mean()),
                "median_delta_peak_pct": float(np.median(values)),
                "ci95_low_pct": float(np.percentile(boot, 2.5)),
                "ci95_high_pct": float(np.percentile(boot, 97.5)),
                "share_lower_peak": float((values < 0).mean()),
                "p10_delta_peak_pct": float(np.percentile(values, 10)),
                "p90_delta_peak_pct": float(np.percentile(values, 90)),
            }
        )
    out = pd.DataFrame.from_records(records)
    out["order"] = out["layout_id"].map({layout: i for i, layout in enumerate(LAYOUT_ORDER)})
    return out.sort_values(["view", "order"]).drop(columns=["order"])


def family_stats(best: pd.DataFrame, proxy_rows: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for view, df, mean_col in [
        ("best-direct", best, "mean_delta_peak_pct"),
        ("proxy-selected", proxy_rows, "mean_delta_peak_pct"),
    ]:
        for family in ["control", "tsfpda"]:
            sub = df[df["family"] == family].copy()
            if sub.empty:
                continue
            rows.append(
                {
                    "view": view,
                    "family": family,
                    "layout_count": int(sub["layout_id"].nunique()),
                    "best_layout": sub.sort_values(mean_col).iloc[0]["layout_id"],
                    "best_mean_delta_peak_pct": float(sub[mean_col].min()),
                    "median_of_layout_means_pct": float(sub[mean_col].median()),
                    "all_negative_mean_rows": bool((sub[mean_col] < 0).all()),
                }
            )
    return pd.DataFrame.from_records(rows)


def join_with_prior(best: pd.DataFrame, integrated: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "layout_id",
        "role",
        "family",
        "delta_opteff_pct",
        "delta_default_flux_ratio_pct",
        "delta_aiming_proxy_pct",
    ]
    prior = integrated.loc[:, [c for c in cols if c in integrated.columns]].copy()
    merged = best.merge(
        prior.drop(columns=["role", "family"], errors="ignore"),
        on="layout_id",
        how="left",
    )
    return merged


def set_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
            "font.weight": "normal",
            "font.size": 8.4,
            "axes.titlesize": 9.0,
            "axes.titleweight": "normal",
            "axes.labelsize": 8.2,
            "xtick.labelsize": 7.4,
            "ytick.labelsize": 7.4,
            "legend.fontsize": 7.2,
            "figure.titlesize": 10.2,
            "axes.facecolor": "white",
            "figure.facecolor": "white",
            "savefig.facecolor": "white",
            "axes.edgecolor": "#334155",
            "axes.linewidth": 0.7,
            "axes.grid": True,
            "grid.color": PALETTE["grid"],
            "grid.alpha": 0.60,
            "grid.linewidth": 0.55,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def make_figure(best: pd.DataFrame, proxy_rows: pd.DataFrame, bootstrap: pd.DataFrame, relative: pd.DataFrame, out: Path) -> None:
    set_style()
    fig = plt.figure(figsize=(7.35, 5.80), dpi=360)
    gs = fig.add_gridspec(
        2,
        2,
        height_ratios=[0.98, 1.08],
        width_ratios=[1.02, 0.98],
        left=0.10,
        right=0.985,
        top=0.93,
        bottom=0.125,
        hspace=0.52,
        wspace=0.30,
    )
    ax0 = fig.add_subplot(gs[0, 0])
    ax1 = fig.add_subplot(gs[0, 1])
    ax2 = fig.add_subplot(gs[1, :])

    for ax, df, title, col, xlim in [
        (ax0, best, "(a) Best direct row", "mean_delta_peak_pct", (-4.25, 0.80)),
        (ax1, proxy_rows, "(b) Proxy-selected row", "mean_delta_peak_pct", (-1.75, 2.70)),
    ]:
        labels = df["label"].tolist()
        y = np.arange(len(df))
        colors = [PALETTE[family] for family in df["family"]]
        ax.barh(y, df[col], color=colors, alpha=0.88, height=0.58)
        ax.axvline(0.0, color=PALETTE["ink"], linewidth=0.8)
        ax.set_yticks(y)
        ax.set_yticklabels(labels)
        ax.invert_yaxis()
        ax.set_xlabel("Mean peak / active-mean change (%)")
        ax.set_title(title, loc="left", pad=6)
        ax.set_xlim(*xlim)
        for yi, (_, row) in enumerate(df.iterrows()):
            value = float(row[col])
            strategy = row.get("strategy_short", "")
            x_text = -0.10 if value < 0 else 0.10
            ha = "right" if value < 0 else "left"
            label = f"{value:+.1f}%  {strategy}"
            ax.text(
                x_text,
                yi,
                label,
                va="center",
                ha=ha,
                fontsize=6.7,
                color=PALETTE["ink"],
                bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.72, "pad": 0.6},
            )

    best_keys = set(zip(best["layout_id"], best["strategy"], strict=False))
    rel = relative[
        relative.apply(lambda r: (r["layout_id"], r["strategy"]) in best_keys, axis=1)
    ].copy()
    rel = rel[rel["layout_id"].isin(LAYOUT_ORDER)]
    plot_rows = []
    for layout in LAYOUT_ORDER:
        sub = rel[rel["layout_id"] == layout]
        for value in sub["delta_peak_to_active_mean_pct_vs_baseline_same_strategy"].dropna():
            plot_rows.append({"layout_id": layout, "label": label_for(layout), "value": float(value), "family": family_for(layout)})
    plot = pd.DataFrame.from_records(plot_rows)
    rng = np.random.default_rng(20260523)
    for pos, layout in enumerate(LAYOUT_ORDER):
        values = plot.loc[plot["layout_id"] == layout, "value"].to_numpy(dtype=float)
        if len(values) == 0:
            continue
        ax2.boxplot(
            values,
            positions=[pos],
            widths=0.50,
            patch_artist=True,
            showfliers=False,
            boxprops={"facecolor": "#E2E8F0", "edgecolor": "#475569", "linewidth": 0.8},
            medianprops={"color": PALETTE[family_for(layout)], "linewidth": 1.35},
            whiskerprops={"color": "#64748B", "linewidth": 0.8},
            capprops={"color": "#64748B", "linewidth": 0.8},
        )
        jitter = rng.normal(0.0, 0.040, size=len(values))
        colors = np.where(values < 0, PALETTE["negative"], PALETTE["positive"])
        ax2.scatter(np.full(len(values), pos) + jitter, values, s=13, color=colors, alpha=0.78, edgecolor="white", linewidth=0.25)
    ax2.axhline(0.0, color=PALETTE["ink"], linewidth=0.8, linestyle="--")
    ax2.set_xticks(np.arange(len(LAYOUT_ORDER)))
    ax2.set_xticklabels([label_for(layout) for layout in LAYOUT_ORDER])
    ax2.set_ylabel("Condition-level best-row change (%)")
    ax2.set_title("(c) Condition-level spread for each best direct row", loc="left", pad=6)
    ax2.set_xlabel("Layout role; gold = simple control, blue = TS-FPDA representative")

    handles = [
        plt.Line2D([0], [0], color=PALETTE["control"], lw=6, label="same-condition control"),
        plt.Line2D([0], [0], color=PALETTE["tsfpda"], lw=6, label="TS-FPDA representative"),
    ]
    fig.legend(handles=handles, frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(0.55, 0.99))
    fig.savefig(out / "figures" / "fig_baseline_direct_soltrace_controls.png", bbox_inches="tight")
    fig.savefig(out / "figures" / "fig_baseline_direct_soltrace_controls.pdf", bbox_inches="tight")
    plt.close(fig)


def markdown_table(df: pd.DataFrame, floatfmt: str = ".3f") -> str:
    if df.empty:
        return "_No rows available._"
    lines = ["| " + " | ".join(df.columns) + " |", "| " + " | ".join(["---"] * len(df.columns)) + " |"]
    for row in df.itertuples(index=False):
        cells = []
        for value in row:
            if isinstance(value, (float, np.floating)):
                cells.append(format(float(value), floatfmt))
            else:
                cells.append(str(value))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def write_report(
    run: Path,
    direct: Path,
    best_joined: pd.DataFrame,
    proxy_rows: pd.DataFrame,
    family_summary: pd.DataFrame,
    boot: pd.DataFrame,
    out: Path,
) -> None:
    best_display = best_joined[
        [
            "label",
            "role",
            "family",
            "strategy_short",
            "cases",
            "mean_delta_peak_pct",
            "median_delta_peak_pct",
            "share_lower_peak",
            "median_delta_intercept_pctpt",
            "delta_opteff_pct",
            "delta_default_flux_ratio_pct",
            "delta_aiming_proxy_pct",
        ]
    ].copy()
    proxy_display = proxy_rows[
        [
            "label",
            "role",
            "family",
            "strategy_short",
            "cases",
            "mean_delta_peak_pct",
            "median_delta_peak_pct",
            "share_lower_peak",
        ]
    ].copy()
    ci_display = boot[
        [
            "label",
            "role",
            "family",
            "view",
            "strategy_short",
            "mean_delta_peak_pct",
            "ci95_low_pct",
            "ci95_high_pct",
            "share_lower_peak",
        ]
    ].copy()
    lines = [
        "# Baseline-Control Reduced PySolTrace Direct Audit",
        "",
        "This audit compares low-complexity same-condition controls with TS-FPDA representatives under the same reduced PySolTrace direct-ray settings. It is intended to test whether the baseline controls explain the receiver-risk queue, not to certify a final plant redesign.",
        "",
        f"- Source run: `{run}`",
        f"- Direct matrix: `{direct}`",
        "- Scope: baseline plus selected simple controls and TS-FPDA representatives; 27 representative solar conditions; visible-equator, five-point, and proxy-union S9 strategies.",
        "- Interpretation: negative peak-to-active-mean change means lower receiver concentration than the paired baseline under the same condition and aiming strategy.",
        "",
        "## Best Direct Rows",
        "",
        markdown_table(best_display),
        "",
        "## Proxy-Selected Rows",
        "",
        markdown_table(proxy_display),
        "",
        "## Family-Level Summary",
        "",
        markdown_table(family_summary),
        "",
        "## Bootstrap Confidence Audit",
        "",
        markdown_table(ci_display),
        "",
        "## Manuscript Interpretation",
        "",
        "- Simple controls remain meaningful and should not be hidden. They are part of the evidence boundary.",
        "- A result is manuscript-worthy only if it improves the direct-check queue or clarifies why TS-FPDA should be described as a benchmark generator rather than a globally superior optimizer.",
        "- Do not use this audit as full-field annual certification: the same reduced-check limitations remain.",
        "",
    ]
    (out / "BASELINE_DIRECT_SOLTRACE_AUDIT.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    run = resolve(args.run)
    direct = resolve(args.direct)
    out = resolve(args.out)
    (out / "tables").mkdir(parents=True, exist_ok=True)
    (out / "figures").mkdir(parents=True, exist_ok=True)

    summary, relative, proxy, integrated = load_inputs(run, direct)
    best = build_best_rows(summary)
    proxy_rows = build_proxy_rows(proxy)
    boot = bootstrap_rows(relative, best, proxy_rows, args.bootstrap, args.seed)
    fam = family_stats(best, proxy_rows)
    best_joined = join_with_prior(best, integrated)

    best.to_csv(out / "tables" / "baseline_direct_best_rows.csv", index=False)
    proxy_rows.to_csv(out / "tables" / "baseline_direct_proxy_selected_rows.csv", index=False)
    boot.to_csv(out / "tables" / "baseline_direct_bootstrap_ci.csv", index=False)
    fam.to_csv(out / "tables" / "baseline_direct_family_summary.csv", index=False)
    best_joined.to_csv(out / "tables" / "baseline_direct_best_rows_with_prior.csv", index=False)

    make_figure(best, proxy_rows, boot, relative, out)
    write_report(run, direct, best_joined, proxy_rows, fam, boot, out)
    print(f"Wrote baseline direct SolTrace audit to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
