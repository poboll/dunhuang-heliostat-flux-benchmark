#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN = ROOT / "server_outputs" / "joint_layout_aiming_20260523"
DEFAULT_DIRECT = DEFAULT_RUN / "soltrace_joint_direct_27cond_20260523"
DEFAULT_OUT = DEFAULT_DIRECT / "analysis"


ROLE_LABEL = {
    "baseline_full": "$L_0$",
    "joint_g02_0333": "$J_{bal}$",
    "joint_g02_0303": "$J_{gain}$",
    "joint_g04_0478": "$J_{flux}$",
}

ROLE_NAME = {
    "baseline_full": "baseline",
    "joint_g02_0333": "no-energy-loss balance",
    "joint_g02_0303": "energy-gated receiver candidate",
    "joint_g04_0478": "receiver-risk boundary",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build manuscript-facing report for joint layout--aiming direct checks.")
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


def load_inputs(run: Path, direct: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    relative_path = direct / "tables" / "soltrace_sensitivity_relative.csv"
    summary_path = direct / "tables" / "soltrace_sensitivity_summary.csv"
    reps_path = run / "tables" / "joint_optimizer_representatives.csv"
    missing = [p for p in [relative_path, summary_path, reps_path] if not p.exists()]
    if missing:
        raise FileNotFoundError("Missing required tables:\n" + "\n".join(str(p) for p in missing))
    return pd.read_csv(relative_path), pd.read_csv(summary_path), pd.read_csv(reps_path)


def representative_subset(reps: pd.DataFrame) -> pd.DataFrame:
    wanted = ["baseline_full", "joint_g02_0333", "joint_g02_0303", "joint_g04_0478"]
    out = reps[reps["candidate_id"].isin(wanted)].copy()
    out["layout_id"] = out["candidate_id"]
    out["label"] = out["layout_id"].map(ROLE_LABEL)
    out["role_name"] = out["layout_id"].map(ROLE_NAME)
    out["strategy_short"] = out["best_strategy"].map(short_strategy)
    out["order"] = out["layout_id"].map({layout_id: i for i, layout_id in enumerate(wanted)})
    return out.sort_values("order")


def build_best_rows(summary: pd.DataFrame, reps: pd.DataFrame) -> pd.DataFrame:
    wanted = reps.loc[reps["layout_id"] != "baseline_full", "layout_id"].tolist()
    best = (
        summary[summary["layout_id"].isin(wanted)]
        .sort_values(["layout_id", "mean_delta_peak_pct", "median_delta_peak_pct"])
        .groupby("layout_id", as_index=False)
        .head(1)
        .copy()
    )
    best["label"] = best["layout_id"].map(ROLE_LABEL)
    best["role_name"] = best["layout_id"].map(ROLE_NAME)
    best["strategy_short"] = best["strategy"].map(short_strategy)
    best["order"] = best["layout_id"].map({layout_id: i for i, layout_id in enumerate(wanted)})
    return best.sort_values("order").drop(columns=["order"])


def build_proxy_rows(relative: pd.DataFrame, reps: pd.DataFrame) -> pd.DataFrame:
    records = []
    for row in reps.itertuples(index=False):
        if row.layout_id == "baseline_full":
            continue
        sub = relative[(relative["layout_id"] == row.layout_id) & (relative["strategy"] == row.best_strategy)].copy()
        values = sub["delta_peak_to_active_mean_pct_vs_baseline_same_strategy"].dropna().to_numpy(dtype=float)
        if len(values) == 0:
            continue
        records.append(
            {
                "layout_id": row.layout_id,
                "label": ROLE_LABEL.get(row.layout_id, row.layout_id),
                "role_name": ROLE_NAME.get(row.layout_id, ""),
                "strategy": row.best_strategy,
                "strategy_short": short_strategy(row.best_strategy),
                "cases": int(len(values)),
                "mean_delta_peak_pct": float(values.mean()),
                "median_delta_peak_pct": float(np.median(values)),
                "p10_delta_peak_pct": float(np.percentile(values, 10)),
                "p90_delta_peak_pct": float(np.percentile(values, 90)),
                "share_lower_peak": float((values < 0).mean()),
                "median_delta_intercept_pctpt": float(sub["delta_receiver_intercept_pctpt_vs_baseline_same_strategy"].median()),
            }
        )
    out = pd.DataFrame.from_records(records)
    order = {layout_id: i for i, layout_id in enumerate(["joint_g02_0333", "joint_g02_0303", "joint_g04_0478"])}
    if not out.empty:
        out["order"] = out["layout_id"].map(order)
        out = out.sort_values("order").drop(columns=["order"])
    return out


def bootstrap_ci(relative: pd.DataFrame, rows: pd.DataFrame, view: str, replicates: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    records = []
    for row in rows.itertuples(index=False):
        strategy = row.strategy
        sub = relative[(relative["layout_id"] == row.layout_id) & (relative["strategy"] == strategy)]
        values = sub["delta_peak_to_active_mean_pct_vs_baseline_same_strategy"].dropna().to_numpy(dtype=float)
        if len(values) == 0:
            continue
        boot = rng.choice(values, size=(replicates, len(values)), replace=True).mean(axis=1)
        records.append(
            {
                "view": view,
                "layout_id": row.layout_id,
                "label": ROLE_LABEL.get(row.layout_id, row.layout_id),
                "role_name": ROLE_NAME.get(row.layout_id, ""),
                "strategy": strategy,
                "strategy_short": short_strategy(strategy),
                "cases": int(len(values)),
                "mean_delta_peak_pct": float(values.mean()),
                "median_delta_peak_pct": float(np.median(values)),
                "ci95_low_pct": float(np.percentile(boot, 2.5)),
                "ci95_high_pct": float(np.percentile(boot, 97.5)),
                "share_lower_peak": float((values < 0).mean()),
                "median_delta_intercept_pctpt": float(
                    sub["delta_receiver_intercept_pctpt_vs_baseline_same_strategy"].median()
                ),
            }
        )
    return pd.DataFrame.from_records(records)


def set_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": "#111827",
            "axes.labelcolor": "#111827",
            "xtick.color": "#111827",
            "ytick.color": "#111827",
        }
    )


def plot_outputs(out: Path, ci: pd.DataFrame, summary: pd.DataFrame) -> None:
    set_style()
    fig_dir = out / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    if not ci.empty:
        fig, ax = plt.subplots(figsize=(8.2, 4.2), dpi=220)
        plot_df = ci.copy()
        plot_df["x_label"] = plot_df["label"] + "\n" + plot_df["view"].str.replace("-", " ")
        colors = plot_df["view"].map({"proxy-selected": "#2563EB", "best-direct": "#B7791F"}).fillna("#64748B")
        x = np.arange(len(plot_df))
        ax.bar(x, plot_df["mean_delta_peak_pct"], color=colors, alpha=0.82)
        yerr = np.vstack(
            [
                plot_df["mean_delta_peak_pct"] - plot_df["ci95_low_pct"],
                plot_df["ci95_high_pct"] - plot_df["mean_delta_peak_pct"],
            ]
        )
        ax.errorbar(x, plot_df["mean_delta_peak_pct"], yerr=yerr, fmt="none", ecolor="#111827", elinewidth=0.9, capsize=3)
        ax.axhline(0.0, color="#111827", linewidth=0.9)
        ax.set_xticks(x)
        ax.set_xticklabels(plot_df["x_label"], fontsize=8)
        ax.set_ylabel("Direct peak-to-active-mean change (%)")
        ax.set_title("Reduced direct audit for joint layout--aiming candidates", fontweight="bold", loc="left")
        ax.grid(True, axis="y", alpha=0.16)
        fig.tight_layout()
        fig.savefig(fig_dir / "fig_joint_direct_summary.png", bbox_inches="tight")
        plt.close(fig)

    wanted = ["joint_g02_0333", "joint_g02_0303", "joint_g04_0478"]
    heat = summary[summary["layout_id"].isin(wanted)].copy()
    if not heat.empty:
        pivot = heat.pivot(index="layout_id", columns="strategy", values="mean_delta_peak_pct")
        pivot = pivot.reindex(wanted)
        fig, ax = plt.subplots(figsize=(8.8, 3.6), dpi=220)
        vmax = float(np.nanmax(np.abs(pivot.to_numpy()))) if np.isfinite(pivot.to_numpy()).any() else 1.0
        im = ax.imshow(pivot.to_numpy(), cmap="RdBu_r", vmin=-vmax, vmax=vmax, aspect="auto")
        ax.set_yticks(np.arange(len(pivot.index)))
        ax.set_yticklabels([ROLE_LABEL.get(idx, idx) for idx in pivot.index])
        ax.set_xticks(np.arange(len(pivot.columns)))
        ax.set_xticklabels([short_strategy(c) for c in pivot.columns], rotation=25, ha="right", fontsize=8)
        for i in range(len(pivot.index)):
            for j in range(len(pivot.columns)):
                value = pivot.iloc[i, j]
                if np.isfinite(value):
                    ax.text(j, i, f"{value:+.1f}", ha="center", va="center", fontsize=7, color="#111827")
        ax.set_title("Mean direct response by joint candidate and strategy", fontweight="bold", loc="left")
        cbar = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.03)
        cbar.set_label("Mean change (%)")
        fig.tight_layout()
        fig.savefig(fig_dir / "fig_joint_direct_strategy_heatmap.png", bbox_inches="tight")
        plt.close(fig)


def markdown_table(df: pd.DataFrame, columns: list[str], floatfmt: str = ".3f") -> str:
    if df.empty:
        return ""
    view = df.loc[:, columns].copy()
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in view.itertuples(index=False):
        cells = []
        for value in row:
            if isinstance(value, (float, np.floating)):
                cells.append(format(float(value), floatfmt))
            else:
                cells.append(str(value))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def write_report(out: Path, reps: pd.DataFrame, ci: pd.DataFrame, relative: pd.DataFrame) -> None:
    conditions = relative["condition_id"].nunique() if "condition_id" in relative.columns else 0
    report = [
        "# Joint Layout--Aiming Reduced Direct Audit",
        "",
        "This report aggregates the reduced PySolTrace direct checks for the joint layout--aiming representatives. It tests whether candidates selected by the integrated screening layer remain directionally useful under direct ray tracing.",
        "",
        f"- Non-baseline joint candidates checked: {int((reps['layout_id'] != 'baseline_full').sum())}",
        f"- Solar conditions aggregated: {conditions}",
        "- Layouts: baseline, J_bal, J_gain, and J_flux.",
        "- Strategies: visible-equator, five-point, and S9 phases p2, p3, and p5.",
        "- Scope: reduced direct numerical audit, not full-field annual certification.",
        "",
        "## Bootstrap Summary",
        "",
    ]
    if not ci.empty:
        cols = [
            "view",
            "label",
            "strategy_short",
            "cases",
            "mean_delta_peak_pct",
            "ci95_low_pct",
            "ci95_high_pct",
            "share_lower_peak",
            "median_delta_intercept_pctpt",
        ]
        report.append(markdown_table(ci, cols))
    else:
        report.append("No direct rows available.")
    report.extend(
        [
            "",
            "## Interpretation",
            "",
            "Positive joint-screening results should be written into the manuscript only when the reduced direct layer supports the same direction. If proxy-selected and best-direct rows diverge, the manuscript should describe the joint optimizer as a candidate generator whose outputs require direct optical-engine auditing.",
            "",
        ]
    )
    (out / "JOINT_DIRECT_SOLTRACE_AUDIT.md").write_text("\n".join(report), encoding="utf-8")


def main() -> int:
    args = parse_args()
    run = resolve(args.run)
    direct = resolve(args.direct)
    out = resolve(args.out)
    (out / "tables").mkdir(parents=True, exist_ok=True)
    relative, summary, reps = load_inputs(run, direct)
    reps = representative_subset(reps)
    best = build_best_rows(summary, reps)
    proxy = build_proxy_rows(relative, reps)
    best.to_csv(out / "tables" / "joint_direct_best_rows.csv", index=False)
    proxy.to_csv(out / "tables" / "joint_direct_proxy_rows.csv", index=False)
    ci = pd.concat(
        [
            bootstrap_ci(relative, proxy, "proxy-selected", args.bootstrap, args.seed),
            bootstrap_ci(relative, best, "best-direct", args.bootstrap, args.seed + 17),
        ],
        axis=0,
        ignore_index=True,
    )
    if not ci.empty:
        order = {"joint_g02_0333": 0, "joint_g02_0303": 1, "joint_g04_0478": 2}
        view_order = {"proxy-selected": 0, "best-direct": 1}
        ci["order"] = ci["layout_id"].map(order)
        ci["view_order"] = ci["view"].map(view_order)
        ci = ci.sort_values(["order", "view_order"]).drop(columns=["order", "view_order"])
    ci.to_csv(out / "tables" / "joint_direct_bootstrap_ci.csv", index=False)
    plot_outputs(out, ci, summary)
    write_report(out, reps, ci, relative)
    print(f"Wrote {out}")
    if not ci.empty:
        print(ci.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
