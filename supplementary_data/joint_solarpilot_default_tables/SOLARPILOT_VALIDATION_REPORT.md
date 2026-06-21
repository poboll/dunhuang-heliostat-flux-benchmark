# Preliminary PySAM SolarPILOT Numerical Check

This run imports exported full-field layout coordinates into `PySAM.Solarpilot`.

Important limitation: `helio_positions_in` accepts x/y field coordinates through the current PySAM wrapper. Terrain-relative z coordinates and custom staggered receiver aiming are not represented in this run. Use these outputs as preliminary layout-level SolarPILOT checks, not as final high-fidelity terrain or aiming verification.

- Layouts evaluated: 8
- Weather file: `/Users/Apple/Developer/paper/dunhuang-heliostat-rebuild-server/data/weather/dunhuang_nasa_power_2023_sam.csv`
- Flux days: 8
- Flux bins: 24 x 24
- Receiver center height: 229.3 m
- Receiver diameter/height: 15.13 m / 18.60 m
- Heliostat aperture and dimensions: 115.72 m2; 11.42 m x 10.42 m

Main table: `tables/solarpilot_summary.csv`
