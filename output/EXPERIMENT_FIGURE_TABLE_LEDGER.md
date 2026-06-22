# Experiment, Figure, and Table Ledger for Solar Energy V8

Updated: 2026-06-22 CST after the `v0.1.10` metadata/status correction pass. Generated against the latest compiled `latex/main.aux`, so this ledger reflects the rendered PDF rather than hidden `\iffalse` supplementary blocks.

## Rendered Inventory

- Main rendered figures: 17.

- Main rendered tables/algorithm tables: 23 including one compact algorithm longtable.

- Hidden/supplementary labels in `main.tex` but absent from the compiled `.aux`: 12. These are retained as supplementary evidence and are not counted as main-article pages.

- The main paper keeps the evidence ladder visible, but file-level data dictionaries, long run logs, V9/V10/V11/V12 expanded tables, threats-to-validity matrices, future-verification roadmaps, and the former package-index table stay outside the rendered journal body. The rendered Data and Code Availability section now cites the intended `v0.1.10` release and manifest in prose rather than displaying a directory-style table.

## Experiment Evidence Ladder

| Layer | Evidence included in the paper/package | Main figures/tables | Claim level |
|---|---|---|---|
| Plant and coordinate audit | Public Dunhuang plant parameters, 11,915-coordinate audited pool, disclosed 20-record gap, random-omission geometry stress test in the supplement | `tab:plant-audit`, `fig:layout-realism` | Plant-anchored numerical benchmark, not as-built survey |
| Candidate generation | Terrain-screened full-field petal/sector deformation, 1,841 screened candidates, count/sector/annulus/spacing/terrain gates | `alg:tfpda`, `tab:param-envelope`, `tab:gates` | Conservative candidate-generation workflow |
| Receiver proxy screening | Aiming-proxy metrics, representative queue, aiming sensitivity over grouping/spot/phase assumptions | `tab:proxy-metrics`, `tab:representative-roles`, `fig:aimproxy`, `fig:aiming-sensitivity` | Screening-level receiver-risk evidence |
| SolarPILOT default-aiming bridge | Common PySAM/SolarPILOT checks for representative layouts, optical efficiency, default receiver-flux maps, receiver-grid and flux-day robustness gates in the supplement | `tab:summary`, `fig:tradeoff`, `fig:fluxmaps` | Layout-level numerical checking under default aiming |
| Baseline and ablation pressure | Same-condition low-complexity controls, literature-inspired same-anchor approximation families, component ablation | `tab:baseline-controls`, `fig:baseline-controls`, `tab:strong-baselines`, `fig:strong-baselines`, `tab:ablation` | Prevents single-method or SOTA-overclaim |
| Annualized optical sanity | Fast annual proxy over public weather, multi-year and interpolation robustness gates, public 351.6 GWh design-generation sanity reference | `fig:fast-annual-proxy` plus supplementary annual-proxy tables | Relative annualized optical ranking only |
| Reduced direct checks | Baseline-control, hold-out, all-phase, high-sample, independent-seed, V12, joint-promotion, and strong-baseline direct gates | `tab:baseline-direct`, `tab:joint-direct`, `tab:soltrace-corrected`, `fig:baseline-direct`, `fig:joint-direct`, `fig:soltrace-corrected` | Sampled direct custom-aimpoint evidence |
| Formal statistics and boundary | Bootstrap confidence intervals, Wilcoxon/sign tests, practical-threshold gate, domain-of-validity table | `tab:formal-paired`, `fig:formal-paired`, `tab:domain-validity` | Candidate promotion queue; no final engineering superiority |

## Main Figures

| No. | Label | Source / type | Evidence role | Keep in main? |
|---:|---|---|---|---|
| 1 | `fig:layout-realism` | PNG figure asset | site context and coordinate/map audit. | Yes |
| 2 | `fig:workflow` | native TikZ | method pipeline and claim boundary. | Yes |
| 3 | `fig:baseline-controls` | PNG figure asset | same-condition low-complexity baseline controls. | Yes |
| 4 | `fig:strong-baselines` | PNG figure asset | strong local baseline pressure test. | Yes |
| 5 | `fig:geometry-advantage` | PNG figure asset | geometry explainability and role-level evidence. | Yes |
| 6 | `fig:baseline-direct` | PNG figure asset | reduced direct control audit. | Yes |
| 7 | `fig:joint-optimizer` | PNG figure asset | joint layout-aiming screening. | Yes |
| 8 | `fig:joint-optimizer-convergence` | PNG figure asset | joint screening convergence. | Yes |
| 9 | `fig:joint-direct` | PNG figure asset | joint reduced direct promotion. | Yes |
| 10 | `fig:tradeoff` | PNG figure asset | SolarPILOT optical-flux trade-off. | Yes |
| 11 | `fig:fast-annual-proxy` | PNG figure asset | annual proxy and plant-scale sanity. | Yes |
| 12 | `fig:afd-proxy` | PNG figure asset | relative receiver-flux proxy. | Yes |
| 13 | `fig:fluxmaps` | PNG figure asset | default-aiming receiver-flux maps. | Yes |
| 14 | `fig:aimproxy` | PNG figure asset | aiming proxy map example. | Yes |
| 15 | `fig:aiming-sensitivity` | PNG figure asset | aiming-proxy robustness. | Yes |
| 16 | `fig:soltrace-corrected` | PNG figure asset | all-phase reduced direct audit. | Yes |
| 17 | `fig:formal-paired` | PNG figure asset | paired statistical claim boundary. | Yes |

## Main Tables and Algorithm Tables

| No. | Label | Env. | Caption / role | Triage |
|---:|---|---|---|---|
| 1 | `tab:plant-audit` | `table` | Public Dunhuang plant parameters used to anchor the benchmark. Values are treated as plant-realism constraints rather than as freely tunable optimization variables. | Keep in main |
| 2 | `tab:nearest-work-positioning` | `table` | Nearest-work positioning matrix. The table defines the manuscript's contribution boundary rather than ranking prior work. | Keep in main |
| 3 | `tab:lit-map` | `table` | Literature map used to position the manuscript. | Keep in main |
| 4 | `tab:reframe` | `table` | How the revised problem definition differs from a descriptor-only layout comparison. | Keep in main |
| 5 | `alg:tfpda` | `longtable` | TS-FPDA: terrain-screened full-field candidate-generation workflow. | Keep as compact algorithm table |
| 6 | `tab:param-envelope` | `table` | Deformation parameters and their manuscript role. Numeric values are interpreted as conservative local-search amplitudes around the audited field. | Keep in main |
| 7 | `tab:gates` | `table` | Candidate-screening gates used to keep the field complete and engineering-plausible. | Keep in main |
| 8 | `tab:proxy-metrics` | `table` | Receiver-aiming proxy metrics and how they are used. | Keep in main |
| 9 | `tab:representative-roles` | `table` | Representative roles used to prevent cherry-picking. | Keep in main |
| 10 | `tab:baseline-controls` | `table` | Same-condition low-complexity baseline controls and TS-FPDA representatives. All layouts preserve the available 11,915-heliostat coordinate pool. Optical and default-flux changes are from PySAM/SolarPILOT; aiming changes are from the proxy  | Keep in main |
| 11 | `tab:strong-baselines` | `table` | Same-anchor strong-baseline pressure test. The baseline families are literature-inspired local approximations under the Dunhuang coordinate anchor, not complete reimplementations of named external optimizers. SolarPILOT values use the commo | Keep in main |
| 12 | `tab:baseline-direct` | `table` | Reduced direct PySolTrace baseline-control audit. Negative values indicate lower peak-to-active-mean receiver concentration than the paired baseline under the same condition and aiming strategy. Bootstrap confidence intervals resample the 2 | Keep in main |
| 13 | `tab:baseline-direct-holdout` | `table` | Leave-one-day-out direct-ray strategy-selection audit. For each layout, the best aiming strategy is selected on eight representative days and then evaluated on the held-out day. Confidence intervals bootstrap the nine held-out day means. Ne | Keep in main |
| 14 | `tab:joint-optimizer` | `table` | Joint layout-aiming screening representatives. The changes are proxy-level values from the integrated search loop and are normalized to the same baseline and best searched baseline aiming strategy. Negative $ R_{aim | Keep in main |
| 15 | `tab:joint-system-evidence` | `table` | Joint layout-aiming evidence summary across proxy screening, SolarPILOT default-aiming bridge, and reduced direct promotion. SolarPILOT values are relative to the same baseline under default aiming; direct values are paired peak-to-active-m | Keep in main |
| 16 | `tab:joint-direct` | `table` | Reduced direct promotion audit for the joint layout-aiming representatives. Negative values indicate lower peak-to-active-mean receiver concentration than the paired baseline under the same condition and strategy. Confidence intervals boots | Keep in main |
| 17 | `tab:summary` | `table` | Integrated numerical-checking summary for representative layouts. Optical and default-flux changes are from PySAM/SolarPILOT. Aiming peak-to-mean change is proxy-screened and is not a final SolarPILOT custom-aimpoint claim. The internal tri | Keep in main |
| 18 | `tab:ablation` | `table` | Component-ablation diagnostics. Proxy metrics come from the screening model; quick SolarPILOT changes are relative to the same quick baseline and are used only for component interpretation. | Keep in main |
| 19 | `tab:candidate-meaning` | `table` | How the current representative candidates should be interpreted. | Keep in main |
| 20 | `tab:aiming-sensitivity` | `table` | Aiming-proxy sensitivity across 81 grouping, spot-width, and staggered-phase assumptions. Negative peak-to-mean change indicates lower proxy concentration relative to the re-optimized baseline under the same condition. | Keep in main |
| 21 | `tab:soltrace-corrected` | `table` | All-phase reduced PySolTrace matrix with verified reflector-to-receiver stage ordering. Negative values indicate lower peak-to-active-mean receiver concentration than the paired baseline under the same day, hour, and aiming strategy. The to | Keep in main |
| 22 | `tab:formal-paired` | `table` | Formal paired-statistics summary for the key reduced direct rows. Confidence intervals bootstrap the 27 paired solar-condition deltas. The Wilcoxon test uses the one-sided alternative that the candidate has lower peak-to-active-mean concent | Keep in main |
| 23 | `tab:domain-validity` | `table` | Domain of validity and claim boundary for the benchmark. | Keep; protects claim boundary |

## Supplementary / Hidden Evidence

The following source labels remain in `main.tex` after `\iffalse` or are represented by prose plus supplementary files rather than rendered as main-article tables. They preserve the evidence chain without making the PDF read like a technical report.

- `tab:v9-confirmation`
- `fig:v9-confirmation`
- `tab:v10-stability`
- `fig:v10-stability`
- `tab:v11-convergence`
- `fig:v11-convergence`
- `tab:v12-followup`
- `tab:v12-bootstrap`
- `tab:threats-validity`
- `tab:novelty-matrix`
- `tab:data-dictionary`
- `tab:completed-future-verification`
- `tab:supplement-index`

## Package and DOI State

- The current verified manuscript-facing release is GitHub release `v0.1.10` (`fix: 发布v0.1.10投稿包最终归档源`), target commit `1239ae2a25869c0e127491aa1fd165b0a540599a`.
- The current `v0.1.10` release archive is `solar_energy_elsarticle_v8_strict_review_rescue_20260622_v010.zip`, SHA-256 `b4c5b850ab7b212775d93570d91d8669ce524d904f525314f8d1de2bdd4f6d2d`, with a companion `.sha256` asset. The current PDF SHA-256 is `367d1a731b589bd455e6a47e9ad47a0e79550f8e8a9b4578ea19a2754403981a`.
- The `v0.1.10` package is a metadata/status correction over the earlier author-review releases. It does not add experiments or broaden the claim boundary.
- The already-published cleanup archives `v0.1.5`, `v0.1.6`, `v0.1.7`, `v0.1.8`, and `v0.1.9` remain historical checkpoints and should not be treated as the final DOI-deposition package now that `v0.1.10` is verified.
- The older `v0.1.1` archive remains a historical package and should not be used as the final DOI-bearing upload if the submitted PDF is the current 2026-06-22 cleanup build.
- The older Zenodo DOI `10.5281/zenodo.16957381` is the coordinate-source DOI only. A new Zenodo DOI for the full V8 benchmark package should be minted from the final GitHub release before DOI-bearing journal submission.
- Current checksum manifest should include `.zenodo.json`, `submission_materials/zenodo_metadata_v010.json`, `submission_materials/zenodo_doi_runbook_v010.md`, the latest 40-page `latex/main.pdf`, refreshed QA preview pages, README/status reports, and figure/data/code artifacts.
- Root `README.md`, package `README.md`, manuscript Data/Code Availability, and `submission_materials/data_availability_statement.md` now agree that the verified `v0.1.10` release is the DOI-deposition source if this current PDF is submitted.

## Claim Boundary Summary

- Main text claims a plant-anchored, receiver-flux-aware, reproducible layout-aiming benchmark and screening queue.
- SolarPILOT/PySAM evidence is default-aiming layout-level evidence; reduced PySolTrace evidence is sampled direct-aimpoint evidence over representative conditions.
- The paper does not claim a certified commercial redesign, final plant-optimal layout, receiver thermal certification, or bankable annual-yield estimate.
