# Joint Layout--Aiming Optimizer Report

This run adds an integrated screening layer above the earlier defensive audits. It searches bounded full-field layout deformation parameters and receiver-aiming strategies under one scalarized objective, then exports a Pareto queue for later direct ray-tracing checks.

## Run Scale

- Candidates evaluated: 489
- Generations: 4
- Publishable geometry candidates: 489
- Joint Pareto candidates: 121
- Aiming strategies tested per candidate: 23
- Baseline best strategy: staggered_levels:9:0.380:5
- Baseline best peak-to-active-mean proxy: 1.5535

## Best Joint Candidate

- Candidate: `joint_g04_0478`
- Strategy: `staggered_levels:9:0.380:5`
- Optical-proxy change: -0.195%
- Best-aiming peak-to-active-mean change: -7.222%
- Spillage proxy change: +0.002 percentage points
- Layout quality score: 0.991
- Minimum nearest-neighbour spacing: 16.84 m

## Representative Queue

| joint_role | candidate_id | delta_energy_pct | delta_peak_to_mean_pct_vs_baseline_best | delta_spillage_pctpt_vs_baseline_best | best_strategy | layout_quality_score |
| --- | --- | --- | --- | --- | --- | --- |
| baseline | baseline_full | 0.000 | 0.000 | 0.000 | staggered_levels:9:0.380:5 | 1.000 |
| J_flux_receiver_boundary | joint_g04_0478 | -0.195 | -7.222 | 0.002 | staggered_levels:9:0.380:5 | 0.991 |
| J_bal_no_energy_loss | joint_g02_0333 | 0.002 | -4.316 | -0.024 | staggered_levels:9:0.380:2 | 0.973 |
| J_gain_receiver_gate | joint_g02_0303 | 0.091 | -3.468 | -0.010 | staggered_levels:9:0.380:3 | 0.965 |
| max_energy_receiver_gate | joint_g00_0097 | 0.134 | -0.075 | 0.000 | staggered_levels:9:0.380:5 | 0.970 |
| min_spillage | joint_g01_0254 | -0.091 | 0.930 | -0.037 | staggered_levels:9:0.380:0 | 1.000 |
| max_geometry_quality | joint_g04_0444 | -0.297 | -6.324 | 0.001 | staggered_levels:9:0.380:5 | 1.000 |
| joint_extra | joint_g03_0355 | -0.203 | -6.542 | 0.000 | staggered_levels:9:0.380:5 | 0.995 |

## Interpretation Boundary

This is a joint screening optimizer, not annual commercial certification. The positive contribution is architectural: layout generation and receiver aiming are now selected in the same loop, instead of being optimized in separated modules. The exported representatives should be sent to reduced direct PySolTrace or CoPylot/SolarPILOT custom-aimpoint validation before any claim of robust receiver-risk reduction is made.
