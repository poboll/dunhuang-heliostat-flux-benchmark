# Experiment, Figure, and Table Ledger for Solar Energy V8

Generated from `latex/main.tex`. This ledger is manuscript-facing: it separates main-text evidence from supplementary package contents and keeps the claims aligned with the benchmark framing.

## Main Figures

| No. | Label | Section | Source file(s) | Evidence role | Submission note |
|---:|---|---|---|---|---|
| 1 | `fig:layout-realism` | Engineering Validity of the Full-Field Surround Layout | `figures/fig1_author_aerial_fullframe.png`, `figures/fig1_locator_geometry_audit.png` | Qualitative site context plus coordinate/map audit; photograph not quantitative evidence. | Keep; visual QA still recommended for map/geometry style consistency. |
| 2 | `fig:workflow` | PySAM/SolarPILOT Numerical Verification | native TikZ in LaTeX | Benchmark pipeline and claim-boundary schematic. | Keep in main text |
| 3 | `fig:baseline-controls` | Same-condition baseline controls | `figures/fig_baseline_controls_summary.png` | Same-condition low-complexity baseline control evidence. | Keep in main text |
| 4 | `fig:strong-baselines` | Same-anchor strong-baseline pressure test | `figures/fig_same_anchor_strong_baselines.png` | Same-anchor pressure-test evidence against stronger local baseline families. | Keep in main text |
| 5 | `fig:geometry-advantage` | Geometry explainability and constrained advantage audit | `figures/fig_geometry_explainability_advantage.png` | Geometry explainability and constrained advantage evidence. | Keep in main text |
| 6 | `fig:baseline-direct` | Reduced direct baseline-control audit | `figures/fig_baseline_direct_soltrace_controls.png` | Same-condition low-complexity baseline control evidence. | Keep in main text |
| 7 | `fig:joint-optimizer` | Joint layout--aiming screening | `figures/fig_joint_optimizer_pareto.png` | Reduced direct ray-tracing evidence. | Keep in main text |
| 8 | `fig:joint-optimizer-convergence` | Joint layout--aiming screening | `figures/fig_joint_optimizer_convergence.png` | Main visual evidence | Keep in main text |
| 9 | `fig:joint-direct` | Joint direct promotion audit | `figures/fig_joint_direct_summary.png` | Reduced direct ray-tracing evidence. | Keep in main text |
| 10 | `fig:tradeoff` | SolarPILOT default-aiming trade-off | `figures/fig_journal_tradeoff_clean.png` | Receiver-flux risk visualization or proxy evidence. | Keep in main text |
| 11 | `fig:fast-annual-proxy` | Fast annual proxy and public plant sanity check | `figures/fig_fast_annual_proxy_sanity.png` | Fast annual proxy and public-weather robustness evidence. | Keep in main text |
| 12 | `fig:afd-proxy` | Receiver-flux normalization and thermal-safety interpretation | `figures/fig_afd_style_flux_proxy.png` | Receiver-flux risk visualization or proxy evidence. | Keep in main text |
| 13 | `fig:fluxmaps` | Receiver-flux maps | `figures/fig_journal_flux_peak_panel.png` | Receiver-flux risk visualization or proxy evidence. | Keep in main text |
| 14 | `fig:aimproxy` | Aiming-proxy queue | `figures/aiming_flux_deform_0893.png` | Main visual evidence | Keep in main text |
| 15 | `fig:aiming-sensitivity` | Aiming-proxy sensitivity | `figures/aiming_sensitivity_boxplot.png` | Main visual evidence | Keep in main text |
| 16 | `fig:soltrace-corrected` | All-phase reduced SolTrace matrix with verified stage ordering | `figures/fig_soltrace_allphase_direct_panel.png` | Reduced direct ray-tracing evidence. | Consider SI if page pressure is severe; keep if direct evidence is central. |
| 17 | `fig:v9-confirmation` | High-sample reduced PySolTrace confirmation | `figures/fig_v9_highsample_confirmation.png` | Reduced direct ray-tracing evidence. | Consider SI if page pressure is severe; keep if direct evidence is central. |
| 18 | `fig:v10-stability` | Independent-seed V10 stability audit | `figures/fig_v10_seed_replicate_stability.png` | Reduced direct ray-tracing evidence. | Consider SI if page pressure is severe; keep if direct evidence is central. |
| 19 | `fig:v11-convergence` | Convergence and uncertainty audit | `figures/fig_v11_soltrace_convergence_audit.png` | Reduced direct ray-tracing evidence. | Consider SI if page pressure is severe; keep if direct evidence is central. |
| 20 | `fig:formal-paired` | Formal paired-statistics audit | `figures/fig_formal_paired_statistics.png` | Reduced direct ray-tracing evidence. | Consider SI if page pressure is severe; keep if direct evidence is central. |

## Active Main-Text Tables

| Label | Environment | Section | Caption / role | Triage |
|---|---|---|---|---|
| `tab:plant-audit` | table | Introduction | Public Dunhuang plant parameters used to anchor the benchmark. Values are treated as plant-realism constraints rather than as freely tunable optimization variables. | Keep |
| `tab:nearest-work-positioning` | table | Research Gap and Contributions | Nearest-work positioning matrix. The table defines the manuscript's contribution boundary rather than ranking prior work. | Keep |
| `tab:lit-map` | table | Plant realism, heliostat technology, and benchmark need | Literature map used to position the manuscript. | Keep |
| `tab:reframe` | table | Problem Definition | How the revised problem definition differs from a descriptor-only layout comparison. | Keep |
| `tab:param-envelope` | table | Parameter envelope | Deformation parameters and their manuscript role. Numeric values are interpreted as conservative local-search amplitudes around the audited field. | Keep |
| `alg:tfpda` | longtable | Algorithm listing | TS-FPDA: terrain-screened full-field candidate-generation workflow. | Keep |
| `tab:gates` | table | Feasibility filters | Candidate-screening gates used to keep the field complete and engineering-plausible. | Keep |
| `tab:parameter-registry` | table | Benchmark settings and traceability | Core benchmark settings used for the manuscript-facing run. Full parameter registry and checksums are supplied in the reproducibility package. | Keep as compact main-text interpretive table |
| `tab:implementation-details` | table | Implementation traceability | Evidence groups used to audit the benchmark workflow. File-level names and SHA-256 checksums are kept in the supplementary manifest. | Keep as compact evidence-group table |
| `tab:workload` | table | Computational workload and audit scale | Computational workload for the manuscript-facing numerical-verification package. Runtime is audit evidence, not a cross-machine performance claim. | Keep, but do not expand |
| `tab:proxy-metrics` | table | Proxy metrics | Receiver-aiming proxy metrics and how they are used. | Keep |
| `tab:verification-protocol` | longtable | PySAM/SolarPILOT Numerical Verification | Numerical-verification protocol used for the current reproducible package. | Keep |
| `tab:representative-roles` | table | Full-field screening | Representative roles used to prevent cherry-picking. | Keep |
| `tab:baseline-controls` | table | Same-condition baseline controls | Same-condition low-complexity baseline controls and TS-FPDA representatives. All layouts preserve the available 11,915-heliostat coordinate pool. Optical and default-flux changes are from PySAM/SolarPILOT; aiming changes are from the proxy search and remain screening-level evidence. | Keep |
| `tab:strong-baselines` | table | Same-anchor strong-baseline pressure test | Same-anchor strong-baseline pressure test. The baseline families are literature-inspired local approximations under the Dunhuang coordinate anchor, not complete reimplementations of named external optimizers. SolarPILOT values use the common default-aiming bridge; aiming values use the common proxy search. | Keep |
| `tab:baseline-direct` | table | Reduced direct baseline-control audit | Reduced direct PySolTrace baseline-control audit. Negative values indicate lower peak-to-active-mean receiver concentration than the paired baseline under the same condition and aiming strategy. Bootstrap confidence intervals resample the 27 condition-level deltas. | Keep |
| `tab:baseline-direct-holdout` | table | Reduced direct baseline-control audit | Leave-one-day-out direct-ray strategy-selection audit. For each layout, the best aiming strategy is selected on eight representative days and then evaluated on the held-out day. Confidence intervals bootstrap the nine held-out day means. Negative values indicate lower peak-to-active-mean concentration than the paired baseline. | Keep |
| `tab:joint-optimizer` | table | Joint layout--aiming screening | Joint layout--aiming screening representatives. The changes are proxy-level values from the integrated search loop and are normalized to the same baseline and best searched baseline aiming strategy. Negative R_aim | Keep |
| `tab:joint-system-evidence` | table | Joint SolarPILOT bridge | Joint layout--aiming evidence summary across proxy screening, SolarPILOT default-aiming bridge, and reduced direct promotion. SolarPILOT values are relative to the same baseline under default aiming; direct values are paired peak-to-active-mean changes with bootstrap intervals over 27 solar conditions. | Keep |
| `tab:joint-direct` | table | Joint direct promotion audit | Reduced direct promotion audit for the joint layout--aiming representatives. Negative values indicate lower peak-to-active-mean receiver concentration than the paired baseline under the same condition and strategy. Confidence intervals bootstrap the 27 condition-level deltas. | Keep |
| `tab:summary` | table | SolarPILOT default-aiming trade-off | Integrated numerical-checking summary for representative layouts. Optical and default-flux changes are from PySAM/SolarPILOT. Aiming peak-to-mean change is proxy-screened and is not a final SolarPILOT custom-aimpoint claim. The internal triage score is shown only to disclose representative selection and is not used as a headline result. | Keep |
| `tab:ablation` | table | Deformation-component ablation | Component-ablation diagnostics. Proxy metrics come from the screening model; quick SolarPILOT changes are relative to the same quick baseline and are used only for component interpretation. | Keep |
| `tab:candidate-meaning` | table | Aiming-proxy queue | How the current representative candidates should be interpreted. | Keep |
| `tab:aiming-sensitivity` | table | Aiming-proxy sensitivity | Aiming-proxy sensitivity across 81 grouping, spot-width, and staggered-phase assumptions. Negative peak-to-mean change indicates lower proxy concentration relative to the re-optimized baseline under the same condition. | Keep |
| `tab:soltrace-corrected` | table | All-phase reduced SolTrace matrix with verified stage ordering | All-phase reduced PySolTrace matrix with verified reflector-to-receiver stage ordering. Negative values indicate lower peak-to-active-mean receiver concentration than the paired baseline under the same day, hour, and aiming strategy. The top block reports each layout's proxy-selected staggered strategy; the lower block reports the best direct strategy for each layout across all 27 solar conditions and 11 aiming strategies. | Keep |
| `tab:v9-confirmation` | table | High-sample reduced PySolTrace confirmation | High-sample reduced PySolTrace confirmation. Negative values indicate lower peak-to-active-mean receiver concentration than the paired baseline. The confirmation run uses 9,000 sampled heliostats, 180,000 requested first-stage ray hits, five verification-relevant strategies, 27 solar conditions, 24 receiver panels, and a 24 by 72 receiver grid. | Keep |
| `tab:v10-stability` | table | Independent-seed V10 stability audit | Independent-seed V10 stability audit. Negative values indicate lower peak-to-active-mean receiver concentration than the paired baseline. V10 uses the same layouts, strategies, and solar conditions as V9, but a fresh stratified sample and the same 24-panel, 24 by 72 receiver grid. | Keep |
| `tab:v11-convergence` | table | Convergence and uncertainty audit | Reduced PySolTrace convergence and uncertainty audit. The table consolidates the all-phase V8 matrix, the high-sample V9 confirmation, and the independent-seed V10 replicate. Negative best-row mean values indicate lower peak-to-active-mean receiver concentration than the paired baseline under the same audit layer. | Keep |
| `tab:v12-followup` | table | V12 240k-ray follow-up audit | V12 240k-ray reduced PySolTrace follow-up. Negative values indicate lower peak-to-active-mean receiver concentration than the paired baseline under the same day, hour, and aiming strategy. The table reports the best direct row for each non-baseline layout at the V12 scale. | Keep |
| `tab:v12-bootstrap` | table | V12 240k-ray follow-up audit | Bootstrap confidence audit for the V12 240k-ray reduced PySolTrace layer. Confidence intervals resample the 27 representative solar conditions within each layout--strategy row. Negative values indicate lower peak-to-active-mean concentration than the paired baseline under the same strategy and condition. | Keep |
| `tab:formal-paired` | table | Formal paired-statistics audit | Formal paired-statistics summary for the key reduced direct rows. Confidence intervals bootstrap the 27 paired solar-condition deltas. The Wilcoxon test uses the one-sided alternative that the candidate has lower peak-to-active-mean concentration than the paired baseline. | Keep |
| `tab:domain-validity` | table | Domain of validity | Domain of validity and claim boundary for the benchmark. | Keep; protects claim boundary and DOI/data package. |
| `tab:supplement-index` | table | Data and Code Availability | Compact index of the review-facing data package. The complete file-level dictionary and checksums are provided in the supplementary manifest rather than in the main text. | Keep; protects claim boundary and DOI/data package. |
| N/A | prose | Nomenclature | Compact abbreviation and symbol paragraph; no numbered table. | Keep |

## Suppressed / Supplementary-Only Long Tables

The following tables appear after `\iffalse` in `main.tex` and are intentionally not rendered in the main PDF. They should remain in the supplementary material or manifest, not the journal article body.

| Label | Caption / role |
|---|---|
| `tab:threats-validity` | Threats to validity and mitigation summary. |
| `tab:novelty-matrix` | Novelty matrix for positioning the contribution. |
| `tab:data-dictionary` | Detailed data dictionary for the reproducibility package. |
| `tab:completed-future-verification` | Completed and future verification tables. |


## Current Build / Package State

- Latest compile: success on 2026-06-21 using `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex`.
- Current PDF: 46 pages, about 30 MiB, Elsevier `final,3p,times`, line numbers disabled.
- Citation/reference QA: no undefined citations or references.
- Box warnings: one minor 1.90001pt overfull hbox and 54 underfull hboxes, mostly from narrow technical table cells.
- Main-text cleanup: Nomenclature is now prose rather than a numbered long table; the detailed data dictionary and extended roadmap remain suppressed after `\iffalse`; the Data/Code Availability package-index table is fixed to its section and no longer floats into the Conclusions.

## Evidence Boundary Summary

- Main text should claim a reproducible plant-anchored benchmark, not a certified commercial redesign.
- SolarPILOT tables support default-aiming layout comparisons; reduced PySolTrace supports sampled direct-aimpoint checks; neither is a bankable annual-yield validation.
- Negative/uncertain rows should remain as boundary evidence, not be promoted to headline superiority claims.
- The GitHub release is present; the manuscript-package Zenodo DOI is still a pre-upload task.
