# WP2 — What RL can and cannot add

Evidence cut-off/access date: 2026-10-30. This is a research synthesis, not an experiment or proof of literature completeness. SOURCE statements below refer to inspected primary texts in the linked cluster dossiers; interpretations are JUDGMENT. Numbers in those cards retain their original task, endpoint, version and comparator. No F6 output was accessed. `PHASE_B_JOURNALS=off` remains in force.

## Result and coverage

**JUDGMENT:** RL is a plausible tool for costly, discrete, feedback-dependent control. Neither “a policy before the encoder” nor “RL against regeneration” is by itself a new contribution. Differentiable optimization, random policies, robust objectives, finite-game solvers and supervised selection are serious competing explanations. The literature does not settle whether a controller can improve this project's fixed reader under its quality and binding requirements at equal total compute.

There are **133 distinct inspected cards** across twelve clusters. The central [search ledger](literature/search-log.md) retains exact queries, counts, index routes and retrieval failures. All discovery was through general web search or direct primary-source opening, not native bibliographic APIs. Valid `site:` searches cover more than five scholarly indexes; malformed `site.domain` strings in C4/C5/C8 are explicitly excluded from restricted-index coverage. Direct opens, within-paper finds and duplicate submissions do not inflate distinct-query counts.

| Cluster | Required | Inspected | Status / evidence |
|---|---:|---:|---|
| C1 watermark/steganography | 15 | 12 | Retrieval-exhaustion exception: 69 exact queries, six indirect indexes, final no-new-accessible batches; [cards and limitations](literature/c1-watermark-stego.md) |
| C2 adaptive attacks | 15 | 15 | [cards](literature/c2-attacks.md) |
| C3 augmentation | 10 | 10 | [cards](literature/c3-augmentation.md) |
| C4 transfer | 15 | 15 | [cards](literature/c4-transfer.md) |
| C5 games | 12 | 12 | [cards](literature/c5-games.md) |
| C6 learned optimization | 8 | 9 | [cards](literature/c6-learned-optimization.md) |
| C7 bandits/personalization | 8 | 8 | [cards](literature/c7-contextual-bandits.md) |
| C8 diffusion/RL | 10 | 10 | [cards](literature/c8-diffusion-rl.md) |
| C9 active verification | 8 | 8 | [cards](literature/c9-verification.md) |
| C10 evaluation/security venues | 10 | 10 | [five methodology cards](literature/c10-reproducibility.md), [five security/attribution cards](literature/c10-security-supplement.md) |
| C11 sim-to-real | 8 | 9 | [cards](literature/c11-sim-to-real.md); eight empirical papers plus one theoretical supplement |
| C12 recent regeneration/transfer | 15 | 15 | [cards](literature/c12-recent.md); last-12-month window and two older-preprint/new-proceedings cases explicitly marked |

C1's exception concerns accessible full text, not absence of work. Four of its cards concern images, eight text/code; that imbalance is a substantive limitation. A separate [priority recovery](literature/priority-recovery.md) tried twelve more SPAR-RL queries and eight SMER queries. Neither manuscript was recovered. The unresolved KAIST handle has not been assigned an invented title. SPAR-RL, ReLOAD, JoPoL, Seek-and-Hide, HFRW, AAMC-RL and the other listed inaccessible leads remain novelty risks. No “first RL watermark” claim is defensible.

## The three meanings of “before the encoder”

**P1: choose a configuration or carrier for this image.** A single choice with terminal feedback is naturally a contextual bandit or supervised selector, even when trained with a policy-gradient estimator. C1's JPEG cost learning and text vocabulary partitioning occupy related one-step decisions. C7's full-information/off-policy literature matters here: when every arm has already been observed, evaluate the actual counterfactual table directly. Importance weighting cannot create missing outcomes for a new writer, and a per-source retrospective oracle is only an upper bound. Payload, clean quality, detector side information and writing cost differ between F5, v5, WAM and VINE; selecting among them changes the method contract.

**P2: distribute a perturbation, bit cost or capacity across regions/frequencies before insertion.** Q-learning block selection, JEC-RL and MCTSteg already occupy the generic idea. Steganalysis evasion has the opposite detection objective from robust ownership verification. The credible unresolved question is whether a constrained spatial allocation preserves a fixed reader's content code after a specified independent regenerator better than matched gradient or discrete optimization. The policy must not obtain privileged post-regeneration feedback at deployment or hide a new decoder inside its state.

**P3: choose transformations, surrogate weights or optimization actions before each encoder call.** This can be sequential if early choices change later perturbations and useful later observations. L2T, adaptive ensembles, learned optimizers and active domain randomization already cover its main ingredients. A dynamic policy must beat fixed/random schedules, momentum, source-only coordinate search, adaptive non-RL scheduling and the same robust loss optimized by gradients. If the only gain is a better loss or more surrogate evaluations, RL has not earned attribution.

The [WP1 decision map](01-decision-map.md) identifies additional attack, verification, curriculum, population and resource-allocation points. Stage P's existing successive halving is not a new RL contribution.

## Evidence that favors trying a bounded controller

**SOURCE:** Relevant positive precedents exist. MCTSteg searches dependent embedding costs; Exposure and AdaptiveISP choose sequential image-processing actions; DRL-FAS compares learned patch selection against random and score-based choices in a TIFS paper. Learned optimization can exploit task structure, and Peng et al. demonstrate recurrent sim-to-real control. These precedents refute an a priori claim that RL can never help a continuous or image-based problem. Their detailed effects and caveats are in C1, C6, C7, C10 and C11.

**JUDGMENT:** The strongest project hypothesis is not direct policy-gradient control of millions of pixels. It is a low-dimensional controller whose feedback changes the value of future actions: allocate scarce surrogate work, stop refinement, switch a discrete operation, or choose a constrained next attack. Repeated deployment might amortize training. To count as Side A, that amortization horizon must be declared before comparison; a cold-start budget must also be reported. To count as Side B, the contribution must be a new information/action structure, a tested mechanism or a rigorous result rather than the optimizer's name.

Positive precedents do not remove three missing links: a learnable reward in this project's data, an advantage over a tuned non-RL algorithm with the same observations, and transfer beyond seen encoder mechanisms. WP3 and WP4 address these links before candidate selection.

## Evidence that weakens broad RL claims

**SOURCE:** RandAugment, TrivialAugment and random architecture search show how simple baselines can erase a policy-search advantage. VeLO assessments show that optimization steps and wall time can rank methods differently. AlignProp and DRaFT exploit pathwise derivatives of diffusion objectives; their gains over score-function methods concern differentiable generator optimization, not proof about this writer. AlignProp's inspected historical manuscript is marked withdrawn/subsumed; no current acceptance is assumed. DomainBed and generalization benchmarks show that specialized robustness/meta-learning may lose to strong ordinary training. C3/C6/C8/C10/C11 retain these negative and mixed comparisons.

**JUDGMENT:** A meaningful experiment must factorially separate action space, representation, reward, sequential feedback and optimizer. Match source images, surrogate access, gradient access, tuning and validation budget. Report training plus search plus evaluation plus deployment cost. An RL model pretrained on the eventual excluded family has already seen that family; renaming the subsequent test “zero-shot” does not repair leakage. Random seeds are not independent model families, and regeneration seeds are not policy-training seeds.

**SOURCE:** Game papers establish useful opponent populations and worst-case objectives, but their convergence results require exact or suitably accurate responses and specified games. Adaptive curricula can concentrate on impossible regions. Sequential verification theory requires valid e-values, confidence sequences or exchangeability assumptions; adaptively maximizing a reader score does not supply them. C5/C9/C11 spell out the assumptions.

**JUDGMENT:** Games and active verification are promising research structures, yet neither increases the physical capacity of a channel that erases the reader-visible signal. A game solver cannot certify security against omitted attack classes, and repeated views cannot be treated as independent Bernoulli trials. Public owner IDs and perceptual consistency are not cryptographic proof of ownership. T4/T5 remain separate endpoints.

## Regeneration and the current no-RL alternatives

**SOURCE:** Adaptive gradient attacks, controlled regeneration, latent-frequency manipulation and learned robust carriers already cover much of the space. DRIFT attacks generation-time diffusion watermarks: its regeneration and verifier-guided strength ladder are non-RL, and an optional DPPO controller refines fidelity after rejection. This occupies a generic RL-assisted refinement mechanism, not demonstrated RL removal of a post-hoc-embedded mark. SPARED combines detector and editing adaptation in an adversarial training loop, making a generic detector/editor game insufficient novelty. AdvMark and other learned carriers provide substantial non-RL robustness precedents. RelZero uses registry-style side information and therefore cannot be represented as a fixed reference-free reader. C2/C8/C12 document those distinctions.

**JUDGMENT:** These works strengthen the case for testing a focused mechanism but weaken a broad application claim. Attack fidelity and clean watermark fidelity must be kept separate: the project's PSNR >35, SSIM >.9, LPIPS <.1 bar concerns the clean marked image. A cited removal attack's lower PSNR is not automatically an inadmissible T3 attack; a prospective attacker study must preregister its own fidelity constraint and compare at matched distortion. Conversely, high VINE survival at a different clean quality/payload does not establish strict-quality dominance over F5.

The pre-existing negative-result article and frozen F6 design remain the no-RL reference routes. This session has neither inspected F6 outcomes nor changed that design. Generic fixed-reader optimization, noise-aware insertion, content binding and registry pointers were already occupied in the earlier TIFS dossier. Any proposed RL route must add something beyond its rejected I02/I04/I08/I10/I11/I12 concepts or clearly state it is a new test of an old idea.

## Novelty map and direct answer

| Proposed claim | Closest inspected evidence | Defensible status now |
|---|---|---|
| First RL image watermark writer | C1 Q-learning image watermarking, JEC-RL, MCTSteg; important uninspected HFRW/SPAR-RL | Occupied as a general claim; specific diffusion/fixed-reader construction unresolved |
| First policy selecting image regions or embedding costs | C1 image methods; C7 image-processing policies | Occupied ingredient; strict-quality transfer benefit still untested |
| First learned pre-encoder transform/surrogate schedule | C4 L2T/AdaEA/BASES; C11 active domain randomization | Occupied ingredient; same-information equal-cost watermark test could be new evidence |
| First RL-assisted fidelity refinement of a diffusion-watermark attack | C12 DRIFT, generation-time target marks | Occupied mechanism; direct evidence for post-hoc-embedded target marks remains unverified |
| First adversarial writer/detector population | C5 PSRO/game literature; C8 SPARED; C1 text co-training | Generic structure occupied; a new binding-aware game requires precise assumptions and evidence |
| RL must outperform gradients for this writer | C3/C6/C8/C10 simple/pathwise baselines | Unsupported; a rigorously matched positive or null comparison remains a possible contribution |
| Source-only policy guarantees arbitrary unseen encoder robustness | C11 limitations and robust-MDP assumptions | Unsupported without a structural assumption; finite excluded-family evidence is narrower |
| Active verification gives free sensitivity at fixed false acceptance | C9 sequential inference/TTA | Unsupported without calibrated sequential error control and charged view cost |

**Direct answer, SOURCE plus bounded JUDGMENT:** this search did **not verify direct full-text evidence of RL writing, selecting or attacking a post-hoc-embedded image mark under diffusion regeneration**. DRIFT is an inspected neighboring precedent: it attacks an already generated image carrying a generation-time diffusion watermark, with optional RL fidelity refinement after non-RL removal. “Post-hoc attack” and “post-hoc embedding” are different settings; §§1, 3.3–3.4 and 5 of its [primary text](https://arxiv.org/html/2609.08213v1) establish that distinction. The inspected C1 papers use RL or bandit-like learning for other image embedding decisions, but do not verify the requested regeneration setting. Nor was the stronger conjunction of fixed-reader/content code, strict clean quality, T4/T5 and a strongest-non-RL equal-total-budget comparison verified. None of these bounded search gaps establishes novelty or absence. The search includes 133 inspected cards, hundreds of logged distinct queries, twelve topic clusters, valid indirect coverage of at least five indexes, 69 C1 queries and a separate bounded recovery attempt. Access failures, malformed operators retained honestly, heterogeneous tasks, preprint-version limits and indirect discovery remain limitations. Novelty is conditional; efficacy is untested.

**WP9 correction:** the original synthesis incorrectly described DRIFT's targets as post-hoc-embedded marks. Card C12-01 already distinguished generation-time targets and optional refinement. The hostile and steelman reviewers independently reopened the primary text; the scope correction does not create a first-use claim or automatically increase a candidate's novelty score.
