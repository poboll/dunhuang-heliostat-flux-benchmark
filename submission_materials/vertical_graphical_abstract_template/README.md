# Vertical Graphical Abstract Template

This folder is the editable source for the vertical graphical abstract used in
`submission_materials/graphical_abstract.png` and
`submission_materials/graphical_abstract.pdf`.

It is not a pasted screenshot. The builder redraws the poster-style abstract
from the author aerial photograph, configuration text, and validation CSV
tables.

## Files

- `config.json`: title, authors, affiliation, data paths, summary numbers, and output paths.
- `build_vertical_graphical_abstract.py`: deterministic template renderer.

## Build

From the package root:

```bash
python submission_materials/vertical_graphical_abstract_template/build_vertical_graphical_abstract.py
```

Or from any directory after changing to the package root:

```bash
cd /path/to/dunhuang-heliostat-flux-benchmark
python submission_materials/vertical_graphical_abstract_template/build_vertical_graphical_abstract.py
```

The current template outputs a vertical 2:3 image at `2048 x 3072 px`, plus a
single-page PDF. The old horizontal graphical abstract is archived under
`submission_materials/archive/graphical_abstract_horizontal_replaced_20260611/`.

## Edit Safely

For routine edits, change `config.json` first. The most likely edits are:

- `title`
- `authors`
- `affiliation`
- `audit_summary`
- `scope`
- `data_sources`

The renderer keeps the claim boundary deliberately conservative: it presents a
reproducible full-field algorithm and receiver-flux checking queue, not a final
commercial optimization of Dunhuang.
