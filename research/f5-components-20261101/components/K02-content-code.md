# K02 — Content code and semantic compatibility

JUDGMENT — PROPOSED WP1 dossier, not a ruling. Scope: structure, prior evidence and conditional ceilings only. No WP2 literature result or WP3–WP5 improvement verdict is implied. Source: [BRIEF](../BRIEF.md), WP1.

## A. Structure

- SOURCE — The supplied descriptor maps to 32 signs of HMAC-derived Rademacher rows. Rows depend on profile key, detector configuration, and vector width, not OwnerID; exact bit generation first scales by the largest absolute component and sets a bit when the projection exceeds `1e-9` (`scripts/revised_watermark_v5.py:322-335`; `scripts/revised_watermark_v4.py:443-463,524-539`). The continuous F5 projections instead unit-normalize the descriptor (`scripts/f5_latent_codec.py:115-128`). DERIVED — Their directions agree away from the tiny numerical threshold, but “signs exactly match” has a threshold/scale qualification near zero.
- SOURCE — F5 soft compatibility estimates an angle on 2,000 fixed points between .001 and pi-.001 using a product likelihood `Phi(c_j*p_j*cot(theta))`, mixed with estimated bit-flip probability e; distance is `32*theta/pi` (`scripts/f5_latent_codec.py:111,131-155`). This is evaluated only on decoded reads with semantic checking active; other found paths use the corrected-distance rule.
- SOURCE — The base code itself warns that the exact angle/pi disagreement identity holds for isotropic Gaussian/Haar hyperplanes, not general Rademacher rows (`scripts/revised_watermark_v4.py:443-450`). DERIVED — Neither this soft likelihood nor 32 iid Bernoulli semantic-bit errors is an exact distributional consequence of CLIP plus Rademacher hashing. Dense descriptors may motivate an approximation; saved success counts do not prove the model.
- DERIVED — Extraction costs 32 by 512 sign projections; a soft-angle evaluation forms 2,000 by 32 likelihood terms. The implementation can evaluate soft status twice on a found semantic channel (`scripts/f5_latent_codec.py:298-300`). There is no direct distortion, but q fixes the robust and instance payload targets. The binding-only ceiling on frozen reads is identifiable; a different q/code family has UNKNOWN ceiling and affects T4/T5 as well as T3.

SOURCE: Full interface/null context is in [code structure](../context/wp1-code-structure.md); paths and line locators above refer to inspected repository code. Historical write time 119 s/mark and detector-row time about 1.5 s are environment-specific anchors, not CPU or isolated component timings (BRIEF.md WP5). No new model timing was run.

## B. Prior evidence

SOURCE: The table carries the relevant inspected earlier experiments into this component. Each E-link resolves to the detailed source/report line locators, full numbers, study units and limitations in [prior evidence](../context/wp1-prior-evidence.md). Historical branch blobs were read with git show. SOURCE denotes an inspected report; no historical count below is a new measurement. Frozen held-out reports are contextual only, never a tuning pool.

| Evidence | Reported result (SOURCE) | What it rules out and leaves open (JUDGMENT, PROPOSED) |
|---|---|---|
| [E02: F5 r1 to r2](../context/wp1-prior-evidence.md#e02-f5-r1r2-binding-was-a-major-real-bottleneck-and-was-successfully-improved) (inventory line 42) | Paired .2 improved 25/28 to 28/28 and .4 improved 21/28 to 23/28 using soft ML plus seven views; r1 .2/.4 had 5/9 binding failures and 0 carrier failures under its older endpoint. | Binding was repairable; older recomputed-inclusive counts are not today's frozen C. No foreign-family guarantee. |
| [E05: H4 threshold kill](../context/wp1-prior-evidence.md#e05-h4-threshold-relaxation-local-rescues-cost-natural-image-specificity) (inventory line 87) | Soft/hard .4=49/58 vs 42/58; radius6/7/8/10 admitted4/10/21/62 of132 ordered semantic cross-source pairs. Radius7 rescued4/6 .4 binding failures. | Equal-specificity relaxation failed. Semantic proximity is not measured joint T5 attribution; other calibrated rules remain open. |
| [E06: Noiseless binding/sketch diagnostic](../context/wp1-prior-evidence.md#e06-noiseless-semantic-binding-ceilings-informative-but-conditional) (inventory line 95) | At4/132 false-pair budget, true feature .4/.5/.6=55/44/14 versus production 49/37/10; random256-bit ranges54–55/44–48/12–15 on173 saved identities. | Shows representation/sketch headroom conditional on transport and finite operating point; not a realizable watermark or universal upper bound. |
| [E07: r3-256 physical kill](../context/wp1-prior-evidence.md#e07-r3-256-the-physical-implementation-lost-more-than-the-noiseless-sketch-gained) (inventory line 116) | First-family .4+.5 fell85→65 at similar PSNR 44.69/44.70 and LPIPS .0173/.0171. .5 checked-only improved 19→26 but declared total selector failed; second family and T4/T5 unrun. | Rejects this256-antipodal-chip/margin4.5 package. Does not reject every longer payload, ECC or codebook. |
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

MEASURED/DERIVED: Table inputs are [loss cells](../results/wp1-accounting/loss-cells.csv) and [fragile/semantic endpoint cells](../results/wp1-fragile/fragile-cells.csv), with row-level locators in [component ceilings](../results/component-ceilings.csv) filtered to K02. There are 22 F5 study/cell rows and 22 matched v5 rows in the full accounting; studies are not pooled. Frozen C/J are unchanged. C/J are semantic endpoints; J never means fragile recovery.

SOURCE/JUDGMENT: The Phase-A pilot/law/mechanism records and inactive attack grids have no complete eligible frozen-C/J detector panel from which to infer this component's recovery; their ceilings are UNKNOWN, not zero. Coverage is explicit in [Phase-A coverage](../results/wp1-accounting/phase-a-coverage.csv). Historical smaller development panels above retain their own endpoints/denominators; no per-component source ceiling is reconstructed from report-only totals. Morphology is not a detector panel. No held-out ceiling or tuning table is created.

### Ranking and next literature work

JUDGMENT — PROPOSED: See the [joint loss/cost ranking](../WP1-SYNTHESIS.md#ranking-by-conditional-loss-opportunity-and-cost-to-change) for this component's role and interactions. Changes to this component cannot be credited with a count improvement until the necessary intervention and safety checks exist. The [K02 WP2 query plan](../literature/WP2-QUERY-PLAN.md) lists the original planned queries; the executed log and conservative count are now in the WP2 intake below.

## C. Literature since2024

SOURCE: [Six full-text cards](../literature/cards/K02.md): CSDH, HIP and DBpHash are3/5 Q1J; CertPHash, CMBH and FEAP are3/3 TOP, with the extended FEAP version disclosed. After excluding15 malformed site filters,31 substantive exact queries and at least four successful surfaces support a two-journal-slot exhaustion request. Full experimental/method locators and venue evidence are in the cards. CSDH/HIP optimize class retrieval, not instance ownership. CertPHash separates certified behavior from average robustness; its COCO perturbation guarantee is not its MNIST collision guarantee. DBpHash's PCBI false-positive fraction .095 is9.5%, not a small security tail. FEAP requires private-source entropy; it cannot extract a secret from a public image.

DERIVED: Rademacher sign disagreement is not universally angle/pi: x=(1,0), y=(1,a),0<a<1 have no sign disagreements under any two-dimensional Rademacher row although their angle is positive. Zero-padding retains this counterexample in512D. This invalidates an exact universal likelihood claim, not the empirical usefulness of F5's approximate soft reader. Neither longer hashes nor learned class retrieval inherits T5 specificity.

## D. Three proposed options

JUDGMENT: The common forecast, visibility, side-information and closed-line conventions are in [OPTIONS](../OPTIONS.md). All are low priority for foreign C repair: the restricted already-read ceiling is +0 on SDXL .2/.4, +1 on .1 and +2 on K3 .2; SD1.5 .4 has +8/60. New written codes have UNKNOWN physical and joint-safe ceilings.

### K02-O1 — Calibrate the existing q32 approximation

JUDGMENT: Use HIP's explicit angular assumptions and the counterexample above to audit/calibrate the existing likelihood, keeping q unchanged. Target decision-model mismatch, especially SD1.5 .4; planning gain0..2 C/60 there and0..1 on SDXL .1,0 on .2/.4 for an already-read-only rule. This narrow range is a judgment within the oracle, not a measured gain. Cheapest available screen is TK2's one-bias saved-feature prediction test, prospectively killed below10% EVALUATE MAE reduction; no C/J substitution follows even if it passes. A full likelihood/negative-tail calibration needs adequate saved per-view/source statistics and disjoint negatives, currently unavailable. Quality and writer cost unchanged; reader adds O(32) arithmetic; reference features are offline diagnostic side information only. T4/T5 can worsen through overacceptance. Strongest simpler alternative: retain current approximate soft score with explicit limitations. No closed line reopened.

### K02-O2 — Report uncertainty or abstain around the content boundary

JUDGMENT: CertPHash motivates separating uncertain from verified decisions; an uncertainty interval for q compatibility would target false binding, not unread carriers. A conservative abstention can only preserve or lower C: planning delta -2..0/60 on SD1.5 .4 and0 on SDXL .2/.4; joint-safe ceiling UNKNOWN. TK2 is only a necessary model-validity diagnostic, and T0 rejects primary foreign-repair status if headroom<10%; neither supplies a valid interval. Cheapest decisive interval test would require repeated independent per-view or perturbation features and a frozen specificity budget, missing from these saved vectors. Kill before such a test if the proposed coverage model assumes the disproven universal Rademacher law; otherwise kill if declared coverage fails or T5 false accepts rise. No writer/quality cost, O(32) reader cost, no production reference; abstention changes endpoint semantics. Simpler: explicit unchecked/conflict status in K10 without new confidence claims. No closed line.

### K02-O3 — A new Gaussian projection code with explicit coding tradeoff

JUDGMENT: HIP/CSDH's quantization distinctions motivate testing truly rotationally symmetric Gaussian rows while keeping32 bits, not assuming a longer hash solves transport. Target code-model bias in all cells; physical ceiling UNKNOWN. Planning C gain0..4/60 on SD1.5 .4 and0..2 on SDXL .2, low confidence because foreign losses are mostly unread. Requires reembedding every image; Gaussian angular expectation does not prove finite-key calibration or T5 safety. Reader/writer matrix cost remains about32x512, payload/chip budget unchanged; no new side information. Flat-region checks follow OPTIONS. Cheapest decisive test needs newly written matched-quality marks and near negatives; unavailable under this session. Kill if no EVALUATE gain at the original false-pair budget or any strict-quality/T4/T5 regression. Simpler: O1, or keep current code. Not a reference-free instance descriptor or E3 retry; no closed line reopened, and no authorization to run it is inferred.

## E. Offline tests and dispositions

SOURCE: Commands, exact commits, input/output hashes, split/missingness, all numbers and inherited prospective kill rules are in [WP4 results ledger](../results/LEDGER.md) and its linked raw outputs. These are exploratory development results; each option below has the test or specific unavailable intervention identified in [OPTIONS](../OPTIONS.md).

MEASURED: TK2's single fitted bias+.1448109 bits reduces source-weighted EVALUATE MAE from1.5253129 to1.4595937 (4.3086%, below10%): O1 simple-calibration priority KILLED. Five DESIGN feature rows remain unavailable; all65 EVALUATE planned rows are present. This is v5 single-view saved-feature evidence, not F5 seven-view likelihood calibration. T0's small binding-only budget independently ranks repair low.
DERIVED/JUDGMENT: O2 cannot claim universal angular/Rademacher coverage because the explicit2D counterexample falsifies it. No independent repeated feature sample or coverage model exists for a meaningful interval test. O3 Gaussian rows require new q and written marks, forbidden here; no performance is inferred. None reopens a closed descriptor line.
