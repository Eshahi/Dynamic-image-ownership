# G2-A: why F5 loses three SD1.5 .2 sources

JUDGMENT: The fixed B reader fails the no-loss rule because its hard semantic binding rejects calls that frozen F5 accepts with soft semantic binding. The semantic carrier remains readable on these calls. This is an intended difference between the two specified rules, not an observed failure of the lower score threshold. The existing promotion outcome remains **KILL**. This bounded diagnostic is not a WP6 independent review and cannot replace one.

SOURCE / SCOPE: Rule commit `dde7280`; result commit `f37ca3b`; Claude's `gates/GATE-2-RULING.md`, R5 G2-A. This note inspects existing CSVs, nine exact Stage-2 journal records and reader source. It executes no reader or experiment, loads no model or pixels, and changes no threshold, radius, veto, pair, scale or result. All CSV line numbers below include the header. Paths without a checkout prefix are relative to `research/f5-components-20261101/`.

## Measured source accounting

MEASURED: In each of Stage-2 and Phase A, the F5 EVALUATE SD1.5 .2 cell has C = 30/30 sources, Bs = B = 27/30, Bi = 0/30, and C OR B = 30/30. The corresponding call counts are C = 89/90 and B = 82/90, with one missing call retained as failure. Source success requires at least two of the three seeds (12, 13, 14). See `results/g2-a/cells.csv:187` and `:25`; the aggregation is `analysis/gate2_saved_tests.py:63-80`.

| Source | C positive seeds | B positive seeds | Stage-2 source CSV line | Phase-A source CSV line |
|---|---|---|---:|---:|
| 629 | 12, 13, 14 | 14 | 3700 | 460 |
| 790 | 12, 13, 14 | 14 | 3703 | 463 |
| 1779 | 12, 13, 14 | 12 | 3720 | 480 |

MEASURED: These are **six study/source-cells but three unique source IDs**, repeated across overlapping studies. They are not six independent failures. The recorded scores are not byte-identical between studies: for example, source 629 / seed 13 has hard distance 7 in Stage-2 and 8 in Phase A. Both reject under B. The repeated endpoint outcomes support the accounting, not an independent replication claim.

MEASURED: The seventh C-positive call lost in each study belongs to source 1332 / seed 13; that source retains two B-positive seeds and therefore remains source-positive (`calls.csv:2102,13982`; `sources.csv:3708,468`). The missing call belongs to source 72, which retains two C-positive and two B-positive calls (`sources.csv:3692,452`), so missingness does not explain the three source losses. SD1.5 .1 remains 30/30 for both C and B (`cells.csv:169,7`). These facts account for `summary.json` reporting six low-strength study/source-cell losses.

## Measured call mechanism

SOURCE: The Stage-2 raw journal is
`W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/20261025-0128-encoder-transfer-stage2b/results/stage2b-full/rows.jsonl`.
For each row below, the relevant call is `detections["f5-r2"]["qim-pilot-owner-alpha"]`; its record ID is `R0:<source>:f5-r2:0.2:<seed>`. Values are displayed rounded; saved decisions use the existing full precision.

| Source / seed | Raw journal line | Semantic score | Hard d | Hard corrected d | Frozen soft distance | Instance score | Stage-2 / Phase-A calls.csv lines |
|---|---:|---:|---:|---:|---:|---:|---|
| 629 / 12 | 10853 | 9.846143 | 8 | 6.540693 | 3.817665 | 4.627291 | 1955 / 13835 |
| 629 / 13 | 10858 | 10.914461 | 7 | 6.103662 | 4.505571 | 5.706087 | 1958 / 13838 |
| 790 / 12 | 10943 | 10.965281 | 8 | 7.228019 | 5.561427 | 2.456436 | 2009 / 13889 |
| 790 / 13 | 10948 | 11.029019 | 8 | 7.258318 | 5.289464 | 2.920172 | 2012 / 13892 |
| 1779 / 13 | 11458 | 12.369796 | 9 | 8.759229 | 5.097490 | 3.333556 | 2318 / 14198 |
| 1779 / 14 | 11463 | 12.812258 | 7 | 6.795755 | 4.841525 | 3.614809 | 2321 / 14201 |

MEASURED: Every listed call has frozen `semantic.read=true`, `semantic.content_match=true`, `binding="soft"`, C=true, Bs=false, Bi=false, B=false and veto=false. Each semantic score exceeds both frozen 8.2593268261 and B's 7.7791330802. Each hard corrected distance exceeds 6, while each saved soft distance is below 6. Every instance score is below B's threshold. Thus the semantic hard-distance comparison is the failing condition; neither the score threshold nor the veto causes these losses, and the instance tier cannot supply an acceptance. The smallest hard-distance excess is about .103662, well above the six-decimal rounding difference in the frozen channel record.

MEASURED: The surviving seed for each source has hard corrected distance below 6: source 629 / 14 = 1.411170 (raw line 10863; `calls.csv:1961,13841`), source 790 / 14 = 2.361929 in Stage-2 (`10953`; `2015,13895`), and source 1779 / 12 = 5.642885 (`11453`; `2315,14195`). Phase A gives the same pass/fail seed sets. Its failing hard corrected distances, directly in `calls.csv`, are respectively 6.539066, 7.205046, 7.231733, 7.258271, 8.758966 and 6.796022 in table order.

DERIVED FROM CODE: Frozen F5 calls `_semantic_status(..., binding="soft")` once a semantic word is readable. It fits an angle from the continuous semantic projections and expresses that angle as `theta * 32 / pi`, rather than using corrected Hamming distance. The likelihood treats disagreement near a zero projection differently from disagreement on a large projection (`scripts/f5_latent_codec.py:115-155,270-272,294-313`). B instead reads the decoded word and suspect's saved q, computes their integer Hamming distance, subtracts the decoding-error model's expected contribution, and requires the resulting distance to be at most 6 (`analysis/gate2_reader.py:19-40`). C and its soft status are explicitly retained from the saved endpoint. Lowering the score threshold therefore does not make B a superset of C: the binding statistic also changes.

JUDGMENT: These rows demonstrate a hard-versus-soft binding disagreement. They do not establish which individual continuous projection caused it, because those projections were not inspected or reconstructed. Source 1779 is especially informative: all three raw endpoints have `q_bit_errors=0`, Q=true and J=true, and all three decoded words are `8e53a459`; its suspect q nevertheless changes, reaching hard distance 9 on seed 13. Exact recovery of the embedded q therefore coexists with failure of B's comparison to the suspect's own q. One must not describe this as disappearance of the watermark or infer that all other sources' mismatches are exclusively feature drift; sources 629 and 790 also have nonzero saved q-bit errors.

## Derived conditional-null argument and its limits

DERIVED: For score s at or above B's threshold, the existing decoding-error function gives e(s) < 1/2. Corrected distance at most 6 implies

`d <= 32e(s) + 6(1 - 2e(s)) = 6 + 20e(s)`.

The fixed code's monotonicity argument bounds this by 9.3072300435 at the threshold, hence every accepted integer distance lies in the radius-9 ball. The ball contains 43,081,973 words, and `_threshold(alpha/2, ball)` is 7.7791330802 (`analysis/gate2_reader.py:50-66`; saved `summary.json.bound`). Being inside the radius-9 ball is only necessary: the effective permitted radius decreases as score rises. This explains why even distance 9 can fail despite a strong score. No new threshold computation or test was run for this note.

DERIVED, CONDITIONAL: Under the stated domain-separated PRF/random-sign model, condition on an honest null image, its carrier projections and the separately derived code centers. The semantic pattern labels `ws` and instance labels `wi` are separate domains (`scripts/revised_watermark_v5.py:343-360`); semantic feature projection has its own label (`scripts/f5_latent_codec.py:125`). For the instance tier, also condition on the semantic table and its routing decision. The selected q can depend on that image and semantic table without depending on the independent instance-pattern randomness. Its fixed h-centered acceptance ball then costs one ball union, rather than an additional enumeration of every possible q. The frozen veto can only remove instance acceptances. The random-sign tail bound plus union over the ball gives at most alpha/2 per tier, hence at most alpha = 1e-6 for B. Independence between the two acceptance events, or between different candidate codewords, is not required for this union bound. Tail normalization and scoring are in `scripts/revised_watermark_v5.py:1149-1204`; routing is in `scripts/f5_latent_codec.py:300-304`.

JUDGMENT / LIMIT: This is a conditional, single-call, fixed-owner null statement under the model. It is not an empirical population false-positive estimate, a family-wide bound across all calls or owners, or a security guarantee for a fixed public key. An adaptive attacker who sees the public patterns and chooses or optimizes an image need not satisfy the image/pattern independence premise. A same-owner transplant also contains signal from the tested pattern family; the honest unmarked null does not bound its acceptance. The Gaussian segment model used to estimate e(s) is not itself a confidence interval for the true number of decoding errors. The deterministic ball containment is useful even when that error estimate is an imperfect physical model, but all random-sign/PRF premises of the tail claim still matter. C OR B remains the separately reported union with bound at most 2 alpha under the corresponding null premises; its 30/30 here does not overturn the fixed rule that killed B.

## Measured T5 scope and diagnostic judgment

MEASURED / SOURCE: The saved `summary.json` reports zero new different-content T5 EVALUATE acceptances under the fixed comparison. `analysis/gate2_saved_tests.py:94-116` takes the marked source's saved decoded scores and words, then compares them with another image's clean C0 q/h centers. It compares B with the frozen-style hard rule at **that same reference center**, using decoded threshold 8.2593 and corrected distance at most 6. The instance score retains the source's saved q-table routing; it is not recomputed under the reference q. The reference-centered veto also uses that frozen-style hard semantic comparison. The precommitted `analysis/GATE2-TEST-PLAN.md`, G2-A, explicitly counts any new contributing tier acceptance conservatively. It is not the frozen soft C comparator.

JUDGMENT / LIMIT: T5 here is a reference-assisted, fixed-table binding diagnostic. Its added side information is the comparison image's q/h; native blind B compares with codes recomputed from the suspect itself. The T5 direction rows do not simulate a newly transplanted image, rerun its encoder/reader, or establish operational blind T5 safety. Zero new accepts means no incremental acceptance under this bounded comparison, not zero total wrong-content acceptance and not adaptive public-key security. The fixed T4 tests, collision observations and independent hostile review retain separate jobs.

JUDGMENT: No substantive implementation error was found in the bounded C-to-B loss trace. The three losses follow the written hard-primary rule; duplicate-study counting does not alter the kill because even one source loss suffices. No soft rescue, radius change, threshold change, altered veto or new variant outcome is proposed or promoted. K09's disposition and the remaining work stay governed by Claude's ruling; WP6 must independently examine the validity argument and the rule choices.
