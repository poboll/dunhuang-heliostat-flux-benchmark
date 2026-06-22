# Submission Repository and DOI Status

Updated: 2026-06-22 CST, post-Figure-1/Zenodo-metadata cleanup

## Current Target

- Target journal: *Solar Energy* using the Elsevier `elsarticle` class (`final,3p,times`).
- Manuscript framing: plant-anchored, receiver-flux-aware, reproducible layout--aiming benchmark and screening evidence ladder.
- No new experiments are required for this status pass; the report records packaging and claim-boundary readiness.

## Repository / Release

- Manuscript-facing GitHub release recorded in the manuscript: <https://github.com/poboll/dunhuang-heliostat-flux-benchmark/releases/tag/v0.1.3>.
- GitHub release title: `fix: 更新Solar Energy V8投稿包排版与数据可用性`.
- Release archive name: `solar_energy_elsarticle_v8_strict_review_rescue_20260622.zip`; the final SHA-256 is recorded on the GitHub release asset and companion `.sha256` file.
- Source coordinate DOI already cited in the manuscript: `10.5281/zenodo.16957381` as the coordinate-source record only.
- Current local package status: the working package has been prepared as the `v0.1.3` manuscript-facing release candidate, including Figure 1 lower-panel rebuild, LaTeX panel-label/caption cleanup, Zenodo metadata/runbook files, and a refreshed checksum manifest.
- Zenodo metadata draft: `.zenodo.json` has been prepared at the package root with `v0.1.3` metadata and the `v0.1.3` GitHub release URL. Add the minted DOI after Zenodo deposition.
- DOI runbook: `submission_materials/zenodo_doi_runbook_v013.md`.
- Required before final journal upload: mint a new Zenodo DOI from the final manuscript-facing release and cite it as the algorithm/data package DOI. Do not reuse the coordinate-source DOI for the full V8 benchmark package.

## Local Package Inventory

- Active package: `/Users/Apple/Developer/paper/dunhuang-heliostat-rebuild-server/paper_submission/solar_energy_elsarticle_v8_strict_review_rescue`
- Main LaTeX source: `/Users/Apple/Developer/paper/dunhuang-heliostat-rebuild-server/paper_submission/solar_energy_elsarticle_v8_strict_review_rescue/latex/main.tex`
- Active PDF: `/Users/Apple/Developer/paper/dunhuang-heliostat-rebuild-server/paper_submission/solar_energy_elsarticle_v8_strict_review_rescue/latex/main.pdf`
- Current formal inspection PDF: 40 pages, 30,903,055 bytes (about 29.5 MiB).
- Active figure assets in `latex/figures`: 33 files.
- Supplementary-data file count: 390 under `supplementary_data/`.
- Reproducibility manifest file count: 612 checked files after the 2026-06-22 journal-style cleanup, Figure 1 cleanup, Zenodo-metadata inventory, and stale-preview pruning; see `reproducibility_manifest/manifest.json` for the authoritative count and checksums.
- DOI metadata in manifest: the checksum manifest now includes both `.zenodo.json` and `submission_materials/zenodo_metadata_v013.json`.
- Manifest present: `/Users/Apple/Developer/paper/dunhuang-heliostat-rebuild-server/paper_submission/solar_energy_elsarticle_v8_strict_review_rescue/reproducibility_manifest/MANIFEST.md` (yes).
- README present: `/Users/Apple/Developer/paper/dunhuang-heliostat-rebuild-server/README.md` (yes).

## Claim Boundary Guardrails

- Main-text claims should use `benchmark`, `candidate-generation workflow`, `screening queue`, and `evidence ladder` rather than `field-optimal design`, `SOTA optimizer`, or `commercial redesign`.
- SolarPILOT/PySAM checks are default-aiming layout-level checks; reduced PySolTrace checks are sampled direct-aimpoint evidence over representative conditions.
- Annual proxy results are sanity and ranking evidence over public weather years, not a dispatch model or bankable annual-yield estimate.
- The aerial photograph is author-owned field context from Zengye Su using DJI Mavic 3 Pro; it is not a quantitative measurement source.

## Immediate Submission Tasks

1. Use the clean `v0.1.3` GitHub release as the manuscript-facing archive.
2. Mint a Zenodo DOI for that final manuscript-facing release before final upload.
3. Add the newly minted DOI to `Data and Code Availability` and `citations/ref.bib`.
4. Keep the detailed data dictionary in supplementary files, not in the rendered journal article body.

## 2026-06-22 Repository Caution

- The main worktree is intentionally not staged wholesale because it contains many historical, generated, and unrelated files. Do not use `git add .` from the dirty working copy.
- The public GitHub repository is reachable as `poboll/dunhuang-heliostat-flux-benchmark`; `v0.1.3` is the intended manuscript-facing release for the current local package.
- The manuscript was rebuilt after `v0.1.1` to remove the rendered package-index table and improve page-level journal style. The `v0.1.3` package adds the Figure 1 and Zenodo-metadata cleanup on top of the earlier public release.
