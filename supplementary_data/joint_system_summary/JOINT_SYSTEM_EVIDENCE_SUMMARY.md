# Joint Layout--Aiming System Evidence Summary

This report merges three evidence layers for the joint representatives: proxy-level joint screening,
PySAM/SolarPILOT default-aiming layout checks, and the reduced PySolTrace direct-promotion audit.
The SolarPILOT bridge is not a custom-aimpoint validation; it tests whether the joint layouts remain
optically plausible under the same default-aiming settings used for the earlier representatives.

| candidate   | layout_id      | role                                         |   proxy_delta_energy_pct |   proxy_delta_receiver_pct | proxy_best_strategy        |   solarpilot_delta_opteff_pct |   solarpilot_delta_default_flux_ratio_pct |   solarpilot_delta_active_cv_pct | direct_proxy_strategy   | direct_proxy_delta_ci_pct   | direct_best_strategy   | direct_best_delta_ci_pct   |   direct_lower_fraction |
|:------------|:---------------|:---------------------------------------------|-------------------------:|---------------------------:|:---------------------------|------------------------------:|------------------------------------------:|---------------------------------:|:------------------------|:----------------------------|:-----------------------|:---------------------------|------------------------:|
| $J_{bal}$   | joint_g02_0333 | directional balance candidate                |                    0.002 |                     -4.316 | staggered_levels:9:0.380:2 |                         0.915 |                                     1.780 |                            0.075 | S9-p2                   | -1.98 [-6.53, +3.11]        | S9-p2                  | -1.98 [-6.55, +3.10]       |                   0.704 |
| $J_{gain}$  | joint_g02_0303 | strategy-sensitive energy-gated candidate    |                    0.091 |                     -3.468 | staggered_levels:9:0.380:3 |                         1.644 |                                     2.404 |                           -0.183 | S9-p3                   | +2.58 [-1.67, +6.66]        | S9-p2                  | -2.49 [-6.74, +2.04]       |                   0.630 |
| $J_{flux}$  | joint_g04_0478 | direct-supported receiver-boundary candidate |                   -0.195 |                     -7.222 | staggered_levels:9:0.380:5 |                        -0.692 |                                     1.007 |                            0.768 | S9-p5                   | -4.06 [-6.99, -0.94]        | S9-p5                  | -4.06 [-6.99, -0.94]       |                   0.741 |

Interpretation: `J_bal` and `J_gain` are not merely proxy-energy artifacts because they also increase
SolarPILOT default optical efficiency, but both increase default receiver concentration and therefore
still require direct custom-aimpoint promotion. `J_flux` is the direct-supported receiver-boundary
candidate, but it sacrifices optical efficiency under both proxy and SolarPILOT default checks.
