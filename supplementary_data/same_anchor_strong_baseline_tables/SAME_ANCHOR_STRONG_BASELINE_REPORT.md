# Same-Anchor Strong Baseline Pressure Test

This report adds literature-inspired baseline approximations under the same Dunhuang coordinate anchor.
The approximation families are not complete reproductions of HelioSliders, HeFAAL, modified ABC, or other named methods.
They are pressure tests that preserve the 11,915 available heliostats and reuse the same SolarPILOT/default-aiming and aiming-proxy pipeline.

## Family summary

| family                        |   layout_count |   best_delta_opteff_pct |   best_delta_aiming_proxy_pct |   best_pressure_score |
|:------------------------------|---------------:|------------------------:|------------------------------:|----------------------:|
| TS-FPDA representative        |          3.000 |                   3.148 |                        -6.223 |                 1.042 |
| hybrid pressure approximation |          2.000 |                   1.740 |                        -4.439 |                 0.999 |
| joint representative          |          2.000 |                   0.915 |                        -8.159 |                 0.114 |
| low-complexity control        |          1.000 |                  -0.892 |                         0.104 |                -0.928 |
| pattern-free approximation    |          2.000 |                   0.655 |                        -5.447 |                 0.628 |
| slider-like approximation     |          3.000 |                   0.472 |                        -6.666 |                 0.307 |
| terrain-aware approximation   |          2.000 |                   1.040 |                        -0.456 |                 0.550 |

## Top pressure-score rows

| role         | layout_id      | family                        |   delta_opteff_pct |   delta_default_flux_ratio_pct |   delta_aiming_proxy_pct |   pressure_score |
|:-------------|:---------------|:------------------------------|-------------------:|-------------------------------:|-------------------------:|-----------------:|
| L_opt        | deform_0276    | TS-FPDA representative        |              3.148 |                          4.679 |                   -5.475 |            1.042 |
| SB_hy_energy | sb_hy_energy   | hybrid pressure approximation |              1.740 |                          1.647 |                   -4.439 |            0.999 |
| SB_pf_energy | sb_pf_energy   | pattern-free approximation    |              0.655 |                          0.059 |                   -3.156 |            0.628 |
| SB_ta_energy | sb_ta_energy   | terrain-aware approximation   |              1.040 |                          1.088 |                   -0.456 |            0.550 |
| SB_hs_energy | sb_hs_energy   | slider-like approximation     |              0.472 |                          0.367 |                   -4.791 |            0.307 |
| J_bal        | joint_g02_0333 | joint representative          |              0.915 |                          1.780 |                   -8.159 |            0.114 |
| L_rob        | deform_1387    | TS-FPDA representative        |              0.706 |                          2.377 |                   -5.341 |           -0.364 |
| L_nom        | deform_0893    | TS-FPDA representative        |              0.242 |                          1.399 |                   -6.223 |           -0.387 |

## Interpretation

- These baselines are stronger than the earlier low-complexity controls because they test sector/ring free-form, slider-like, terrain-aware, and hybrid deformation families.
- They still do not justify a SOTA claim, because they are local same-anchor approximations and not complete literature algorithm reimplementations.
- The manuscript should use them to show whether the Dunhuang benchmark has discriminative power under stronger pressure, not to overstate final engineering superiority.
