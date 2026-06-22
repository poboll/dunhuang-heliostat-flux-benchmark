# Solar Energy CAS-Q2 Elsevier Submission Workspace

This is the strict-review rescue submission workspace for the Dunhuang heliostat full-field layout algorithm and receiver-flux benchmark paper. The current v8 revision uses all-phase, high-sample, independent-seed, baseline-control direct, leave-one-day-out hold-out, missing-20 coordinate-provenance, relative AFD-style flux-proxy, and V12 240k-ray reduced PySolTrace/direct-audit layers on top of the full-field aiming/weather draft.

- `latex/main.tex`: Elsevier `elsarticle` manuscript using `final,3p,times`.
- `latex/main.pdf`: compiled journal-style full-evidence inspection PDF, currently 40 pages in Elsevier `final,3p,times` mode with line numbers disabled for the formal inspection build. The detailed data dictionary, package-index table, and extended roadmap are kept in supplementary/manifest files rather than rendered as a technical-report appendix. The current PDF SHA-256 is recorded in `output/LATEX_BUILD_REPORT.md`.
- `citations/ref.bib`: generated bibliography with 59 cited entries in the compiled PDF.
- `citations/verified.jsonl`: DOI/manual/source verification records.
- `papers/paper_notes.jsonl`: citation metadata notes.
- `template/`: local copy of the installed Elsevier sample template.
- `code/`: key configuration and Python scripts needed to reproduce the candidate generation, numerical-checking summaries, and manuscript-facing figures.
- `latex/figures/`: white-background journal figures rebuilt from the audited run tables.
- `submission_materials/`: highlights, cover letter, declarations, graphical abstract, and reviewer-risk memo.
- `supplementary_data/`: key layout, SolarPILOT, aiming, weather, coordinate-provenance, baseline-control, hold-out, and all-phase SolTrace CSV tables for review.
- `supplementary_data/soltrace_v10_seed_replicate_tables/`: V10 independent-seed stability audit tables and report.
- `supplementary_data/soltrace_v11_convergence_tables/`: consolidated V8/V9/V10 reduced PySolTrace convergence and uncertainty audit tables.
- `supplementary_data/soltrace_v12_seed240k_tables/`: V12 240k-ray reduced PySolTrace follow-up tables and report.
- `supplementary_data/joint_layout_aiming_optimizer/`: integrated joint layout--aiming screening tables for 489 full-field candidates and 121 Pareto rows.
- `supplementary_data/joint_solarpilot_default_tables/`: PySAM/SolarPILOT default-aiming bridge for the baseline and seven joint layouts.
- `supplementary_data/joint_direct_soltrace_tables/`: reduced PySolTrace direct promotion audit for `J_bal`, `J_gain`, and `J_flux`.
- `supplementary_data/joint_system_summary/`: merged proxy, SolarPILOT, and direct-promotion evidence table for the joint representatives.
- `supplementary_data/afd_style_flux_proxy/`: relative AFD-style p95/p99 and hotspot-area proxy audit derived from SolarPILOT default-aiming flux tables.
- `supplementary_data/fast_annual_proxy_sanity/`: fast annual optical proxy and public plant design-generation sanity check built from hourly NASA POWER DNI and SolarPILOT optical-efficiency tables.
- `supplementary_data/flux_resolution_gate/`: SolarPILOT default receiver-bin robustness gate comparing 24 x 24 and 36 x 36 receiver maps.
- `supplementary_data/flux_day_sampling_gate/`: SolarPILOT default-flux sampling robustness gate comparing 8 and 12 flux days.
- `supplementary_data/formal_paired_statistics/`: formal paired condition-level statistics for selected reduced direct rows.
- `supplementary_data/same_anchor_strong_baseline_tables/`: literature-inspired same-anchor strong-baseline pressure test, including pattern-free-, slider-like-, terrain-aware-, and hybrid-approximation families.
- `supplementary_data/strong_baseline_promotion_gate/`: conservative writeback gate for the strong-baseline direct-promotion queue; it keeps `B_hy,E`, `B_pf,R`, and `B_hs,R` out of headline direct-supported claims.
- `supplementary_data/strong_baseline_direct_promotion_queue/`: queued layouts, runbook, and inputs used for the same-run reduced direct gate.
- `supplementary_data/strong_baseline_direct_soltrace_tables/`: completed 27-condition same-run reduced direct gate; no new strong-baseline row passed the proxy-selected bootstrap-CI promotion rule.
- `supplementary_data/geometry_explainability_advantage/`: radial-density, azimuth-sector, nearest-neighbour, movement-scale, and constrained-advantage audit showing how selected full-field layouts move and which role-level claims are supported.
- `SUBMISSION_MAIN_SI_TRANSFER_PLAN_20260523.md`: main-text/Supplementary transfer plan for a future shorter Solar Energy submission package.
- `POINT_BY_POINT_REVIEW_RESPONSE_20260523_FOCUSED_SECOND_REVISION.md`: point-by-point response to the focused second-revision review.
- `VERSION_RESTORATION_AUDIT_20260514.md`: audit explaining why the 17-page v6 short draft was over-pruned and why the evidence-rich full manuscript remains the active author-review track.
- `archive/superseded_v7_soltrace_20260512/`: old 270-case SolTrace figures and tables moved out of the active result set.
- `output/LATEX_BUILD_REPORT.md`: build and QA report.
- `reproducibility_manifest/`: SHA-256 manifest covering the audited run and active submission package.

What changed in the current revision:

- Confirmed the primary target as Solar Energy and documented the Elsevier `elsarticle` template choice.
- Added a direct LetPub/New-Ranking check and a 2026-06-21 XR Scholar browser confirmation: `Solar Energy`, ISSN `0038-092X`, SCIE/Scopus, Engineering/工程技术 `2区 Top`, and JCR `ENERGY & FUELS` `3区`.
- Switched the active build from a loose review layout to a compact journal-style `final,3p,times` layout.
- Rebuilt active figures with an Arial/Helvetica-first white-background style, clearer labels, larger receiver-map panels, and a non-compressed selected-row SolTrace heatmap.
- Recompiled with `pdflatex+bibtex` to use the standard Elsevier/Times font stack and remove XeLaTeX font-substitution warnings.
- Added a 2026 Solar Energy sloped-terrain/spatiotemporal layout reference to keep the research-gap discussion current.
- Replaced the earlier SolTrace text with an all-phase direct-ray 1,485-case matrix with verified stage ordering: 6,000 sampled heliostats per layout, 60,000 requested first-stage ray hits per case, 27 solar conditions, and 11 aiming strategies.
- Added the V9 high-sample reduced PySolTrace confirmation matrix: 9,000 sampled heliostats per layout, 180,000 requested first-stage ray hits per case, 27 solar conditions, five verification-relevant strategies, and a 24-panel receiver grid.
- Added the V10 independent-seed reduced PySolTrace stability audit: same scale as V9, but with a fresh stratified sample to test whether the candidate queue is seed-stable.
- Added the V11 reduced PySolTrace convergence and uncertainty audit, which consolidates V8, V9, and V10 to separate stable candidate roles from seed- and grid-sensitive exact aiming rows.
- Added the V12 240k-ray reduced PySolTrace follow-up, which strengthens the evidence for `L_nom` and `L_ctrl` as next-stage candidates while keeping weak or inconsistent rows out of the headline claim.
- Added a static regression test so the PySolTrace script keeps the heliostat reflector stage before the receiver absorber stage.
- Added Elsevier submission materials and a graphical abstract draft that preserves the conservative claim boundary.
- Added and redesigned `fig_soltrace_allphase_direct_panel.png` as a three-panel direct-row/proxy-transfer/response-surface figure, plus all-phase direct/proxy-selected strategy tables.
- Updated the claim boundary: all-phase reduced direct ray tracing is now reported more strongly, but full-field annual custom-aimpoint verification remains future work.
- Added a 2026 Renewable Energy reference on fast annual energy estimation through heliostat grouping and solar-position sampling.
- Added component-ablation evidence for `deform_0276` and `deform_0893`.
- Added quick SolarPILOT ablation numerical check (`flux-days=2`, `flux-bins=16`).
- Corrected the high-resolution numerical-checking wording to five layouts total.
- Removed internal rejection/journal-positioning language from the manuscript.
- Added weather/DNI anchoring against the reported Dunhuang corrected TMY annual DNI.
- Upgraded aiming-proxy sensitivity to 81 grouping, spot-width, and staggered-phase assumptions so the custom-aimpoint queue is not supported by one arbitrary proxy discretization.
- Updated data/code availability language so the checksum manifest covers layouts, weather, terrain, SolarPILOT tables, proxy tables, sensitivity outputs, figures, and scripts.
- Added a 2026-05-16 response pass: point-by-point P0/P1 review response, receiver-flux normalization and thermal-safety interpretation, DOI/release blocker wording, and a light prose polish pass to reduce repetitive defensive phrasing while preserving the claim boundary.
- Added a final 2026-05-16 author-voice pass: tightened several abstract, introduction, results, discussion, and appendix sentences so the manuscript reads less like a defensive revision memo while keeping the same scientific claim boundary.
- Added a 2026-05-16 late-result writeback: incorporated the completed V12 240k-ray audit into the results, data dictionary, Data and Code Availability statement, manifest, and review-response checklist.
- Added a 2026-05-22/23 strict-review strengthening pass: same-condition low-complexity controls, a reduced direct baseline-control audit, leave-one-day-out strategy-selection audit, line numbers, hidden link boxes, and updated Solar Energy submission materials.
- Added a 2026-05-23 coordinate-provenance hardening pass: a seeded missing-20 random-omission geometry sensitivity audit over 2000 replicates, copied to `supplementary_data/missing20_geometry_sensitivity/` and registered in the manifest.
- Added a 2026-05-23 active system-design pass: a joint layout--aiming screening optimizer, a SolarPILOT default-aiming bridge for joint candidates, and a reduced direct promotion gate. The combined evidence promotes `J_flux` only as a receiver-boundary candidate, keeps `J_bal` as a directional balance candidate, and treats `J_gain` as a strategy-sensitivity case.
- Added a 2026-05-23 focused second-revision pass: a hardened paper-alone Parameter Registry, formal paired statistics with bootstrap CI, Hodges--Lehmann shifts, sign/Wilcoxon tests, a +/-1% practical-indistinguishability threshold, and a main/SI transfer plan. This pass supports `J_flux`, `L_rob`, and V12 `L_nom` as the clearest current receiver-risk candidates, but keeps final engineering superiority out of the claims.
- Added a 2026-05-23 AFD-style flux-proxy pass: SolarPILOT default-aiming flux tables are converted into baseline-relative p95/p99 concentration and active hotspot-area metrics. This strengthens receiver-risk reporting while explicitly avoiding absolute allowable-flux-density or tube-temperature claims.
- Added a 2026-05-23 same-anchor strong-baseline pressure test: 168 literature-inspired approximation candidates are screened under the same Dunhuang coordinate pool, SolarPILOT default bridge, and aiming proxy. The strongest hybrid approximation gives +1.74% default SolarPILOT optical efficiency and -4.44% aiming-proxy concentration change, so the paper now treats TS-FPDA as a benchmark queue rather than a SOTA optimizer.
- Added a 2026-05-23 direct-promotion runbook for the strong-baseline comparison and a 2026-05-24 completed 27-condition reduced direct gate. The gate is included as boundary evidence, not as a new main-text victory result.
- Added a 2026-05-24 fast annual proxy and public plant sanity check: SolarPILOT optical-efficiency tables are interpolated over the 8760-hour public weather file, the annual DNI is scaled to the reported corrected TMY value, and the baseline annual thermal proxy is checked against the 351.6 GWh design-generation reference. This is annualized optical ranking and plant-scale sanity evidence, not bankable annual yield or full-field custom-aimpoint validation.
- Added a 2026-05-24 geometry-explainability and constrained-advantage audit: selected TS-FPDA, joint, control, and strong-baseline rows are compared by radial-density shifts, sector-population shifts, nearest-neighbour spacing, movement-vector direction, annual proxy, default-flux penalty, aiming proxy, AFD-style proxy, and reduced-direct evidence. This audit makes the layout movement interpretable and keeps the conclusion at role-level queue strength rather than SOTA optimizer strength.
- Added 2026-05-24 robustness gates for annual-proxy weather years, annual-proxy interpolation choices, SolarPILOT receiver-bin resolution, and SolarPILOT flux-day sampling density. These gates support short sanity-check statements only; they do not convert the manuscript into annual custom-aimpoint validation, thermal certification, cross-code validation, or a bankable annual-yield study.
- Added a 2026-05-24 strong-baseline direct promotion gate. It merges annual, interpolation, 36-bin SolarPILOT default-flux, 12-flux-day sampling, aiming-proxy, geometry, and the completed same-run reduced direct matrix for the prepared queue. It promotes no new strong-baseline row to a direct-supported headline result, which is why the manuscript keeps `B_hy,E`, `B_pf,R`, and `B_hs,R` as screening or boundary rows rather than winners.
- Added a 2026-06-21 journal-format polish pass: converted the Nomenclature from a numbered long table into compact prose, moved detailed parameter, implementation, workload, verification-protocol, data-dictionary, and roadmap material behind `\iffalse`, and rebuilt the PDF successfully at 40 pages with no undefined references.
- Published the manuscript-facing public package as GitHub release `v0.1.5` (`fix: 同步v0.1.5清单与发布状态`) after the Figure 1 cleanup plus Zenodo metadata pass. That release is now a historical checkpoint because the current local package has a post-release journal-target, wording, README, and DOI-metadata consistency pass. The current release candidate is `v0.1.6`; mint the V8 manuscript-package DOI from that final release if this PDF is submitted.
- Added a 2026-06-22 journal-style cleanup pass: removed the rendered Data/Code Availability package-index table, simplified the representative-role table to reduce broken words, replaced inline V9/V10/V11/V12 path lists with a formal supplementary-package reference, and rebuilt the PDF successfully at 40 pages with 17 rendered figures and 23 rendered tables/algorithm tables.
- Added a 2026-06-22 Figure 1/DOI-metadata pass: rebuilt the lower locator/geometry panel while keeping the author-owned aerial photograph unedited, prepared Zenodo metadata, and refreshed the manifest so the DOI metadata is checksum-registered.
- Added a 2026-06-22 wording/README consistency pass: root README, manuscript Data/Code Availability, and the standalone data-availability statement now separate the source-coordinate DOI from the pending V8 package DOI, and the main article uses benchmark/workflow/queue language instead of final-design or SOTA-optimizer language. The current release candidate is `v0.1.6`.

Current submission stance:

- Submit as an algorithmic benchmark and numerical-checking workflow, not as a final Dunhuang redesign.
- Treat pattern-free, slider-like, terrain-aware, and hybrid strong baselines as pressure-test approximations, not as complete external optimizer reproductions.
- Treat the all-phase reduced PySolTrace matrix as direct but reduced custom-aimpoint evidence.
- Treat the joint layer as the active system contribution: layout deformation and aiming are selected together, then checked by a SolarPILOT default-aiming bridge and a reduced direct promotion audit.
- Treat full-field annual custom-aimpoint verification with receiver thermal constraints as the next scientific upgrade rather than as a hidden completed claim.
- Use this full-evidence v8 package as the current author-review draft. If a shorter Solar Energy main text is later required, use `SUBMISSION_MAIN_SI_TRANSFER_PLAN_20260523.md`; do not silently prune the workload, figures, or evidence chain back to the 17-page v6 short draft.
- Treat GitHub `v0.1.6` as the current manuscript-facing release candidate. After publishing it, mint the Zenodo DOI from the final release and write the DOI back into the manuscript and bibliography.
