# Selected statistical design for the next local component study

Author: Codex statistical-design subagent, 19 October 2026. **Research-only, NOT RUN.** This is a prospective scientific decision document, not a registered study, execution manifest, acquisition permission, human approval or independent milestone review. The parent's bounded follow-up authorizes this writing after the original session deadline. The first local clock was `2026-10-19T06:01:31.7078429-08:00`; no deadline was reset.

Parent integration fixes the temporal offset at 0.5–1.0 seconds, retains historical seeds 15/16/17 and channel settings, chooses the planned-bank bounded interpretation, verifies analytic arithmetic and records implementation inheritance. These are prospective researcher decisions made under the user's delegated authority, not human experimental approval.

## 1. Decision and scope

Select a paired Full-versus-ORVF study of **same-owner record discrimination, conditional on a finite curated frame of small, disjoint registries**. Use 1,200 randomly sampled creator/production-and-bank blocks; each has eight records, two assigned test-owner profiles and three fixed positive regeneration seeds per checkpoint. The two checkpoint cells are SD1.5 and SD2.1-base, each at strength .2. They must both satisfy the prespecified criterion. This is a finite-frame, fixed-bank-size, fixed-schedule result, not inference to all Internet images, arbitrary registries, unseen seed distributions, independent encoders or active adversaries.

The primary q-benefit quantity is the proportion of blocks in which ORVF makes at least one same-owner wrong-record acceptance and Full eliminates **every** wrong-record acceptance over the fixed schedule. Require at least a 5-percentage-point proportion of such resolved episodes, at most 2 percentage points of blocks suffering any q-induced correct-record loss, and at least 85% Full delivered source-majority recovery. Use exact finite-population hypergeometric confidence limits with a simultaneous 95% family covering both directions for all three quantities in both checkpoints. No asymptotic cluster standard error or independent-comparison binomial denominator is used.

This deliberately strengthens and narrows [contract 23](../23-component-study-contract.md): a generic reduction in any-wrong-record incidence alone is insufficient, and small relative recovery loss alone is insufficient. The benefit must resolve a same-owner error episode and the Full method must still recover intended records. Both frozen algorithms, thresholds and all-accepted-set semantics remain unchanged. Historical beta `found=false/read=false` motivates the design but supplies no assumed q effect, baseline rate or prospective power estimate.

External methods, active re-marking, method variants and new threshold fitting are not part of this next local study. Their existing authorization boundaries remain closed. A positive result does not by itself complete the broader empirical article or establish method novelty.

## 2. Target frame, sampling and dependence

### Selected population

The target is the equal-weight finite set of eligible **creator/production dependency components** from one prospectively frozen Wikimedia Commons real-camera sequence frame, under the source and licensing restrictions in [the fresh-data plan](../20-fresh-data-plan/README.md). Each eligible component must supply the bank described below. This is a provenance- and availability-selected frame. It is not a probability sample of all creators or Internet photographs. Open Images ordinary photographs are not pooled into this temporal-neighbor population, and agreement-gated reserves do not silently replace it.

The finite target is the enumerated, frozen curated list, not all eligible material that might exist on Commons. Preserve discovery queries, metadata snapshot dates and curation exclusions to disclose coverage. Curation may be selective on the declared metadata/provenance criteria; it may not use method outcomes. Conditional inference to this actual list remains meaningful without pretending the discovery process itself was probability sampling.

Eligibility and metadata collection must later be completed before method outputs and before the random sample. There are currently **no selected asset identities, metadata snapshot, real N, verified individual licenses, new labels, or demonstrated 1,200-block availability**. Those are factual inputs to be acquired only under later authorization; they are not omitted statistical choices. Frame membership cannot depend on q, descriptor similarity, owner detection, marking success, new regeneration results or past method failures.

Conservative connected-component grouping follows shared creator, production, original work, reupload and derivative evidence. Unknown creator/provenance remains excluded before frame freeze. A component is one block even if it contains many videos, creators or source groups. Select exactly four distinct capture groups from each eligible component by a reproducible ordering fixed before outcomes. Each contributes two separately captured, provenance-supported same-shot observations A and B. The new ground-truth relation is **distinct capture**, not a new PSNR threshold and not a relabeling of historical E2. Two independent, output-blinded labelers and one output-blinded adjudicator resolve disagreements before frame freeze; unresolved pairs make that candidate component ineligible. Real personnel and judgments remain to be supplied, not invented here.

The within-group pair rule selects A as the earliest eligible original capture and B as the earliest subsequent eligible capture at least 0.5 and at most 1.0 seconds later. Use original timestamps, or frame index divided by a documented constant native frame rate; for an explicit burst, require recorded capture times. Missing/contradictory timing makes the group ineligible. This fixed half-second minimum avoids defining the entire task by immediately adjacent frames; it is a researcher scope choice, not a guarantee of content difference or a tuned difficulty parameter. Sort eligible capture groups by canonical original-work ID then capture-group ID and take the first four. Eligibility requires native width and height each at least 512 pixels, an unambiguous shared shot/capture group, and no edit, interpolated/generated frame or scene cut between the observations. The labelers verify capture provenance and continuity; they do not grade method difficulty. Later disagreement about distinct-capture identity is retained as label uncertainty, never settled using detector outputs. Distinct captures may still produce identical canonical pixels or nearly identical content: retain and separately disclose that subgroup. The claim concerns original-record identification by capture provenance, not a claim that every negative is perceptually different.

### Random selection

1. Freeze the full eligible block list, its size N, the four pairs per block, reference/query roles, test-owner assignment, source records, exclusion register and label decisions. Preserve the committed frame and its hash. No outcome may yet be known.
2. Only then obtain and record one fresh randomization seed, generated by a standard cryptographic random source without seed search or retries. Use an unbiased uniform shuffle of the canonical block list and take the first 1,200 blocks. A hand-chosen seed or deterministic ranking by a researcher-chosen salt is reproducible but is not the selected probability-sampling design.
3. Use simple random sampling without replacement, with inclusion probability `1200/N` for every block. There is no replacement for post-selection failures. If `N=1200`, this is a census and the inferential interval reduces to the exact finite-frame proportion. If `N<1200`, the selected study does not proceed: report insufficient frame feasibility and require a separate pre-outcome scoped plan, without borrowing pairs to inflate N.

Each sampled block contributes equal weight. Its fixed repeated seeds, records, native owner calls and all within-bank comparisons are internal observations, not additional random-sampling units. **There is no cross-block reference, source, creator/production component, derivative, distractor or bank reuse.** The same frozen model/software and two public test-owner profiles may be fixed constants across blocks; these do not themselves become randomly sampled owners. Public owner IDs do not assert real legal ownership.

The finite-frame design does not require image outcomes from different creators to be iid. Its uncertainty arises from genuine random selection of blocks with fixed potential protocol outcomes. Cross-block bank reuse is nevertheless prohibited because it would make a block's decision depend on which other blocks were sampled, destroying the selected fixed-unit target. No trial-wide adaptive caches, data-dependent calibration or candidate aggregation may alter another block's outputs. If later grouping shows two nominal blocks share a dependency component, the frame is invalidated rather than repaired by dropping the worse result.

Inference conditions on the frozen implementation, seed schedule, enrollment rule, per-block processing policy and frame. It does not average over future execution environments. Undocumented nondeterminism, order-dependent failures or shared-resource interference that changes block outcomes with sample membership requires a narrower descriptive report; the random-sampling argument must not simply be asserted after such a breach.

## 3. Bank, positive targets and fixed schedule

For every block, rank its four source pairs by the frozen rule and call them `(A1,B1)` through `(A4,B4)`. These names are roles, not invented asset IDs. Assign pairs 1 and 2 to test owner alpha and pairs 3 and 4 to test owner beta. Each owner therefore has four distinct enrolled records; every block contains eight. Freeze this mapping before outputs. Each record is enrolled from its ordinary F5-r2-marked publication image with its own unchanged q and reference descriptors. This is ordinary assigned-owner marking, not an attacker re-marking another owner's publication.

The primary original target is A1, its admissible correct-record set is the singleton `{A1}`, and its legitimate owner set is `{alpha}`. B1 is an enrolled same-owner, same-shot distinct-capture distractor. A2/B2 provide two more same-owner wrong records; A3/B3/A4/B4 provide four other-owner wrong records. None is removed because its q collides, F passes, or the reference is inconvenient. The bank is small on purpose: the local identification question requires within-owner alternatives and a second owner while allowing complete-set decisions without a huge shared registry. It gives no extrapolation to large-bank risk.

Regenerate A1's published marked image once per checkpoint at strength .2 using each of the fixed seeds `15,16,17`, the historical registry schedule, with DDIM20, empty prompt and guidance 1. Preserve the SD1.5 safety checker and the existing SD2.1-base configuration without that checker; their difference is part of the declared channels, not a clean model-only contrast. Seed reuse is a fixed transformation schedule, not reuse of a consumed source and not random sampling from future seeds. This produces three scheduled positive queries per checkpoint, six per block and **7,200 scheduled primary queries** over 1,200 blocks. The design entails **9,600 enrolled records**, not 9,600 independent observations. These are arithmetic design counts, not acquired assets, successful generations, runtime estimates or promises of feasibility. Use the inherited 512-by-512 RGB8 canonicalization and frozen F5 r2 settings. Exact intended source identities and remaining implementation facts are documented in [implementation inheritance](implementation-inheritance.md); none is an executable package or approval.

Every query sees its entire planned eight-record bank and both owner candidates. Full and ORVF use the exact same native outputs, F decisions, reference records and query image; the only logical deletion is Q. Missing later stages are not manufactured rejection values. Stage outputs required for controls must be available even if the deployed Full path short-circuits.

All six local controls from contract 23 are retained as diagnostics on those shared outputs: owner-only, F, OF, ORVF, ORVQ and Full. Owner-only has no record-recovery endpoint. No extra independent runs or calibrations are introduced for the controls. Retain a clean A1 query and its pre-marking A1 source as per-block diagnostic queries if later execution is authorized; they are not part of the primary three-seed opportunity count and cannot rescue a failed primary criterion. Other T4/passive competing-enrollment panels remain separate future questions; no JPEG/crop/color or active attack panel is added here.

## 4. Primary estimands, exact predicates and rationale

For checkpoint m and block b, let `M_hbms` be arm h's **entire accepted-record set** on seed s. On fully known decisions, define:

| Symbol | Fixed block predicate | Meaning |
|---|---|---|
| `E_hbm` | At least one scheduled seed accepts any record other than A1. | Any wrong-record episode; correct-plus-wrong counts as error. |
| `S_hbm` | At least one scheduled seed accepts B1, A2 or B2. | Same-owner wrong-record episode. |
| `H_bm` | `S_ORVF,bm=1 AND E_Full,bm=0`. | q resolves a same-owner error episode without leaving any wrong-record acceptance anywhere in the schedule. |
| `L_bm` | At least one seed includes A1 under ORVF and excludes A1 under Full. | Any q-induced correct-record loss within the three-seed schedule. |
| `G_bm` | At least two scheduled seeds deliver a valid Full output establishing inclusion of A1. | All-attempt Full source-majority recovery; missing/failed delivery is a miss for this service-yield endpoint. |

The three primary parameters in each checkpoint are equal-block finite-frame means `theta_Hm=N^-1 sum_b H_bm`, `theta_Lm=N^-1 sum_b L_bm`, and `theta_Gm=N^-1 sum_b G_bm`. Their sample estimates divide by 1,200, never by the number of returned outputs.

Under shared valid inputs, Full is a subset of ORVF. Thus `H <= E_ORVF-E_Full` and `H <= S_ORVF-S_Full` pointwise. A 5-point H benefit therefore implies at least a 5-point reduction in **both** any-wrong and same-owner-wrong block incidence. H is a **qualified resolved-episode frequency**, not the generic paired error difference. Its failure does not refute every possible smaller or cross-owner-only q benefit. The ordinary paired differences are still mandatory reported quantities.

Also `mean_s(C_ORVF-C_Full) <= L` for each block. Consequently the 2-point limit on mean L is stronger than a 2-point limit on mean per-seed recovery loss. It explicitly limits how many source episodes suffer any degradation. It is not interchangeable with a per-comparison 2% error budget. The G floor prevents a q gate that resolves ambiguity mainly by universal abstention from being called useful. G includes A1 even if there is co-acceptance, so Full exclusivity and its wrong-record rate remain separately visible.

**Selected practical margins:** `theta_H >= .05`, `theta_L <= .02`, and `theta_G >= .85`, separately in both checkpoints.

- Five percent means resolving at least one additional same-owner-confused source episode in twenty under exactly three regeneration opportunities and this eight-record bank. A smaller effect is not the selected thesis-level justification for an extra record-code gate. This is a declared researcher utility judgment, not a measured user preference or externally validated deployment threshold.
- Two percent means no more than one source episode in fifty suffers any extra correct-record loss. The asymmetry against five-point benefit is intentional: correct retrieval is already difficult, and the additional gate should consume only a small recovery budget. It is stricter than the earlier provisional five-point mean-loss allowance.
- Eighty-five percent requires successful intended-record recovery on at least two of three seeds in at least 85% of source episodes. It reuses the thesis's recovery-service aspiration, but **does not transfer historical-cohort evidence or claim equal task difficulty**. No legal or high-assurance security threshold is implied.

Margins are fixed research decisions now. If ORVF rarely reaches same-owner wrong-record acceptance, H may be below .05; that is a legitimate negative component result. Neither O/R gating nor low baseline error is grounds to relax the margin after evaluation.

## 5. Paired finite-population inference and multiplicity

For any one binary endpoint Y in this table, the full finite frame contains an unknown integer K of positive blocks. A genuine SRS of n=1,200 gives count X with

`P_K(X=x) = choose(K,x) choose(N-K,n-x) / choose(N,n)`.

This distribution comes from randomization over a fixed finite population, not iid modeling of source pairs. The same sampled blocks serve both arms and both checkpoints; dependence between endpoints is allowed. H and L are constructed **within each paired block first**. They are never obtained by subtracting two independent arm confidence intervals or by treating record comparisons as trials.

Allocate `a=.05/12=1/240` to each of 12 one-sided limits: three quantities, two checkpoints, two directions. For observed count x, retain candidate integer K for its lower-tail test if `P_K(X<=x)>a`, and for its upper-tail test if `P_K(X>=x)>a`. Define

`Lower(x)=min{K/N: P_K(X>=x)>a}`;

`Upper(x)=max{K/N: P_K(X<=x)>a}`.

Include K=0 and K=N in the candidate grid with their degenerate distributions, and evaluate impossible counts as probability zero; do not force 0 and 1 into every resulting interval. Equivalently invert the exact discrete one-sided tests; no mid-p correction, normal approximation or randomization of boundary decisions is used. The two limits jointly cover each endpoint with at least `1-2a`, and the union bound gives at least 95% simultaneous coverage of all six intervals without assuming checkpoint independence. Exact discrete intervals can be conservative. For a fully observed census they collapse to the observed fraction.

The final rule uses these limits and realized N, not a binomial approximation. Boundary equality is explicit: support allows a lower limit equal to a lower margin and an upper limit equal to an upper margin; refutation requires a strict violation. Allocating both directions up front allows a bounded negative result without selecting a convenient one-sided direction afterward.

There is **one primary family**. Read-availability, F-only, OF, ORVQ, raw q-distance histograms, D1-fallback strata, clean/unmarked diagnostics, owner ambiguity and cross-owner decomposition are descriptive secondary analyses. Report point summaries and logical missingness ranges; any optional intervals are labeled marginal/exploratory and are excluded from the confirmatory decision. No secondary promotion, post-hoc gatekeeping or search across favorable bank sizes is allowed.

## 6. Analytic sample-size and precision justification

The chosen n is **1,200 distinct eligible blocks**, not the earlier acquisition ambition of 100 source groups or 20 creators. Select a prospective target of **at least 95% joint randomization assurance in the strong planning region defined below**, while keeping the two-checkpoint 95% simultaneous inference family. These are different probabilities. The n choice is conservative and is not claimed to be the smallest adequate size; it does not imply that the frame exists or that the true effects resemble that region.

For planning only, define Bernoulli relative entropy

`D(t||p)=t log(t/p)+(1-t) log((1-t)/(1-p))`.

The Chernoff upper bound `exp[-n D(t||p)]` applies to the appropriate upper or lower hypergeometric tail by the without-replacement convex-order result. The probability law and this transfer are documented in Greene–Wellner, arXiv:1507.08298v3, §1 equation (1.2) and §2 opening paragraph. The calculation below is our analytic design derivation; it is not a result of running the method or a simulation. [Opened primary manuscript](https://arxiv.org/pdf/1507.08298v3). The parent verified the arithmetic and supplied a sensitivity analysis in [analytic justification](analytic-justification.md).

The following **sufficient**, conservative observed count conditions in each checkpoint imply the corresponding exact limit clears its margin, for any N>=1,200:

| Quantity | Sufficient count | Least-favorable margin tail, bounded analytically | Relation to a=1/240 |
|---|---:|---|---|
| H benefit | `x_H>=90` (7.5%) | `exp[-1200 D(.075||.05)]`, approximately .00102 | Below .004167 |
| L loss | `x_L<=8` (2/3%) | `exp[-1200 D(1/150||.02)]`, approximately .000663 | Below .004167 |
| G recovery | `x_G>=1080` (90%) | `exp[-1200 D(.90||.85)]`, approximately .00000210 | Below .004167 |

These are not the final exact critical values; hypergeometric inversion can support less extreme counts depending on N. Their purpose is to show a concrete, distribution-valid sufficient region without inventing a frame size or reporting unperformed numerical enumeration.

For an explicit **hypothetical planning alternative**, assume the finite-frame proportions in both checkpoints satisfy `theta_H>=.10`, `theta_L<=.002`, `theta_G>=.95`, and all scheduled outputs are evaluable. These are assumptions for design, **not pilot estimates, forecasts, calibration evidence or claims about F5**. Failure of the sufficient region has the union bound

`P(not all sufficient conditions) <= 2{ exp[-1200D(.075||.10)] + exp[-1200D(.0075||.002)] + exp[-1200D(.90||.95)] } < .032`.

For the first term, failure is `X_H<=89`, bounded conservatively by the event `X_H<=90`. For the second, failure is `X_L>=9`, hence `9/1200=.0075`. For recovery, failure is `X_G<=1079`, conservatively bounded by `X_G<=1080`. Approximate terms are .0109, .00493 and less than `2e-11`, respectively. Thus the design has **at least 96.8% randomization assurance within this explicitly strong, fully observed alternative region**. This is an analytic lower bound, not achieved power, an empirical probability, or an assurance near the margin. Integer finite-frame proportions only narrow the least-favorable tail cases. The calculation uses no assumption that the six endpoints are independent.

Useful sanity check: with no observed positive endpoint events, a conservative upper limit is at most the binomial zero-event expression `1-a^(1/1200)`, approximately .00456, because `P_K(X=0)<= (1-K/N)^1200`. That is far below either .02 or .05. This does not license treating unavailable outcomes as observed zeroes. General interval width remains data- and N-dependent; no fixed ± precision claim is made.

**Feasibility decision:** the selected design is demanding: 1,200 disjoint creator/production components and 9,600 eligible reference images, plus blinded curation. The existing dossier establishes neither this availability nor costs. If the frame cannot supply it, this exact study is infeasible; no experiment proceeds under the fiction that more seeds, records or pairs replace components. A new, separately labeled pre-outcome plan may narrow the population, use a census or weaken the precision objective, but that would be an amendment, not execution of this design. No paid compute or resource commitment is authorized here.

## 7. Missingness, malformed output and identification bounds

Retain all 1,200 selected blocks and all fixed slots. Record separately: before-selection administrative ineligibility; selected-source withdrawal; marking failure; absent query; blocked query; missing native owner call; valid O=false; valid R=false; malformed/missing q; explicit valid D1 abstention; absent/invalid descriptor; missing reference; label uncertainty; complete decision; and missing inventory/status itself. No replacement on successful-output grounds, no zero-filling of error counts, and no transformation of a missing artifact into D1 fallback.

Use contract 23's three-valued conjunction semantics, including valid early rejection when an observed false gate logically suffices. For each query retain lower and upper possible accepted sets `Mminus` and `Mplus` in the **planned eight-record bank**. Compute each block's H and L lower/upper values by extrema over jointly consistent completions preserving shared outputs and Full-subset-ORVF. In particular, H=1 needs a known ORVF same-owner wrong acceptance and known rejection of every wrong Full record on every scheduled seed. An incomplete Full bank cannot be certified error-free simply because its observed subset is empty. Malformed q is an unknown/invalid scientific input, not evidence that Q usefully rejected a record. Preserve known wrong accepts even when the rest is unavailable.

For endpoint Y, let `x_Y^-` be the number of blocks known to satisfy Y and `x_Y^+` the number that could satisfy it. Use `[Lower(x_Y^-), Upper(x_Y^+)]`. Monotonicity and the pointwise containment of the unknown full-data count make this a conservative combination of identification uncertainty and random-sampling uncertainty, with the same simultaneous family allocation. There is no missing-at-random assumption. Wide missingness bounds are substantive unresolved evidence, not a reason for complete-case replacement.

G has two deliberately separate meanings in reporting:

1. **Primary operational G:** count a seed as delivered only if the scheduled attempt provides a usable output establishing intended-record inclusion. A failed/absent attempt provides no delivered recovery; it is an operational miss, not a measured native rejection. With all planned statuses accounted for, G is a known binary source-majority service-yield outcome. Use its all-attempt denominator and the specified exact limit under the fixed per-block attempt-policy target.
2. **Underlying scientific recovery:** retain C lower/upper membership and a possible majority result under missing decisions. Show their identification bounds beside operational G. These are not substituted for G to rescue delivery failures; conversely an operational miss cannot prove that the unobserved native method would reject.

The fixed potential-outcome requirement applies to operational G too. Freeze one scheduled attempt per seed, with only exact resumption of an interrupted attempt allowed; no new seed, new candidate or outcome-selected rerun. If an unrecoverable shared outage or order-dependent resource failure invalidates the per-block policy/noninterference assumption, report operational yield descriptively and withhold the corresponding population-level support/refutation. Missing scientific decisions can still receive conservative bounds, but an execution-policy breach is not repaired by a formal confidence interval.

All scheduled record/owner decisions and failure statuses must be inventoried. The selected primary claim is **planned-bank bounded**: logical bounds may support it despite unknown decisions only if every allowed completion clears the simultaneous criteria. This prospective choice does not require every reference/output to be observed, and does not certify a fully evaluated bank. Report a separate complete-observed-bank flag, true only if all eight planned records and their required decisions are available in every scheduled query; any missing item makes that flag false. This deliberately separates the new bounded claim from the historical strict E3 complete-bank gate, which remains unchanged and failed. Where a failed operation leaves no uniquely defined latent native decision, the scientific contrast is a set of compatible completions, not an asserted hidden measured value; bounds must cover all of them. Operational G still counts failed delivery as a miss.

## 8. Required reporting and decisions

Publish the block-level paired table and all accepted sets/statuses at the permitted release granularity. For each checkpoint report all-attempt C mean, G majority, exclusive-original recovery X, any wrong record E, same-owner error S, any wrong owner, record ambiguity, owner ambiguity, certified abstention, incomplete/invalid output and clean quality availability. Report C-plus-E explicitly; neither wrong-only counts nor a chosen best record can replace E. Report q loss L, H qualified resolution, the generic `E_ORVF-E_Full` and `S_ORVF-S_Full`, and ORVF's opportunity rate `S_ORVF`. The H result is never presented as evidence of cryptographic authentication.

Report per-seed results descriptively as well as block aggregation. Distinguish explicit valid D1 fallback from missing descriptors. Include the native O/R joint table and V statuses, so the study can reveal that q had few reachable opportunities without treating unread/invalid calls as q discrimination. The strict frozen clean-quality criteria remain reported on all marking attempts; no human quality ratings are fabricated and no successful-quality-only subset replaces the primary cohort. A q component finding is not an automatic quality-qualified publication decision.

Using the simultaneous bounds after missingness:

- **Support this selected useful increment:** both checkpoints satisfy `Lower(H)>=.05`, `Upper(L)<=.02`, `Lower(G)>=.85`, and no frame/noninterference/predicate breach invalidates the design. Report all diagnostics and the narrow finite-frame interpretation. A resolved same-owner episode can still end in abstention; the separate loss budget and absolute recovery floor are therefore part of the same claim.
- **Refute this selected utility specification:** at least one checkpoint satisfies `Upper(H)<.05`, `Lower(L)>.02`, or `Upper(G)<.85`, with the same valid coverage assumptions. Identify the failed condition and checkpoint. This refutes the stated two-checkpoint useful-operating-point claim, not all q uses, all banks or an isolated smaller benefit. If a protocol breach prevents valid inference, call the study invalid/unresolved rather than refuted.
- **Unresolved:** neither support nor refutation is established, including intervals/bounds straddling margins. Low returned-output counts, malformed codes or missing banks cannot be converted to a negative result merely to close the study. No favorable checkpoint replaces the conjunction.

One fixed analysis occurs after all scheduled blocks are accounted for. No interim efficacy, futility, sample-size re-estimation, optional extension or early success stop. Operational stops are only authorization/resource limits, rights/provenance breach, invalid frame, integrity failure or inability to finish the frozen schedule. Preserve every attempted result; an early stop is reported with the missingness bounds and generally unresolved. Any new design uses a new untouched frame rather than selectively extending this one.

## 9. Provenance and source access

Read authoritative MAIN `thesis-runs/d916749c/STATE.md` once, the thesis-experiment-design skill, dossier BRIEF, contract 23, F1/F2 in `07-gap-closure-plan.md`, the fresh-data README and `05-theory-security.md`. One attempted filename `07-future-experiment-agenda.md` did not exist; the correct `07-gap-closure-plan.md` was then read. The skill supplied falsifiability, units, leakage and stopping principles only; the user's research-only instruction overrides its execution helper, manifests and runner requirements. No helper was run.

| Access, 19 October 2026 | Exact query/URL and result | Relied-on locator |
|---|---|---|
| Web search | `Chvatal hypergeometric tail 1979 sampling without replacement Hoeffding exponential bound pdf` | Discovery only; snippets not treated as inspected papers. |
| Failed primary mirror open | `https://pmc.ncbi.nlm.nih.gov/articles/PMC5839521/` returned browser/reCAPTCHA page. | No fulltext claim. |
| Failed author-PDF open | `https://sites.stat.washington.edu/jaw/JAW-papers/jaw-greene.bern.2017.pdf` returned 404. | No fulltext claim. |
| Successful primary HTML | `https://arxiv.org/html/1507.08298` explicitly identifies **arXiv:1507.08298v3, 7 March 2016**, Greene and Wellner, *Exponential Bounds for the Hypergeometric Distribution*. | §1 equation (1.2): finite-population probability law; §2 first paragraph: Chernoff bounds transfer via convex ordering. |
| Successful primary PDF | `https://arxiv.org/pdf/1507.08298`, same paper; 38-page PDF opened. | Text cross-access; no independent version upgrade beyond v3 HTML identification. |

Tail inversion, paired-event inequalities, utility margins and the sample-size choices above are the author's derivations/decisions, not endorsements in the cited paper. Approximate arithmetic is analytic and explicitly prospective. No interpreter, simulation, dataset/image/model/code download, image inspection, generation, detector, metric, experiment, calibration, install, execution manifest, approval or shared-file edit was used. This owned Markdown file is the sole deliverable.
