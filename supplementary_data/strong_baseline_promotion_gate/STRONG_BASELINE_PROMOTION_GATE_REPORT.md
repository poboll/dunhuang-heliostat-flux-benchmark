# Strong-Baseline Promotion Gate

This report is a conservative writeback gate for the prepared strong-baseline direct-promotion queue.
It merges annual-proxy, interpolation, 36-bin SolarPILOT default-flux, 12-flux-day sampling, aiming-proxy,
geometry, and already completed reduced-direct evidence. It does not claim that the queued strong-baseline
rows have been direct-promoted; rows without completed direct confidence intervals remain queue-only.

## Gate Decision

- Overall recommendation: `write_supplementary_gate_and_short_boundary_sentence_only`.
- Newly promoted strong-baseline rows: `[]`.
- Queue-only strong-baseline rows: `['sb_hy_energy', 'sb_hs_flux', 'sb_pf_flux']`.
- Server direct matrix status: `not_completed_ssh_auth_failed_this_turn`.

## Promotion Table

| Role | Layout | Tier | Annual mean delta (%) | 36-bin peak delta (%) | 12-day peak delta (%) | Aiming proxy delta (%) | Direct CI | Gate status | Writeback |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| L_nom | deform_0893 | core | +0.25 | +1.60 | +1.40 | -6.22 | -3.41 [-6.48, -0.35] | direct_supported_annual_positive_boundary | may_write_as_existing_direct_supported_role |
| L_rob | deform_1387 | core | +0.74 | +2.23 | +2.38 | -5.34 | -3.61 [-6.17, -0.97] | direct_supported_annual_positive_boundary | may_write_as_existing_direct_supported_role |
| J_bal | joint_g02_0333 | core | +0.97 | +1.83 | +1.78 | -8.16 | -1.98 [-6.53, +2.93] | directional_direct_only | write_directional_or_keep_secondary |
| B_hy,E | sb_hy_energy | core | +1.85 | +2.07 | +1.65 | -4.44 | n/a | screening_only_annual_positive_needs_direct | do_not_headline_keep_in_direct_promotion_queue |
| J_flux | joint_g04_0478 | core | -0.74 | +0.87 | +1.01 | -7.94 | -4.06 [-6.99, -0.93] | direct_supported_receiver_boundary | may_write_as_existing_direct_supported_role |
| B_hs,R | sb_hs_flux | core | -0.84 | -0.19 | -0.18 | -6.67 | n/a | screening_only_receiver_pressure_needs_direct | do_not_headline_keep_in_direct_promotion_queue |
| B_pf,R | sb_pf_flux | core | -0.86 | -0.45 | -0.54 | -5.45 | n/a | screening_only_receiver_pressure_needs_direct | do_not_headline_keep_in_direct_promotion_queue |
| L0 | baseline_full | core | n/a | +0.00 | +0.00 | +0.00 | n/a | paired_baseline | reference_only |
| C_rad+ | ctrl_radial_expand_015 | core | -0.94 | n/a | n/a | +0.10 | -2.43 [-6.61, +1.70] | directional_direct_only | write_directional_or_keep_secondary |
| L_opt | deform_0276 | extended | +3.36 | +5.00 | +4.69 | -5.48 | -1.20 [-5.80, +3.65] | directional_direct_only | write_directional_or_keep_secondary |
| J_gain | joint_g02_0303 | extended | n/a | n/a | n/a | n/a | n/a | control_or_context_only | secondary_context_only |

## Interpretation

- Existing direct-supported rows can still be discussed as direct-supported role boundaries, not final engineering winners.
- `B_hy,E` remains the strongest annual-positive strong-baseline screening row, but it has no completed same-run direct CI.
- `B_pf,R` and `B_hs,R` remain receiver-pressure screening rows: they reduce aiming proxy and are stable in the default-flux gates, but they are not annual optical headline rows.
- `L_opt` remains an optical stress case because its annual optical signal persists while default-flux and hotspot penalties persist.
- The next real scientific upgrade remains the same-run reduced direct promotion matrix or a true same-aimpoint cross-code/custom-aiming check.

## Direct-Supported Rows Already Available

| Role | Layout | Tier | Annual mean delta (%) | 36-bin peak delta (%) | 12-day peak delta (%) | Aiming proxy delta (%) | Direct CI | Gate status | Writeback |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| L_nom | deform_0893 | core | +0.25 | +1.60 | +1.40 | -6.22 | -3.41 [-6.48, -0.35] | direct_supported_annual_positive_boundary | may_write_as_existing_direct_supported_role |
| L_rob | deform_1387 | core | +0.74 | +2.23 | +2.38 | -5.34 | -3.61 [-6.17, -0.97] | direct_supported_annual_positive_boundary | may_write_as_existing_direct_supported_role |
| J_flux | joint_g04_0478 | core | -0.74 | +0.87 | +1.01 | -7.94 | -4.06 [-6.99, -0.93] | direct_supported_receiver_boundary | may_write_as_existing_direct_supported_role |

## Queue-Only Rows

| Role | Layout | Tier | Annual mean delta (%) | 36-bin peak delta (%) | 12-day peak delta (%) | Aiming proxy delta (%) | Direct CI | Gate status | Writeback |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B_hy,E | sb_hy_energy | core | +1.85 | +2.07 | +1.65 | -4.44 | n/a | screening_only_annual_positive_needs_direct | do_not_headline_keep_in_direct_promotion_queue |
| B_hs,R | sb_hs_flux | core | -0.84 | -0.19 | -0.18 | -6.67 | n/a | screening_only_receiver_pressure_needs_direct | do_not_headline_keep_in_direct_promotion_queue |
| B_pf,R | sb_pf_flux | core | -0.86 | -0.45 | -0.54 | -5.45 | n/a | screening_only_receiver_pressure_needs_direct | do_not_headline_keep_in_direct_promotion_queue |
