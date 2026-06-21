# Joint Layout--Aiming Reduced Direct Audit

This report aggregates the reduced PySolTrace direct checks for the joint layout--aiming representatives. It tests whether candidates selected by the integrated screening layer remain directionally useful under direct ray tracing.

- Non-baseline joint candidates checked: 3
- Solar conditions aggregated: 27
- Layouts: baseline, J_bal, J_gain, and J_flux.
- Strategies: visible-equator, five-point, and S9 phases p2, p3, and p5.
- Scope: reduced direct numerical audit, not full-field annual certification.

## Bootstrap Summary

| view | label | strategy_short | cases | mean_delta_peak_pct | ci95_low_pct | ci95_high_pct | share_lower_peak | median_delta_intercept_pctpt |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| proxy-selected | $J_{bal}$ | S9-p2 | 27 | -1.982 | -6.526 | 3.109 | 0.704 | 0.228 |
| best-direct | $J_{bal}$ | S9-p2 | 27 | -1.982 | -6.554 | 3.104 | 0.704 | 0.228 |
| proxy-selected | $J_{gain}$ | S9-p3 | 27 | 2.576 | -1.671 | 6.664 | 0.481 | 0.643 |
| best-direct | $J_{gain}$ | S9-p2 | 27 | -2.495 | -6.738 | 2.041 | 0.630 | 0.528 |
| proxy-selected | $J_{flux}$ | S9-p5 | 27 | -4.063 | -6.985 | -0.939 | 0.741 | -0.615 |
| best-direct | $J_{flux}$ | S9-p5 | 27 | -4.063 | -6.987 | -0.944 | 0.741 | -0.615 |

## Interpretation

Positive joint-screening results should be written into the manuscript only when the reduced direct layer supports the same direction. If proxy-selected and best-direct rows diverge, the manuscript should describe the joint optimizer as a candidate generator whose outputs require direct optical-engine auditing.
