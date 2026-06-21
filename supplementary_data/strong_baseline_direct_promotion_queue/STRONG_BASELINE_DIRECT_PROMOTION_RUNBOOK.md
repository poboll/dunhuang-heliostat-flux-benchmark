# Strong-Baseline Direct Promotion Queue

This directory prepares the next reduced-direct promotion experiment after the same-anchor
strong-baseline pressure test. It is a runnable queue, not a completed result.

## Queue

| layout_id              | symbol   | role                                       | source   | tier     | reason                                                                                                             | source_layout_path                                                                                                                                     |
|:-----------------------|:---------|:-------------------------------------------|:---------|:---------|:-------------------------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------|
| baseline_full          | L0       | paired baseline                            | strong   | core     | Reference field for paired receiver-risk deltas.                                                                   | /Users/Apple/Developer/paper/dunhuang-heliostat-rebuild-server/server_outputs/same_anchor_strong_baselines_20260523/layouts/baseline_full.csv          |
| deform_0893            | L_nom    | held-out TS-FPDA nominal candidate         | strong   | core     | Nominal TS-FPDA row with prior held-out/direct support.                                                            | /Users/Apple/Developer/paper/dunhuang-heliostat-rebuild-server/server_outputs/same_anchor_strong_baselines_20260523/layouts/deform_0893.csv            |
| deform_1387            | L_rob    | held-out TS-FPDA receiver-risk candidate   | strong   | core     | Receiver-risk TS-FPDA row with the clearest prior held-out support.                                                | /Users/Apple/Developer/paper/dunhuang-heliostat-rebuild-server/server_outputs/same_anchor_strong_baselines_20260523/layouts/deform_1387.csv            |
| ctrl_radial_expand_015 | C_rad+   | simple radial-control baseline             | strong   | core     | Low-complexity control that should remain in the benchmark.                                                        | /Users/Apple/Developer/paper/dunhuang-heliostat-rebuild-server/server_outputs/same_anchor_strong_baselines_20260523/layouts/ctrl_radial_expand_015.csv |
| joint_g04_0478         | J_flux   | joint receiver-boundary candidate          | strong   | core     | Direct-supported receiver-boundary row from the joint audit.                                                       | /Users/Apple/Developer/paper/dunhuang-heliostat-rebuild-server/server_outputs/same_anchor_strong_baselines_20260523/layouts/joint_g04_0478.csv         |
| joint_g02_0333         | J_bal    | joint balance hypothesis                   | strong   | core     | No-energy-loss joint hypothesis; directional but uncertain in direct audit.                                        | /Users/Apple/Developer/paper/dunhuang-heliostat-rebuild-server/server_outputs/same_anchor_strong_baselines_20260523/layouts/joint_g02_0333.csv         |
| sb_hy_energy           | B_hy,E   | hybrid strong-baseline energy pressure row | strong   | core     | Best strong-baseline optical/receiver compromise: +1.74% SolarPILOT optical and -4.44% aiming-proxy concentration. | /Users/Apple/Developer/paper/dunhuang-heliostat-rebuild-server/server_outputs/same_anchor_strong_baselines_20260523/layouts/sb_hy_energy.csv           |
| sb_pf_flux             | B_pf,R   | pattern-free receiver-pressure row         | strong   | core     | Pattern-free approximation with -5.45% aiming-proxy concentration but optical loss.                                | /Users/Apple/Developer/paper/dunhuang-heliostat-rebuild-server/server_outputs/same_anchor_strong_baselines_20260523/layouts/sb_pf_flux.csv             |
| sb_hs_flux             | B_hs,R   | slider-like receiver-pressure row          | strong   | core     | Slider-like approximation with -6.67% aiming-proxy concentration but optical loss.                                 | /Users/Apple/Developer/paper/dunhuang-heliostat-rebuild-server/server_outputs/same_anchor_strong_baselines_20260523/layouts/sb_hs_flux.csv             |
| deform_0276            | L_opt    | optical stress case                        | strong   | extended | Default-bridge optical upper case; retained to quantify receiver-flux penalty.                                     | /Users/Apple/Developer/paper/dunhuang-heliostat-rebuild-server/server_outputs/same_anchor_strong_baselines_20260523/layouts/deform_0276.csv            |
| joint_g02_0303         | J_gain   | joint proxy/direct mismatch case           | joint    | extended | Energy-gated joint candidate that exposed proxy/direct strategy sensitivity.                                       | /Users/Apple/Developer/paper/dunhuang-heliostat-rebuild-server/server_outputs/joint_layout_aiming_20260523/layouts/joint_g02_0303.csv                  |

## Proxy-Best Strategies Carried Into the Run

| layout_id              | strategy                   |
|:-----------------------|:---------------------------|
| baseline_full          | staggered_levels:9:0.380:0 |
| ctrl_radial_expand_015 | staggered_levels:9:0.380:0 |
| deform_0276            | staggered_levels:9:0.380:0 |
| deform_0893            | staggered_levels:9:0.380:2 |
| deform_1387            | staggered_levels:9:0.380:1 |
| joint_g02_0333         | staggered_levels:9:0.380:0 |
| joint_g04_0478         | staggered_levels:9:0.380:6 |
| sb_hs_flux             | staggered_levels:9:0.380:2 |
| sb_hy_energy           | staggered_levels:9:0.380:2 |
| sb_pf_flux             | staggered_levels:9:0.380:8 |
| joint_g02_0303         | staggered_levels:9:0.380:3 |

Unique proxy-best strategies: `staggered_levels:9:0.380:0, staggered_levels:9:0.380:1, staggered_levels:9:0.380:2, staggered_levels:9:0.380:3, staggered_levels:9:0.380:6, staggered_levels:9:0.380:8`.

## Recommended Core Run

The core run keeps runtime close to the previous baseline-control direct matrix while adding
the three strongest strong-baseline pressure rows.

```bash
conda run --no-capture-output -n uu python scripts/run_soltrace_sensitivity_matrix.py \
  --run server_outputs/strong_baseline_direct_promotion_queue_20260523 \
  --config configs/server_full.json \
  --pysoltrace-dir /home/kk/projects/paper/tools/SolTrace/app/deploy/api \
  --layout-ids baseline_full,deform_0893,deform_1387,ctrl_radial_expand_015,joint_g04_0478,joint_g02_0333,sb_hy_energy,sb_pf_flux,sb_hs_flux \
  --days 20,80,110,140,172,200,230,266,326 \
  --hours 10,12,14 \
  --base-strategies visible_equator,five_point \
  --include-proxy-union \
  --out server_outputs/strong_baseline_direct_promotion_queue_20260523/soltrace_core_27cond_20260523 \
  --max-heliostats 6000 \
  --rays 60000 \
  --threads 16 \
  --receiver-panels 18 \
  --receiver-nx 20 \
  --receiver-ny 60 \
  --seed 2026052311
```

## Optional Extended Run

The extended run also includes `L_opt` as an optical stress case and `J_gain` as a
proxy/direct mismatch case.

```bash
conda run --no-capture-output -n uu python scripts/run_soltrace_sensitivity_matrix.py \
  --run server_outputs/strong_baseline_direct_promotion_queue_20260523 \
  --config configs/server_full.json \
  --pysoltrace-dir /home/kk/projects/paper/tools/SolTrace/app/deploy/api \
  --layout-ids baseline_full,deform_0893,deform_1387,ctrl_radial_expand_015,joint_g04_0478,joint_g02_0333,sb_hy_energy,sb_pf_flux,sb_hs_flux,deform_0276,joint_g02_0303 \
  --days 20,80,110,140,172,200,230,266,326 \
  --hours 10,12,14 \
  --base-strategies visible_equator,five_point \
  --include-proxy-union \
  --out server_outputs/strong_baseline_direct_promotion_queue_20260523/soltrace_extended_27cond_20260523 \
  --max-heliostats 6000 \
  --rays 60000 \
  --threads 16 \
  --receiver-panels 18 \
  --receiver-nx 20 \
  --receiver-ny 60 \
  --seed 2026052312
```

## Claim Boundary

Only write these results into the manuscript after the direct matrix is actually completed
and aggregated. The expected scientific question is not whether TS-FPDA is SOTA. It is whether
the role-level queue remains useful when literature-inspired strong baselines are promoted
through the same reduced direct gate.
