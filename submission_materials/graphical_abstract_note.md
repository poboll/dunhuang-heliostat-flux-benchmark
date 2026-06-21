# Graphical Abstract Note

Elsevier guidance encourages an original image that summarizes the take-home message and is displayed online with the article. Elsevier's current graphical-abstract guidance recommends a minimum 1328 x 531 px image at 300 dpi: https://www.elsevier.com/researcher/author/tools-and-resources/graphical-abstract

The current graphical abstract is a vertical poster-style template generated at `2048 x 3072 px`, so it clears the minimum size requirement. It is not a pasted raster-only image: the editable source lives in `vertical_graphical_abstract_template/`.

Current graphical abstract structure for this paper:

1. Top: author-captured Dunhuang aerial photograph as the visual anchor for the surround-field benchmark.
2. Middle: plant-anchor audit and a compact evidence-chain workflow from coordinate audit to direct PySolTrace re-ranking.
3. Lower middle: three evidence bands plus representative validation snapshots showing SolarPILOT optical gain, SolarPILOT default receiver-flux penalty, and high-sample reduced SolTrace receiver-risk reduction in the shared blue/orange/purple style.
4. Bottom: benchmark scale and validation scope, followed by the conservative claim boundary.

Build route:

```bash
python submission_materials/vertical_graphical_abstract_template/build_vertical_graphical_abstract.py
```

Routine edits should be made in `vertical_graphical_abstract_template/config.json`, then rebuilt with the command above.

The graphical abstract should not say "optimized plant" or "best layout". Its message should be: reproducible full-field layout generation plus flux-risk numerical checking reveals tool-dependent candidate roles.

The included draft follows that boundary by using the author-captured aerial context, a concise auditable workflow, and the disagreement among SolarPILOT optical efficiency, SolarPILOT default receiver-flux concentration, and high-sample reduced SolTrace tests. The photograph is used as qualitative context only and should not be described as a measured performance or coordinate source.
