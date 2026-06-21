# Aiming Proxy Sensitivity

This run tests whether the proxy aiming conclusion depends on one arbitrary discretization. It perturbs sector count, annular count, azimuthal spot width, vertical spot width, and staggered phase, then re-optimizes the best proxy aiming strategy for each layout and condition.

| Layout | Conditions | Fraction lower peak/mean | Median change (%) | P10/P90 change (%) | Median intercept change (pct-pt) |
| --- | ---: | ---: | ---: | ---: | ---: |
| `deform_1387` | 81 | 0.72 | -1.94 | -5.32/+1.95 | +0.000 |
| `deform_0893` | 81 | 0.64 | -0.32 | -4.42/+1.31 | -0.008 |
| `deform_1822` | 81 | 0.63 | -0.21 | -1.06/+1.24 | -0.000 |
| `deform_0276` | 81 | 0.32 | +0.61 | -0.87/+2.86 | -0.001 |

Interpretation rule: this remains a proxy-level robustness test. It strengthens the candidate queue only if a layout improves peak-to-active-mean concentration across many assumptions without large intercept loss. It does not replace CoPylot/SolarPILOT or SolTrace custom-aimpoint numerical checking.

Main tables:

- `tables/aiming_sensitivity_records.csv`
- `tables/aiming_sensitivity_summary.csv`

Main figures:

- `figures/aiming_sensitivity_boxplot.png`
- `figures/aiming_sensitivity_intercept_tradeoff.png`
