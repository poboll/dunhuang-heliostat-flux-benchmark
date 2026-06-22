# Journal Target and Template

## Primary target

Solar Energy is the most scientifically aligned venue because the manuscript is centered on solar tower field layout, SolarPILOT numerical checks, receiver flux, and aiming strategy. It is not the easiest route, but it is the cleanest audience match. The Elsevier/ScienceDirect journal page describes Solar Energy as the official journal of the International Solar Energy Society and as devoted to the science and technology of solar-energy applications. The same page currently reports journal-level signals including CiteScore 12.6, Impact Factor 6.6, and a CSP/heliostat special-issue trail, which supports topical fit for a heliostat-field benchmark paper: https://www.sciencedirect.com/journal/solar-energy

The target also satisfies the user's SCI/CAS-Q2-style constraint at the planning level. The accessible LetPub/New-Ranking search page lists `Solar Energy` with ISSN `0038-092X`, New-Ranking partition `2区`, large category `工程技术`, small category `能源与燃料`, and SCI/SCIE indexing signal: https://www.letpub.com.cn/index.php?page=journalapp&view=search&searchname=Solar%20Energy. A 2026-06-21 XR Scholar browser check confirmed the 2026 entry `j-mjpnp982`: SCIE/Scopus, publisher `PERGAMON-ELSEVIER SCIENCE LTD`, Engineering/工程技术 `2区 Top`, and JCR `ENERGY & FUELS` `3区`.

The paper should not be resubmitted as a data descriptor. The strongest current story is algorithmic and benchmark-oriented: full-field layout generation under plant-scale constraints, receiver-flux-aware screening, SolarPILOT default-aiming numerical checks, and an all-phase reduced SolTrace direct-aimpoint matrix.

## Fallback targets

1. Solar Energy: primary target and best topical fit. The bar is meaningful because recent Solar Energy/Applied Energy/Renewable Energy work already includes petal layouts, terrain optimization, differentiable ray tracing, neural aiming surrogates, and receiver-flux verification/control studies.
2. Renewable Energy: possible if the next revision strengthens annual/custom-aimpoint numerical checking and emphasizes layout--aiming co-design.
3. Results in Engineering or Energy Reports: more pragmatic fallbacks if the paper is positioned as a reproducible engineering workflow and benchmark rather than as a high-novelty optimizer.
4. Applied Energy or Energy Conversion and Management: not recommended for the current draft unless a substantially stronger annual techno-economic and receiver-thermal verification layer is added.

## Template

The workspace uses the Elsevier `elsarticle` LaTeX class installed in TeX Live:

- `/usr/local/texlive/2024/texmf-dist/tex/latex/elsarticle/elsarticle.cls`
- `/usr/local/texlive/2024/texmf-dist/doc/latex/elsarticle/elsarticle-template-num.tex`

The current inspection PDF uses the official Elsevier `elsarticle` class:

```tex
\documentclass[final,3p,times]{elsarticle}
```

This is a tighter Elsevier journal-style layout and removes the previous double spacing and line numbers. The choice follows Elsevier's `elsarticle` guidance that the article class is part of the standard Elsevier template package and supports final-style options such as `3p`, `5p`, and `times`: https://www.elsevier.com/researcher/author/policies-and-guidelines/latex-instructions

The compact inspection PDF is currently 46 pages and is compiled with `pdflatex+bibtex`, matching Elsevier's common `elsarticle` workflow. This does not mean the content is a technical report; the detailed data dictionary and extended roadmap are suppressed from the rendered article and kept in the supplementary package. A separate review-copy build can be produced later if the submission system requests line numbers or a looser format.

Artwork follows Elsevier's artwork guidance: use uniform lettering, recommended fonts such as Arial/Helvetica/Times, and keep figure text readable at final size. The current active figure set therefore uses a white page background, Arial/Helvetica-first sans-serif text in the graphics, and colorblind-safe accents. Relevant guideline: https://www.elsevier.com/about/policies-and-standards/author/artwork-and-media-instructions/artwork-overview

If the editorial system requests a line-numbered review file, create a separate review copy with `preprint,review,12pt`, `lineno`, and line numbers. Do not use that loose review copy as the visual-quality draft for internal checking.

## Manual pre-submission checks

Before upload, perform three final administrative checks in a normal browser session:

1. Reconfirm the current `Solar Energy` entry on `xr-scholar.com/Journals/Search` if the submission date is no longer close to the 2026-06-21 browser check.
2. Open the Elsevier submission page from the journal site and confirm whether the system requests a compact source build, a line-numbered review PDF, or both.
3. Confirm artwork limits and graphical-abstract pixel requirements at the time of submission.

## Current reviewer-risk judgement

The manuscript is no longer in the rejected Scientific Data shape. It now has a defensible algorithmic story, but the claim must remain conservative. The best SCI-Q2 route is to submit only after the figures, implementation traceability, and all-phase reduced SolTrace matrix are clear, and after the cover letter states that this is a reproducible benchmark and numerical-checking queue rather than a final Dunhuang redesign.

Remaining risk:

- Novelty risk: petal/layout deformation is not enough by itself; the paper must emphasize plant anchoring, full-field preservation, terrain audit, receiver-flux disagreement, and reproducibility.
- Numerical-check risk: reduced SolTrace is useful but not annual full-field custom aiming. Recent 2025-2026 literature now includes deformable petal layout, uneven-terrain layout tooling, sloped-terrain spatiotemporal layout optimization, differentiable ray tracing, differentiable rasterization, and commercial-scale ray-tracing round-robin comparisons, so overclaiming would be easy for reviewers to attack.
- Engineering realism risk: SRTM90m and NASA POWER are reproducible public inputs, not survey-grade plant inputs.
- Presentation risk: active manuscript figures must stay white-background, common-font, and non-compressed.

Checked: 2026-06-21.
