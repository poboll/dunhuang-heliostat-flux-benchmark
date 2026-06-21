# Geometry Explainability and Constrained Advantage Audit

This audit addresses the reviewer concern that the manuscript needs to show how the layouts actually move and where the advantage is constrained.

## Main findings

- The strongest annualized optical row remains `L_opt` (`deform_0276`), with a fast annual thermal-proxy change of +3.36%. It is therefore an optical stress case, not a final winner.
- The strongest aiming-proxy reduction among the selected rows is `J_bal` (`joint_g02_0333`), with -8.16%. Its interpretation still depends on direct promotion.
- Direct confidence intervals below zero are available for: L_nom, L_rob, J_flux. These rows form the strongest current receiver-risk evidence boundary.
- The largest p95 movement scale in the audited set is `L_opt` at 107.5 m; the smallest non-baseline p95 movement scale is `C_rad+` at 26.8 m. This confirms that the search is a local count-preserving deformation, not mirror deletion.

## Claim boundary

The constrained table should not be read as a SOTA ranking. It identifies role-level rows: annual optical stress cases, annual-positive screening candidates, receiver-pressure screening candidates, and direct-supported receiver-boundary rows. Strong-baseline rows without reduced direct evidence remain candidates for the prepared direct-promotion queue.

## Generated artifacts

- `tables/geometry_explainability_summary.csv`
- `tables/radial_density_change.csv`
- `tables/sector_population_change.csv`
- `tables/nearest_neighbor_summary.csv`
- `tables/constrained_advantage_summary.csv`
- `figures/fig_geometry_explainability_advantage.png`
- `figures/fig_geometry_explainability_advantage.pdf`
