# Dunhuang Heliostat Flux Benchmark

Rebuild repository for the Dunhuang 100 MW heliostat-field manuscript targeted at *Solar Energy*.

This repository rejects the earlier "PySAM default layout equals optimized benchmark" story. The current manuscript treats the exported layout as an audited reference coordinate pool, then builds a transparent, plant-anchored full-field layout--aiming benchmark:

- solar-geometry marginal contribution for each heliostat;
- seasonal robustness;
- calibrated energy and capital-cost proxies using audited Layout A/B summaries;
- receiver flux-risk proxy based on angular clustering and optical contribution;
- reproducible candidate generation and representative queueing;
- PySAM/SolarPILOT default-aiming checks and reduced PySolTrace custom-aimpoint audits;
- formal paired statistics, geometry explainability, and checksum-backed reproducibility manifests.

The output is not a final plant redesign, a surveyed as-built model, or a bankable annual-yield estimate. It is a reproducible numerical benchmark and screening evidence ladder used to decide which layouts and aiming strategies deserve future full-field annual custom-aimpoint validation.

## Current Manuscript Package

- Active submission workspace: `paper_submission/solar_energy_elsarticle_v8_strict_review_rescue/`
- Main PDF: `paper_submission/solar_energy_elsarticle_v8_strict_review_rescue/latex/main.pdf`
- Main source: `paper_submission/solar_energy_elsarticle_v8_strict_review_rescue/latex/main.tex`
- Current build target: compact Elsevier `final,3p,times` inspection format.
- References: verified records are stored under the package `citations/` directory.
- Reproducibility manifest: rebuild with `scripts/build_reproducibility_manifest.py` after each manuscript/package edit.
- Core historical server run: `server_outputs/streamed_fullfield_20260511_205252/`
- Target journal: *Solar Energy* using the official Elsevier `elsarticle` template. Current XR Scholar inspection lists `Solar Energy` as Engineering `2区 Top` and JCR small-category Energy & Fuels `3区`; publisher pages should still be rechecked immediately before upload.

Latest validation layer:

- High-resolution PySAM/SolarPILOT validation for five key layouts under default aiming.
- Aiming-proxy and 24-condition proxy sensitivity.
- All-phase reduced PySolTrace strategy-union matrix, high-sample/independent-seed follow-up, V12 240k-ray selected audit, baseline-control direct audit, hold-out audit, and joint direct-promotion audit.
- Strong-baseline pressure-test and direct-gate reports that keep unpromoted strong-baseline rows in the queue rather than in the headline claims.

## Release and DOI Status

- Source coordinate archive: Zenodo/GitHub dataset `10.5281/zenodo.16957381`, used only as the coordinate-source record.
- Manuscript-facing release prepared for the final V8 package: <https://github.com/poboll/dunhuang-heliostat-flux-benchmark/releases/tag/v0.1.2>.
- The older `v0.1.1` release remains a historical archive; the `v0.1.2` package should be used if the submitted PDF, manifest, and public archive need to match.
- Final journal upload should mint a Zenodo DOI from the final GitHub release if the journal or authors require DOI-bearing archival data. Do not reuse the old coordinate-source DOI as the new algorithm/receiver-flux package DOI.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/run_rebuild_experiment.py --config configs/default.json --out outputs/run_local
```

On the paper server:

```bash
cd /home/kk/projects/paper/dunhuang-heliostat-rebuild
source .venv/bin/activate
python scripts/run_rebuild_experiment.py --config configs/default.json --out outputs/run_$(date +%Y%m%d_%H%M%S)
```

This workflow is CPU-first. GPU is only needed if a later neural surrogate is added.

## Main Outputs

- `candidate_metrics.csv`: all generated candidates.
- `pareto_front.csv`: proxy non-dominated candidates.
- `representatives.csv`: selected layouts for high-fidelity simulation.
- `layouts/*.csv`: exported representative coordinate files.
- `figures/*.png`: Pareto and layout diagnostics.
- `EXPERIMENT_REPORT.md`: reviewer-facing run report.

## Current SCI-Q2 Rebuild Route

The active manuscript route is now full-field and receiver-aiming centered:

```bash
python scripts/build_dunhuang_power_weather.py --year 2023

python scripts/run_fullfield_deformation.py \
  --config configs/server_full.json \
  --out outputs/fullfield_deformation \
  --random-candidates 760

python scripts/run_aiming_proxy.py \
  --run outputs/fullfield_deformation \
  --config configs/server_full.json \
  --layout-ids baseline_full,deform_0276,deform_0893,deform_1387,deform_1822

python scripts/run_solarpilot_validation.py \
  --run outputs/fullfield_deformation \
  --weather data/weather/dunhuang_nasa_power_2023_sam.csv \
  --layout-ids baseline_full,deform_0276,deform_0893,deform_1387,deform_1822 \
  --flux-days 8 \
  --flux-bins 24

python scripts/build_publication_summary.py \
  --run outputs/fullfield_deformation \
  --validation-dir solarpilot_validation
```

Important claim boundary: `run_solarpilot_validation.py` imports x/y coordinates through PySAM `Solarpilot`. It does not yet validate terrain-relative z coordinates or custom staggered aim points. Use it as a preliminary SolarPILOT bridge, not as the final SolTrace/SolarPILOT aiming validation.

Reduced direct-aimpoint validation is now available through:

```bash
python scripts/run_soltrace_sensitivity_matrix.py \
  --run server_outputs/streamed_fullfield_20260511_205252 \
  --config configs/server_full.json \
  --pysoltrace-dir /home/kk/projects/paper/tools/SolTrace/app/deploy/api \
  --out server_outputs/streamed_fullfield_20260511_205252/soltrace_corrected_stage_order_matrix \
  --include-proxy-union \
  --max-heliostats 6000 \
  --rays 60000 \
  --threads 8
```

The server is the preferred experiment environment. The local SAM App can be used for manual inspection, but current reproducible runs use the server's project-local Python environment and PySAM.
