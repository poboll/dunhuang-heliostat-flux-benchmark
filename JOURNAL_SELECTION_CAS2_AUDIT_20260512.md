# SCI-Q2 / CAS-Q2 Journal Selection Audit

Updated: 2026-05-12

## Decision

The primary target should remain **Solar Energy**.

Reason: the manuscript is now an algorithmic solar-tower layout and receiver-flux benchmark. Solar Energy is the best topical match among SCI/CAS-Q2-type options because it regularly publishes heliostat-field layout, SolarPILOT, receiver-flux, aiming, terrain, and ray-tracing studies. It also uses the standard Elsevier `elsarticle` workflow already applied in this package.

## Evidence used

- Direct partition check: the LetPub/New-Ranking search page returned `Solar Energy` with ISSN `0038-092X`, New-Ranking partition `2区`, large category `工程技术`, small category `能源与燃料`, and SCI/SCIE indexing signal. This matches the user's `xr-scholar`/New-Ranking target logic.
  URL checked: https://www.letpub.com.cn/index.php?page=journalapp&view=search&searchname=Solar%20Energy
- Official journal scope: Elsevier Shop describes Solar Energy as the official journal of the International Solar Energy Society, devoted to solar-energy applications, and welcoming original studies on solar-energy research, development, application, measurement, or policy.
  URL: https://shop.elsevier.com/journals/solar-energy/0038-092X
- Official LaTeX route: Elsevier instructs LaTeX authors to use the `elsarticle` package and journal article template package.
  URL: https://www.elsevier.com/researcher/author/policies-and-guidelines/latex-instructions
- Direct automated access to `https://www.xr-scholar.com/Journals/Search` returned a Cloudflare challenge in this environment. The companion WebAPI landing page was reachable, but it did not expose a public unauthenticated journal-search API. Therefore the automated evidence is recorded from the accessible LetPub/New-Ranking search page plus official Elsevier pages. Before final submission, the author should still manually confirm the latest `xr-scholar` entry in a normal browser session.
- Partition wording should stay outside the manuscript. It is a submission-planning fact, not a scientific claim.

## Candidate comparison

| Candidate journal | Fit to manuscript | Template | Index/partition signal | Risk judgement |
| --- | --- | --- | --- | --- |
| Solar Energy | Best fit: CSP, heliostat fields, SolarPILOT, receiver flux, aiming, benchmark numerical checks | Elsevier `elsarticle`; current package already uses it | LetPub/New-Ranking search reports `2区`, `工程技术`, `能源与燃料`, SCI/SCIE | Primary target. Bar is real, but story is aligned. |
| Thermal Science and Engineering Progress | Possible if the paper is reframed toward receiver thermal/flux risk rather than layout algorithm | Elsevier `elsarticle` | Reported JCR Q1/Q2 depending category; CAS large-category signals vary by source and year | Not first target unless a receiver thermal constraint model is added. |
| Results in Engineering | Pragmatic broad engineering fallback | Elsevier `elsarticle` | Often listed as ESCI/JCR Q1 engineering; CAS signals vary | Easier fit but may not satisfy a strict SCI-only requirement if ESCI is not accepted locally. |
| Renewable Energy | Strong renewable-energy fit but likely higher bar | Elsevier `elsarticle` | High-impact/Q1-type signal in many indexes | Better after stronger annual custom-aimpoint and techno-economic checks. |
| Applied Energy / Energy Conversion and Management | Excellent energy-systems fit but much higher novelty/verification bar | Elsevier `elsarticle` | High-impact Q1-type journals | Not recommended for the current verification level. |

## Template decision

Use the official Elsevier template:

```tex
\documentclass[final,3p,times]{elsarticle}
\journal{Solar Energy}
\bibliographystyle{elsarticle-num}
```

The active PDF is a compact journal-style inspection build, not a loose review-copy build. If the editorial system requests line numbers, produce a separate review version with `preprint,review,12pt` and `lineno`; do not use that review version to judge the final visual quality.

## Reviewer-level positioning

The manuscript should be submitted as:

> A reproducible, plant-anchored full-field heliostat-layout candidate-generation algorithm and receiver-flux numerical-checking benchmark for the Dunhuang 100 MW solar tower.

It should not be submitted as:

> A final optimized redesign of the operating Dunhuang plant.

This distinction is essential. Current evidence supports a SCI-Q2 attempt if the claims remain conservative. The largest remaining scientific weakness is still the absence of full-field annual custom-aimpoint verification with receiver thermal constraints.

## Current go/no-go judgement

**Go for Solar Energy after one more QA pass**, provided the title, abstract, cover letter, and discussion keep the conservative benchmark framing. The draft is now much more coherent than a Scientific Data-style descriptor because it has an algorithm, a plant-scale audit, a numerical-checking funnel, negative/mixed evidence, and a reproducibility package.

**Do not submit as-is if the authors want to claim an optimized Dunhuang redesign.** That claim would require full-field annual custom-aimpoint verification, a receiver thermal constraint model, better terrain/civil constraints, and a stronger techno-economic layer.
