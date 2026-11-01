# K01 — Semantic descriptor

JUDGMENT — PROPOSED WP1 dossier, not a ruling. Scope: structure, prior evidence and conditional ceilings only. No WP2 literature result or WP3–WP5 improvement verdict is implied. Source: [BRIEF](../BRIEF.md), WP1.

## A. Structure

- SOURCE — Inputs are suspect/source RGB8 and the pinned CLIP ViT-B/32 model plus preprocessing. Each view produces a checked, finite, nonzero 512-dimensional unit vector. F5 averages full image, horizontal mirror, four corner crops, and center crop, then renormalizes (`scripts/three_threat_models.py:150-160`; `scripts/f5_gate.py:35-54`). The crop side is `round(width*7/8)`, so the code assumes the canonical square input, rather than independently defining a fractional height.
- SOURCE — The descriptor is computed from original source pixels at embedding and from saved suspect pixels at standalone detection. Embed-report self-verification is different: it receives the supplied original feature vector (`scripts/encoder_transfer_runtime.py:158-165,173-179`; `scripts/f5_latent_codec.py:254`). DERIVED — An embedded verification report is not evidence that CLIP re-extraction from the final mark succeeded.
- DERIVED — Cost is seven CLIP forward passes per image, shared across owner calls in the transfer adapter, with zero direct pixel distortion. Individual CLIP-view latency was not identified; low-level detector `seconds` excludes these passes (`scripts/encoder_transfer_runtime.py:173-183`; `scripts/f5_latent_codec.py:276,327`). It is one averaged descriptor, not seven tests and not a best-view search.
- JUDGMENT — Keep K1 distinct from K2, but name preprocessing/canonicalization as part of K1. Changing its model, views, or preprocessing changes q and the soft statistic; a reader-only change can therefore also change recomputed presence and instance-table selection. Its causal recovery ceiling is UNKNOWN. A content-decision-only oracle with frozen scores is bounded by existing reads; replacing E and rewriting is not bounded by that oracle.

SOURCE: Full interface/null context is in [code structure](../context/wp1-code-structure.md); paths and line locators above refer to inspected repository code. Historical write time 119 s/mark and detector-row time about 1.5 s are environment-specific anchors, not CPU or isolated component timings (BRIEF.md WP5). No new model timing was run.

## B. Prior evidence

SOURCE: The table carries the relevant inspected earlier experiments into this component. Each E-link resolves to the detailed source/report line locators, full numbers, study units and limitations in [prior evidence](../context/wp1-prior-evidence.md). Historical branch blobs were read with git show. SOURCE denotes an inspected report; no historical count below is a new measurement. Frozen held-out reports are contextual only, never a tuning pool.

| Evidence | Reported result (SOURCE) | What it rules out and leaves open (JUDGMENT, PROPOSED) |
|---|---|---|
| [E02: F5 r1 to r2](../context/wp1-prior-evidence.md#e02-f5-r1r2-binding-was-a-major-real-bottleneck-and-was-successfully-improved) (inventory line 42) | Paired .2 improved 25/28 to 28/28 and .4 improved 21/28 to 23/28 using soft ML plus seven views; r1 .2/.4 had 5/9 binding failures and 0 carrier failures under its older endpoint. | Binding was repairable; older recomputed-inclusive counts are not today's frozen C. No foreign-family guarantee. |
| [E05: H4 threshold kill](../context/wp1-prior-evidence.md#e05-h4-threshold-relaxation-local-rescues-cost-natural-image-specificity) (inventory line 87) | Soft/hard .4=49/58 vs 42/58; radius6/7/8/10 admitted4/10/21/62 of132 ordered semantic cross-source pairs. Radius7 rescued4/6 .4 binding failures. | Equal-specificity relaxation failed. Semantic proximity is not measured joint T5 attribution; other calibrated rules remain open. |
| [E06: Noiseless binding/sketch diagnostic](../context/wp1-prior-evidence.md#e06-noiseless-semantic-binding-ceilings-informative-but-conditional) (inventory line 95) | At4/132 false-pair budget, true feature .4/.5/.6=55/44/14 versus production 49/37/10; random256-bit ranges54–55/44–48/12–15 on173 saved identities. | Shows representation/sketch headroom conditional on transport and finite operating point; not a realizable watermark or universal upper bound. |
| [E10: E3 and unseen transfer](../context/wp1-prior-evidence.md#e10-e3-real-codingobjective-gains-costly-writing-and-endpoint-sensitive-comparisons) (inventory line 150) | Fresh development E3/F5 SD2.1 .2 C24/24 each retained F5 under selector; .4 C/J22/22 vs 12/4; median write130.133 vs 52.4685s, LPIPS .03926 vs.01443. Frozen E3 M2 also documented separately. | Coding/objective package can improve exact semantic J, but BCH, distortion, initialization and eligibility confound attribution. Closed E3 micro-variants remain closed. |
| [E11: Descriptor/reissue round](../context/wp1-prior-evidence.md#e11-descriptorreissue-round-stability-and-specificity-are-separate-from-transport) (inventory line 170) | Perfect old-h transport oracle .2=6/18 (one source majority); CD1/BI1/FG128 .2 oracle 18/18,10/18,17/18 but sibling/impostor failures differed. Reissue MSE2.95–6.40→10.34–14.62. | Transport does not fix old-h instability. Fixed protocols failed, not all instance information; no closed descriptor-line reopening authorized. |
| [E12: Registry with trusted records](../context/wp1-prior-evidence.md#e12-registry-additional-side-information-helps-a-different-task-with-hard-near-negative-limits) (inventory line 190) | Fresh 40-source F_R .2 SD1.5/SD2.1=30/40,32/40 below 36/40; fingerprint-only accepted4/13 near-duplicate pairs, registry 0/13 on unmarked no-pointer pairs. Later frozen held-out near-lookalikes 3/45 accepted. | Additional side information changes task; negative result not rescued by earlier screening or dependent millions of unrelated comparisons. |

### Current saved-development accounting and per-cell ceilings

DERIVED: The restricted oracle changes only the content verdict on already decoded words. Its C ceiling is existing read-majorities and its J ceiling is existing exact-Q majorities. It is a diagnostic for one narrow role of this component, not a bound on a new descriptor, code, or rewritten watermark. A literal accept-all oracle would sacrifice T4/T5.

DERIVED: All ceilings are source-level potential increments relative to frozen C/J, not sums of per-call failures. Shared ceilings must not be added across components. Missing calls remain failures in baseline C/J. Every unconstrained new design and every joint strict-quality/T4/T5-safe recovery ceiling is UNKNOWN; current scores contain no new-method negatives or human visual verdict. Protocol: [accounting specification](../analysis/WP1-ACCOUNTING-SPEC.md); endpoint source: scripts/m1b_e3_s1_analysis.py:70–84.

| Study/cell | C /60 | J /60 | Restricted C ceiling (gain) | Restricted J ceiling (gain) | Missing-C upper | Trivial C gain cap |
|---|---:|---:|---|---|---:|---:|
| phase-a / R0-0.1 | 60 | 41 | 60 (+0) | 41 (+0) | 60 | 0 |
| phase-a / R0-0.2 | 57 | 38 | 59 (+2) | 39 (+1) | 58 | 3 |
| phase-a / R0-0.4 | 39 | 14 | 47 (+8) | 15 (+1) | 40 | 21 |
| phase-a / R1-0.1 | 0 | 0 | 1 (+1) | 0 (+0) | 0 | 60 |
| phase-a / R1-0.2 | 0 | 0 | 0 (+0) | 0 (+0) | 0 | 60 |
| phase-a / R1-0.4 | 0 | 0 | 0 (+0) | 0 (+0) | 0 | 60 |
| phase-a / ctrlB-codec | 60 | 47 | 60 (+0) | 47 (+0) | 60 | 0 |
| stage2-union / D1 | 55 | 31 | 55 (+0) | 31 (+0) | 55 | 5 |
| stage2-union / D3 | 55 | 35 | 55 (+0) | 35 (+0) | 55 | 5 |
| stage2-union / R0-0.1 | 60 | 41 | 60 (+0) | 41 (+0) | 60 | 0 |
| stage2-union / R0-0.2 | 57 | 38 | 58 (+1) | 38 (+0) | 58 | 3 |
| stage2-union / R0-0.4 | 39 | 14 | 47 (+8) | 16 (+2) | 40 | 21 |
| stage2-union / R1-0.1 | 0 | 0 | 1 (+1) | 0 (+0) | 0 | 60 |
| stage2-union / R1-0.2 | 0 | 0 | 0 (+0) | 0 (+0) | 0 | 60 |
| stage2-union / R1-0.4 | 0 | 0 | 0 (+0) | 0 (+0) | 0 | 60 |
| stage2-union / R1-mode-0.2 | 0 | 0 | 0 (+0) | 0 (+0) | 0 | 60 |
| stage2-union / R1-rinse-0.1 | 0 | 0 | 0 (+0) | 0 (+0) | 0 | 60 |
| stage2-union / R1-smooth-0.2 | 0 | 0 | 0 (+0) | 0 (+0) | 0 | 60 |
| stage2-union / R3-0.2 | 5 | 0 | 7 (+2) | 0 (+0) | 5 | 55 |
| stage2-union / X1 | 60 | 46 | 60 (+0) | 46 (+0) | 60 | 0 |
| stage2-union / X2 | 60 | 41 | 60 (+0) | 41 (+0) | 60 | 0 |
| stage2-union / clean | 60 | 52 | 60 (+0) | 52 (+0) | 60 | 0 |

MEASURED/DERIVED: Table inputs are [loss cells](../results/wp1-accounting/loss-cells.csv) and [fragile/semantic endpoint cells](../results/wp1-fragile/fragile-cells.csv), with row-level locators in [component ceilings](../results/component-ceilings.csv) filtered to K01. There are 22 F5 study/cell rows and 22 matched v5 rows in the full accounting; studies are not pooled. Frozen C/J are unchanged. C/J are semantic endpoints; J never means fragile recovery.

SOURCE/JUDGMENT: The Phase-A pilot/law/mechanism records and inactive attack grids have no complete eligible frozen-C/J detector panel from which to infer this component's recovery; their ceilings are UNKNOWN, not zero. Coverage is explicit in [Phase-A coverage](../results/wp1-accounting/phase-a-coverage.csv). Historical smaller development panels above retain their own endpoints/denominators; no per-component source ceiling is reconstructed from report-only totals. Morphology is not a detector panel. No held-out ceiling or tuning table is created.

### Ranking and next literature work

JUDGMENT — PROPOSED: See the [joint loss/cost ranking](../WP1-SYNTHESIS.md#ranking-by-conditional-loss-opportunity-and-cost-to-change) for this component's role and interactions. Changes to this component cannot be credited with a count improvement until the necessary intervention and safety checks exist. The [K01 WP2 query plan](../literature/WP2-QUERY-PLAN.md) lists 15 exact planned queries across five indexes; none has been executed or counted as literature evidence in WP1. Gate 1 precedes that work.
## C. Literature since 2024
SOURCE: [K01 intake](../literature/intake/K01.md),4 Q1J +3 TOP,54 exact/42 substantive queries and four successful scholarly surfaces; one journal slot explicitly exhausted. Holistic CLIP evaluation shows training/objective/resolution dependence. CLIP Surgery preserves the original global branch, so its dense explainability gains do not improve F5's unchanged pooled vector. Intramodal consistency and AlignCLIP require learned representations and optimize different retrieval/classification targets. ClearCLIP and Sober CLIP expose spatial/spurious-feature issues. ICDiff's SD1.5-trained embedding has SDXL positive-score .818 versus CLIP .735 in its Table3, but that panel is100 selected positives per model without a negative/FPR endpoint; Appendix H explicitly reports semantic false positives without copying.
JUDGMENT: None establishes a drop-in descriptor with better T3 and unchanged T5. The relevant current bottleneck audit is [T0 summary](../results/wp4-t0/summary.json), not a semantic-retrieval leaderboard. Global versus dense, semantic versus instance, and generation-copy detection versus same-source img2img must stay distinct.

## D. Improvement options
JUDGMENT: Forecasts follow [OPTIONS](../OPTIONS.md).

### O1. Confidence-aware abstention with the current descriptor
SOURCE: Holistic calibration findings and the current soft-ML binding contract. Preserve seven-view CLIP and refuse a stronger content claim when already-read semantic evidence is inconsistent; no new carrier or descriptor. Targets binding-only errors. Restricted ceilings are the K01 section B binding-only pool, with zero foreign repair wherever no semantic word is read; unrestricted descriptor replacement remains UNKNOWN.
JUDGMENT: Delta C/60 foreign cells0..+1 for a permissive binding repair, or -5..0 for a conservative abstention; these are distinct policies, not a selected threshold. T4/T5 specificity could improve at the price of true accepts. Reader arithmetic small, no writer/quality/side-information change. Simpler alternative retain current C/J and report uncertainty only.
JUDGMENT: T0's precommitted <10% loss-headroom rule kills prioritizing binding as the main foreign repair before any threshold fitting. A later abstention rule must be fixed on DESIGN and cannot claim improvement unless T5 specificity gains justify its T3 cost. No closed line reopened; no new threshold is selected here.

### O2. Dense-feature or foreground-aware semantic pooling
SOURCE: ClearCLIP and CLIP Surgery suggest changing which spatial representation is pooled, not simply swapping an advertised robust backbone. Targets semantic drift after regeneration/T4 paste. New q definitions require new consistently written marks; old decoded q cannot measure its efficacy. Physical ceiling UNKNOWN.
JUDGMENT: Delta C/60 SD1.5 .4 0..+5, SDXL .2 0..+3, K3 .2 0..+3; lower ranking because a better descriptor cannot repair absent carrier evidence by itself. Dense features/category conditioning increase reader memory/compute and may add text/class side information; foreground invariance can increase T5 collisions. Writer must re-encode q, with all-image/flat-region/human checks. Simpler alternative current seven-view global descriptor.
JUDGMENT: T0 is the available bottleneck screen. A future matched new-mark comparison is killed if better same-source stability does not retain the same different-instance false-accept rate, or strict quality/T4/T5 fails. If sold as a new reference-free instance descriptor, this is REOPENS-CLOSED-LINE and remains inactive. No model assets are downloaded or adapted now.

### O3. Instance-aware representation learning
SOURCE: Intramodal consistency, AlignCLIP and ICDiff motivate joint invariance and hard-negative specificity, while ICDiff Appendix H supplies the counterexample. Train only under a separately specified fresh development design; no training is allowed now. Targets semantic collision plus drift, physical ceiling UNKNOWN.
JUDGMENT: Delta C/60 foreign .2 cells0..+5 and SD1.5 .4 0..+8 are low-confidence planning ranges, not the paper's performance; T5 could worsen. New trained weights, training data and extra reader/version side information are substantial costs, and changed q requires new marks/quality checks. Simpler alternative O1 diagnosis with the fixed model.
JUDGMENT: T0 already tests whether this can be the principal present T3 repair. A future prototype is killed if invariance gains disappear at a fixed T5 false-accept threshold or require lost strict quality. REOPENS-CLOSED-LINE for reference-free instance representation; judge ruling required before any implementation, training or new data. No closed line is reopened in this package.

## E. Offline tests and dispositions

SOURCE: Commands, exact commits, input/output hashes, split/missingness, all numbers and inherited prospective kill rules are in [WP4 results ledger](../results/LEDGER.md) and its linked raw outputs. These are exploratory development results; each option below has the test or specific unavailable intervention identified in [OPTIONS](../OPTIONS.md).

MEASURED: T0 gives only1/207 F5 foreign EVALUATE source-cell losses available to an already-read binding-only repair (.483%, studies overlapping), below the10% priority rule. K01-O1 is killed as the principal foreign repair; abstention remains a possible narrower claim/specificity policy, not a gain. T0 cannot bound a physically rewritten descriptor.
JUDGMENT: O2/O3 have no saved alternate feature/payload marks and cannot run without new feature extraction/rewriting or training; their physical gain is UNKNOWN and any reference-free instance variant remains closed. No unexecuted representation is assigned a zero ceiling. The prior noiseless and r3-256 negatives in B still constrain enthusiasm.
