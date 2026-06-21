# Baseline-Control Reduced PySolTrace Direct Audit

This audit compares low-complexity same-condition controls with TS-FPDA representatives under the same reduced PySolTrace direct-ray settings. It is intended to test whether the baseline controls explain the receiver-risk queue, not to certify a final plant redesign.

- Source run: `/Users/Apple/Developer/paper/dunhuang-heliostat-rebuild-server/server_outputs/baseline_strengthening_20260522`
- Direct matrix: `/Users/Apple/Developer/paper/dunhuang-heliostat-rebuild-server/server_outputs/baseline_strengthening_20260522/soltrace_baseline_controls_direct_27cond_20260523`
- Scope: baseline plus selected simple controls and TS-FPDA representatives; 27 representative solar conditions; visible-equator, five-point, and proxy-union S9 strategies.
- Interpretation: negative peak-to-active-mean change means lower receiver concentration than the paired baseline under the same condition and aiming strategy.

## Best Direct Rows

| label | role | family | strategy_short | cases | mean_delta_peak_pct | median_delta_peak_pct | share_lower_peak | median_delta_intercept_pctpt | delta_opteff_pct | delta_default_flux_ratio_pct | delta_aiming_proxy_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| $C_{rad-}$ | same-condition control | control | S9-p5 | 27 | -1.443 | -0.541 | 0.667 | 0.427 | 0.886 | 1.071 | -0.106 |
| $C_{rad+}$ | same-condition control | control | visible | 27 | -2.434 | -7.172 | 0.556 | -0.538 | -0.892 | -1.044 | 0.104 |
| $C_{wave}$ | same-condition control | control | five-point | 27 | -2.303 | -0.081 | 0.556 | -0.255 | -0.013 | 0.150 | -2.382 |
| $L_{opt}$ | TS-FPDA optical-upper | tsfpda | five-point | 27 | -1.197 | -0.494 | 0.741 | 1.368 | 3.148 | 4.679 | -5.475 |
| $L_{nom}$ | TS-FPDA nominal-proxy | tsfpda | S9-p0 | 27 | -3.491 | -0.194 | 0.519 | -0.222 | 0.242 | 1.399 | -6.223 |
| $L_{rob}$ | TS-FPDA receiver-risk | tsfpda | S9-p2 | 27 | -3.605 | -0.722 | 0.593 | -0.112 | 0.706 | 2.377 | -5.341 |
| $L_{ctrl}$ | TS-FPDA default-flux-control | tsfpda | five-point | 27 | -0.878 | 0.286 | 0.444 | 0.120 | 0.506 | 0.897 | -3.328 |

## Proxy-Selected Rows

| label | role | family | strategy_short | cases | mean_delta_peak_pct | median_delta_peak_pct | share_lower_peak |
| --- | --- | --- | --- | --- | --- | --- | --- |
| $C_{rad-}$ | same-condition control | control | S9-p0 | 27 | -0.642 | -0.137 | 0.556 |
| $C_{rad+}$ | same-condition control | control | S9-p0 | 27 | -1.196 | 0.245 | 0.444 |
| $C_{wave}$ | same-condition control | control | S9-p1 | 27 | 1.334 | 0.251 | 0.407 |
| $L_{opt}$ | TS-FPDA optical-upper | tsfpda | S9-p0 | 27 | 1.617 | -0.544 | 0.704 |
| $L_{nom}$ | TS-FPDA nominal-proxy | tsfpda | S9-p2 | 27 | 2.114 | 0.284 | 0.370 |
| $L_{rob}$ | TS-FPDA receiver-risk | tsfpda | S9-p1 | 27 | -0.404 | 0.035 | 0.481 |
| $L_{ctrl}$ | TS-FPDA default-flux-control | tsfpda | S9-p1 | 27 | -0.734 | -0.260 | 0.519 |

## Family-Level Summary

| view | family | layout_count | best_layout | best_mean_delta_peak_pct | median_of_layout_means_pct | all_negative_mean_rows |
| --- | --- | --- | --- | --- | --- | --- |
| best-direct | control | 3 | ctrl_radial_expand_015 | -2.434 | -2.303 | True |
| best-direct | tsfpda | 4 | deform_1387 | -3.605 | -2.344 | True |
| proxy-selected | control | 3 | ctrl_radial_expand_015 | -1.196 | -0.642 | False |
| proxy-selected | tsfpda | 4 | deform_1822 | -0.734 | 0.607 | False |

## Bootstrap Confidence Audit

| label | role | family | view | strategy_short | mean_delta_peak_pct | ci95_low_pct | ci95_high_pct | share_lower_peak |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| $C_{rad-}$ | same-condition control | control | best-direct | S9-p5 | -1.443 | -5.029 | 2.146 | 0.667 |
| $C_{rad+}$ | same-condition control | control | best-direct | visible | -2.434 | -6.612 | 1.703 | 0.556 |
| $C_{wave}$ | same-condition control | control | best-direct | five-point | -2.303 | -5.798 | 1.199 | 0.556 |
| $L_{opt}$ | TS-FPDA optical-upper | tsfpda | best-direct | five-point | -1.197 | -5.801 | 3.648 | 0.741 |
| $L_{nom}$ | TS-FPDA nominal-proxy | tsfpda | best-direct | S9-p0 | -3.491 | -7.149 | 0.086 | 0.519 |
| $L_{rob}$ | TS-FPDA receiver-risk | tsfpda | best-direct | S9-p2 | -3.605 | -6.174 | -0.965 | 0.593 |
| $L_{ctrl}$ | TS-FPDA default-flux-control | tsfpda | best-direct | five-point | -0.878 | -4.470 | 2.710 | 0.444 |
| $C_{rad-}$ | same-condition control | control | proxy-selected | S9-p0 | -0.642 | -4.823 | 3.903 | 0.556 |
| $C_{rad+}$ | same-condition control | control | proxy-selected | S9-p0 | -1.196 | -4.548 | 2.313 | 0.444 |
| $C_{wave}$ | same-condition control | control | proxy-selected | S9-p1 | 1.334 | -2.522 | 5.264 | 0.407 |
| $L_{opt}$ | TS-FPDA optical-upper | tsfpda | proxy-selected | S9-p0 | 1.617 | -2.976 | 7.412 | 0.704 |
| $L_{nom}$ | TS-FPDA nominal-proxy | tsfpda | proxy-selected | S9-p2 | 2.114 | -2.310 | 6.733 | 0.370 |
| $L_{rob}$ | TS-FPDA receiver-risk | tsfpda | proxy-selected | S9-p1 | -0.404 | -4.933 | 3.941 | 0.481 |
| $L_{ctrl}$ | TS-FPDA default-flux-control | tsfpda | proxy-selected | S9-p1 | -0.734 | -4.746 | 3.629 | 0.519 |

## Manuscript Interpretation

- Simple controls remain meaningful and should not be hidden. They are part of the evidence boundary.
- A result is manuscript-worthy only if it improves the direct-check queue or clarifies why TS-FPDA should be described as a benchmark generator rather than a globally superior optimizer.
- Do not use this audit as full-field annual certification: the same reduced-check limitations remain.
