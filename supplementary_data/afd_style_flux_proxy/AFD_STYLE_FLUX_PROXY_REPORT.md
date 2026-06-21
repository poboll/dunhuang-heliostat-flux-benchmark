# Relative AFD-style Receiver-Flux Proxy Audit

This audit converts the existing SolarPILOT default-aiming flux tables into relative
allowable-flux-density-style screening metrics. It does not claim certified receiver
tube safety or a plant-grade thermal model. Instead, it asks whether high-percentile
receiver loading and hotspot-area proxies tell the same story as the simpler
peak-to-active-mean ratio already reported in the manuscript.

Definitions:

- Active cells are cells above the 55th percentile of the layout-specific flux table,
  matching the active-zone convention used in the SolarPILOT summary scripts.
- Baseline p95 and p99 thresholds are computed separately within each SolarPILOT cohort.
- Hot-area proxies report the fraction of active cells above the corresponding baseline
  p95 or p99 threshold. These are relative exceedance metrics, not absolute AFD limits.

## Selected manuscript rows

| Candidate   | Cohort            |   Delta optical (%) |   Delta p99/active-mean |   Active > baseline p99 (%) |   Delta active hot-area (pct-pt) |   Peak/active-mean |
|:------------|:------------------|--------------------:|------------------------:|----------------------------:|---------------------------------:|-------------------:|
| $L_0$       | baseline_controls |               0.000 |                   0.000 |                       1.000 |                            0.000 |              1.364 |
| $C_{rad-}$  | baseline_controls |               0.886 |                   0.001 |                       1.063 |                            0.063 |              1.379 |
| $C_{rad+}$  | baseline_controls |              -0.892 |                  -0.000 |                       0.951 |                           -0.049 |              1.350 |
| $C_{wave}$  | baseline_controls |              -0.013 |                  -0.002 |                       0.884 |                           -0.117 |              1.366 |
| $L_{opt}$   | baseline_controls |               3.148 |                   0.004 |                       1.377 |                            0.377 |              1.428 |
| $L_{nom}$   | baseline_controls |               0.242 |                  -0.001 |                       1.005 |                            0.004 |              1.383 |
| $L_{rob}$   | baseline_controls |               0.706 |                  -0.008 |                       0.772 |                           -0.229 |              1.396 |
| $L_{ctrl}$  | baseline_controls |               0.506 |                  -0.004 |                       0.839 |                           -0.162 |              1.376 |
| $L_0$       | joint_default     |               0.000 |                   0.000 |                       1.000 |                            0.000 |              1.364 |
| $J_{bal}$   | joint_default     |               0.915 |                  -0.005 |                       0.870 |                           -0.130 |              1.388 |
| $J_{gain}$  | joint_default     |               1.644 |                  -0.004 |                       0.942 |                           -0.058 |              1.397 |
| $J_{flux}$  | joint_default     |              -0.692 |                  -0.005 |                       0.727 |                           -0.274 |              1.378 |

## Main interpretation

- $L_{opt}$ remains a stress-test layout: it improves default optical efficiency by +3.15% but increases the active p99 hot-area proxy by +0.38 percentage points relative to the baseline-control cohort.
- $L_{rob}$ is still not thermally certified. Under default aiming its active p99 hot-area proxy changes by -0.23 percentage points, so its stronger receiver-risk role still comes from the direct custom-aimpoint audits rather than from default aiming alone.
- $J_{gain}$ reinforces the bridge/direct split: default SolarPILOT optical efficiency improves by +1.64%, but the active p99 hot-area proxy changes by -0.06 percentage points, so it cannot be claimed as receiver-safe without custom-aimpoint promotion.
- $J_{flux}$ remains a receiver-boundary candidate because of the reduced direct promotion audit, not because of default aiming. Its default-aiming active p99 hot-area proxy changes by -0.27 percentage points.

## Full CSV outputs

- `tables/afd_flux_proxy_summary.csv`: all layouts in both SolarPILOT cohorts.
- `tables/afd_flux_proxy_selected.csv`: manuscript-facing selected rows.
- `figures/fig_afd_style_flux_proxy.png`: compact figure for the manuscript.
