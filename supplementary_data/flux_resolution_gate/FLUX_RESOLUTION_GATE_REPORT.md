# SolarPILOT Flux-Resolution Robustness Gate

## Scope

This audit compares the existing 24 x 24 SolarPILOT default-flux tables with a higher-resolution
rerun. It checks whether receiver-flux role labels are artifacts of the receiver-bin discretization.
It remains a default-aiming SolarPILOT audit, not custom-aimpoint or thermal certification.

## Selected Roles

| Role   | Layout         |   Peak delta baseline (%) |   Peak delta highres (%) |   Peak shift (pct-pt) |   P99 delta baseline (%) |   P99 delta highres (%) |   P99 shift (pct-pt) |
|:-------|:---------------|--------------------------:|-------------------------:|----------------------:|-------------------------:|------------------------:|---------------------:|
| L_opt  | deform_0276    |                     4.679 |                    4.997 |                 0.318 |                    0.333 |                   0.365 |                0.031 |
| L_nom  | deform_0893    |                     1.399 |                    1.605 |                 0.206 |                   -0.043 |                  -0.068 |               -0.025 |
| L_rob  | deform_1387    |                     2.377 |                    2.229 |                -0.148 |                   -0.658 |                  -0.640 |                0.018 |
| J_bal  | joint_g02_0333 |                     1.780 |                    1.826 |                 0.046 |                   -0.427 |                  -0.535 |               -0.108 |
| J_flux | joint_g04_0478 |                     1.007 |                    0.866 |                -0.141 |                   -0.407 |                  -0.394 |                0.014 |
| B_hs,R | sb_hs_flux     |                    -0.175 |                   -0.190 |                -0.014 |                    0.051 |                  -0.049 |               -0.100 |
| B_hy,E | sb_hy_energy   |                     1.647 |                    2.074 |                 0.427 |                    0.643 |                   0.467 |               -0.176 |
| B_pf,R | sb_pf_flux     |                    -0.539 |                   -0.453 |                 0.087 |                    0.205 |                   0.080 |               -0.124 |

## Gate Decision

- Recommendation: `write_short_resolution_robustness_sentence`.
- Max absolute peak-ratio delta shift: 0.427 pct-pt.
- Max absolute p99-ratio delta shift: 0.176 pct-pt.
- L_opt still has a high-resolution flux penalty: `True`.
- Receiver-pressure rows are not annual headline rows: `True`.
- Interpretation: High-resolution flux maps preserve the manuscript's default-flux role interpretation.

## Boundary

Write this into the manuscript only as a short discretization-robustness sentence if the gate passes.
Do not cite it as receiver thermal safety or same-aimpoint cross-code validation.
