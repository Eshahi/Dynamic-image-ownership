# C8 — Reinforcement learning, diffusion policies, and sampling control

Author: Codex C8 research agent. Access date: 2026-10-30. Scope: research only; no experiments or downloads. Ten distinct full texts inspected online, including four deliberately retained non-RL comparators. No F6 results were accessed. This is a bounded literature assessment, not a systematic-review completeness claim.

## Search and access ledger

All 23 queries below were actually issued through the web search tool. Correction: 13 intended domain-targeted queries use malformed `site.domain` terms rather than `site:domain` operators. They count as general-web queries, not enforced searches of scholarly indexes. The intended domains were arXiv, OpenReview, CVF Open Access, PMLR, and DBLP. Exact historical strings are retained. Queries were submitted in batches; result attribution records useful leads from that batch, not per-query provenance. No native index or Google Scholar search is claimed; the global index floor relies on valid queries in other logs.

| ID | Exact query | Route/index contents | Useful lead or result status |
|---|---|---|---|
| Q01 | `site.arxiv.org diffusion reinforcement learning DDPO DPOK reward backpropagation DRaFT` | Indirect arXiv | DDPO, DPOK, AlignProp; inspected below. |
| Q02 | `site.openreview.net diffusion reinforcement learning sampling schedule policy optimization` | Indirect OpenReview | Diffusion-policy and scheduler leads; OpenReview direct access sometimes CAPTCHA. |
| Q03 | `site.thecvf.com diffusion reinforcement learning sampling trajectory attack` | Indirect CVF | RaSS primary CVPR PDF discovered, retrieval blocked; excluded. |
| Q04 | `site.proceedings.mlr.press diffusion reward optimization AlignProp ReFL` | Indirect PMLR | DMSampler proceedings lead; not counted without method/evaluation inspection. |
| Q05 | `site.arxiv.org "Directly Fine-Tuning Diffusion Models" reward gradients` | Indirect arXiv | DRaFT; full text recovered at v2 HTML. |
| Q06 | `site.openreview.net "Diffusion Policy Policy Optimization"` | Indirect OpenReview | DPPO ICLR paper; arXiv full text inspected. |
| Q07 | `site.dblp.org diffusion "Aligning" reward backpropagation` | Indirect DBLP | No additional qualifying full text. |
| Q08 | `site.arxiv.org diffusion adversarial attack reinforcement learning trajectory` | Indirect arXiv | Preference/attack leads, including D3PO; no additional counted card. |
| Q09 | `site.arxiv.org "diffusion" "reinforcement learning" "adversarial" image attack` | Indirect arXiv | SPARED, SHIFT, ReLAPSe leads; SPARED inspected. |
| Q10 | `site.openreview.net "Aligning Text-to-Image Diffusion Models with Reward Backpropagation"` | Indirect OpenReview | AlignProp primary venue lead; arXiv full text inspected. |
| Q11 | `site.openaccess.thecvf.com "timestep" "reinforcement" diffusion scheduler` | Indirect CVF | ADOPT and optimized timesteps; latter inspected through arXiv. |
| Q12 | `site.dblp.org "diffusion" "reinforcement" sampling` | Indirect DBLP | Yilie Huang DBLP publication page/ART scheduler lead; not counted. |
| Q13 | `"DRaFT" "Clark" paper pdf directly fine tuning` | General web discovery | Official ICLR PDF and arXiv versions; large PDF unavailable, HTML recovered. |
| Q14 | `"Steering Your Diffusion Policy" arxiv` | General web discovery | DSRL; inspected. |
| Q15 | `"RaSS" arxiv` | General web discovery | Mostly unrelated acronym results; no qualifying recovery. |
| Q16 | `"Reinforcement Learning-based Adaptive Control" diffusion arxiv` | General web discovery | ADOPT WACV primary lead; retrieval blocked. |
| Q17 | `"RaSS" "Ding" "sampling" arxiv pdf` | General web discovery | No accessible primary full-text recovery. |
| Q18 | `"Accelerating Diffusion Sampling with Optimized Time Steps" arxiv` | General web discovery | arXiv 2402.17376 and DBLP record; inspected v2. |
| Q19 | `site.arxiv.org "Diffusion Model Alignment Using Direct Preference Optimization"` | Indirect arXiv | Diffusion-DPO; inspected v1. |
| Q20 | `"Reinforced Active Sampling Scheduler" arxiv` | General web discovery | CVF and secondary RaSS listings; still excluded. |
| Q21 | `"diffusion" "learning to schedule" "Wang" reinforcement` | General web discovery | KDD Learning to Schedule, DOI and DBLP; no accessible full text. |
| Q22 | `"Self-Supervised Diffusion Model Sampling With Reinforcement Learning" arxiv` | General web discovery | OpenReview PDF lead; CAPTCHA prevented full-text inspection. |
| Q23 | `"Aligning Text-to-Image Diffusion Models with Reward Backpropagation" withdrawn ICLR` | General web metadata verification | Withdrawal/subsumption confirmed against primary arXiv v5 notice; ICLR acceptance not established. |

The IRL sampler in C08-10 was followed as a primary-paper lead during these searches and related-paper inspection. Its full text, not its search snippet, supplies the evidence. Version-specific URLs below are the actual inspected artifacts. A missing publication DOI is recorded as null, not inferred from a title. Repository identifiers are provided separately.

Primary result URL register for the query log (shared batch leads are deliberately grouped): Q01–Q04: [DDPO](https://arxiv.org/abs/2305.13301), [DPOK](https://arxiv.org/abs/2305.16381), [AlignProp](https://arxiv.org/abs/2310.03739), [PMLR DMSampler](https://proceedings.mlr.press/v306/liu26ev.html). Q05–Q08: [DRaFT](https://arxiv.org/abs/2309.17400), [DPPO venue](https://openreview.net/pdf?id=mEpqHvbD2h), [D3PO lead](https://arxiv.org/abs/2311.13231); Q07 yielded no new qualifying source. Q09–Q12: [SPARED](https://arxiv.org/abs/2608.12876), [SHIFT lead](https://arxiv.org/abs/2511.07701), [ReLAPSe lead](https://arxiv.org/abs/2602.00350), [DBLP publication-list lead](https://dblp1.uni-trier.de/pid/331/6322.html), and the CVF leads in the exclusion table. Q13: [DRaFT](https://arxiv.org/abs/2309.17400). Q14: [DSRL](https://arxiv.org/abs/2506.15799). Q15/Q17/Q20 found no accessible new primary full text; Q16 has the blocked ADOPT lead below. Q18: [optimized timesteps](https://arxiv.org/abs/2402.17376), [DBLP record](https://dblp.org/rec/journals/corr/abs-2402-17376.html). Q19: [Diffusion-DPO](https://arxiv.org/abs/2311.12908). Q21: [KDD DOI](https://doi.org/10.1145/3580305.3599412). Q22: [blocked OpenReview PDF](https://openreview.net/pdf?id=aATVaBx01a). Q23: [primary withdrawal/subsumption notice](https://arxiv.org/abs/2310.03739v5). These are discovery locators; only the versioned full texts in the cards count as inspected evidence.

## Inspected cards

Each card below is under 180 source-derived words and inherits access date **2026-10-30**. Linked full texts contain canonical full author lists where `et al.` is used. `Not established` statements identify missing evidence in the inspected evaluation, rather than claiming exhaustive absence from the literature. Publication status is conservative where only the preprint was verified. Numerical outcomes are SOURCE reports, not new calculations or reproduced results.

### C08-01 — Training Diffusion Models with Reinforcement Learning (DDPO)

Metadata: Kevin Black et al.; 2023, inspected arXiv:2305.13301v4 (2024-01-04); publication DOI: null. [Primary full text](https://arxiv.org/html/2305.13301v4). Status: FULL_TEXT_INSPECTED_ONLINE.

Method: §4.3 treats denoising as an MDP: state = prompt, timestep, noisy latent; action = next latent; terminal reward = image score. DDPO uses score-function policy gradients, including importance-sampled/clipped updates. It updates the generator, not merely a sampler schedule.

Evaluation: §6.1/Fig.4 compares reward-weighted regression and sparse variants on SD1.4 aesthetics/compressibility tasks. DDPO has better reward-query curves; no exact graph endpoint is transcribed here. §6.3 tests unseen prompts, not independent generator families. Appendix D.4 reports 50,000-sample runs taking roughly four hours on v4-64 TPUs for DDPO versus v3-128 for RWR; these are different hardware allocations. VLM rewards additionally use eight A100-80GB GPUs.

Limitation: §6/App.A show overoptimization and stylistic changes. Higher reward does not establish source-image preservation, watermark survival, or T4/T5 safety.

### C08-02 — DPOK: Reinforcement Learning for Fine-tuning Text-to-Image Diffusion Models

Metadata: Ying Fan et al.; NeurIPS 2023, arXiv:2305.16381v2 (2023-10-28); publication DOI: null. [Primary full text](https://arxiv.org/html/2305.16381v2). Status: FULL_TEXT_INSPECTED_ONLINE.

Method: §4.1/Eqs.4–8 use denoising-state/action trajectories, terminal ImageReward, REINFORCE, and a sum of transition KL penalties toward the pretrained generator. Online reward samples differ from fixed-data supervised KL-D/KL-O alternatives (§4.2).

Evaluation: §5.1–5.2 uses SD1.5 LoRA and four single-prompt capability tasks. RL and supervised KL-O each consume 20,000 generated training images. Fig.3 reports stronger RL reward and quality; its exact plotted effect is not numerically extracted here. Human evaluation uses 160 images per model and eight raters. Unseen-prompt examples appear in Appendix E.

Cost/limits: Equal generated-image counts do not establish equal training compute. These comparisons omit modern pathwise-gradient baselines. ImageReward, aesthetic evaluation, and human preference assess generation alignment; they do not measure ownership binding, strict fidelity to an input image, or excluded-family regeneration.

### C08-03 — Aligning Text-to-Image Diffusion Models with Reward Backpropagation (AlignProp)

Metadata: Mihir Prabhudesai, Anirudh Goyal, Deepak Pathak, Katerina Fragkiadaki; 2023 preprint; arXiv:2310.03739v2 (2024-06-22); publication DOI: null. [Inspected full text](https://arxiv.org/html/2310.03739v2). Status: FULL_TEXT_INSPECTED_ONLINE, historical/subsumed. [Later withdrawal notice](https://arxiv.org/abs/2310.03739v5) states subsumption by arXiv:2407.08737; no ICLR acceptance is assumed.

Method: §4/Eqs.2–4 backpropagate differentiable image reward through DDIM into LoRA; randomized gradient truncation and checkpointing control memory/collapse. Classification here: direct pathwise optimization, **not score-function RL**; state/action/reward MDP labels are unnecessary for implementation.

Evaluation: §5.1/Fig.5 uses the same four-A100 configuration and batch size: HPS reward 2.8 takes approximately 48 minutes versus approximately 23 hours for DDPO. These measured times are preferable to treating the paper's rounded speedup as universal. Table 1 reports unseen-animal aesthetic reward 8.71 versus DDPO 6.82, and HPS 3.32 versus 2.93.

Limits: §4.1 reports collapse with full untruncated backpropagation. Rewards are learned preferences, not perceptual ownership constraints; prompt transfer does not establish generator-family transfer. This is a required strong comparator whenever the proposed reward and pipeline are differentiable.

### C08-04 — Directly Fine-Tuning Diffusion Models on Differentiable Rewards (DRaFT)

Metadata: Kevin Clark, Paul Vicol, Kevin Swersky, David J. Fleet; ICLR 2024; arXiv:2309.17400v2 (2024-06-21); publication DOI: null. [Primary full text](https://arxiv.org/html/2309.17400v2). Status: FULL_TEXT_INSPECTED_ONLINE.

Method: §4/Algorithm 1 uses pathwise reward gradients through sampling, LoRA, checkpointing, truncated DRaFT-K, and last-step variance-reduced DRaFT-LV. Classification: differentiable optimization, not online score-function RL; no task-transition policy is required.

Evaluation: §5.1/Fig.3 compares DDPO, ReFL, and prompt engineering for SD1.4 aesthetic optimization. §5.2/Fig.4 compares HPSv2 rewards, including best-of-16 and DOODL; DRaFT-LV learns approximately twice as fast as DRaFT-1. Default runs use 10,000 training steps; §4 describes approximately 10% extra computation for the variance-reduction construction. This is not a universal end-to-end speedup over RL.

Limits: §5.1/App.B.8 explicitly document high-reward diversity collapse. §5.2 tests prompt/reward transfer, not cross-autoencoder regeneration or ownership detection. Truncation changes the optimized gradient; reward improvement alone is insufficient evidence of semantic fidelity.

### C08-05 — Diffusion Policy Policy Optimization (DPPO)

Metadata: Allen Z. Ren et al.; arXiv:2409.00588v2 (2024-11-07); ICLR 2025 venue record; publication DOI: null. [Inspected full text](https://arxiv.org/html/2409.00588v2); [venue paper](https://openreview.net/pdf?id=mEpqHvbD2h). Status: FULL_TEXT_INSPECTED_ONLINE.

Method: §4 builds a two-layer MDP: environment state plus noisy action chunk; denoising actions ultimately become robot actions; reward is environment task return. PPO/GAE optimize diffusion transition likelihoods with denoising discounting and selected fine-tuned steps. This is genuine RL whose action distribution is a diffusion model.

Evaluation: §5 compares DRWR, DAWR, DIPO, IDQL, DQL, QSM, and Gaussian/GMM policies. Fig.7 reports above-90% Transport success. Appendix D.6 uses 40 parallel environments for DPPO versus one for Kitchen baselines; D.7 uses 50 for all Robomimic policies and 50 evaluation episodes, with different pretraining epochs.

Limits: Environment-sample efficiency is not total-compute efficiency. Robot diffusion policies are not image-regeneration controllers. Differentiable image reward backpropagation cannot automatically replace learning through unknown physical dynamics; conversely, this robotics result does not establish DDPO superiority for image rewards.

### C08-06 — Steering Your Diffusion Policy with Latent Space Reinforcement Learning (DSRL)

Metadata: Andrew Wagenmaker et al.; 2025 preprint; arXiv:2506.15799v1 (2025-06-18); publication DOI: null. [Inspected full text](https://arxiv.org/html/2506.15799v1). Status: FULL_TEXT_INSPECTED_ONLINE. Later v2 metadata was seen, but its results are not substituted.

Method: §4 transforms the control MDP: state = environment observation; action = initial noise for a frozen diffusion/flow policy; reward = environment return. Noise-space Q-learning/SAC learns steering without updating generator weights; action aliasing requires care.

Evaluation: §5.1 compares DPPO, IDQL, DQL, DIPO, QSM on simulated control. §5.2/Table 1 offline OGBench includes scene success 88±9 versus flow BC 0±0 and FQL 76±9; antmaze-giant remains 0 versus ReBRAC 27±22. DSRL uses four seeds there; baseline numbers come from previous work.

Cost/limits: Frozen weights avoid generator fine-tuning, but repeated denoising and environment rollouts remain. Sample-efficiency plots are not matched total-compute evidence. The structural analogy to selecting image-regeneration noise is plausible, but robot returns provide no evidence of watermark preservation or cross-generator transfer.

### C08-07 — SPARED: Reasoning-Based AI-Generated Image Detection via Adversarially Edited Data

Metadata: Yicheng Bao, Xiahui Guo, Xuhong Wang, Xin Tan; 2026 preprint; arXiv:2608.12876v1 (2026-08-13); publication DOI: null. [Primary full text](https://arxiv.org/html/2608.12876v1). Status: FULL_TEXT_INSPECTED_ONLINE.

Method: Method section/Eqs.1–3 alternates a GRPO reasoning detector and a DiffusionNFT image editor. Editor context is a real image plus instruction; generated edits earn detector-fooling reward only when PaCo fidelity exceeds 0.7. Defender reward is verdict correctness; paired originals limit shortcuts. This is adversarial policy optimization, not watermark-specific regeneration control.

Evaluation: Table 3 reports DFJDetect accuracy 72.1% at iteration 1 versus 79.5% at iteration 3. Static-pool extra GRPO reaches 74.3% at 4.7× budget; fresh-source/frozen-attacker reaches 73.7% at 7.1×. Fig.3a's unseen-generator mean improves, but Janus accuracy regresses from 86.5% to 73.1% between iterations 2–3.

Limits: Relative budgets are not complete GPU accounting. A fidelity gate does not prove shortcut immunity, strict input preservation, or ownership binding. Generic diffusion-editor/detector adversarial co-training is already occupied prior art.

### C08-08 — Accelerating Diffusion Sampling with Optimized Time Steps

Metadata: Shuchen Xue et al.; CVPR 2024; arXiv:2402.17376v2 (2024-07-01); publication DOI: null. [Primary full text](https://arxiv.org/html/2402.17376v2). Status: FULL_TEXT_INSPECTED_ONLINE.

Method: §§4–5/Eq.35/Algorithm 1 optimize timestep grids using an ODE approximation-error bound and constrained numerical optimization. **Not RL:** decision variable = timestep grid; objective = numerical error bound; no state-conditioned learned reward policy or environment exploration.

Evaluation: §6.2/Appendix Table 5, DiT-XL/2 conditional ImageNet-256 with UniPC and guidance 1.5: at five function evaluations, optimized-grid FID is 8.66 versus uniform-time 23.48; at fifteen, 2.36 versus 2.50. These are sampler/distribution-quality results, not per-image retention measurements.

Cost: §6.3/Table 2 reports CPU grid optimization around 1.9 seconds at five evaluations and 14.1 seconds at fifteen on Xeon Gold 6278C; schedules are reusable.

Limits: This gives a strong inexpensive non-RL schedule comparator. No RL novelty follows from merely replacing a fixed grid with optimized timesteps, and no watermark-transfer conclusion follows from FID.

### C08-09 — Diffusion Model Alignment Using Direct Preference Optimization

Metadata: Bram Wallace et al.; CVPR 2024; arXiv:2311.12908v1 (2023-11-21); publication DOI: null. [Primary full text](https://arxiv.org/html/2311.12908v1). Status: FULL_TEXT_INSPECTED_ONLINE.

Method: §4/Eq.14 compares denoising errors for preferred/dispreferred images against a reference model. Although derived from an off-policy RL objective, implemented training uses fixed preference pairs. Classification here: offline supervised preference optimization, not online exploratory RL; no sampled action receives an online environment reward.

Evaluation: §5.1 uses 851,293 Pick-a-Pic-v2 pairs and 58,960 prompts; effective batch 2,048 on sixteen A100s. §5.2/Fig.4 reports human general-preference wins of 69% on PartiPrompts and 64% on HPS against SDXL base-plus-refiner, with five-labeler majority votes. DDPO did not give stable improvement in the authors' public-implementation trial (§5.1), not a conclusive matched-method defeat.

Cost/limits: Training and preference collection are substantial; inference retains the base architecture. Qualitative SDEdit examples (§5.3) are not evidence of ownership preservation. Prompt-preference gains cannot justify claims about T3/T4/T5 robustness.

### C08-10 — Learning To Sample From Diffusion Models Via Inverse Reinforcement Learning

Metadata: Constant Bourdrez, Alexandre Vérine, Olivier Cappé; 2026 preprint; arXiv:2602.08689v1 (2026-02-09); publication DOI: null. [Primary full text](https://arxiv.org/html/2602.08689v1). Status: FULL_TEXT_INSPECTED_ONLINE.

Method: §§4–5 uses state = noisy image/noise level; actions select guidance, renoising, or stochasticity of a frozen denoiser. An expert noised-data occupancy objective supplies density-ratio/discriminator learning signals; importance-weighted policy gradients use clipping. This is actual sequential sampler control via IRL.

Evaluation: §6/Table 2 evaluates 50,000-sample FID. ImageNet-64 renoising rKL reaches FID 2.92 at 52.1 mean function evaluations versus EDM 3.01 at 350. FFHQ instead worsens: rKL 3.07 at 68.2 versus EDM 2.60 at 59. Table 1's CIFAR guidance improvement is small, 2.05 versus 2.07.

Cost/limits: §6 explicitly adds trajectory/discriminator training; inference overhead is described qualitatively, without complete training amortization. Do not transplant later-version numerical cost claims into v1. Distribution matching and fewer evaluations do not establish per-source semantic retention or watermark detection.

## Setting, classification, and pre-emption register

This register makes the taxonomy explicit. The pre-emption column is JUDGMENT about occupied ingredients, not a claim that the paper implements our exact ownership task. Comparator-not-RL entries have state/action/reward = N/A; their optimization variables/objectives are described in the cards.

| Card | Setting | RL class | Occupied ingredient / relevance boundary |
|---|---|---|---|
| C08-01 | Generation-time image model adaptation | R-full | Multi-step denoising policy gradients; not post-hoc ownership marking. |
| C08-02 | Generation-time image model adaptation | R-full | KL-constrained online generator fine-tuning. |
| C08-03 | Generation-time image model adaptation | comparator-not-RL | Differentiable reward backpropagation; historical/subsumed source. |
| C08-04 | Generation-time image model adaptation | comparator-not-RL | Truncated/variance-reduced pathwise reward gradients. |
| C08-05 | Robotics action generation/control | R-full | Nested diffusion/environment policy optimization. |
| C08-06 | Robotics action generation/control | R-full | RL over a frozen diffusion decoder's latent noise. |
| C08-07 | Post-hoc image editing and synthetic-image detection | R-game | Alternating diffusion-editor/detector adaptation; no ownership binding. |
| C08-08 | Generation-time image sampling | comparator-not-RL | Numerical optimization of a reusable timestep grid. |
| C08-09 | Generation-time image model adaptation; editing examples | comparator-not-RL | Fixed-pair preference training; no online exploratory environment. |
| C08-10 | Generation-time image sampling | R-full (IRL) | State-conditioned guidance, stochasticity and renoising policies. |

## Excluded and unresolved leads

These entries contribute **zero** to the inspected-paper floor.

| Lead | Primary locator or discovery trail | Disposition |
|---|---|---|
| RaSS / Reinforced Active Sampling Scheduler | [CVF proceedings search index](https://openaccess.thecvf.com/CVPR2025) | CVPR primary PDF discovered; repeated retrieval returned access errors. UNINSPECTED; no method/effect claim borrowed from snippets. |
| ADOPT / Reinforcement Learning-based Adaptive Control for Diffusion Model Optimization | [CVF WACV proceedings index](https://openaccess.thecvf.com/WACV2025) | Primary PDF retrieval blocked. UNINSPECTED; title-level lead only. |
| Learning to Schedule in Diffusion Probabilistic Models | [DOI record](https://doi.org/10.1145/3580305.3599412); [DBLP](https://dblp.dagstuhl.de/rec/conf/kdd/WangWD0X23.html) | KDD 2023, Yunke Wang et al.; bibliographic lead without inspected primary method/evaluation. |
| Self-Supervised Diffusion Model Sampling With Reinforcement Learning | [OpenReview PDF](https://openreview.net/pdf?id=aATVaBx01a) | CAPTCHA; UNINSPECTED. |
| DMSampler | [PMLR lead](https://proceedings.mlr.press/v306/liu26ev.html) | Discovered but not method/evaluation-inspected; no evidence claim. |
| SHIFT; ReLAPSe; ART | arXiv leads 2511.07701, 2602.00350, 2601.18681 | Search leads only; no card, effect, or novelty exclusion asserted. |
| DRIFT | arXiv:2609.08213, assigned to root C12 | Deliberate cross-cluster duplicate exclusion. No new count or result imported here. |

Access failures also included an oversized DRaFT PDF and unavailable guessed HTML versions; inspection was recovered using its actual v2 HTML. No claim that an abstract-only visit satisfies full-text inspection. AlignProp is counted as one inspected historical artifact, with later withdrawal explicitly disclosed; its successor [Video Diffusion Alignment via Reward Gradients](https://arxiv.org/abs/2407.08737) was metadata-only inspected and contributes zero additional papers. Historical speed claims should be attributed to the v2 manuscript, not presented as independently validated or current peer-reviewed guarantees.

## Project synthesis and decisions

The following are **researcher inferences/proposals**, not claims that these papers tested this thesis.

1. **Separate four mechanisms before calling anything RL.** DDPO/DPOK update image generators with scalar terminal rewards; DPPO/DSRL improve robot action distributions; C08-10 controls an image sampler sequentially; Diffusion-DPO uses fixed preference supervision. AlignProp/DRaFT and numerical timestep optimization remain mandatory non-RL alternatives. A one-shot choice of seed, strength, or configuration is a contextual bandit unless later observations change subsequent choices. A diffusion decoder inside a robot policy does not itself create evidence for image-regeneration robustness.

2. **Dense gradients are the strongest easy-to-miss comparator.** If both a continuous mark objective and development regenerator are differentiable, compare pathwise/truncated-gradient optimization (AlignProp/DRaFT style) before spending on score-function RL. Gradients transmit more directional information than a scalar reward; truncation/memory and surrogate mismatch remain limitations. For genuinely discrete schedules, unavailable derivatives, expensive black-box verdicts, or delayed state-dependent decisions, score-function RL has a defensible role. This is a method-selection argument, not a theorem that gradients always win. For DPPO's physical environments, a differentiable learned critic/actor baseline can be relevant, but image-reward backpropagation is not an interchangeable oracle through unknown dynamics.

3. **The credible control question is narrower than “RL for diffusion.”** A development-only controller could observe intermediate latent statistics and remaining compute/quality budget, then choose a bounded next denoising intervention. The question is whether observing the trajectory adds value beyond an input-conditioned fixed schedule, optimized numerical grid, random search, Bayesian/CMA-ES search, or a contextual bandit with the same action set. Existing sampler IRL and the unresolved schedule leads make a generic novelty claim untenable. A mark-preserving controller also changes which side controls regeneration; it is not evidence of survival against an attacker who ignores that controller.

4. **Total cost must include every route to the reported checkpoint.** Preregister accounting as `C_total = C_preparation + C_tuning + C_rollouts + C_rewards + C_updates + C_final_evaluation + N_deploy * C_inference`. Report denoiser evaluations, reward/detector calls, backward passes, memory, accelerator type/hours, and failed trials separately; hardware counts and simulator parallelism prevent naive wall-clock comparisons. Compare reward-query budgets *and* total costs. A reusable schedule/policy amortizes training only after enough deployments; report the crossover, or state that it never occurs in the planned study. Include best-of-N selection cost and any surrogate training. No supplied paper establishes the complete budget ordering for this thesis.

5. **Transfer must mean an excluded generator family, not an unseen prompt.** Fix development-only training families and a family excluded from policy training and hyperparameter choice; evaluate it once under a locked rule. A lower reward on that family is a negative result, not an invitation to tune and continue calling it excluded. Match regenerator operation points and quality constraints, and report individual families instead of only a pooled mean. Source-held-out confirmatory data remain unavailable without the user's later approval. These cards supply no direct evidence that an ownership mark or controller transfers across independently trained autoencoders.

6. **Reward hacking is central, not an auxiliary visualization.** A weighted reward permits exchanging fidelity for detector score. Keep strict source-quality constraints, semantic preservation, detector score, and detector error rates as separate outputs; require feasibility before ranking feasible candidates. Evaluation should include independent development assessors and blinded human assessments when available, with missing human judgments explicitly missing. Neither CLIP/ImageReward/HPS nor FID proves ownership binding. Test C0/wrong-owner negatives and T4/T5 under the same frozen verification rule; a T3 improvement cannot silently relax them. SPARED makes adversarial data generation an especially important novelty comparator, while its task remains synthetic-image detection rather than ownership verification.

7. **Publication implication.** Plausible contribution: a constrained, budget-accounted, state-dependent regeneration/attack controller whose additional trajectory information gives measurable value, paired with independent-family transfer and T3/T4/T5 evidence. Unpromising claim: “first RL diffusion scheduler,” “diffusion policy therefore watermark robustness,” or “preference optimization is an RL experiment.” A negative result showing that gradients or simple search dominate at equal full cost would still answer the research question honestly.

Mapping to the user's readings: **P1** (per-image configuration before marking) is usually a contextual choice; DSRL supplies an analogy to latent/configuration steering, not a proof that long-horizon RL is needed. **P2** (spatial/frequency allocation before encoding) has no direct supporting ownership experiment in this cluster; continuous allocation should face a gradient baseline. **P3** (surrogate/timestep/transform selection inside the writer loop) is the closest sequential-control analogy, but actual value requires intermediate feedback that changes the best next action. C08-08/C08-10 occupy generic schedule optimization/control; the unresolved task-specific contribution is preservation of content-bound ownership under separately controlled regeneration. C08-07 additionally bears on P6/P7 attacker/writer games, not direct proof for P1–P3.

## Coverage count and handoff

- Distinct inspected full-text cards: **10**. Method and evaluation inspected for every counted card.
- Actual logged queries: **23**, including **13** malformed domain-targeted terms; these are not site-restricted searches. Native index API searches: **0**.
- Genuine RL/IRL or adversarial policy optimization: DDPO, DPOK, DPPO, DSRL, SPARED, sampler IRL (**6**). Differentiable optimization comparators: AlignProp, DRaFT (**2**). Numerical schedule comparator (**1**). Offline preference comparator (**1**).
- Direct schedule/trajectory control: C08-10; strong non-RL schedule baseline: C08-08. Direct gradient baselines: C08-03/C08-04. Diffusion-editor attack/detector game: C08-07. Robotics latent/action diffusion analogies: C08-05/C08-06.
- Unresolved: blocked schedule papers may further narrow novelty; none is counted as inspected. No card directly demonstrates a T3/T4/T5 ownership result. No experiment recommendation here authorizes execution.
