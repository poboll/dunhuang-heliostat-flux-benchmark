# Multi-Year Annual-Proxy Robustness Gate

## Scope

This is a weather-year robustness audit for the fast annual proxy. It reuses the same
SolarPILOT default-aiming optical-efficiency tables and reweights them over each available
NASA POWER SAM weather year. It is not full annual custom-aimpoint validation.

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

| Role   | Layout         |   Mean annual delta (%) |   Min annual delta (%) |   Max annual delta (%) |   Positive-year fraction |   Best rank |   Worst rank |
|:-------|:---------------|------------------------:|-----------------------:|-----------------------:|-------------------------:|------------:|-------------:|
| L_opt  | deform_0276    |                   3.363 |                  3.346 |                  3.377 |                    1.000 |       1.000 |        1.000 |
| B_hy,E | sb_hy_energy   |                   1.850 |                  1.842 |                  1.857 |                    1.000 |       2.000 |        2.000 |
| J_bal  | joint_g02_0333 |                   0.972 |                  0.968 |                  0.976 |                    1.000 |       4.000 |        4.000 |
| L_rob  | deform_1387    |                   0.741 |                  0.737 |                  0.744 |                    1.000 |       5.000 |        5.000 |
| L_nom  | deform_0893    |                   0.249 |                  0.247 |                  0.250 |                    1.000 |       9.000 |        9.000 |
| J_flux | joint_g04_0478 |                  -0.738 |                 -0.741 |                 -0.736 |                    0.000 |      11.000 |       11.000 |
| B_hs,R | sb_hs_flux     |                  -0.842 |                 -0.845 |                 -0.839 |                    0.000 |      13.000 |       13.000 |
| B_pf,R | sb_pf_flux     |                  -0.863 |                 -0.866 |                 -0.861 |                    0.000 |      14.000 |       14.000 |

## Gate Decision

- Recommendation: `write_short_robustness_sentence`.
- Positive annual rows all positive: `True`.
- L_opt remains top-three in all years: `True`.
- Receiver-pressure rows do not become annual headline rows: `True`.
- Interpretation: Annual-proxy role signs are stable across the available NASA POWER weather years.

## Boundary

Do not cite this audit as bankable annual yield or annual custom-aimpoint verification.
If written into the manuscript, it should be a short robustness sentence or a supplementary
artifact describing weather-year sign/rank stability.
