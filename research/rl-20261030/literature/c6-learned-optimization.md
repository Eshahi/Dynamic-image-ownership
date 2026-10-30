# C6 — Learned optimization and finite-budget optimizer control

Access date: 2026-10-30. Scope: WP2 C6; research only. No experiments, code/model downloads, run data, F6 outcomes, or git operations. All primary full texts below were opened online and substantive method and evaluation passages inspected. `FULL_TEXT_INSPECTED_ONLINE` means those sections were inspected, not every appendix or publisher-final verification. Source reports and project judgments are separated. No local-artifact/hash verification is claimed.

## Search log

All searches used `web.run` search_query. **Site-qualified queries are indirect index-content searches, not native index searches.** There were 14 distinct query strings, across six scholarly sites/indexes: arXiv, OpenReview, PMLR, NeurIPS proceedings, ACM DL, and DBLP. The first 12 were issued in four batches of three; Q04–Q09 were repeated individually because the initial batch output was truncated. Those six repeats are not counted as new queries. Q13–Q14 were general-web follow-ups. Thus 20 query submissions, 14 distinct queries. A returned irrelevant hit does not count as eligible literature or successful substantive coverage of its index.

| ID | Exact query | Index/access | Returned lead and disposition |
|---|---|---|---|
| C6-Q01 | `site:arxiv.org learning to optimize Li Malik reinforcement learning 2016` | arXiv, indirect | [Learning to Optimize](https://arxiv.org/abs/1606.01885); inspected C06-01. |
| C6-Q02 | `site:arxiv.org learning to optimize neural nets Li Malik 2017` | arXiv, indirect | [Learning to Optimize Neural Nets](https://arxiv.org/abs/1703.00441); inspected C06-02. |
| C6-Q03 | `site:proceedings.neurips.cc learning to learn gradient descent gradient descent Andrychowicz` | NeurIPS, indirect | [2016 proceedings](https://proceedings.neurips.cc/paper/2016/hash/fb87582825f9d28a8d42c5e5e5e8b23d-Abstract.html); PDF inspected C06-03. Reviews and later papers citing it were not counted. |
| C6-Q04 | `site:proceedings.mlr.press learned optimizers scale generalize Wichrowska` | PMLR, indirect | [Wichrowska](https://proceedings.mlr.press/v70/wichrowska17a.html), [VeLO critique](https://proceedings.mlr.press/v239/rezk23a.html), [tradeoffs](https://proceedings.mlr.press/v199/metz22a.html), [pathologies](https://proceedings.mlr.press/v97/metz19a.html), [guard](https://proceedings.mlr.press/v162/premont-schwarz22a.html); first two inspected; others leads only. |
| C6-Q05 | `site:openreview.net VeLO training versatile learned optimizer thousands tasks` | OpenReview, indirect | [Celo2](https://openreview.net/pdf?id=hxDB30LwVe), [critique](https://openreview.net/pdf?id=R7OizRVhEu), [Celo](https://openreview.net/forum?id=SLqJbt4emY); Celo2 redirected to browser challenge on open, resolved through arXiv; critique resolved through PMLR. Celo not counted. |
| C6-Q06 | `site:openreview.net practical tradeoffs learned optimizers Metz` | OpenReview, indirect | [A Closer Look](https://openreview.net/pdf?id=cxZEBQFDoFK), [Reverse engineering](https://openreview.net/pdf?id=gRlsFQMo_ze), later reference-list matches. No fulltext card for these leads. |
| C6-Q07 | `site:proceedings.mlr.press D-adaptation parameter free learning rates` | PMLR, indirect | [D-Adaptation](https://proceedings.mlr.press/v202/defazio23a.html), [DoG](https://proceedings.mlr.press/v202/ivgi23a.html), [Prodigy](https://proceedings.mlr.press/v235/mishchenko24a.html); first two inspected; Prodigy not counted. |
| C6-Q08 | `site:openreview.net DoG learning rate free learning` | OpenReview, indirect | [DoG PDF](https://openreview.net/pdf?id=ZrvQmCqiqh), [D-Adaptation PDF](https://openreview.net/pdf?id=GXZ6cT5cvY), [2025 tuning-free comparison](https://openreview.net/pdf?id=6BlOCx5c5T); duplicates of C06-05/06 followed via PMLR; third not counted. |
| C6-Q09 | `site:dl.acm.org reinforcement learning learning rate control neural network optimization` | ACM DL, indirect | [Adaptive sampling](https://dl.acm.org/doi/pdf/10.1145/3598301), [rehabilitation](https://dl.acm.org/doi/pdf/10.1145/3415227), [TinyNS](https://dl.acm.org/doi/pdf/10.1145/3603171); returned scope mismatches, not optimizer-control evidence. No ACM fulltext card. |
| C6-Q10 | `site:dblp.org Learning to Optimize Li Malik` | DBLP, indirect | [Ke Li bibliographic record](https://dblp.org/pid/75/6627-11.html); verifies ICLR 2017 for C06-01 and preprint listing for C06-02. Bibliography not counted as full text. |
| C6-Q11 | `site:arxiv.org reinforcement learning learned optimizer gradient descent comparison evaluation` | arXiv, indirect | [Wichrowska](https://arxiv.org/abs/1703.04813) duplicate; [Conformal Symplectic Optimization for Stable RL](https://arxiv.org/pdf/2412.02291) optimizes RL agents rather than learning an optimizer policy; not counted. |
| C6-Q12 | `site:openreview.net learning rate controller reinforcement learning Xu 2017` | OpenReview, indirect | Mostly author/profile and unrelated RL results, including [Xie search profile](https://openreview.net/search?content=authors&group=all&sort=cdate%3Adesc&source=forum&term=~Linhai_Xie1). No eligible controller paper recovered by this query. |
| C6-Q13 | `"CELO2" arxiv` | General web | [arXiv 2602.19142](https://arxiv.org/abs/2602.19142), author [repository](https://github.com/amoudgl/celo2); arXiv HTML inspected C06-08, repository not downloaded. Also surfaced newer ELO lead below. |
| C6-Q14 | `"VeLO" "2211.09760" HTML` | General web | [DBLP VeLO](https://dblp.org/rec/journals/corr/abs-2211-09760.html), citations and author discussions; direct arXiv HTML then opened and inspected C06-09. |

## Inspected cards

### C06-01 — Learning to Optimize

Ke Li and Jitendra Malik. ICLR 2017; inspected arXiv v1, 6 June 2016. DOI: null (publisher DOI not verified). [Canonical](https://arxiv.org/abs/1606.01885), [full text](https://arxiv.org/pdf/1606.01885). `FULL_TEXT_INSPECTED_ONLINE`; §§3.1–3.4, 4.1, Figure 1, PDF pp.2–6.

**SOURCE:** Other/continuous optimization, not image watermark insertion. **R-full:** guided policy search; state includes iterate, historical objectives and gradients; action is update vector; cost is current objective, hence reward its negative; finite horizon. Training samples 20 trajectories of 40 steps per objective each policy-search iteration (§3.4). Logistic-regression evaluation trains on 90 objectives and tests 100; comparators are tuned gradient descent, momentum, conjugate gradient and L-BFGS (§4.1). Figure 1 reports faster early progress, but L-BFGS ultimately reaches slightly better minima. Six percent of objectives with diverging/oscillating comparison methods are excluded from the averaged margin plot. No reliable numeric objective gain is extracted from curves. Total meta-training wall-clock cost is not established here. This is genuinely RL despite using gradients as observations.

**JUDGMENT:** Pre-empts “learn the writer update as an RL policy.” Supports finite-horizon acceleration as a hypothesis, not unseen-regenerator robustness or equal-total-budget superiority.

### C06-02 — Learning to Optimize Neural Nets

Ke Li and Jitendra Malik. 2017 arXiv preprint; inspected v2, 30 November 2017; DOI: null. [Canonical](https://arxiv.org/abs/1703.00441), [full text](https://arxiv.org/pdf/1703.00441). `FULL_TEXT_INSPECTED_ONLINE`; §§3.1–3.2, state/observation features in §3 (p.6), §4 and Figures 1–5 (pp.6–8).

**SOURCE:** Other/neural-network training. **R-full:** history-derived objective, gradient and iterate features; action is parameter-step vector; trajectory meta-loss sums objective values (§3.1); observations are cheaper/noisier than training state features. Meta-training uses a projected-MNIST network with 48 inputs/48 hidden units, horizon 400 and batch 64 (§4). Tests transfer to TFD, CIFAR-10/100, larger networks and different batches. Comparators include Adam, RMSprop, AdaGrad, momentum, L-BFGS and Andrychowicz's learned optimizer. Figure 2 changes to 100 input/200 hidden units; Figure 5 evaluates 800 iterations. Reported objective curves favor Predicted Step Descent, while the competing learned optimizer can diverge on changed tasks. No exact numerical objective effect or equal-total-compute advantage is extracted; full meta-training cost unavailable in inspected evaluation. These are shallow training problems, not watermark constraints.

**JUDGMENT:** Occupies transfer of RL-learned optimizer rules; its favorable transfer prevents assuming all optimizer policies necessarily fail outside training, but gives no guarantee for foreign diffusion families.

### C06-03 — Learning to learn by gradient descent by gradient descent

Marcin Andrychowicz, Misha Denil, Sergio Gómez Colmenarejo, Matthew W. Hoffman, David Pfau, Tom Schaul, Brendan Shillingford, Nando de Freitas. NeurIPS 2016 proceedings PDF; DOI: null. [Canonical](https://proceedings.neurips.cc/paper/2016/hash/fb87582825f9d28a8d42c5e5e5e8b23d-Abstract.html), [full text](https://proceedings.neurips.cc/paper/6461-learning-to-learn-by-gradient-descent-by-gradient-descent.pdf). `FULL_TEXT_INSPECTED_ONLINE`; §2, Eq.3, §2.1, §§3–3.2, Figures 4–6.

**SOURCE:** Other/optimization including neural training; **comparator-not-RL**, differentiable meta-learning. A coordinatewise LSTM consumes gradients and recurrent memory and emits updates; the outer loss sums inner objectives. RL state/action/reward: N/A. Truncated BPTT drops second-derivative terms. Experiments use two-layer LSTMs with 20 units per layer; inner training lasts 100 steps with 20-step unrolls (§3). SGD, Adam, RMSprop and NAG receive learning-rate tuning. Figure 4 shows successful continuation to 200 steps; Figure 5 shows failure to generalize when the optimizee changes from sigmoid to ReLU. Exact curve differences and amortized cost are not recoverable as trustworthy numeric effect sizes from inspected text. Optimizer validation chooses the checkpoint, so meta-training/selection is a real additional budget.

**JUDGMENT:** A learned pre-encoder update need not be RL. This is an essential learned non-RL control arm if an RL writer loop claims the benefit comes from sequential credit assignment.

### C06-04 — Learned Optimizers that Scale and Generalize

Olga Wichrowska, Niru Maheswaranathan, Matthew W. Hoffman, Sergio Gómez Colmenarejo, Misha Denil, Nando de Freitas, Jascha Sohl-Dickstein. ICML 2017, PMLR 70:3751–3760; proceedings PDF; DOI: null. [Canonical](https://proceedings.mlr.press/v70/wichrowska17a.html), [full text](https://proceedings.mlr.press/v70/wichrowska17a/wichrowska17a.pdf). `FULL_TEXT_INSPECTED_ONLINE`; §§3.1–3.2, 4.1.5–4.5, 5.2–5.6; Figures 2,4,6,7.

**SOURCE:** Other/neural optimization. **Comparator-not-RL**: hierarchical parameter/tensor/global GRUs, gradient-history features, average-log-loss meta-objective, backpropagation through partial unrolls including second derivatives. RL tuple: N/A. Heavy-tailed training horizons encourage extrapolation. §4.5 reports at least 40 million meta-iterations across 1,000 workers. Adam/RMSprop and momentum are comparison methods. §5.3/Figure 4b: Inception/ResNet training is stable for the first 10K–20K steps, but later progress stalls; Inception loss approaches approximately 6.5. No precise cross-method loss delta is extracted. §5.6 reports worse wall-clock performance at small minibatches, with overhead shrinking at larger batches. Task-transfer gains and deployment efficiency therefore differ.

**JUDGMENT:** Occupies hierarchy, gradient memory and horizon randomization. A single-image writer must measure actual seconds; lower step counts alone are inadequate. Late failure also motivates evaluating the precise intended stopping horizon.

### C06-05 — Learning-Rate-Free Learning by D-Adaptation

Aaron Defazio and Konstantin Mishchenko. ICML 2023, PMLR 202:7449–7479; proceedings PDF; DOI: null. [Canonical](https://proceedings.mlr.press/v202/defazio23a.html), [full text](https://proceedings.mlr.press/v202/defazio23a/defazio23a.pdf). `FULL_TEXT_INSPECTED_ONLINE`; §1/Algorithm 1, §4 and §6 passages, Figure 3, Table 1 and §§7.1–7.2.

**SOURCE:** Other/convex optimization and neural training. **Comparator-not-RL**; no state/action/reward policy or meta-training. The method grows a lower estimate of distance to a solution to adapt step scale, without extra gradient/function evaluations. Convex deterministic theory does not directly prove stochastic deep-network behavior. Figure 3 gives GPT BookWiki test perplexity 19.46 (SE .019) for D-Adapt Adam versus 19.49 (.012) for Adam; IWSLT14 test loss is slightly worse, 4.33 versus 4.31. These are comparisons with literature/code baseline rates, whose tuning granularity the authors say is unknown (§7.2). Table 1 reports rates, not accuracy. No controller-training cost is required; other training choices remain. Numerical effects are not watermark evidence.

**JUDGMENT:** Directly pre-empts adaptive learning rate as an RL contribution. Useful cheap comparator alongside tuned Adam, with the caveat that its convergence theorem does not cover the constrained nonconvex writer.

### C06-06 — DoG is SGD's Best Friend: A Parameter-Free Dynamic Step Size Schedule

Maor Ivgi, Oliver Hinder, Yair Carmon. ICML 2023, PMLR 202:14465–14499; proceedings PDF; DOI: null. [Canonical](https://proceedings.mlr.press/v202/ivgi23a.html), [full text](https://proceedings.mlr.press/v202/ivgi23a/ivgi23a.pdf). `FULL_TEXT_INSPECTED_ONLINE`; DoG formula, §3/Proposition 3.9/Theorem 3.10, §§4.1–4.7, Table 1.

**SOURCE:** Other/optimization; **comparator-not-RL**, RL tuple N/A. Step size uses maximum displacement from initialization divided by accumulated gradient norm. T-DoG has convex stochastic guarantees; ordinary DoG and layerwise DoG empirical behavior must not be confused with that theorem. Main evaluation uses tuned cosine/warmup baselines and five seeds (§4.1). Table 1, CLIP ViT-B/32 ImageNet after 25K steps with averaging: L-DoG 80.12% top-1, best listed AdamW 79.01%, DoG 77.22%, best listed SGD 77.54%. Without averaging, L-DoG 78.20% trails best AdamW 79.04%. §4.6 reports a counterexample where L-DoG is worse than tuned Adam from scratch. No meta-training; averaging and remaining choices matter.

**JUDGMENT:** Strong analytic schedule control, not proof it is best for image perturbations. Include a displacement-aware schedule before attributing gains to a policy's learning.

### C06-07 — Is Scaling Learned Optimizers Worth It? Evaluating The Value of VeLO's 4000 TPU Months

Fady Rezk, Antreas Antoniou, Henry Gouk, Timothy M. Hospedales (author order from inspected PMLR PDF). I Can't Believe It's Not Better 2023 workshop, PMLR 239; proceedings PDF; DOI: null. [Canonical](https://proceedings.mlr.press/v239/rezk23a.html), [full text](https://proceedings.mlr.press/v239/rezk23a/rezk23a.pdf). `FULL_TEXT_INSPECTED_ONLINE`; §§4–6, Tables 1–2, Figure 1.

**SOURCE:** Other/optimizer evaluation; **comparator-not-RL**, no policy-learning tuple. Compares VeLO with Adam, heavy-ball, Nesterov, NAdam and NAdamW on four MLCommons workloads, distinguishing fixed steps, fixed seconds and time-to-target. Table 1: VeLO's 75%-horizon prompt reaches Criteo training target in 6,088 seconds where the 100% prompt times out; OGBG reverses this, with 100% reaching target in 13,215 seconds and 75% timing out. Table 2 ImageNet training loss: VeLO .1046 versus Adam .0470; validation: VeLO 1.5017 versus Adam 1.9438. Thus a method can improve generalization while minimizing training loss worse. Baselines use defaults, no HPO. The four-workload scope limits broad rejection; VeLO also wins some endpoints. Pretraining cost must be amortized over new tasks, not reused meta-training tasks.

**JUDGMENT:** Pre-empts simplistic “fewer steps means a better optimizer.” A writer trial should preregister terminal acceptance and strict quality, plus wall-clock totals including policy search.

### C06-08 — Celo2: Towards Learned Optimization Free Lunch

Abhinav Moudgil, Boris Knyazev, Eugene Belilovsky. ICLR 2026 listed by author release; inspected arXiv v1, 22 February 2026, not publisher-final PDF (OpenReview challenge). DOI: null. [Canonical](https://arxiv.org/abs/2602.19142), [full text](https://arxiv.org/html/2602.19142v1). `FULL_TEXT_INSPECTED_ONLINE`; §3/Algorithm 1, §4/implementation and §4.1, §5/Table 1, Appendix D/PES.

**SOURCE:** Other/neural optimization. **Comparator-not-RL:** PES estimates meta-gradients; evaluating it as the optimizer of PPO does not make optimizer learning RL. Small MLP emits normalized update directions; step size remains tunable, with optional orthogonalization and distinct AdamW components. Meta-training uses four tiny image-MLP tasks, 100–2,000-step unrolls, 50-step truncations; reported cost 4.5 GPU-hours (§§3–4). Evaluation sweeps seven learning rates except VeLO's default horizon mode. Figure 2/§4.1: ImageNet-ViT reaches VeLO's final loss in approximately half the steps, not a demonstrated half wall-clock cost. Table 1c task augmentation changes validation loss 4.417 to 3.812. Figure 3: PPO returns comparable to tuned AdamW, not universally superior. Meta-training budget excludes the large TPU evaluation and tuning.

**JUDGMENT:** Counters blanket claims that learned optimizers always need enormous training budgets. It strengthens the non-RL comparator, not the novelty of RL, and does not establish feasibility of training on expensive regeneration feedback.

### C06-09 — VeLO: Training Versatile Learned Optimizers by Scaling Up

Luke Metz et al.; [canonical full author list](https://arxiv.org/abs/2211.09760). 2022 arXiv preprint; inspected v1, 17 November 2022, HTML. DOI: 10.48550/arXiv.2211.09760 (repository DOI, not a journal DOI). [Full text](https://arxiv.org/html/2211.09760). `FULL_TEXT_INSPECTED_ONLINE`; §2, §§3.1–3.3, §§4.1–4.3.7; Figure 4, Figures 6/8.

**SOURCE:** Other/neural optimization. **Comparator-not-RL:** ES meta-gradients of final training loss; RL tuple N/A. Per-tensor LSTM generates per-parameter MLP weights; features include gradients, moment statistics, loss and fraction of training completed. Full trajectories are evaluated; §3.3 reports approximately four weeks using 1K–4K TPU accelerators. §4.1 contrasts learning-rate tuning with 1,000-trial NAdamW search; these are separate comparison budgets. Figure 4 reports matching/beating best tuned Adam on five of six MLCommons workloads, except OGBG. §4.2 uses 20 random baseline trials and also evaluates 75%-duration VeLO. Exact endpoint deltas not reliably extracted. Figure 6 shows weaker scaling to the largest ViT; Figure 8 reports batch-dependent reversals versus Adafactor. Terminal-loss optimization can intentionally plateau or increase intermediate loss (§3.3).

**JUDGMENT:** Occupies horizon-conditioned learned schedules and rich update rules. Encourages terminal reward design but warns that greedy intermediate stopping may invalidate a policy trained for a particular horizon. C06-07 gives an independent narrower counterevaluation.

## Access barriers and uncounted leads

- OpenReview Celo2 PDF opened to a browser-verification challenge. The arXiv v1 HTML supplied full method/evaluation access. This is a resolved access barrier, not a tenth paper.
- VeLO PDF request failed because content length was too large (27,854,150 bytes); arXiv HTML v1 supplied substantive access. No paper was downloaded.
- Q06's Closer Look and reverse-engineering work, Q04's guard/pathology/tradeoff papers, and Q07's Prodigy are relevant **UNINSPECTED** leads, not exhausted or counted. The paper floor is met without claiming the field exhausted.
- [Efficient Long-Horizon Learning for Learned Optimization](https://arxiv.org/abs/2607.06772) surfaced in Q13–14. **UNINSPECTED** newer preprint lead; no numerical performance claim adopted from its snippet or mirrors. It is a priority follow-up if the final candidate specifically hinges on long-horizon meta-training. Secondary mirrored metadata disagreed on dates; use the primary record before citing.
- Q09 ACM matches are excluded for topic mismatch. Q12 did not identify the sought controller. Daniel/Taylor/Nowozin's step-size-controller work is mentioned in inspected reference lists but is **UNINSPECTED**, not silently counted.
- ArXiv/proceedings duplicates and search snippets count zero additional cards. None of these nine papers establishes post-hoc content-bound image watermarking under diffusion regeneration.

## Cluster synthesis and project consequences

**SOURCE synthesis:** C06-01/02 provide actual RL precedents; C06-03/04 and C06-08/09 show learned optimizer behavior can come from differentiable or evolutionary meta-learning. C06-05/06 provide cheap analytic adaptation. C06-07 demonstrates that endpoint, horizon prompt, workload distribution, tuning and time-versus-step accounting can reverse conclusions. These are occupied ingredients, not an identical watermark construction.

**JUDGMENT — what could beat a strong non-RL alternative:** A P4 policy is plausible only if available history predicts useful changes that a tuned fixed/analytic schedule misses, with enough related future writes to amortize training. The simplest relevant control is the unchanged writer with tuned Adam and a fixed budget; add a no-training adaptive step-size arm before adding a complex learned comparator. A small learned non-RL direction/schedule is a fair additional arm if claiming that RL rather than learned specialization causes the gain. Celo2 makes a categorical “learned optimizer training is necessarily unaffordable” argument untenable, but its tiny surrogate tasks do not price this project's costly regeneration rewards.

**JUDGMENT — P1/P2/P3 readings:** P1 (choose settings before marking) is often a one-shot contextual selection problem and needs a bandit/supervised baseline rather than a full optimizer MDP. P2 (region/frequency allocation) could use learned coordinatewise updates, but the cards pre-empt that mechanism and provide no evidence of security-preserving allocation. P3 (choose transforms/surrogates per writer step) becomes a genuine sequential policy only when early choices alter later useful states; test random/static mixtures and gradient-trained weighting under the same budget. A learned optimizer cannot itself supply missing evidence about an excluded regenerator family.

**JUDGMENT — finite-budget accounting:** Charge optimizer/policy training, trial selection, controller execution, all failed rollouts and the final write; distinguish cost for one image from amortized deployment over N new images. A break-even claim requires `training cost < N × (baseline per-image cost − policy per-image cost)` with positive measured savings, plus equal acceptance/security/quality. This is a derived accounting identity, not a measured break-even N. No cross-hardware conversion of paper TPU/GPU time to the project's instance-hours is justified here.

**JUDGMENT — scientific bar:** Preserve strict PSNR >35, SSIM >.9, LPIPS <.1 and assess T3, T4 and T5 separately. None of the source losses is C/J acceptance, ownership binding, or a false-positive guarantee. Hold a diffusion family out of policy training and all tuning; success on different shallow classification datasets does not stand in for that test. A prospective RL-vs-gradients null result is defensible; attaching RL to existing frozen results is not. Conditional on F6 GO, this is an efficiency/complement study; on failure, diagnose the carrier/reader before optimizing its loop; on RESOURCE_STOP, the literature alone cannot resolve feasibility.

## Counts

- Distinct full-text method+evaluation inspected papers: **9** (C06-01 through C06-09); floor 8 met.
- Actual classes: **2 R-full, 0 R-bandit, 7 comparator-not-RL**. Among the seven are two analytic optimizers and one independent evaluation, all within learning-to-optimize scope.
- Actual distinct queries: **14**; query submissions including repeats: **20**; scholarly index/site contents queried indirectly: **6**, of which ACM returned only irrelevant matches. No native-index-search claim.
- Identical-task evidence for RL-controlled post-hoc content-bound image marking under unseen diffusion regeneration: **0 in this cluster**. This is a bounded retrieval result, not an absence or first-ever claim.
