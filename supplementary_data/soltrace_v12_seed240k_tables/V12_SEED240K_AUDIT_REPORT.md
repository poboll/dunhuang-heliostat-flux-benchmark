# Enlarged Reduced SolTrace Sensitivity Matrix

This run extends the first reduced PySolTrace pilot by testing each explicit aiming strategy across multiple representative solar conditions. It is still a reduced validation layer, not a full-field annual flux certification.

- Days: [20, 80, 110, 140, 172, 200, 230, 266, 326]
- Hours: [10.0, 12.0, 14.0]
- Layouts: `baseline_full,deform_0276,deform_0893,deform_1387,deform_1822`
- Strategies: `visible_equator, five_point, staggered_levels:9:0.380:0, staggered_levels:9:0.380:1, staggered_levels:9:0.380:2`
- Sampled heliostats per layout: 9000
- Requested rays per case: 240000
- Receiver panels/bins: 24 panels, 24 x 72 bins each

## Strategy Summary

| layout_id | strategy | cases | median_delta_peak_pct | mean_delta_peak_pct | p10_delta_peak_pct | p90_delta_peak_pct | share_lower_peak |
| --- | --- | --- | --- | --- | --- | --- | --- |
| deform_0893 | staggered_levels:9:0.380:1 | 27 | -5.481 | -3.408 | -11.696 | 6.543 | 0.556 |
| deform_0893 | visible_equator | 27 | -4.442 | -2.586 | -11.124 | 5.816 | 0.630 |
| deform_1822 | staggered_levels:9:0.380:1 | 27 | -4.856 | -2.132 | -11.597 | 8.991 | 0.741 |
| deform_0893 | staggered_levels:9:0.380:2 | 27 | 0.346 | -0.555 | -10.820 | 7.079 | 0.444 |
| deform_0893 | five_point | 27 | 0.149 | -0.473 | -13.478 | 9.775 | 0.444 |
| deform_0276 | staggered_levels:9:0.380:2 | 27 | -0.455 | -0.386 | -8.779 | 8.366 | 0.704 |
| deform_1822 | staggered_levels:9:0.380:2 | 27 | 0.288 | -0.167 | -13.653 | 9.594 | 0.407 |
| deform_1387 | staggered_levels:9:0.380:1 | 27 | -0.251 | -0.037 | -8.078 | 8.877 | 0.630 |
| deform_1822 | five_point | 27 | -0.001 | 0.317 | -11.171 | 9.465 | 0.519 |
| deform_1822 | visible_equator | 27 | 0.084 | 0.566 | -7.122 | 10.034 | 0.407 |
| deform_0276 | visible_equator | 27 | -0.432 | 0.602 | -10.878 | 14.467 | 0.519 |
| deform_1387 | visible_equator | 27 | -0.004 | 0.793 | -9.336 | 12.561 | 0.519 |
| deform_1387 | staggered_levels:9:0.380:2 | 27 | 0.182 | 1.025 | -11.278 | 12.674 | 0.370 |
| deform_1387 | five_point | 27 | -0.022 | 1.948 | -11.211 | 20.135 | 0.519 |
| deform_0276 | staggered_levels:9:0.380:1 | 27 | -0.423 | 2.119 | -11.785 | 13.900 | 0.593 |
| deform_1822 | staggered_levels:9:0.380:0 | 27 | 0.163 | 2.322 | -5.811 | 12.657 | 0.444 |
| deform_1387 | staggered_levels:9:0.380:0 | 27 | 0.110 | 2.824 | -5.883 | 13.013 | 0.444 |
| deform_0893 | staggered_levels:9:0.380:0 | 27 | 5.463 | 3.002 | -6.018 | 14.606 | 0.296 |
| deform_0276 | staggered_levels:9:0.380:0 | 27 | 5.358 | 3.404 | -8.923 | 14.158 | 0.407 |
| deform_0276 | five_point | 27 | -0.265 | 3.407 | -6.700 | 15.626 | 0.593 |

## Proxy-Best Staggered Strategy Summary

| layout_id | proxy_best_strategy | cases | median_delta_peak_pct | mean_delta_peak_pct | p10_delta_peak_pct | p90_delta_peak_pct | share_lower_peak | best_condition_delta_pct | worst_condition_delta_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| deform_1822 | staggered_levels:9:0.380:1 | 27 | -4.856 | -2.132 | -11.597 | 8.991 | 0.741 | -20.995 | 24.944 |
| deform_0893 | staggered_levels:9:0.380:2 | 27 | 0.346 | -0.555 | -10.820 | 7.079 | 0.444 | -16.642 | 12.531 |
| deform_1387 | staggered_levels:9:0.380:1 | 27 | -0.251 | -0.037 | -8.078 | 8.877 | 0.630 | -11.838 | 26.125 |
| deform_0276 | staggered_levels:9:0.380:0 | 27 | 5.358 | 3.404 | -8.923 | 14.158 | 0.407 | -12.033 | 19.059 |

## Claim Boundary

The matrix strengthens the direct evidence for selected layout--aiming pairs, but it remains sampled. It should be described as enlarged reduced SolTrace validation. Full-field annual custom-aimpoint validation remains future work.
