# Reference Audit for 2025/2026 and Source Records

Generated: 2026-05-14

This audit targets the entries most likely to trigger reviewer concern: newly published 2025/2026 papers, tool webpages without DOI, and the source coordinate archive. It does not replace final manual publisher-page proofreading before submission.

## Summary

- Entries dated 2025 or later in `ref.bib`: 20.
- Verification records in `verified.jsonl`: 64.
- Most recent peer-reviewed journal entries carry DOI links; NREL/NASA/USGS tool records are intentionally treated as source records rather than journal articles.
- The coordinate-source DOI `10.5281/zenodo.16957381` resolves as the older MIT-licensed `Dunhuang_Heliostat_Benchmark_Dataset: 1.0.0`; it is not the DOI for the new 2026 algorithm package.

## Entries

| Key | Year | DOI/URL status | Verification status | Submission note |
|---|---:|---|---|---|
| `zaihu2025dunhuangdataset` | 2025 | 10.5281/zenodo.16957381 | crosscite_metadata | DOI present; final proofread title/year against DOI landing page. |
| `mitchell2025roundrobin` | 2025 | 10.1016/j.solener.2025.113785 | crossref_metadata | DOI present; final proofread title/year against DOI landing page. |
| `li2026aimingreview` | 2026 | 10.1016/j.rser.2025.116489 | crossref_metadata | DOI present; final proofread title/year against DOI landing page. |
| `carballo2025rl` | 2025 | 10.1016/j.apenergy.2024.124574 | crossref_metadata | DOI present; final proofread title/year against DOI landing page. |
| `lin2025dmcrt` | 2025 | 10.1016/j.apenergy.2025.125640 | crossref_metadata | DOI present; final proofread title/year against DOI landing page. |
| `zheng2025diffneg` | 2025 | 10.1111/cgf.70166 | crossref_metadata | DOI present; final proofread title/year against DOI landing page. |
| `alcantara2025nn` | 2025 | 10.1016/j.egyai.2025.100520 | crossref_metadata | DOI present; final proofread title/year against DOI landing page. |
| `grange2025canting` | 2025 | 10.1016/j.solener.2025.113901 | crossref_metadata | DOI present; final proofread title/year against DOI landing page. |
| `tang2025petal` | 2025 | 10.1016/j.renene.2025.122612 | crossref_metadata | DOI present; final proofread title/year against DOI landing page. |
| `biencinto2025hefesto` | 2025 | 10.1016/j.renene.2025.122736 | crossref_metadata | DOI present; final proofread title/year against DOI landing page. |
| `ghazanfari2025hefaal` | 2025 | 10.1016/j.solener.2025.113915 | crossref_metadata | DOI present; final proofread title/year against DOI landing page. |
| `liu2026fastannual` | 2026 | 10.1016/j.renene.2026.125243 | sciencedirect_metadata | DOI present; final proofread title/year against DOI landing page. |
| `adam2026heliosliders` | 2026 | 10.1016/j.solener.2026.114596 | crossref_metadata | DOI present; final proofread title/year against DOI landing page. |
| `yu2026slopedterrain` | 2026 | 10.1016/j.solener.2026.114549 | crossref_metadata | DOI present; final proofread title/year against DOI landing page. |
| `wu2026mlmpc` | 2026 | 10.1016/j.solener.2025.114258 | crossref_metadata | DOI present; final proofread title/year against DOI landing page. |
| `schiricke2025fluxprediction` | 2025 | 10.1016/j.solener.2025.113631 | crossref_metadata | DOI present; final proofread title/year against DOI landing page. |
| `li2026windslope` | 2026 | 10.1016/j.solener.2025.114186 | crossref_metadata | DOI present; final proofread title/year against DOI landing page. |
| `freeman2025tiltroll` | 2025 | 10.3390/en18020426 | crossref_metadata | DOI present; final proofread title/year against DOI landing page. |
| `nrel2025solarpilotdocs` | 2025 | https://www.nrel.gov/csp/solarpilot | manual_source_record | No DOI in BibTeX; source/tool webpage, keep as manual source record. |
| `nrel2025pysam` | 2025 | https://nrel-pysam.readthedocs.io/ | manual_source_record | No DOI in BibTeX; source/tool webpage, keep as manual source record. |

## Coordinate-Source Record

- `zaihu2025dunhuangdataset`: DOI `10.5281/zenodo.16957381`, verified through DOI metadata on 2026-05-14.
- Manuscript use: source coordinate archive only. The paper discloses that the audited baseline retains 11,915 non-origin records and does not claim this package is an official as-built survey.
- Required before submission: create a separate 2026 versioned archive for the new algorithm/data/code package and replace `[DOI/URL for the 2026 release-candidate archive]` in the manuscript.
