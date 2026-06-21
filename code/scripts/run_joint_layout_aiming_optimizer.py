#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
SCRIPTS = ROOT / "scripts"
for path in [SRC, SCRIPTS]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from dhf_rebuild.data_io import load_json, load_layout, write_layout
from dhf_rebuild.optimizer import build_calibration
from dhf_rebuild.solar_proxy import compute_heliostat_features
from dhf_rebuild.terrain import attach_terrain_features, load_terrain, terrain_relative_layout
from run_aiming_proxy import flux_map, make_groups, offsets_for_strategy
from run_fullfield_deformation import PARAM_KEYS, evaluate_candidate, parameter_set, transform_layout


BOUNDS = {
    "x_scale": (0.965, 1.035),
    "y_scale": (0.965, 1.035),
    "radial_scale": (-0.025, 0.025),
    "radial_wave": (-0.018, 0.018),
    "twist": (-0.035, 0.035),
    "az_wave": (-0.020, 0.020),
    "petal_amp": (-0.026, 0.026),
    "petal_phase": (-math.pi, math.pi),
    "petal_twist": (-0.012, 0.012),
    "north_bias": (-0.012, 0.012),
}

MUTATION_SIGMA = {
    "x_scale": 0.006,
    "y_scale": 0.006,
    "radial_scale": 0.006,
    "radial_wave": 0.004,
    "twist": 0.008,
    "az_wave": 0.005,
    "petal_amp": 0.006,
    "petal_phase": 0.45,
    "petal_twist": 0.003,
    "north_bias": 0.004,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Jointly screen bounded full-field layout deformations and receiver-aiming strategies."
    )
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "server_full.json")
    parser.add_argument(
        "--source-run",
        type=Path,
        default=ROOT / "server_outputs" / "streamed_fullfield_20260511_205252",
        help="Existing full-field run used to seed the joint optimizer.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "server_outputs" / "joint_layout_aiming_20260523",
    )
    parser.add_argument("--initial-random", type=int, default=72)
    parser.add_argument("--initial-from-prior", type=int, default=96)
    parser.add_argument("--generations", type=int, default=4)
    parser.add_argument("--children-per-generation", type=int, default=72)
    parser.add_argument("--elite-count", type=int, default=16)
    parser.add_argument("--seed", type=int, default=20260523)
    parser.add_argument("--theta-bins", type=int, default=64)
    parser.add_argument("--z-bins", type=int, default=64)
    return parser.parse_args()


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def canonical_params(params: dict[str, float]) -> dict[str, float]:
    out = {key: float(params.get(key, 0.0)) for key in PARAM_KEYS}
    out["petal_order"] = float(int(round(out.get("petal_order", 0.0))))
    if int(out["petal_order"]) == 0:
        out["petal_amp"] = 0.0
        out["petal_phase"] = 0.0
        out["petal_twist"] = 0.0
    for key, (lo, hi) in BOUNDS.items():
        out[key] = float(np.clip(out[key], lo, hi))
    return out


def params_key(params: dict[str, float]) -> tuple:
    out = []
    for key in PARAM_KEYS:
        value = params.get(key, 0.0)
        if key == "petal_order":
            out.append(int(round(float(value))))
        else:
            out.append(round(float(value), 6))
    return tuple(out)


def load_prior_params(source_run: Path, limit: int) -> list[dict[str, float]]:
    table = source_run / "tables" / "fullfield_candidates.csv"
    if not table.exists():
        return []
    df = pd.read_csv(table)
    required = set(PARAM_KEYS)
    if not required.issubset(df.columns):
        return []
    pool = df.copy()
    for column, higher in [
        ("energy_ratio_vs_baseline", True),
        ("flux_risk_index", False),
        ("layout_quality_score", True),
        ("terrain_slope_p95_pct", False),
    ]:
        values = pool[column].astype(float)
        lo, hi = values.min(), values.max()
        if abs(hi - lo) < 1e-12:
            score = pd.Series(np.ones(len(pool)), index=pool.index)
        else:
            score = (values - lo) / (hi - lo)
        pool[f"_{column}"] = score if higher else 1.0 - score
    pool["_seed_score"] = pool[
        [
            "_energy_ratio_vs_baseline",
            "_flux_risk_index",
            "_layout_quality_score",
            "_terrain_slope_p95_pct",
        ]
    ].mean(axis=1)
    records = []
    baseline = pool[pool["candidate_id"] == "baseline_full"]
    if not baseline.empty:
        records.append(canonical_params(baseline.iloc[0].to_dict()))
    for _, row in pool.sort_values("_seed_score", ascending=False).head(limit).iterrows():
        records.append(canonical_params(row.to_dict()))
    return records


def mutate_params(parent: dict[str, float], rng: np.random.Generator, scale: float) -> dict[str, float]:
    child = dict(parent)
    if rng.random() < 0.18:
        child["petal_order"] = float(rng.choice([0, 4, 6, 8], p=[0.35, 0.30, 0.25, 0.10]))
    for key, sigma in MUTATION_SIGMA.items():
        child[key] = float(child.get(key, 0.0) + rng.normal(0.0, sigma * scale))
    if int(round(child.get("petal_order", 0.0))) > 0 and abs(child.get("petal_amp", 0.0)) < 0.004:
        child["petal_amp"] = float(rng.choice([-1.0, 1.0]) * rng.uniform(0.004, 0.014))
    return canonical_params(child)


def strategy_set() -> list[str]:
    strategies = ["equator", "five_point"]
    strategies.extend([f"staggered_levels:9:0.380:{phase:d}" for phase in range(9)])
    strategies.extend([f"staggered_levels:9:0.340:{phase:d}" for phase in [0, 2, 4, 6, 8]])
    strategies.extend([f"staggered_levels:9:0.420:{phase:d}" for phase in [1, 3, 5, 7]])
    strategies.extend(["balanced:0.240:0.000", "balanced:0.320:0.015", "balanced:0.400:0.030"])
    return list(dict.fromkeys(strategies))


def evaluate_aiming(
    features: pd.DataFrame,
    config: dict,
    strategies: list[str],
    theta_bins: int,
    z_bins: int,
) -> tuple[dict[str, float | str | int], pd.DataFrame]:
    receiver_height = float(config["plant"]["receiver_height_m"])
    receiver_diameter = float(config["plant"]["receiver_diameter_m"])
    groups = make_groups(features)
    rows = []
    for strategy in strategies:
        aimed = offsets_for_strategy(groups, strategy, receiver_height)
        _, metrics = flux_map(
            aimed,
            receiver_height,
            receiver_diameter,
            theta_bins=theta_bins,
            z_bins=z_bins,
        )
        objective = (
            metrics["peak_to_mean_proxy"]
            + 0.75 * metrics["cv_active_proxy"]
            + 7.0 * metrics["spillage_proxy"]
        )
        rows.append({"strategy": strategy, "aiming_objective": objective, **metrics})
    table = pd.DataFrame.from_records(rows).sort_values(["aiming_objective", "peak_to_mean_proxy"])
    best = table.iloc[0].to_dict()
    best["searched_strategy_count"] = len(table)
    best["group_count"] = len(groups)
    return best, table


def joint_loss(row: dict[str, float | str | int], baseline: dict[str, float]) -> float:
    energy_ratio = float(row["energy_ratio_vs_baseline"])
    peak_ratio = float(row["best_peak_to_mean_proxy"]) / max(baseline["best_peak_to_mean_proxy"], 1e-12)
    spillage_penalty = max(0.0, float(row["best_spillage_proxy"]) - baseline["best_spillage_proxy"])
    quality_penalty = max(0.0, 0.98 - float(row["layout_quality_score"]))
    spacing_penalty = max(0.0, 16.0 - float(row["min_neighbor_m"])) / 16.0
    terrain_penalty = max(0.0, float(row["terrain_slope_p95_pct"]) - 1.35) / 1.35
    return (
        100.0 * (peak_ratio - 1.0)
        - 55.0 * (energy_ratio - 1.0)
        + 600.0 * spillage_penalty
        + 6.0 * quality_penalty
        + 4.0 * spacing_penalty
        + 2.0 * terrain_penalty
    )


def evaluate_params(
    cid: str,
    generation: int,
    params: dict[str, float],
    base_flat: pd.DataFrame,
    base_layout: pd.DataFrame,
    base_proxy_sum: float,
    base_flux_p99: float,
    calibration,
    config: dict,
    terrain: pd.DataFrame,
    strategies: list[str],
    theta_bins: int,
    z_bins: int,
) -> tuple[dict[str, float | str | int], pd.DataFrame, pd.DataFrame]:
    layout = terrain_relative_layout(transform_layout(base_flat, params), terrain)
    layout_row, features = evaluate_candidate(
        cid,
        layout,
        base_layout,
        base_proxy_sum,
        base_flux_p99,
        calibration,
        config,
        terrain,
    )
    best_aim, aim_table = evaluate_aiming(features, config, strategies, theta_bins, z_bins)
    record = {**layout_row, **params}
    record.update(
        {
            "generation": generation,
            "best_strategy": best_aim["strategy"],
            "best_aiming_objective": float(best_aim["aiming_objective"]),
            "best_intercept_fraction_proxy": float(best_aim["intercept_fraction_proxy"]),
            "best_spillage_proxy": float(best_aim["spillage_proxy"]),
            "best_peak_to_mean_proxy": float(best_aim["peak_to_mean_proxy"]),
            "best_cv_active_proxy": float(best_aim["cv_active_proxy"]),
            "searched_strategy_count": int(best_aim["searched_strategy_count"]),
            "group_count": int(best_aim["group_count"]),
        }
    )
    aim_table.insert(0, "candidate_id", cid)
    return record, features, aim_table


def pareto_mask(df: pd.DataFrame) -> np.ndarray:
    values = df[
        [
            "energy_ratio_vs_baseline",
            "best_peak_to_mean_proxy",
            "best_spillage_proxy",
            "layout_quality_score",
        ]
    ].to_numpy(dtype=float)
    obj = values.copy()
    obj[:, 1] *= -1.0
    obj[:, 2] *= -1.0
    n = len(obj)
    dominated = np.zeros(n, dtype=bool)
    for i in range(n):
        better_or_equal = (obj >= obj[i]).all(axis=1)
        strictly = (obj > obj[i]).any(axis=1)
        better_or_equal[i] = False
        dominated[i] = bool((better_or_equal & strictly).any())
    return ~dominated


def select_representatives(df: pd.DataFrame) -> pd.DataFrame:
    pool = df[df["is_publishable_geometry"].astype(int) == 1].copy()
    if pool.empty:
        pool = df.copy()
    picks: list[int] = []
    roles: dict[int, str] = {}

    def add(idx: int, role: str) -> None:
        if idx not in roles:
            picks.append(idx)
            roles[idx] = role

    baseline = df.index[df["candidate_id"] == "baseline_full"].tolist()
    if baseline:
        add(baseline[0], "baseline")
    add(pool["joint_loss"].idxmin(), "J_flux_receiver_boundary")
    no_loss = pool[(pool["delta_energy_pct"] >= 0.0) & (pool["delta_peak_to_mean_pct_vs_baseline_best"] <= 0.0)].copy()
    if not no_loss.empty:
        add(no_loss["delta_peak_to_mean_pct_vs_baseline_best"].idxmin(), "J_bal_no_energy_loss")
        useful_gain = no_loss[no_loss["delta_peak_to_mean_pct_vs_baseline_best"] <= -2.0].copy()
        if useful_gain.empty:
            useful_gain = no_loss
        add(useful_gain["delta_energy_pct"].idxmax(), "J_gain_receiver_gate")
        add(no_loss["delta_energy_pct"].idxmax(), "max_energy_receiver_gate")
    else:
        receiver_gate = pool[pool["delta_peak_to_mean_pct_vs_baseline_best"] <= 0.0].copy()
        if receiver_gate.empty:
            receiver_gate = pool
        add(receiver_gate["energy_ratio_vs_baseline"].idxmax(), "energy_with_receiver_gate")
    add(pool["best_spillage_proxy"].idxmin(), "min_spillage")
    add(pool["layout_quality_score"].idxmax(), "max_geometry_quality")
    for idx in pool.sort_values("joint_loss").index:
        if len(picks) >= 8:
            break
        add(idx, "joint_extra")
    reps = df.loc[picks].copy()
    reps["joint_role"] = [roles[idx] for idx in picks]
    return reps


def set_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
            "axes.edgecolor": "#222222",
            "axes.labelcolor": "#111827",
            "xtick.color": "#111827",
            "ytick.color": "#111827",
            "figure.facecolor": "white",
            "axes.facecolor": "white",
        }
    )


def plot_outputs(out: Path, df: pd.DataFrame, reps: pd.DataFrame, layouts: dict[str, pd.DataFrame]) -> None:
    set_style()
    fig_dir = out / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    plot_df = df.copy()
    fig, ax = plt.subplots(figsize=(7.2, 5.1), dpi=220)
    sc = ax.scatter(
        plot_df["delta_energy_pct"],
        plot_df["delta_peak_to_mean_pct_vs_baseline_best"],
        c=plot_df["joint_loss"],
        cmap="viridis_r",
        s=18,
        alpha=0.72,
        linewidth=0.0,
    )
    ax.axhline(0.0, color="#374151", linewidth=0.9)
    ax.axvline(0.0, color="#374151", linewidth=0.9)
    ax.set_xlabel("Layout optical-proxy change vs baseline (%)")
    ax.set_ylabel("Best aiming peak-to-active-mean change (%)")
    ax.set_title("Joint layout--aiming search surface", fontweight="bold", loc="left")
    cbar = fig.colorbar(sc, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("joint loss (lower is better)")
    for _, row in reps.iterrows():
        ax.scatter(
            [row["delta_energy_pct"]],
            [row["delta_peak_to_mean_pct_vs_baseline_best"]],
            s=58,
            facecolor="none",
            edgecolor="#DC2626",
            linewidth=1.1,
        )
        ax.text(
            row["delta_energy_pct"],
            row["delta_peak_to_mean_pct_vs_baseline_best"],
            " " + str(row["joint_role"]),
            fontsize=7,
            va="center",
        )
    ax.grid(True, alpha=0.16)
    fig.tight_layout()
    fig.savefig(fig_dir / "fig_joint_optimizer_pareto.png", bbox_inches="tight")
    plt.close(fig)

    conv = (
        df.sort_values(["generation", "joint_loss"])
        .groupby("generation", as_index=False)
        .agg(
            best_joint_loss=("joint_loss", "min"),
            best_peak_delta_pct=("delta_peak_to_mean_pct_vs_baseline_best", "min"),
            best_energy_delta_pct=("delta_energy_pct", "max"),
            evaluated=("candidate_id", "count"),
        )
    )
    fig, ax1 = plt.subplots(figsize=(7.2, 4.2), dpi=220)
    ax1.plot(conv["generation"], conv["best_joint_loss"], marker="o", color="#2563EB", label="best joint loss")
    ax1.set_xlabel("Generation")
    ax1.set_ylabel("Best joint loss")
    ax2 = ax1.twinx()
    ax2.plot(
        conv["generation"],
        conv["best_peak_delta_pct"],
        marker="s",
        color="#B7791F",
        label="best receiver delta",
    )
    ax2.set_ylabel("Best peak-to-mean change (%)")
    ax1.set_title("Joint optimizer convergence", fontweight="bold", loc="left")
    ax1.grid(True, alpha=0.16)
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc="best", frameon=False)
    fig.tight_layout()
    fig.savefig(fig_dir / "fig_joint_optimizer_convergence.png", bbox_inches="tight")
    plt.close(fig)

    ncols = min(3, len(reps))
    nrows = int(math.ceil(len(reps) / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(4.1 * ncols, 4.0 * nrows), dpi=220)
    axes = np.array(axes).reshape(-1)
    base = layouts.get("baseline_full")
    for ax, (_, row) in zip(axes, reps.iterrows()):
        layout = layouts[str(row["candidate_id"])]
        if base is not None and str(row["candidate_id"]) != "baseline_joint":
            ax.scatter(base["x_m"], base["y_m"], s=0.08, color="#CBD5E1", alpha=0.45, label="baseline")
        ax.scatter(layout["x_m"], layout["y_m"], s=0.13, color="#0F766E", alpha=0.72, label="candidate")
        ax.scatter([0], [0], marker="^", s=28, color="#B91C1C")
        ax.set_aspect("equal")
        ax.set_xlim(-2200, 2200)
        ax.set_ylim(-2200, 2200)
        ax.set_title(
            f"{row['joint_role']} | {row['candidate_id']}",
            fontsize=8,
            fontweight="bold",
            loc="left",
        )
        ax.text(
            0.02,
            0.02,
            f"E {row['delta_energy_pct']:+.2f}%\nR {row['delta_peak_to_mean_pct_vs_baseline_best']:+.2f}%\n{row['best_strategy'].replace('staggered_levels:9:0.380:', 'S9-p')}",
            transform=ax.transAxes,
            fontsize=7,
            bbox={"facecolor": "white", "edgecolor": "#E5E7EB", "alpha": 0.88, "pad": 2},
        )
        ax.grid(True, alpha=0.12)
    for ax in axes[len(reps):]:
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(fig_dir / "fig_joint_optimizer_layouts.png", bbox_inches="tight")
    plt.close(fig)


def markdown_table(df: pd.DataFrame, columns: list[str], floatfmt: str = ".3f") -> str:
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


def write_report(out: Path, df: pd.DataFrame, reps: pd.DataFrame, baseline: dict[str, float]) -> None:
    best = df.sort_values("joint_loss").iloc[0]
    pareto_count = int(df["is_joint_pareto"].sum())
    report = f"""# Joint Layout--Aiming Optimizer Report

This run adds an integrated screening layer above the earlier defensive audits. It searches bounded full-field layout deformation parameters and receiver-aiming strategies under one scalarized objective, then exports a Pareto queue for later direct ray-tracing checks.

## Run Scale

- Candidates evaluated: {len(df):,}
- Generations: {int(df['generation'].max())}
- Publishable geometry candidates: {int(df['is_publishable_geometry'].sum()):,}
- Joint Pareto candidates: {pareto_count:,}
- Aiming strategies tested per candidate: {int(df['searched_strategy_count'].max())}
- Baseline best strategy: {baseline['best_strategy']}
- Baseline best peak-to-active-mean proxy: {baseline['best_peak_to_mean_proxy']:.4f}

## Best Joint Candidate

- Candidate: `{best['candidate_id']}`
- Strategy: `{best['best_strategy']}`
- Optical-proxy change: {best['delta_energy_pct']:+.3f}%
- Best-aiming peak-to-active-mean change: {best['delta_peak_to_mean_pct_vs_baseline_best']:+.3f}%
- Spillage proxy change: {best['delta_spillage_pctpt_vs_baseline_best']:+.3f} percentage points
- Layout quality score: {best['layout_quality_score']:.3f}
- Minimum nearest-neighbour spacing: {best['min_neighbor_m']:.2f} m

## Representative Queue

{markdown_table(reps, ['joint_role', 'candidate_id', 'delta_energy_pct', 'delta_peak_to_mean_pct_vs_baseline_best', 'delta_spillage_pctpt_vs_baseline_best', 'best_strategy', 'layout_quality_score'])}

## Interpretation Boundary

This is a joint screening optimizer, not annual commercial certification. The positive contribution is architectural: layout generation and receiver aiming are now selected in the same loop, instead of being optimized in separated modules. The exported representatives should be sent to reduced direct PySolTrace or CoPylot/SolarPILOT custom-aimpoint validation before any claim of robust receiver-risk reduction is made.
"""
    (out / "JOINT_LAYOUT_AIMING_OPTIMIZER_REPORT.md").write_text(report, encoding="utf-8")


def main() -> int:
    args = parse_args()
    config = load_json(resolve(args.config))
    source_run = resolve(args.source_run)
    out = resolve(args.out)
    for child in ["tables", "layouts", "figures"]:
        (out / child).mkdir(parents=True, exist_ok=True)
    (out / "run_config.json").write_text(json.dumps(vars(args), indent=2, default=str), encoding="utf-8")

    rng = np.random.default_rng(args.seed)
    terrain = load_terrain(ROOT / config["data"]["terrain_grid"])
    base_flat = load_layout(ROOT / config["data"]["layout_a"], remove_origin=True)
    base_layout = terrain_relative_layout(base_flat, terrain)
    eval_config = json.loads(json.dumps(config))
    eval_config["solar_sampling"] = {
        **config["solar_sampling"],
        "day_step": max(9, int(config["solar_sampling"]["day_step"])),
        "hours": [8, 9, 10, 11, 12, 13, 14, 15, 16],
    }
    base_features = compute_heliostat_features(base_layout, eval_config["plant"], eval_config["solar_sampling"])
    base_features = attach_terrain_features(base_features, terrain)
    base_sum = float(base_features["optical_proxy"].sum())
    base_flux_p99 = float(np.percentile(base_features["flux_risk_raw"], 99))
    calibration = build_calibration(eval_config, n_a=len(base_layout), n_b=9532)
    strategies = strategy_set()

    baseline_params = canonical_params({key: 0.0 for key in PARAM_KEYS} | {"x_scale": 1.0, "y_scale": 1.0})
    baseline_record, baseline_layout, baseline_aim = evaluate_params(
        "baseline_full",
        0,
        baseline_params,
        base_flat,
        base_layout,
        base_sum,
        base_flux_p99,
        calibration,
        eval_config,
        terrain,
        strategies,
        args.theta_bins,
        args.z_bins,
    )
    baseline_record["joint_loss"] = 0.0
    records = [baseline_record]
    all_aim = [baseline_aim]
    layouts: dict[str, pd.DataFrame] = {"baseline_full": baseline_layout}
    seen = {params_key(baseline_params)}

    seeds = load_prior_params(source_run, args.initial_from_prior)
    seeds.extend(parameter_set(args.initial_random, args.seed))
    initial_params = []
    for params in seeds:
        params = canonical_params(params)
        key = params_key(params)
        if key in seen:
            continue
        seen.add(key)
        initial_params.append(params)

    def evaluate_batch(params_list: list[dict[str, float]], generation: int, offset: int) -> list[dict[str, float | str | int]]:
        batch_records = []
        for i, params in enumerate(params_list):
            cid = f"joint_g{generation:02d}_{offset + i:04d}"
            record, layout, aiming = evaluate_params(
                cid,
                generation,
                params,
                base_flat,
                base_layout,
                base_sum,
                base_flux_p99,
                calibration,
                eval_config,
                terrain,
                strategies,
                args.theta_bins,
                args.z_bins,
            )
            batch_records.append(record)
            all_aim.append(aiming)
            layouts[cid] = layout
            if (i + 1) % 20 == 0 or i + 1 == len(params_list):
                print(f"generation {generation}: evaluated {i + 1}/{len(params_list)}", flush=True)
        return batch_records

    records.extend(evaluate_batch(initial_params, generation=0, offset=1))

    for generation in range(1, args.generations + 1):
        current = pd.DataFrame.from_records(records)
        base_metrics = {
            "best_peak_to_mean_proxy": float(baseline_record["best_peak_to_mean_proxy"]),
            "best_spillage_proxy": float(baseline_record["best_spillage_proxy"]),
        }
        current["joint_loss"] = current.apply(lambda row: joint_loss(row.to_dict(), base_metrics), axis=1)
        elite_pool = current[current["is_publishable_geometry"].astype(int) == 1].copy()
        if elite_pool.empty:
            elite_pool = current.copy()
        elite_pool = elite_pool.sort_values("joint_loss").head(args.elite_count)
        elite_params = [
            canonical_params({key: row[key] for key in PARAM_KEYS})
            for _, row in elite_pool.iterrows()
        ]
        children = []
        attempts = 0
        while len(children) < args.children_per_generation and attempts < args.children_per_generation * 20:
            attempts += 1
            parent = elite_params[int(rng.integers(0, len(elite_params)))]
            child = mutate_params(parent, rng, scale=max(0.45, 1.0 - 0.12 * generation))
            key = params_key(child)
            if key in seen:
                continue
            seen.add(key)
            children.append(child)
        records.extend(evaluate_batch(children, generation=generation, offset=len(records)))

    df = pd.DataFrame.from_records(records)
    base_metrics = {
        "best_peak_to_mean_proxy": float(baseline_record["best_peak_to_mean_proxy"]),
        "best_spillage_proxy": float(baseline_record["best_spillage_proxy"]),
    }
    df["joint_loss"] = df.apply(lambda row: joint_loss(row.to_dict(), base_metrics), axis=1)
    df["delta_energy_pct"] = (df["energy_ratio_vs_baseline"] - 1.0) * 100.0
    df["delta_peak_to_mean_pct_vs_baseline_best"] = (
        df["best_peak_to_mean_proxy"] / float(baseline_record["best_peak_to_mean_proxy"]) - 1.0
    ) * 100.0
    df["delta_spillage_pctpt_vs_baseline_best"] = (
        df["best_spillage_proxy"] - float(baseline_record["best_spillage_proxy"])
    ) * 100.0
    df["is_joint_pareto"] = pareto_mask(df).astype(int)
    df = df.sort_values(["joint_loss", "generation"]).reset_index(drop=True)
    df.to_csv(out / "tables" / "joint_optimizer_all_candidates.csv", index=False)

    aiming_df = pd.concat(all_aim, axis=0, ignore_index=True)
    aiming_df.to_csv(out / "tables" / "joint_optimizer_aiming_rows.csv", index=False)
    pareto = df[df["is_joint_pareto"] == 1].copy().sort_values("joint_loss")
    pareto.to_csv(out / "tables" / "joint_optimizer_pareto.csv", index=False)
    reps = select_representatives(df)
    reps.to_csv(out / "tables" / "joint_optimizer_representatives.csv", index=False)

    exported_layouts = {}
    for _, row in reps.iterrows():
        cid = str(row["candidate_id"])
        exported_layouts[cid] = layouts[cid]
        write_layout(out / "layouts" / f"{cid}.csv", layouts[cid])
    # Keep the baseline available even when it is not one of the selected rows.
    if "baseline_full" not in exported_layouts:
        exported_layouts["baseline_full"] = layouts["baseline_full"]
        write_layout(out / "layouts" / "baseline_full.csv", layouts["baseline_full"])

    plot_outputs(out, df, reps, exported_layouts)
    write_report(out, df, reps, baseline_record)
    print(f"Wrote {out}")
    print(df.head(8).loc[:, ["candidate_id", "joint_loss", "delta_energy_pct", "delta_peak_to_mean_pct_vs_baseline_best", "best_strategy"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
