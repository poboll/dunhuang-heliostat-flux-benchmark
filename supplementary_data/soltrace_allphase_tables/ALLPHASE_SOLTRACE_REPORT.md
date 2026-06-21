# All-Phase Reduced SolTrace Matrix Report

This report summarizes the all-phase direct PySolTrace check layer. It tests visible-equator, five-point, and all nine S9 staggered phases under paired baseline comparisons.

## Detected Matrix Scope

| matrix_rows | layouts | strategies | conditions | sampled_heliostats | rays_per_case | intercept_min | intercept_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1485 | 5 | 11 | 27 | 6000 | 60000 | 0.639 | 0.748 |

Detected condition IDs: d20_h10, d20_h12, d20_h14, d80_h10, d80_h12, d80_h14, d110_h10, d110_h12, d110_h14, d140_h10, d140_h12, d140_h14, d172_h10, d172_h12, d172_h14, d200_h10, d200_h12, d200_h14, d230_h10, d230_h12, d230_h14, d266_h10, d266_h12, d266_h14, d326_h10, d326_h12, d326_h14.

Detected solar days: 20, 80, 110, 140, 172, 200, 230, 266, 326; detected hours: 10.0, 12.0, 14.0.

## Best Direct Strategy by Layout

| layout_id | strategy | cases | median_delta_peak_pct | mean_delta_peak_pct | share_lower_peak | median_delta_intercept_pctpt |
| --- | --- | --- | --- | --- | --- | --- |
| deform_1387 | staggered_levels:9:0.380:1 | 27 | -0.656 | -2.978 | 0.704 | -0.043 |
| deform_0893 | staggered_levels:9:0.380:2 | 27 | -0.364 | -2.780 | 0.556 | -0.117 |
| deform_1822 | staggered_levels:9:0.380:0 | 27 | -8.622 | -2.321 | 0.741 | 0.137 |
| deform_0276 | staggered_levels:9:0.380:0 | 27 | -0.401 | -0.817 | 0.667 | 1.357 |

## Proxy-Selected Strategies Under Direct Tracing

| layout_id | proxy_strategy | direct_median_delta_peak_pct | direct_mean_delta_peak_pct | direct_share_lower_peak |
| --- | --- | --- | --- | --- |
| deform_1387 | staggered_levels:9:0.380:1 | -0.656 | -2.978 | 0.704 |
| deform_0893 | staggered_levels:9:0.380:2 | -0.364 | -2.780 | 0.556 |
| deform_1822 | staggered_levels:9:0.380:1 | -0.591 | -2.320 | 0.593 |
| deform_0276 | staggered_levels:9:0.380:0 | -0.401 | -0.817 | 0.667 |

## Run Config

The stored run configuration below may correspond to the final tail-acceleration job. The detected matrix scope above is computed from the merged output tables and is the authoritative scope used for manuscript claims.

```json
{
  "run": "/home/kk/projects/paper/dunhuang-heliostat-rebuild-sci2/server_outputs/streamed_fullfield_20260511_205252",
  "config": "/home/kk/projects/paper/dunhuang-heliostat-rebuild-sci2/configs/server_full.json",
  "pysoltrace_dir": "/home/kk/projects/paper/tools/SolTrace/app/deploy/api",
  "layout_ids": "baseline_full,deform_0276,deform_0893,deform_1387,deform_1822",
  "days": [
    200,
    230,
    266,
    326
  ],
  "hours": [
    10.0,
    12.0,
    14.0
  ],
  "strategies": [
    "visible_equator",
    "five_point",
    "staggered_levels:9:0.380:0",
    "staggered_levels:9:0.380:1",
    "staggered_levels:9:0.380:2",
    "staggered_levels:9:0.380:3",
    "staggered_levels:9:0.380:4",
    "staggered_levels:9:0.380:5",
    "staggered_levels:9:0.380:6",
    "staggered_levels:9:0.380:7",
    "staggered_levels:9:0.380:8"
  ],
  "proxy_best": {
    "baseline_full": "staggered_levels:9:0.380:0",
    "deform_0276": "staggered_levels:9:0.380:0",
    "deform_0567": "staggered_levels:9:0.380:1",
    "deform_0665": "staggered_levels:9:0.380:8",
    "deform_0893": "staggered_levels:9:0.380:2",
    "deform_1387": "staggered_levels:9:0.380:1",
    "deform_1444": "staggered_levels:9:0.380:2",
    "deform_1822": "staggered_levels:9:0.380:1"
  },
  "max_heliostats": 6000,
  "rays": 60000,
  "threads": 10,
  "receiver_panels": 18,
  "receiver_nx": 20,
  "receiver_ny": 60,
  "seed": 2026051214
}
```

## Claim Boundary

This remains reduced direct ray tracing, not full-field annual custom-aimpoint certification. Its role is to test whether the direct-aiming conclusion depends on testing only proxy-selected staggered phases.
