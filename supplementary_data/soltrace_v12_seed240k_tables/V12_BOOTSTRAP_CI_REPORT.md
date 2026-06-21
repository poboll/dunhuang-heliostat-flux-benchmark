# V12 Bootstrap Confidence Audit

This report bootstraps the condition-level V12 reduced PySolTrace peak-to-active-mean deltas.
It is used as a reviewer-facing uncertainty check, not as a new optimization pass.

## Best direct row by layout

| Layout | Role | Strategy | Mean % | 95% bootstrap CI | Lower fraction | Evidence grade |
|---|---|---|---:|---:|---:|---|
| $L_{nom}$ | nominal-proxy | S9-p1 | -3.41 | [-6.32, -0.43] | 0.56 | weak reduction |
| $L_{ctrl}$ | default-flux-control | S9-p1 | -2.13 | [-5.47, 1.45] | 0.74 | directional reduction |
| $L_{opt}$ | optical-upper | S9-p2 | -0.39 | [-3.65, 3.10] | 0.70 | directional reduction |
| $L_{rob}$ | receiver-risk | S9-p1 | -0.04 | [-3.00, 3.21] | 0.63 | directional reduction |

## Proxy-selected rows

| Layout | Role | Strategy | Mean % | 95% bootstrap CI | Lower fraction | Evidence grade |
|---|---|---|---:|---:|---:|---|
| $L_{opt}$ | optical-upper | S9-p0 | 3.40 | [0.25, 6.48] | 0.41 | not supported |
| $L_{nom}$ | nominal-proxy | S9-p2 | -0.56 | [-3.54, 2.35] | 0.44 | weak reduction |
| $L_{rob}$ | receiver-risk | S9-p1 | -0.04 | [-3.00, 3.21] | 0.63 | directional reduction |
| $L_{ctrl}$ | default-flux-control | S9-p1 | -2.13 | [-5.47, 1.45] | 0.74 | directional reduction |

## Interpretation

- The best direct V12 rows support directional reductions for $L_{nom}$ and $L_{ctrl}$, but their bootstrap confidence intervals still cross zero.
- $L_{opt}$ remains weak at the V12 scale and should not be described as a receiver-risk-safe optical winner.
- $L_{rob}$ is nearly neutral in V12, so its earlier receiver-risk role should be kept as a queue member rather than a headline winner.
- The correct manuscript claim is role-level screening usefulness, not final aiming-phase optimality.
