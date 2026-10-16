# E3-S1 M2 post-hoc sensitivity to the clean exact-H gate

This is a **post-hoc sensitivity analysis**, requested in the October 14 brief. It changes neither the frozen primary endpoint nor the reviewed [M2 report](e3-s1-m2-results.md). It reads only retained endpoint dictionaries, without executing a detector, opening source images, accessing new held-out data or changing retained outputs. The original study and all its failures remain intact.

## Declared input and reproducible procedure

Input: MAIN `.thesis-build/analysis/e3-s1-local-r3-20261013/run-r3/metrics/endpoints.json`, frozen analysis version `e3-s1-analysis-v1`. The reproduction script is [e3_s1_m2_sensitivity.py](../../scripts/e3_s1_m2_sensitivity.py). It uses `methods[m].clean_coverage.per_source` and `methods[m].t3[s].raw_read_results` only. It checks 300 unique paired sources, exactly seeds 3/4/5 per source per method/strength, explicit availability and boolean endpoints for available calls. Missing source/seed rows, duplicated observations or malformed endpoints cause an error rather than exclusion. Explicitly unavailable calls follow the original frozen rule: they are not successes and remain in the planned denominator.

The saved predicates are the outputs of frozen `m1b_e3_s1_analysis.predicates()`: S is semantic found and content match; J is exact checked semantic q and content match. The script does not redefine detector thresholds. Majority means at least two of the three seeds. Every comparison retains the same denominator of 300 sources; the analysis unit is a paired source cluster, not 900 independent seed calls.

The original clean gate is admitted AND strict quality AND exact Q AND exact H AND F. The sensitivity removes **only exact H**, retaining admitted, strict quality, exact Q and clean F. These gates are applied separately to each method's native clean results. The ungated S and J rows remove the clean gate entirely. None equalizes native h construction, quality, coding or detector operating points.

Of 900 planned calls per method/strength, E3 has 16 unavailable calls at .1 and 12 at .2; v5 has six and four. The observed majority counts do not repair, impute or drop them. An initial validation attempt rejected these unavailable calls; the corrected reproduction explicitly preserves the frozen non-success convention and reports missingness.

To reproduce from the journal worktree in PowerShell:

```powershell
& 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/venv/Scripts/python.exe' `
  scripts/e3_s1_m2_sensitivity.py `
  'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/analysis/e3-s1-local-r3-20261013/run-r3/metrics/endpoints.json'
```

The JSON output records the input SHA-256, script SHA-256 and checkout commit. `--output` writes to a new path exclusively and refuses to overwrite an existing file.

Successful reproduction used committed code `da4de38c913131388e7230adaa571b95b2a8a8e9`, input SHA-256 `95f228c4d56f4c1089a44462a51eca3dfe5e8a010ff466ac72972af45eead80b`, and script SHA-256 `7c5445fca2423fb54b7cf3f64ee1a4547e3eac6edf06f13ae9a01d27c9044819`. Runtime was approximately 0.25 s, CPU only, USD 0. All original primary counts and discordances reproduced exactly.

## Paired results

All counts below are source-majority successes out of 300. Discordance is E3-only / v5-only. The p values are exact one-sided paired sign/McNemar tests under an exchangeable discordant-source null with probability 1/2. They describe this post-hoc sensitivity; they are not replacement confirmatory tests or a new prospectively controlled test family. The retained original primary analysis has its own multiplicity treatment.

| Endpoint | Strength | E3-S1 | v5 r3 | E3 minus v5, pp | Discordance | One-sided exact p |
|---|---|---:|---:|---:|---:|---:|
| Reported primary: original clean gate AND majority S | .1 | 281 | 151 | +43.33 | 136 / 6 | 1.91846e-33 |
| Reported primary: original clean gate AND majority S | .2 | 278 | 129 | +49.67 | 156 / 7 | 4.76379e-38 |
| Clean gate without exact H AND majority S | .1 | 281 | 278 | +1.00 | 18 / 15 | .364 |
| Clean gate without exact H AND majority S | .2 | 278 | 229 | +16.33 | 64 / 15 | 1.15e-8 |
| Majority S, no clean gate | .1 | 287 | 283 | +1.33 | 15 / 11 | .279 |
| Majority S, no clean gate | .2 | 284 | 232 | +17.33 | 63 / 11 | 2.66e-10 |
| Majority J, no clean gate | .1 | 287 | 80 | +69.00 | 211 / 4 | 1.67548e-57 |
| Majority J, no clean gate | .2 | 284 | 17 | +89.00 | 267 / 0 | 4.21688e-81 |

The v5 clean exact-H predicate fails on 138/300 sources, with 134 sources failing H while passing all other original clean-gate components. Its clean F nevertheless passes on 299/300. Thus native `both_match` and exact evaluator-target h recovery are distinct requirements. The original clean gate admits E3 294/300 versus v5 159/300; removing exact H admits E3 294/300 versus v5 293/300. This substantially changes eligibility rather than changing attacked-image detection.

## Interpretation and claim limits

At .1, the original +43.33 pp composite difference falls to +1.00 pp under the H-free gate and +1.33 pp for ungated S. **A .1 semantic-survival advantage is not established by these analyses.** The nonsignificant paired tests do not establish equivalence: no equivalence margin or prospective equivalence test was specified. The October 14 brief's word “equivalent” is therefore interpreted as lack of an established survival advantage, not a statistical equivalence conclusion.

At .2, the observed semantic-survival gain persists without exact-H eligibility: +16.33 pp with the other clean requirements retained and +17.33 pp without a clean gate. The large exact checked-payload J differences also persist at both strengths. These are defensible, endpoint-specific observations on the pinned SD1.5 DDIM20 channel used by the E3 writer. They do not establish unseen-model transfer, equal-quality superiority, calibrated low false-positive rates, a causal contribution of refinement, or general ownership security.

Full ownership acceptance after regeneration remains absent in the original M2 results; this addendum changes no F result. Detectors in this retained analysis receive the suspect image and public claimed owner/model configuration, without the clean reference or a registry. Evaluator-target q/h are used to score exact recovery, not supplied to the detector. The separately authorized registry method introduces additional side information and requires its own evidence.
