# Fast Annual Proxy and Public Plant Sanity Check

## Scope

This audit is a conservative annualization bridge, not full-field annual custom-aimpoint validation. It interpolates each SolarPILOT optical-efficiency table over the 8760-hour NASA POWER 2023 weather file, weights daylight hours by DNI, uniformly scales DNI to the public Dunhuang corrected-TMY annual DNI, and uses the reported public annual generation only as a plant-scale sanity anchor.

## Weather and Plant-Scale Anchors

- NASA POWER 2023 annual DNI: 1842.4 kWh m^-2 y^-1.
- Public corrected-TMY annual DNI: 1883.0 kWh m^-2 y^-1.
- Uniform DNI scale factor: 1.0220.
- Public annual-generation reference used for sanity checking: 351,600 MWh y^-1.
- Baseline annual thermal proxy after DNI scaling: 945,884 MWh_th y^-1.
- Calibrated net electric conversion factor needed to match the public design-generation reference: 0.372.
- The public design generation corresponds to a 40.14% capacity factor for a 100 MW plant.

## Ranking Signal

Top rows by the reported-TMY-scaled thermal proxy:

| Layout | Annual thermal proxy (MWh_th/y) | Change vs baseline (%) | Calibrated electric proxy (GWh_e/y) |
| --- | ---: | ---: | ---: |
| `deform_0276` | 977,708 | +3.36 | 363.4 |
| `sb_hy_energy` | 963,390 | +1.85 | 358.1 |
| `sb_ta_energy` | 956,344 | +1.11 | 355.5 |
| `joint_g02_0333` | 955,081 | +0.97 | 355.0 |
| `deform_1387` | 952,902 | +0.74 | 354.2 |
| `sb_pf_energy` | 952,476 | +0.70 | 354.1 |

## Interpretation

- The audit links representative SolarPILOT optical tables to the full public-weather year, so it is stronger than a single design-point comparison.
- It still uses SolarPILOT default aiming and interpolated optical-efficiency tables, not custom annual ray tracing.
- The public-generation sanity check shows that the baseline annual proxy is in the right plant-scale order after a plausible net electric conversion calibration.
- Percentage changes from this table may be cited as annual-proxy ranking evidence, but not as bankable annual generation or final plant redesign evidence.
