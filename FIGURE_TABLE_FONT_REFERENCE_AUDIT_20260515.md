# Figure, Table, Font, Reference, and Claim Audit

Date: 2026-05-15

Active package: `solar_energy_elsarticle_v7_balanced_full_submission`

## 1. Figure 1 and Geographic Locator

- The active Figure 1 source photograph is `/Users/Apple/Downloads/官方主题/175354060700-675.webp`.
- The original WebP is copied byte-for-byte to `latex/figures/fig1_author_aerial_original.webp`.
- The LaTeX-compatible PNG `latex/figures/fig1_author_aerial_fullframe.png` is a pixel-identical, no-resampling conversion of the original WebP: 4000 by 2224 pixels, same decoded RGB pixels, no crop, annotation, colour adjustment, or geometric edit.
- The caption and main text identify the photograph as a real aerial photograph of the Dunhuang heliostat field taken by co-author Zengye Su using a DJI Mavic 3 Pro drone. It is used as qualitative context only.
- The locator panel is a GEO/China-wide projected map using a Lambert-style conic projection tuned for China. It replaces the earlier longitude/latitude direct plot to avoid visual compression, keeps the complete China extent visible, highlights Gansu, and marks Dunhuang near 94.426 E and 40.063 N.
- The coordinate audit panel remains separate from the photograph and map, so the figure no longer mixes visual context with numerical evidence in one crowded collage.
- Panel (c) now uses compact role labels below the plot (`baseline`, `Lopt`, `Lnom`, `Lrob`, `Lctrl`) rather than a text block inside the coordinate panel.

## 2. Figure 2 Workflow

- Figure 2 is now native LaTeX/TikZ rather than a raster flowchart.
- The revised structure uses two visual lanes: `layout-generation evidence` and `receiver-check evidence`.
- Nodes are numbered, use white fills, light rules, and restrained blue/orange/purple accents.
- The feedback arrow is retained because it is scientifically important: direct PySolTrace checks can reorder the proxy-selected candidate queue.
- This keeps the method story compact while avoiding the heavy-box, poster-like flowchart style.

## 3. Fulfilled / Merge-Ordered / Blue Layout Diagnostics

- No active manuscript occurrence of `Fulfilled` or `Merge-Ordered` was found.
- The likely user-referenced blue/orange images are archived diagnostics, for example:
  - `server_outputs/server_20260511_142712/figures/representative_layout_slots.png`
  - `/Users/Apple/Downloads/官方主题/Figure_2_Layout_Comparison.png`
- These are not used in the active v7 manuscript.
- The central circular blank region in those figures is the tower/receiver exclusion zone, not missing heliostats.
- The large sector or annular holes in the old slot/deletion diagnostics are precisely why those layouts were rejected or superseded. The active v7 design preserves 11,915 heliostats and uses the full-field surround/ellipse-like layout.
- The old blue figure is useful only as a historical diagnostic of why mirror-deletion comparisons are unsafe for this paper. It should not be promoted to a main manuscript figure.

## 4. Longtable / Three-Line Table Handling

- Long tables use `longtable` with `\endfirsthead` and `\endhead`.
- Page rendering confirms repeated headers and continued captions:
  - Table G.23 `Detailed data dictionary` starts on page 29 and continues on page 30 with the table title and column headers repeated.
  - Table I.24 `Completed and future verification tables` starts on page 30 and continues on page 31 with the table title and column headers repeated.
- Table captions are kept above the table, following Elsevier/engineering-journal convention. Internal mini-titles inside table bodies are avoided unless they carry real grouping information.

## 5. Font Policy

- The manuscript uses `\documentclass[final,3p,times]{elsarticle}`, so the body text is in the Elsevier Times-style 3p layout.
- Active Matplotlib figures use `font.family=serif` with `Times New Roman`, `Times`, and `DejaVu Serif` fallback.
- Active TikZ diagrams inherit `\rmfamily` from the manuscript.
- No `PingFang` occurrence is present in `latex/main.tex`.
- The practical rule is: Times-style serif for body, captions, TikZ, and scientific figures; embedded figure text uses normal weight by default. Bold is reserved for LaTeX figure/table labels and journal caption styling rather than arbitrary in-figure annotations.
- Elsevier artwork guidance emphasizes uniformity across figures and legible lettering. Elsevier's artwork sizing guidance gives a rule of thumb of 7 pt finished normal text and no smaller than 6 pt for subscript/superscript characters. Source: https://www.elsevier.com/about/policies-and-standards/author/artwork-and-media-instructions/artwork-sizing
- Elsevier also recommends EPS/PDF/TIFF/JPEG for electronic artwork, with EPS preferred for vector graphics and JPEG accepted for photographs. Source: https://www.elsevier.com/about/policies-and-standards/author/artwork-and-media-instructions/artwork-overview

## 6. Solar Energy Fit and Manuscript Claim Boundary

- The target journal remains `Solar Energy`. Its guide for authors states that regular papers should give in-depth treatment and clearly articulate state of knowledge, knowledge gaps, and original contributions; it also warns against purely local application studies and incremental work. Source: https://www.sciencedirect.com/journal/solar-energy/publish/guide-for-authors
- The active paper should therefore be framed as a reproducible full-field layout-deformation and receiver-flux screening benchmark, not as a Dunhuang-only resource note and not as a certified commercial redesign.
- Current status is not SOTA as a final heliostat-field optimizer because it lacks full-field annual custom-aimpoint verification and cross-code validation.
- Current status is defensible as a complete system-oriented numerical benchmark paper because it contains: coordinate audit, full-field deformation, feasibility gates, SolarPILOT default-aiming checks, proxy aiming sensitivity, reduced PySolTrace V8--V11 checks, manifest, and explicit claim boundaries.
- The next scientific strengthening step is not more cosmetic plotting. It is full-field or statistically enlarged custom-aimpoint verification, cross-code comparison, and public release with DOI/GitHub/Zenodo.

## 7. Reference Audit

- `citations/ref.bib` contains 64 entries.
- `citations/verified.jsonl` contains 64 traceability records.
- `latex/main.tex` cites 60 unique keys.
- Missing citation keys in BibTeX: none.
- Uncited but verified reserve entries: `alcantara2024nn`, `itoiz2024clustering`, `mellado2024comparison`, `watkins2020arbitrary`.
- URL/DOI reachability check on 2026-05-15:
  - 54 records returned HTTP 200.
  - 9 records returned HTTP 403 from publisher/DOI landing pages, consistent with access blocking rather than immediate evidence of fabricated citations.
  - 1 record returned HTTP 405 from a DOI landing page method restriction.
- Metadata recheck for all 10 non-200 DOI landing pages succeeded through Crossref or DataCite metadata APIs; titles were recovered for all 10 records and written to `citations/reference_metadata_recheck_failed_dois_20260515.jsonl`.
- Non-200 landing pages still worth manually opening before final submission:
  - `hamilton2022copilot`
  - `zheng2025diffneg`
  - `belhomme2014ant`
  - `zhu2024swarm`
  - `zhu2023mpc`
  - `watkins2020arbitrary`
  - `chen2020shapes`
  - `derbal2023noblocking`
  - `freeman2025tiltroll`
  - `usgs2015srtm`
- No evidence was found in this pass that the active cited reference list contains fabricated keys. The 403/405 items are metadata-confirmed but should still be manually opened before final submission because publisher anti-bot responses prevent full automated page verification.
