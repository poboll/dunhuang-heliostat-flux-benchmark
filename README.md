# Solar Energy CAS-Q2 Elsevier Submission Workspace

This is the strengthened submission workspace for the Dunhuang heliostat full-field layout algorithm and receiver-flux benchmark paper. The current revision uses all-phase, high-sample, and independent-seed reduced PySolTrace direct-ray matrices with verified reflector-to-receiver stage ordering on top of the full-field aiming/weather draft.

- `latex/main.tex`: Elsevier `elsarticle` manuscript using `final,3p,times`.
- `latex/main.pdf`: compiled compact journal-style inspection PDF.
- `citations/ref.bib`: generated bibliography with 59 cited entries in the compiled PDF.
- `citations/verified.jsonl`: DOI/manual/source verification records.
- `papers/paper_notes.jsonl`: citation metadata notes.
- `template/`: local copy of the installed Elsevier sample template.
- `code/`: key configuration and Python scripts needed to reproduce the candidate generation, numerical-checking summaries, and manuscript-facing figures.
- `latex/figures/`: white-background journal figures rebuilt from the audited run tables.
- `submission_materials/`: highlights, cover letter, declarations, graphical abstract, and reviewer-risk memo.
- `supplementary_data/`: key layout, SolarPILOT, aiming, weather, and all-phase SolTrace CSV tables for review.
- `supplementary_data/soltrace_v10_seed_replicate_tables/`: V10 independent-seed stability audit tables and report.
- `supplementary_data/soltrace_v11_convergence_tables/`: consolidated V8/V9/V10 reduced PySolTrace convergence and uncertainty audit tables.
- `VERSION_RESTORATION_AUDIT_20260514.md`: audit explaining why the 17-page v6 short draft was over-pruned and why this 35-page v7 package is the active full manuscript.
- `archive/superseded_v7_soltrace_20260512/`: old 270-case SolTrace figures and tables moved out of the active result set.
- `output/LATEX_BUILD_REPORT.md`: build and QA report.
- `reproducibility_manifest/`: SHA-256 manifest covering the audited run and active submission package.

What changed in the current revision:

- Confirmed the primary target as Solar Energy and documented the Elsevier `elsarticle` template choice.
- Added a direct LetPub/New-Ranking check: `Solar Energy`, ISSN `0038-092X`, New-Ranking `2区`, large category `工程技术`, small category `能源与燃料`, SCI/SCIE signal. Automated `xr-scholar` access was blocked by Cloudflare, so manual browser confirmation remains on the final checklist.
- Switched the active build from a loose review layout to a compact journal-style `final,3p,times` layout.
- Rebuilt active figures with an Arial/Helvetica-first white-background style, clearer labels, larger receiver-map panels, and a non-compressed selected-row SolTrace heatmap.
- Recompiled with `pdflatex+bibtex` to use the standard Elsevier/Times font stack and remove XeLaTeX font-substitution warnings.
- Added a 2026 Solar Energy sloped-terrain/spatiotemporal layout reference to keep the research-gap discussion current.
- Replaced the earlier SolTrace text with an all-phase direct-ray 1,485-case matrix with verified stage ordering: 6,000 sampled heliostats per layout, 60,000 requested first-stage ray hits per case, 27 solar conditions, and 11 aiming strategies.
- Added the V9 high-sample reduced PySolTrace confirmation matrix: 9,000 sampled heliostats per layout, 180,000 requested first-stage ray hits per case, 27 solar conditions, five verification-relevant strategies, and a 24-panel receiver grid.
- Added the V10 independent-seed reduced PySolTrace stability audit: same scale as V9, but with a fresh stratified sample to test whether the candidate queue is seed-stable.
- Added the V11 reduced PySolTrace convergence and uncertainty audit, which consolidates V8, V9, and V10 to separate stable candidate roles from seed- and grid-sensitive exact aiming rows.
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

Current submission stance:

- Submit as an algorithmic benchmark and numerical-checking workflow, not as a final Dunhuang redesign.
- Treat the all-phase reduced PySolTrace matrix as direct but reduced custom-aimpoint evidence.
- Treat full-field annual custom-aimpoint verification with receiver thermal constraints as the next scientific upgrade rather than as a hidden completed claim.
- Use this 35-page v7 package as the current author-review manuscript. If a shorter Solar Energy main text is later required, first prepare an explicit main-text versus Supplementary Information transfer table; do not silently prune the workload, figures, or evidence chain back to the 17-page v6 short draft.
