# C4 — Transfer across unseen models

Research date: 2026-10-30. Author: Codex C4 literature agent. Scope: online primary-source inspection only; no experiments, model execution, held-out data, or F6 outcomes. `PHASE_B_JOURNALS=off`. This file reports classifier-transfer evidence and its limits for post-hoc image watermarking. It does not report watermark success.

## Search log

All queries below were actually issued through `web.run.search_query` on 2026-10-30. Correction: the displayed `site.domain` strings are malformed operators, not `site:domain` restrictions. Here `Indirect` means general-web discovery using a domain-name search term; it does not establish enforced index coverage. Exact historical strings are retained. URLs in the result column are destinations subsequently inspected or identified as inaccessible; several became accessible through versioned arXiv HTML. No native index search or exhaustive coverage is claimed. The global index floor relies on valid queries in other cluster logs, not these malformed operators.

| ID | Exact query | Route / index | Primary results, new leads, failures |
|---|---|---|---|
| C4-Q01 | `site.openaccess.thecvf.com Boosting Adversarial Attacks Momentum Diverse Input Patterns translation invariant` | Indirect / CVF | MI-FGSM, DI and TI leads; inspected versions [C04-01](https://arxiv.org/html/1710.06081v3), [C04-02](https://arxiv.org/html/1803.06978v4), [C04-03](https://arxiv.org/html/1904.02884v1). CVF PDF access subsequently failed. |
| C4-Q02 | `site.arxiv.org Nesterov Iterative Fast Gradient Sign Method scale invariant transferability` | Indirect / arXiv | [NI/SI](https://arxiv.org/html/1908.06281v3), C04-04. |
| C4-Q03 | `site.openaccess.thecvf.com Enhancing Transferability Adversarial Attacks Variance Tuning` | Indirect / CVF | Variance-tuning lead; [accessible author preprint](https://arxiv.org/html/2103.15571v1), C04-05. |
| C4-Q04 | `site.openreview.net adversarial transfer ensemble adaptive weighting reinforcement learning` | Indirect / OpenReview | Mixed ensemble/transfer results; no additional eligible fully inspected paper from this query. |
| C4-Q05 | `site.openaccess.thecvf.com Improving Transferability Adversarial Examples Input Diversity 2019` | Indirect / CVF | Confirms DI lead; [C04-02](https://arxiv.org/html/1803.06978v4). |
| C4-Q06 | `site.openaccess.thecvf.com Evading Defenses Transferable Adversarial Examples Translation Invariant 2019` | Indirect / CVF | Confirms TI lead; [C04-03](https://arxiv.org/html/1904.02884v1). |
| C4-Q07 | `site.dblp.org adversarial ensemble reinforcement learning transferability` | Indirect / DBLP | Bibliographic discovery; no new fully inspected eligible work attributable to this query. Native DBLP search not used. |
| C4-Q08 | `site.arxiv.org adversarial transferability reinforcement learning transformations AutoMA` | Indirect / arXiv | [Learning to Transform Dynamically](https://arxiv.org/html/2405.14077v1), C04-06; AutoMA remains an uninspected lead. |
| C4-Q09 | `site.openreview.net "transfer" "reinforcement" "adversarial" ensemble` | Indirect / OpenReview | Mixed/domain-generalization material including [SMEE lead](https://openreview.net/pdf?id=4kJfWZChJI); excluded from attack-transfer cards. |
| C4-Q10 | `site.ieeexplore.ieee.org "adversarial" "ensemble" "adaptive" transferability` | Indirect / IEEE Xplore | Mixed defense/ensemble results; no new eligible accessible full-text card. This is a logged weak retrieval, not IEEE full-text verification. |
| C4-Q11 | `site.arxiv.org "ensemble" "weight" "black-box" "BASES"` | Indirect / arXiv | [BASES](https://arxiv.org/html/2208.03610v2), C04-08. |
| C4-Q12 | `site.openaccess.thecvf.com "transferability" "meta" "ensemble"` | Indirect / CVF | AdaEA, SMER and ViT-EnsembleAttack leads; [AdaEA](https://arxiv.org/html/2308.02897v1), C04-07. Other search returns led to TransferBench; no claim all results were within requested domain. |
| C4-Q13 | `site.openaccess.thecvf.com "Ensemble Diversity Facilitates Adversarial Transferability"` | Indirect / CVF | [SMER publisher PDF](https://openaccess.thecvf.com/content/CVPR2024/papers/Tang_Ensemble_Diversity_Facilitates_Adversarial_Transferability_CVPR_2024_paper.pdf): repeated 403; not counted. |
| C4-Q14 | `site.openaccess.thecvf.com "Learning to Transform Dynamically"` | Indirect / CVF | No additional verified publisher version; use [author preprint](https://arxiv.org/html/2405.14077v1), C04-06. |
| C4-Q15 | `site.arxiv.org "Blackbox Attacks via Surrogate Ensemble Search"` | Indirect / arXiv | [BASES](https://arxiv.org/html/2208.03610v2), C04-08. |
| C4-Q16 | `site.openaccess.thecvf.com "Admix" "Spectrum Simulation"` | Indirect / CVF | Admix/spectrum leads; inspected [Admix](https://arxiv.org/html/2102.00436v3), C04-11, and later C04-15. |
| C4-Q17 | `"Ensemble Diversity Facilitates" arxiv pdf` | General web discovery | SMER; no accessible primary full text found. Author repository inspected later; not a paper-inspection substitute. |
| C4-Q18 | `"Rethinking Model Ensemble" arxiv` | General web discovery | [Common Weakness Attack](https://arxiv.org/html/2303.09105v2), C04-09. |
| C4-Q19 | `"Stochastic Variance Reduced Ensemble" arxiv` | General web discovery | [SVRE](https://arxiv.org/html/2111.10752v2), C04-10. |
| C4-Q20 | `"Admix: Enhancing" arxiv` | General web discovery | [Admix](https://arxiv.org/html/2102.00436v3), C04-11. |
| C4-Q21 | `site.arxiv.org "Skip Connections Matter" adversarial` | Indirect / arXiv | [SGM](https://arxiv.org/html/2002.05990v1), C04-13. |
| C4-Q22 | `site.arxiv.org "Intermediate Level Attack" transferability` | Indirect / arXiv | [ILA](https://arxiv.org/html/1907.10823v1), C04-14. Earlier versions/related identifiers not counted again. |
| C4-Q23 | `site.arxiv.org "Frequency Domain Model Augmentation" adversarial` | Indirect / arXiv | [Spectrum simulation](https://arxiv.org/html/2207.05382v1), C04-15. |
| C4-Q24 | `"Ensemble Diversity Facilitates Adversarial Transferability" "pdf" -site:openaccess.thecvf.com -site:bytez.com` | General web discovery | Alternate author access sought; [official code](https://github.com/tangbwb/SMER) inspected, no full-paper replacement located. |

TransferBench was additionally followed as a citation/search lead to its [NeurIPS proceedings PDF](https://papers.neurips.cc/paper_files/paper/2025/file/cc41a858306c9bbb72127c90c1b9f5d6-Paper-Datasets_and_Benchmarks_Track.pdf). Citation following and URL opens are not inflated into extra queries. All 15 counted papers below had substantive method **and** evaluation passages opened. This is online inspection, not a claim that local PDFs were downloaded or hashes verified.

## Inspected cards

Interpretation: SOURCE denotes a paper report; DERIVED denotes arithmetic from that report; JUDGMENT denotes project-specific inference. All settings below concern post-hoc perturbations of existing images. A classifier's attack success rate is neither ownership detection nor content-bound acceptance. `comparator-not-RL` has state/action/reward `N/A`; optimization iterations alone do not make a method RL. DOI is recorded as null when not verified.

### C04-01 — Boosting Adversarial Attacks with Momentum

- Metadata: Yinpeng Dong, Fangzhou Liao, Tianyu Pang, Hang Su, Jun Zhu, Xiaolin Hu, Jianguo Li. CVPR 2018. DOI: null. [Canonical inspected source](https://arxiv.org/html/1710.06081v3), v3; accessed 2026-10-30; **FULL_TEXT_INSPECTED_ONLINE**.
- Inspected: §3.1, Eqs. 6–7; §3.2, Eqs. 8–9/Algorithm 2; §4.1–4.2/Table 1. Setting: ImageNet classifier transfer, 1,000 jointly correctly classified images. RL: comparator-not-RL; state/action/reward: N/A.
- SOURCE: MI-FGSM accumulates normalized gradients; an extension averages surrogate logits. Table 1, Inc-v3 to Inc-v4 untargeted ASR: I-FGSM 22.8%, MI-FGSM 48.8%. DERIVED: +26.0 percentage points (pp).
- JUDGMENT: Momentum and fixed ensembles pre-empt generic P3/P4 claims. Momentum adds little beyond an existing gradient; ensembles multiply surrogate work. These classifier results establish neither diffusion-encoder transfer nor T3/T4/T5 protection.

### C04-02 — Improving Transferability of Adversarial Examples with Input Diversity

- Metadata: Cihang Xie, Zhishuai Zhang, Yuyin Zhou, Song Bai, Jianyu Wang, Zhou Ren, Alan Yuille. CVPR 2019. DOI: null. [Source](https://arxiv.org/html/1803.06978v4), v4; accessed 2026-10-30; **FULL_TEXT_INSPECTED_ONLINE**.
- Inspected: §3.3/Eqs. 5–7; §4.1–4.2/Table 1. Setting: 5,000 correctly classified ImageNet images, perturbation bound 15/255; random resize/pad probability 0.5. RL: comparator-not-RL; state/action/reward: N/A.
- SOURCE: Per-step randomized input transformations improve surrogate-gradient transfer. Table 1, Inc-v3 to Inc-v4 untargeted ASR: MI-FGSM 36.6%, M-DI2-FGSM 63.9%. DERIVED: +27.3 pp.
- JUDGMENT: Random transforms are a mandatory simple P3 comparator. No learned policy is required for this gain. Count transformed forwards/backwards and reject attribution to learning when randomness alone explains performance. Classifier perturbation budgets do not establish strict watermark quality.

### C04-03 — Evading Defenses to Transferable Adversarial Examples by Translation-Invariant Attacks

- Metadata: Yinpeng Dong, Tianyu Pang, Hang Su, Jun Zhu. CVPR 2019. DOI: null. [Source](https://arxiv.org/html/1904.02884v1), v1; accessed 2026-10-30; **FULL_TEXT_INSPECTED_ONLINE**.
- Inspected: §3.2.1–3.2.3, Eqs. 10–11; §4.1/§4.5, Tables 4–5. Setting: 1,000 NIPS attack images and defended classifiers. RL: comparator-not-RL; state/action/reward: N/A.
- SOURCE: A convolution approximates gradients averaged over translated images. Table 4, Inc-v3 surrogate to HGD target, untargeted ASR: DIM 9.7%, TI-DIM 38.3%. DERIVED: +28.6 pp.
- JUDGMENT: Analytical averaging can replace transform sampling or a learned selector. The approximation's convolution cost differs from many backward passes. This pre-empts a generic “ensemble over nuisance transforms” ingredient, not a watermark construction. HGD classifier defense is not an independently trained regeneration encoder.

### C04-04 — Nesterov Accelerated Gradient and Scale Invariance for Adversarial Attacks

- Metadata: Jiadong Lin, Chuanbiao Song, Kun He, Liwei Wang, John E. Hopcroft. ICLR 2020; inspected preprint v3 (2019). DOI: null. [Source](https://arxiv.org/html/1908.06281v3); accessed 2026-10-30; **FULL_TEXT_INSPECTED_ONLINE**.
- Inspected: §3.2/Eqs. 5–7; §3.3; §4/Table 2. Setting: ImageNet classifier transfer. RL: comparator-not-RL; state/action/reward: N/A.
- SOURCE: Nesterov lookahead and gradients over scaled input copies are combined. Table 2(a), Inc-v3 to IncRes-v2 untargeted ASR: TIM 42.8%, SI-NI-TIM 75.8%. DERIVED: +33.0 pp.
- JUDGMENT: This is a compound comparison, not an isolated NI effect. Extra scale copies add gradient work; iteration matching does not equal compute matching. P3/P4 must beat scale averaging and lookahead before crediting RL. The transfer endpoint remains classification failure.

### C04-05 — Enhancing the Transferability of Adversarial Attacks through Variance Tuning

- Metadata: Xiaosen Wang, Kun He. CVPR 2021. DOI: null. [Source](https://arxiv.org/html/2103.15571v1), v1; accessed 2026-10-30; **FULL_TEXT_INSPECTED_ONLINE**.
- Inspected: §3.2/Eq. 7; §4/Table 1. Setting: ImageNet transfer to normal and adversarially trained classifiers. RL: comparator-not-RL; state/action/reward: N/A.
- SOURCE: Neighborhood gradients estimate variance used to correct the next iteration. Table 1, Inc-v3 to Inc-v4 untargeted ASR: MI-FGSM 43.6%, VMI-FGSM 71.7%; NI-FGSM 51.7%, VNI-FGSM 76.5%. DERIVED: respectively +28.1 and +24.8 pp.
- JUDGMENT: Adaptive gradient correction already has a simple non-RL implementation. Neighborhood samples require additional backwards, so a policy compared only at equal iteration count has an incomplete budget comparison. No published endpoint here demonstrates preservation of watermark semantics or instance binding.

### C04-06 — Learning to Transform Dynamically for Better Adversarial Transferability

- Metadata: Rongyi Zhu, Zeliang Zhang, Susan Liang, Zhuo Liu, Chenliang Xu. Preprint 2024; publisher venue unverified. DOI: null. [Source](https://arxiv.org/html/2405.14077v1), v1; accessed 2026-10-30; **FULL_TEXT_INSPECTED_ONLINE**.
- Inspected: §3.3/Eqs. 4–5/Algorithm 1; §4.1, §4.3, §4.5/Figure 8. Setting: 1,000 ImageNet images, ten attack iterations, bound 16/255, composed transformations.
- RL: authors frame RL; operational classification **R-bandit-like**, rather than demonstrated delayed-return R-full. State: current image/iteration and transform probabilities; action: sampled transformation composition; reward: surrogate classification loss; update: probability gradients through a one-step approximation.
- SOURCE: §4.3 reports randomized-smoothing-target ASR 46.7% versus AITL 42.1% (+4.6 pp); Figure 8 shows increasing sampling count also improves ASR.
- JUDGMENT: Direct P3 precedent: dynamically learned transformation choice is occupied. Total sampling, probability-update and tuning cost must be charged. Surrogate loss does not prove an advantage over random search for regeneration-surviving watermark acceptance.

### C04-07 — An Adaptive Model Ensemble Adversarial Attack for Boosting Adversarial Transferability

- Metadata: Bin Chen, Jiali Yin, Shukai Chen, Bohao Chen, Ximeng Liu. ICCV 2023. DOI: null. [Source](https://arxiv.org/html/2308.02897v1), v1; accessed 2026-10-30; **FULL_TEXT_INSPECTED_ONLINE**.
- Inspected: §3.2/Algorithm 1; §4/Table 1. Setting: image classifier ensembles including CNNs and transformers. RL: comparator-not-RL; state/action/reward: N/A.
- SOURCE: AdaEA estimates each model's cross-surrogate contribution to update weights, and filters inconsistent gradient regions. Table 1, ImageNet average over eight victims: Ens ASR 46.38%, SVRE 46.39%, AdaEA 49.36%. DERIVED: +2.98 pp over Ens.
- JUDGMENT: Per-image/per-iteration model weighting and spatial gradient filtering are already non-RL ingredients relevant to P2/P3. Additional cross-model evaluations belong in the budget. Architecture diversity helps in the tested classifier panel, but this is not evidence for unseen independent diffusion encoders.

### C04-08 — Blackbox Attacks via Surrogate Ensemble Search

- Metadata: Zikui Cai, Chengyu Song, Srikanth Krishnamurthy, Amit Roy-Chowdhury, M. Salman Asif. NeurIPS 2022. DOI: null. [Source](https://arxiv.org/html/2208.03610v2), v2; accessed 2026-10-30; **FULL_TEXT_INSPECTED_ONLINE**.
- Inspected: §3.2–3.3/Eqs. 3–6/Algorithms 1–2; §4.2/Table 1. Setting: targeted black-box image classification with victim score queries. RL: comparator-not-RL; state/action/reward: N/A.
- SOURCE: BASES uses coordinate search over surrogate weights, invoking an inner gradient attack and querying both candidate weight updates. Table 1, VGG19 target: BASES ASR 95.9%, mean queries 3.0; GFCS 89.1%, mean queries 101. The ensemble has 20 surrogates.
- JUDGMENT: This pre-empts generic query-adapted weighting, but the queried victim is not unseen during adaptation. Few target queries can conceal expensive surrogate optimization. Compare total compute and separate query-free transfer from target-adaptive access.

### C04-09 — Rethinking Model Ensemble in Transfer-based Adversarial Attacks

- Metadata: Huanran Chen, Yichi Zhang, Yinpeng Dong, Xiao Yang, Hang Su, Jun Zhu. ICLR 2024. DOI: null. [Source](https://arxiv.org/html/2303.09105v2), v2; accessed 2026-10-30; **FULL_TEXT_INSPECTED_ONLINE**.
- Inspected: §3.2–3.3; §4/Table 1. Setting: NIPS 2017 images, normal and robust unseen classifier targets. RL: comparator-not-RL; state/action/reward: N/A.
- SOURCE: Common Weakness Attack motivates shared flat adversarial regions and approximates costly higher-order objectives. Table 1, AlexNet black-box target: SSA ASR 89.0%, SSA-CWA 96.9%; MI 73.2%, MI-CWA 94.6%. DERIVED: +7.9 pp over the stronger SSA baseline, +21.4 pp over MI.
- JUDGMENT: Baseline strength changes apparent effect materially. Shared surrogate geometry is a direct non-RL competitor for P3/P4. Inner optimization and surrogate passes must count; favorable classifier transfer does not imply a common robust carrier across independent generative encoders.

### C04-10 — Stochastic Variance Reduced Ensemble Adversarial Attack for Boosting the Adversarial Transferability

- Metadata: Yifeng Xiong, Jiadong Lin, Min Zhang, John E. Hopcroft, Kun He. CVPR 2022. DOI: null. [Source](https://arxiv.org/html/2111.10752v2), v2; accessed 2026-10-30; **FULL_TEXT_INSPECTED_ONLINE**.
- Inspected: §3.3/Algorithm 1; §4.2/Table 1. Setting: four-model CNN ensemble, leave-one-out image classifier transfer. RL: comparator-not-RL; state/action/reward: N/A.
- SOURCE: SVRE samples a surrogate and corrects its gradient using local, anchor and ensemble gradients. Table 1 mean untargeted ASR: MI-FGSM Ens 84.13%, SVRE 93.59%; SI-TI-DIM Ens 97.08%, SVRE 98.35%. DERIVED: gains 9.46 pp and 1.27 pp respectively.
- JUDGMENT: Randomized model selection with variance reduction is a strong simple P3 comparator. More sophisticated base attacks sharply reduce the remaining gain. Inner-loop gradients must be budgeted; neither equal outer iterations nor four-CNN leave-one-out establishes unseen-family generalization.

### C04-11 — Admix: Enhancing the Transferability of Adversarial Attacks

- Metadata: Xiaosen Wang, Xuanran He, Jingdong Wang, Kun He. ICCV 2021. DOI: null. [Source](https://arxiv.org/html/2102.00436v3), v3; accessed 2026-10-30; **FULL_TEXT_INSPECTED_ONLINE**.
- Inspected: §3.2–3.3; §4/Table 2. Setting: ImageNet classifier transfer, gradients from images admixed with small amounts of other-class content while retaining the original label. RL: comparator-not-RL; state/action/reward: N/A.
- SOURCE: Table 2, Inc-v4 to Inc-v3 untargeted ASR: SIM 80.6%, Admix 87.8%. DERIVED: +7.2 pp.
- JUDGMENT: This occupies the general ingredient of content-dependent gradient augmentation; it does not propose watermark binding. Extra sampled images and gradients contribute to cost. A watermark use would need to ensure transform-based optimization does not encourage content-independent acceptance under T4 or T5, which these classification experiments never evaluate.

### C04-12 — TransferBench: Benchmarking Ensemble-based Black-box Transfer Attacks

- Metadata: Fabio Brau, Maura Pintor, Antonio Emanuele Cinà, Raffaele Mura, Luca Scionis, Luca Oneto, Fabio Roli, Battista Biggio. NeurIPS 2025, Datasets and Benchmarks. DOI: null. [Proceedings PDF](https://papers.neurips.cc/paper_files/paper/2025/file/cc41a858306c9bbb72127c90c1b9f5d6-Paper-Datasets_and_Benchmarks_Track.pdf), proceedings version; accessed 2026-10-30; **FULL_TEXT_INSPECTED_ONLINE**.
- Inspected: §2–3.2; §4/Table 2. Setting: targeted CIFAR/ImageNet classifier attacks, 17 scenarios, query budget 50. RL: comparator-not-RL; state/action/reward: N/A.
- SOURCE: The benchmark distinguishes homogeneous and heterogeneous surrogate ensembles and includes continued-PGD NaiveAvg baselines. Table 2, BASES against ResNeXt101: homogeneous ASR 86.3%, heterogeneous 29.0%. DERIVED: 57.3 pp lower with this heterogeneous ensemble, not a universal diversity penalty.
- JUDGMENT: Architecture composition can dominate transfer results. A fixed representative target panel, strong continued optimization, and explicit access accounting are necessary; reporting only favorable unseen targets is insufficient.

### C04-13 — Skip Connections Matter: On the Transferability of Adversarial Examples Generated with ResNets

- Metadata: Dongxian Wu, Yisen Wang, Shu-Tao Xia, James Bailey, Xingjun Ma. ICLR 2020. DOI: null. [Source](https://arxiv.org/html/2002.05990v1), v1; accessed 2026-10-30; **FULL_TEXT_INSPECTED_ONLINE**.
- Inspected: §3.1–3.3/Eqs. 8–10; §4.1/Table 3; §4.2/Table 5. Setting: residual/densely connected image classifier surrogates. RL: comparator-not-RL; state/action/reward: N/A.
- SOURCE: SGM attenuates residual-branch gradients. Table 3, DenseNet201 to SE154 untargeted ASR over five random runs: MI 64.38±0.69%, SGM 72.03±0.53%; DI 61.75±0.88%. DERIVED: SGM exceeds MI by 7.65 pp. The method claims no extra forward/backward pass.
- JUDGMENT: Architecture-aware gradient control can improve transfer without learned policy overhead. It is a P4 baseline idea, but residual-network mechanisms cannot simply be asserted to survive an independent diffusion encoder. Robust-target results differ from ordinary-target results.

### C04-14 — Enhancing Adversarial Example Transferability with an Intermediate Level Attack

- Metadata: Qian Huang, Isay Katsman, Horace He, Zeqi Gu, Serge Belongie, Ser-Nam Lim. ICCV 2019. DOI: null. [Source](https://arxiv.org/html/1907.10823v1), v1; accessed 2026-10-30; **FULL_TEXT_INSPECTED_ONLINE**.
- Inspected: §3; §4/Table 1 and layer-selection discussion. Setting: intermediate classifier features, CIFAR-10/ImageNet post-hoc attacks. RL: comparator-not-RL; state/action/reward: N/A.
- SOURCE: ILA amplifies a baseline perturbation's feature-space direction. Table 1, CIFAR-10 ResNet18 to DenseNet121: post-attack accuracy is 35.1% for 20-step MI-FGSM versus 30.4% for ten baseline plus ten ILA steps. DERIVED: 4.7 pp higher misclassification at equal total iterations. Lower accuracy is better here.
- JUDGMENT: Feature-level allocation/optimization already has a non-RL precedent relevant to P2/P4. Equal iterations exclude layer-selection/tuning overhead. Target-optimized OptILA columns must not be presented as source-only transfer. Feature perturbations are not content-bound watermark bits.

### C04-15 — Frequency Domain Model Augmentation for Adversarial Attack

- Metadata: Yuyang Long, Qilong Zhang, Boheng Zeng, Lianli Gao, Xianglong Liu, Jian Zhang, Jingkuan Song. ECCV 2022. DOI: null. [Source](https://arxiv.org/html/2207.05382v1), v1; accessed 2026-10-30; **FULL_TEXT_INSPECTED_ONLINE**.
- Inspected: §3.3/Eqs. 5–6/algorithm; §4/Tables 1–2. Setting: ImageNet classifier transfer using randomized DCT-domain input transformations. RL: comparator-not-RL; state/action/reward: N/A.
- SOURCE: Spectrum simulation averages gradients over randomized spectral modifications. Table 1, Inc-v3 to Inc-v4 untargeted ASR: FI-MI 83.6%, S2I-MI 88.2%. DERIVED: +4.6 pp.
- JUDGMENT: Frequency augmentation and surrogate simulation are occupied P2/P3 ingredients. Sampling count and transform/backward work must be charged. Calling transformations “model augmentation” does not mean independently trained diffusion models were evaluated; the reported endpoint is classifier failure, without a strict PSNR/SSIM/LPIPS watermark gate.

## Relevant leads not counted

| Lead | Access/status | Why it matters / disposition |
|---|---|---|
| **Ensemble Diversity Facilitates Adversarial Transferability**, Bowen Tang, Zheng Wang, Yi Bin, Qi Dou, Yang Yang, Heng Tao Shen; CVPR 2024 | **UNINSPECTED PAPER**. Publisher [PDF](https://openaccess.thecvf.com/content/CVPR2024/papers/Tang_Ensemble_Diversity_Facilitates_Adversarial_Transferability_CVPR_2024_paper.pdf) and HTML repeatedly returned 403. [Official SMER repository](https://github.com/tangbwb/SMER) opened, confirms identity, but is not full-text method/evaluation inspection. | Indexed primary text describes reinforcement-learning ensemble weighting. This is a **priority novelty lead**, not validated effect evidence. Do not claim first RL model-weighting method while it remains unresolved. No SMER numbers enter counted cards. |
| AutoMA, AITL, ATTA and other transform-policy references in L2T | UNINSPECTED independently in this cluster | L2T's related-work discussion is not a substitute for inspecting each source. C3/C6 may independently cover them; no duplicate count asserted here. |
| ViT-EnsembleAttack, ICCV 2025 lead | Publisher access failed; UNINSPECTED | Relevant newer ensemble work; no effect claims adopted. |
| Enhancing Adversarial Transferability through Adversarial Weight Tuning, arXiv:2408.09469 | Discovery lead only; UNINSPECTED | Potentially relevant additional non-RL comparator. No absence claim based on omission. |
| Earlier ILA identifiers/versions | DUPLICATE LINE | C04-14 counts the inspected paper once. |
| Domain-generalization ensembles, adversarial attacks **on** multi-agent RL, unrelated audio attacks/defense-oriented retrievals | EXCLUDED / topic mismatch | These do not demonstrate an RL attack policy transferring among image models. They do not fill C4's floor. |

## Synthesis for the RL decision

**Finding:** This cluster does not establish that RL beats a strong non-RL method under an equal total budget for post-hoc content-bound watermarking under diffusion regeneration. It supplies useful mechanisms and strong comparators, together with a substantial novelty burden. None of these 15 evaluations measures the thesis's joint ownership/content acceptance, T4 copy-paste rejection or T5 semantic-collision rejection.

1. **P3 has direct prior art; adaptation alone is not novelty.** L2T already learns dynamic transform distributions. AdaEA adapts ensemble contributions without RL; BASES tunes weights by coordinate search with victim queries; SVRE samples models with variance correction. The unresolved SMER primary-paper lead further prevents a defensible first-RL-weighting claim. These are occupied ingredients, not an assertion that an identical watermark construction has been published.
2. **P2 and P4 need unusually strong baselines.** Random input/spectral augmentation, intermediate feature objectives, momentum/lookahead, neighborhood variance corrections and architecture-sensitive gradients can already produce substantial classifier-transfer gains. A proposed spatial or band policy must beat a fixed allocation plus these appropriate simple optimization controls. Papers' different datasets, norms, access models and endpoints make their percentages unsuitable for a pooled effect estimate.
3. **P1 would require new evidence of predictable image-dependent utility.** These attack papers do not show that clean-image features predict which watermark carrier or budget survives regeneration. A contextual selector needs a genuine held-out advantage over the best fixed choice, random selection, and a small supervised predictor. No delayed reward requirement follows from per-image choice alone.
4. **Count total work, not just iterations or target queries.** For a future test, separately record surrogate forwards/backwards, transform samples, inner optimization, policy training, policy updates, reward calls, hyperparameter selection and deployment calls. Fix both a total-compute ceiling and a target-access regime. Report cold-start and amortized policy costs; pretraining on the eventual target family invalidates an unseen-family claim. BASES-style target queries are a different information setting from query-free transfer.
5. **Classifier transfer is an analogy, not encoder evidence.** Leave-one-classifier-out can retain near-identical training data, architectures or objectives. The relevant future split must exclude an independently trained autoencoder/denoiser family from policy training, reward design and parameter selection, with unseen source images separately reserved. Development-family selection should be fixed before outcomes; results must be shown per family, including failures. Cross-validation among a few seen families cannot certify arbitrary future regenerators.
6. **Guard against surrogate overfit and reward shortcuts.** Increasing surrogate loss or classification ASR is not the target reward. A watermark policy could increase owner recovery while erasing content binding, or trade clean quality for recovery. Every future candidate therefore needs the same strict clean-quality constraints and separately reported T3, T4 and T5 endpoints; a weighted reward must not hide a failed constraint. These are design requirements inferred for this project, not findings demonstrated by these papers.

**Minimal fair future comparator set (design only):** best fixed surrogate mixture; uniform random surrogate/transform sampling; a DI/TI/SI-style fixed transform distribution appropriate to the actual writer; gradient/coordinate optimization of continuous weights; AdaEA- or SVRE-style adaptive ensemble baseline; a matched-budget random search; and, only when feedback is genuinely sequential and decision-dependent, a bandit or RL controller. Avoid transplanting irrelevant ordinary-distortion attacks as thesis endpoints. Candidate-specific comparator pruning must be justified before results exist.

**Evidence status and counts:** 24 actual distinct general-web queries; five intended domain terms (CVF, arXiv, OpenReview, DBLP, IEEE Xplore), but malformed operators do not establish restricted-index searches; 15 distinct **FULL_TEXT_INSPECTED_ONLINE** paper cards; 14 comparator-not-RL cards and one authors-claimed-RL / operationally R-bandit-like card; zero independently demonstrated R-full superiority results for the thesis task. The C4 card floor is met. The search is **not declared exhausted**: SMER and other explicitly listed relevant leads remain unresolved. This limited dossier supports a conditional mechanism transfer hypothesis and a strong baseline requirement, not a novelty or efficacy guarantee.
