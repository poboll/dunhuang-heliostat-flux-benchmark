# LaTeX Build Report

Updated: 2026-06-22 CST

## Build Command

`latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex`

## Result

- Status: success
- Output PDF: `/Users/Apple/Developer/paper/dunhuang-heliostat-rebuild-server/paper_submission/solar_energy_elsarticle_v8_strict_review_rescue/latex/main.pdf`
- Page count: 40
- PDF size: 30,901,565 bytes on disk, reported as about 29.5 MiB for submission planning.
- Template/class: Elsevier `elsarticle`, `final,3p,times`
- Line numbers: disabled for the formal inspection build

## Citation / Reference QA

- Undefined citation/reference warnings: 0

## Box Warnings

- Overfull hbox count: 1
- Underfull hbox count: 28
- Overfull details: one minor `1.90001pt` overfull while output is active

## Visual QA Render

Rendered preview pages are stored in `output/pdf_previews/` and `output/pdf_previews/latest/`. The current pass specifically checked Figure 1, the workflow region, direct/statistics pages, and the final Data/Code Availability region.

## Interpretation

The current PDF compiles cleanly under the Solar Energy/Elsevier inspection format. The manuscript now uses a compact Nomenclature section rather than a numbered long table, keeps the detailed data dictionary and extended audit tables suppressed after `\iffalse`, and replaces the former Data/Code Availability package-index table with concise prose. Remaining underfull warnings come from narrow table cells and wrapped technical terms; they are layout polish items rather than build blockers.

## 2026-06-21 Consistency Pass

- Re-ran `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex` after the benchmark-wording cleanup.
- Verified the current PDF with `pypdf`: 40 pages, 30,901,565 bytes.
- Re-scanned the LaTeX log: no undefined citation/reference warnings were found; the remaining layout warnings are one minor overfull hbox and 28 underfull hboxes from narrow table cells.
- Refreshed the reproducibility manifest after the PDF, report, Figure 1, and Zenodo-metadata updates; it now records 612 checked files after stale-preview pruning. The manuscript-facing public archive has been advanced to GitHub release `v0.1.5` for this exact local package.

## 2026-06-22 Journal-Style Cleanup

- Replaced the rendered Data/Code Availability package-index table with prose, so the main article no longer shows a directory-style artifact inventory.
- Simplified the representative-role table from three narrow columns to two wider columns to reduce broken words and improve page-14 readability.
- Replaced an inline multi-path V9/V10/V11/V12 run-log sentence with a formal supplementary-package reference.
- Rebuilt successfully with `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex`.
- Current rendered inventory after this cleanup: 17 main figures and 23 main tables/algorithm tables.

## 2026-06-22 Figure 1 and Zenodo-Metadata Cleanup

- Rebuilt the Figure 1 lower locator/geometry panel and kept the author-owned aerial photograph unedited, with the panel label handled by LaTeX rather than drawn into the photograph.
- Verified the current PDF with `pypdf`: 40 pages, 30,901,565 bytes.
- Refreshed the reproducibility manifest after adding DOI metadata files to the package inventory; it now records 612 checked files, including `.zenodo.json` and `submission_materials/zenodo_metadata_v015.json`.
- The current local package is the `v0.1.5` release package. Mint the Zenodo DOI from that release before DOI-bearing journal upload.
