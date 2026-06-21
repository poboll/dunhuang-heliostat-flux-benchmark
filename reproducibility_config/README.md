# Reproducibility Configuration

This folder records the configuration needed to rerun or audit the strict-review rescue draft.

## Files

- `server_full.json`: audited plant, weather, terrain, deformation, and screening configuration.
- `PARAMETER_REGISTRY.md`: paper-facing parameter registry extracted from the actual scripts and run configuration.
- `requirements.txt`: Python package floor versions used by the local run.
- `environment.yml`: Conda environment recipe for a clean rerun.
- `../code/scripts/run_baseline_comparison.py`: generator and aggregator for the same-condition low-complexity baseline controls added during the strict-review strengthening pass.
- `../code/scripts/build_baseline_direct_soltrace_report.py`: manuscript-facing aggregation, bootstrap CI, and figure builder for the reduced direct baseline-control audit.
- `../code/scripts/build_baseline_direct_holdout_report.py`: leave-one-day-out strategy-selection audit for the reduced direct baseline-control matrix.
- `../code/scripts/build_missing20_geometry_sensitivity.py`: random-omission geometry sensitivity audit for the 20-coordinate gap between the available coordinate pool and the public plant count.
- `../code/scripts/run_joint_layout_aiming_optimizer.py`: integrated screening layer that selects bounded full-field layout deformations and receiver-aiming strategies in one loop.
- `../code/scripts/run_solarpilot_validation.py`: PySAM/SolarPILOT default-aiming bridge used for the earlier representative layouts and the joint candidate bridge.
- `../code/scripts/build_fast_annual_proxy_and_sanity.py`: annualization and plant-scale sanity bridge that interpolates SolarPILOT default-aiming optical-efficiency tables over the public 8760-hour weather file and calibrates the baseline proxy to the public 351.6 GWh Dunhuang design-generation reference.
- `../code/scripts/build_multi_year_annual_proxy_gate.py`: multi-year annual-proxy robustness gate over NASA POWER 2020--2025 weather files.
- `../code/scripts/build_annual_interpolation_robustness_gate.py`: annual-proxy interpolation robustness gate over nearest-neighbour, IDW-3, IDW-6, IDW-12, and linear interpolation with nearest fallback.
- `../code/scripts/build_flux_resolution_gate.py`: SolarPILOT default-flux receiver-bin resolution gate comparing 24 x 24 and 36 x 36 receiver maps.
- `../code/scripts/build_flux_day_sampling_gate.py`: SolarPILOT default-flux sampling gate comparing the original 8-flux-day receiver maps with a 12-flux-day rerun.
- `../code/scripts/build_strong_baseline_promotion_gate.py`: conservative writeback gate that merges the prepared strong-baseline queue with annual, default-flux, flux-day, aiming-proxy, geometry, and completed reduced-direct evidence.
- `../code/scripts/build_strong_baseline_direct_soltrace_report.py`: same-run reduced PySolTrace aggregation, bootstrap CI, best-direct/proxy-selected comparison, and writeback gate for the strong-baseline direct-promotion matrix.
- `../code/scripts/remote_strong_baseline_direct_recover.sh`: operator script that syncs the direct-report builder to the server, counts completed condition summaries, runs the direct gate, and prints remote resource status after SSH control access is available.
- `../code/scripts/build_joint_system_summary.py`: merge table for joint proxy screening, SolarPILOT default-aiming bridge, and reduced direct promotion evidence.
- `../code/scripts/build_joint_direct_soltrace_report.py`: aggregation, bootstrap CI, and figure builder for the reduced direct promotion audit of joint layout--aiming representatives.
- `../code/scripts/build_formal_paired_statistics.py`: paired condition-level statistics for selected reduced direct rows, including bootstrap CI, Hodges--Lehmann shifts, sign/Wilcoxon tests, and the +/-1% practical-indistinguishability threshold.
- `../code/scripts/build_geometry_explainability_and_advantage.py`: geometry-explainability and constrained-advantage audit for selected TS-FPDA, joint, control, and strong-baseline rows.
- `../code/scripts/run_soltrace_condition_worker.py`: condition-level worker used to complete the server-side direct PySolTrace matrix without overlapping output directories.

## Minimal Local Setup

```bash
conda env create -f environment.yml
conda activate dunhuang-heliostat-benchmark
python -m pytest -q
```

The submission package is a release-candidate archive. The GitHub release URL is listed in the manuscript data availability statement. Before journal submission, the author should mint a Zenodo DOI from the release if the target journal requires DOI-bearing code/data deposition.

The same-condition baseline-control tables are included under `../supplementary_data/baseline_strengthening_tables/`. They preserve the same 11,915-heliostat coordinate pool and compare six simple controls with the TS-FPDA representatives under the same SolarPILOT and aiming-proxy settings.

The reduced direct baseline-control audit is included under `../supplementary_data/baseline_direct_soltrace_tables/`. It compares three simple controls and four TS-FPDA representatives against the same baseline over 27 representative solar conditions and seven direct aiming strategies. The package also includes a leave-one-day-out strategy-selection audit, where each representative day is held out after selecting the strategy on the other eight days. These audits are useful for claim boundary, role-level queue checking, and selection-bias control; they remain sampled PySolTrace layers rather than full-field annual custom-aimpoint certification.

The coordinate-provenance sensitivity audit is included under `../supplementary_data/missing20_geometry_sensitivity/`. It does not synthesize the 20 unavailable records. It repeats random 20-heliostat omissions from the available 11,915-coordinate pool to quantify how much basic field-geometry descriptors move under an omission of the same size.

The joint layout--aiming screening outputs are included under `../supplementary_data/joint_layout_aiming_optimizer/`. This layer evaluates 489 full-field candidates, searches 23 aiming strategies for each candidate, exports 121 joint Pareto rows, and reports representatives such as `J_bal` and `J_gain`. The SolarPILOT default-aiming bridge for the joint layouts is included under `../supplementary_data/joint_solarpilot_default_tables/`; it shows that `J_bal` and `J_gain` are optically positive under the common SolarPILOT bridge while also increasing default receiver concentration. The reduced direct follow-up is included under `../supplementary_data/joint_direct_soltrace_tables/`; it compares baseline, `J_bal`, `J_gain`, and `J_flux` over 27 representative solar conditions and five direct aiming strategies. The merged evidence table is stored under `../supplementary_data/joint_system_summary/`. It promotes `J_flux` as a receiver-boundary candidate while treating `J_bal` and `J_gain` as directional or strategy-sensitive hypotheses, not annual optima.

The formal paired-statistics audit is included under `../supplementary_data/formal_paired_statistics/`. It treats each selected reduced direct row as 27 paired condition-level deltas against the same baseline and reports bootstrap confidence intervals, Hodges--Lehmann shifts, one-sided sign tests, one-sided Wilcoxon tests, and a +/-1 percentage-point practical-indistinguishability threshold. This audit strengthens the claim boundary: it supports `J_flux`, `L_rob`, and the V12 `L_nom` row as the clearest receiver-risk candidates, but it does not justify final engineering superiority.

The geometry-explainability and constrained-advantage audit is included under `../supplementary_data/geometry_explainability_advantage/`. It reports radial-density shifts, azimuth-sector population shifts, nearest-neighbour spacing, per-heliostat displacement distributions, movement-direction rose curves, and a constrained evidence-role table that combines annual proxy, default SolarPILOT flux, aiming proxy, AFD-style hotspot-area proxy, and reduced-direct confidence intervals. This audit explains how selected layouts move while keeping the result at role-level benchmark strength rather than a SOTA ranking.

The fast annual proxy and public plant sanity check is included under `../supplementary_data/fast_annual_proxy_sanity/`. It interpolates each SolarPILOT default-aiming optical-efficiency table across the NASA POWER 2023 weather year, keeps the annual comparison relative to the same public-weather profile, uniformly scales annual DNI from 1842.4 to 1883.0 kWh m^-2 y^-1, and uses the 351.6 GWh public Dunhuang design-generation reference only to calibrate a baseline net electric conversion factor. This bridge supports annualized optical ranking and plant-scale order-of-magnitude checking; it is not a dispatch model, bankable annual yield, or full annual custom-aimpoint ray trace.

The multi-year annual-proxy robustness gate is included under `../supplementary_data/multiyear_annual_proxy_gate/`. It repeats the annual-proxy calculation over NASA POWER 2020--2025 weather files and reports whether selected role signs and annual ranks are stable. This is a weather-year robustness check only, not measured annual operation.

The annual-proxy interpolation robustness gate is included under `../supplementary_data/annual_interpolation_robustness_gate/`. It repeats the same default-aiming annual-proxy calculation with nearest-neighbour, IDW-3, IDW-6, IDW-12, and linear interpolation with nearest fallback across the NASA POWER 2020--2025 weather files. The gate supports a short interpolation-robustness statement only; it is not annual custom-aimpoint validation.

The SolarPILOT flux-resolution gate is included under `../supplementary_data/flux_resolution_gate/`. It compares the existing 24 x 24 default receiver-flux tables with a 36 x 36 rerun for the direct-promotion queue layouts. This reduces receiver-bin discretization concern but does not certify receiver thermal safety.

The SolarPILOT flux-day sampling gate is included under `../supplementary_data/flux_day_sampling_gate/`. It compares the original eight-flux-day default receiver-flux tables with a twelve-flux-day rerun for the selected direct-promotion layouts. The gate supports a short default-flux sampling-robustness statement only; it is not annual custom aiming, cross-code validation, or receiver thermal certification.

The strong-baseline promotion gate is included under `../supplementary_data/strong_baseline_promotion_gate/`, and the completed same-run reduced direct matrix is archived under `../supplementary_data/strong_baseline_direct_soltrace_tables/`. The 27-condition follow-up did not promote `B_hy,E`, `B_pf,R`, or `B_hs,R`: their proxy-selected direct rows are adverse or uncertain under the bootstrap-CI rule. These files are meant to prevent screening-level rows from being promoted into unsupported main-text claims.

The same-run strong-baseline direct-report script is included for the active server follow-up. It should be run after the 27 condition directories exist under `strong_baseline_direct_promotion_queue_20260523/soltrace_core_27cond_20260524`. The safe writeback rule is intentionally conservative: a strong-baseline row can enter the manuscript as a new same-run direct-supported role only when the complete matrix gives a proxy-selected 95% bootstrap confidence interval below zero. If only a best-direct alternative strategy passes, the result should be written as strategy sensitivity, not as proxy-selected promotion. Incomplete, weak, or adverse rows should remain supplementary/internal evidence.

## Claim Boundary

The files support rerunning the benchmark workflow and checking tables/figures against the manifest. They do not provide plant-grade weather, survey-grade terrain, receiver thermal certification, full annual custom-aimpoint certification, dispatch modeling, or commercial retrofit evidence.
