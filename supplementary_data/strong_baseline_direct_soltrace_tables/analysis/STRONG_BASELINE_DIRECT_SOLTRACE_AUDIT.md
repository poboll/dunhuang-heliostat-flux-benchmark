# Strong-Baseline Same-Run Direct SolTrace Audit

This report aggregates the same-run reduced PySolTrace matrix for the strong-baseline direct-promotion queue.
It is a writeback gate: a result is promoted only when the complete matrix supports the proxy-selected layout--aiming row.

## Completion

- Completed conditions: 27 / 27.
- Missing conditions: `[]`.
- Complete matrix: `True`.

## Gate Decision

- Newly supported strong-baseline rows: `[]`.
- Non-promoted or adverse strong-baseline rows: `['sb_hy_energy', 'sb_pf_flux', 'sb_hs_flux']`.
- Main-text writeback allowed: `False`.
- Safe rule: Write new strong-baseline claims only when the complete same-run direct matrix gives a proxy-selected 95% bootstrap CI below zero. Otherwise keep rows as supplementary or internal evidence.

## Gate Summary

| symbol | layout_id | role | tier | proxy_strategy_short | proxy_cases | proxy_mean_delta_peak_pct | proxy_ci95_low_pct | proxy_ci95_high_pct | best_strategy_short | best_mean_delta_peak_pct | best_ci95_low_pct | best_ci95_high_pct | direct_promotion_status | writeback_recommendation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| L0 | baseline_full | paired baseline | core | nan | nan | nan | nan | nan | nan | nan | nan | nan | paired_baseline | reference_only |
| L_nom | deform_0893 | held-out TS-FPDA nominal candidate | core | S9-p2 | 27.000 | 4.734 | 0.484 | 9.146 | visible | -0.363 | -3.528 | 2.795 | not_supported_or_adverse | do_not_write_main_text |
| L_rob | deform_1387 | held-out TS-FPDA receiver-risk candidate | core | S9-p1 | 27.000 | 0.965 | -3.786 | 5.664 | five-point | 0.217 | -3.976 | 4.629 | not_supported_or_adverse | do_not_write_main_text |
| C_rad+ | ctrl_radial_expand_015 | simple radial-control baseline | core | S9-p0 | 27.000 | -0.443 | -5.640 | 4.737 | S9-p0 | -0.443 | -5.612 | 4.749 | directional_not_promoted | supplementary_directional_only |
| J_flux | joint_g04_0478 | joint receiver-boundary candidate | core | S9-p6 | 27.000 | 4.632 | 0.119 | 9.167 | S9-p1 | -2.270 | -6.628 | 1.867 | not_supported_or_adverse | do_not_write_main_text |
| J_bal | joint_g02_0333 | joint balance hypothesis | core | S9-p0 | 27.000 | -1.342 | -5.442 | 2.432 | S9-p0 | -1.342 | -5.379 | 2.543 | directional_not_promoted | supplementary_directional_only |
| B_hy,E | sb_hy_energy | hybrid strong-baseline energy pressure row | core | S9-p2 | 27.000 | 7.250 | 4.386 | 10.240 | S9-p1 | -0.533 | -4.752 | 3.965 | not_supported_or_adverse | do_not_write_main_text |
| B_pf,R | sb_pf_flux | pattern-free receiver-pressure row | core | S9-p8 | 27.000 | 4.781 | 1.753 | 7.910 | S9-p1 | -0.508 | -5.246 | 4.319 | not_supported_or_adverse | do_not_write_main_text |
| B_hs,R | sb_hs_flux | slider-like receiver-pressure row | core | S9-p2 | 27.000 | 3.238 | 0.130 | 6.310 | S9-p1 | -0.269 | -4.942 | 4.521 | not_supported_or_adverse | do_not_write_main_text |

## Bootstrap Rows

| view | label | layout_id | strategy_short | cases | mean_delta_peak_pct | ci95_low_pct | ci95_high_pct | share_lower_peak | median_delta_intercept_pctpt |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| proxy-selected | $L_{nom}$ | deform_0893 | S9-p2 | 27 | 4.734 | 0.484 | 9.146 | 0.296 | -0.155 |
| proxy-selected | $L_{rob}$ | deform_1387 | S9-p1 | 27 | 0.965 | -3.786 | 5.664 | 0.444 | -0.092 |
| proxy-selected | $C_{rad+}$ | ctrl_radial_expand_015 | S9-p0 | 27 | -0.443 | -5.640 | 4.737 | 0.519 | -0.430 |
| proxy-selected | $J_{flux}$ | joint_g04_0478 | S9-p6 | 27 | 4.632 | 0.119 | 9.167 | 0.407 | -0.590 |
| proxy-selected | $J_{bal}$ | joint_g02_0333 | S9-p0 | 27 | -1.342 | -5.442 | 2.432 | 0.556 | 0.042 |
| proxy-selected | $B_{hy,E}$ | sb_hy_energy | S9-p2 | 27 | 7.250 | 4.386 | 10.240 | 0.222 | 0.888 |
| proxy-selected | $B_{pf,R}$ | sb_pf_flux | S9-p8 | 27 | 4.781 | 1.753 | 7.910 | 0.333 | -0.527 |
| proxy-selected | $B_{hs,R}$ | sb_hs_flux | S9-p2 | 27 | 3.238 | 0.130 | 6.310 | 0.148 | -0.477 |
| best-direct | $L_{nom}$ | deform_0893 | visible | 27 | -0.363 | -3.528 | 2.795 | 0.481 | -0.123 |
| best-direct | $L_{rob}$ | deform_1387 | five-point | 27 | 0.217 | -3.976 | 4.629 | 0.556 | -0.127 |
| best-direct | $C_{rad+}$ | ctrl_radial_expand_015 | S9-p0 | 27 | -0.443 | -5.612 | 4.749 | 0.519 | -0.430 |
| best-direct | $J_{flux}$ | joint_g04_0478 | S9-p1 | 27 | -2.270 | -6.628 | 1.867 | 0.481 | -0.743 |
| best-direct | $J_{bal}$ | joint_g02_0333 | S9-p0 | 27 | -1.342 | -5.379 | 2.543 | 0.556 | 0.042 |
| best-direct | $B_{hy,E}$ | sb_hy_energy | S9-p1 | 27 | -0.533 | -4.752 | 3.965 | 0.667 | 0.852 |
| best-direct | $B_{pf,R}$ | sb_pf_flux | S9-p1 | 27 | -0.508 | -5.246 | 4.319 | 0.407 | -0.652 |
| best-direct | $B_{hs,R}$ | sb_hs_flux | S9-p1 | 27 | -0.269 | -4.942 | 4.521 | 0.519 | -0.527 |

## Manuscript Use

- If the matrix is incomplete, do not write new claims into the manuscript.
- If a strong-baseline proxy-selected row has a complete 95% CI below zero, it can be written as a same-run direct-supported role, not as a final plant redesign.
- If only a best-direct alternative strategy passes, write it as strategy sensitivity and keep the proxy-selected queue claim bounded.
- Weak, adverse, or incomplete rows should remain supplementary/internal and should not be used to inflate novelty.
