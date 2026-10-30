# WP9 round 2 — Independent floor audit

**Verdict: PASS for delivered WP0–WP8 floors and the floor-auditor component of WP9. No blocking finding.** This is not a verdict that RL improves the method, that a prospective protocol is ready to execute, or that a paper is publishable. WP10 is intentionally pending WP9 and is not an unmet delivered research floor.

Audit date: 2026-10-30. The supplied corrected snapshot was `db00b73`; I also read the subsequent round-2 disposition text in `09-review.md`. I was a fresh reviewer with no inherited authoring conversation. I read the brief, inspected the dossier and round-1 review/disposition evidence, counted the artifacts independently, and successfully checked **15 paper cards online against substantive primary-source methods, tables or theory, spanning all 12 clusters**. Round 1 was a locator, not a replacement for these inspections. No claim is made that I independently verified all 133 card occurrences or reproduced any experiment.

I did not read STATE, AGENTS, F6 outcomes, Phase B journals, protected source identities or images. Read-only counting and hash/schema checks used the permitted isolated stdlib interpreter; no scientific execution occurred. I performed no git operation. Accordingly, my independent freeze check covers current file hashes; the historical commit chronology is documented in the dossier and was checked against git by the round-1 auditor, not independently re-proved here. This review is my only file deliverable.

## 1. Independent floor inventory

Paths below are relative to `research/rl-20261030/`. Counts describe delivered artifacts, not a universal certification of their substantive claims.

| Work package | Required floor | Independently inspected delivery and locator | Result |
|---|---|---|---|
| WP0 | Start record, exact journal setting, floor table and 17 starting files | `PROGRESS.md` records start 2026-10-30 12:30 UTC, `PHASE_B_JOURNALS=off`, the starting-file inventory and reading allocation, and WP0–WP10 status. The context notes separate code/results/TIFS background. This is a documented reading record; a reviewer cannot reconstruct another agent's private attention from Markdown. | PASS |
| WP1 | At least 12 decision points with operational and informational distinctions | `01-decision-map.md` has **22 rows D01–D22**. Rows and accompanying sections distinguish chooser, action type, gradient availability and cost, delayed feedback, information at decision time, sequential dependence, limitations and natural non-RL tools. Necessary-condition discussion does not simply equate discreteness with RL. | PASS |
| WP2 | At least 80 exact queries over at least 5 indexes; cluster floors or permitted exhaustion; substantive cards; direct post-hoc/RL answer | **335 distinct logged query strings**, **10 valid scholarly host families**, **133 card occurrences** over all 12 clusters. Eleven clusters reach their numerical floors; C1 uses the documented exhaustion exception. Details and online sample are below. `02-prior-art.md` now gives the correctly qualified direct answer. | PASS, with bounded exhaustion and access limitations |
| WP3 | All six prescribed analyses, using allowed evidence | `03-logged-analysis.md` answers margins/floor effects; source/seed residual variation; fixed versus oracle; leave-one-source-out prediction with pre-decision information versus a constant; K=8/64/1024 and score-function costs; and attacker spread. Journal-dependent evidence stays unavailable with journals off. Development summaries, retrospective oracles and toy/bound calculations are labelled accordingly. | PASS |
| WP4 | Estimator/gradient costs, short-horizon regret, transfer identifiability, representation/quality separation | `04-theory.md` covers all four. It distinguishes sufficient sample bounds from universal lower bounds, the limits of short-horizon bandit bounds, nonidentifiability from only a few training families, source difficulty from action heterogeneity, and fixed-reader/F5 constraints from the possibility of another carrier or reader. | PASS |
| WP5 | At least 40 raw ideas, at least 3 fresh framings, frozen rule, at least 20 complete sheets, at least 7 policy points, all classes, at least 4 outside analogies, shortlist at most 6 | **60 raw ideas**: RT20, RS20, RO20 in three separate framing files. **21 full sheets C01–C21**, **10 policy points**, full RL/bandit/game classes and P1/P2/P3; outside analogies include compiler, chip design, robotics/dual control, active sensing, databases and experimental design. **Four shortlisted: C18, C03, C04, C09.** `05-screen-rule.md`, `05-candidate-table.md`, `05-candidates/`, and `ideas/` provide fields, comparisons, kills and dispositions. Expensive ideas remain marked expensive rather than being called experimental failures. | PASS |
| WP6 | At least 5 fresh forecasters, identical neutral packet, prescribed events/scenarios/quantiles, aggregation and caveats | **Five separate F1–F5 records**; each contains **186 ordered numerical p10/p50/p90 triples and 21 explicit null triples**, across GO, FAIL and RESOURCE_STOP. Total: **930 numerical triples, 105 null triples**. Packet hashes match. History reference, no-RL comparisons, conditional interpretations, median/spread tables and reason chains are present. Independent spot calculations below match. File records document fresh-model assignments; hidden-context independence is not something a file audit can prove. | PASS |
| WP7 | At least 10 routes; required route types; claims, audiences, 3 closest works, costs/dependencies, venues, objections, probabilities, decoration check | **10 routes R01–R10**, each with **five numbered objections: 50 total**. Each provides at least three primary-paper links and the required discussion. At least **five** routes do not require F6 success (R01/R02/R04/R07/R08). Null, attacker, game, small-RL and two no-RL routes are represented. Ranking-verification attempts and UNKNOWN outcomes are explicit; the brief says to report both JCR/SJR wherever verifiable, not to fabricate inaccessible quartiles. | PASS, with ranking/full-cost unknowns |
| WP8 | At most 2 prospective designs, complete controls/data/stops/costs/F6 tree, no execution | **Two designs only**, C03 and C18, in `designs/`, integrated by `08-next-experiment.md`. Both specify equal-budget comparators, random controls, source exclusion, cells/seeds, an optimization-excluded family, C/J and quality/T4/T5 requirements, stopping/multiplicity, inventory/cost and F6-contingent decisions. C03 is a conservative triage screen; C18 has explicit numerical-freeze readiness conditions. | PASS as prospective designs |

The full-sheet inventory is not just a count of names. The candidate files and their linked writer/security/systems bundles contain mechanism, information/leakage contracts, controls, necessary conditions, effect/data/costs, threat and kill criteria, closest-work comparisons, TD03 comparison, proposed claim, steelman and hostile views, and verdict. Some hostile discussion is inline alongside the steelman rather than under its own heading; this is not a missing field. Shared D/Q/B/L contracts are explicitly linked and applied.

### 1.1 Literature counts and the C1 exception

| Cluster | Required | Counted | Location |
|---|---:|---:|---|
| C1 watermarking/steganography | 15 or exhaustion | **12** | `literature/c1-watermark-stego.md` |
| C2 removal/forgery attacks | 15 | **15** | `literature/c2-attacks.md` |
| C3 augmentation | 10 | **10** | `literature/c3-augmentation.md` |
| C4 transfer/adversarial examples | 15 | **15** | `literature/c4-transfer.md` |
| C5 games | 12 | **12** | `literature/c5-games.md` |
| C6 learned optimization | 8 | **9** | `literature/c6-learned-optimization.md` |
| C7 contextual bandits | 8 | **8** | `literature/c7-contextual-bandits.md` |
| C8 diffusion/RL | 10 | **10** | `literature/c8-diffusion-rl.md` |
| C9 verification/statistics | 8 | **8** | `literature/c9-verification.md` |
| C10 reproducibility/security | 10 | **10** | `literature/c10-reproducibility.md` (5) plus `c10-security-supplement.md` (5) |
| C11 sim-to-real | 8 | **9** | `literature/c11-sim-to-real.md` |
| C12 recent work | 15 | **15** | `literature/c12-recent.md` |
| Total card occurrences |  | **133** | A paper recurring in different cluster roles is not automatically a distinct paper |

I independently parsed the consolidated exact-query column of `literature/search-log.md`: G001–G335 give **335 distinct actual strings**. Valid positive scholarly host restrictions total **130**: arXiv 46, IEEE 9, ACM 11, Semantic Scholar 2, DBLP 7, OpenReview 22, CVF 9, PMLR 17, NeurIPS 6 across its two hosts, and AAAI 1. These are **10 host families**. Other hosts and **51 malformed `site.domain` restrictions** are not credited toward this count. All are general-web, site-restricted searches; native index/API queries remain **zero**. The floor is met without counting the malformed entries or pretending that each query is a new scientific concept.

C1 contains **69 distinct queries** and valid restrictions across **six scholarly host families** (arXiv, IEEE, ACM, Semantic Scholar, DBLP, OpenReview). KAIST is an additional institutional source, not credited as an index. The C1 log shows new leads as late as Q55, followed by the Q59–Q69 closure/recovery series; Q66–Q69 span four indexes and add no newly accessible eligible method-and-evaluation paper. Twelve substantive cards are retained (four image, eight text/code); unresolved leads remain access-limited, not silently counted. Priority SPAR/SMER recovery attempts are not themselves counted as inspected papers.

This exceeds the brief's exception threshold of twelve distinct queries over four indexes and provides a visible closure attempt. It supports **bounded search exhaustion under this access and eligibility rule**, not proof that no additional C1 paper exists. Broadening C1 into text/code steganography is visible and its transfer limitations are explicit; it does not establish image-watermark evidence by analogy.

### 1.2 Freeze and forecast checks

I independently recomputed the current screening-rule SHA-256:

`df774bae6ae4d62b8e37f1f2f2058d4a87170e30708b795daa03423b0397f799`

It matches the recorded freeze. The documented rule commit `dbf4dcd` precedes the sheet commit `5dc554b`; round 1 independently checked that chronology. I made no git call and do not claim a second independent commit-tree verification. Current shortlist and rule remain unchanged through the corrections.

All four current packet hashes independently match `forecasts/PACKET-FREEZE.md`:

| Packet component | SHA-256 |
|---|---|
| evidence-packet.md | `3000fec9aa3b34bfabf285a0d8d0c846481ab7a91f62979973863da1d7344a6a` |
| history-reference.md | `8c0710c9476cb22c302ac2a46d9fd031ee8edceacbdac990cffdc661d6e57ba8` |
| venue-context.md | `c5a7a2802df92a799ab2a32e25ff23bad1edd44c1da8da20a7e743326934b6c5` |
| forecast-instructions.md | `a229af2c54800d2fbeb0939ea6b6fac3fd555dc9f346ee5787aa45a705c39823` |

My independent JSON/schema and central aggregation spot checks agree with the report:

| Scenario | Overall A2 median of forecaster p50s; min–max | Overall future-potential event median; min–max |
|---|---|---|
| GO | **8%; 6.5–9%** | **27%; 23–33%** |
| FAIL | **4%; 3.2–4%** | **25%; 19–30%** |
| RESOURCE_STOP | **6%; 4.6–6.2%** | **23%; 18–28%** |

I did not recheck every aggregate-table row; round 1 did the broader aggregation audit. The historical reference correctly separates six families from the three assessed under a common comparative gate: two qualified, one failed, three earlier families not evaluated against that full gate. It does not turn this into a common Bernoulli 2/6 success estimate.

## 2. Fifteen independent online primary-source checks

Each credited row below involved opening substantive full text during this audit, beyond the abstract or paper's existence, and comparing a concrete card claim against the primary method, theorem or result. All twelve clusters are represented. The sample is mostly different from round 1; DRIFT is intentionally repeated because it was a blocker. Page locators refer to the displayed PDF page where a source uses PDF, and section/table identifiers where it uses HTML. The checks certify only the statements specified here, not every claim in each paper or card.

| # / cluster / card | Primary text inspected and concrete comparison | Result |
|---|---|---|
| 1 / C1 / JEC-RL | [Tang et al., primary PDF](https://arxiv.org/pdf/2105.03867), §§III-B/C, equations 13–18 and Table IV, PDF pp.7/11. Policy samples coefficient modifications; rewards use environmental-loss gradients; learned costs feed syndrome-trellis coding. At 0.3 bpnzAC the GFR entries include J-UNI 29.56 versus JEC-RL(J-UNI) 33.89, but MSUERD 32.99 versus JEC-RL(MSU) 31.49; full JEC-RL 35.85. | Card preserves mixed effects and steganalysis scope; no regeneration claim inferred. |
| 2 / C2 / CtrlRegen | [Primary HTML](https://arxiv.org/html/2410.05470v2), §§3.1–3.3 and §4.2 Table 1. Regeneration starts from clean Gaussian noise while image/edge conditioning supplies content. Tree-Ring TPR at 1% FPR: CtrlRegen 0.12, PSNR 19.32; Regen 0.87/25.59; Rinse 0.61/23.28. | Non-RL removal mechanism and substantial fidelity tradeoff agree. |
| 3 / C2 / Black-Box Forgery of Semantic Watermarks | [Primary HTML](https://arxiv.org/html/2412.03283v3), §3.1 equation 4 and §4.2 Table 1. Proxy inversion/latent matching uses a reference watermarked image. For FLUX/Gaussian Shading, 150-step forgery has detection 0.95, PSNR 20.14, LPIPS 0.247; the averaged 5,000-image alternative has detection 0. | Card's proxy-gradient, reference-dependent forgery claim is supported; it is not RL. |
| 4 / C3 / AutoAugment | [Primary PDF](https://arxiv.org/pdf/1805.09501v3), §5.1 random-search ablation, PDF p.8. Best of twenty random policies gives 3.0 average error over five runs; the learned policy gives 2.6 ± 0.1. Authors discuss search-space contribution and convenience of RL. | Supports a bounded search advantage, not a proof RL is necessary for augmentation. |
| 5 / C4 / Input Diversity | [Primary HTML](https://arxiv.org/html/1803.06978v4), §3.3 equations 5–7 and §4.2 Table 1. Random input transformations with probability p enter gradient/momentum attacks. Inc-v3 to Inc-v4 transfer is 36.6 for MI-FGSM and 63.9 for M-DI2-FGSM. | Card correctly treats the 27.3-point contrast as non-RL classifier-transfer evidence. |
| 6 / C5 / Scalar Quadratic-Gaussian Soft Watermarking Games | [Primary PDF](https://arxiv.org/pdf/1607.03273), §3.3, Remark 1 and Table 1, PDF pp.14–15, with theorem/lemma context. Optimality is restricted to linear mappings/Gaussian-affine strategies; the comparison also supplies an upper bound for a broader class and distinguishes erasure regimes. | Analytical/restricted equilibrium evidence, not empirical diffusion defense, matches the card. |
| 7 / C6 / Learning to Optimize Neural Nets | [Primary PDF](https://arxiv.org/pdf/1703.00441), §3 formulation and §4 experiments, PDF pp.4/7 and Figures 2/4/5. State/history supplies gradients and objectives, action is an optimization step, recurrent policies optimize objective costs. The inspected setup has 48-dimensional input/hidden layers, horizon 400, batch 64; extended problems test different dimensions/horizons. | Supports learned recurrent optimization and bounded generalization tests; no invented exact curve gain. |
| 8 / C7 / Contextual Bandit Bake-off | [Primary PDF](https://arxiv.org/pdf/1802.04064), §2 methods and Table 2(a), PDF p.16, with reshuffling context. RCV1 losses include greedy 0.215 ± 0.010, RegCB 0.225 ± 0.008, Cover-NU 0.215 ± 0.006 and bootstrap 0.251 ± 0.005. | Simple greedy can be competitive; this does not validate off-policy evaluation on unsuitable saved records. |
| 9 / C8 / AlignProp | [Primary HTML](https://arxiv.org/html/2310.03739v2), §§4/4.1 and §5.1 Figure 5. Randomized truncation, checkpointing and LoRA enable reward backpropagation; full backpropagation collapses in the reported two-epoch example. Reward 2.8 takes 48 minutes versus DDPO's 23 hours on the matched four-A100 comparison. | Supports the differentiable-reward competitor and stated setting, not ownership robustness. The card's historical status caveat remains. |
| 10 / C9 / False Discovery Rate Control with E-values | [Primary HTML](https://arxiv.org/html/2009.02824v5), §5 Theorem 2 and §7 Table 2. Base e-BH controls FDR under arbitrary dependence with valid null e-values. The inspected 500-arm simulation gives e-BH 73.2 true discoveries and FDP 1.58%, versus BY 70.4 and 0.31%. | Conditional statistical result and simulation agree; arbitrary reader margins are not automatically valid e-values. |
| 11 / C10 / Deep RL at the Edge of the Statistical Precipice | [Primary HTML](https://arxiv.org/html/2108.13264v3), §3 Figure 3 and §4 interval/IQM discussion. Reported SPR median bias of about 0.03 is substantial relative to an approximately 0.08 claimed gain; few-run uncertainty and maximum-score selection affect comparisons. | Card's uncertainty warning is supported without asserting a universal sufficient seed count. |
| 12 / C11 / Sim-to-Real Transfer with Dynamics Randomization | [Primary PDF](https://arxiv.org/pdf/1710.06537v3), §IV A–D and Table II, PDF pp.3–4/7. Task uses binary reward, 52-dimensional state, seven-dimensional relative-angle actions and randomized dynamics. Real success: LSTM 0.89 ± 0.06 (28 trials), feedforward 0.67 ± 0.14 (12), no-randomization feedforward 0 (10). | Positive RL transfer evidence agrees; history and physical-task feedback matter to its applicability. |
| 13 / C12 / DRIFT | [Primary HTML](https://arxiv.org/html/2609.08213v1), §§1/3/3.1/5.3 Table 3 and Appendix E.4 Table 7. Setup is generation-time target watermarking, `x_w = W_f(prompt, key)`. Core removal/ladder is non-RL; optional DPPO refines fidelity under verifier conditions. On 225 inputs LPIPS moves 0.136 to 0.114, PSNR 24.95 to 25.19, with 1.16 mean rounds and zero measured survival. | The corrected stage and optional RL role are supported. This does not establish RL insertion into an already-existing image or isolate a new RL removal-efficacy benefit. |
| 14 / C12 / LatentFreqMask | [Primary HTML](https://arxiv.org/html/2610.02010v1), Algorithm 1 and §V Table I. Selected Fourier components of the encoded latent are replaced. The diffusion-replacement row has TPR 0.44, PSNR 28.4 and LPIPS 0.043; the Gaussian-replacement row has 0.36/21.6/0.119. | Card's non-RL latent-frequency mechanism and quality/removal tradeoff are supported. |
| 15 / C12 / ReWatermark | [Primary HTML](https://arxiv.org/html/2605.16796v1), §4 Policy Training Procedure and Table 4. An interference table selects a rule conditioned on victim family and quality/erasure objectives; the word policy does not make it RL. PixelSeal TPR is 0.029 versus Regen 0.080, while RoSteALS bit accuracy 0.749 coexists with TPR 0.992. | Supports heterogeneous watermark-specific outcomes and the distinction between bit accuracy and detection. |

**Unsuccessful retrieval, not credited:** the NeurIPS RandAugment PDF request timed out. It contributes zero to the fifteen checks. The additional successful C12 checks above bring the sample to fifteen without relaxing the full-text standard. No abstract-only or search-snippet-only result is counted.

## 3. Round-1 findings and corrections

I read the original findings and their dispositions and inspected the affected dossier text. This audit independently closes the following documentation issues for floor purposes; it does not replace the hostile scientist's or steelman's scientific judgment.

| Finding | Inspection and disposition | Floor-audit assessment |
|---|---|---|
| H-B1 / SB1: DRIFT stage and RL-role error | `02-prior-art.md` direct answer/novelty map, C08 and security-bundle clarifications, article scope, and WP6 correction record now distinguish generation-time target marks, non-RL removal, and optional RL fidelity refinement. My online check above independently supports the correction. | CLOSED. Exact post-hoc embedding + RL + diffusion evidence remains unverified, not a proof of absence or novelty. |
| H-B2: binomial coverage premise | Both protocols now require justified iid source-level indicators conditional on frozen fitted policies/seeds, or a separately valid sampling design. Deterministic hash ordering, split names, exchangeability or no duplicates do not prove this premise. Without it, finite-cohort reporting remains possible but inferential success/null gates are unavailable. | CLOSED as a written-design correction. The premise must actually be justified before any future inference. |
| H-W1/H-W2: triage interpretation and deployment semantics | C03 labels its order/heterogeneity rules conservative continuation priorities, not necessary conditions for every useful policy. Deployment is deterministic argmax with A tie-break. C18 requires a numerical prior/covariance/acquisition freeze; otherwise DESIGN_NOT_READY. | Addressed; future readiness is not inferred from the document's existence. |
| H-W3–H-W5: costs, novelty and forecasts | Current screen costs and full inventories are visible, claims distinguish mechanism/efficiency from a new RL algorithm, and frozen forecasts retain subjective broad-campaign scope. | Addressed with continuing final-report obligations. |
| F-W1–F-W6 | Access-limited art, indirect searches, sample bounds, forecast/cost scope, ranking/full-cost unknowns and the historical directory deviation remain explicitly disclosed. | Accepted limitations, not erased or converted into positive evidence. |
| S1–S4 | C08 probing remains WATCHLIST; C15 exact-decision stopping is a deferred certificate question; D7 scheduling charges unfinished sources; expensive/new-reader ideas remain unresolved rather than experimentally disproved. | Fair dispositions under the unchanged rule, without a hidden shortlist promotion. |
| M1–M3 | The steelman supplied three distinct missed mechanisms, pool comparisons, inspected primary methods and falsifiers: adaptive coupling of native randomness, trajectory change of measure, and goal-valid hindsight reuse. Dispositions retain marginal/support/weight/transition obligations and closest-work preemption. | Required three-idea review floor is met. These are not three demonstrated novel algorithms or a third WP8 protocol. |

The subsequently available `hostile-r2.md` and `steelman-r2.md` record PASS and their accepted boundaries in `09-review.md`. I checked the disposition summary rather than adopting their verdict as my own evidence. The nonblocking M2 clarification is sound at the floor level: a valid likelihood ratio on sampled input noise can suffice through a common map; unknown common transition factors can cancel. It should not be restated as requiring an explicit output-image density in every case. No score or forecast change is needed to record this qualification.

## 4. Numbered findings

**Blocking findings: none for delivered WP0–WP8 or this floor review.**

1. **F2-W1 — C1 exhaustion and inaccessible close art remain bounded.** The documented exception passes, but SPAR/SMER and other unresolved close leads prevent a cleared-priority or first-use claim. Keep the distinction between image and text/code evidence and the exact post-hoc question in the final report.
2. **F2-W2 — Search counts are indirect retrieval evidence.** Report 335 exact strings and ten valid host families without calling them native-index queries, independent concepts, or a completeness proof. Malformed restrictions receive no index credit.
3. **F2-W3 — Verification scope is fifteen successful primary checks.** The 133-card count is an inventory, not blanket independent verification. I did not reproduce experiments, verify every aggregate row, prove hidden-context independence, or independently traverse historical git objects. These limits do not invalidate the delivered artifact floors.
4. **F2-W4 — Preserve forecast and cost scope.** The forecasts are uncalibrated judgments from one model family about broader future campaigns. C03's full 623.02–1,107.69 hours exceeds the 600-hour forecast convention, and C18's conservative 201.853 hours exceeds 200. Cheap triage screens are not their success events. Current screen costs are C03 8.71–14.74 hours plus up to two ancillary hours, and C18 13.674 hours, with a 20-hour hard cap. Do not manufacture revised probabilities from these corrections.
5. **F2-W5 — Research-floor completion is not execution/publication readiness.** Source-model justification, numerical freezes, labels and runtime anchors remain future conditions. JCR/SJR values remain UNKNOWN where verification failed; R10 full cost/compatibility remains UNKNOWN. A finite-cohort comparison, a positive diagnostic, or an optimization-excluded but historically known family is not unrestricted transfer evidence or a publication certificate.
6. **F2-W6 — Preserve the historical write-scope disclosure.** The documented transient out-of-directory placeholder was removed and supplied no evidence. Deletion does not make “no out-of-directory write ever occurred” true. I did not perform a fresh whole-worktree git audit; the retained status claim is supported by the author's disclosure and round-1 record, not a new assertion of my own filesystem-wide verification.

## 5. Remaining closeout

WP10 must now produce its required final report, carry forward the qualified recommendation and warnings, complete the contents/provenance checks, and perform the authorized commit/push and Persian user summary. Those are **remaining closeout obligations**, not reasons to fail already delivered WP0–WP8. The author should update the WP9 disposition table and status only after incorporating this independent review with the other two round-2 reviews.

No additional scientific experiment, extra paper quota, new forecast elicitation, or additional candidate is required by this audit. Do not pad the research package after the remaining closeout requirements pass.
