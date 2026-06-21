# Formal Paired Statistics Audit

This report treats each reduced direct matrix as a paired condition-level experiment. 
For each selected layout--strategy row, the paired sample is the condition-level 
change in peak-to-active-mean receiver concentration relative to the same baseline 
under the same day, hour, and aiming strategy.

- Bootstrap replicates for mean confidence intervals: 10,000
- Practical indistinguishability threshold: +/-1.0 percentage point
- Sign and Wilcoxon tests use the one-sided alternative that the paired change is lower than zero.
- The audit formalizes uncertainty for the existing reduced matrices; it is not a new full-field annual run.

## Key Rows

| Matrix | View | Candidate | Strategy | Mean % | 95% CI % | HL % | Lower frac. | Wilcoxon p | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| V12 240k reduced direct | best-direct | $L_{nom}$ | S9-p1 | -3.408 | [-6.48, -0.35] | -2.774 | 0.556 | 0.089 | CI-supported reduction |
| V12 240k reduced direct | best-direct | $L_{ctrl}$ | S9-p1 | -2.132 | [-5.46, +1.46] | -2.978 | 0.741 | 0.053 | directional practical reduction |
| V12 240k reduced direct | best-direct | $L_{opt}$ | S9-p2 | -0.386 | [-3.70, +3.13] | -0.441 | 0.704 | 0.097 | engineering-indistinguishable/uncertain |
| V12 240k reduced direct | best-direct | $L_{rob}$ | S9-p1 | -0.037 | [-2.96, +3.27] | -0.200 | 0.630 | 0.281 | engineering-indistinguishable/uncertain |
| baseline-control direct | best-direct | $L_{rob}$ | S9-p2 | -3.605 | [-6.17, -0.97] | -4.492 | 0.593 | 0.035 | CI-supported reduction |
| baseline-control direct | best-direct | $L_{nom}$ | S9-p0 | -3.491 | [-7.15, +0.09] | -4.056 | 0.519 | 0.151 | weak directional reduction |
| baseline-control direct | best-direct | $C_{rad+}$ | visible | -2.434 | [-6.61, +1.70] | -3.026 | 0.556 | 0.214 | weak directional reduction |
| baseline-control direct | best-direct | $C_{wave}$ | five-point | -2.303 | [-5.80, +1.20] | -2.749 | 0.556 | 0.214 | weak directional reduction |
| baseline-control direct | best-direct | $C_{rad-}$ | S9-p5 | -1.443 | [-5.03, +2.15] | -0.555 | 0.667 | 0.124 | directional practical reduction |
| baseline-control direct | best-direct | $L_{opt}$ | five-point | -1.197 | [-5.80, +3.65] | -0.634 | 0.741 | 0.124 | directional practical reduction |
| baseline-control direct | best-direct | $L_{ctrl}$ | five-point | -0.878 | [-4.47, +2.71] | -0.022 | 0.444 | 0.495 | engineering-indistinguishable/uncertain |
| joint direct promotion | best-direct | $J_{flux}$ | S9-p5 | -4.063 | [-6.99, -0.93] | -4.643 | 0.741 | 0.006 | CI-supported reduction |
| joint direct promotion | best-direct | $J_{gain}$ | S9-p2 | -2.495 | [-6.57, +1.99] | -4.333 | 0.630 | 0.119 | weak directional reduction |
| joint direct promotion | best-direct | $J_{bal}$ | S9-p2 | -1.982 | [-6.59, +2.98] | -4.451 | 0.704 | 0.053 | directional practical reduction |
| joint direct promotion | proxy-selected | $J_{flux}$ | S9-p5 | -4.063 | [-6.99, -0.92] | -4.643 | 0.741 | 0.006 | CI-supported reduction |
| joint direct promotion | proxy-selected | $J_{bal}$ | S9-p2 | -1.982 | [-6.53, +2.93] | -4.451 | 0.704 | 0.053 | directional practical reduction |
| joint direct promotion | proxy-selected | $J_{gain}$ | S9-p3 | 2.576 | [-1.54, +6.67] | 1.884 | 0.481 | 0.907 | not supported or adverse |

## CI-Supported Rows

| Matrix | View | Candidate | Strategy | Mean % | 95% CI % | HL % | Lower frac. | Wilcoxon p | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| baseline-control direct | best-direct | $L_{rob}$ | S9-p2 | -3.605 | [-6.17, -0.97] | -4.492 | 0.593 | 0.035 | CI-supported reduction |
| joint direct promotion | best-direct | $J_{flux}$ | S9-p5 | -4.063 | [-6.99, -0.93] | -4.643 | 0.741 | 0.006 | CI-supported reduction |
| joint direct promotion | proxy-selected | $J_{flux}$ | S9-p5 | -4.063 | [-6.99, -0.92] | -4.643 | 0.741 | 0.006 | CI-supported reduction |
| V12 240k reduced direct | best-direct | $L_{nom}$ | S9-p1 | -3.408 | [-6.48, -0.35] | -2.774 | 0.556 | 0.089 | CI-supported reduction |

## Practical-Threshold Rows

No selected row has its 95% bootstrap mean confidence interval entirely below the -1% practical threshold. The evidence is therefore best written as screening-level promotion rather than final engineering superiority.

## Interpretation

- The formal statistics support the manuscript's conservative wording: role-level promotion is stronger than a single best-row claim.
- Rows whose confidence intervals cross zero should remain directional or hypothesis-generating, even when their mean change is negative.
- `J_flux` and `L_rob` are the clearest receiver-risk rows in the current direct evidence; `J_bal`, `J_gain`, and several V12 rows remain strategy- or sample-sensitive.
- The +/-1% threshold is intentionally conservative: reductions smaller than this band should be treated as engineering-indistinguishable in the absence of plant-grade thermal validation.
