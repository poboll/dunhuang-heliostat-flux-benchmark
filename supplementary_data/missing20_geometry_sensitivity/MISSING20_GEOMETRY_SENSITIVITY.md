# Missing-20 Coordinate Geometry Sensitivity Audit

Baseline coordinate pool: `11915` heliostats.
Random omission stress test: `20` heliostats removed per replicate, `2000` replicates, seed `20260523`.

This audit does not reconstruct the 20 unavailable records. It asks a narrower provenance question: if a 20-record gap is treated as an unknown omission from the available full-field coordinate pool, how much do basic geometry descriptors move under random omissions of the same size?

## Key Geometry Deltas

| Metric | Baseline | Mean absolute delta | 95th percentile absolute delta | 95th percentile relative delta (%) |
| --- | ---: | ---: | ---: | ---: |
| `mean_radius_m` | 1020.56 | 0.1382 | 0.3324 | 0.0325704 |
| `p05_radius_m` | 296.935 | 0.00427275 | 7.67163e-06 | 2.5836e-06 |
| `p95_radius_m` | 1785.92 | 9.95338e-06 | 8.36868e-05 | 4.68592e-06 |
| `x_span_m` | 3530.44 | 0.01555 | 0 | 0 |
| `y_span_m` | 3503.93 | 0.0055 | 0 | 0 |
| `axis_ratio_x_over_y` | 1.00757 | 6.02048e-06 | 0 | 0 |
| `sector_coverage_frac` | 1 | 0 | 0 | 0 |
| `annular_coverage_frac` | 1 | 0 | 0 | 0 |

## Interpretation

The count gap is 0.168% of the reported 11,935-heliostat plant count. Across random omissions of the same size, global radial, axis-span, axis-ratio, and coverage descriptors change by far less than the deformation amplitudes studied in the manuscript. The result supports using the 11,915-record pool as a stable benchmark geometry, while preserving the claim boundary that the unavailable records are not an official as-built survey gap closure.
