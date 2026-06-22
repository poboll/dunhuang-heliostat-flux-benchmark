# Submission Repository and DOI Status

Updated: 2026-06-22 CST, v0.1.7 release-clone package prepared after verified v0.1.6 release

## Current Target

- Target journal: *Solar Energy* using the Elsevier `elsarticle` class (`final,3p,times`).
- Manuscript framing: plant-anchored, receiver-flux-aware, reproducible layout--aiming benchmark and screening evidence ladder.
- No new experiments are required for this status pass; the report records packaging and claim-boundary readiness.
- Current PDF identity for the post-v0.1.6 polish package in the clean release clone: 40 pages, 30,905,489 bytes, SHA-256 `9b5b2cdbd283a08d525d1439bb60d75b7e431a78cfedbe0c5201668c920861e5`.

## Repository / Release

- Manuscript-facing GitHub release recorded in the current manuscript: <https://github.com/poboll/dunhuang-heliostat-flux-benchmark/releases/tag/v0.1.7>.
- Previous verified public release: <https://github.com/poboll/dunhuang-heliostat-flux-benchmark/releases/tag/v0.1.6>.
- Previous `v0.1.6` release title: `fix: 更新v0.1.6投稿包口径与DOI元数据`.
- Previous `v0.1.6` target commit: `bded4aa827ed8070fb95305fafd433b0d614231d`.
- Previous `v0.1.6` archive: `solar_energy_elsarticle_v8_strict_review_rescue_20260622_v016.zip`, SHA-256 `017641e0623397f3c166888b236a9b0841bf642a9b46c950e68601095dc84c8a`.
- Source coordinate DOI already cited in the manuscript: `10.5281/zenodo.16957381` as the coordinate-source record only.
- Current clean package status: post-`v0.1.6` polish package prepared for `v0.1.7`. It includes the cleaner Figure 1/China locator treatment, a more formal TikZ workflow, and `v0.1.7` Data/Code Availability URL. The public `v0.1.6` release remains a verified checkpoint but should not be used for DOI deposition if this current PDF is submitted.
- Zenodo metadata draft: `.zenodo.json` has been prepared at the package root with `v0.1.7` metadata and the `v0.1.7` GitHub release URL. Add the minted DOI after Zenodo deposition.
- DOI runbook: `submission_materials/zenodo_doi_runbook_v017.md`.
- Required before final DOI-bearing journal upload: publish a clean GitHub `v0.1.7` release from this exact package, mint a new Zenodo DOI from that release, and cite it as the algorithm/data package DOI. Do not reuse the coordinate-source DOI for the full V8 benchmark package.

## Local Package Inventory

- Active clean release package: `/Users/Apple/Developer/paper/dunhuang-heliostat-flux-benchmark-release`
- Main LaTeX source: `/Users/Apple/Developer/paper/dunhuang-heliostat-flux-benchmark-release/latex/main.tex`
- Active PDF: `/Users/Apple/Developer/paper/dunhuang-heliostat-flux-benchmark-release/latex/main.pdf`
- Current formal inspection PDF: 40 pages. The exact byte size and SHA-256 are recorded in `output/LATEX_BUILD_REPORT.md` after each compile.
- Active figure assets in `latex/figures`: 33 files.
- Supplementary-data file count: 390 under `supplementary_data/`.
- Reproducibility manifest file count: see `reproducibility_manifest/manifest.json` for the authoritative count and checksums after the `v0.1.7` candidate refresh.
- DOI metadata in manifest: the checksum manifest should include `.zenodo.json`, `submission_materials/zenodo_metadata_v017.json`, and `submission_materials/zenodo_doi_runbook_v017.md`.
- Manifest present: `/Users/Apple/Developer/paper/dunhuang-heliostat-flux-benchmark-release/reproducibility_manifest/MANIFEST.md` (yes).
- README present: `/Users/Apple/Developer/paper/dunhuang-heliostat-flux-benchmark-release/README.md` (yes).

## Claim Boundary Guardrails

- Main-text claims should use `benchmark`, `candidate-generation workflow`, `screening queue`, and `evidence ladder` rather than `field-optimal design`, `SOTA optimizer`, or `commercial redesign`.
- SolarPILOT/PySAM checks are default-aiming layout-level checks; reduced PySolTrace checks are sampled direct-aimpoint evidence over representative conditions.
- Annual proxy results are sanity and ranking evidence over public weather years, not a dispatch model or bankable annual-yield estimate.
- The aerial photograph is author-owned field context from Zengye Su using DJI Mavic 3 Pro; it is not a quantitative measurement source.

## Immediate Submission Tasks

1. Publish and verify a clean GitHub `v0.1.7` release for the current PDF before final DOI-bearing upload.
2. Mint a Zenodo DOI from the verified `v0.1.7` release.
3. Add the newly minted DOI to `Data and Code Availability`, `citations/ref.bib`, `.zenodo.json`, and the standalone data-availability statement.
4. Keep the detailed data dictionary in supplementary files, not in the rendered journal article body.

## 2026-06-22 Repository Caution

- The main worktree is intentionally not staged wholesale because it contains many historical, generated, and unrelated files. Do not use `git add .` from the dirty working copy.
- The public GitHub repository is reachable as `poboll/dunhuang-heliostat-flux-benchmark`; `v0.1.6` is the latest verified public release at the time of this status update, while `v0.1.7` is the current clean release target.
- The manuscript was rebuilt after `v0.1.1` to remove the rendered package-index table and improve page-level journal style. The verified `v0.1.6` release carries the earlier Figure 1 cleanup, Zenodo metadata, journal-target reassessment, and benchmark-wording guardrail; the `v0.1.7` candidate adds the final Figure 1/Figure 2 journal polish and version consistency.
- The 2026-06-22 wording pass keeps the article framed as a benchmark and direct-promotion queue, keeps detailed file dictionaries in the manifest rather than in the article body, and requires DOI deposition from the release that exactly matches the submitted PDF.
