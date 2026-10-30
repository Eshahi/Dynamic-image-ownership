# C3 — Learned augmentation versus random augmentation

Access date: 2026-10-30. Research-only, online inspection; no scientific execution, downloads, run-data access, or git operations. PHASE_B_JOURNALS=off. Scope is augmentation-policy evidence, not a claim of watermark performance. SOURCE denotes a paper's report; DERIVED denotes arithmetic; JUDGMENT denotes project inference. Numerical differences below are percentage points, not relative percentages.

## Query log

All 15 queries below were actually issued through `web.run.search_query`. Every route is **INDIRECT_INDEX_SEARCH**, using the literal `site:` restriction shown; none is a native-index search. Five scholarly index contents were searched: CVF, NeurIPS proceedings, PMLR, arXiv, OpenReview. Mixed batch results occasionally include out-of-domain discoveries; these do not count as native access or as successful retrieval from the intended index. Dates and snippets were not used as evidence without the subsequent full-text inspection.

| ID | Exact query | Index content | Primary result URLs and disposition |
|---|---|---|---|
| C3-Q01 | `site:openaccess.thecvf.com AutoAugment Learning Augmentation Strategies Data` | CVF | [AutoAugment](https://openaccess.thecvf.com/content_CVPR_2019/html/Cubuk_AutoAugment_Learning_Augmentation_Strategies_From_Data_CVPR_2019_paper.html), new C03-01. CVF PDF returned 403; arXiv fallback inspected. |
| C3-Q02 | `site:papers.nips.cc RandAugment Practical automated data augmentation reduced search space` | NeurIPS | [RandAugment](https://papers.nips.cc/paper/2020/hash/d85b63ef0ccb114d0a3bb7b7d808028f-Abstract.html), new C03-02; proceedings PDF inspected. |
| C3-Q03 | `site:proceedings.mlr.press Population Based Augmentation Efficient Learning Augmentation Policy Schedules` | PMLR | [PBA](https://proceedings.mlr.press/v97/ho19b.html), new C03-04; PDF inspected. |
| C3-Q04 | `site:arxiv.org Fast AutoAugment DADA Faster AutoAugment` | arXiv | [Fast AA](https://arxiv.org/abs/1905.00397), [DADA](https://arxiv.org/abs/2003.03780), [Faster AA](https://arxiv.org/abs/1911.06987), new C03-03/05/06. |
| C3-Q05 | `site:openreview.net TrivialAugment Tuning Free Yet State of the Art Data Augmentation` | OpenReview | No target record recovered in batch; tangential [ultrasound study](https://openreview.net/pdf?id=iGcxlTLIL5) not inspected or counted. TrivialAugment later recovered through CVF/arXiv. |
| C3-Q06 | `site:openaccess.thecvf.com UniformAugment Search Paradigm-Free Data Augmentation` | CVF | No target CVF full text recovered; indirect citations in [Domain Generalization by Rejecting Extreme Augmentations](https://openaccess.thecvf.com/content/WACV2024/papers/Aminbeidokhti_Domain_Generalization_by_Rejecting_Extreme_Augmentations_WACV_2024_paper.pdf). Batch also exposed [UniformAugment arXiv](https://arxiv.org/abs/2003.14348), new C03-08; not evidence of CVF-native retrieval. |
| C3-Q07 | `site:papers.nips.cc DADA Differentiable Automatic Data Augmentation` | NeurIPS | No matching DADA record; [DiffAugment](https://papers.nips.cc/paper_files/paper/2020/hash/55479c55ebd1efd3ff125f1337100388-Abstract.html) is a different paper and not counted. DADA recovered through Q04. |
| C3-Q08 | `site:arxiv.org SmartAugment efficient automated data augmentation` | arXiv | [Smart(Sampling)Augment](https://arxiv.org/abs/2111.00487), [Smart Augmentation](https://arxiv.org/abs/1703.08383), new leads, UNINSPECTED, not counted. |
| C3-Q09 | `site:openaccess.thecvf.com "TrivialAugment" "2021" Muller` | CVF | [TrivialAugment](https://openaccess.thecvf.com/content/ICCV2021/html/Muller_TrivialAugment_Tuning-Free_Yet_State-of-the-Art_Data_Augmentation_ICCV_2021_paper.html), new C03-07. PDF 403; arXiv fallback inspected. |
| C3-Q10 | `site:openreview.net "Adversarial AutoAugment"` | OpenReview | [AdvAA PDF](https://openreview.net/pdf?id=ByxdUySKvS), new C03-09; direct open redirected to browser challenge. ArXiv fallback inspected. |
| C3-Q11 | `site:arxiv.org "Faster AutoAugment" Hataya` | arXiv | [Faster AA](https://arxiv.org/abs/1911.06987), duplicate lead, authors verified. |
| C3-Q12 | `site:proceedings.mlr.press "UniformAugment"` | PMLR | No matching primary PMLR record returned; not a successful native or full-text search. Existing arXiv lead retained. |
| C3-Q13 | `site:arxiv.org "TrivialAugment"` | arXiv | [TrivialAugment](https://arxiv.org/abs/2103.10158), accessible fallback for C03-07. |
| C3-Q14 | `site:arxiv.org "Online Hyper-Parameter Learning"` | arXiv | [OHL-Auto-Aug](https://arxiv.org/abs/1905.07373), new lead; PDF partially examined, not counted as an inspected card. |
| C3-Q15 | `site:arxiv.org "Adversarial AutoAugment"` | arXiv | [AdvAA](https://arxiv.org/abs/1912.11188), fallback C03-09; [Challenges of Adversarial Image Augmentations](https://arxiv.org/abs/2111.12427), new C03-10, full text inspected. |

Additional operations were direct PDF opens, in-document finds, and arXiv metadata opens for version verification, not additional queries. No general-web query is included in the count.

## Inspected cards

### C03-01 — AutoAugment: Learning Augmentation Strategies From Data

- Metadata: Ekin D. Cubuk, Barret Zoph, Dandelion Mane, Vijay Vasudevan, Quoc V. Le. CVPR 2019. DOI: null. [Canonical record](https://openaccess.thecvf.com/content_CVPR_2019/html/Cubuk_AutoAugment_Learning_Augmentation_Strategies_From_Data_CVPR_2019_paper.html); [inspected PDF](https://arxiv.org/pdf/1805.09501v3). Access: 2026-10-30.
- Inspection: FULL_TEXT_INSPECTED_ONLINE; arXiv v3, 11 April 2019; §3, §4.1, §5.1, Tables 1–2. Publisher PDF blocked.
- SOURCE setting/class: image-classifier training augmentation, neither post-hoc marking nor generation-time watermarking; R-full sequence construction using PPO, operationally terminal-reward combinatorial search.
- SOURCE state/action/reward: RNN history of preceding decisions; operation, magnitude, application probability; child-model validation accuracy. About 15,000 policies evaluated (§3).
- SOURCE comparator/effect: CIFAR-10 WRN-28-10, §5.1: learned policy error 2.6±0.1%; best randomized policy 3.0%, averaged over five reruns after 20 randomized candidates. Table 1 estimates 5,000 P100 hours for CIFAR-10 search.
- Limits: random ablation does not match search budget. Paper explicitly separates augmentation-space contribution from optimizer choice.
- JUDGMENT pre-emption: P3 operation-sequence policy search is occupied. This supports searching good transformations, not an RL-specific watermark advantage; training-sequence construction alone is not evidence that physical writer dynamics need RL.

### C03-02 — RandAugment: Practical Automated Data Augmentation with a Reduced Search Space

- Metadata: Ekin Dogus Cubuk, Barret Zoph, Jonathon Shlens, Quoc V. Le. NeurIPS 2020. DOI: null. [Canonical record](https://papers.nips.cc/paper/2020/hash/d85b63ef0ccb114d0a3bb7b7d808028f-Abstract.html); [PDF](https://papers.nips.cc/paper_files/paper/2020/file/d85b63ef0ccb114d0a3bb7b7d808028f-Paper.pdf). Access: 2026-10-30.
- Inspection: FULL_TEXT_INSPECTED_ONLINE; NeurIPS proceedings PDF; §§3–4, Table 1, Figure 1, method pseudocode.
- SOURCE setting/class: image training augmentation; comparator-not-RL. State/action/reward: N/A as RL; choose operation count N and shared magnitude M, then sample operations uniformly; validation selects hyperparameters.
- SOURCE comparator/effect: Table 1 ImageNet EfficientNet-B7 top-1 accuracy: RA 84.7%, AA 84.3%, baseline 83.7%; CIFAR-10 PyramidNet both RA/AA 98.5%. Figure 1 varies model/data size; optimal magnitude changes. Footnote 5 reports random and grid magnitude search perform similarly.
- Limits: RA still requires hyperparameter trials; published-comparison table does not establish universally equal total compute. The distinct CVPR-workshop version has different headline numbers; not mixed here.
- JUDGMENT pre-emption: P3 reduced search and random surrogate selection are strong mandatory alternatives. Designing a useful transform space can matter more than learning a high-dimensional policy.

### C03-03 — Fast AutoAugment

- Metadata: Sungbin Lim, Ildoo Kim, Taesup Kim, Chiheon Kim, Sungwoong Kim. NeurIPS 2019 work; inspected preprint. DOI: 10.48550/arXiv.1905.00397. [Canonical/version record](https://arxiv.org/abs/1905.00397); [PDF](https://arxiv.org/pdf/1905.00397v2). Access: 2026-10-30.
- Inspection: FULL_TEXT_INSPECTED_ONLINE; v2, 25 May 2019; §§3.1–3.2.2, §4, Algorithm 1, Tables 1–2.
- SOURCE setting/class: image training augmentation; comparator-not-RL, TPE Bayesian search. State/action/reward: N/A as RL; search operation/probability/magnitude configurations against augmented-validation loss using already trained models and split-fold density matching.
- SOURCE comparator/effect: Table 2 CIFAR-10 WRN-28-10 error: Fast AA 2.7% (direct or transfer), AA 2.6%, Cutout 3.1%. Table 1 search: 3.5 V100 hours versus quoted 5,000 P100 hours for AA.
- Limits: hardware differs; costs concern policy search, not identical total training. Proxy density matching is not true future-regenerator feedback.
- JUDGMENT pre-emption: cached-surrogate evaluation and Bayesian policy search precede any P3 proposal. An expensive reward warrants avoiding repeated full evaluations before adding an RL controller.

### C03-04 — Population Based Augmentation: Efficient Learning of Augmentation Policy Schedules

- Metadata: Daniel Ho, Eric Liang, Xi Chen, Ion Stoica, Pieter Abbeel (canonical PMLR metadata order). ICML 2019, PMLR 97:2731–2741. DOI: null. [Canonical record](https://proceedings.mlr.press/v97/ho19b.html); [PDF](https://proceedings.mlr.press/v97/ho19b/ho19b.pdf). Access: 2026-10-30.
- Inspection: FULL_TEXT_INSPECTED_ONLINE; proceedings PDF; §§3.1–3.3, §4, Algorithm 1, Tables 1–2.
- SOURCE setting/class: image training augmentation; comparator-not-RL, population-based hyperparameter evolution. State/action/reward: N/A as RL; model weights, epoch and augmentation parameters are retained; worse members copy better members and perturb probability/magnitude schedules, ranked by validation performance.
- SOURCE comparator/effect: Table 2 CIFAR-10 PyramidNet+ShakeDrop error: PBA 1.46±0.077%, AA 1.48%; five model initializations. Table 1 search: PBA five Titan XP hours versus AA's estimated 5,000 P100 hours.
- Limits: unequal hardware; small error difference does not establish significance. Search costs exclude common final training.
- JUDGMENT pre-emption: changing transform schedules over time is already achievable without RL. P3/P4 novelty requires something beyond evolving a schedule and reusing prefix computation.

### C03-05 — DADA: Differentiable Automatic Data Augmentation

- Metadata: Yonggang Li, Guosheng Hu, Yongtao Wang, Timothy Hospedales, Neil M. Robertson, Yongxin Yang. Inspected arXiv preprint, 2020; publisher venue not independently verified here. DOI: 10.48550/arXiv.2003.03780. [Canonical record](https://arxiv.org/abs/2003.03780); [PDF](https://arxiv.org/pdf/2003.03780v3). Access: 2026-10-30.
- Inspection: FULL_TEXT_INSPECTED_ONLINE; v3, 30 July 2020; §§3.1–3.5, §4.1, Table 1, Eq.12.
- SOURCE setting/class: image training augmentation; comparator-not-RL, bilevel differentiable optimization with RELAX. State/action/reward: N/A as RL; categorical sub-policy and Bernoulli application distributions; validation objective and jointly updated network weights.
- SOURCE comparator/effect: Table 1 CIFAR-10 WRN-28-10 error: DADA 2.7%, AA 2.6%; search 0.1 Titan XP hour versus 5,000 P100 hours. §4.1 uses half reduced data for training, half for validation; 20 search epochs.
- Limits: cross-hardware estimates and different search procedures; RELAX's unbiased distribution-gradient estimator does not make the approximate magnitude derivative exact.
- JUDGMENT pre-emption: score-function/control-variate machinery is not automatically full RL. P3 must compare direct or relaxed gradient optimization wherever derivatives are available.

### C03-06 — Faster AutoAugment: Learning Augmentation Strategies using Backpropagation

- Metadata: Ryuichiro Hataya, Jan Zdenek, Kazuki Yoshizoe, Hideki Nakayama. Inspected arXiv preprint, 2019; publisher venue not independently verified here. DOI: 10.48550/arXiv.1911.06987. [Canonical record](https://arxiv.org/abs/1911.06987); [PDF](https://arxiv.org/pdf/1911.06987v1). Access: 2026-10-30.
- Inspection: FULL_TEXT_INSPECTED_ONLINE; v1, 16 November 2019; §§4.1–4.2, §§5.1–5.3, Tables 1, 3–6, Eqs.4–6.
- SOURCE setting/class: image training augmentation; comparator-not-RL, differentiable density matching. State/action/reward: N/A as RL; relaxed operation selection, approximate magnitude gradients, distribution-matching objective.
- SOURCE comparator/effect: Table 4 CIFAR-10 WRN-28-10 error: Faster AA and AA both 2.6%; Faster AA averages three runs. Table 1 search: 0.23 V100 hour versus quoted AA 5,000 P100 hours. Table 6 ImageNet top-1 error is 24.1→23.5% for Faster AA, while AA is 23.7→22.4%.
- Limits: ImageNet baselines differ, so the surrounding prose's stronger improvement language should not replace table values; not equal-budget evidence.
- JUDGMENT pre-emption: approximating otherwise discrete transform gradients is occupied. P3 needs comparison against such approximations, including their bias and native-feedback failures.

### C03-07 — TrivialAugment: Tuning-free Yet State-of-the-Art Data Augmentation

- Metadata: Samuel G. Müller, Frank Hutter. ICCV 2021. DOI: 10.48550/arXiv.2103.10158. [Canonical conference record](https://openaccess.thecvf.com/content/ICCV2021/html/Muller_TrivialAugment_Tuning-Free_Yet_State-of-the-Art_Data_Augmentation_ICCV_2021_paper.html); [PDF](https://arxiv.org/pdf/2103.10158v2). Access: 2026-10-30.
- Inspection: FULL_TEXT_INSPECTED_ONLINE; v2, 17 August 2021; §3/Algorithm 1, §§4.1.1–4.1.3, §4.2.1, Tables 3–6, Figure 3.
- SOURCE setting/class: image training augmentation; comparator-not-RL. State/action/reward: N/A; uniformly sample one operation and its strength per image; no policy-learning reward.
- SOURCE comparator/effect: Table 4, fixed-training CIFAR-100 WRN-28-10 accuracy: TA(RA) 83.54±0.12%, AA 82.91±0.41%, RA 83.1±0.32%. Table 3, augmented-batch setting: TA(Wide) 84.62±0.14% versus AdvAA 84.51±0.18%. §4.1.3/Figure 3 compares estimated total search-plus-training cost.
- Limits: augmentation spaces differ across variants; RA reproduction underperformed published scores; cost frontier uses estimates and selected architectures. These are not universal dominance or significance claims.
- JUDGMENT pre-emption: a well-designed random policy is essential. This is the cluster's strongest reason to demand matched training, operation space, batch multiplicity and total budget before attributing improvement to RL.

### C03-08 — UniformAugment: A Search-free Probabilistic Data Augmentation Approach

- Metadata: Tom Ching LingChen, Ava Khonsari, Amirreza Lashkari, Mina Rafi Nazari, Jaspreet Singh Sambee, Mario A. Nascimento; names as PDF front matter. arXiv preprint, 2020. DOI: null. [Canonical record](https://arxiv.org/abs/2003.14348); [PDF](https://arxiv.org/pdf/2003.14348v1). Access: 2026-10-30.
- Inspection: FULL_TEXT_INSPECTED_ONLINE; v1, 31 March 2020; §3, Algorithm 1, §§4–4.1, Tables 2–4.
- SOURCE setting/class: image training augmentation; comparator-not-RL. State/action/reward: N/A; uniform operations, continuous application probabilities and magnitudes; fixed operation count.
- SOURCE comparator/effect: Table 2 CIFAR-10 WRN-28-10 mean error: UA 2.67%, AA 2.6%, RA 2.7%; five UA runs. Table 3 CIFAR-100 same model: UA 17.18%, RA 16.7%. Search is absent; final training remains.
- Limits: approximately distribution-invariant transform space is assumed, not guaranteed for arbitrary transforms; comparator values mostly imported. No equal-total-budget reallocation study.
- JUDGMENT pre-emption: uniform randomization with bounded transformation strength is occupied. P3's safe action set matters, and P2 region allocation cannot inherit an invariance argument without content-binding and quality checks.

### C03-09 — Adversarial AutoAugment

- Metadata: Xinyu Zhang, Qiang Wang, Jian Zhang, Zhao Zhong. ICLR 2020. DOI: null. [Canonical OpenReview link](https://openreview.net/forum?id=ByxdUySKvS); [inspected PDF](https://arxiv.org/pdf/1912.11188v1). Access: 2026-10-30.
- Inspection: FULL_TEXT_INSPECTED_ONLINE; v1, 24 December 2019, carrying ICLR-2020 heading; §§3.2–3.3, §§4.1–4.2, Algorithm 1, Eqs.7–9, Tables 1–3. OpenReview PDF challenge; arXiv fallback.
- SOURCE setting/class: image training augmentation; R-game-style adversarial training with REINFORCE policy search. State: RNN decision history and changing target model via feedback; action: transform sequence/magnitudes; reward: normalized target training loss, maximized.
- SOURCE comparator/effect: Table 1 CIFAR-10 WRN-28-10 error: AdvAA 1.90±0.15%, AA 2.68%, PBA 2.58%; five initializations (§4.1). Training uses multiple augmented instances per example (Eq.4).
- Limits: quoted comparator results and batch multiplicity prevent clean attribution to RL alone; no matched-total-budget random-policy victory established by this table.
- JUDGMENT pre-emption: an augmentation adversary co-trained with a learner is occupied. For P3/P6/P7, use this as the positive steelman while separately testing whether stochastic diversity, curriculum, or extra computation explains the gain.

### C03-10 — Challenges of Adversarial Image Augmentations

- Metadata: Arno Blaas, Xavier Suau, Jason Ramapuram, Nicholas Apostoloff, Luca Zappella. ICBINB NeurIPS workshop 2021 per author record; inspected preprint. DOI: 10.48550/arXiv.2111.12427. [Canonical record](https://arxiv.org/abs/2111.12427); [PDF](https://arxiv.org/pdf/2111.12427v2). Access: 2026-10-30.
- Inspection: FULL_TEXT_INSPECTED_ONLINE; v2, 3 December 2021; §§3–4.1, Corollary 1, Table 2 and curriculum experiments.
- SOURCE setting/class: image training augmentation; comparator-not-RL diagnosis of adversarial/RL claims. State/action/reward: N/A as learned RL; current classifier loss selects worst transform or a fixed curriculum; random baseline samples transformations.
- SOURCE comparator/effect: Table 2 CIFAR-100 WRN-28-10, M=1: baseline accuracy 81.1%, random +1.3 points, exhaustive TrueAdv −0.8 points. Five runs, 200 epochs; reported endpoint is best test accuracy over training epochs (§4).
- Limits: reduced action space; exhaustive adversary costs more; best-test-epoch reporting is optimistic. It does not reproduce AdvAA under equal total compute; stochastic-controller explanation remains conjecture.
- JUDGMENT pre-emption: maximizing training difficulty need not improve unseen performance. P3 adversarial schedules need a causal ablation against random diversity and simple curricula, not only an improved attack loss.

## Other leads, access failures, and duplicates

- AutoAugment, TrivialAugment and OHL CVF PDFs returned 403. AutoAugment and TrivialAugment were recovered on arXiv and counted only once each. OHL's [arXiv PDF](https://arxiv.org/pdf/1905.07373) was opened but only partially read; NOT counted. The directly relevant adversarial-diagnosis card was selected instead.
- AdvAA's OpenReview PDF redirected to a browser challenge. Its arXiv full text supplied methods and evaluation. This is an access failure at OpenReview, not absence of the work.
- RandAugment's [CVPR-workshop version](https://openaccess.thecvf.com/content_CVPRW_2020/html/w40/Cubuk_Randaugment_Practical_Automated_Data_Augmentation_With_a_Reduced_Search_Space_CVPRW_2020_paper.html) is a duplicate work with different headline ImageNet results; the NeurIPS version controls C03-02.
- Smart(Sampling)Augment and Smart Augmentation remain UNINSPECTED leads. DiffAugment, ultrasound applications, domain-generalization citations and incidental CVF search results were not used to fill the floor.
- Li/Talwalkar random NAS was not needed: all ten counted works directly concern augmentation. No NAS analogy was substituted for augmentation evidence.

## Cluster synthesis

**JUDGMENT, supported by the inspected comparisons:** this cluster does not establish that RL beats the strongest simple alternative under equal total budget. It establishes a useful ingredient—training with an appropriate distribution of transformations—and repeatedly weakens the attribution of gains to a sophisticated search optimizer. This is not a theorem that RL cannot help.

**SOURCE evidence hierarchy:** AutoAugment's random-policy ablation favors its learned policy but mismatches search effort (C03-01 §5.1). Adversarial AutoAugment is a positive result whose training multiplicity requires separate controls (C03-09). TrivialAugment supplies fixed-training reproductions and a total-compute comparison, with caveats about estimated costs, spaces and reproduction (C03-07). The exhaustive-adversary diagnosis tests objective alignment, not a clean equal-budget RL race (C03-10). Fast AA/PBA/DADA/Faster AA show alternative search mechanisms with different proxy and hardware costs; their GPU-hour ratios must not be interpreted as normalized end-to-end speedups.

**JUDGMENT for the thesis:** P3 is the closest match: choose a surrogate, noise level or bounded transform in the writer loop. Before an RL controller, compare a fixed diverse mixture, uniform operation/strength sampling, a small grid or random hyperparameter search, and differentiable optimization where possible. P1 per-image decisions require demonstrably predictive clean-image context; none of these cards establishes that for watermark survival. P2 spatial/frequency allocation needs separate carrier and binding evidence; augmentation-label invariance is insufficient.

An equal-budget prospective comparison should hold the permitted action set, quality constraint, data, feedback calls, update count and evaluation protocol fixed; charge policy training, failed searches, hyperparameter selection, expanded batches and final application to one total budget. Also compare the best use of the budget by the non-RL arm, rather than making it idle after one random draw. A fixed schedule and a random policy should each have a fair tuning allowance. Separate an optimizer comparison within one space from a method comparison where the action space itself changes.

Dataset/model transfer in classification does not establish transfer across unseen diffusion regenerators. No counted card reports post-hoc content-bound watermark C/J, strict PSNR/SSIM/LPIPS gates, T3 native regeneration, or T4/T5 forgery/collision guarantees. Ordinary image augmentations here are methodological analogies; T1/T2 improvements carry no thesis verdict weight. A P3 paper must show native excluded-family gains and preserve binding and quality. Generic learned augmentations, curricula, adversarial augmentation and gradient-relaxed selection are occupied ingredients; this search cannot establish absence of an identical watermark construction elsewhere.

## Counts and stopping basis

- Actual distinct queries: **15**; scholarly index contents searched: **5**; native-index queries: **0**; general-web queries: **0**.
- Unique FULL_TEXT_INSPECTED_ONLINE cards: **10**, C03-01 through C03-10; target: **10**. All include method and evaluation inspection, comparator/effect locators, metadata, setting, class, state/action/reward, pre-emption and limits.
- No local PDF artifacts or hash verification are claimed. Online inspection does not certify publisher-final identity when a preprint fallback was used.
- Floor met. No exhaustion claim; further literature exists. Stop at this bounded cluster deliverable rather than pad it.
