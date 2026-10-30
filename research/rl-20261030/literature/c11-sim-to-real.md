# C11 — Sim-to-real, domain randomization, and excluded-family transfer

Date: 2026-10-30. Researcher: Codex C11 sub-agent. Scope: WP2 literature only; no experiment, implementation, outcome inspection, or compute recommendation has been executed. Nine primary full texts were opened and their methods plus evaluations or proofs inspected. Status is **FULLTEXT_WEB_INSPECTED**, not locally downloaded/checksum-verified. No bibliography validator was run. Paper claims, author interpretations, project inferences, and open assumptions are distinguished below. Numerical results are from the specified versions, not from search snippets or later revisions.

## Main finding and boundary

**Project inference:** domain randomization and adaptive policies offer a plausible development hypothesis, but these papers do not establish that training on three or four regeneration families transfers to a genuinely excluded independently trained encoder. Randomization is not uniquely RL, and useful transfer depends on what varies, what information the policy receives, and what the target shares with training. Positive robotic transfer is relevant evidence for possibility; it is not a watermarking success probability.

The proposed setting remains a fixed SD1.5 VAE reader, posthoc marking of existing images, and continuous bounded perturbations. F6 is treated only as the frozen, pre-outcome surrogate-PGD specification: R0.2/R1.1/R1.2, normalized gradients, 60 older development sources. No F6 result is used. A new mechanism would still have to satisfy strict clean PSNR > 35 dB, SSIM > .9 and LPIPS < .1, semantic C, content-binding J, and T4/T5 negatives. None of the papers below measures that conjunction.

## Actual search ledger

All searches occurred on 2026-10-30 through the web search tool. **Site-restricted searches are indirect web searches, not native queries submitted to the named index.** Fourteen actual queries are recorded verbatim, including unsuccessful and locator queries; twelve are site-restricted across five scholarly hosts. Paper links were subsequently opened; bibliography/search hits alone are not counted as inspected papers.

| ID | Exact query | Search surface and outcome |
|---|---|---|
| Q01 | `site:arxiv.org "Domain Randomization for Transferring Deep Neural Networks" Tobin` | Indirect arXiv search; located C11-01. |
| Q02 | `site:arxiv.org "Sim-to-Real Transfer of Robotic Control with Dynamics Randomization"` | Indirect arXiv search; located C11-02. |
| Q03 | `site:openreview.net "EPOpt: Learning Robust Neural Network Policies Using Model Ensembles"` | Indirect OpenReview search; located C11-03, but OpenReview PDF presented a browser challenge; arXiv full text used. |
| Q04 | `site:proceedings.mlr.press "Quantifying Generalization in Reinforcement Learning"` | Indirect PMLR search; located C11-06. |
| Q05 | `site:proceedings.mlr.press "Leveraging Procedural Generation to Benchmark Reinforcement Learning"` | Indirect PMLR search; located C11-07. |
| Q06 | `site:openreview.net "In Search of Lost Domain Generalization"` | Indirect OpenReview search; initial response did not locate intended result. |
| Q07 | `site:openreview.net "In Search of Lost Domain Generalization" Gulrajani` | Indirect OpenReview search; located C11-08; inspected arXiv version separately. |
| Q08 | `site:proceedings.mlr.press "Active Domain Randomization"` | Indirect PMLR search; located C11-04. |
| Q09 | `site:arxiv.org "Assessing Generalization in Deep Reinforcement Learning"` | Indirect arXiv search; located C11-05. |
| Q10 | `site:dblp.org "Robust Control of Markov Decision Processes with Uncertain Transition Matrices"` | Indirect DBLP search; publication metadata for C11-09, not full-text evidence. |
| Q11 | `site:ieeexplore.ieee.org "Sim-to-Real" "Dynamics Randomization"` | Indirect IEEE Xplore search; C11-02 publication record/DOI and additional uninspected leads. |
| Q12 | `site:proceedings.mlr.press "domain randomization" "theory" "sim-to-real"` | Indirect PMLR search; additional leads including invariant-policy work; not counted as inspected. |
| Q13 | `"EPOpt" arxiv 1610` | Unrestricted locator search after OpenReview access challenge; C11-03 full text. |
| Q14 | `"Nilim" "Ghaoui" robust 2005 pdf` | Unrestricted locator search; C11-09 Berkeley author-hosted draft. |

This is a bounded cluster search, not evidence that the literature is exhausted or that no newer direct watermarking paper exists. In particular, the oldest foundational studies establish occupied concepts and transfer limitations; they cannot support a current “first RL watermarking” claim.

## Full-text paper cards

### C11-01 — Domain Randomization for Transferring Deep Neural Networks from Simulation to the Real World

**Metadata:** Josh Tobin, Rachel Fong, Alex Ray, Jonas Schneider, Wojciech Zaremba, Pieter Abbeel; IROS 2017. Inspected arXiv:1703.06907v1, 20 March 2017, [full text](https://arxiv.org/pdf/1703.06907v1); accessed 2026-10-30. Read §§III–IV, randomization/training procedure, real-image evaluation and ablations.

**Classification/mechanism:** non-RL supervised visual localization. RGB images are inputs and object coordinates are predictions; no policy state/action/reward or decision horizon applies. An L2-trained CNN sees randomized textures, lighting, camera parameters, objects and noise. Randomization does not require reinforcement learning.

**Direct evidence:** evaluation uses 480 real webcam images, eight objects with 60 images each. Average real localization error is about 1.5 cm versus 0.3–0.5 cm in simulation. Ablations compare rendering variation and training choices; the table-plane setup constrains the localization problem. These are localization errors, not a measured RL advantage.

**Project inference:** source randomization is an already-established non-RL transfer mechanism. This pre-empts novelty based simply on training under varied regeneration conditions and motivates ordinary randomized-loss optimization as a comparator. Variation among rendering nuisances does not demonstrate that perturbations readable through one VAE survive another independently trained VAE. **Open assumption:** the randomized surrogate distribution must preserve some target-relevant signal; this paper does not identify such a signal for watermarking.

### C11-02 — Sim-to-Real Transfer of Robotic Control with Dynamics Randomization

**Metadata:** Xue Bin Peng, Marcin Andrychowicz, Wojciech Zaremba, Pieter Abbeel; ICRA 2018, DOI 10.1109/ICRA.2018.8460528. Inspected arXiv:1710.06537v3, 3 March 2018, [full text](https://arxiv.org/pdf/1710.06537v3); accessed 2026-10-30. Read §§IV–V and Tables I–III.

**Classification/mechanism:** full RL, recurrent deterministic policy gradients with hindsight replay. The 52-dimensional observation describes robot/puck state; seven actions adjust joint angles; goal reward is 0 on success and −1 otherwise. Training episodes have 100 control steps, real evaluation 200. Randomized dynamics train a recurrent controller that receives execution feedback.

**Direct evidence:** Table II reports real success .89 ± .06 for LSTM, .67 ± .14 for randomized feedforward, and 0 for nonrandomized feedforward, with respectively 28, 12 and 10 physical trials. Simulation scores are .91, .83 and .51. Small real trial counts limit precision.

**Project inference:** this is a strong positive example of useful recurrent transfer, but recurrent history can reveal the physical target during operation. A writer acting before an unknown future regenerator cannot obtain that same target feedback. It pre-empts generic “RL plus dynamics randomization transfers” novelty, while leaving open whether source-only sequential optimization yields information unavailable to matched PGD.

### C11-03 — EPOpt: Learning Robust Neural Network Policies Using Model Ensembles

**Metadata:** Aravind Rajeswaran, Sarvjeet Ghotra, Balaraman Ravindran, Sergey Levine; ICLR 2017. Inspected arXiv:1610.01283v4, 3 March 2017, [full text](https://arxiv.org/pdf/1610.01283v4); accessed 2026-10-30. Read §§2–4, especially 3.1–3.2/4.2–4.4, and Appendix A.2/A.5/Table 2.

**Classification/mechanism:** full RL. Continuous locomotion observations drive joint controls; reward is task locomotion return over 1,000 steps. TRPO updates use the lowest-return fraction of trajectories sampled from a source-model ensemble, approximating a CVaR objective; a separate adaptation component updates the ensemble using target observations.

**Direct evidence:** Hopper Table 2 compares ε=.1 against ε=1: tenth-percentile return 2,848 versus 1,354; mean return 3,063 versus 3,224. Thus robustness trades some mean return for lower-tail improvement. Testing omitted mass variation helps but is less robust than training with it; the simulator's underlying task remains shared.

**Project inference:** lower-tail/worst-surrogate training is occupied territory, and the same objective can drive non-RL differentiable PGD. Source-ensemble robustness is not a bound on arbitrary excluded encoders. Target-informed adaptation would change the proposed zero-shot information contract. **Open assumption:** an excluded regenerator must share enough structure with the source ensemble for tail optimization to remain relevant.

### C11-04 — Active Domain Randomization

**Metadata:** Bhairav Mehta, Manfred Diaz, Florian Golemo, Christopher J. Pal, Liam Paull; CoRL 2019, PMLR 100 (2020), 1162–1176. Inspected [proceedings full text](https://proceedings.mlr.press/v100/mehta20a/mehta20a.pdf); accessed 2026-10-30. Read §§2–5.1, Algorithm 1, and Appendices C/F/H.

**Classification/mechanism:** full RL at two levels. An SVPG sampler observes simulator parameters, moves them with bounded continuous actions, and receives discriminator-based rollout-difference rewards; particles reset every 50 steps. The inner DDPG controller receives physical task state, takes control actions, and earns task reward; episodes last 1,000 or 100 steps depending on task.

**Direct evidence:** comparison is uniform domain randomization, not non-RL watermark optimization. ADR wins all but one reported Pusher test region; exact plotted margins were not safely extracted. A concrete negative finding is degeneracy when engine-strength sampling spans [6,20]; values below approximately 8 make landing nearly impossible. Restricting training to [8,20] corrects this failure. Pusher training uses [.67,1] times default parameters and testing [.5,.67].

**Project inference:** learned surrogate scheduling is already established. Sampling ranges and feasibility determine what the adversarial curriculum can teach. This supports studying a scheduler only if impossible watermark/quality regions are handled explicitly; it supplies no excluded-encoder guarantee and no evidence that RL beats differentiable non-RL allocation under equal total cost.

### C11-05 — Assessing Generalization in Deep Reinforcement Learning

**Metadata:** Charles Packer, Katelyn Gao, Jernej Kos, Philipp Krähenbühl, Vladlen Koltun, Dawn Song; 2018 preprint, revised 2019. Inspected arXiv:1810.12282v2, 15 March 2019, [full text](https://arxiv.org/pdf/1810.12282v2); accessed 2026-10-30. Read §§4–7 and Tables 1–2. No peer-reviewed venue is asserted here.

**Classification/mechanism:** full RL benchmark: A2C/PPO, robust EPOpt and recurrent meta-RL RL². States are physical observations; actions are discrete forces or continuous controls; rewards are native control-task objectives; limits span 200/500/1,000 steps. Training and testing separate default, randomized and extreme parameter distributions across six tasks.

**Direct evidence:** aggregate extrapolation success is 63.72 ± 2.08 for feedforward A2C, 48.37 ± 3.21 for feedforward PPO, 59.26 ± 5.81 for feedforward EPOpt-PPO, and 21.36 ± 4.41 for recurrent RL²-PPO. EPOpt helps PPO but does not beat every simple baseline. Architecture and trainability complicate causal attribution.

**Project inference:** specialized adaptive/robust learning can lose to an ordinary baseline, so “RL handles OOD” is inadequate justification. The paper pre-empts that generic claim and motivates matched tuning. Its extrapolation changes simulator parameters within known task equations, not independent encoder architecture/training; the reported percentages cannot be imported as watermark transfer likelihoods.

### C11-06 — Quantifying Generalization in Reinforcement Learning

**Metadata:** Karl Cobbe, Oleg Klimov, Chris Hesse, Taehoon Kim, John Schulman; ICML 2019, PMLR 97, 1282–1289. Inspected [proceedings full text](https://proceedings.mlr.press/v97/cobbe19a/cobbe19a.pdf); accessed 2026-10-30. Read §§3.1–3.2 and 4, including training-set/architecture experiments.

**Classification/mechanism:** full RL using PPO on CoinRun. Image observations guide platformer movement actions; the coin provides the positive task reward. Episodes terminate on collection, death or 1,000 steps. The central contribution is evaluating generalization, not inventing an algorithm that guarantees it.

**Direct evidence:** training compares 100–16,000 levels and an effectively unbounded generator at 256 million training steps, with five seeds and 10,000 evaluation episodes. Overfitting is substantial below 4,000 training levels and remains detectable at 16,000. These are quantitative sample-diversity findings; exact plotted accuracy gaps are not claimed. Training and testing sample the same procedural level distribution.

**Project inference:** holding out images or random seeds does not constitute holding out an encoder family. Larger independent-looking sample counts can hide shared mechanism. The work pre-empts describing same-generator held-out samples as evidence of structural extrapolation. **Open assumption:** a writer's source-family diversity, rather than only its number of images, may govern transfer; this analogy needs testing and does not imply any particular minimum number of regeneration families.

### C11-07 — Leveraging Procedural Generation to Benchmark Reinforcement Learning

**Metadata:** Karl Cobbe, Christopher Hesse, Jacob Hilton, John Schulman; ICML 2020, PMLR 119, 2048–2056. Inspected [proceedings full text](https://proceedings.mlr.press/v119/cobbe20a/cobbe20a.pdf); accessed 2026-10-30. Read §§2–4, especially 3.1–3.3, benchmark setup and model-size comparison.

**Classification/mechanism:** full RL benchmark, primarily PPO. Each of 16 games has its own policy; observations are 64×64 RGB, action space has 15 discrete actions, and reward/episode termination are game-specific. A common episode cap was not established in the inspected text; 200 million steps is a training budget, not a decision horizon.

**Direct evidence:** across training sets of 100–100,000 levels, as many as 10,000 levels are needed to close the generalization gap. The standard generalization split trains on 500 levels. A deterministic-level ablation rarely reaches beyond level 20 and performs poorly when sequences are randomized. Test levels still come from each game's procedural family.

**Project inference:** this strengthens the warning against memorizing a narrow source distribution, but it does not test cross-game policy transfer or independently trained encoders. It pre-empts conflating diversity of episodes with diversity of generating mechanisms. Neither “10,000 levels” nor “16 games” supplies a watermark sample-size prescription. Model capacity and training distribution remain non-RL-method design choices that a fair baseline must also receive.

### C11-08 — In Search of Lost Domain Generalization

**Metadata:** Ishaan Gulrajani, David Lopez-Paz; ICLR 2021. **Version caveat:** the actually inspected text is the earlier arXiv:2007.01434v1, 2 July 2020, [full text](https://arxiv.org/pdf/2007.01434v1), accessed 2026-10-30. Read §§2–5 and Table 4. The following nine-algorithm results belong to this version, not the later expanded publication.

**Classification/mechanism:** non-RL supervised classification with domain-generalization penalties and ordinary empirical risk minimization (ERM). Image/class prediction and classification loss replace policy state/action/reward; no sequential horizon applies. Model selection is explicitly part of the algorithm.

**Direct evidence:** under training-domain validation, Table 4 averages are ERM 67.0, CORAL 67.2, DRO 65.5 and IRM 66.0. Seven datasets, three selection methods and repeated hyperparameter sweeps expose the strength of tuned ERM. These are benchmark averages, not proof that ERM always dominates.

**Project inference:** a sophisticated invariance/robustness label alone does not justify novelty or expected gains. The watermark analogue is strong randomized expected-loss PGD, tuned without the excluded target, plus matched robust objectives. This paper pre-empts weak-baseline domain-generalization claims. **Open assumption:** shared features sufficient for the target task must exist; the project must establish that its fixed reader observes such features after an independent encoder, rather than assuming invariance.

### C11-09 — Robust Control of Markov Decision Processes with Uncertain Transition Matrices

**Metadata:** Arnab Nilim, Laurent El Ghaoui; Operations Research 53(5), 780–798 (2005), DOI 10.1287/opre.1050.0216. Inspected the undated, author-hosted draft titled *Robust Solutions to Markov Decision Problems with Uncertain Transition Matrices*, [full text](https://people.eecs.berkeley.edu/~elghaoui/Pubs/phd1.pdf), accessed 2026-10-30. The draft is not asserted identical to the published version. Read §§2–3.1, Theorem 1/proof, §4.1 contraction argument, and §8.1 setup.

**Classification/mechanism:** non-RL robust model-based dynamic programming. Finite states/actions and transition uncertainty sets are given; the objective minimizes worst-case accumulated cost. Horizons are finite N or infinite discounted. No policy-gradient learner or exploration reward is involved.

**Direct theoretical evidence:** robust Bellman recursion solves the stated finite-horizon minimax problem; the discounted operator contracts with discount factor ν, yielding geometric convergence. The transition-set and adversary assumptions define the guarantee. A time-varying uncertainty formulation can upper-bound its stationary counterpart; this is not arbitrary distribution-free robustness.

**Project inference:** robust optimization predates the proposed RL controller and is a serious conceptual comparator. A bound over an explicitly specified transition set says nothing about an excluded encoder outside that set. Continuous perturbations and a fixed reader do not automatically instantiate the finite-state theorem; neither its guarantee nor computational properties can be transferred without a new derivation.

## Transfer taxonomy and publication implications

The following classification is a project inference informed by the cards, not an additional experimental result.

| Evaluation | What it can establish | What it cannot establish |
|---|---|---|
| New images/seeds under the same regenerators | Instance generalization under known mechanisms | Independently trained encoder transfer |
| Unseen strengths/samplers within a shared encoder | Parameter/intervention generalization within that family | Structural extrapolation beyond the encoder |
| Excluded independently trained encoder/regenerator family | Empirical transfer to that specified target, if entirely untouched during selection | Universal unseen-family robustness |
| Target-query adaptation | Performance with stated target feedback and query cost | Source-only zero-shot transfer |
| Minimax over an explicit surrogate uncertainty set | Robustness within the set, subject to solver/approximation limits | Robustness to transformations outside the set |

**Informal identifiability argument, derived here:** source-family observations alone need not distinguish two possible future regenerators that behave identically on all available evidence yet preserve different perturbation components. If the future transformation removes every feasible reader-visible component, source-side RL cannot create surviving information merely by optimizing a different policy. This is not a theorem about real diffusion systems or a claim that the project is impossible; it identifies a missing structural assumption. Empirical survival evidence or a defensible shared-mechanism argument is necessary.

**Strongest non-RL alternatives, proposed rather than run:** (1) projected optimization of an expected loss over the same surrogate distribution; (2) projected CVaR/worst-family optimization with identical losses and feasible set; (3) fixed or randomized surrogate schedules tuned on source-only development folds; (4) a supervised predictor of useful schedule/step allocations when suitable source-only targets exist. They should receive the same observables and total training, hyperparameter-search, validation, and per-image inference budgets as RL. Counting only final writer inference would conceal policy pretraining cost; counting only surrogate calls can conceal gradient/discriminator/training cost. Report both resource measures where possible. An adaptive non-RL scheduler should be included if sequential feedback, rather than RL itself, is the hypothesized benefit.

**Novelty boundary:** domain randomization, tail-risk optimization, and learned simulator scheduling are already occupied concepts. A defensible new claim would require a watermark-specific information/action structure and prospective evidence of better C/J retention under a truly excluded family at equal total cost, while all quality and T4/T5 conditions pass. Mere use of PPO, an adaptive schedule, or a held-out seed is insufficient. This cluster supplies no basis for claiming the first such application; direct watermark/RL literature must be reconciled separately.

**Family-count caveat:** three or four source families offer few independent mechanism-level observations. More source images, random seeds or closely related checkpoints do not manufacture independent encoder families. Leave-one-family-out development diagnostics can expose source sensitivity; once a family influences method selection it is no longer the final untouched target. Treat several related SD1.5 configurations as shared-family evidence unless a stronger independence argument is documented. No numerical publication-success probability can be defensibly extracted from these heterogeneous studies.

## Remaining evidence gaps

- No inspected paper directly demonstrates bounded posthoc watermark transfer through an independently trained diffusion autoencoder with the fixed SD1.5 reader and simultaneous C/J/quality/T4/T5 gates.
- No inspected result establishes RL superiority over source-matched, budget-matched differentiable optimization for this task.
- Robust-MDP guarantees require explicit uncertainty assumptions; this cluster has not derived a continuous watermark analogue.
- The evidence includes successful transfer and negative results, but not an exhaustive current novelty search. C11-08 and C11-09 carry explicit version caveats; plotted margins not read reliably remain unreported.

Coverage audit: 14 executed searches; 5 scholarly site targets; 9 opened primary full texts; 6 RL cards and 3 non-RL cards; no experiments or result files read. The ninth theoretical card is supplemental to the eight method/evaluation cards, with its draft limitation retained.
