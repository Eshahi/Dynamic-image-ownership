# Raw ideas from an RL theorist

2026-10-30. **WP5 divergence only.** All twenty entries are **JUDGMENT: prospective hypotheses**, not measured effects, novelty determinations, scores or recommendations. Order is by policy point followed by two broader method changes, not merit. No candidate has been screened, ranked or eliminated. The later committed screening rule should decide those questions.

Read: the authoritative MAIN `STATE.md` once, plus `BRIEF.md`, `01-decision-map.md`, `02-prior-art.md`, `03-logged-analysis.md` and `04-theory.md`. No other raw-agent output was read. No science ran; no F6 output, Phase B per-source journal, image, reserve identifier or Stage C identifier was opened. The approved F6 package remains frozen. All prospective training, tuning and testing below require newly authorized, fresh disjoint sources: the existing sixty development sources are already assigned.

For writer ideas, reward means the declared C/J endpoint under separately enforced strict clean quality and T4/T5 requirements; generic carrier score alone is insufficient. A soft shaping signal would need independent validation against that endpoint. An altered reader, payload or registry contract is stated where relevant. For attacks, removal/false acceptance and attack-output fidelity have their own declared objectives. All observations, native probes, training and deployment work must eventually be matched with the comparator. These are common definitions, not a screening result.

## RT01 — Contextual selection of a robust operating point

- **Class / point:** R-bandit; P1, before marking.
- **State, action, feedback:** Source-only features and a deployment-declared threat mixture; choose one configuration from a newly defined menu of quality budgets and carrier shapes; later receive its C/J and constraint outcomes. No future regenerator identity is given to the selector.
- **Why it could differ:** A contextual bandit can learn differential action value when only the selected configuration is evaluated, whereas a fixed configuration ignores conditional tradeoffs. With full information, a supervised selector is the natural additional comparator.
- **Biggest unknown:** Whether the new menu has source-dependent action advantages; predictability of survival alone is insufficient. A possible mechanism is conditional robustness rather than a generally superior arm.

## RT02 — Learn which pre-mark probe is worth acquiring

- **Class / point:** R-full; P1, with P3 observations.
- **State, action, feedback:** A belief about this source's channel sensitivity, updated only from permitted writer-side probes; choose another surrogate/encoder probe or commit to a writer configuration. Terminal feedback includes native C/J and total observation cost.
- **Why it could differ:** The useful second probe can depend on the first answer. A policy can jointly learn information acquisition and the downstream decision, instead of buying every probe or using a fixed probe order. Compare with greedy information gain and Bayesian experimental design.
- **Biggest unknown:** Whether inexpensive pre-mark observations distinguish which configuration will work, rather than merely identifying difficult sources. The potential contribution is a measurable value of adaptive information before insertion.

## RT03 — Sequential allocation with an explicit remaining distortion budget

- **Class / point:** R-full; P2, before encoder calls.
- **State, action, feedback:** Existing reader-slot margins, region/band statistics and remaining quality budget; allocate another perturbation increment to one legal region-band group or stop. Allocation changes later margins and the budget available to other groups; terminal C/J supplies delayed feedback.
- **Why it could differ:** A locally unhelpful allocation could enable a later compatible allocation when regions interact. Compare with water-filling, projected gradient masks and discrete coordinate search using the same measurements.
- **Biggest unknown:** Whether these interactions are strong and learnable enough to reward planning. This version changes energy allocation inside an agreed reader layout, without silently requiring an unknown layout at detection.

## RT04 — Allocate protection against correlated bit failures

- **Class / point:** R-full; P2/P9; explicitly a possible new code/reader contract.
- **State, action, feedback:** Partial allocation of a fixed semantic payload, predicted joint bit-error structure and remaining redundancy; choose which bit group to repeat, interleave or place in a distinct carrier component. Feedback is recovery of the intended bound code after regeneration, not average bit accuracy alone.
- **Why it could differ:** The best next redundancy unit can depend on earlier allocation because a burst can erase several jointly protected bits. Compare with fixed error-correcting codes, analytic unequal protection and combinatorial optimization.
- **Biggest unknown:** Whether a transferable joint-error model exists and whether the reader can identify the layout without fragile metadata. Any extra layout signaling or side information is part of the method, not free capacity.

## RT05 — Dual control of surrogate fidelity and writer progress

- **Class / point:** R-full; P3.
- **State, action, feedback:** Current mark, surrogate losses and uncertainty about local surrogate/native disagreement; choose a cheap surrogate update, a higher-fidelity probe or a native check on the current candidate. Checks update the belief; updates change the image. Terminal C/J is the target.
- **Why it could differ:** A probe has value through improving later decisions, even when it does not immediately improve the mark. Compare with fixed probe intervals, multi-fidelity Bayesian optimization and model-predictive control with the same native-check access.
- **Biggest unknown:** Whether observed disagreement predicts how to correct the next updates. Deployment checks concern permitted known channels, never the unknowable future attack or an excluded-family test result.

## RT06 — Schedule surrogate blocks to exploit noncommuting updates

- **Class / point:** R-full; P3.
- **State, action, feedback:** Recent per-family margins, gradient alignment and trajectory history; select a surrogate family/timestep and a block length before reconsidering. The action changes the next residual and therefore later gradient directions; final native C/J is delayed reward.
- **Why it could differ:** A beneficial order could move through a basin that simultaneous averaged gradients cannot reach. Compare with fixed/random schedules, gradient-conflict weighting and an equally informed myopic scheduler.
- **Biggest unknown:** Whether order has a reproducible causal effect beyond unequal gradient counts or better average surrogate weights. The potential scientific contribution is history-dependent optimization, tested by state/history ablations rather than the optimizer's name.

## RT07 — Learn a sequence of encoder input coordinate systems

- **Class / point:** R-full; P3, a literal pre-encoder policy.
- **State, action, feedback:** Current perturbation, local robustness margins and previous transform responses; choose an allowed invertible coordinate transform, differentiate through its encoder path, then map the update back. Actions might include resampling phase or reversible channel/basis mixing; terminal feedback remains native C/J on the final untransformed image.
- **Why it could differ:** The transform changes which encoder sensitivities are exposed, and the useful next transform may depend on previous updates. Compare with fixed transform ensembles, random schedules and discrete search.
- **Biggest unknown:** Whether transformed gradients reveal useful native-channel directions or merely optimize unrealistic inputs. These transforms are writer operations, not extra T1/T2 threat endpoints.

## RT08 — Learn when a writer trajectory is no longer worth continuing

- **Class / point:** R-full; P4.
- **State, action, feedback:** Current margins, gradient history, quality slack and remaining budget; continue, switch to refinement, restart or finalize. Restart destroys some progress; finalization commits the image. Reward combines terminal C/J with a separately reported resource objective.
- **Why it could differ:** Slow early improvement may precede a useful basin, while a high local margin may conceal transfer failure. A history-dependent value function could outperform fixed iteration counts. Compare with fixed early-stop rules, sequential improvement tests and non-RL restart allocation.
- **Biggest unknown:** Whether trajectory observations predict future native improvement. A policy that merely learns a shorter constant schedule would support the schedule change without establishing a sequential RL contribution.

## RT09 — Plan robustness updates inside a constrained safe set

- **Class / point:** R-full; P4.
- **State, action, feedback:** Robust and content-binding margins, quality slack and their recent responses; choose a discrete update direction/mixing rule or a repair step. A feasibility controller rejects invalid final outputs; delayed reward is feasible C/J, with violations recorded separately.
- **Why it could differ:** A temporary sacrifice in one local margin might enable later robustness while preserving final constraints. Compare with constrained optimization, primal-dual weighting and backtracking using the same observations.
- **Biggest unknown:** Whether the available state predicts constraint recovery well enough for useful planning. The possible result concerns a constrained reachable set; no claim is made that an approximate local safety check certifies final perceptual quality or T4/T5 security.

## RT10 — Active verification under a valid error budget

- **Class / point:** R-full; P5; explicitly changes the verification procedure.
- **State, action, feedback:** Previous suspect-image measurements, candidate code hypotheses and the remaining statistical error budget; choose the next semantic view/measurement, reject, abstain or accept only through a valid calibrated rule. Feedback during training is correct attribution and observation cost.
- **Why it could differ:** Different early ambiguities can call for different later observations. Compare with fixed prefixes, cheap-to-expensive cascades and a myopic information rule.
- **Biggest unknown:** Whether useful adaptivity remains after controlling false acceptance under dependent views and adaptive stopping. The potential contribution is a policy-plus-valid-test construction, not threshold optimization or an assumed independence of repeated views.

## RT11 — A partially observed regeneration attacker

- **Class / point:** R-full; P6/T3, under a prospectively declared detector-query variant.
- **State, action, feedback:** Current published marked image, permitted reader feedback, measured attack fidelity and remaining query budget; choose regenerator/strength/prompt, preserve a previous candidate or stop. Each accepted regeneration changes the physical state and later attack possibilities.
- **Why it could differ:** Early calls can identify which kind of residual signal survives and enable a tailored next call. Compare with a fixed chain, exhaustive shallow search, beam search and model-predictive control at matched access.
- **Biggest unknown:** Whether useful sequential adaptation exists after matching fidelity and total queries. Generic RL regeneration attack novelty is not assumed; the mechanism here is partial observability and the information value of feedback.

## RT12 — Learn a donor-to-recipient forgery assembly

- **Class / point:** R-full; P6/T4, with an explicit query-access contract.
- **State, action, feedback:** Public donor and recipient, the current composite, allowed reader feedback and remaining fidelity budget; choose a donor patch, placement, blending action or rollback. Reward is donor-instance false acceptance on an operationally different recipient under the declared constraint.
- **Why it could differ:** Individually ineffective patches could cooperate, so the value of the next placement depends on previous placements. Compare with a patch grid, greedy placement, beam search and any access-matched gradient attack.
- **Biggest unknown:** Whether the reader admits compositional forgery paths. Neither the private clean donor residual nor evaluator ground-truth identity becomes attacker state; stronger access would define a separately labeled diagnostic.

## RT13 — A bandit that explores semantic collision neighborhoods

- **Class / point:** R-bandit; P6/T5, under a declared query budget.
- **State, action, feedback:** Public descriptors of an eligible candidate pool and previous allowed detector replies; query the next target/neighborhood. The underlying targets stay fixed; feedback is the declared acceptance signal, while evaluators separately establish distinct-instance truth.
- **Why it could differ:** A query may reveal which semantic directions cause a code collision and change the value of querying related candidates. Compare with nearest-neighbor ranking, randomized matched candidates and supervised collision-risk ranking.
- **Biggest unknown:** Whether detector replies contain generalizable information about unqueried candidates. This is adaptive search under partial feedback, not a long-horizon image-control claim; the potential outcome is a query-conditioned security curve.

## RT14 — Hidden writer randomization against an observing attacker

- **Class / point:** R-game; P7 with P1 actions.
- **State, action, feedback:** Writer sees the clean source and samples a compatible configuration; attacker sees the published image and the public strategy distribution but not the sampled action. Learned attacker responses produce T3/T4/T5 payoffs under separate constraints.
- **Why it could differ:** Randomization may remove the attacker's ability to choose a single specialized response. Compare with one fixed writer, an exact finite minimax mixture and double-oracle optimization without learned responses.
- **Biggest unknown:** Whether the configuration remains inferable from the published image and whether a useful information advantage survives. Randomization is not a secret-key substitute; a publishable game claim would need an explicit information structure and evidence beyond solving a small payoff matrix.

## RT15 — Separate removal and forgery adversaries in a vector-payoff game

- **Class / point:** R-game; P7 with P2/P9 writer actions.
- **State, action, feedback:** A population of compatible writers, a T3-removal adversary and separate T4/T5-forgery adversaries; train or select new responses against the current mixtures. Keep survival, binding failures and quality as separate constrained payoffs.
- **Why it could differ:** A robustness improvement that helps a removal adversary less may expose a forgery response; the opponent population can reveal this moving tradeoff. Compare with fixed robust objectives, finite constrained games and robust optimization over the same accumulated attacks.
- **Biggest unknown:** Whether new responses expose meaningful strategic interactions rather than merely filling a static benchmark. No weighted average may hide a binding failure, and security is claimed only against the specified response classes.

## RT16 — Allocate experiments to learn action differences, not source difficulty

- **Class / point:** R-bandit; P8.
- **State, action, feedback:** A posterior or confidence set for source-feature-by-action interactions on fresh development sources; choose the next source stratum, action pair or regeneration cell to evaluate. Paired feedback updates which policy decision is uncertain.
- **Why it could differ:** Uniform testing can spend work estimating already-known arm means while leaving the policy boundary uncertain. Compare with fixed stratification, optimal experimental design, Neyman allocation and ordinary racing.
- **Biggest unknown:** Whether interaction-directed allocation improves final decision quality after charging all exploration. The target is learning differential action value with honest sampling probabilities; this is distinct from renaming the existing Stage P successive halving or selectively reporting easier sources.

## RT17 — Learn the repair order of interacting robust and fragile carriers

- **Class / point:** R-full; P9/P4.
- **State, action, feedback:** Current robust-code, fragile-code and content-consistency margins plus quality slack; choose which carrier to repair, how long to refine, whether to quantize and re-read, or when to stop. Each operation can disturb the other carrier; final C/J and binding outcomes arrive after the complete sequence.
- **Why it could differ:** A noncommuting repair order could preserve a joint operating point that an alternating fixed schedule misses. Compare with fixed orders, coordinate descent and a myopic most-violated-margin rule.
- **Biggest unknown:** Whether the interference has stable structure and matters to native survival. This is a scheduling hypothesis over explicitly declared carriers, not a presumption that generic carrier combination is new or that current failure is caused by interference.

## RT18 — Policy-guided registry retrieval with candidate-aware verification

- **Class / point:** R-full; P10/P5; explicitly uses trusted enrolled-record side information.
- **State, action, feedback:** Suspect descriptors, the current candidate-record set, acquired record comparisons and remaining query/error budgets; acquire another descriptor, refine retrieval, compare a record, abstain or stop. Feedback is correct record attribution, false acceptance and total lookup cost.
- **Why it could differ:** Ambiguity among candidates can determine which descriptor is most informative next. Compare with fixed descriptor order, approximate nearest-neighbor retrieval and greedy entropy reduction.
- **Biggest unknown:** Whether adaptive retrieval adds useful information after candidate-set multiplicity and correlated near-duplicate errors are controlled. The possible contribution concerns information acquisition and valid attribution with a registry; it does not establish lawful ownership or a reference-free detector.

## RT19 — Learn a discrete communication protocol jointly with its reader

- **Class / point:** R-game; P2/P9/P5; explicitly replaces the carrier and reader.
- **State, action, feedback:** A sender sees the clean source and a mandatory owner/content payload; it selects discrete perceptual code atoms. A receiver sees only the transmitted/regenerated image and declared public/key information, then chooses evidence and decodes. A constrained attacker supplies separate T3/T4/T5 challenges. Exact payload recovery and correct binding determine the cooperative payoff.
- **Why it could differ:** Joint learning could discover a carrier/reader agreement inaccessible to optimizing the fixed F5 score, while discrete code decisions can be trained against native black-box channels. Compare with a differentiable communication autoencoder, supervised codebook learning and fixed adversarial training.
- **Biggest unknown:** Whether a jointly learned protocol generalizes across messages, sources and channels without learning an easily copied owner token. The payload cannot be selected for convenience; protocol learning does not itself supply cryptographic authenticity or ownership proof.

## RT20 — Insert sparse latent pulses along an actual reconstruction trajectory

- **Class / point:** R-full; P2/P3 extended to an actual latent writer, rather than an image-domain comparator.
- **State, action, feedback:** During reconstruction of the original image, observe the current latent, predicted clean image, fixed payload and remaining fidelity budget; choose a timestep/subspace in which to inject a code-conditioned latent pulse, defer insertion or stop. Later denoising transports or erases earlier pulses; terminal feedback evaluates final quality, declared reader recovery and T3/T4/T5 behavior.
- **Why it could differ:** Insertion timing and subsequent denoising form a genuine controlled trajectory with delayed consequences. Compare with fixed latent insertion, backpropagation through the trajectory and non-RL optimal control using identical model access.
- **Biggest unknown:** Whether any such trajectory retains the intended source tightly enough while leaving a transferable readable signal. It is a new latent-method hypothesis with an explicit reader contract, never a relabeling of F5 or an amendment to frozen F6.

## Handoff boundary

These are independent raw proposals for later consolidation. No novelty search beyond the supplied synthesis, cost elimination, candidate scoring, shortlist, probability elicitation or experiment selection was performed here. A future positive result must isolate the claimed mechanism—context, information acquisition, action order, correlated failures or strategic response—from a stronger objective, extra observations and extra compute.
