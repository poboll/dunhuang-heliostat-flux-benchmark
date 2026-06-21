# Same-Condition Baseline Strengthening Report

This experiment adds low-complexity controls to test whether the TS-FPDA representatives merely reproduce simple global field transformations.

## Controls

- `C_rad-`: uniform 1.5% radial compaction.
- `C_rad+`: uniform 1.5% radial expansion.
- `C_ell`: simple east-west/west-east ellipse scaling.
- `C_nb`: smooth north/south radial redistribution.
- `C_wave`: two-lobe radial wave.
- `C_stag`: pure azimuthal stagger.

All controls preserve the 11,915 available heliostats and are evaluated with the same public terrain layer, the same SolarPILOT bridge, and the same aiming-proxy search used for the representative layouts.

## Main observations

- Best simple-control SolarPILOT optical gain: `C_rad-` / `ctrl_radial_compact_015` at +0.89%, with default flux-ratio change +1.07%.
- Best simple-control default-flux ratio: `C_rad+` / `ctrl_radial_expand_015` at -1.04%, with SolarPILOT optical change -0.89%.
- Best simple-control aiming-proxy ratio: `C_wave` / `ctrl_ring_wave_012` at -2.38%, with SolarPILOT optical change -0.01%.
- TS-FPDA representatives remain interpretable as role-based candidates rather than a single winner. The comparison should be written as a claim-boundary check, not as a state-of-the-art superiority claim.

Main tables:

- `tables/baseline_proxy_geometry.csv`
- `tables/baseline_comparison_integrated.csv`
- `tables/baseline_comparison_publication.csv`

Main figure:

- `figures/fig_baseline_controls_summary.png`
