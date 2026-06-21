# Enlarged Reduced SolTrace Sensitivity Matrix

This run extends the first reduced PySolTrace pilot by testing each explicit aiming strategy across multiple representative solar conditions. It is still a reduced validation layer, not a full-field annual flux certification.

- Days: [20, 80, 110, 140, 172, 200, 230, 266, 326]
- Hours: [10.0, 12.0, 14.0]
- Layouts: `baseline_full,ctrl_radial_compact_015,ctrl_radial_expand_015,ctrl_ring_wave_012,deform_0276,deform_0893,deform_1387,deform_1822`
- Strategies: `visible_equator, five_point, staggered_levels:9:0.380:0, staggered_levels:9:0.380:1, staggered_levels:9:0.380:2, staggered_levels:9:0.380:5, staggered_levels:9:0.380:8`
- Sampled heliostats per layout: 6000
- Requested rays per case: 60000
- Receiver panels/bins: 18 panels, 20 x 60 bins each

## Strategy Summary

| layout_id | strategy | cases | median_delta_peak_pct | mean_delta_peak_pct | p10_delta_peak_pct | p90_delta_peak_pct | share_lower_peak |
| --- | --- | --- | --- | --- | --- | --- | --- |
| deform_1387 | staggered_levels:9:0.380:2 | 27 | -0.722 | -3.605 | -10.429 | 1.069 | 0.593 |
| deform_0893 | staggered_levels:9:0.380:0 | 27 | -0.194 | -3.491 | -16.740 | 10.329 | 0.519 |
| ctrl_radial_expand_015 | visible_equator | 27 | -7.172 | -2.434 | -14.467 | 9.957 | 0.556 |
| ctrl_ring_wave_012 | five_point | 27 | -0.081 | -2.303 | -15.964 | 10.528 | 0.556 |
| ctrl_ring_wave_012 | visible_equator | 27 | -6.769 | -1.829 | -13.864 | 9.777 | 0.593 |
| ctrl_radial_compact_015 | staggered_levels:9:0.380:5 | 27 | -0.541 | -1.443 | -12.710 | 10.388 | 0.667 |
| deform_0276 | five_point | 27 | -0.494 | -1.197 | -16.672 | 21.246 | 0.741 |
| ctrl_radial_expand_015 | staggered_levels:9:0.380:0 | 27 | 0.245 | -1.196 | -9.893 | 9.972 | 0.444 |
| ctrl_ring_wave_012 | staggered_levels:9:0.380:0 | 27 | -0.056 | -1.143 | -9.816 | 10.988 | 0.593 |
| deform_0893 | five_point | 27 | 0.071 | -0.921 | -16.573 | 15.297 | 0.481 |
| deform_1387 | visible_equator | 27 | -0.066 | -0.899 | -14.783 | 15.769 | 0.556 |
| deform_1822 | five_point | 27 | 0.286 | -0.878 | -16.183 | 11.228 | 0.444 |
| deform_1822 | staggered_levels:9:0.380:0 | 27 | 0.116 | -0.842 | -9.492 | 10.090 | 0.481 |
| deform_1822 | staggered_levels:9:0.380:1 | 27 | -0.260 | -0.734 | -10.086 | 10.348 | 0.519 |
| ctrl_radial_compact_015 | staggered_levels:9:0.380:0 | 27 | -0.137 | -0.642 | -12.587 | 10.743 | 0.556 |
| deform_0893 | staggered_levels:9:0.380:1 | 27 | 0.180 | -0.641 | -16.746 | 10.548 | 0.370 |
| ctrl_radial_compact_015 | staggered_levels:9:0.380:2 | 27 | -0.224 | -0.608 | -13.079 | 10.331 | 0.593 |
| deform_1387 | staggered_levels:9:0.380:0 | 27 | -0.001 | -0.555 | -9.593 | 10.486 | 0.519 |
| deform_1387 | staggered_levels:9:0.380:1 | 27 | 0.035 | -0.404 | -12.743 | 14.016 | 0.481 |
| deform_1822 | staggered_levels:9:0.380:2 | 27 | 0.117 | -0.044 | -9.918 | 9.888 | 0.444 |
| deform_0276 | staggered_levels:9:0.380:1 | 27 | -0.229 | 0.060 | -10.277 | 10.007 | 0.593 |
| deform_0893 | staggered_levels:9:0.380:8 | 27 | 0.214 | 0.151 | -17.233 | 14.442 | 0.481 |
| ctrl_ring_wave_012 | staggered_levels:9:0.380:2 | 27 | 0.003 | 0.226 | -10.437 | 14.382 | 0.481 |
| deform_0893 | visible_equator | 27 | 0.519 | 0.268 | -14.532 | 9.739 | 0.370 |
| deform_1387 | five_point | 27 | 0.040 | 0.340 | -11.654 | 10.522 | 0.481 |
| ctrl_ring_wave_012 | staggered_levels:9:0.380:8 | 27 | 0.349 | 0.393 | -9.481 | 11.012 | 0.444 |
| ctrl_ring_wave_012 | staggered_levels:9:0.380:5 | 27 | -0.028 | 0.414 | -9.477 | 19.491 | 0.519 |
| ctrl_radial_compact_015 | staggered_levels:9:0.380:1 | 27 | 0.181 | 0.516 | -9.650 | 14.177 | 0.481 |
| deform_0276 | visible_equator | 27 | -0.964 | 0.571 | -11.441 | 17.213 | 0.667 |
| deform_1822 | staggered_levels:9:0.380:8 | 27 | -0.154 | 1.063 | -9.559 | 14.893 | 0.556 |
| ctrl_radial_compact_015 | visible_equator | 27 | 0.135 | 1.276 | -15.290 | 17.517 | 0.481 |
| deform_1822 | staggered_levels:9:0.380:5 | 27 | 0.059 | 1.334 | -9.406 | 14.536 | 0.481 |
| ctrl_ring_wave_012 | staggered_levels:9:0.380:1 | 27 | 0.251 | 1.334 | -9.368 | 14.274 | 0.407 |
| deform_0276 | staggered_levels:9:0.380:5 | 27 | -0.018 | 1.519 | -10.558 | 10.542 | 0.519 |
| ctrl_radial_expand_015 | staggered_levels:9:0.380:1 | 27 | 0.538 | 1.592 | -12.174 | 11.117 | 0.333 |
| ctrl_radial_compact_015 | staggered_levels:9:0.380:8 | 27 | 0.086 | 1.593 | -10.364 | 10.433 | 0.481 |
| deform_0276 | staggered_levels:9:0.380:8 | 27 | -0.098 | 1.595 | -13.237 | 10.498 | 0.519 |
| deform_0276 | staggered_levels:9:0.380:0 | 27 | -0.544 | 1.617 | -9.619 | 13.176 | 0.704 |
| deform_0893 | staggered_levels:9:0.380:2 | 27 | 0.284 | 2.114 | -12.479 | 15.102 | 0.370 |
| deform_0276 | staggered_levels:9:0.380:2 | 27 | -0.140 | 2.232 | -10.218 | 19.613 | 0.556 |
| deform_1387 | staggered_levels:9:0.380:5 | 27 | -0.165 | 2.592 | -9.333 | 14.425 | 0.556 |
| ctrl_radial_expand_015 | staggered_levels:9:0.380:2 | 27 | 0.617 | 2.605 | -9.154 | 11.076 | 0.370 |
| deform_1387 | staggered_levels:9:0.380:8 | 27 | 0.107 | 2.683 | -12.737 | 14.698 | 0.444 |
| ctrl_radial_expand_015 | staggered_levels:9:0.380:8 | 27 | 0.223 | 2.717 | -9.322 | 15.110 | 0.444 |
| deform_0893 | staggered_levels:9:0.380:5 | 27 | 0.589 | 3.100 | -9.208 | 14.516 | 0.370 |
| deform_1822 | visible_equator | 27 | 0.003 | 3.134 | -14.590 | 22.769 | 0.481 |
| ctrl_radial_expand_015 | staggered_levels:9:0.380:5 | 27 | 0.513 | 3.842 | -8.919 | 14.791 | 0.333 |
| ctrl_radial_expand_015 | five_point | 27 | 9.654 | 4.456 | -16.660 | 22.336 | 0.296 |
| ctrl_radial_compact_015 | five_point | 27 | 0.249 | 5.034 | -9.295 | 21.255 | 0.444 |

## Proxy-Best Staggered Strategy Summary

| layout_id | proxy_best_strategy | cases | median_delta_peak_pct | mean_delta_peak_pct | p10_delta_peak_pct | p90_delta_peak_pct | share_lower_peak | best_condition_delta_pct | worst_condition_delta_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ctrl_radial_expand_015 | staggered_levels:9:0.380:0 | 27 | 0.245 | -1.196 | -9.893 | 9.972 | 0.444 | -18.431 | 23.435 |
| deform_1822 | staggered_levels:9:0.380:1 | 27 | -0.260 | -0.734 | -10.086 | 10.348 | 0.519 | -22.881 | 33.580 |
| ctrl_radial_compact_015 | staggered_levels:9:0.380:0 | 27 | -0.137 | -0.642 | -12.587 | 10.743 | 0.556 | -18.738 | 33.588 |
| deform_1387 | staggered_levels:9:0.380:1 | 27 | 0.035 | -0.404 | -12.743 | 14.016 | 0.481 | -31.196 | 20.179 |
| ctrl_ring_wave_012 | staggered_levels:9:0.380:1 | 27 | 0.251 | 1.334 | -9.368 | 14.274 | 0.407 | -17.721 | 23.443 |
| deform_0276 | staggered_levels:9:0.380:0 | 27 | -0.544 | 1.617 | -9.619 | 13.176 | 0.704 | -19.016 | 55.658 |
| deform_0893 | staggered_levels:9:0.380:2 | 27 | 0.284 | 2.114 | -12.479 | 15.102 | 0.370 | -18.813 | 30.514 |

## Claim Boundary

The matrix strengthens the direct evidence for selected layout--aiming pairs, but it remains sampled. It should be described as enlarged reduced SolTrace validation. Full-field annual custom-aimpoint validation remains future work.
