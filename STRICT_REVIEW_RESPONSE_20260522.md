# Strict Review Rescue Response - 2026-05-22

## Editorial Decision

The manuscript should not be downgraded immediately, but the current claim must be tightened. The rescue version reframes the paper as a receiver-flux-aware reproducible layout--aiming benchmark, not as a final optimal heliostat-field redesign.

## Point-by-Point Actions

| Review concern | Action taken in v8 rescue draft | Remaining risk |
|---|---|---|
| Novelty is unclear and petal deformation alone is not enough. | Retitled the paper and added a nearest-work positioning matrix that explicitly states the contribution as a public plant-anchored layout--aiming benchmark. Added six same-condition low-complexity baseline controls: radial compaction/expansion, ellipse scaling, north bias, radial wave, and azimuth stagger. | These are control baselines, not literature reimplementations; full external SOTA baselines remain future work. |
| Paper-alone reproducibility is incomplete. | Added a main-text Parameter Registry and created `reproducibility_config/README.md`, `environment.yml`, and `PARAMETER_REGISTRY.md`. | Final package still needs Zenodo DOI before submission. |
| Coordinate provenance and the 20-heliostat count gap need quantification. | Added a seeded missing-20 random-omission geometry audit with 2000 replicates and copied the report/tables into the supplementary package. | The unavailable records are still not reconstructed; this only quantifies geometry sensitivity. |
| Validation is mostly reduced/proxy. | Added a main-text Domain of Validity table and kept proxy, SolarPILOT, reduced PySolTrace, and future full-field annual checks separate. | Full-field annual custom-aimpoint validation remains future work. |
| UQ/CI is insufficient. | Added `code/scripts/build_v12_bootstrap_ci.py`, generated `v12_bootstrap_ci.csv`, and wrote a V12 bootstrap confidence table into the results. | CI results are intentionally cautious and do not turn the study into a final optimum paper. |
| Strong baselines may explain the result. | Added a direct baseline-control PySolTrace audit for the baseline, three simple controls, and four TS-FPDA representatives across 27 solar conditions and seven aiming strategies. | The audit supports role-level TS-FPDA usefulness but confirms that simple controls remain meaningful and must stay in the benchmark. |
| Strategy selection and reporting use the same reduced direct conditions. | Added a leave-one-day-out direct-ray hold-out audit: each representative day is held out, the strategy is selected on the other eight days, and the selected row is evaluated on the held-out day. | This reduces selection optimism but remains a representative-condition audit, not annual custom aiming. |
| The paper was becoming defensive rather than a complete optimization system. | Added a joint layout--aiming screening layer that evaluates 489 full-field candidates, tests 23 aiming strategies per candidate, exports 121 joint Pareto rows, and separates `J_flux`, `J_bal`, and `J_gain` roles. Added a reduced direct promotion audit for the joint representatives. | `J_flux` is direct-supported as a receiver-boundary candidate; `J_bal` and `J_gain` remain directional or strategy-sensitive hypotheses. Full annual custom aiming remains future work. |
| Main claim sounds too strong. | Abstract, cover letter, and data statement now emphasize benchmark/screening queue and explicitly reject commercial redesign claims. | The introduction still needs one more human-language polish pass before submission. |
| Submission materials are incomplete. | Updated highlights, cover letter, and data availability statement to match the strict-review positioning. | Graphical abstract and Zenodo DOI remain author-finalization tasks. |

## Evidence Added

- V12 240k-ray bootstrap CI: `supplementary_data/soltrace_v12_seed240k_tables/v12_bootstrap_ci.csv`
- V12 bootstrap report: `supplementary_data/soltrace_v12_seed240k_tables/V12_BOOTSTRAP_CI_REPORT.md`
- Main-text Table: V12 bootstrap confidence audit.
- Main-text Table: nearest-work positioning matrix.
- Main-text Table: parameter registry.
- Main-text Table: domain of validity.
- Main-text Table and Figure: same-condition baseline controls.
- Baseline-control tables: `supplementary_data/baseline_strengthening_tables/baseline_comparison_integrated.csv`
- Joint layout--aiming screening tables: `supplementary_data/joint_layout_aiming_optimizer/`
- Joint direct promotion audit tables: `supplementary_data/joint_direct_soltrace_tables/`
- Main-text Table and Figure: reduced direct baseline-control audit.
- Direct baseline-control audit tables: `supplementary_data/baseline_direct_soltrace_tables/`
- Missing-20 geometry sensitivity audit: `supplementary_data/missing20_geometry_sensitivity/`

## Current Submission Judgment

The paper is stronger than a downgraded technical note because it now has a coherent benchmark contribution, but it is still high-risk for direct Solar Energy submission unless the final DOI, package audit, and one more text/figure polish pass are completed. The honest claim is:

> A reproducible full-field Dunhuang layout--aiming benchmark with receiver-flux-aware screening and bounded reduced direct checks.

The paper should not claim:

- SOTA optimizer
- certified receiver thermal safety
- final commercial redesign
- plant retrofit recommendation
- LCOE/economic superiority

## 2026-05-22 Baseline Strengthening Addendum

The new baseline-control pass directly addresses the reviewer concern that TS-FPDA might only reproduce simple global geometry effects. Six low-complexity controls were generated while preserving the same 11,915-heliostat coordinate pool and evaluated with the same PySAM/SolarPILOT and aiming-proxy settings. The result is deliberately nuanced:

- Best simple optical control: radial compaction, +0.89% SolarPILOT optical efficiency and +1.07% default flux-ratio penalty.
- Best simple default-flux control: radial expansion, -1.04% default flux ratio but -0.89% optical efficiency.
- Best simple aiming-proxy control: radial wave, -2.38% proxy peak-to-mean change with nearly neutral optical change.
- TS-FPDA representatives still dominate the simple controls in the tested role-based queue: `L_opt` gives +3.15% optical efficiency, while `L_nom`, `L_opt`, and `L_rob` give -6.22%, -5.48%, and -5.34% aiming-proxy changes.

This strengthens the manuscript as a benchmark/workflow paper, but it does not justify a SOTA or commercial-redesign claim.

## 2026-05-23 Direct Baseline-Control Addendum

The proxy/SolarPILOT baseline-control pass has now been followed by a reduced PySolTrace direct audit. The audit compares `baseline_full`, three simple controls (`C_rad-`, `C_rad+`, `C_wave`), and four TS-FPDA representatives over 27 representative solar conditions and seven aiming strategies. Each case uses 6,000 sampled heliostats, 60,000 requested first-stage ray hits, an 18-panel receiver approximation, and 20 x 60 bins per panel.

The direct result is useful but deliberately not overclaimed:

- Simple controls remain real competitors: `C_rad+` gives a -2.43% best-direct mean peak-to-active-mean change, and `C_wave` gives -2.30%, although their bootstrap CIs cross zero.
- `L_rob` is the strongest direct best-row in this audit: -3.61% mean change, 95% bootstrap CI [-6.17%, -0.97%], lower-peak fraction 0.59.
- `L_nom` is close at -3.49%, but its 95% CI [-7.15%, +0.09%] touches zero.
- Proxy-selected rows are not reliable enough to prescribe final phases: `L_nom` and `L_opt` become positive under proxy-selected direct rows in this audit.

This addendum strengthens the paper because it directly tests the strongest baseline criticism. It also makes the claim narrower: TS-FPDA is a role-level benchmark generator and screening queue, not a uniformly superior optimizer.

## 2026-05-23 Leave-One-Day-Out Hold-Out Addendum

The reduced direct baseline-control audit has now been extended with a strategy-selection hold-out test. For each non-baseline layout, one representative day is held out, the best aiming strategy is selected from the other eight days, and the selected strategy is evaluated on the held-out day. This directly addresses the review concern that a best-row table can overstate improvement when the same matrix is used for both selection and reporting.

The hold-out result narrows the claims:

- `L_rob` remains the strongest held-out row: -3.61% mean peak-to-active-mean change, 95% day-bootstrap CI [-5.19%, -1.89%], lower-day fraction 0.89.
- `L_nom` also remains supported: -3.49% mean change, 95% CI [-5.77%, -1.38%], lower-day fraction 0.78.
- `C_rad+` becomes directional but uncertain: -1.07% mean change, 95% CI [-4.61%, +1.93%].
- `C_rad-`, `C_wave`, `L_opt`, and `L_ctrl` become positive on held-out days, so they must not be described as general receiver-risk reductions from this layer.

This is a useful hardening result because it confirms that the receiver-risk queue is not just a full-matrix best-row artifact for `L_rob` and `L_nom`, while also showing that several apparently favourable rows were selection-optimistic. The paper now explicitly reports this as a selection-bias control, not as final annual custom-aimpoint proof.

## 2026-05-23 Joint Layout--Aiming Direct Promotion Addendum

The joint layout--aiming optimizer has now been followed by a reduced direct PySolTrace promotion audit. The audit compares `baseline_full`, `J_bal` (`joint_g02_0333`), `J_gain` (`joint_g02_0303`), and `J_flux` (`joint_g04_0478`) over 27 representative solar conditions and five direct aiming strategies. Each case uses 6,000 sampled heliostats, 60,000 requested first-stage ray hits, an 18-panel receiver approximation, and 20 x 60 bins per panel.

The direct result makes the system contribution stronger but more honest:

- `J_flux` is promoted as a receiver-boundary candidate: -4.06% mean peak-to-active-mean change, 95% bootstrap CI [-6.99%, -0.94%], lower-condition fraction 0.74. It is not a headline winner because its proxy optical contribution is slightly negative.
- `J_bal` remains a directional no-energy-loss balance hypothesis: -1.98% mean direct change, but its CI [-6.55%, +3.10%] crosses zero.
- `J_gain` exposes proxy/direct strategy mismatch: its proxy-selected S9-p3 row is adverse (+2.58% mean), while S9-p2 is directionally lower (-2.49%) but uncertain.

This addendum moves the paper beyond purely defensive revision. The manuscript now contains an integrated candidate-generation system and a direct promotion gate. The correct claim is not that the joint optimizer has found a final plant optimum, but that it generates a reproducible queue in which receiver-boundary, balance, and strategy-sensitivity roles can be tested by higher-fidelity optical engines.
