# Version Restoration Audit

Generated: 2026-05-14

## Why this audit exists

The compact `solar_energy_elsarticle_v6_submission_short` draft was useful for removing over-claims, defensive wording, and unsupported submission language. However, it over-pruned the manuscript. It reduced the paper to 17 pages and removed too much of the workload narrative, visual story, evidence chain, implementation detail, and extended verification logic that made the project look like a full algorithmic benchmark rather than a small layout note.

The active manuscript is therefore restored to `solar_energy_elsarticle_v7_balanced_full_submission`. This version keeps the safer claim boundaries from v6 while restoring the substantive content from the richer pre-pruning drafts.

## Version comparison

| Version | Main role | Source lines | Figures | Tables | Compiled pages | Current status |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `v1` | Early long reconstruction | 604 | 5 | 8 | 45 | Superseded; too loose and report-like. |
| `v2_streamed` | Long streamed-run draft | 602 | 5 | 8 | 45 | Superseded; useful historical evidence. |
| `v3_reviewer_strengthened` | Reviewer-risk strengthened draft | 630 | 5 | 9 | 46 | Superseded; contained useful boundary language. |
| `v4_aiming_weather` | Aiming/weather expanded draft | 747 | 9 | 12 | 55 | Superseded; too long but contains story/evidence material. |
| `v5_soltrace_matrix` | Complete technical draft | 772 | 10 | 13 | 26 | Technical/supplementary reference. |
| `v6_submission_short` | Conservative short/safe draft | 458 | 5 | 4 | 17 | Retained only as compact option, not active main draft. |
| `v7_balanced_full_submission` | Balanced full submission draft | 983 | 11 | 16 | 34 | Active manuscript. |

## Content restored in v7

- Full workload evidence: screened 1,841 full-field candidates; exported representatives; all-phase, high-sample, independent-seed, and consolidated reduced PySolTrace audits.
- Visual story: author-captured aerial context, geometry audit, workflow figure, SolarPILOT trade-off figure, receiver-flux panels, aiming sensitivity, all-phase direct-check plot, V9/V10/V11 uncertainty figures.
- Evidence chain: plant audit -> coordinate provenance -> bounded full-field deformation -> feasibility gates -> proxy screening -> SolarPILOT default-aiming checks -> reduced PySolTrace direct custom-aimpoint checks -> V11 convergence and claim boundary.
- Method detail: parameter envelope, feasibility filters, implementation traceability, computational workload table, proxy metric definitions, reduced ray-tracing settings.
- Appendices: algorithm audit checklist, reproducibility package, threats to validity, extended literature positioning, extended algorithm specification, experimental roadmap, data dictionary, claim boundary, and future verification tables.
- Aerial photograph handling: restored because the author states the image is self-captured with a DJI drone. The manuscript uses it only as qualitative site context with author permission, not as quantitative evidence or a coordinate source.

## Claim-boundary fixes retained from v6

- The manuscript does not claim an official as-built Dunhuang survey.
- The 11,915-coordinate pool is disclosed as 20 records fewer than the reported 11,935-heliostat plant count; the missing records are not synthetically completed.
- The old DOI `10.5281/zenodo.16957381` is cited only as the source coordinate archive, not as the new 2026 algorithm/receiver-flux package DOI.
- SolarPILOT results are described as default-aiming numerical checks, not full custom-aimpoint certification.
- Reduced PySolTrace results are described as sampled direct checks over representative conditions, not full-field annual plant certification.
- Proxy cost and receiver metrics are screening scores, not economic or commercial redesign claims.

## Current verification

- Active PDF: `latex/main.pdf`
- Page count: 34 pages
- LaTeX status: successful `latexmk -g -pdf -bibtex -interaction=nonstopmode -halt-on-error main.tex`
- Undefined citations/references: none after final pass
- Tests: `pytest -q` returned `4 passed`
- Reproducibility manifest: 254 checked files

## Practical recommendation

Use v7 as the manuscript the authors review next. Keep v6 as an emergency compact version or as a source for later journal-length compression only after the authors explicitly decide which figures, appendices, and tables can move to supplementary information. Do not treat v6 as the main paper by default.
