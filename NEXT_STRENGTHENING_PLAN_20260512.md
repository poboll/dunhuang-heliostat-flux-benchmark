# Next Strengthening Plan

Updated: 2026-05-12

## Current assessment

The paper is now a credible SCI-Q2 attempt only as a **benchmark/workflow paper**. The strongest story is not "we redesigned Dunhuang". The strongest story is:

> A plant-anchored full-field layout algorithm exposes that optical efficiency, default receiver flux, proxy aiming, and all-phase reduced direct ray tracing select different candidates.

This is meaningful and current because recent heliostat-field work has moved toward terrain-constrained layout, petal/hybrid layout families, flux-aware aiming, neural surrogates, differentiable optics, and cross-code ray-tracing comparison. A simple coordinate perturbation would be behind the field; a reproducible layout-to-flux numerical-checking queue is still useful.

## Go/no-go for Solar Energy

Go after final QA if the claims remain conservative.

Do not submit if the authors want to claim any of the following:

- final optimized Dunhuang plant layout;
- retrofit recommendation for the operating field;
- full-field annual custom-aimpoint superiority;
- economic superiority from the cost-normalized screening-score layer.

The current package supports:

- full-field candidate generation around 11,915 audited coordinates;
- terrain/geometry audit;
- PySAM/SolarPILOT default-aiming numerical checks;
- aiming-proxy sensitivity;
- all-phase stage-order-corrected reduced PySolTrace custom-aimpoint matrix;
- high-sample reduced PySolTrace confirmation with finer receiver discretization;
- reproducibility package with checksums.

## Next scientific upgrade

The next upgrade should be a higher-fidelity custom-aimpoint numerical-checking layer, not more decorative plotting. The V8 all-phase reduced SolTrace run and V9 high-sample confirmation are now complete and have replaced the earlier 270-case matrix in the active draft. A V10 independent-seed high-sample replicate has been completed on the server to audit whether the V9 reduced-check ranking is stable under a fresh stratified sample.

Minimum queue:

- Layouts: `baseline_full`, `deform_0276`, `deform_0893`, `deform_1387`, `deform_1822`.
- Strategies: default, visible-equator, five-point, proxy-selected staggered, and directly re-optimized staggered phase.
- Conditions: retain the current 9-condition matrix as the pilot; expand either heliostat sampling, solar-position sampling, or both.
- Metrics: intercept, spillage, peak flux, peak-to-active-mean, active-zone CV, total receiver-power proxy, paired deltas versus baseline.

Completed V8/V9 runs:

- V8 output: `server_outputs/streamed_fullfield_20260511_205252/soltrace_allphase_27cond_20260512`.
- V8 scope: 5 layouts x 27 solar conditions x 11 direct strategies = 1,485 reduced SolTrace cases.
- Purpose: test whether the direct-aiming conclusion depends on testing only proxy-selected staggered phases.
- V9 output: `server_outputs/streamed_fullfield_20260511_205252/soltrace_v9_confirm_highsample_20260512`.
- V9 scope: 5 layouts x 27 solar conditions x 5 check-relevant strategies = 675 reduced SolTrace cases, using 9,000 sampled heliostats, 180,000 requested first-stage ray hits, 24 receiver panels, and a 24 by 72 receiver grid.
- V9 interpretation: role-level receiver-risk candidates remain useful, but exact best aiming rows change from V8; the manuscript must keep this as reduced numerical-check evidence rather than a final aiming prescription.

Completed V10/V11 audit:

- Output: `server_outputs/streamed_fullfield_20260511_205252/soltrace_v10_seed_replicate_20260513`.
- Scope: same as V9, but with an independent random seed (`2026051301`).
- Purpose: audit seed/sample stability before deciding whether to write V10 into the manuscript or keep it as supplementary reviewer evidence.
- V11 output: `server_outputs/streamed_fullfield_20260511_205252/soltrace_v11_convergence_audit_20260514`.
- V11 interpretation: candidate roles are more stable than exact aiming rows; small differences must be treated as uncertainty-limited, not final plant redesign evidence.

Decision rule:

- If `deform_1387` or `deform_1822` remains receiver-safer under enlarged direct checks, strengthen the paper toward layout--aiming co-design.
- If rankings change, keep the paper as a benchmark showing why proxy and reduced checks can disagree.
- If all deformations lose under enlarged direct checks, the paper can still be salvaged as a negative benchmark, but the title and abstract must become more conservative.

## Writing upgrades before submission

1. Keep the target journal out of the manuscript text; document it only in submission files.
2. Keep the introduction centered on the numerical-check disagreement, not on a claimed positive redesign.
3. Keep the limitations blunt. A reviewer will notice the 20-heliostat coordinate gap, SRTM terrain resolution, NASA POWER weather, and reduced SolTrace sampling anyway.
4. Do not add more references just for count. The current 61-entry bibliography is enough if every cited stream is used.
5. Preserve the white-background figure style. Avoid reverting to mixed dark/light graphics.

## Immediate QA checklist

- Recompile `latex/main.tex` with `latexmk -pdf -bibtex`.
- Confirm no undefined citations or references.
- Confirm no old pre-correction SolTrace text remains.
- Rebuild the reproducibility manifest after every manuscript or submission-material change.
- Sync the final package to `/Users/Apple/Downloads/官方主题/dunhuang_sci2_rebuild_20260512/`.
