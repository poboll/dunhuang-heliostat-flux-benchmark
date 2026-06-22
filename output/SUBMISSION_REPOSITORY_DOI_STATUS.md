# Submission Repository and DOI Status

Updated: 2026-06-22 CST, v0.1.6 release-candidate consistency pass

## Current Target

- Target journal: *Solar Energy* using the Elsevier `elsarticle` class (`final,3p,times`).
- Manuscript framing: plant-anchored, receiver-flux-aware, reproducible layout--aiming benchmark and screening evidence ladder.
- No new experiments are required for this status pass; the report records packaging and claim-boundary readiness.

## Repository / Release

- Manuscript-facing GitHub release recorded in the manuscript: <https://github.com/poboll/dunhuang-heliostat-flux-benchmark/releases/tag/v0.1.6>.
- Intended GitHub release title: `fix: 更新v0.1.6投稿包口径与DOI元数据`.
- Intended release archive name: `solar_energy_elsarticle_v8_strict_review_rescue_20260622_v016.zip`; SHA-256 will be recorded in the companion `.sha256` release asset after the archive is built.
- Source coordinate DOI already cited in the manuscript: `10.5281/zenodo.16957381` as the coordinate-source record only.
- Current local package status: `v0.1.6` release candidate after the journal-target reassessment, benchmark-wording guardrail, README consistency, and DOI-metadata update. The public `v0.1.5` release remains the previous archival checkpoint and should not be treated as identical to this PDF.
- Zenodo metadata draft: `.zenodo.json` has been prepared at the package root with `v0.1.6` metadata and the `v0.1.6` GitHub release URL. Add the minted DOI after Zenodo deposition.
- DOI runbook: `submission_materials/zenodo_doi_runbook_v016.md`.
- Required before final journal upload: mint a new Zenodo DOI from the final manuscript-facing release and cite it as the algorithm/data package DOI. Do not reuse the coordinate-source DOI for the full V8 benchmark package.

## Local Package Inventory

- Active package: `/Users/Apple/Developer/paper/dunhuang-heliostat-rebuild-server/paper_submission/solar_energy_elsarticle_v8_strict_review_rescue`
- Main LaTeX source: `/Users/Apple/Developer/paper/dunhuang-heliostat-rebuild-server/paper_submission/solar_energy_elsarticle_v8_strict_review_rescue/latex/main.tex`
- Active PDF: `/Users/Apple/Developer/paper/dunhuang-heliostat-rebuild-server/paper_submission/solar_energy_elsarticle_v8_strict_review_rescue/latex/main.pdf`
- Current formal inspection PDF: 40 pages. The exact byte size and SHA-256 are recorded in `output/LATEX_BUILD_REPORT.md` after each compile.
- Active figure assets in `latex/figures`: 33 files.
- Supplementary-data file count: 390 under `supplementary_data/`.
- Reproducibility manifest file count: see `reproducibility_manifest/manifest.json` for the authoritative count and checksums after the v0.1.6 refresh.
- DOI metadata in manifest: the checksum manifest should include `.zenodo.json` and `submission_materials/zenodo_metadata_v016.json`.
- Manifest present: `/Users/Apple/Developer/paper/dunhuang-heliostat-rebuild-server/paper_submission/solar_energy_elsarticle_v8_strict_review_rescue/reproducibility_manifest/MANIFEST.md` (yes).
- README present: `/Users/Apple/Developer/paper/dunhuang-heliostat-rebuild-server/README.md` (yes).

## Claim Boundary Guardrails

- Main-text claims should use `benchmark`, `candidate-generation workflow`, `screening queue`, and `evidence ladder` rather than `field-optimal design`, `SOTA optimizer`, or `commercial redesign`.
- SolarPILOT/PySAM checks are default-aiming layout-level checks; reduced PySolTrace checks are sampled direct-aimpoint evidence over representative conditions.
- Annual proxy results are sanity and ranking evidence over public weather years, not a dispatch model or bankable annual-yield estimate.
- The aerial photograph is author-owned field context from Zengye Su using DJI Mavic 3 Pro; it is not a quantitative measurement source.

## Immediate Submission Tasks

1. Publish the clean `v0.1.6` GitHub release from the current release-candidate package before DOI minting.
2. Mint a Zenodo DOI for the final manuscript-facing release before final upload.
3. Add the newly minted DOI to `Data and Code Availability` and `citations/ref.bib`.
4. Keep the detailed data dictionary in supplementary files, not in the rendered journal article body.

## 2026-06-22 Repository Caution

- The main worktree is intentionally not staged wholesale because it contains many historical, generated, and unrelated files. Do not use `git add .` from the dirty working copy.
- The public GitHub repository is reachable as `poboll/dunhuang-heliostat-flux-benchmark`; `v0.1.5` is the latest already-published manuscript-facing release, while `v0.1.6` is the current release candidate.
- The manuscript was rebuilt after `v0.1.1` to remove the rendered package-index table and improve page-level journal style. The `v0.1.6` candidate carries the Figure 1 cleanup, Zenodo metadata, journal-target reassessment, and benchmark-wording guardrail on top of the earlier public release.
- The 2026-06-22 wording pass keeps the article framed as a benchmark and direct-promotion queue, updates the release candidate to `v0.1.6`, and keeps detailed file dictionaries in the manifest rather than in the article body.
