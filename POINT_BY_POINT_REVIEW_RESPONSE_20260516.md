# Point-by-Point Major Revision Response

Date: 2026-05-16

Active package: `solar_energy_elsarticle_v7_balanced_full_submission`

## Stance

The revised manuscript remains a long-form full-submission draft rather than the over-pruned 17-page short version. The evidence chain is intentionally retained: plant audit, full-field TS-FPDA candidate generation, feasibility gates, SolarPILOT default-aiming checks, aiming-proxy sensitivity, reduced PySolTrace V8/V9/V10/V11 audits, data dictionary, and claim-boundary appendix. For Solar Energy submission, a shorter main text plus supplementary file is recommended later, but the current working draft should not be cut until the evidence has been stabilized.

## P0 Items

| Item | Status | Action taken or decision |
|---|---|---|
| P0-1 Data/code DOI | Blocking before submission | The manuscript no longer leaves a literal `[DOI/URL]` placeholder. It now states that the 2026 layout-algorithm and receiver-flux screening package must be deposited as a versioned GitHub/Zenodo record before final submission. No DOI was fabricated. |
| P0-2 Main text too long | Partially adopted | The current v7 is kept as the strengthened full draft because previous compression removed too much evidence. A later submission split should move detailed data dictionary, novelty matrix, claim boundary, and long verification roadmap to Supplementary. |
| P0-3 Reviewer-facing wording | Done | The remaining table header `Reviewer-facing check` was changed to `Audit check`. AI statement wording was also softened from `reviewer-risk checklist` to `revision-risk checklist`. |
| P0-4 Absolute flux / thermal safety | Done for current evidence level | A new subsection, `Receiver-flux normalization and thermal-safety interpretation`, explains why current results use peak-to-active-mean ratio and why absolute kW/m2 or MW/m2 certification would require plant-specific receiver thermal data. |
| P0-5 Reduced PySolTrace claim level | Done | Abstract, discussion, conclusion, and protocol continue to say `reduced checks`, `sampled`, `representative solar conditions`, and `not final commercial redesign`. |
| P0-6 Reference verification | Partially done | Existing audit: 64 BibTeX entries, 64 verification records, no missing cited keys; 54 URL/DOI checks returned HTTP 200 and 10 blocked pages were metadata-confirmed through Crossref/DataCite. Manual publisher-page opening remains recommended before final submission. |
| P0-7 Elsevier AI declaration | Done | Declaration retained in Elsevier style: tools, use cases, author review, verification, and author responsibility. |

## P1 Items

| Item | Status | Current decision |
|---|---|---|
| P1-1 Full-field or enlarged custom-aimpoint verification | Future experiment | Current reduced PySolTrace audits support a screening queue, not final annual custom aiming. Next server run should expand toward full-field/statistically enlarged annual sampling. |
| P1-2 Cross-code sanity check | Future experiment | Not invented in the manuscript. The current package is prepared for SolarPILOT, SolTrace/PySolTrace, and possible Solstice comparison, but no cross-code numerical result is claimed. |
| P1-3 Absolute flux / allowable flux discussion | Partially done | Discussion added. Numeric absolute heat-flux limits are not reported because plant-specific receiver/absorber/control data are unavailable. |
| P1-4 External baseline-family comparison | Future experiment | Component ablation exists, but external SolarPILOT regular/radial-stagger or simple radial/north-shift baseline families should be added in the next experimental iteration. |
| P1-5 Terrain sensitivity | Future experiment | SRTM90m terrain screening is included. High-resolution or perturbed-terrain sensitivity is listed as a next-stage verification table rather than claimed as complete. |

## Submission Readiness Judgment

The paper is defensible as a reproducible full-field numerical benchmark and receiver-flux screening workflow. It should not be submitted as a final Solar Energy article until the 2026 package has a public DOI/URL. To strengthen the chance at Solar Energy Q2/TOP level, the next hard experiments should prioritize: public archive DOI, full-field/enlarged custom-aimpoint verification, absolute receiver-flux scaling with defensible thermal assumptions, cross-code sanity check, and external baseline-family comparison.
