#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STRONG = ROOT / "server_outputs" / "same_anchor_strong_baselines_20260523"
DEFAULT_JOINT = ROOT / "server_outputs" / "joint_layout_aiming_20260523"
DEFAULT_OUT = ROOT / "server_outputs" / "strong_baseline_direct_promotion_queue_20260523"


QUEUE = [
    {
        "layout_id": "baseline_full",
        "symbol": "L0",
        "role": "paired baseline",
        "source": "strong",
        "tier": "core",
        "reason": "Reference field for paired receiver-risk deltas.",
    },
    {
        "layout_id": "deform_0893",
        "symbol": "L_nom",
        "role": "held-out TS-FPDA nominal candidate",
        "source": "strong",
        "tier": "core",
        "reason": "Nominal TS-FPDA row with prior held-out/direct support.",
    },
    {
        "layout_id": "deform_1387",
        "symbol": "L_rob",
        "role": "held-out TS-FPDA receiver-risk candidate",
        "source": "strong",
        "tier": "core",
        "reason": "Receiver-risk TS-FPDA row with the clearest prior held-out support.",
    },
    {
        "layout_id": "ctrl_radial_expand_015",
        "symbol": "C_rad+",
        "role": "simple radial-control baseline",
        "source": "strong",
        "tier": "core",
        "reason": "Low-complexity control that should remain in the benchmark.",
    },
    {
        "layout_id": "joint_g04_0478",
        "symbol": "J_flux",
        "role": "joint receiver-boundary candidate",
        "source": "strong",
        "tier": "core",
        "reason": "Direct-supported receiver-boundary row from the joint audit.",
    },
    {
        "layout_id": "joint_g02_0333",
        "symbol": "J_bal",
        "role": "joint balance hypothesis",
        "source": "strong",
        "tier": "core",
        "reason": "No-energy-loss joint hypothesis; directional but uncertain in direct audit.",
    },
    {
        "layout_id": "sb_hy_energy",
        "symbol": "B_hy,E",
        "role": "hybrid strong-baseline energy pressure row",
        "source": "strong",
        "tier": "core",
        "reason": "Best strong-baseline optical/receiver compromise: +1.74% SolarPILOT optical and -4.44% aiming-proxy concentration.",
    },
    {
        "layout_id": "sb_pf_flux",
        "symbol": "B_pf,R",
        "role": "pattern-free receiver-pressure row",
        "source": "strong",
        "tier": "core",
        "reason": "Pattern-free approximation with -5.45% aiming-proxy concentration but optical loss.",
    },
    {
        "layout_id": "sb_hs_flux",
        "symbol": "B_hs,R",
        "role": "slider-like receiver-pressure row",
        "source": "strong",
        "tier": "core",
        "reason": "Slider-like approximation with -6.67% aiming-proxy concentration but optical loss.",
    },
    {
        "layout_id": "deform_0276",
        "symbol": "L_opt",
        "role": "optical stress case",
        "source": "strong",
        "tier": "extended",
        "reason": "Default-bridge optical upper case; retained to quantify receiver-flux penalty.",
    },
    {
        "layout_id": "joint_g02_0303",
        "symbol": "J_gain",
        "role": "joint proxy/direct mismatch case",
        "source": "joint",
        "tier": "extended",
        "reason": "Energy-gated joint candidate that exposed proxy/direct strategy sensitivity.",
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the next direct-promotion queue after the same-anchor strong-baseline pressure test."
    )
    parser.add_argument("--strong-run", type=Path, default=DEFAULT_STRONG)
    parser.add_argument("--joint-run", type=Path, default=DEFAULT_JOINT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def read_best_strategy(strong_run: Path, joint_run: Path) -> pd.DataFrame:
    strong_best = pd.read_csv(strong_run / "aiming_proxy" / "best_aiming_by_layout.csv")
    rows = strong_best.to_dict("records")
    joint_reps = pd.read_csv(joint_run / "tables" / "joint_optimizer_representatives.csv")
    for layout_id in {"joint_g02_0303"}:
        match = joint_reps[joint_reps["candidate_id"] == layout_id]
        if match.empty:
            continue
        rows.append(
            {
                "layout_id": layout_id,
                "strategy": str(match.iloc[0]["best_strategy"]),
                "heliostat_count": 11915,
                "group_count": int(match.iloc[0].get("group_count", 0)),
                "intercept_fraction_proxy": float(match.iloc[0].get("best_intercept_fraction_proxy", float("nan"))),
                "spillage_proxy": float(match.iloc[0].get("best_spillage_proxy", float("nan"))),
                "peak_flux_proxy": float("nan"),
                "mean_active_flux_proxy": float("nan"),
                "peak_to_mean_proxy": float(match.iloc[0].get("best_peak_to_mean_proxy", float("nan"))),
                "cv_active_proxy": float(match.iloc[0].get("best_cv_active_proxy", float("nan"))),
            }
        )
    best = pd.DataFrame(rows)
    queue_ids = [row["layout_id"] for row in QUEUE]
    best = best[best["layout_id"].isin(queue_ids)].drop_duplicates("layout_id", keep="last")
    return best


def copy_layout(layout_id: str, source: str, strong_run: Path, joint_run: Path, out: Path) -> str:
    if source == "strong":
        src = strong_run / "layouts" / f"{layout_id}.csv"
    elif source == "joint":
        src = joint_run / "layouts" / f"{layout_id}.csv"
    else:
        raise ValueError(source)
    if not src.exists():
        raise FileNotFoundError(src)
    dst = out / "layouts" / f"{layout_id}.csv"
    shutil.copy2(src, dst)
    return str(src)


def write_runbook(out: Path, queue_df: pd.DataFrame, best: pd.DataFrame) -> None:
    core_ids = queue_df.loc[queue_df["tier"] == "core", "layout_id"].tolist()
    extended_ids = queue_df["layout_id"].tolist()
    proxy_strategies = sorted(best["strategy"].dropna().astype(str).unique().tolist())
    runbook = f"""# Strong-Baseline Direct Promotion Queue

This directory prepares the next reduced-direct promotion experiment after the same-anchor
strong-baseline pressure test. It is a runnable queue, not a completed result.

## Queue

{queue_df.to_markdown(index=False)}

## Proxy-Best Strategies Carried Into the Run

{best.loc[:, ["layout_id", "strategy"]].to_markdown(index=False)}

Unique proxy-best strategies: `{", ".join(proxy_strategies)}`.

## Recommended Core Run

The core run keeps runtime close to the previous baseline-control direct matrix while adding
the three strongest strong-baseline pressure rows.

```bash
conda run --no-capture-output -n uu python scripts/run_soltrace_sensitivity_matrix.py \\
  --run {out.relative_to(ROOT)} \\
  --config configs/server_full.json \\
  --pysoltrace-dir /home/kk/projects/paper/tools/SolTrace/app/deploy/api \\
  --layout-ids {",".join(core_ids)} \\
  --days 20,80,110,140,172,200,230,266,326 \\
  --hours 10,12,14 \\
  --base-strategies visible_equator,five_point \\
  --include-proxy-union \\
  --out {out.relative_to(ROOT)}/soltrace_core_27cond_20260523 \\
  --max-heliostats 6000 \\
  --rays 60000 \\
  --threads 16 \\
  --receiver-panels 18 \\
  --receiver-nx 20 \\
  --receiver-ny 60 \\
  --seed 2026052311
```

## Optional Extended Run

The extended run also includes `L_opt` as an optical stress case and `J_gain` as a
proxy/direct mismatch case.

```bash
conda run --no-capture-output -n uu python scripts/run_soltrace_sensitivity_matrix.py \\
  --run {out.relative_to(ROOT)} \\
  --config configs/server_full.json \\
  --pysoltrace-dir /home/kk/projects/paper/tools/SolTrace/app/deploy/api \\
  --layout-ids {",".join(extended_ids)} \\
  --days 20,80,110,140,172,200,230,266,326 \\
  --hours 10,12,14 \\
  --base-strategies visible_equator,five_point \\
  --include-proxy-union \\
  --out {out.relative_to(ROOT)}/soltrace_extended_27cond_20260523 \\
  --max-heliostats 6000 \\
  --rays 60000 \\
  --threads 16 \\
  --receiver-panels 18 \\
  --receiver-nx 20 \\
  --receiver-ny 60 \\
  --seed 2026052312
```

## Claim Boundary

Only write these results into the manuscript after the direct matrix is actually completed
and aggregated. The expected scientific question is not whether TS-FPDA is SOTA. It is whether
the role-level queue remains useful when literature-inspired strong baselines are promoted
through the same reduced direct gate.
"""
    (out / "STRONG_BASELINE_DIRECT_PROMOTION_RUNBOOK.md").write_text(runbook, encoding="utf-8")


def main() -> int:
    args = parse_args()
    strong_run = resolve(args.strong_run)
    joint_run = resolve(args.joint_run)
    out = resolve(args.out)
    (out / "layouts").mkdir(parents=True, exist_ok=True)
    (out / "aiming_proxy").mkdir(parents=True, exist_ok=True)
    (out / "tables").mkdir(parents=True, exist_ok=True)

    source_paths = []
    for row in QUEUE:
        source_paths.append(copy_layout(row["layout_id"], row["source"], strong_run, joint_run, out))

    queue_df = pd.DataFrame(QUEUE)
    queue_df["source_layout_path"] = source_paths
    queue_df.to_csv(out / "tables" / "direct_promotion_queue.csv", index=False)

    best = read_best_strategy(strong_run, joint_run)
    best.to_csv(out / "aiming_proxy" / "best_aiming_by_layout.csv", index=False)

    core_ids = queue_df.loc[queue_df["tier"] == "core", "layout_id"].tolist()
    extended_ids = queue_df["layout_id"].tolist()
    (out / "tables" / "layout_ids_core.txt").write_text(",".join(core_ids) + "\n", encoding="utf-8")
    (out / "tables" / "layout_ids_extended.txt").write_text(",".join(extended_ids) + "\n", encoding="utf-8")

    run_config = {
        "run_id": out.name,
        "purpose": "Next same-run reduced-direct promotion queue after the same-anchor strong-baseline pressure test.",
        "strong_run": str(strong_run),
        "joint_run": str(joint_run),
        "core_layout_ids": core_ids,
        "extended_layout_ids": extended_ids,
        "recommended_days": [20, 80, 110, 140, 172, 200, 230, 266, 326],
        "recommended_hours": [10, 12, 14],
        "recommended_base_strategies": ["visible_equator", "five_point"],
        "include_proxy_union": True,
        "recommended_reduced_direct_settings": {
            "max_heliostats": 6000,
            "rays": 60000,
            "threads": 16,
            "receiver_panels": 18,
            "receiver_nx": 20,
            "receiver_ny": 60,
            "seed_core": 2026052311,
            "seed_extended": 2026052312,
        },
        "claim_boundary": "Runnable queue only; do not write as result until the direct matrix is complete.",
    }
    (out / "run_config.json").write_text(json.dumps(run_config, indent=2), encoding="utf-8")
    write_runbook(out, queue_df, best)
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
