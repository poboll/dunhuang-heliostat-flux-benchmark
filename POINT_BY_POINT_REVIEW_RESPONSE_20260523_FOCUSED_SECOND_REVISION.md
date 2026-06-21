# Point-by-Point Response: Focused Second Revision

Date: 2026-05-23

Review source: `/Users/Apple/Developer/Pycharm/q/定日镜场修改请按点核对.md`

## Summary Judgment

The review is largely correct. The manuscript has become a credible benchmark/workflow paper, but the previous v8 draft still had three high-risk gaps for a Solar Energy submission: dispersed reproducibility parameters, insufficiently formal paired statistics, and an over-optimistic impression that the current SolarPILOT/PySolTrace evidence might equal true cross-code validation. This revision focuses on those hard risks and avoids deleting the evidence chain.

## Point-by-Point Actions

| Review issue | Decision | Action taken |
|---|---|---|
| Paper-alone reproducibility is still incomplete | Accepted | Expanded `reproducibility_config/PARAMETER_REGISTRY.md` and the main-text registry table with local coordinate frame, origin-filter rule, OpenTopoData SRTM90m grid/API, interpolation and slope method, deterministic/random candidate design, hard gates, 27 direct solar conditions, PySAM version, PySolTrace backend path, seed policy, and local package versions. |
| Missing formal paired statistics | Accepted | Added `scripts/build_formal_paired_statistics.py` and copied it to `code/scripts/`. Generated `supplementary_data/formal_paired_statistics/` with bootstrap CI, Hodges--Lehmann shifts, one-sided sign tests, one-sided Wilcoxon tests, and a +/-1% practical-indistinguishability threshold. Added Table `tab:formal-paired` and Figure `fig:formal-paired` to the manuscript. |
| Need effect/equivalence policy | Accepted with conservative wording | Used Hodges--Lehmann shift and Cohen-style paired standardized shift in CSV; main text reports HL and Wilcoxon, while the +/-1% practical band is used as an equivalence/practical-indistinguishability policy. Since no row clears CI entirely below -1%, the manuscript keeps screening-queue wording. |
| Cross-code check still future | Accepted, but clarified current status | Main text now calls the current SolarPILOT default-aiming bridge + PySolTrace reduced direct gate a cross-engine evidence ladder, not true same-aimpoint cross-code validation. Appendix Stage 5 now defines the minimum future queue and matched settings for SolarPILOT/CoPylot, SolTrace, and Solstice. |
| Main text is too long | Accepted, but not solved by deletion in this pass | Added `SUBMISSION_MAIN_SI_TRANSFER_PLAN_20260523.md`. It preserves the 48-page full-evidence draft as the master version and maps which figures/tables can move to SI in a future shortened package. No silent pruning was performed. |
| Fig. 1 / Fig. 8--11 efficiency concerns | Partly deferred | Current pass prioritizes reproducibility and statistics. The SI transfer plan identifies which figure families can move or compress. No new figure pruning was done because the user previously rejected losing evidence-chain material. |
| DOI/Zenodo remains required | Accepted as blocking item | Manuscript continues to list the GitHub v0.1.0 release and explicitly states that a Zenodo DOI should be minted before final journal submission if required. No fake DOI was inserted. |
| Benchmark/workflow positioning, not final optimizer | Accepted and strengthened | Abstract, discussion, conclusion, and formal-statistics section now emphasize role-level promotion, receiver-boundary candidates, and direct promotion queue. No SOTA/commercial redesign claim is made. |

## New Evidence Boundary

The formal paired-statistics audit supports:

- `J_flux` as the clearest joint receiver-boundary row: mean -4.06%, 95% CI [-6.99, -0.93]%, HL -4.64%, Wilcoxon p=0.006.
- `L_rob` as the clearest baseline-control direct TS-FPDA row: mean -3.61%, 95% CI [-6.17, -0.97]%, HL -4.49%, Wilcoxon p=0.035.
- V12 `L_nom` as a high-ray follow-up candidate: mean -3.41%, 95% CI [-6.48, -0.35]%, HL -2.77%, Wilcoxon p=0.089.

It also downgrades:

- `J_bal` to directional balance evidence because CI crosses zero.
- `J_gain` proxy-selected S9-p3 to adverse/strategy-sensitive evidence.
- `L_ctrl` to directional rather than confirmed evidence at V12.

No selected row clears the stricter criterion that the full 95% CI lies below the -1% practical threshold, so the correct claim remains a screening queue and promotion workflow, not final engineering superiority.

## Files Added Or Modified

- Added: `scripts/build_formal_paired_statistics.py`
- Added: `paper_submission/solar_energy_elsarticle_v8_strict_review_rescue/code/scripts/build_formal_paired_statistics.py`
- Added: `paper_submission/solar_energy_elsarticle_v8_strict_review_rescue/supplementary_data/formal_paired_statistics/`
- Added: `paper_submission/solar_energy_elsarticle_v8_strict_review_rescue/latex/figures/fig_formal_paired_statistics.png`
- Added: `paper_submission/solar_energy_elsarticle_v8_strict_review_rescue/SUBMISSION_MAIN_SI_TRANSFER_PLAN_20260523.md`
- Modified: `paper_submission/solar_energy_elsarticle_v8_strict_review_rescue/latex/main.tex`
- Modified: `paper_submission/solar_energy_elsarticle_v8_strict_review_rescue/reproducibility_config/PARAMETER_REGISTRY.md`
- Modified: `paper_submission/solar_energy_elsarticle_v8_strict_review_rescue/reproducibility_config/README.md`

## Remaining Blockers

- Zenodo DOI still needs to be minted from the GitHub release or another archival repository.
- A true same-aimpoint cross-code matrix remains future work.
- A shortened main+SI submission package should be generated only after the authors approve the transfer plan.
