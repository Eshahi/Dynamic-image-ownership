# C7 — Per-image adaptive settings, contextual bandits, and logged-data evaluation

Access date: 2026-10-30. Author: Codex research subagent `wp2_c7`. Research only; PHASE_B_JOURNALS=off. No run files, F6 outcomes, scientific execution, downloads, installations, or git mutations were used. Only this file was written. The main agent supplied the data-design fact that old development tables contain every arm/source/cell and lack randomized behavior propensities; this file does not independently audit those tables.

## Search and inspection accounting

**8 distinct FULL_TEXT_INSPECTED_ONLINE papers; floor 8 met. 14 distinct meaningful query strings; 26 actual query submissions including 12 exact repeats. Six scholarly index contents targeted indirectly: arXiv, PMLR, ACM DL, OpenReview, DBLP, IEEE Xplore.** These are web `search_query` searches with `site:` restrictions, not native index searches. Two follow-ups used general web discovery. Index targeting is not a claim of complete coverage, and no exhaustion or absence-of-prior-art claim is made.

All Q01–Q12 were submitted once in grouped batches, then repeated individually with shorter responses to recover untruncated provenance. R01–R12 below are these actual repeated submissions, not additional distinct queries. Q13–Q14 were submitted together after access failures. Exact strings:

| IDs, including repeated submissions | Exact query | Route / index | Returned primary lead and disposition |
|---|---|---|---|
| Q01, R01 | `site:arxiv.org contextual bandit doubly robust policy evaluation learning Dudik 2011` | Indirect arXiv | [1103.4601](https://arxiv.org/abs/1103.4601), inspected C07-01; [1503.02834](https://arxiv.org/abs/1503.02834), extension not separately counted. |
| Q02, R02 | `site:arxiv.org contextual bandit bake off Bietti Agarwal Langford 2021` | Indirect arXiv | [1802.04064](https://arxiv.org/abs/1802.04064), C07-02; [1402.0555](https://arxiv.org/abs/1402.0555), uninspected adjacent lead. |
| Q03, R03 | `site:arxiv.org Exposure white box photo post processing framework reinforcement learning` | Indirect arXiv | [1709.09602](https://arxiv.org/abs/1709.09602), C07-03; [2404.01636](https://arxiv.org/abs/2404.01636), camera-control lead, not inspected. |
| Q04, R04 | `site:proceedings.mlr.press doubly robust off policy evaluation shrinkage 2020` | Indirect PMLR | [su20a](https://proceedings.mlr.press/v119/su20a.html), C07-04; [kallus20b](https://proceedings.mlr.press/v119/kallus20b.html), sequential-OPE lead not inspected. |
| Q05, R05 | `site:proceedings.mlr.press optimal adaptive off policy evaluation contextual bandits Wang Agarwal Dudik` | Indirect PMLR | [wang17a](https://proceedings.mlr.press/v70/wang17a.html), C07-05; su20a duplicate. |
| Q06, R06 | `site:proceedings.mlr.press counterfactual risk minimization logged bandit feedback` | Indirect PMLR | [swaminathan15](https://proceedings.mlr.press/v37/swaminathan15.html), C07-06. |
| Q07, R07 | `site:dl.acm.org contextual bandit approach personalized news article recommendation Li 2010` | Indirect ACM DL | Returned [10.1145/3598301](https://dl.acm.org/doi/pdf/10.1145/3598301), adaptive physiological sampling; intended Li paper not recovered in displayed results. Off-topic lead not counted. |
| Q08, R08 | `site:dl.acm.org unbiased offline evaluation contextual bandit algorithms Li 2011` | Indirect ACM DL | Same [10.1145/3598301](https://dl.acm.org/doi/pdf/10.1145/3598301) lead; failed intended retrieval, no card. |
| Q09, R09 | `site:openreview.net off policy evaluation contextual bandit deficient support` | Indirect OpenReview | [SklcyJBtvB](https://openreview.net/pdf?id=SklcyJBtvB), browser challenge on open; author/arXiv alternative found in Q13, C07-07. Also [supplement](https://openreview.net/attachment?id=uFSrUpapQ5K&name=supplementary_material), not inspected. |
| Q10, R10 | `site:openreview.net per image adaptive image enhancement reinforcement learning` | Indirect OpenReview | [pgQCsyKdpN](https://openreview.net/pdf?id=pgQCsyKdpN), browser challenge on open; recovered through Q14, C07-08. |
| Q11, R11 | `site:dblp.org Exposure White-Box Photo Post-Processing Framework` | Indirect DBLP | [Hu author record](https://dblp.org/pid/204/4110.html) and [TOG record](https://dblp.org/rec/journals/tog/HuHXWL18), metadata corroboration for C07-03, not another paper. |
| Q12, R12 | `site:ieeexplore.ieee.org contextual bandit adaptive image enhancement parameter selection` | Indirect IEEE Xplore | [10192479](https://ieeexplore.ieee.org/document/10192479/), generic model selection, not inspected; [8803231](https://ieeexplore.ieee.org/document/8803231/), image denoising parameter-selection lead in first submission, abstract only; no card. |
| Q13 | `"Off-Policy Bandits with Deficient Support" arxiv` | General web discovery | [2006.09438](https://arxiv.org/abs/2006.09438), C07-07; [Cornell author PDF](https://www.cs.cornell.edu/~tj/publications/sachdeva_etal_20a.pdf), available alternative lead. |
| Q14 | `"AdaptiveISP" arxiv` | General web discovery | [2410.22939](https://arxiv.org/abs/2410.22939), C07-08. |

Access barriers: the two OpenReview PDFs returned browser-verification pages, not papers. Exposure's arXiv PDF timed out; arXiv HTML v2 worked. AdaptiveISP HTML v2 returned 404; v1 worked. No barrier was bypassed. Publisher-final versions were not presumed identical to inspected preprints. Search snippets and abstract-only leads do not count as full-text inspections.

## Inspected cards

All cards below have status **FULL_TEXT_INSPECTED_ONLINE**, access date **2026-10-30**. SOURCE blocks are compact source-derived paraphrases; JUDGMENT blocks are project-specific inference. DOI `null` means not verified, rather than no DOI exists. No source quotation is used.

### C07-01 — Doubly Robust Policy Evaluation and Learning

Miroslav Dudík, John Langford, Lihong Li. ICML 2011. DOI: null. [Canonical](https://arxiv.org/abs/1103.4601); [inspected PDF v2, 6 May 2011](https://arxiv.org/pdf/1103.4601). Read §§2–4, Eq.1, Theorems 1–2, §5.1, Tables 1–3 (PDF pp.2–6).

**SOURCE.** Other-domain offline contextual-bandit evaluation/learning; **R-bandit**, horizon one per context. Context is a feature vector; action a label/treatment; reward observed success or classification loss. DR combines a reward predictor and propensity-weighted residual. Its bias involves both nuisance errors; data splitting keeps fitted models separate from evaluation. Comparators: direct method and IPS. In Table 2, letter classification-error RMSE is DR .030 versus IPS .049 and DM .213; pendigits reverses the DR/IPS ordering, .016 versus .015. §5.1 uses uniform known action probabilities and 500 evaluation replicates. Comparable total compute budget is not reported. Occupied ingredient: DR contextual-policy evaluation. Limits: identification assumptions and reward-model quality matter; this is not watermark evidence.

**JUDGMENT.** Do not invent a historical propensity to attach this estimator to deterministic full-information development sweeps.

### C07-02 — A Contextual Bandit Bake-off

Alberto Bietti, Alekh Agarwal, John Langford. Inspected arXiv v5, 4 June 2021; initial preprint 2018; journal-final venue not independently verified here. DOI: null. [Canonical](https://arxiv.org/abs/1802.04064); [PDF](https://arxiv.org/pdf/1802.04064). Read §§2.1–2.3, §4 evaluation setup, Tables 1–2 and surrounding interpretation, §5 practitioner guidance.

**SOURCE.** Other-domain online **R-bandit** benchmark: feature context, label/action, immediate loss; no action-dependent next context. Supervised datasets become bandit problems by hiding other actions' losses. Methods include Greedy, RegCB, Cover, bootstrap/Thompson approximations and epsilon-greedy. Table 2(a), RCV1 progressive-validation loss: Greedy .215±.010, RegCB-optimistic .225±.008, Cover-NU .215±.006, bootstrap-greedy .251±.005, epsilon-greedy .230±.009; errors are standard errors across ten reshufflings. Overall rankings depend on representation, loss encoding and tuning. Some deterministic methods produce unsuitable logs for later OPE. Total training/tuning costs are not matched to watermark rollouts. Occupied ingredient: simple greedy and regression-oracle comparators. Limits: supervised-to-bandit simulation, not deployment or diffusion robustness.

**JUDGMENT.** Greedy supervised selection is a mandatory baseline; a bandit label alone is not evidence of added value.

### C07-03 — Exposure: A White-Box Photo Post-Processing Framework

Yuanming Hu, Hao He, Chenxi Xu, Baoyuan Wang, Stephen Lin. ACM TOG 37(2), article 26, 2018 (DBLP corroboration). DOI: null; the inspected HTML contains a placeholder DOI, not a usable identifier. [Canonical](https://arxiv.org/abs/1709.09602); [HTML v2, 6 February 2018](https://arxiv.org/html/1709.09602). Read §§3.2,4.1–4.2,5.2 reward/learning,6 implementation and §6.1, Table 2.

**SOURCE.** Post-processing RAW images into styled photographs; **R-full**. State is the current image; action chooses a differentiable filter and continuous parameters; reward is discriminator-score improvement plus penalties. Five edits, discount one. Table 2, FiveK target style: user rating 3.43 versus CycleGAN 2.47, paired Pix2pix 3.37, expert 3.66. Histogram endpoints do not uniformly favor RL. §6 reports training under three hours, 30 ms inference on TITAN X, model below 30 MB; these are not an equal-budget controller ablation. Occupied ingredient: interpretable, per-image hybrid discrete/continuous processing policies. Limits: aesthetics and distribution matching, different supervision across baselines, no content binding or regeneration experiment.

**JUDGMENT.** Strong P3 architectural precedent, not a reason to claim that five watermark-writing actions outperform a differentiable selector.

### C07-04 — Doubly robust off-policy evaluation with shrinkage

Yi Su, Maria Dimakopoulou, Akshay Krishnamurthy, Miroslav Dudík. ICML 2020, PMLR 119:9167–9176. DOI: null. [Canonical](https://proceedings.mlr.press/v119/su20a.html); [conference PDF](https://proceedings.mlr.press/v119/su20a/su20a.pdf). Read §§2–3, Eq.3, §6.1.1–6.1.2, Tables 1–3, Figure 1 discussion.

**SOURCE.** Other-domain **R-bandit** OPE; context/action/reward triplets, horizon one. Shrinking DR importance weights trades bias for variance; target-action support under the logger remains assumed. Comparators include DM, self-normalized estimators and SWITCH. §6.1.1 uses 108 conditions, nine datasets, six loggers, deterministic/stochastic rewards, 500 replicates and clipped MSE. Table 3's oracle-tuned comparison with a squared-importance-weight regressor favors pessimistic shrinkage in 55 conditions and optimistic shrinkage in 29. This is an ablation win count, not deployment effect size. Figure 1 discussion reports degradation of DRs-upper under stochastic rewards. Total comparable compute is unavailable. Occupied ingredient: adaptive OPE bias/variance control. Limits: oracle tuning is explicitly distinguished; shrinkage cannot supply absent outcomes.

**JUDGMENT.** Useful only after a genuine logged-bandit design exists; finite-sample stabilization does not fix support or provenance.

### C07-05 — Optimal and Adaptive Off-policy Evaluation in Contextual Bandits

Yu-Xiang Wang, Alekh Agarwal, Miroslav Dudík. ICML 2017, PMLR 70:3589–3597. DOI: null. [Canonical](https://proceedings.mlr.press/v70/wang17a.html); [conference PDF](https://proceedings.mlr.press/v70/wang17a/wang17a.pdf). Read §2 support condition, §4.1–4.2, Eq.7, Theorem 2, §5 and Figures 1–2.

**SOURCE.** Other-domain **R-bandit** OPE; observed feature context, chosen label/action, bounded reward, horizon one. SWITCH uses importance-based evaluation for smaller weights and reward modeling for larger weights, choosing a threshold through a bias/variance criterion. Comparators: IPS, DM, DR, trimmed/truncated IPS and MAGIC-style tuning. §5 converts ten UCI datasets to bandits; a noisy condition reveals truth with probability .5 and otherwise a coin toss. Evaluation uses 500 bootstrap replicates and squared errors clipped at one. Figure 1 favors SWITCH-DR in aggregate, but no precise cross-method numerical effect is extracted from its curves. Dashed oracle curves tune on test error. Comparable compute not reported. Occupied ingredient: adaptive estimator selection. Limits: overlap and model error remain; this is not a policy's watermark robustness result.

**JUDGMENT.** State estimation uncertainty separately from uncertainty about novel writers or unseen regenerators.

### C07-06 — Counterfactual Risk Minimization: Learning from Logged Bandit Feedback

Adith Swaminathan, Thorsten Joachims. ICML 2015, PMLR 37:814–823. DOI: null. [Canonical](https://proceedings.mlr.press/v37/swaminathan15.html); [conference PDF](https://proceedings.mlr.press/v37/swaminathan15.pdf). Read §§3–4, Eq.1–2, §6 methodology and §6.1–6.2, Tables 2–3.

**SOURCE.** Other-domain batch **R-bandit** policy learning; input features, structured-label action, Hamming-loss feedback, horizon one. CRM penalizes variance of clipped propensity-weighted empirical risk; POEM optimizes stochastic exponential-family policies. Table 3, TMC expected test Hamming loss: POEM(B) 2.197 versus IPS(B) 2.808; fully supervised CRF 1.189. Values average ten runs. Logging uses a CRF trained on a small supervised subset; generated feedback includes action propensities. §6.2 discusses batch versus stochastic optimization cost, but no watermark-equivalent budget is available. Occupied ingredient: variance-aware policy learning from partial feedback. Limits: full-information CRF has more information, explicitly acknowledged; simulated feedback does not establish watermark transfer.

**JUDGMENT.** With all measured arm outcomes available, give the supervised comparator that information instead of handicapping it to manufacture a bandit advantage.

### C07-07 — Off-policy Bandits with Deficient Support

Noveen Sachdeva, Yi Su, Thorsten Joachims. KDD 2020. DOI: **10.1145/3394486.3403139**. [Canonical](https://arxiv.org/abs/2006.09438); [inspected PDF v1, 16 June 2020](https://arxiv.org/pdf/2006.09438). Read §3.1–3.2 including Proposition 2, policy-restriction Eq.15–17, §4 setup, Figures 3–5 discussion, §5.

**SOURCE.** Other-domain offline **R-bandit** learning; context features, action, immediate reward, horizon one. Studies action restriction, reward extrapolation and policy restriction when the logger assigns zero probability to some actions. Extrapolation bias depends on unknown reward errors in unsupported regions. Evaluation converts CIFAR10 and credit-card data into support-deficient logs with separate learning/validation/test sets. Figure 3 compares accuracy as logged-data volume grows; no exact comparative effect is digitized from curves. §5 favors policy restriction while identifying regression misspecification risks for DR and extrapolation. Restricting actions can require costly evaluation of historical policies at inference. Occupied ingredient: explicit support-aware learning and limitations. No approach establishes arbitrary missing rewards without extra information.

**JUDGMENT.** Restrict current claims to measured arms/cells; assumptions about smooth interpolation are additional hypotheses, not recovered evidence.

### C07-08 — AdaptiveISP: Learning an Adaptive Image Signal Processor for Object Detection

Yujin Wang, Tianyi Xu, Fan Zhang, Tianfan Xue, Jinwei Gu. Inspected arXiv preprint v1, 30 October 2024; publisher-final venue not verified here. DOI: null. [Canonical](https://arxiv.org/abs/2410.22939); [HTML v1](https://arxiv.org/html/2410.22939v1). Read §§3.1–3.3, Eq.3–11, §4.1 and cost analysis, Tables 1,3,4.

**SOURCE.** Image ISP processing for detection; **R-full**, multi-stage processing horizon. State includes current image, module-use record and stage; actions select module/parameters; reward reduces frozen-detector loss with reuse/exploration/runtime penalties. Table 1, LOD mAP@.5: 71.4 versus adaptive Attention-aware Learning 70.9 and Hyperparameter Optimization 70.1. Table 4 changes runtime penalty from zero to .1: mAP@.5 71.4→69.9 and time 14.73→9.20 ms. Table 3 includes detectors absent from training. Occupied ingredient: per-image module selection and accuracy/cost control. Limits: detector performance rather than strict image fidelity; runtime is not total training/tuning budget, and cross-detector transfer is not unseen diffusion-family transfer.

**JUDGMENT.** Relevant P1/P3 precedent with stronger adaptive baselines; cannot justify accepting destructive preprocessing under the thesis's quality constraints.

## C7 synthesis: what the literature supports here

**No inspected paper demonstrates that RL beats the strongest simple non-RL alternative under equal total budget for post-hoc content-bound image watermarking against diffusion regeneration.** The papers occupy adaptive per-image processing, practical contextual selection, and off-policy estimation ingredients. They do not jointly establish the required construction or its T3/T4/T5 claims. This is a scoped evidence conclusion, not a first-ever claim.

### Existing data: full-information selection, not retrospective bandit logs

Project-specific inference from the supplied complete-arm design:

1. For an observed source/cell, a frozen policy choosing among measured arms can be scored directly by the corresponding measured outcome. A stochastic policy can use its weighted sum across those arms. No IPS denominator is required. The resulting quantity describes this measured table, not novel-action outcomes or a broader image population automatically.
2. Train/tune a selector on one development partition and evaluate it on disjoint development sources; cluster repeated attack seeds/cells by source. Any apparent gain from choosing each row's best observed arm is an oracle upper bound, not a deployable policy result. Unseen-family claims need a genuinely excluded regenerator family; image separation alone is insufficient.
3. Only decision-time features are legitimate. An oracle that uses regeneration outcomes or a future detector score to choose the writer leaks unavailable information. In this session, new image features requiring encoder computation cannot be acquired; unavailable context remains unavailable.
4. Fitting frequencies to a designed sweep does not reconstruct randomized behavior propensities. Since every arm was measured, missing propensities are not a defect for direct full-information comparisons. They are a reason not to rename these comparisons IPS/DR OPE. If some cells are missing, neither a fitted propensity nor DR makes their outcomes observed.
5. New writers, new strengths outside the measured set, changed carriers, unobserved intermediate states, and policy-induced trajectories are unsupported. Reward-model interpolation requires a testable structural assumption; an outcome at the end of one fixed run does not identify the effect of an alternative intermediate action. PHASE_B_JOURNALS=off supplies no additional permission or trajectory evidence.

### Which policy locations are plausible?

| Location | C7 interpretation | Simplest strong comparator | Evidence required before an RL claim |
|---|---|---|---|
| P1: choose settings before marking | One-shot image/context-to-arm mapping. Full-information supervised selection for the current table; R-bandit only if future collection observes selected arms alone. | Best fixed feasible arm; shallow/linear reward regressor or small decision rule; contextual greedy selection. | Out-of-source gain, stable arm heterogeneity, decision-time features and net benefit after feature/selection cost. |
| P2: allocate regions/bands | A single allocation vector can still be a supervised or differentiable action; repeated updates are not automatically RL. | Fixed allocation, constrained gradient optimization, small equal-budget search. | Observable local state, meaningful allocation heterogeneity, hard fidelity feasibility, and actions changing subsequent decision opportunities. |
| P3: select transforms within writing | Potential R-full when current image/optimization state changes the value of later choices. Adjacent image-processing architectures already exist. | Fixed schedule, greedy one-step choice, direct differentiable parameter controller, equal-budget random search. | Ablate sequential credit assignment against these controls; count all training, tuning and inference calls; independently test unseen-family transfer. |

For future genuinely partial-feedback development collection, predefine allowed arms, probabilities bounded away from zero on target support, recorded contexts/actions/rewards/costs, and stopping/tuning rules. OPE then estimates a specified fixed policy under its assumptions; it does not certify privacy, binding, image quality, or adversarial security. Known support permits IPS/DR; clipping, SWITCH or shrinkage changes the bias/variance tradeoff. None is a substitute for evidence in unobserved regions. This is a research recommendation only, not authorization to collect data or implement infrastructure.

Strict PSNR/SSIM/LPIPS feasibility should be enforced before optimizing a selection score; a higher average reward cannot compensate for an image failing a hard quality gate. Selection must retain C0/wrong-owner controls and separately examine T4 copy-paste and T5 semantic collision. A policy that picks a stronger known-surrogate setting may amplify overfitting rather than repair a carrier's transfer failure. Registry access, original-image access, keys, and any chosen-image descriptors must be disclosed as detector or writer side information.

## Uncounted leads and coverage limits

- Related versions of Dudík's work were deliberately not added to inflate the count. No C9 Active Testing, TTA, confidence-sequence, conformal-risk or e-value paper is included.
- `Taming the Monster` and `Double Reinforcement Learning` remain relevant uninspected leads. They are not evidence claims in this dossier.
- The IEEE denoising-parameter-selection lead is potentially useful for a non-RL image controller, but only its abstract was retrieved. It contributes no inspected card.
- The ACM personalized-news queries returned irrelevant adaptive physiological-sampling material in displayed results. Those searches are recorded as retrieval failures, not successful inspections of the intended Li papers.
- OpenReview failures were recovered through author-hosted arXiv full text, but publisher-final changes are not verified. Counts are article-level, not URL-level. Exposure/AdaptiveISP may overlap C6 or another cluster; root should disclose any cross-cluster overlap.
- The retrieval establishes neither novelty nor exhaustion of per-image watermark selection. It supplies eight inspected conceptual/methodological comparators for C7 and makes the limits of old-data inference explicit.

**Final counts:** 8 inspected distinct papers; 2 image-processing R-full papers; 6 R-bandit learning/evaluation/benchmark papers; 14 distinct meaningful queries; 26 actual submissions including repeats; 6 indirectly targeted scholarly indexes; 0 experiment or held-out outcome accesses.
