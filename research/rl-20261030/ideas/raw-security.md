# WP5 raw ideas: watermark and security framing

2026-10-30. **DIVERGENCE ONLY.** Twenty independent raw hypotheses, all **JUDGMENT**, without scores, ranking, screening, cost elimination or a shortlist. No experiment or policy was run. This author read the supplied WP1–WP4 documents and frozen TD03, not other raw-agent files. F6 outcomes remain unseen; `PHASE_B_JOURNALS=off` applies. Later empirical work needs fresh, disjoint sources; the 60 existing development sources are already assigned.

SOURCE context: [decision map](../01-decision-map.md), [prior art](../02-prior-art.md), [saved-number analysis](../03-logged-analysis.md), [theory](../04-theory.md), and [TD03](../../tifs-20261028/03-ideas.md). Their inspected literature already occupies generic RL diffusion attacks (DRIFT), editor/detector games, embedding-cost learning and generic binding. These are questions about specific mechanisms, not first-use claims. TD03 references below identify overlap, not endorsement of its old rankings or source allocations.

Common security contract: T3 retention, T4 donor transplantation and T5 acceptance of an operationally distinct unmodified target remain separate endpoints. Carrier presence is not exact donor/record attribution. Preserve C/J semantics when retaining F5; explicitly name a new reader when changing them. Clean writer quality and attack-output fidelity are separate constraints. Native/detector queries used during learning are charged; deploying a writer before future regeneration does not grant it future outcomes. Any Q>0 attacker is a prospective extension of the original Q=0 threat, with feedback and access stated. No claim establishes lawful ownership.

## RS01 — Carrier-conditioned transplant-and-regenerate attacker

**Class/point:** R-full; P6. **State/action/feedback:** Start with published marked donor, recipient, current composite, previous permitted reads and remaining fidelity/query budgets. Choose donor region, placement, blend, regeneration step or stop. Feedback separates donor-carrier delivery, exact donor q/record recovery and content acceptance; only their declared conjunction is forgery success.

**Why potentially different from non-RL:** A fixed patch grid followed by one regeneration cannot respond when a previous step delivers the carrier but destroys binding, or vice versa; compare that grid and equally informed beam search. **Biggest unknown:** Whether intermediate feedback predicts a useful next action without consuming the remaining fidelity budget. **TD03 overlap:** I05 directly; the additional hypothesis is useful sequential feedback, not a new laundering threat or first RL diffusion attack.

## RS02 — Adaptive search over unmodified T5 candidates

**Class/point:** R-bandit; P6/P10. **State/action/feedback:** Given a fixed eligible public candidate pool, claimed donor and query history, choose the next unmodified, operationally distinct candidate to query. Reward is verified false donor attribution, with carrier delivery and exact-code status recorded separately. Candidate identity labels belong to evaluation, not privileged policy input.

**Why potentially different from non-RL:** Query results might reveal which semantic neighborhoods are dangerous for this reader beyond the initial nearest-neighbor ordering; compare fixed similarity ranking, stratified random search and supervised ranking. **Biggest unknown:** Whether feedback teaches anything beyond a publicly computable similarity score, especially with rare positives. **TD03 overlap:** I05's T5 negatives and I08's search-budget accounting; editing a candidate would instead create a separately labelled composed attack.

## RS03 — Probe first, then choose a T3 chain

**Class/point:** R-full; P6. **State/action/feedback:** A published marked image and declared black-box feedback define an uncertain carrier/channel state. Choose a small permitted regeneration probe, a subsequent destructive step or stop; retain query outcomes and current fidelity. Training rewards terminal removal and charges both informative unsuccessful probes and successful attacks.

**Why potentially different from non-RL:** An initially weak probe could distinguish mechanisms and improve a later action, unlike greedy strongest-first removal. Compare fixed chains, myopic score descent and explicit Bayesian experimental design. **Biggest unknown:** Whether informative probes exist whose quality cost is recoverable; a hidden family label cannot be supplied for free. **TD03 overlap:** I06's rescue/erasure mechanism; DRIFT already occupies generic RL regeneration/refinement attacks.

## RS04 — Binding-aware population game with separate players

**Class/point:** R-game; P7. **State/action/feedback:** Maintain populations of writers, declared verifiers and T3/T4/T5 adversaries. Add a best response by changing one role at a time. Payoffs retain a vector of genuine acceptance, exact-record forgery, abstention and quality, rather than rewarding carrier presence alone; decoder changes and registry assistance are explicit strategies.

**Why potentially different from non-RL:** A newly found transplant could provoke a verifier response that a removal-only writer/attacker game misses. Compare a finite payoff-table solver, fixed robust training and double oracle without learned responses. **Biggest unknown:** Whether expanding the strategy set discovers reproducible security trade-offs rather than cycling between overfit opponents. **TD03 overlap:** I02/I05/I12; generic adversarial co-training is already occupied, including SPARED.

## RS05 — Public-policy exploitation versus randomized writer commitments

**Class/point:** R-game; P1/P7. **State/action/feedback:** The defender commits to a source-conditioned carrier/configuration policy; the attacker knows its algorithm and observes the published image. Compare deterministic choices with an explicitly randomized policy, including an attacker that infers the realized choice. Matchup feedback is T3 removal or T4/T5 false attribution under the same access.

**Why potentially different from non-RL:** A selector that improves average retention may expose a predictable weakness; equilibrium randomization could change exploitability. Compare a fixed mixture and exact finite minimax solution before learned strategies. **Biggest unknown:** Whether the output itself reveals the action, eliminating the supposed uncertainty. **TD03 overlap:** I01's writer and I05's attacks; randomization is not cryptographic authentication, and its seed secrecy cannot silently become a new security assumption.

## RS06 — Pre-encoder curriculum driven by binding counterexamples

**Class/point:** R-full; P3/P4. **State/action/feedback:** During writing, observe the residual, clean margin, surrogate retention, negative-control margins and remaining quality slack. Choose the next low-dimensional operation: positive T3-surrogate update, T4-transfer counterexample update, T5-separation update, clean repair or stop. Existing pathwise gradients implement each operation; policy feedback is delayed joint C/J and negative behavior on training episodes.

**Why potentially different from non-RL:** Early robustness updates may change which binding constraint becomes active later. Compare a fixed summed loss, constrained gradient optimization and a myopic worst-constraint rule with identical observations. **Biggest unknown:** Whether training negatives expose transferable binding weaknesses rather than teaching rejection of specific pairs. **TD03 overlap:** I01/I11; the question concerns state-dependent constraint ordering, not simply adding a loss or extra optimization.

## RS07 — Low-dimensional carrier allocation with protected content directions

**Class/point:** R-bandit; P2. **State/action/feedback:** From clean-source features, allocate a fixed total residual budget across a small declared set of carrier bands or basis groups, with directions affecting the content descriptor represented separately. One allocation produces one mark; training feedback includes regenerated C/J, T4/T5 and final strict quality. The code itself remains source-derived, not reward-selected.

**Why potentially different from non-RL:** Source context might predict which allocation preserves carrier evidence without making unrelated content acceptable. Compare fixed allocation, differentiable coefficient optimization and low-dimensional Bayesian optimization. **Biggest unknown:** Whether carrier and content sensitivities can actually be separated through native regeneration. **TD03 overlap:** I01/I11; spatial/frequency embedding-cost learning is existing prior art, and decoder-aware basis changes must be disclosed as a new method.

## RS08 — Unequal protection of a fixed verification payload across carriers

**Class/point:** R-bandit; P9. **State/action/feedback:** Given a source and a fixed, fully specified record/authentication payload, choose protection allocation across two carriers, including ECC redundancy and any required selector metadata. State includes only available source features and declared carrier profiles. Reward is exact verified-payload recovery plus binding, not known-message presence.

**Why potentially different from non-RL:** Source-dependent correlated errors could make a universal bit split waste capacity; compare a fixed coding allocation and supervised conditional selection. **Biggest unknown:** Whether the joint channel provides enough payload after coding, metadata and authentication overhead, especially if failures are correlated. **TD03 overlap:** I02/I09 directly. A registry pointer is registry-assisted, and a short arbitrary tag is not a public-key signature. The raw hypothesis is adaptive protection, not generic carrier combination.

## RS09 — Sequential erasure decisions for exact decoding

**Class/point:** R-full; P5/P9. **State/action/feedback:** A newly named reader observes bit reliabilities and partial syndrome information. It chooses another permitted measurement, an erasure pattern, decode attempt or abstention. Training feedback distinguishes exact payload recovery, wrong-payload output and abstention; the whole deployed policy is frozen before calibration.

**Why potentially different from non-RL:** Correlated burst-like bit uncertainty might require deciding which information to acquire before committing an erasure pattern. Compare fixed ECC decoding, reliability-ordered erasures and list decoding at equal work. **Biggest unknown:** Whether reliability patterns retain useful information after regeneration and permit a valid wrong-decode bound under adaptive attempts. **TD03 overlap:** I09; the action cannot increase the carrier's information content or turn a presence threshold into a decoding guarantee.

## RS10 — Active views under an external error-control rule

**Class/point:** R-full; P5. **State/action/feedback:** A new verifier chooses its next semantic/carrier view from previous evidence, remaining work and a fixed error budget. The policy may request observations or stop; acceptance is authorized only by a separately specified valid sequential test or a calibrated full-policy statistic. Training balances true T3 acceptance, false attribution and observation count.

**Why potentially different from non-RL:** Different disagreements could call for different next views; compare fixed prefixes, a cheap-to-expensive cascade and optimal stopping on the same state. **Biggest unknown:** Conditional null validity with highly dependent views of one image; repeated reads are not independent trials. **TD03 overlap:** I08/I12. The proposed contribution would be efficient evidence acquisition subject to validity, not an RL-chosen permissive threshold.

## RS11 — Registry interrogation that resolves competing records

**Class/point:** R-full; P10/P5. **State/action/feedback:** With explicitly trusted registry access, start from a fixed candidate-retrieval procedure. Choose which enrolled record and descriptor channel to inspect next, or abstain. State contains observed comparisons and remaining candidates; reward is correct record identification with calibrated error and charged lookup cost. Registry contents remain fixed.

**Why potentially different from non-RL:** The most useful next descriptor may depend on which rival records remain plausible. Compare a fixed descriptor cascade, exhaustive comparison and greedy information gain. **Biggest unknown:** Whether source-disjoint calibration remains valid after adaptive candidate selection and across roster sizes. **TD03 overlap:** I12 directly, plus I08's multiplicity. Trusted enrollment and stored descriptors are added side information; performance cannot be labelled reference-free F5 verification.

## RS12 — Detector feedback disclosure as a security game

**Class/point:** R-game; P5/P6/P7. **State/action/feedback:** Hold the internal verification rule fixed while choosing the public feedback channel: binary output, calibrated coarse bins or richer scores, possibly as a fixed transcript-dependent protocol. Adaptive T4/T5 attackers optimize against each channel with the same query allowance; legitimate task completion and attacker success are separate payoffs.

**Why potentially different from non-RL:** Strategic query sequences may exploit score precision differently from one-shot attacks. Compare fixed disclosure protocols and a finite game solution. **Biggest unknown:** Whether any practical security gain survives an attacker trained specifically against the restricted feedback. **TD03 overlap:** I05/I08. Less feedback changes the access contract; it must not be advertised as an algorithmic improvement under unchanged information or as security against unlimited queries.

## RS13 — Active factorial diagnosis of writer, carrier and reader bottlenecks

**Class/point:** R-bandit; P8. **State/action/feedback:** Maintain explicit competing explanations of failure: writer objective, carrier representation, decoder mismatch or clean-quality feasibility. Select the next permitted writer/carrier/reader swap on fresh development sources; update from the complete retention, exact decoding, negative and quality vector. Reward is reduction in uncertainty about those prespecified explanations, not discovery of favorable outcomes.

**Why potentially different from non-RL:** One observation can change which intervention distinguishes the remaining explanations. Compare a fixed factorial design and classical optimal experimental design. **Biggest unknown:** Whether interventions isolate those mechanisms rather than jointly changing payload, access and quality. **TD03 overlap:** I03/I06/I09. This is an experiment-efficiency hypothesis, not a claim to improve watermark survival or a license to omit unfavorable cells.

## RS14 — Adaptive attack discovery with valid target-risk estimation

**Class/point:** R-bandit; P8/P6. **State/action/feedback:** From a prospectively defined finite target distribution over eligible T4/T5 units, adapt sampling toward suspicious strata while keeping recorded positive selection probabilities. Each query provides a failure indicator and its sampling history. The objective is both attack discovery and precision of a separately valid weighted risk estimate.

**Why potentially different from non-RL:** Rare failures might cluster in learnable strata, allowing better precision than uniform sampling without pretending selected attacks are population-random. Compare fixed stratification and non-RL adaptive importance sampling. **Biggest unknown:** Support coverage and extreme weights may erase the benefit; adaptive uncertainty calculations must match the design. **TD03 overlap:** I05/I08. Finding many attacks and estimating their target-population rate are distinct outputs.

## RS15 — Least-favorable legitimate/forged observation-pair game

**Class/point:** R-game; P6/P7. **State/action/feedback:** One generator selects allowed T3 transformations of a genuine source; another selects operationally distinct unmodified T5 targets or separately labelled T4 constructions. A verifier responds using a fixed declared observation interface. Reward encourages conflicting truth labels with equal or tightly controlled reader observations; exact collision witnesses are retained.

**Why potentially different from non-RL:** Alternating best responses could expose observation conflicts missed by nearest-neighbor search. Compare exhaustive finite pairing and direct constrained optimization. **Biggest unknown:** Whether meaningful equal-observation conflicts exist under valid identity labels and fidelity. **TD03 overlap:** I07 directly. A discriminator's failure is not an upper bound on total variation; only actual witnesses or separately justified distributional assumptions support a ceiling, scoped to that observation interface.

## RS16 — Low-dimensional quantization-phase selection before encoding

**Class/point:** R-bandit; P3/P4. **State/action/feedback:** Choose a small vector of declared quantization/dither phases for residual initialization and saved-RGB8 reconciliation before surrogate encoding. State includes source statistics and clean rounding sensitivity; training feedback uses final saved pixels, native C/J and negatives. Any information required by decoding is fixed or carried with its overhead counted.

**Why potentially different from non-RL:** Discrete rounding could make phase choice source-dependent even when continuous residual gradients look similar. Compare fixed phase, exhaustive small-grid search and straight-through/pathwise optimization. **Biggest unknown:** Whether phase effects persist through regeneration rather than only repairing a clean numerical artifact. **TD03 overlap:** I11's quantization/interference issue. This is a small-action hypothesis, not a claim that dither or quantization-aware optimization is new.

## RS17 — Owner-conditioned reader-subspace inference for T4

**Class/point:** R-full; P6. **State/action/feedback:** Under an explicitly stronger Q>0 access model, use published donors, recipients, allowed patch/basis perturbations and queried owner-conditioned responses to infer an effective detection direction. Choose informative probes before attempting a donor-attributing transplant. No private clean-donor residual or signing key is provided.

**Why potentially different from non-RL:** A probe useful for inferring the reader may not immediately increase forgery score; compare a fixed probe design, regression-based reconstruction and SPSA/NES with the same calls. **Biggest unknown:** Whether the inferred direction generalizes to new recipients and passes the content gate. **TD03 overlap:** I05's stronger-access diagnostics and I08's query accounting. The issue is learned effective response, not automatically recovery of a cryptographic secret; F5's public owner labels must stay public in the account.

## RS18 — Content-code feature acquisition before committing the code

**Class/point:** R-full; P1/P9. **State/action/feedback:** In a newly named writer/reader pair, sequentially choose descriptor components or quantizers from a public fixed menu, then commit the content code by a deterministic rule. State contains measured source features and remaining payload budget; training rewards exact recovery after T3 and rejection of defined T4/T5 alternatives. Selection metadata and reproducibility by the verifier are explicit.

**Why potentially different from non-RL:** Early feature observations could reveal which later components separate real near-copies while remaining stable under regeneration. Compare a fixed feature set and supervised information-bottleneck/greedy selection. **Biggest unknown:** Whether the verifier can recover the selection without circular dependence or prohibitive overhead. **TD03 overlap:** I02/I09/I12; generic semantic binding is occupied, and choosing an easier arbitrary payload from attack outcomes is excluded.

## RS19 — Writer-side abstention with declared coverage

**Class/point:** R-bandit; P1. **State/action/feedback:** Before publication, choose a permitted writer configuration or explicitly decline to provide the specified security claim for that source. State uses genuinely available predecision features; training outcomes include strict quality, T3 retention and T4/T5 behavior. Optimize a preregistered utility with a minimum coverage requirement and count every declined source.

**Why potentially different from non-RL:** Source-specific feasibility prediction might allocate a limited marking budget or avoid unsupported guarantees more effectively than one universal writer. Compare a calibrated fixed reject rule and supervised selective prediction at identical coverage and information cost. **Biggest unknown:** Whether features predict differential secure feasibility rather than simply easy-source survival. **TD03 overlap:** I12's selective-verification principle, moved to the writing decision. This changes coverage and cannot substantiate an all-source improvement.

## RS20 — Active counterclaim interrogation without a registry

**Class/point:** R-full; P5. **State/action/feedback:** A new reference-free verifier receives the suspect and claimed owner, then chooses public counterclaim/decoy-owner reads from a fixed roster. Its state is the vector of responses and remaining work. Training asks whether the claimed response is specifically attributable or merely part of broad cross-owner activation; terminal decisions use a separately calibrated full-policy rule.

**Why potentially different from non-RL:** Different response patterns could call for different counterclaims, reducing work relative to reading every roster entry. Compare fixed decoys, exhaustive roster reading and a greedy discriminative rule. **Biggest unknown:** Whether counterclaim patterns distinguish genuine regenerated marks from transplants without losing genuine acceptance, particularly for attacker-chosen owners. **TD03 overlap:** I08 and I05. Chosen owners are not automatically random-key nulls, and the roster is added public side information even though no enrolled image is used.
