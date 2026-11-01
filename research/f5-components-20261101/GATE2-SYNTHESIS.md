# Gate 2 follow-up: fixed reader fails; diagnosis remains the next step

JUDGMENT: The proposed disposition is **KEEP K09, with no rescue**. B fails two separately fixed promotion rules: loss of retained SD1.5 successes in G2-A and new residual-transfer acceptances in G2-B. This follows Claude's [R3/R5 ruling](gates/GATE-2-RULING.md); it neither rejects every two-carrier reader nor demonstrates a better writer. Frozen C/J, F6 and all protected artifacts remain unchanged.

## G2-A: decoded-word evidence and a hard-binding cost

SOURCE: Rules and implementations were committed at `dde7280`, before any B EVALUATE outcome. [Plan](analysis/GATE2-TEST-PLAN.md), [reader](analysis/gate2_reader.py#L15), [results](results/g2-a/summary.json), [loss trace](results/g2-a/DIAGNOSIS.md). The exact threshold is 7.779133080172838, from alpha/2 and the 43,081,973-word radius-9 ball. B uses corrected hard distance <=6, semantic OR instance with the fixed semantic contradiction veto; no recomputed route is admitted. C OR B is separate.

MEASURED: F5 Stage-2 EVALUATE source majorities, denominator 30 per cell ([cells](results/g2-a/cells.csv), filter study=stage2-union, arm=f5-r2, split=EVALUATE, role=marked):

| Cell | C | J | Bs | Bi | B | C OR B |
|---|---:|---:|---:|---:|---:|---:|
| SD1.5 .1 |30|20|30|0|30|30|
| SD1.5 .2 |30|20|27|0|27|30|
| SD1.5 .4 |21|7|24|0|24|24|
| SDXL .1 |0|0|0|11|12|12|
| SDXL .2 |0|0|0|4|4|4|
| SDXL .4 |0|0|0|0|0|0|
| K3 .2 |3|0|6|0|6|6|

DERIVED: B is combined at the call level before the 2/3 source majority, so B need not equal the OR of the Bs/Bi source majorities. The 19/120 foreign gains pass the >=5 screen, but any low-strength C loss kills promotion. The three distinct sources 629, 790 and 1779 lose SD1.5 .2 source success in both Stage 2 and Phase A; six study/source-cells are not six independent failures. All 22 study/cells, both methods and both halves, negatives, missingness and bounds remain in the raw tables. Zero saved C0/wrong-owner events and zero new old-T4 or reference-assisted T5 events do not override this kill ([summary](results/g2-a/summary.json)).

MEASURED: The six failing Stage-2 seeds have semantic decoded scores 9.8461–12.8123, above both thresholds. Frozen soft distances 3.8177–5.5614 pass; fixed B hard corrected distances 6.1037–8.7592 fail. The instance scores are too low to rescue them, and the veto is false. The [diagnosis](results/g2-a/DIAGNOSIS.md#measured-call-mechanism) gives the exact rows.

JUDGMENT: This challenges the ruling's phrase “no change to the binding logic” for **F5**, whose frozen binding uses continuous soft features. The written G2-A rule explicitly changes that statistic and was run unchanged. These losses do not demonstrate that the lower score threshold itself causes regression. They do kill the specified B package. No soft sensitivity or threshold/radius/veto repair is selected after outcomes.

## G2-B: decoded-word checking is still insufficient

MEASURED: The fixed 8 DESIGN donors x 30 EVALUATE recipients x 2 scales yields 480/480 successful reads and 480/480 PSNR>35/SSIM>.9 cases. Counts are C=0, O=14, O_U=8, Bs=0, Bi=B=2. Existing LPIPS weights loaded locally for all 480. Sixty CPU batches lasted 50.313–63.437 seconds each, with four concurrent workers. [Summary](results/g2-b-transfer/summary.json), [donors](results/g2-b-transfer/by-donor.csv), [recipients](results/g2-b-transfer/by-recipient.csv).

| B-not-C event | Instance decoded score | Hard d / corrected | PSNR | SSIM | LPIPS |
|---|---:|---|---:|---:|---:|
| 544→1359, scale .5 |7.811984902|9 / 5.593171325|47.831397|.989417504|.013517014|
| 544→1359, scale 1 |8.894064897|8 / 5.653505340|42.346683|.963925469|.071865894|

SOURCE: Exact raw rows are [batch-0448-08.jsonl](results/g2-b-transfer/batch-0448-08.jsonl#L7), lines 7 and 8. Both have Bs=false, Bi=true, veto=false and B=true. PNGs are retained for any of the six reported acceptances; all metrics/raw calls are retained, including negatives.

JUDGMENT: **G2-B KILL.** These are two scales of one donor-recipient pair, not independent attack successes. The scale-1 decoded score also exceeds the old 8.2593 threshold, so this new failure is not confined to the old recomputed-only threshold gap. It does not establish a general attack rate or which code mismatch dominates. Metrics do not provide a human invisibility verdict; that remains MISSING.

DERIVED: Had there been zero events in 480 independent trials, the one-sided 95% upper bound would be about .622%. Neither premise holds here: there are two events, and the panel shares donors/recipients. No independent-binomial security claim is made. The fixed any-event kill requires no independence assumption.

## G2-C: q is concentrated; h is more separated on these sources

MEASURED: Clean C0 code pairs, exact counts in [summary.csv](results/g2-c/summary.csv) and all 1,770 identities in [pairs.csv](results/g2-c/pairs.csv):

| Split/code | Pairs | Mean | Minimum | <=6 | <=8 | <=9 |
|---|---:|---:|---:|---:|---:|---:|
| DESIGN q |435|10.029885|2|30|125|178|
| DESIGN h |435|16.128736|9|0|0|2|
| EVALUATE q |435|10.857471|3|28|95|143|
| EVALUATE h |435|16.022989|7|0|1|3|
| CROSS q |900|10.468889|3|67|225|337|
| CROSS h |900|16.028889|8|0|1|6|
| ALL q |1770|10.456497|2|125|445|658|
| ALL h |1770|16.051977|7|0|2|11|

DERIVED: For independent uniform 32-bit words the corresponding shares are .0002675264, .0035001833 and .0100308035. The observed EVALUATE q shares are 28/435, 95/435 and 143/435; these dependent empirical pairs strongly differ from the uniform reference. This is not an estimate of population entropy or a probability bound for an arbitrary transplant. Decoder noise, selected q routing, codeword dependence and the mismatch statistic intervene between clean-code proximity and acceptance. G2-C has no kill rule ([fixed plan](analysis/GATE2-TEST-PLAN.md)).

JUDGMENT: K01/K02 retain a semantic-specificity limitation; stable semantic codes are not interchangeable with unique image identity. h is a better-separated clean binding center **on this cohort**, not a demonstrated safe endpoint or a newly authorized descriptor. G2-B prevents converting that separation into a safety claim. K08 keeps the current h while diagnosing carrier/order effects.

## Corrected interpretation of the earlier failures

SOURCE: Claude's N3 [R2](gates/GATE-2-RULING.md#r2-reader-conclusions) identifies old `t4-residual-177015-25394-0.5`: decoded score 8.2202 fails 8.2593, recomputed 5.3190 passes 4.9820, yet the best word is 12 bits from recipient h. Same-owner tables share 32-d segments; the observed recomputed/decoded ratio .647 is close to the .625 shared-segment fraction. At scale 1 the decoded mismatch rejects. This is a recomputed-route failure, not proof that the second carrier is useless.

JUDGMENT: A cross-tier semantic-only veto cannot remove that semantic-absent event. The earlier broader claim that “no contradiction is available” was wrong: an intra-tier decoded-word disagreement was available. B checks it, but the larger panel now falsifies B's sufficiency too. No second-tier information is discarded merely because these particular unions fail.

SOURCE/MEASURED: Gate-1 values 32 and 12 for “C or second tier content-ok” on SDXL .1/.2 included the unsafe recomputed route and are withdrawn as gains. Physical second-tier found counts 52/60 and 30/60 remain descriptive evidence. Exact r3 accepts all 114 different-content F5 T5 directions (22 DESIGN, 30 EVALUATE, 62 CROSS), not only 30/30 EVALUATE; it permits a nearby candidate despite a contradictory best decoded word ([ruling R2](gates/GATE-2-RULING.md), [T2 ledger](results/LEDGER.md#t2--exact-maximization-adds-little-and-exposes-binding-failure)).

DERIVED: Conditional-q remains the primary honest-null model statement: domain-separated instance patterns are independent of the honest image/semantic-table-selected q under the PRF model. The accepted hard-distance set is contained in the radius-9 ball because 6+20e(s)<=9.3072300435<10 for s>=threshold. Union bounding gives B<=alpha and separately C OR B<=2alpha under the stated premises; it does not require independent tier events. O_Q is labelled sensitivity only. A same-owner residual transfer contains pattern signal, and a public adaptive image may depend on the patterns, so neither is covered. No empirical 1e-6 guarantee follows from development zeros ([reader proof](analysis/gate2_reader.py#L50), [assumptions](results/g2-a/DIAGNOSIS.md#derived-conditional-null-argument-and-its-limits)).

## What remains untested

JUDGMENT: No writer change, new code, optimizer, secret, registry, encoder, diffusion objective or alternative B policy was executed. Q-RES and Q-STAGE remain prospective, require the user's server decision, and cannot certify T4/T5 or human visibility. The two integrated designs retain frozen readers; B is not substituted into either. Later method comparison requires fresh disjoint development, then separately authorized confirmation. The literature floor is 32/56 journal assignments and 36/36 TOP assignments with nine accepted access-limited exhaustions, not full journal coverage ([floor ledger](literature/floor-accounting.md)).
