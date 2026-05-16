# V11 Reduced PySolTrace Convergence and Uncertainty Audit

This report consolidates the V8 all-phase matrix, the V9 high-sample confirmation, and the V10 independent-seed replicate. It is a claim-boundary audit for the reduced direct-check layer, not a new plant-design optimization.

## Matrix scale

| matrix | rows | strategies | conditions | sampled_heliostats | ray_hits | receiver_panels | receiver_grid | intercept_min | intercept_max | mean_elapsed_s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| V8 | 1485 | 11 | 27 | 6000 | 60000 | 18 | 20 x 60 | 0.639 | 0.748 | 6.241 |
| V9 | 675 | 5 | 27 | 9000 | 180000 | 24 | 24 x 72 | 0.636 | 0.745 | 12.108 |
| V10 | 675 | 5 | 27 | 9000 | 180000 | 24 | 24 x 72 | 0.636 | 0.745 | 8.321 |

## Best-row role stability

| role_label | role_name | v8_strategy | v8_mean_delta_pct | v9_strategy | v9_mean_delta_pct | v10_strategy | v10_mean_delta_pct | best_mean_range_pct | always_negative_best_row |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| $L_{rob}$ | receiver-risk | S9-p1 | -2.978 | five-point | -3.414 | S9-p1 | -2.693 | 0.721 | True |
| $L_{nom}$ | nominal-proxy | S9-p2 | -2.780 | S9-p1 | -3.041 | five-point | -2.331 | 0.710 | True |
| $L_{ctrl}$ | default-flux-control | S9-p0 | -2.321 | five-point | -2.373 | S9-p0 | -2.476 | 0.155 | True |
| $L_{opt}$ | optical-upper | S9-p0 | -0.817 | S9-p1 | -0.398 | five-point | -0.306 | 0.511 | True |

## Matched-strategy shift statistics

| comparison | matched_rows | same_mean_sign_rows | same_mean_sign_fraction | median_abs_mean_shift_pct | p90_abs_mean_shift_pct | max_abs_mean_shift_pct |
| --- | --- | --- | --- | --- | --- | --- |
| V8_to_V9 | 20 | 9 | 0.450 | 2.616 | 4.561 | 6.961 |
| V9_to_V10 | 20 | 10 | 0.500 | 1.794 | 3.455 | 3.795 |

## Reviewer-facing interpretation

- The role-level queue is more stable than exact aiming phase selection: the receiver-risk candidates remain ahead of the optical-upper layout across V8, V9, and V10.
- Exact best strategies are not stable. This is reported as sampling, receiver-discretization, and seed sensitivity rather than hidden behind a single favorable phase.
- V8-to-V9 and V9-to-V10 shifts mean that small peak-to-active-mean differences should not be described as final receiver-design improvements.
- The defensible claim is a reproducible screening queue for future full-field annual custom-aimpoint studies.
