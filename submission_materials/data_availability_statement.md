# Data Availability Statement

The release-candidate submission package contains the data and scripts needed to audit the manuscript's evidence ladder: layout CSV files, public weather and terrain inputs, deformation-candidate tables, joint layout--aiming screening tables, PySAM/SolarPILOT numerical-checking tables, reduced PySolTrace custom-aimpoint outputs, same-condition and same-anchor baseline checks, coordinate-provenance sensitivity tables, formal paired-statistics tables, journal figures, and SHA-256 reproducibility manifests. Review-facing CSV copies are organized under `supplementary_data/`; the active checksum manifest is included as `reproducibility_manifest/manifest.json` and `reproducibility_manifest/MANIFEST.md`.

The supplementary tables are grouped by evidence role rather than by manuscript page: candidate generation and geometry audit, SolarPILOT default-aiming bridge, receiver-risk proxy and AFD-style hotspot-area audit, reduced direct-ray promotion matrices, joint layout--aiming screening, strong-baseline pressure tests, annualized optical sanity checks, and formal statistics. The full file-level dictionary is supplied through the manifest instead of being repeated in the article body.

The source coordinate pool is derived from the MIT-licensed Zenodo/GitHub archive `10.5281/zenodo.16957381`, after audit and removal of the origin placeholder. That DOI is used only as the coordinate-source citation for the older dataset package. The new layout-algorithm and receiver-flux screening package is publicly available as a versioned GitHub release:

https://github.com/poboll/dunhuang-heliostat-flux-benchmark/releases/tag/v0.1.6

The v0.1.6 release candidate is the manuscript-facing package after the Figure 1 cleanup, journal-target reassessment, benchmark-wording guardrail, and DOI-metadata consistency pass. A machine-readable Zenodo metadata file is included as `.zenodo.json`, and `submission_materials/zenodo_doi_runbook_v016.md` lists the required release-to-DOI steps. Until the new DOI is issued, the GitHub release is the public versioned package record and the older Zenodo DOI remains only the source-coordinate citation.

The package supports rerunning and auditing the numerical benchmark. It does not include plant SCADA, survey-grade terrain, plant-grade TMY files, calibrated receiver tube-temperature limits, or commercial retrofit data.
