# Zenodo DOI Runbook for the V8 Solar Energy Package

Status: GitHub release `v0.1.8` is the intended DOI-deposition source after the metadata/status correction pass.

## What this file is for

The manuscript cites the coordinate-source DOI `10.5281/zenodo.16957381` and the manuscript-facing GitHub release `v0.1.8`. The next required external archival step is to mint a new Zenodo DOI from the verified `v0.1.8` release. This release does not add experiments relative to `v0.1.7`; it removes pre-release wording from the archival metadata and keeps the DOI package aligned with the final author-review manuscript.

## Required order

1. Build and verify the final PDF and manifest.
2. Confirm the clean GitHub release `v0.1.8` is available from the final package.
3. Update `.zenodo.json`:
   - confirm `version` is `v0.1.8`;
   - confirm the GitHub `related_identifiers` URL points to release `v0.1.8`;
   - keep `10.5281/zenodo.16957381` only as `isDerivedFrom`.
4. Upload the release archive to Zenodo or use GitHub-Zenodo integration.
5. Copy the newly minted DOI into:
   - `latex/main.tex`, Data and Code Availability;
   - `citations/ref.bib` as the manuscript package dataset/software record;
   - `submission_materials/data_availability_statement.md`;
   - `output/SUBMISSION_REPOSITORY_DOI_STATUS.md`;
   - `/Users/Apple/Developer/Pycharm/q/定日镜场修改请按点核对.md`.

## Boundary text to keep

Do not describe the Zenodo record as an operating-plant survey, a certified Dunhuang redesign, a receiver thermal-safety record, or a bankable annual-yield dataset. It is a reproducible numerical benchmark package and direct-promotion queue for future layout-aiming co-design studies.

## Current source-coordinate DOI

`10.5281/zenodo.16957381` remains the coordinate-source archive DOI only. It must not be reused as the DOI for the full V8 benchmark package.
