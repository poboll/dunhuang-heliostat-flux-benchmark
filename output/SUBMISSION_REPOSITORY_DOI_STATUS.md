# Submission Repository and DOI Status

Updated: 2026-06-22 CST

## Current Target

- Target journal: *Solar Energy* using the Elsevier `elsarticle` class (`final,3p,times`).
- Manuscript framing: plant-anchored, receiver-flux-aware, reproducible layout--aiming benchmark and screening evidence ladder.
- No new experiments are required for this status pass; the report records packaging and claim-boundary readiness.

## Repository / Release

- Manuscript-facing GitHub release recorded in the manuscript: <https://github.com/poboll/dunhuang-heliostat-flux-benchmark/releases/tag/v0.1.2>.
- GitHub release title: `fix: 更新Solar Energy V8投稿包排版与数据可用性`.
- Release archive name: `solar_energy_elsarticle_v8_strict_review_rescue_20260622.zip`; the final SHA-256 is recorded on the GitHub release asset and companion `.sha256` file.
- Source coordinate DOI already cited in the manuscript: `10.5281/zenodo.16957381` as the coordinate-source record only.
- Required before final journal upload: create a follow-up release/tag if the final local package is used, mint a new Zenodo DOI from that manuscript-facing release, and cite it as the algorithm/data package DOI. Do not reuse the coordinate-source DOI for the full V8 benchmark package.

## Local Package Inventory

- Active package: `/Users/Apple/Developer/paper/dunhuang-heliostat-rebuild-server/paper_submission/solar_energy_elsarticle_v8_strict_review_rescue`
- Main LaTeX source: `/Users/Apple/Developer/paper/dunhuang-heliostat-rebuild-server/paper_submission/solar_energy_elsarticle_v8_strict_review_rescue/latex/main.tex`
- Active PDF: `/Users/Apple/Developer/paper/dunhuang-heliostat-rebuild-server/paper_submission/solar_energy_elsarticle_v8_strict_review_rescue/latex/main.pdf`
- Current formal inspection PDF: 40 pages, 30,834,421 bytes (about 29.4 MiB).
- Active figure assets in `latex/figures`: 33 files.
- Supplementary-data file count: 390 under `supplementary_data/`.
- Reproducibility manifest file count: 609 checked files after the 2026-06-22 journal-style cleanup and stale-preview pruning; see `reproducibility_manifest/manifest.json` for the authoritative count and checksums.
- Manifest present: `/Users/Apple/Developer/paper/dunhuang-heliostat-rebuild-server/paper_submission/solar_energy_elsarticle_v8_strict_review_rescue/reproducibility_manifest/MANIFEST.md` (yes).
- README present: `/Users/Apple/Developer/paper/dunhuang-heliostat-rebuild-server/README.md` (yes).

## Claim Boundary Guardrails

- Main-text claims should use `benchmark`, `candidate-generation workflow`, `screening queue`, and `evidence ladder` rather than `field-optimal design`, `SOTA optimizer`, or `commercial redesign`.
- SolarPILOT/PySAM checks are default-aiming layout-level checks; reduced PySolTrace checks are sampled direct-aimpoint evidence over representative conditions.
- Annual proxy results are sanity and ranking evidence over public weather years, not a dispatch model or bankable annual-yield estimate.
- The aerial photograph is author-owned field context from Zengye Su using DJI Mavic 3 Pro; it is not a quantitative measurement source.

## Immediate Submission Tasks

1. Mint a Zenodo DOI for the manuscript-facing `v0.1.2` release before final upload.
2. Add the newly minted DOI to `Data and Code Availability` and `citations/ref.bib`.
3. Keep the detailed data dictionary in supplementary files, not in the rendered journal article body.

## 2026-06-22 Repository Caution

- The main worktree is intentionally not staged wholesale because it contains many historical, generated, and unrelated files. Do not use `git add .` from the dirty working copy.
- The public GitHub repository is reachable as `poboll/dunhuang-heliostat-flux-benchmark`; `v0.1.2` is the intended journal-style cleanup release for the active package.
- The manuscript was rebuilt after `v0.1.1` to remove the rendered package-index table and improve page-level journal style. The `v0.1.2` release is intended to fix that version mismatch.
