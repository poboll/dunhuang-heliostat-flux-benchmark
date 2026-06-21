#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DIRECT = (
    ROOT
    / "server_outputs"
    / "baseline_strengthening_20260522"
    / "soltrace_baseline_controls_direct_27cond_20260523"
)
DEFAULT_OUT = DEFAULT_DIRECT / "analysis"

DELTA_COL = "delta_peak_to_active_mean_pct_vs_baseline_same_strategy"

ROLE_META = {
    "ctrl_radial_compact_015": ("$C_{rad-}$", "C_rad-", "control"),
    "ctrl_radial_expand_015": ("$C_{rad+}$", "C_rad+", "control"),
    "ctrl_ring_wave_012": ("$C_{wave}$", "C_wave", "control"),
    "deform_0276": ("$L_{opt}$", "L_opt", "tsfpda"),
    "deform_0893": ("$L_{nom}$", "L_nom", "tsfpda"),
    "deform_1387": ("$L_{rob}$", "L_rob", "tsfpda"),
    "deform_1822": ("$L_{ctrl}$", "L_ctrl", "tsfpda"),
}

LAYOUT_ORDER = list(ROLE_META)
PALETTE = {
    "control": "#B7791F",
    "tsfpda": "#2563EB",
    "ink": "#111827",
    "grid": "#CBD5E1",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build a leave-one-day-out strategy-selection audit for the baseline-control "
            "reduced PySolTrace direct matrix."
        )
    )
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
    return ROLE_META[layout_id][0]


def text_label_for(layout_id: str) -> str:
    return ROLE_META[layout_id][1]


def family_for(layout_id: str) -> str:
    return ROLE_META[layout_id][2]


def set_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
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
            "grid.alpha": 0.62,
            "grid.linewidth": 0.55,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def bootstrap_ci(values: np.ndarray, replicates: int, rng: np.random.Generator) -> tuple[float, float]:
    if len(values) == 0:
        return float("nan"), float("nan")
    boot = rng.choice(values, size=(replicates, len(values)), replace=True).mean(axis=1)
    return float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))


def build_holdout(relative: pd.DataFrame, replicates: int, seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    days = sorted(relative["sun_day"].unique())
    daily_records: list[dict[str, object]] = []

    for layout_id in LAYOUT_ORDER:
        layout_df = relative[relative["layout_id"] == layout_id].copy()
        for held_day in days:
            train = layout_df[layout_df["sun_day"] != held_day].copy()
            test_pool = layout_df[layout_df["sun_day"] == held_day].copy()
            train_by_strategy = (
                train.groupby("strategy", as_index=False)
                .agg(
                    train_mean_delta_pct=(DELTA_COL, "mean"),
                    train_median_delta_pct=(DELTA_COL, "median"),
                    train_lower_frac=(DELTA_COL, lambda s: float((s < 0).mean())),
                )
                .sort_values(["train_mean_delta_pct", "train_median_delta_pct", "strategy"])
            )
            selected = str(train_by_strategy.iloc[0]["strategy"])
            test = test_pool[test_pool["strategy"] == selected].copy()
            values = test[DELTA_COL].to_numpy(dtype=float)
            daily_records.append(
                {
                    "layout_id": layout_id,
                    "label": label_for(layout_id),
                    "family": family_for(layout_id),
                    "held_out_day": int(held_day),
                    "selected_strategy": selected,
                    "selected_strategy_short": short_strategy(selected),
                    "train_mean_delta_pct": float(train_by_strategy.iloc[0]["train_mean_delta_pct"]),
                    "test_cases": int(len(values)),
                    "test_mean_delta_pct": float(values.mean()),
                    "test_median_delta_pct": float(np.median(values)),
                    "test_lower_frac": float((values < 0).mean()),
                    "generalization_gap_pct": float(values.mean() - train_by_strategy.iloc[0]["train_mean_delta_pct"]),
                }
            )

    daily = pd.DataFrame.from_records(daily_records)

    full_best = (
        relative[relative["layout_id"].isin(LAYOUT_ORDER)]
        .groupby(["layout_id", "strategy"], as_index=False)
        .agg(full_matrix_mean_delta_pct=(DELTA_COL, "mean"))
        .sort_values(["layout_id", "full_matrix_mean_delta_pct", "strategy"])
        .groupby("layout_id", as_index=False)
        .head(1)
        .rename(columns={"strategy": "full_matrix_best_strategy"})
    )

    summary_records: list[dict[str, object]] = []
    for layout_id in LAYOUT_ORDER:
        sub_daily = daily[daily["layout_id"] == layout_id].copy()
        # Weight each representative day equally in the uncertainty interval.
        day_values = sub_daily["test_mean_delta_pct"].to_numpy(dtype=float)
        ci_low, ci_high = bootstrap_ci(day_values, replicates, rng)
        selected_counts = sub_daily["selected_strategy_short"].value_counts()
        mode_strategy = str(selected_counts.index[0])
        mode_share = float(selected_counts.iloc[0] / selected_counts.sum())
        selected_concat = "; ".join(f"{k}:{v}" for k, v in selected_counts.items())
        full_row = full_best[full_best["layout_id"] == layout_id].iloc[0]
        summary_records.append(
            {
                "layout_id": layout_id,
                "label": label_for(layout_id),
                "family": family_for(layout_id),
                "heldout_days": int(sub_daily["held_out_day"].nunique()),
                "heldout_cases": int(sub_daily["test_cases"].sum()),
                "loo_mean_delta_pct": float(sub_daily["test_mean_delta_pct"].mean()),
                "loo_median_of_day_means_pct": float(np.median(day_values)),
                "loo_ci95_low_pct": ci_low,
                "loo_ci95_high_pct": ci_high,
                "loo_lower_day_frac": float((day_values < 0).mean()),
                "mean_generalization_gap_pct": float(sub_daily["generalization_gap_pct"].mean()),
                "modal_selected_strategy": mode_strategy,
                "modal_strategy_share": mode_share,
                "selected_strategy_counts": selected_concat,
                "full_matrix_best_strategy": short_strategy(str(full_row["full_matrix_best_strategy"])),
                "full_matrix_best_mean_delta_pct": float(full_row["full_matrix_mean_delta_pct"]),
                "optimism_gap_vs_full_best_pct": float(
                    sub_daily["test_mean_delta_pct"].mean() - full_row["full_matrix_mean_delta_pct"]
                ),
            }
        )

    summary = pd.DataFrame.from_records(summary_records)
    summary["order"] = summary["layout_id"].map({layout: i for i, layout in enumerate(LAYOUT_ORDER)})
    return summary.sort_values("order").drop(columns=["order"]), daily


def make_figure(summary: pd.DataFrame, daily: pd.DataFrame, out: Path) -> None:
    set_style()
    fig = plt.figure(figsize=(7.35, 3.85), dpi=360)
    gs = fig.add_gridspec(
        1,
        2,
        width_ratios=[1.18, 0.82],
        left=0.10,
        right=0.985,
        top=0.88,
        bottom=0.19,
        wspace=0.30,
    )
    ax0 = fig.add_subplot(gs[0, 0])
    ax1 = fig.add_subplot(gs[0, 1])

    labels = summary["label"].tolist()
    y = np.arange(len(labels))
    colors = [PALETTE[family_for(layout)] for layout in summary["layout_id"]]
    means = summary["loo_mean_delta_pct"].to_numpy(dtype=float)
    lows = summary["loo_ci95_low_pct"].to_numpy(dtype=float)
    highs = summary["loo_ci95_high_pct"].to_numpy(dtype=float)
    xerr = np.vstack([means - lows, highs - means])
    ax0.barh(y, means, color=colors, alpha=0.88, height=0.58)
    ax0.errorbar(means, y, xerr=xerr, fmt="none", ecolor=PALETTE["ink"], elinewidth=0.8, capsize=2.4)
    ax0.axvline(0, color="#334155", linewidth=0.85)
    ax0.set_yticks(y)
    ax0.set_yticklabels(labels)
    ax0.invert_yaxis()
    ax0.set_xlabel("Leave-one-day-out test mean ΔR (%)")
    ax0.set_title("(a) Held-out direct-ray performance")
    ax0.grid(axis="y", visible=False)

    jitter = np.linspace(-0.18, 0.18, 9)
    for idx, layout_id in enumerate(summary["layout_id"]):
        sub = daily[daily["layout_id"] == layout_id].sort_values("held_out_day")
        ax0.scatter(
            sub["test_mean_delta_pct"].to_numpy(dtype=float),
            np.full(len(sub), idx) + jitter[: len(sub)],
            s=10,
            color="white",
            edgecolor="#111827",
            linewidth=0.35,
            zorder=3,
        )

    shares = summary["modal_strategy_share"].to_numpy(dtype=float)
    gaps = summary["optimism_gap_vs_full_best_pct"].to_numpy(dtype=float)
    ax1.scatter(gaps, shares, s=52, c=colors, edgecolor="#111827", linewidth=0.45)
    label_offsets = {
        "ctrl_radial_compact_015": (0.08, -0.018),
        "ctrl_radial_expand_015": (0.08, 0.012),
        "ctrl_ring_wave_012": (0.08, -0.010),
        "deform_0276": (0.08, 0.010),
        "deform_0893": (0.08, 0.022),
        "deform_1387": (0.08, -0.022),
        "deform_1822": (0.08, 0.000),
    }
    for _, row in summary.iterrows():
        dx, dy = label_offsets.get(str(row["layout_id"]), (0.08, 0.0))
        ax1.text(
            row["optimism_gap_vs_full_best_pct"] + dx,
            row["modal_strategy_share"] + dy,
            text_label_for(str(row["layout_id"])),
            va="center",
            fontsize=7.0,
        )
    ax1.axvline(0, color="#334155", linewidth=0.85)
    ax1.set_xlabel("Optimism gap vs full-matrix best (pct-pt)")
    ax1.set_ylabel("Modal strategy share")
    ax1.set_xlim(min(-0.35, gaps.min() - 0.35), gaps.max() + 1.05)
    ax1.set_ylim(0.08, 1.02)
    ax1.set_title("(b) Selection stability")

    fig.suptitle("Leave-one-day-out direct-ray strategy-selection audit", y=0.965, fontweight="normal")
    for ext in ["png", "pdf"]:
        fig.savefig(out / "figures" / f"fig_baseline_direct_holdout.{ext}", dpi=360)
    plt.close(fig)


def write_report(summary: pd.DataFrame, daily: pd.DataFrame, out: Path) -> None:
    best = summary.sort_values("loo_mean_delta_pct").iloc[0]
    strongest_ci = summary[summary["loo_ci95_high_pct"] < 0].copy()
    lines = [
        "# Leave-One-Day-Out Direct-Ray Hold-Out Audit",
        "",
        "This report uses the completed baseline-control reduced PySolTrace matrix to address strategy-selection bias.",
        "For each non-baseline layout, one representative day is held out, the best aiming strategy is selected on the other eight days, and the selected strategy is then evaluated on the held-out day.",
        "",
        "## Summary",
        "",
        f"- Layouts tested: {summary.shape[0]} non-baseline layouts.",
        f"- Held-out days per layout: {int(summary['heldout_days'].iloc[0])}.",
        f"- Held-out condition rows per layout: {int(summary['heldout_cases'].iloc[0])}.",
        f"- Best held-out mean: {best['label']} at {best['loo_mean_delta_pct']:.2f}% peak-to-active-mean change.",
        f"- Rows with day-bootstrap CI entirely below zero: {', '.join(str(v) for v in strongest_ci['label']) if not strongest_ci.empty else 'none'}.",
        "",
        "## Leave-one-day-out summary table",
        "",
        summary.to_markdown(index=False, floatfmt=".3f"),
        "",
        "## Daily selected strategies",
        "",
        daily.to_markdown(index=False, floatfmt=".3f"),
        "",
    ]
    (out / "BASELINE_DIRECT_HOLDOUT_AUDIT.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    direct = resolve(args.direct)
    out = resolve(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "tables").mkdir(parents=True, exist_ok=True)
    (out / "figures").mkdir(parents=True, exist_ok=True)

    relative_path = direct / "tables" / "soltrace_sensitivity_relative.csv"
    if not relative_path.exists():
        raise FileNotFoundError(relative_path)
    relative = pd.read_csv(relative_path)
    relative = relative[relative["layout_id"].isin(LAYOUT_ORDER)].copy()

    summary, daily = build_holdout(relative, args.bootstrap, args.seed)
    summary.to_csv(out / "tables" / "baseline_direct_leave_one_day_holdout.csv", index=False)
    daily.to_csv(out / "tables" / "baseline_direct_holdout_daily.csv", index=False)
    make_figure(summary, daily, out)
    write_report(summary, daily, out)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
