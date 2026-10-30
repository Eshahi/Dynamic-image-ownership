# C2 — Learned attacks and adaptive black-box attacks

Access date: 2026-10-30. Scope: WP2 C2, including its explicitly authorized adaptive black-box component. Research only; no experiments, run outputs, images, or scientific runtimes accessed. PHASE_B_JOURNALS=off. This file contains 15 counted primary-paper cards, six on image watermark attacks, one on text watermark attacks, and eight on adaptive classifier attacks. The latter are algorithmic analogies, not evidence about watermark regeneration survival.

All counted papers have substantive methods and evaluation inspected online. `FULL_TEXT_INSPECTED_ONLINE` means the specified full text was opened and those sections read; it does not mean every appendix was audited or that an arXiv version is publisher-final. DOI null means no publisher DOI verified. Source paraphrases are compact; JUDGMENT paragraphs are project-specific inferences. There are no new MEASURED project results here.

## Actual query log

All queries below were issued through `web.run.search_query` on 2026-10-30. `I` means indirect index search through the general search engine, not a native index search; `G` means general web discovery. The exact query strings are retained. Direct URL opens, reference chasing, and retries are not counted as queries.

| ID | Exact query | Route / index | Primary results and disposition |
|---|---|---|---|
| C2-Q01 | `site:openreview.net Lukas 2024 image watermark attacks generative` | I / OpenReview | [Lukas](https://openreview.net/pdf?id=O9PArxKLe1), new; initial challenge, recovered arXiv and proceedings full text; C2-01. |
| C2-Q02 | `site:arxiv.org reinforcement learning watermark removal attack detector` | I / arXiv | [RLCracker](https://arxiv.org/abs/2509.20924), new, C2-05; [LLM embedding](https://arxiv.org/abs/2403.10553), different topic; [RemTraceNet](https://arxiv.org/abs/2609.31694) and [DeMark](https://arxiv.org/abs/2609.34003), uninspected leads. |
| C2-Q03 | `site:openaccess.thecvf.com reinforcement learning black box attack policy` | I / CVF | [Sarkar CVPRW2023](https://openaccess.thecvf.com/content/CVPR2023W/AML/html/Sarkar_Robustness_With_Query-Efficient_Adversarial_Attack_Using_Reinforcement_Learning_CVPRW_2023_paper.html), new but 403; reference chasing later recovered SafeAI paper C2-07. Other hits concerned model inversion or attacking RL agents; excluded. |
| C2-Q04 | `site:dl.acm.org reinforcement learning watermark attack` | I / ACM DL | No eligible primary ACM result returned. Empty search, not evidence of absence. |
| C2-Q05 | `site:ieeexplore.ieee.org reinforcement learning watermark removal black box attack` | I / IEEE Xplore | [Forgery](https://ieeexplore.ieee.org/document/11095200), C2-04; [2020 black-box attack](https://ieeexplore.ieee.org/document/9123270), abstract-only; [DAPAO](https://ieeexplore.ieee.org/document/11699107), uninspected; [model watermark](https://ieeexplore.ieee.org/document/11495080), different protected object. |
| C2-Q06 | `site:arxiv.org UnMarker universal watermark remover policy driven attack` | I / arXiv | [UnMarker](https://arxiv.org/abs/2405.08363), new, C2-02. |
| C2-Q07 | `site:openreview.net Policy Driven Attack Learning to Query Hard label` | I / OpenReview | [Policy-Driven Attack](https://openreview.net/forum?id=pzpytjk3Xb2), new, C2-06; direct PDF challenged, alternate primary PDF recovered. OPT-attack also surfaced; not counted. |
| C2-Q08 | `site:arxiv.org "watermark" "attack" "reinforcement" image` | I / arXiv | RLCracker again; [DnD](https://arxiv.org/abs/2609.31693), [forensic-stealth](https://arxiv.org/abs/2605.09203), new uninspected leads sent to C12. |
| C2-Q09 | `site:openreview.net black box attacks bandits priors Ilyas 2019` | I / OpenReview | [Prior Convictions](https://openreview.net/pdf?id=BkMiWhR5K7), new, C2-09. |
| C2-Q10 | `site:arxiv.org reinforcement learning black box adversarial policy attack query efficient` | I / arXiv | [Sparse video attack](https://arxiv.org/abs/2001.03754), new, C2-08; [action poisoning](https://arxiv.org/abs/2110.04471), [policy attack](https://arxiv.org/abs/2011.07114), [optimal attacks](https://arxiv.org/abs/1907.13548), different target setting, not counted. |
| C2-Q11 | `site:dl.acm.org watermark removal reinforcement learning adaptive attack image` | I / ACM DL | No eligible primary ACM result returned; empty search. |
| C2-Q12 | `site:openaccess.thecvf.com "Black-Box Forgery Attacks"` | I / CVF | Müller CVPR2025 primary record/PDF found; direct CVF access failed, [arXiv full text](https://arxiv.org/abs/2412.03283) later recovered; C2-04. |
| C2-Q13 | `site:arxiv.org 2610.02010 LFM watermark` | I / arXiv | No exact lead returned. Direct [LFM URL](https://arxiv.org/abs/2610.02010) subsequently opened; counted by C12, excluded here. |
| C2-Q14 | `site:arxiv.org CtrlRegen controlled regeneration watermark removal 2410.05470` | I / arXiv | [CtrlRegen](https://arxiv.org/abs/2410.05470), new, C2-03; [semantic regeneration](https://arxiv.org/abs/2505.08234), uninspected lead. |
| C2-Q15 | `site:proceedings.mlr.press Black-box Adversarial Attacks Limited Queries Information Ilyas` | I / PMLR | [Ilyas et al.](https://proceedings.mlr.press/v80/ilyas18a.html), new, C2-10. |
| C2-Q16 | `site:proceedings.mlr.press Simple Black-box Adversarial Attacks Guo` | I / PMLR | [SimBA](https://proceedings.mlr.press/v97/guo19a.html), new, C2-11. Low-frequency perturbation paper also surfaced; not counted. |
| C2-Q17 | `"Leveraging Optimization for Adaptive Attacks" arxiv` | G | [Lukas arXiv](https://arxiv.org/abs/2309.16952), alternative full-text route; C2-01. |
| C2-Q18 | `"Policy-Driven Attack" arxiv` | G | [OpenReview alternate PDF](https://openreview.net/references/pdf?id=zQ8_-FYrn3), successful recovery, C2-06. |
| C2-Q19 | `"Square Attack" arxiv` | G | [Square Attack](https://arxiv.org/abs/1912.00049), new; official ECVA PDF inspected, C2-12. |
| C2-Q20 | `"HopSkipJumpAttack" arxiv` | G | [HSJA](https://arxiv.org/abs/1904.02144), new, C2-13. |
| C2-Q21 | `"Robustness With Query-Efficient Adversarial Attack" arxiv` | G | CVPRW2023 Sarkar again; full text remained 403. No new accessible paper. |
| C2-Q22 | `"Invisible Image Watermarks Are Provably Removable" arxiv` | G | [Zhao et al.](https://arxiv.org/abs/2306.01953), new; official NeurIPS PDF inspected, C2-15. |
| C2-Q23 | `site:arxiv.org "Steganalysis on Digital Watermarking"` | I / arXiv | [Yang et al.](https://arxiv.org/abs/2406.09026), new, C2-14. |
| C2-Q24 | `"Policy-Driven Attack" "pre-training"` | G | Secondary descriptions only; not used as evidence. Primary PDF supplies cost caveat. |
| C2-Q25 | `"Black-Box Forgery Attacks" "arxiv"` | G | Secondary discovery link led to [primary arXiv](https://arxiv.org/abs/2412.03283); C2-04 recovered. |
| C2-Q26 | `"Robustness with Query-efficient" "pdf" -site:openaccess.thecvf.com` | G | [AAAI2024 demonstration](https://ojs.aaai.org/index.php/AAAI/article/download/30579/32741), full text inspected but not counted separately from RLAB lineage. |
| C2-Q27 | `"RLAB" "Sarkar" "arxiv"` | G | Same demonstration; no original arXiv full text recovered. |
| C2-Q28 | `"Steganalysis on Digital Watermarking" journal` | G | Same arXiv paper; journal venue not verified. |
| C2-Q29 | `"Sarkar" "Robustness With Query-Efficient" pdf reinforcement learning` | G | CVF repeated; [author publication page](https://www.sarkar.org/) found. Author/referral routes expose SafeAI2023 and AAAI2025 lineage. |
| C2-Q30 | `"Robustness With Query-Efficient Adversarial Attack" "PPO"` | G | Search surfaced method fragments and repeated CVF/RLAB references; snippets not treated as inspection. Primary [SafeAI2023 paper](https://ceur-ws.org/Vol-3381/8.pdf) recovered via AAAI2024 references and opened substantively; C2-07. |

Query count: **30** actual, meaningfully distinct strings; **17 indirect index queries** and **13 general discovery queries**. Six scholarly index contents searched: arXiv, OpenReview, CVF, IEEE Xplore, ACM DL, PMLR. Five returned relevant leads; ACM searches were empty. AAAI, CEUR, ECVA and NeurIPS primary full texts were additionally reached by reference chasing, not counted as separately searched indexes. No native-index search or exhaustive coverage is claimed.

## Counted inspected cards

### C2-01 — Leveraging Optimization for Adaptive Attacks on Image Watermarks

Nils Lukas, Abdulrahman Diaa, Lucas Fenaux, Florian Kerschbaum. ICLR 2024. DOI: null. [Canonical](https://arxiv.org/abs/2309.16952). Access: 2026-10-30. `FULL_TEXT_INSPECTED_ONLINE`: [v2 HTML](https://arxiv.org/html/2309.16952v2), §§4.1–4.2, Algorithm 1, §5/Table 1; proceedings PDF also opened.

**SOURCE.** Post-hoc image removal; comparator-not-RL. A differentiable surrogate key enables gradient optimization of adversarial noise or a compression model. State/action/reward: N/A; watermark loss and perceptual distortion are optimization objectives. Comparators include ordinary perturbations, compression and diffusion regeneration. Table 1 selects attacks driving TPR below 10% at 1% FPR: Tree-Ring adversarial noising at 2/255 obtains TPR 5.2%, LPIPS .032. These selected operating points are not an equal-total-cost RL comparison. Algorithm knowledge and surrogate-key construction matter; no trained sequential controller is tested.

**JUDGMENT — pre-emption/limits.** Adaptive learned removal and surrogate-driven attack optimization are occupied ingredients. Calling the surrogate a reward model does not make gradient descent RL. Low LPIPS alone does not establish all strict-quality gates or content-bound T4/T5 security.

### C2-02 — UnMarker: A Universal Attack on Defensive Image Watermarking

Andre Kassis, Urs Hengartner. IEEE S&P 2025, author version. DOI: 10.1109/SP61157.2025.00005. [Canonical](https://arxiv.org/abs/2405.08363). Access: 2026-10-30. `FULL_TEXT_INSPECTED_ONLINE`: [v2](https://arxiv.org/html/2405.08363v2), §§V-A–V-B, VI-A–VI-B, Table III.

**SOURCE.** Post-hoc image removal; comparator-not-RL. Spectral-amplitude optimization and learned filtering disrupt watermark carriers without detector feedback. State/action/reward: N/A; constrained spectral/perceptual objectives. The complete attack combines crop, high-frequency and low-frequency stages. Table III(b), Tree-Ring: detection 40%, LPIPS .10, versus uncropped diffusion attack 99%, .32. These operating points have different mechanisms and distortion, not matched strict quality. No detector queries or RL policy are needed; optimization still has computational cost.

**JUDGMENT — pre-emption/limits.** Occupies detector-free adaptive spectral removal. Its crop component is outside this project's primary T3/T4/T5 attack scope and cannot carry a project verdict. Do not adopt the paper's broad watermark-impossibility conclusion from these particular schemes and quality criteria. It supplies no RL advantage evidence.

### C2-03 — Image Watermarks are Removable Using Controllable Regeneration from Clean Noise

Yepeng Liu et al.; [full author list/canonical](https://arxiv.org/abs/2410.05470). ICLR 2025. DOI: null. Access: 2026-10-30. `FULL_TEXT_INSPECTED_ONLINE`: [v2](https://arxiv.org/html/2410.05470v2), §§3.1–3.3, §4/Table 1.

**SOURCE.** Post-hoc image removal; comparator-not-RL. CtrlRegen uses semantic and spatial conditioning to reconstruct from clean Gaussian noise; CtrlRegen+ varies starting noise. Adapters use supervised denoising training. State/action/reward: N/A; conditioning and noise level are controls, not a learned RL policy. Table 1, Tree-Ring TPR at 1% FPR: CtrlRegen .12 at PSNR 19.32 dB, versus Regen .87 at 25.59 dB and Rinse .61 at 23.28 dB. Detector queries are unnecessary for regeneration itself; adapter training is an additional cost. The displayed comparison does not match distortion.

**JUDGMENT — pre-emption/limits.** Occupies semantic/spatially controlled T3 regeneration and a continuous removal–fidelity knob. A controller selecting these settings needs a distinct contribution. These attack-output PSNR values are not clean writer quality: the project's clean PSNR bar cannot by itself exclude an attack. A future attacker comparison needs its own fixed fidelity constraint. These comparisons establish neither RL superiority nor T4/T5 binding.

### C2-04 — Black-Box Forgery Attacks on Semantic Watermarks for Diffusion Models

Andreas Müller, Denis Lukovnikov, Jonas Thietke, Asja Fischer, Erwin Quiring. CVPR 2025. DOI: 10.1109/CVPR52734.2025.01950. [Canonical](https://arxiv.org/abs/2412.03283). Access: 2026-10-30. `FULL_TEXT_INSPECTED_ONLINE`: [v3](https://arxiv.org/html/2412.03283v3), §§3.1–3.3, §4.1/Table 1.

**SOURCE.** Post-hoc image forgery/removal, plus generation by reprompting. Comparator-not-RL; state/action/reward N/A. A single watermarked reference guides gradients through an unrelated diffusion inversion model. Table 1, FLUX.1 Gaussian Shading: 150 optimization steps yield detection .95, PSNR 20.14 dB, LPIPS .247; watermark averaging yields detection zero. Detection and attribution use the paper's watermark-specific thresholds. Transfer across unlike architectures is demonstrated; this is not a policy-learning comparison. The cited metrics are from arXiv v3; cached CVF snippets differ and were not substituted.

**JUDGMENT — pre-emption/limits.** Occupies one-reference surrogate-latent forgery and reprompting. Especially relevant to T4/T5: removal robustness cannot imply content binding. Neither these fidelity numbers nor the attacked watermark constructions establish success against this project's complete verifier. Query-free transfer and query-assisted stopping must be distinguished.

### C2-05 — RLCracker: Evaluating the Worst-Case Vulnerability of LLM Watermarks with Adaptive RL Attacks

Hanbo Huang et al.; [canonical author list](https://arxiv.org/abs/2509.20924v1). Preprint 2025; current metadata reports ICML 2026 acceptance. DOI: null. Access: 2026-10-30. `FULL_TEXT_INSPECTED_ONLINE`: [v1](https://arxiv.org/html/2509.20924v1), §4.2, §§5.1–5.2/Table 1, Appendix C.

**SOURCE.** Post-hoc text paraphrasing; R-full, GRPO over generated tokens. State: marked text and output prefix. Action: next token. Reward combines semantic similarity with divergence objectives against a watermarked proxy distribution; reference-policy regularization constrains drift. Table 1, Qwen2.5-3B, 1,500-token Unigram: effective success 98.5% versus SysP 4.50%; success requires semantic similarity above .7. Training uses 100 short marked samples per scheme, with separate learned models. It does not require target-detector queries for its proxy reward. No equal-total-training-cost comparison is supplied.

**JUDGMENT — pre-emption/limits.** RL watermark removal is occupied in text. This is positive evidence for learning a discrete paraphrase policy, not evidence for image carriers, strict visual fidelity, unseen diffusion families or T4/T5. Version-specific findings here should not silently inherit later v2 changes.

### C2-06 — Policy-Driven Attack: Learning to Query for Hard-label Black-box Adversarial Examples

Ziang Yan, Yiwen Guo, Jian Liang, Changshui Zhang. ICLR 2021. DOI: null. [Canonical](https://openreview.net/forum?id=pzpytjk3Xb2). Access: 2026-10-30. `FULL_TEXT_INSPECTED_ONLINE`: [primary PDF](https://openreview.net/references/pdf?id=zQ8_-FYrn3), §§3.2–3.4, §4.2/Table 1.

**SOURCE.** Post-hoc image classifier attack. R-bandit under this brief: §3.2 explicitly uses a one-step REINFORCE problem. State: current boundary image and attack context; action: sampled search direction; reward: discretized potential distortion reduction, using label queries. Table 1, ImageNet ResNet-18 mean L2 at 1,000 queries: PDA 6.751 versus HSJA 14.295. At 25,000 queries: 1.481 versus 1.479, eliminating that advantage. §4.2 explicitly omits pretraining queries because they are amortized across many images.

**JUDGMENT — pre-emption/limits.** Occupies learned query-direction selection. Repeated one-step policy optimization does not by itself establish delayed-credit RL. The low-budget advantage is credible within the reported accounting, but not evidence of equal total cost for a small watermark study. No watermark, unseen-regenerator or content-binding endpoint is tested.

### C2-07 — Robustness with Black-Box Adversarial Attack using Reinforcement Learning

Soumyendu Sarkar et al.; [full authors/canonical PDF](https://ceur-ws.org/Vol-3381/8.pdf). SafeAI workshop at AAAI, 2023, CEUR volume 3381. DOI: null. Access: 2026-10-30. `FULL_TEXT_INSPECTED_ONLINE`: proceedings PDF, §§3.2–3.6, §4, Tables 1 and 5.

**SOURCE.** Post-hoc image classifier attack; R-full, dueling DQN, discount .95. State: patch sensitivities, class probabilities, recent L2 history. Action: numbers of patches receiving/removing Gaussian noise. Reward: probability-change/distortion ratio, Eq. 2. Table 5, ImageNet ResNet-50: learned policy 169 average queries/L2 4.03 versus tuned fixed-action heuristic 210/5.62. Table 1 versus Square: 169/4.01/100% success versus 401/5/99.8%. Training uses 80% of the validation set; eight V100s serve training/evaluation. Sensitivity probing and cleanup surround the policy. Total training cost is not matched in those comparisons.

**JUDGMENT — pre-emption/limits.** Positive RL-versus-heuristic evidence and occupied patch-allocation ingredient. Query accounting needs careful reconstruction, including sensitivity passes. It does not establish watermark removal, T3 transfer or strict quality. Count only this RLAB paper, not its CVPRW/AAAI follow-ups again.

### C2-08 — Sparse Black-box Video Attack with Reinforcement Learning

Xingxing Wei, Huanqian Yan, Bo Li. IJCV 2022, author version. DOI: null. [Canonical](https://arxiv.org/abs/2001.03754). Access: 2026-10-30. `FULL_TEXT_INSPECTED_ONLINE`: [v3](https://arxiv.org/html/2001.03754v3), §§3.1–3.4, §4.5/Table 5 and Figure 7.

**SOURCE.** Post-hoc video classifier attack. R-bandit: §3.2 defines a one-step MDP despite sequential LSTM computation. State: video/frame features; action: frame-selection mask; reward: diversity, representativeness, perturbation and query penalties. FGSM plus NES supplies pixel updates. Table 5, 20-video C3D untargeted ablation at matched fooling rate: dense FGSM+NES mean perturbation 6.5037 versus full SVA 1.8624, with sparsity rising from zero to 74.65%. Figure 7 additionally compares random selection at equal frame count. Reward changes at 15,000/30,000 queries (§3.2); policy training cost is not equalized against a complete alternative budget.

**JUDGMENT — pre-emption/limits.** Occupies learned sparse allocation around a non-RL optimizer. Supports P2 as an analogy, not image watermark evidence. An LSTM is not sufficient evidence for R-full; unseen diffusion-family transfer and content binding remain untested.

### C2-09 — Prior Convictions: Black-Box Adversarial Attacks with Bandits and Priors

Andrew Ilyas, Logan Engstrom, Aleksander Madry. ICLR 2019. DOI: null. [Canonical](https://arxiv.org/abs/1807.07978). Access: 2026-10-30. `FULL_TEXT_INSPECTED_ONLINE`: [v2](https://arxiv.org/html/1807.07978v2), §§3.1–3.2, §4/Table 1.

**SOURCE.** Post-hoc image classifier attack; R-bandit, online gradient estimation with time/data priors. State: accumulated gradient estimate and current image. Action: query direction. Bandit loss targets alignment with the unknown gradient using finite-difference feedback. No pretrained rollout policy is needed. Table 1, ImageNet Inception-v3, L-infinity attack, 10,000-query cap: failures 4.6% for Bandits-TD versus NES 22.2%. On the common subset successfully attacked by NES, average queries are 703 versus 1,735. Comparisons condition on success and must retain the failure endpoint.

**JUDGMENT — pre-emption/limits.** Occupies adaptive reuse of local feedback and low-dimensional priors. A relevant comparator when detector gradients are unavailable, but not evidence that a full RL controller beats gradients or regeneration search. No watermark, strict PSNR/SSIM/LPIPS conjunction, or T4/T5 result is reported.

### C2-10 — Black-box Adversarial Attacks with Limited Queries and Information

Andrew Ilyas, Logan Engstrom, Anish Athalye, Jessy Lin. ICML 2018, PMLR 80. DOI: null. [Canonical](https://proceedings.mlr.press/v80/ilyas18a.html). Access: 2026-10-30. `FULL_TEXT_INSPECTED_ONLINE`: [conference PDF](https://proceedings.mlr.press/v80/ilyas18a/ilyas18a.pdf), §§2.1–2.3, §§3.1–3.2/Table 1.

**SOURCE.** Post-hoc image classifier attacks; comparator-not-RL. State/action/reward N/A: NES estimates gradients, followed by constrained updates; partial-information and label-only variants construct usable surrogate objectives. Table 1, targeted ImageNet Inception-v3, L-infinity .05: query-limited attack succeeds on 99.2%, median 11,550 queries; label-only attack succeeds on 90%, median 2.7 million. Evaluation uses 1,000 and 100 examples respectively. These are information-regime results, not a matched RL comparison; no comparable numerical RL advantage is extractable.

**JUDGMENT — pre-emption/limits.** Occupies derivative-free feedback search. An unavailable analytic gradient does not imply RL is necessary. Query counts can be prohibitive when each query invokes regeneration. The norm budget and classifier endpoint cannot be translated into this project's quality gates or C/J detection.

### C2-11 — Simple Black-box Adversarial Attacks

Chuan Guo, Jacob R. Gardner, Yurong You, Andrew Gordon Wilson, Kilian Q. Weinberger. ICML 2019, PMLR 97. DOI: null. [Canonical](https://proceedings.mlr.press/v97/guo19a.html). Access: 2026-10-30. `FULL_TEXT_INSPECTED_ONLINE`: [conference PDF](https://proceedings.mlr.press/v97/guo19a/guo19a.pdf), §3/Algorithm 1, §4/Table 1.

**SOURCE.** Post-hoc score-based image classifier attack; comparator-not-RL. State/action/reward N/A. SimBA tests positive/negative random basis directions and accepts a score decrease; DCT restriction supplies a frequency prior. Table 1, untargeted ImageNet ResNet-50: SimBA-DCT averages 1,283 queries, L2 3.06, success 97.8%; Bandits-TD 5,251, 5.00, 80.5%. §4 describes reproduced baseline settings and some borrowed results; the table mixes different attainable success/distortion points. No offline policy training is required, and no RL ablation is present.

**JUDGMENT — pre-emption/limits.** Strong simple frequency-search baseline for P2-inspired optimization. “Adaptive” acceptance does not establish learned control. The reported advantage concerns classifier attacks, not T3 regeneration; comparing only against unstructured random pixels would miss this simpler structured alternative.

### C2-12 — Square Attack: a Query-Efficient Black-Box Adversarial Attack via Random Search

Maksym Andriushchenko, Francesco Croce, Nicolas Flammarion, Matthias Hein. ECCV 2020. DOI: null. [Canonical](https://arxiv.org/abs/1912.00049). Access: 2026-10-30. `FULL_TEXT_INSPECTED_ONLINE`: [conference PDF](https://www.ecva.net/papers/eccv_2020/papers_ECCV/papers/123680477.pdf), §3/Algorithm 1, §4.3/Table 1.

**SOURCE.** Post-hoc image classifier attack; comparator-not-RL. State/action/reward N/A. Random localized square updates, a fixed size schedule and loss-based acceptance create structured search. Table 1, ImageNet ResNet-50, L-infinity .05, 1,000 points and 10,000-query cap: square updates with constant channel colors and stripe initialization average 73 queries versus 339 for the random-shape/constant-color ablation; both report zero failures. This isolates a useful geometric prior without learning a policy. No training-query expenditure or RL comparison is present.

**JUDGMENT — pre-emption/limits.** Occupies efficient spatially structured adaptation. P2/P6 policy proposals must beat structured heuristics, not just naive noise. These pixel attacks are comparator mechanisms, not authorization to expand the project's primary threat scope beyond T3/T4/T5. Norm-limited classification success is not watermark or content-binding success.

### C2-13 — HopSkipJumpAttack: A Query-Efficient Decision-Based Attack

Jianbo Chen, Michael I. Jordan, Martin J. Wainwright. arXiv preprint, revised 2020; publisher venue not verified here. DOI: null. [Canonical](https://arxiv.org/abs/1904.02144). Access: 2026-10-30. `FULL_TEXT_INSPECTED_ONLINE`: [v5](https://arxiv.org/html/1904.02144v5), §§III–IV-A, Eq. 9/algorithm, §V/Table I.

**SOURCE.** Post-hoc hard-label image classifier attack; comparator-not-RL. State/action/reward N/A. Boundary projection, Monte Carlo directional estimation from binary decisions, and adaptive step sizes reduce distance to the original. Table I, untargeted CIFAR-10 ResNet, 1,000 queries: median L2 .559 versus Boundary Attack 2.78 and OPT 2.07. The comparison limits online queries; it does not train a reusable RL policy. Binary-search and estimation queries are intrinsic costs.

**JUDGMENT — pre-emption/limits.** Occupies decision-only adaptive optimization. Hard-label detector access alone does not motivate RL; a policy must improve over boundary-estimation alternatives at matched total expense. Its boundary geometry, norm budget and classification endpoint do not establish feasibility for low-FPR content-bound watermark detection, stochastic diffusion queries, or unseen-family transfer.

### C2-14 — Steganalysis on Digital Watermarking: Is Your Defense Truly Impervious?

Pei Yang, Hai Ci, Yiren Song, Mike Zheng Shou. arXiv preprint, 2024; journal unverified. DOI: null. [Canonical](https://arxiv.org/abs/2406.09026). Access: 2026-10-30. `FULL_TEXT_INSPECTED_ONLINE`: [v1 HTML](https://arxiv.org/html/2406.09026), §§3.2–3.3, §§4.1/4.4, Table 1/Figure 4, Appendix A.5/Table 2.

**SOURCE.** Post-hoc image removal/forgery; comparator-not-RL. State/action/reward N/A. Averaging marked versus unmarked collections estimates a reusable additive pattern; subtracting/adding it removes/forges marks. Black-box collection can be unpaired. Table 1, Tree-Ring detection at 1% FPR: unattacked 1.00; five-image averaging .08; 5,000-image averaging .14. Appendix Table 2, black-box 5,000-image PSNR: 15.47 versus unattacked 15.62 dB; §4.1 references the unmarked counterpart, not attack input. Thus this is not a matched attack-fidelity gate. The forgery-table/prose relationship is ambiguous; no forgery effect extracted. Collection size is an attacker resource.

**JUDGMENT — pre-emption/limits.** Occupies simple pattern stealing and motivates comparing learned attacks against collection-based statistics. Content-dependent constructions may change applicability. These outcomes neither show RL advantage nor establish T4/T5 success against a bound verifier.

### C2-15 — Invisible Image Watermarks Are Provably Removable Using Generative AI

Xuandong Zhao et al.; [canonical/full author list](https://arxiv.org/abs/2306.01953). NeurIPS 2024. DOI: null. Access: 2026-10-30. `FULL_TEXT_INSPECTED_ONLINE`: [conference PDF](https://papers.neurips.cc/paper_files/paper/2024/file/10272bfd0371ef960ec557ed6c866058-Paper-Conference.pdf), §§3–4, Definition 4.2/Theorems 4.3–4.4, §5/Figure 4/Table 1.

**SOURCE.** Post-hoc image regeneration; comparator-not-RL. State/action/reward N/A. Gaussian corruption followed by reconstruction suppresses small watermark differences. The ROC bound depends on watermark perturbation size, encoder sensitivity and noise; fidelity additionally depends on denoiser assumptions. §5.3 reports over 99% removal for DwtDctSvd, RivaGAN and SSL; StegaStamp needs stronger corruption. Baselines include conventional distortions and learned compression. Figure 4 presents quality/removal trade-offs: no single comparable numerical effect at this project's strict-quality conjunction is extractable. Regeneration itself needs no detector feedback.

**JUDGMENT — pre-emption/limits.** Occupies T3 regeneration and conditional information-loss bounds. It does not prove universal impossibility for every carrier at every quality budget. RL cannot be credited with escaping assumptions without identifying which one changes; no RL comparison is provided.

## Uncounted, inaccessible and cross-cluster leads

| Lead | Inspection/disposition |
|---|---|
| [Sarkar CVPRW2023](https://openaccess.thecvf.com/content/CVPR2023W/AML/papers/Sarkar_Robustness_With_Query-Efficient_Adversarial_Attack_Using_Reinforcement_Learning_CVPRW_2023_paper.pdf) | `UNINSPECTED` at this publisher version: repeated PDF/HTML 403, alternate URL routes unsuccessful. C2-07 is the separately identified SafeAI primary paper, not a claim to have read this CVPRW PDF. Do not import CVPRW abstract percentages. |
| [Sarkar AAAI2024 demonstration](https://ojs.aaai.org/index.php/AAAI/article/download/30579/32741) | Full three-page report inspected, pp.23829–23830 methods/results. No independently extractable aggregate comparator table. Excluded from count to avoid inflating the RLAB lineage. DOI 10.1609/aaai.v38i21.30579. |
| Sarkar AAAI2025 custom-filter platform | Author page exposes a later report. Not fully inspected; not counted or used for numerical claims. |
| [DRIFT](https://arxiv.org/abs/2609.08213), [WAW](https://arxiv.org/abs/2605.16796), [RAVEN](https://arxiv.org/abs/2601.08832), [LFM](https://arxiv.org/abs/2610.02010) | Root owns cards in [C12 dossier](c12-recent.md); zero duplicate C2 cards. Root reports DRIFT as DPPO refinement, WAW as learned classification plus deterministic rewriting rather than RL. Use C12's inspected locators for those claims. LFM was opened during discovery but is deliberately excluded here. |
| [RemTraceNet](https://arxiv.org/abs/2609.31694), [DnD](https://arxiv.org/abs/2609.31693), [forensic stealth](https://arxiv.org/abs/2605.09203), [DAPAO](https://ieeexplore.ieee.org/document/11699107) | Sent to root as recent leads; not full-text-inspected by this C2 worker, not counted. |
| [Semantic regeneration](https://arxiv.org/abs/2505.08234), [IEEE 2020 attack](https://ieeexplore.ieee.org/document/9123270) | Relevant follow-up candidates, uninspected; no inference from abstracts. |
| Han model-inversion RL, attacks targeting RL agents, model-IP watermarking, LLM embedding | Different protected object/task; excluded. C2 includes classifier attacks because adaptive black-box attacks are explicitly in its scope, not because all adversarial ML is interchangeable. |
| Tang SMER | Transfer-cluster lead assigned elsewhere; not counted here. |

Access failures also included challenged direct OpenReview PDFs and unavailable arXiv HTML version suffixes. Successful primary alternatives are the exact URLs in the cards. No failed fetch was counted as inspection. Search coverage is substantial but not exhaustive; no absence or first-ever claim follows from uninspected leads.

## Cluster synthesis

**JUDGMENT — answer to the equal-budget question.** These papers support using learned attackers as a plausible research arm. They do **not** demonstrate that full RL beats the strongest simple alternative under equal total budget for post-hoc, content-bound image watermarking under diffusion regeneration. This is a missing comparison within inspected evidence, not a claim that no such paper exists. Root's recent DRIFT card must be included when deciding image-RL novelty; this file alone must not be used to claim its absence.

| Evidence question | What the inspected evidence permits | What remains unresolved |
|---|---|---|
| Does RL ever improve adaptive attacks? | C2-07 directly compares a policy with a tuned heuristic; C2-05 demonstrates an effective learned text attacker. | Complete training cost, strength of all alternative policies, stochastic variability, and transport to image watermarks. |
| Does policy gradient establish R-full? | C2-06 and C2-08 expose one-step objectives. Their contribution can be useful without delayed credit assignment. | Whether a proposed regeneration chain genuinely needs stateful decisions rather than choosing a complete action once. |
| Are gradients unavailable in watermark attacks? | C2-01 and C2-04 give surrogate routes; C2-02 avoids target-detector feedback; C2-03 has supervised control. | Availability and fidelity of those routes for the project's actual reader and allowed attacker knowledge. |
| What should a strong comparator include? | C2-09–13 provide bandit priors, NES, structured basis search, localized search and hard-label boundary estimation. | Adaptation to the same T3/T4/T5 action set, with identical source/seed/quality/query accounting. Pixel attacks themselves are not new project threat gates. |
| Does transfer evidence solve unseen regeneration? | C2-04 shows transfer can occur across unlike architectures. | A trained policy retaining advantage on a completely excluded regenerator family at strict quality and with the complete content-bound verifier. |
| Can removal evidence settle ownership security? | C2-04 and C2-14 make forgery/pattern transfer a separate consideration. | T4 copy-paste and T5 collision outcomes against actual content binding; reported watermark detection cannot substitute for C/J. |

**JUDGMENT — P1/P2/P3 implications.** P1 per-image arm selection should first be compared with the best fixed arm and a simple feature-conditioned selector; none of these cards establishes that selecting one configuration needs full RL. P2 spatial/frequency allocation has close attack-side precedents and strong non-RL alternatives; its novelty must reside in a watermark-specific mechanism or a robust equal-cost result. P3 selection of surrogate/transform/noise at successive writer steps needs evidence that earlier choices change useful later observations. A preset schedule, random schedule, differentiable weighting and one-step selection are necessary conceptual comparators before claiming delayed-credit benefit. The strongest direct connection of C2 is P6: red-team selection under the already authorized T3/T4/T5 action set.

**JUDGMENT — accounting needed to make a future claim credible.** Separate target-detector queries, generator/encoder calls, surrogate training, policy training, hyperparameter search, evaluation, and rejection/quality checks. State whether cost is per attacked image or amortized over a declared deployment size. A query unit must identify whether one batch or every evaluated image counts. Training a policy on expensive feedback and then reporting only cheap inference can be sensible operationally, but it cannot answer the brief's equal-total-budget question without the amortization assumption. Count failed attacks and sources rejected by strict quality. A reward penalty is not proof that PSNR>35, SSIM>.9 and LPIPS<.1 hold for accepted outputs.

**JUDGMENT — occupied ingredient versus identical construction.** Adaptive attacks, learned spatial selection, one-step learned query policies, semantic regeneration control and one-reference forgery are occupied. Combining an RL label with one of them is insufficient novelty. A potentially distinct question is whether feedback about content binding and quality permits an efficient T3/T4/T5 policy that generalizes to an excluded family and beats the best non-RL attack under equal complete expenditure. The answer is presently conditional; no experiment was run and no F6 outcome was consulted.

## Exact completion accounting

- Counted cards: **15**, IDs C2-01 through C2-15, all `FULL_TEXT_INSPECTED_ONLINE` with method and evaluation locators.
- Setting coverage: **6 image-watermark papers + 1 text-watermark paper + 8 adaptive image/video classifier-attack papers**. No unrelated embedding, attacks-on-RL-agent, or model-IP papers fill the floor.
- Classification: **2 R-full** (C2-05, C2-07); **3 R-bandit** (C2-06, C2-08, C2-09); **10 comparator-not-RL**. No R-game paper counted.
- Queries: **30**, across **6 scholarly index contents searched indirectly**, five with relevant hits. No native-index count asserted.
- Recent C12 duplicates counted here: **0**. AAAI2024 RLAB demonstration counted additionally: **0**.
- Floor reached; **no exhaustion exception invoked**. Inaccessible relevant versions and uninspected leads remain disclosed. These counts establish coverage, not completeness or an absence proof.
