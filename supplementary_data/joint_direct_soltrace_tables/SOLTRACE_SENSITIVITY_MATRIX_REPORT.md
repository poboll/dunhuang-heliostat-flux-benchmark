# Enlarged Reduced SolTrace Sensitivity Matrix

This run extends the first reduced PySolTrace pilot by testing each explicit aiming strategy across multiple representative solar conditions. It is still a reduced checks layer, not a full-field annual flux certification.

- Days: [20, 80, 110, 140, 172, 200, 230, 266, 326]
- Hours: [10.0, 12.0, 14.0]
- Layouts: `baseline_full,joint_g02_0333,joint_g02_0303,joint_g04_0478`
- Strategies: `visible_equator, five_point, staggered_levels:9:0.380:2, staggered_levels:9:0.380:3, staggered_levels:9:0.380:5`
- Sampled heliostats per layout: 6000
- Requested rays per case: 60000
- Receiver panels/bins: 18 panels, 20 x 60 bins each

## Strategy Summary

| layout_id | strategy | cases | median_delta_peak_pct | mean_delta_peak_pct | p10_delta_peak_pct | p90_delta_peak_pct | share_lower_peak |
| --- | --- | --- | --- | --- | --- | --- | --- |
| joint_g04_0478 | staggered_levels:9:0.380:5 | 27 | -7.622 | -4.063 | -10.168 | 3.905 | 0.741 |
| joint_g02_0303 | staggered_levels:9:0.380:2 | 27 | -0.740 | -2.495 | -17.001 | 10.667 | 0.630 |
| joint_g02_0333 | staggered_levels:9:0.380:2 | 27 | -0.530 | -1.982 | -13.270 | 19.835 | 0.704 |
| joint_g02_0333 | staggered_levels:9:0.380:5 | 27 | -0.305 | -0.272 | -12.654 | 19.693 | 0.630 |
| joint_g04_0478 | staggered_levels:9:0.380:2 | 27 | 0.048 | 0.445 | -9.320 | 14.539 | 0.481 |
| joint_g04_0478 | visible_equator | 27 | 0.053 | 0.802 | -8.201 | 9.923 | 0.444 |
| joint_g02_0333 | visible_equator | 27 | -0.029 | 1.103 | -8.610 | 9.091 | 0.519 |
| joint_g02_0333 | five_point | 27 | -0.434 | 1.140 | -10.136 | 14.822 | 0.556 |
| joint_g04_0478 | five_point | 27 | 0.248 | 1.550 | -9.739 | 15.209 | 0.370 |
| joint_g02_0303 | five_point | 27 | -0.231 | 2.129 | -10.507 | 14.081 | 0.630 |
| joint_g04_0478 | staggered_levels:9:0.380:3 | 27 | 0.361 | 2.239 | -8.416 | 11.016 | 0.333 |
| joint_g02_0303 | staggered_levels:9:0.380:3 | 27 | 0.353 | 2.576 | -11.700 | 14.443 | 0.481 |
| joint_g02_0333 | staggered_levels:9:0.380:3 | 27 | 0.475 | 3.647 | -10.014 | 14.129 | 0.370 |
| joint_g02_0303 | staggered_levels:9:0.380:5 | 27 | 0.469 | 3.925 | -9.513 | 13.976 | 0.481 |
| joint_g02_0303 | visible_equator | 27 | 7.473 | 4.700 | -8.342 | 16.773 | 0.370 |

## Proxy-Best Staggered Strategy Summary

| layout_id | proxy_best_strategy | cases | median_delta_peak_pct | mean_delta_peak_pct | p10_delta_peak_pct | p90_delta_peak_pct | share_lower_peak | best_condition_delta_pct | worst_condition_delta_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| joint_g04_0478 | staggered_levels:9:0.380:5 | 27 | -7.622 | -4.063 | -10.168 | 3.905 | 0.741 | -17.967 | 19.094 |
| joint_g02_0333 | staggered_levels:9:0.380:2 | 27 | -0.530 | -1.982 | -13.270 | 19.835 | 0.704 | -24.138 | 32.543 |
| joint_g02_0303 | staggered_levels:9:0.380:3 | 27 | 0.353 | 2.576 | -11.700 | 14.443 | 0.481 | -16.160 | 22.039 |

## Claim Boundary

The matrix strengthens the direct evidence for selected layout--aiming pairs, but it remains sampled. It should be described as an enlarged reduced SolTrace numerical check. Full-field annual custom-aimpoint numerical checking remains future work.
