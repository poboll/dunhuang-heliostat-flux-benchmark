# Streamed Full-Field Run Update

Date: 2026-05-11

## What changed in the current streamed-run draft

- Added a memory-efficient streamed candidate search in `scripts/run_fullfield_deformation.py`.
- Ran a new server experiment with 1,841 full-field candidates.
- Checked five key layouts with high-resolution PySAM/SolarPILOT settings (`flux-days=8`, `flux-bins=24`).
- Replaced old hard-coded figure panels with dynamic panels for the new candidate set.
- Rebuilt the Elsevier manuscript PDF with the new trade-off interpretation.
- Added component-ablation evidence and quick SolarPILOT ablation checks.
- Added weather/DNI anchoring against the reported Dunhuang corrected TMY annual DNI.
- Added aiming-proxy sensitivity across 81 grouping, spot-width, and staggered-phase assumptions.
- Added the all-phase stage-order-corrected reduced PySolTrace matrix: five layouts, 27 solar conditions, 11 aiming strategies, and 1,485 layout--strategy--condition cases.
- Regenerated the reproducibility manifest with SHA-256 checksums.
- Rewrote manuscript wording to remove internal rejection/journal-positioning language.

## Current key result

The stronger search did not remove the core trade-off. It sharpened it:

- `deform_0276`: +3.15% SolarPILOT mean optical efficiency, but +4.69% default peak/active-mean flux.
- `deform_0893`: +0.24% SolarPILOT mean optical efficiency and -6.22% nominal aiming-proxy peak/mean concentration.
- `deform_1822`: +0.51% SolarPILOT mean optical efficiency and +0.91% default peak/active-mean flux.
- `deform_1387`: strongest aiming-proxy sensitivity median improvement (-1.94%) and strongest all-phase mean direct peak-to-active-mean reduction (-2.98%) under S9-p1, but higher default SolarPILOT flux penalty.
- `deform_1822`: best all-phase direct median reduction under S9-p0 (-8.62%) and a conservative default-flux role, but not a universal winner.

The manuscript keeps the conservative claim boundary: this is a full-field layout and receiver-flux benchmark with a custom-aimpoint numerical-checking queue, not a final optimized Dunhuang plant design.

## Main deliverables

- `latex/main.tex`
- `latex/main.pdf`
- `output/LATEX_BUILD_REPORT.md`
- `latex/figures/fig_journal_tradeoff_clean.png`
- `latex/figures/fig_journal_layout_realism_panel.png`
- `latex/figures/fig_journal_flux_peak_panel.png`
- `latex/figures/aiming_flux_deform_0893.png`
- `latex/figures/aiming_sensitivity_boxplot.png`
- `latex/figures/fig_soltrace_allphase_direct_panel.png`
- `server_outputs/streamed_fullfield_20260511_205252/deformation_ablation/`
- `server_outputs/streamed_fullfield_20260511_205252/aiming_sensitivity_deep_20260512/`
- `server_outputs/streamed_fullfield_20260511_205252/soltrace_allphase_27cond_20260512/`
- `server_outputs/streamed_fullfield_20260511_205252/weather_dni_sensitivity/`
- `server_outputs/streamed_fullfield_20260511_205252/reproducibility_manifest/`
