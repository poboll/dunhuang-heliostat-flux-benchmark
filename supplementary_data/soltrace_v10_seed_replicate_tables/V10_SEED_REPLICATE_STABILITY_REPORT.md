# V10 Independent-Seed Stability Audit

This report compares the V9 high-sample reduced PySolTrace matrix with an independent-seed V10 replicate using the same layouts, solar conditions, strategies, sampled-field size, receiver discretization, and requested ray count. It is a robustness audit for the reduced-check layer, not a final annual full-field certification.

## Matrix Scale

| matrix | relative_rows | layouts | strategies | conditions | summary_rows | intercept_min | intercept_max | mean_elapsed_s | max_elapsed_s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| V9 | 675 | 5 | 5 | 27 | 20 | 0.636 | 0.745 | 12.108 | 15.129 |
| V10 | 675 | 5 | 5 | 27 | 20 | 0.636 | 0.745 | 8.321 | 13.725 |

## Best-Row Comparison

| layout_id | v9_best_strategy | v9_best_mean_delta_pct | v9_best_median_delta_pct | v9_best_lower_frac | v10_same_strategy_mean_delta_pct | v10_same_strategy_median_delta_pct | v10_same_strategy_lower_frac | v10_best_strategy | v10_best_mean_delta_pct | v10_best_median_delta_pct | v10_best_lower_frac | v10_best_intercept_median_pctpt | same_best_strategy | best_mean_shift_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| deform_1387 | five-point | -3.414 | -5.653 | 0.556 | -0.652 | 0.047 | 0.481 | S9-p1 | -2.693 | -0.402 | 0.630 | -0.006 | False | 0.721 |
| deform_1822 | five-point | -2.373 | -0.277 | 0.556 | -2.321 | -0.140 | 0.556 | S9-p0 | -2.476 | -0.561 | 0.667 | -0.093 | False | -0.103 |
| deform_0893 | S9-p1 | -3.041 | -6.737 | 0.556 | 0.754 | 0.653 | 0.407 | five-point | -2.331 | -6.424 | 0.593 | -0.263 | False | 0.710 |
| deform_0276 | S9-p1 | -0.398 | -0.673 | 0.667 | -0.246 | -0.566 | 0.741 | five-point | -0.306 | -0.114 | 0.556 | 1.095 | False | 0.093 |

## Matched-Strategy Stability

| layout_id | strategy | mean_delta_peak_pct_v9 | mean_delta_peak_pct_v10 | mean_shift_pct | median_shift_pct | same_mean_sign |
| --- | --- | --- | --- | --- | --- | --- |
| deform_1387 | S9-p1 | 0.103 | -2.693 | -2.796 | -0.468 | False |
| deform_1822 | S9-p0 | 0.974 | -2.476 | -3.451 | -0.822 | False |
| deform_0893 | five-point | -0.635 | -2.331 | -1.696 | -6.467 | True |
| deform_1822 | five-point | -2.373 | -2.321 | 0.052 | 0.137 | True |
| deform_1822 | S9-p1 | -0.559 | -2.173 | -1.614 | -0.166 | True |
| deform_1387 | S9-p2 | 2.282 | -1.209 | -3.491 | -0.457 | False |
| deform_1387 | visible | 0.765 | -1.128 | -1.893 | -0.542 | False |
| deform_1822 | S9-p2 | -1.017 | -0.697 | 0.320 | 0.011 | True |
| deform_1387 | five-point | -3.414 | -0.652 | 2.763 | 5.700 | True |
| deform_1822 | visible | -0.579 | -0.491 | 0.088 | -0.034 | True |
| deform_0276 | five-point | 1.602 | -0.306 | -1.908 | 0.089 | False |
| deform_0276 | S9-p0 | 1.784 | -0.254 | -2.038 | -6.639 | False |
| deform_0276 | S9-p1 | -0.398 | -0.246 | 0.152 | 0.107 | True |
| deform_0276 | visible | 0.378 | 0.323 | -0.055 | -0.057 | True |
| deform_0893 | S9-p0 | 0.671 | 0.440 | -0.232 | -0.257 | True |
| deform_1387 | S9-p0 | -0.566 | 0.517 | 1.083 | 0.291 | False |
| deform_0893 | visible | -0.298 | 0.624 | 0.922 | 0.103 | False |
| deform_0893 | S9-p1 | -3.041 | 0.754 | 3.795 | 7.390 | False |
| deform_0893 | S9-p2 | -2.036 | 1.222 | 3.257 | 0.677 | False |
| deform_0276 | S9-p2 | 3.952 | 1.524 | -2.428 | 0.200 | True |

## Interpretation Rule

If V9 and V10 preserve the same receiver-risk candidate queue but disagree on individual aiming phases, the manuscript should keep the present conservative claim boundary: robust candidate roles are defensible, exact reduced-SolTrace aiming phases are not final design prescriptions.
