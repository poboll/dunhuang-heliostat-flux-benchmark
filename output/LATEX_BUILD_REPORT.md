# LaTeX Build Report

Updated: 2026-06-22 CST

## Build Command

`latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex`

## Result

- Status: success
- Output PDF: `/Users/Apple/Developer/paper/dunhuang-heliostat-rebuild-server/paper_submission/solar_energy_elsarticle_v8_strict_review_rescue/latex/main.pdf`
- Page count: 40
- PDF size: 30,901,688 bytes on disk, reported as about 29.5 MiB for submission planning.
- PDF SHA-256: `d0ea90a580fe7cf68c229d1e12f9999f2fbeebb2db4626e03134b4e31ab590af`
- Template/class: Elsevier `elsarticle`, `final,3p,times`
- Line numbers: disabled for the formal inspection build

## Citation / Reference QA

- Undefined citation/reference warnings: 0

## Box Warnings

- Overfull hbox count: 1
- Underfull hbox count: 28
- Overfull details: one minor `1.90001pt` overfull while output is active

## Visual QA Render

Rendered preview pages are stored in `output/pdf_previews/`. The current QA pass specifically checked the title/abstract page, Figure 1, the workflow/table region, direct/statistics pages, and the final Data/Code Availability / references region.

## Interpretation

The current PDF compiles cleanly under the Solar Energy/Elsevier inspection format. The manuscript now uses a compact Nomenclature section rather than a numbered long table, keeps the detailed data dictionary and extended audit tables suppressed after `\iffalse`, and replaces the former Data/Code Availability package-index table with concise prose. Remaining underfull warnings come from narrow table cells and wrapped technical terms; they are layout polish items rather than build blockers.

## 2026-06-21 Consistency Pass

- Re-ran `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex` after the benchmark-wording cleanup.
- Verified the current PDF with `pypdf`: 40 pages, 30,901,589 bytes.
- Re-scanned the LaTeX log: no undefined citation/reference warnings were found; the remaining layout warnings are one minor overfull hbox and 28 underfull hboxes from narrow table cells.
- Refreshed the reproducibility manifest after the PDF, report, Figure 1, and Zenodo-metadata updates; it now records 612 checked files after stale-preview pruning. The manuscript-facing public archive has been advanced to GitHub release `v0.1.5` for this exact local package.

## 2026-06-22 Journal-Style Cleanup

- Replaced the rendered Data/Code Availability package-index table with prose, so the main article no longer shows a directory-style artifact inventory.
- Simplified the representative-role table from three narrow columns to two wider columns to reduce broken words and improve page-14 readability.
- Replaced an inline multi-path V9/V10/V11/V12 run-log sentence with a formal supplementary-package reference.
- Rebuilt successfully with `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex`.
- Current rendered inventory after this cleanup: 17 main figures and 23 main tables/algorithm tables.

## 2026-06-22 Figure 1 and Zenodo-Metadata Cleanup (Historical v0.1.5 Checkpoint)

- Rebuilt the Figure 1 lower locator/geometry panel and kept the author-owned aerial photograph unedited, with the panel label handled by LaTeX rather than drawn into the photograph.
- Verified the current PDF with `pypdf`: 40 pages, 30,901,589 bytes.
- Refreshed the reproducibility manifest after adding DOI metadata files to the package inventory; at that checkpoint it recorded 612 checked files, including `.zenodo.json` and `submission_materials/zenodo_metadata_v015.json`.
- This was superseded by the later `v0.1.6` release-candidate consistency pass below.

## 2026-06-22 v0.1.5 Release and Final QA (Historical Checkpoint)

- Created and verified GitHub release `v0.1.5`: <https://github.com/poboll/dunhuang-heliostat-flux-benchmark/releases/tag/v0.1.5>.
- Release target commit: `4c8974ac94f32e2b548b9ae2e1922b1ebc60acfc`.
- Release asset: `solar_energy_elsarticle_v8_strict_review_rescue_20260622_v015.zip`, SHA-256 `c563354a987d6341dedb8155bfb1cfe8847e8a4229719279a55ed5f1e22cdd86`.
- Re-ran `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex`: all targets up to date and successful.
- Rechecked with `pypdf`: 40 pages, 30,901,589 bytes.
- Re-scanned the LaTeX log: no undefined citation/reference warnings, no missing cross-reference rerun warning, one minor `1.90001pt` overfull hbox, and 28 underfull hbox warnings from narrow table cells.
- Checked `\includegraphics` targets: 20 references, 0 missing files.
- Rendered current QA previews for pages 1, 5, 14, 31, 37, and 40 under `output/pdf_previews/current_qa/`; no obvious clipping, overlap, missing map context, or directory-table artifact was found.

## 2026-06-22 Submission-Wording and README Consistency Pass (Superseded by v0.1.6)

- Updated the root README at that checkpoint so `v0.1.5` was the only current manuscript-facing release; older `v0.1.1`--`v0.1.4` releases were historical archives.
- Adjusted the manuscript wording from `candidate generator` / `method` toward `candidate-generation workflow` and `benchmark workflow` where the wording could be misread as a SOTA optimizer or final field design.
- Revised Data and Code Availability prose so the source-coordinate DOI and the V8 manuscript package are separated clearly. This wording was later advanced to the `v0.1.6` release-candidate URL.
- Condensed the standalone data-availability statement from a long path list into evidence-role groups while preserving the manifest as the file-level dictionary.
- Re-ran `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex`: success.
- Rechecked with `pypdf`: 40 pages, 30,901,704 bytes, SHA-256 `8921f263ffa7191764387faa800263b963be44f39d643cca50f326fa193d861a`.
- Re-scanned the LaTeX log: no undefined citations, no undefined references, no rerun warning, one minor overfull hbox, and 28 underfull hboxes from narrow table cells.
- Checked `\includegraphics` targets: 20 references, 0 missing files.
- Re-rendered QA previews for pages 1, 5, 14, 31, 37, and 40 under `output/pdf_previews/current_qa/`; Figure 1, the TikZ workflow, Data/Code Availability, and the final reference page show no obvious clipping or overlap.

## 2026-06-22 Benchmark-Wording Guardrail Pass

- Replaced the remaining visible `method superiority`, `SOTA ranking`, and `final optimum` style phrases with benchmark/workflow/queue wording where they could imply a standalone optimizer claim.
- Updated `output/EXPERIMENT_FIGURE_TABLE_LEDGER.md` and `submission_materials/reviewer_risk_response_memo.md` so the paper is described as a candidate-generation workflow and evidence ladder rather than a candidate generator or civil-design drawing.
- Re-ran `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex`: success.
- Current PDF: 40 pages, 30,901,697 bytes, SHA-256 `fd17a102743dfb109d1e13d6a90ae23ee94a5d4daa64f95882bcf7d30a47e381`.
- Log QA: 0 undefined citations, 0 undefined references, no rerun warning, 20 `\includegraphics` references with 0 missing files, 17 rendered figure labels, and 23 rendered table/algorithm labels.
- Remaining box warnings are unchanged in kind: one minor 1.90001 pt overfull hbox and 28 underfull hboxes from narrow table cells.
- Refreshed the active package manifest in `reproducibility_manifest/`; it still records 618 checked files and now contains the current PDF hash.

## 2026-06-22 v0.1.6 Release-Candidate Consistency Pass

- Updated the manuscript Data and Code Availability URL, `.zenodo.json`, standalone data-availability statement, DOI runbook, repository/DOI status report, root README, package README, and experiment ledger from the post-`v0.1.5` state to the `v0.1.6` release-candidate state.
- Kept the old Zenodo DOI `10.5281/zenodo.16957381` only as the coordinate-source DOI; the full V8 manuscript package still requires a new Zenodo DOI minted from the final GitHub release.
- Re-ran `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex`: success.
- Current PDF: 40 pages, 30,901,688 bytes, SHA-256 `d0ea90a580fe7cf68c229d1e12f9999f2fbeebb2db4626e03134b4e31ab590af`.
- Log QA: 0 undefined citations, 0 undefined references, no rerun warning, 20 `\includegraphics` references with 0 missing files, one minor overfull hbox, and 28 underfull hboxes from narrow table cells.
- Refreshed the active package manifest in `reproducibility_manifest/`; it records 618 checked files and includes `.zenodo.json`, `submission_materials/zenodo_metadata_v016.json`, `submission_materials/zenodo_doi_runbook_v016.md`, and the current PDF hash.
