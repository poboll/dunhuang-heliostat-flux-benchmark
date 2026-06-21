# Submission Strategy and Reviewer Audit

## Bottom line

The rebuilt paper has a plausible SCI-Q2 route only if it is framed as an algorithmic benchmark and numerical-checking workflow, not as a final optimized redesign of the Dunhuang plant. The current evidence is meaningful because it exposes disagreement between optical efficiency, default receiver flux, proxy aiming, and all-phase reduced direct ray tracing. That is a real research story. It is not yet strong enough for a top energy journal that expects full annual techno-economic co-design.

## Primary target

Solar Energy is the best first target because its scope explicitly covers solar energy research, development, application, and measurement, and it has a live CSP/heliostat audience. The paper's use of SolarPILOT, receiver flux, full-field layout, and aiming strategy matches that audience better than Scientific Data.

The target is also consistent with the requested SCI/CAS-Q2-style screening. The accessible LetPub/New-Ranking search page lists `Solar Energy` as SCI/SCIE, New-Ranking `2区`, large category `工程技术`, and small category `能源与燃料`. Automated access to `xr-scholar.com/Journals/Search` returned a Cloudflare challenge, so the final administrative checklist still requires manual browser confirmation. This is a planning fact; it should not be written into the manuscript itself.

## Why the topic is still current

Recent work has moved beyond simple layout perturbation. The frontier now includes:

- differentiable Monte Carlo ray tracing and differentiable rasterization for online aiming;
- neural surrogate and constraint-learning approaches for receiver-flux optimization;
- receiver aiming reviews emphasizing non-uniform flux, thermal stress, allowable flux, and dynamic operation;
- deformable petal and hybrid heliostat layouts;
- terrain-constrained and sloped-terrain heliostat-field layout optimization;
- round-robin receiver-flux comparison across ray-tracing tools.

This means the manuscript cannot claim novelty from "petal deformation" alone. Its defensible gap is narrower: a public, plant-anchored, full-field Dunhuang benchmark that preserves heliostat count and links layout generation to receiver-flux numerical checking.

## Practical value

The practical value is preliminary-design and benchmark value, not retrofit value. Moving heliostats in an operating 100 MW plant would be unrealistic because roads, foundations, wiring, land constraints, calibration, and O&M are fixed. The useful contribution is a reproducible large-field test case for algorithms that must decide whether layout, aiming, and receiver-risk metrics agree.

## Current weaknesses to keep visible

- The available coordinate pool has 11,915 heliostats, while the public plant report states 11,935.
- SRTM90m terrain is reproducible but not survey-grade.
- NASA POWER weather is reproducible but not the plant's corrected TMY file.
- PySAM/SolarPILOT numerical checks currently use x/y imported coordinates and default aiming.
- All-phase and high-sample PySolTrace direct aiming are sampled and representative-condition based, not annual full-field custom aiming.
- Proxy aiming results are useful for queueing but not final plant-level verification.

## What changed in this iteration

- Switched the inspection manuscript from loose `preprint,12pt` double spacing to `elsarticle` `final,3p,times`.
- Removed line numbers and double spacing from the visual draft.
- Rebuilt active manuscript figures with one white-background style, Arial/Helvetica-first font rules, clearer callouts, and non-compressed heatmaps.
- Replaced the dark workflow graphic with a white journal workflow figure.
- Rebuilt the receiver-flux and aiming-proxy heatmaps with light low-value backgrounds.
- Replaced the 270-case SolTrace layer with a 1,485-case all-phase direct matrix covering five layouts, 27 solar conditions, visible-equator, five-point, and all nine S9 staggered phases.
- Replaced the corrected SolTrace figure with an all-phase direct panel so the heatmap shows every tested layout--strategy row without compression.
- Added an implementation-details table to make code paths, generated artifacts, and reviewer checks explicit.
- Recompiled with the standard Elsevier `pdflatex+bibtex` path; the active compact PDF is 34 pages and has no undefined citations or references.
- Added recent aiming/layout references while keeping 59 cited entries in the compiled PDF and 63 verification records.
- Added a direct journal-selection audit and tightened the submission claim boundary around the Solar Energy target.
- Added a computational-workload paragraph/table to the manuscript so reviewers can see the scale and cost of the all-phase reduced SolTrace matrix rather than treating it as an opaque figure.
- Added V9 high-sample reduced PySolTrace confirmation. This deliberately weakens any overconfident "best strategy" claim while strengthening the benchmark story: candidate roles are more stable than exact aiming phases.
- Started a V10 independent-seed high-sample replicate on the server to test whether the V9 queue is stable under a fresh stratified sample.

## Next strengthening step

The next real scientific upgrade is not another prettier plot. It is an enlarged annual or statistically representative custom-aimpoint numerical-checking layer using CoPylot/SolarPILOT, SolTrace, or Solstice, with the same layout queue. That would convert the current benchmark from "credible SCI-Q2 candidate" toward a stronger layout--aiming co-design paper.

Recommended queue for that next run:

1. Layouts: `baseline_full`, `deform_0276`, `deform_0893`, `deform_1387`, and `deform_1822`.
2. Strategies: default, visible-equator, five-point, proxy-best staggered, and directly re-optimized staggered phases.
3. Metrics: intercept, spillage, peak flux, peak-to-active-mean flux, active-zone CV, total receiver-power proxy, and paired condition-level deltas.
4. Minimum additional value: treat the current 1,485-case all-phase matrix as the reduced direct-check layer, then expand heliostat sampling or annual solar-position sampling before adding new plant-design claims.
