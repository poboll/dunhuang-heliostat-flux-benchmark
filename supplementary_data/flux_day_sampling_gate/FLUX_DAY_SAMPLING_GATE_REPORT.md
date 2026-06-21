# SolarPILOT Flux-Day Sampling Robustness Gate

## Scope

This audit compares the original eight-flux-day SolarPILOT default-flux tables with an
enlarged twelve-flux-day rerun for the selected direct-promotion layouts. It checks
whether receiver-flux role labels are artifacts of the flux-day sampling density.
It remains a default-aiming SolarPILOT audit, not custom-aimpoint, annual, or thermal certification.

## Selected Roles

| Role   | Layout         |   Peak delta 8-day (%) |   Peak delta 12-day (%) |   Peak shift (pct-pt) |   P99 delta 8-day (%) |   P99 delta 12-day (%) |   P99 shift (pct-pt) |
|:-------|:---------------|-----------------------:|------------------------:|----------------------:|----------------------:|-----------------------:|---------------------:|
| L_opt  | deform_0276    |                  4.679 |                   4.687 |                 0.008 |                 0.333 |                  0.367 |                0.034 |
| L_nom  | deform_0893    |                  1.399 |                   1.401 |                 0.002 |                -0.043 |                 -0.025 |                0.018 |
| L_rob  | deform_1387    |                  2.377 |                   2.379 |                 0.002 |                -0.658 |                 -0.593 |                0.065 |
| J_bal  | joint_g02_0333 |                  1.780 |                   1.783 |                 0.003 |                -0.427 |                 -0.411 |                0.016 |
| J_flux | joint_g04_0478 |                  1.007 |                   1.006 |                -0.001 |                -0.407 |                 -0.334 |                0.073 |
| B_hs,R | sb_hs_flux     |                 -0.175 |                  -0.176 |                -0.001 |                 0.051 |                 -0.011 |               -0.062 |
| B_hy,E | sb_hy_energy   |                  1.647 |                   1.652 |                 0.005 |                 0.643 |                  0.660 |                0.017 |
| B_pf,R | sb_pf_flux     |                 -0.539 |                  -0.541 |                -0.002 |                 0.205 |                  0.241 |                0.036 |

## Gate Decision

- Recommendation: `write_short_flux_day_sampling_sentence`.
- Max absolute peak-ratio delta shift: 0.008 pct-pt.
- Max absolute p99-ratio delta shift: 0.073 pct-pt.
- Pre-set shift threshold: 1.500 pct-pt.
- L_opt still has a 12-day default-flux penalty: `True`.
- Receiver-pressure rows are not optical headline rows: `True`.
- Interpretation: The enlarged SolarPILOT flux-day sample preserves the manuscript's default-flux role interpretation.

## Boundary

Write this into the manuscript only as a short flux-day-sampling robustness sentence if the gate passes.
Do not cite it as receiver thermal safety, annual custom aiming, or same-aimpoint cross-code validation.
