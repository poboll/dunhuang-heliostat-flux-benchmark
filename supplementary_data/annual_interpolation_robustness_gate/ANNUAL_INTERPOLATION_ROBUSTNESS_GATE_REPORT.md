# Annual-Proxy Interpolation Robustness Gate

## Scope

This audit checks whether the fast annual proxy depends on a single interpolation
choice when discrete SolarPILOT default-aiming optical-efficiency tables are mapped
to hourly public weather files. It is not annual custom-aimpoint validation.

Tested interpolation methods: `idw12, idw3, idw6, linear_nearest, nearest`.

## Weather Years

|    year |   annual_dni_kwh_m2 |   positive_dni_hours |
|--------:|--------------------:|---------------------:|
| 2020.00 |             2012.40 |              4254.00 |
| 2021.00 |             1964.90 |              4193.00 |
| 2022.00 |             1783.27 |              4213.00 |
| 2023.00 |             1842.41 |              4248.00 |
| 2024.00 |             1694.85 |              4215.00 |
| 2025.00 |             1725.64 |              4208.00 |

## Selected Roles

| Role   | Layout         |   Mean annual delta (%) |   Min annual delta (%) |   Max annual delta (%) |   Spread (pct-pt) |   Positive fraction |   Best rank |   Worst rank |
|:-------|:---------------|------------------------:|-----------------------:|-----------------------:|------------------:|--------------------:|------------:|-------------:|
| L_opt  | deform_0276    |                   3.323 |                  3.182 |                  3.379 |             0.197 |               1.000 |       1.000 |        1.000 |
| B_hy,E | sb_hy_energy   |                   1.831 |                  1.761 |                  1.861 |             0.100 |               1.000 |       2.000 |        2.000 |
| J_bal  | joint_g02_0333 |                   0.963 |                  0.931 |                  0.976 |             0.045 |               1.000 |       4.000 |        4.000 |
| L_rob  | deform_1387    |                   0.731 |                  0.704 |                  0.744 |             0.040 |               1.000 |       5.000 |        5.000 |
| L_nom  | deform_0893    |                   0.242 |                  0.219 |                  0.250 |             0.031 |               1.000 |       9.000 |        9.000 |
| J_flux | joint_g04_0478 |                  -0.734 |                 -0.748 |                 -0.714 |             0.034 |               0.000 |      11.000 |       11.000 |
| B_hs,R | sb_hs_flux     |                  -0.835 |                 -0.847 |                 -0.809 |             0.038 |               0.000 |      13.000 |       13.000 |
| B_pf,R | sb_pf_flux     |                  -0.858 |                 -0.870 |                 -0.836 |             0.034 |               0.000 |      14.000 |       14.000 |

## Method Means

| Role   | Layout         | Method         |   Mean annual delta (%) |   Median rank |
|:-------|:---------------|:---------------|------------------------:|--------------:|
| L_opt  | deform_0276    | idw12          |                   3.356 |         1.000 |
| L_opt  | deform_0276    | idw3           |                   3.333 |         1.000 |
| L_opt  | deform_0276    | idw6           |                   3.363 |         1.000 |
| L_opt  | deform_0276    | linear_nearest |                   3.358 |         1.000 |
| L_opt  | deform_0276    | nearest        |                   3.203 |         1.000 |
| L_nom  | deform_0893    | idw12          |                   0.248 |         9.000 |
| L_nom  | deform_0893    | idw3           |                   0.244 |         9.000 |
| L_nom  | deform_0893    | idw6           |                   0.249 |         9.000 |
| L_nom  | deform_0893    | linear_nearest |                   0.244 |         9.000 |
| L_nom  | deform_0893    | nearest        |                   0.223 |         9.000 |
| L_rob  | deform_1387    | idw12          |                   0.739 |         5.000 |
| L_rob  | deform_1387    | idw3           |                   0.733 |         5.000 |
| L_rob  | deform_1387    | idw6           |                   0.741 |         5.000 |
| L_rob  | deform_1387    | linear_nearest |                   0.735 |         5.000 |
| L_rob  | deform_1387    | nearest        |                   0.709 |         5.000 |
| J_bal  | joint_g02_0333 | idw12          |                   0.970 |         4.000 |
| J_bal  | joint_g02_0333 | idw3           |                   0.965 |         4.000 |
| J_bal  | joint_g02_0333 | idw6           |                   0.972 |         4.000 |
| J_bal  | joint_g02_0333 | linear_nearest |                   0.971 |         4.000 |
| J_bal  | joint_g02_0333 | nearest        |                   0.936 |         4.000 |
| J_flux | joint_g04_0478 | idw12          |                  -0.737 |        11.000 |
| J_flux | joint_g04_0478 | idw3           |                  -0.735 |        11.000 |
| J_flux | joint_g04_0478 | idw6           |                  -0.738 |        11.000 |
| J_flux | joint_g04_0478 | linear_nearest |                  -0.744 |        11.000 |
| J_flux | joint_g04_0478 | nearest        |                  -0.717 |        11.000 |
| B_hs,R | sb_hs_flux     | idw12          |                  -0.840 |        13.000 |
| B_hs,R | sb_hs_flux     | idw3           |                  -0.837 |        13.000 |
| B_hs,R | sb_hs_flux     | idw6           |                  -0.842 |        13.000 |
| B_hs,R | sb_hs_flux     | linear_nearest |                  -0.843 |        13.000 |
| B_hs,R | sb_hs_flux     | nearest        |                  -0.812 |        13.000 |
| B_hy,E | sb_hy_energy   | idw12          |                   1.847 |         2.000 |
| B_hy,E | sb_hy_energy   | idw3           |                   1.835 |         2.000 |
| B_hy,E | sb_hy_energy   | idw6           |                   1.850 |         2.000 |
| B_hy,E | sb_hy_energy   | linear_nearest |                   1.851 |         2.000 |
| B_hy,E | sb_hy_energy   | nearest        |                   1.771 |         2.000 |
| B_pf,R | sb_pf_flux     | idw12          |                  -0.862 |        14.000 |
| B_pf,R | sb_pf_flux     | idw3           |                  -0.860 |        14.000 |
| B_pf,R | sb_pf_flux     | idw6           |                  -0.863 |        14.000 |
| B_pf,R | sb_pf_flux     | linear_nearest |                  -0.867 |        14.000 |
| B_pf,R | sb_pf_flux     | nearest        |                  -0.839 |        14.000 |

## Gate Decision

- Recommendation: `write_short_interpolation_robustness_sentence`.
- Positive annual rows positive across all tested method-year pairs: `True`.
- L_opt remains top-three across all tested method-year pairs: `True`.
- Receiver-pressure rows do not become annual headline rows: `True`.
- Max selected delta spread: 0.197 pct-pt; threshold: 0.200 pct-pt.
- Interpretation: Annual-proxy signs and role ranks are stable across tested interpolation methods and weather years.

## Boundary

If written into the manuscript, this audit should be a short interpolation-robustness
statement for the annual proxy. It must not be cited as measured annual operation,
bankable generation, dispatch simulation, or full-field annual custom aiming.
