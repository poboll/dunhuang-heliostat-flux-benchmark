#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN = ROOT / "server_outputs" / "joint_layout_aiming_20260523"
DEFAULT_SOLARPILOT = DEFAULT_RUN / "solarpilot_joint_default"
DEFAULT_DIRECT = DEFAULT_RUN / "soltrace_joint_direct_27cond_20260523" / "analysis"

LABELS = {
    "joint_g02_0333": "$J_{bal}$",
    "joint_g02_0303": "$J_{gain}$",
    "joint_g04_0478": "$J_{flux}$",
}

ROLES = {
    "joint_g02_0333": "directional balance candidate",
    "joint_g02_0303": "strategy-sensitive energy-gated candidate",
    "joint_g04_0478": "direct-supported receiver-boundary candidate",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Merge joint proxy, SolarPILOT default-aiming, and reduced direct audit evidence."
    )
    parser.add_argument("--run", type=Path, default=DEFAULT_RUN)
    parser.add_argument("--solarpilot", type=Path, default=DEFAULT_SOLARPILOT)
    parser.add_argument("--direct-analysis", type=Path, default=DEFAULT_DIRECT)
    parser.add_argument("--out", type=Path, default=DEFAULT_RUN / "joint_system_summary")
    return parser.parse_args()


def fmt_ci(row: pd.Series) -> str:
    return f"{row['mean_delta_peak_pct']:+.2f} [{row['ci95_low_pct']:+.2f}, {row['ci95_high_pct']:+.2f}]"


def main() -> int:
    args = parse_args()
    run = args.run if args.run.is_absolute() else ROOT / args.run
    solarpilot = args.solarpilot if args.solarpilot.is_absolute() else ROOT / args.solarpilot
    direct = args.direct_analysis if args.direct_analysis.is_absolute() else ROOT / args.direct_analysis
    out = args.out if args.out.is_absolute() else ROOT / args.out
    (out / "tables").mkdir(parents=True, exist_ok=True)

    reps = pd.read_csv(run / "tables" / "joint_optimizer_representatives.csv")
    sp = pd.read_csv(solarpilot / "tables" / "solarpilot_summary.csv")
    ci = pd.read_csv(direct / "tables" / "joint_direct_bootstrap_ci.csv")

    base_sp = sp.loc[sp["layout_id"] == "baseline_full"].iloc[0]
    sp = sp.copy()
    sp["solarpilot_delta_opteff_pct"] = (sp["opteff_mean"] / base_sp["opteff_mean"] - 1.0) * 100.0
    sp["solarpilot_delta_default_flux_ratio_pct"] = (
        sp["flux_peak_to_active_mean"] / base_sp["flux_peak_to_active_mean"] - 1.0
    ) * 100.0
    sp["solarpilot_delta_active_cv_pct"] = (sp["flux_active_cv"] / base_sp["flux_active_cv"] - 1.0) * 100.0

    rows: list[dict[str, object]] = []
    for cid in LABELS:
        proxy = reps.loc[reps["candidate_id"] == cid].iloc[0]
        sp_row = sp.loc[sp["layout_id"] == cid].iloc[0]
        ci_rows = ci.loc[ci["label"].str.contains(LABELS[cid].replace("$", ""), regex=False)].copy()
        if ci_rows.empty:
            # The label column usually contains math text, but keep a robust fallback.
            ci_rows = ci.loc[ci["label"].astype(str).str.contains(cid, regex=False)].copy()
        proxy_ci = ci_rows.loc[ci_rows["view"] == "proxy-selected"].iloc[0]
        best_ci = ci_rows.loc[ci_rows["view"] == "best-direct"].iloc[0]
        rows.append(
            {
                "candidate": LABELS[cid],
                "layout_id": cid,
                "role": ROLES[cid],
                "proxy_delta_energy_pct": float(proxy["delta_energy_pct"]),
                "proxy_delta_receiver_pct": float(proxy["delta_peak_to_mean_pct_vs_baseline_best"]),
                "proxy_best_strategy": proxy["best_strategy"],
                "solarpilot_delta_opteff_pct": float(sp_row["solarpilot_delta_opteff_pct"]),
                "solarpilot_delta_default_flux_ratio_pct": float(
                    sp_row["solarpilot_delta_default_flux_ratio_pct"]
                ),
                "solarpilot_delta_active_cv_pct": float(sp_row["solarpilot_delta_active_cv_pct"]),
                "direct_proxy_strategy": proxy_ci["strategy_short"],
                "direct_proxy_delta_ci_pct": fmt_ci(proxy_ci),
                "direct_best_strategy": best_ci["strategy_short"],
                "direct_best_delta_ci_pct": fmt_ci(best_ci),
                "direct_lower_fraction": float(best_ci["share_lower_peak"]),
            }
        )

    summary = pd.DataFrame(rows)
    summary.to_csv(out / "tables" / "joint_system_evidence_summary.csv", index=False)

    lines = [
        "# Joint Layout--Aiming System Evidence Summary",
        "",
        "This report merges three evidence layers for the joint representatives: proxy-level joint screening,",
        "PySAM/SolarPILOT default-aiming layout checks, and the reduced PySolTrace direct-promotion audit.",
        "The SolarPILOT bridge is not a custom-aimpoint validation; it tests whether the joint layouts remain",
        "optically plausible under the same default-aiming settings used for the earlier representatives.",
        "",
        summary.to_markdown(index=False, floatfmt=".3f"),
        "",
        "Interpretation: `J_bal` and `J_gain` are not merely proxy-energy artifacts because they also increase",
        "SolarPILOT default optical efficiency, but both increase default receiver concentration and therefore",
        "still require direct custom-aimpoint promotion. `J_flux` is the direct-supported receiver-boundary",
        "candidate, but it sacrifices optical efficiency under both proxy and SolarPILOT default checks.",
    ]
    (out / "JOINT_SYSTEM_EVIDENCE_SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
