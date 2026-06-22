# Submission Repository and DOI Status

Updated: 2026-06-22 CST, v0.1.9 metadata/status correction pass

## Current Target

- Target journal: *Solar Energy* using the Elsevier `elsarticle` class (`final,3p,times`).
- Manuscript framing: plant-anchored, receiver-flux-aware, reproducible layout--aiming benchmark and screening evidence ladder.
- No new experiments are required for this status pass; the report records packaging and claim-boundary readiness.
- Current PDF identity after the metadata/status correction pass: 40 pages, 30,907,906 bytes, SHA-256 `4b5aaa74d4e37bf755e25fc2f10cf44f67edf5e0f228456f722373b855852a89`.

## Repository / Release

- Manuscript-facing GitHub release recorded in the current manuscript: <https://github.com/poboll/dunhuang-heliostat-flux-benchmark/releases/tag/v0.1.9>.
- Previous verified public release: <https://github.com/poboll/dunhuang-heliostat-flux-benchmark/releases/tag/v0.1.8>.
- Previous `v0.1.7` release title: `fix: 发布v0.1.7图文润色投稿包`.
- Previous `v0.1.7` target commit: `d15f9ae3f1436227583414f57ec199621ad02c57`.
- Previous `v0.1.7` archive: `solar_energy_elsarticle_v8_strict_review_rescue_20260622_v017.zip`, SHA-256 `9ee1eba84e36552035d73fa00817871aa7c074d644f99f5067277ff235dc3bf8`.
- Source coordinate DOI already cited in the manuscript: `10.5281/zenodo.16957381` as the coordinate-source record only.
- Current clean package status: `v0.1.9` is a metadata and submission-status correction over `v0.1.7`. It does not add experiments or broaden claims; it removes pre-release wording from the archival metadata and points the manuscript Data/Code Availability to the DOI-deposition release.
- Zenodo metadata draft: `.zenodo.json` has been prepared at the package root with `v0.1.9` metadata and the `v0.1.9` GitHub release URL. Add the minted DOI after Zenodo deposition.
- DOI runbook: `submission_materials/zenodo_doi_runbook_v019.md`. Superseded `v016/v017` Zenodo metadata and DOI-runbook files were removed from the active package to avoid stale DOI instructions.
- Required before final DOI-bearing journal upload: publish and verify GitHub `v0.1.9`, mint a new Zenodo DOI from that release, and cite it as the algorithm/data package DOI. Do not reuse the coordinate-source DOI for the full V8 benchmark package.

## Local Package Inventory

- Active clean release package: `/Users/Apple/Developer/paper/dunhuang-heliostat-flux-benchmark-release`
- Main LaTeX source: `/Users/Apple/Developer/paper/dunhuang-heliostat-flux-benchmark-release/latex/main.tex`
- Active PDF: `/Users/Apple/Developer/paper/dunhuang-heliostat-flux-benchmark-release/latex/main.pdf`
- Current formal inspection PDF: 40 pages. The exact byte size and SHA-256 are recorded in `output/LATEX_BUILD_REPORT.md` after each compile.
- Active figure assets in `latex/figures`: 33 files.
- Supplementary-data file count: 390 under `supplementary_data/`.
- Reproducibility manifest file count: see `reproducibility_manifest/manifest.json` for the authoritative count and checksums after the `v0.1.9` manifest refresh.
- DOI metadata in manifest: the checksum manifest should include `.zenodo.json`, `submission_materials/zenodo_metadata_v019.json`, and `submission_materials/zenodo_doi_runbook_v019.md`.
- Manifest present: `/Users/Apple/Developer/paper/dunhuang-heliostat-flux-benchmark-release/reproducibility_manifest/MANIFEST.md` (yes).
- README present: `/Users/Apple/Developer/paper/dunhuang-heliostat-flux-benchmark-release/README.md` (yes).

## Claim Boundary Guardrails

- Main-text claims should use `benchmark`, `candidate-generation workflow`, `screening queue`, and `evidence ladder` rather than `field-optimal design`, `SOTA optimizer`, or `commercial redesign`.
- SolarPILOT/PySAM checks are default-aiming layout-level checks; reduced PySolTrace checks are sampled direct-aimpoint evidence over representative conditions.
- Annual proxy results are sanity and ranking evidence over public weather years, not a dispatch model or bankable annual-yield estimate.
- The aerial photograph is author-owned field context from Zengye Su using DJI Mavic 3 Pro; it is not a quantitative measurement source.

## Immediate Submission Tasks

1. Publish and verify a clean GitHub `v0.1.9` release for the current PDF before final DOI-bearing upload.
2. Mint a Zenodo DOI from the verified `v0.1.9` release.
3. Add the newly minted DOI to `Data and Code Availability`, `citations/ref.bib`, `.zenodo.json`, and the standalone data-availability statement.
4. Keep the detailed data dictionary in supplementary files, not in the rendered journal article body.

## 2026-06-22 Repository Caution

- The main worktree is intentionally not staged wholesale because it contains many historical, generated, and unrelated files. Do not use `git add .` from the dirty working copy.
- The public GitHub repository is reachable as `poboll/dunhuang-heliostat-flux-benchmark`; `v0.1.8` is the previous verified public release, and `v0.1.9` is the current clean release target until the status-cleanup release is published and verified.
- The manuscript was rebuilt after `v0.1.1` to remove the rendered package-index table and improve page-level journal style. The verified `v0.1.7` release carries the Figure 1/Figure 2 polish and version consistency; the `v0.1.9` correction keeps that scientific content while making the archival metadata Zenodo-ready.
- The 2026-06-22 wording pass keeps the article framed as a benchmark and direct-promotion queue, keeps detailed file dictionaries in the manifest rather than in the article body, and requires DOI deposition from the release that exactly matches the submitted PDF.
