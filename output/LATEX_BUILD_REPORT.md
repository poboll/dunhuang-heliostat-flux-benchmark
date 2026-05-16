# LaTeX Build Report

Generated: 2026-05-16

## Build

- Command: `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex`
- Target: `paper_submission/solar_energy_elsarticle_v7_balanced_full_submission/latex/main.pdf`
- Result: success
- Pages: 35 (verified from the LaTeX build output after adding the receiver-flux normalization subsection)

## QA

- Undefined citations: none after final latexmk pass.
- Undefined references: none after final latexmk pass.
- Remaining warnings: one tiny `1.90001pt` overfull hbox and several underfull hboxes caused by long path-like identifiers in the Data and Code Availability section.
- Tests: `conda run --no-capture-output -n uu python -m pytest -q` returned `4 passed`.
- Manifest: rebuilt with 261 files, including the regenerated Fig. 1 split assets, reference URL/metadata recheck records, `FIGURE_TABLE_FONT_REFERENCE_AUDIT_20260515.md`, and `POINT_BY_POINT_REVIEW_RESPONSE_20260516.md`.
- Figure QA: Fig. 1 is now a true stacked layout: the real Dunhuang heliostat-field aerial photograph taken by co-author Zengye Su using a DJI Mavic 3 Pro drone is inserted as the upper image through a pixel-identical, no-resampling PNG conversion, while the original WebP is copied byte-for-byte into the figure package. Panel (b) is a GEO/China-wide projected locator with Gansu highlighted; panel (c) uses compact role labels below the coordinate audit rather than an in-panel text block. Fig. 2 is a native TikZ white-background evidence-flow diagram with thin rules and feedback explanation in the caption. Fig. 5 is a six-panel white-background warm heatmap figure; Fig. 11 uses the consolidated color-blind-friendly convergence palette.
- Table QA: page renders around pages 29--31 confirm repeated longtable headers for the detailed data dictionary and verification-roadmap tables.
- Reference QA: `ref.bib` has 64 entries, `verified.jsonl` has 64 records, 60 keys are cited in the manuscript, and no cited key is missing from BibTeX. Automated DOI/URL reachability returned 54 HTTP 200 responses plus 10 publisher/method blocks; all 10 non-200 DOI landing pages were then metadata-confirmed through Crossref or DataCite and written to `citations/reference_metadata_recheck_failed_dois_20260515.jsonl`.

## Version stance

This is the balanced full-submission draft. It restores the long-form workload, story figure, evidence chain, parameter envelope, implementation traceability, V8/V9/V10/V11 reduced PySolTrace audits, data dictionary, claim-boundary appendix, and extended experimental roadmap that were over-pruned in the compact v6 short draft. The compact v6 package is retained only as a conservative short/safe draft and should not replace this full manuscript unless the journal specifically requests a shorter main text.

## Scientific caveat retained

The package remains a local release candidate until the authors create a public GitHub/Zenodo record for the new 2026 algorithm and receiver-flux screening archive. The older DOI `10.5281/zenodo.16957381` is cited only as the source coordinate package. The manuscript now makes this a pre-submission blocker instead of leaving a literal DOI/URL placeholder.

## 2026-05-16 reviewer-response fixes

- Removed the remaining `Reviewer-facing check` table header from the manuscript and replaced it with `Audit check`.
- Added `Receiver-flux normalization and thermal-safety interpretation`, defining `q''_peak` and `q''_mean,active` while explaining why the current package reports peak-to-active-mean screening ratios rather than unsupported absolute kW/m2 or MW/m2 heat-flux certification.
- Softened the AI declaration wording from `reviewer-risk checklist` to `revision-risk checklist` while preserving the Elsevier-style author-responsibility statement.
- Rewrote Data and Code Availability to state that the 2026 package must be publicly archived before final submission; no DOI was fabricated.
- Added `POINT_BY_POINT_REVIEW_RESPONSE_20260516.md` and updated `/Users/Apple/Developer/Pycharm/q/定日镜场修改请按点核对.md` with P0/P1 completion status.
