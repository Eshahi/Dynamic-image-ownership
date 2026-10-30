# C12 — recent regeneration and transfer robustness

Access date throughout: 2026-10-30. Window: 2025-10-30 through 2026-10-30. Status is FULL_TEXT_INSPECTED_ONLINE unless explicitly excluded. No local verification or reproduction is claimed. Fifteen completed cards: thirteen first posted within the window and two2026 publication/update entries with older preprints, explicitly identified. Full-text inspection does not imply endorsement of a paper's evidence quality. DOI is unverified unless supplied.

## Issued discovery queries

All queries below were actually issued through web search over the indicated scholarly index's content; these are indirect index searches, not claims of native index API access. Mixed-result batches were inspected collectively. Empty/irrelevant responses remain in the log.

| ID | Query | Index content | Result / follow-up |
|---|---|---|---|
| C12-Q01 | site:arxiv.org watermark regeneration robustness diffusion 2026 | arXiv | Recent regeneration candidates; full texts opened below. |
| C12-Q02 | site:openreview.net watermark regeneration 2026 | OpenReview | CtrlRegen+ lead. |
| C12-Q03 | site:openaccess.thecvf.com 2026 watermark regeneration | CVF | RAVEN, PECCVAI and ClusterMark leads. |
| C12-Q04 | site:ieeexplore.ieee.org 2026 watermark diffusion regeneration | IEEE Xplore | Robustness-security paradox lead; full text not yet inspected. |
| C12-Q05 | site:arxiv.org 2026 watermark "reinforcement learning" | arXiv | DRIFT lead, inspected. |
| C12-Q06 | site:dl.acm.org watermark regeneration diffusion 2026 | ACM DL | IH&MMSec leads. |
| C12-Q07 | site:dblp.org 2026 watermark regeneration | DBLP | Gesny/Giboulot and WAW bibliographic leads. |
| C12-Q08 | site:arxiv.org 2026 watermark "MarkNull" OR "rank" OR "transfer" | arXiv | Mixed results; no MarkNull assertion made. |
| C12-Q09 | site:arxiv.org "watermark" "regeneration" "2026" "MarkNull" | arXiv | No verified new MarkNull paper. |
| C12-Q10 | site:openreview.net 2026 watermark robustness regeneration transfer | OpenReview | Regeneration/transfer leads, pending inspection. |
| C12-Q11 | site:openaccess.thecvf.com/content/CVPR2026 watermark "regeneration" | CVF | CVPR full-text leads. |
| C12-Q12 | site:semanticscholar.org 2026 watermark diffusion robustness | Semantic Scholar | Bibliographic discovery only. |
| C12-Q13 | "CtrlRegen" watermark arxiv | General web / arXiv lead | Corrected date: ICLR2025, outside C12 window. |
| C12-Q14 | "RAVEN" "Erasing Invisible Watermarks" arxiv | General web / arXiv lead | arXiv2601.08832; author confirms CVPR2026. |
| C12-Q15 | "PECCVAI" arxiv | General web / CVF lead | CVPR2026 title recovered; full text pending. |
| C12-Q16 | "ClusterMark" arxiv | General web / author lead | Author page confirms CVPR2026; CVF access failed. |
| C12-Q17 | site:arxiv.org "PECCVAI" | arXiv | No new exact-spelling full text. |
| C12-Q18 | site:arxiv.org "PECCAVI" watermark | arXiv | 2506.22960, first posted June2025; publication-date eligibility checked separately. |
| C12-Q19 | site:arxiv.org "Rel-Zero" | arXiv | Initial batch did not recover exact full text. |
| C12-Q20 | site:arxiv.org watermark regeneration 2026 robust imperceptible transfer | arXiv | Vanishing Watermarks, FeatMark; audio Latent-Mark is adjacent, not image floor. |
| C12-Q21 | "Rel-Zero" "Harnessing" | General web / arXiv + CVF leads | 2603.17531 and CVPR2026 supplement recovered. |
| C12-Q22 | watermark "regeneration" "2026" "reinforcement" | General web | DRIFT rediscovered; no new eligible RL-image writer. |
| C12-Q23 | "PECCVAI" "CVPR" 2026 | General web / CVF | Primary CVF publication confirmation; older preprint inspected separately. |
| C12-Q24 | "Decoupling Defense Strategies" watermark arxiv | General web / arXiv + CVF | AdvMark full text recovered. |

## C12-01 — DRIFT: Removing Diffusion Watermarks by Deflecting the Generative Trajectory

Rui Bao, Zheng Gao, Xiaoyu Li, Xiaoyan Feng, Yang Song, Jiaojiao Jiang. 2026 arXiv preprint, v1, 8 September; venue unverified. [Full text](https://arxiv.org/html/2609.08213v1). Read §§3–5, Appendix D and E, especially Tables 3, 6, 7.

- **Setting/class:** attacks generation-time image watermarks. Stochastic regeneration and verifier-guided ladder are non-RL; optional fidelity refinement is R-full (DPPO).
- **State/action/reward:** source/retained-image DINOv2 features, history and round; re-noising, two guidance weights and stop; quality increment minus steps plus terminal bonuses.
- **Comparator/effect:** nonadaptive versus non-RL ladder: mean attack success 96.8→99.7%, LPIPS .19→.16. Refinement on 225 images: LPIPS .136→.114 and PSNR 24.95→25.19, 1.16 rounds, zero survival under its verifier. Reward/back-off ablations are provided.
- **Pre-emption:** RL-assisted diffusion watermark removal and adaptive strength/fidelity scheduling already exist.
- **Limits:** no demonstrated equal-total-compute RL advantage over a strong non-RL refinement controller. Verifier-gated retention, independently of learning, ensures feasibility. Generation-time families do not establish benefit for the F5 post-hoc writer or unseen encoders.

## C12-02 — Exploring Weaknesses of Generative Image Watermarks against Latent Frequency Masking

Kirill Aistov, Khaled Abud, Irina Serzhenko, Egor Kovalev, Aleksey Yakushev, Aleksandr Akimenkov, Dmitry Obydenkov, Yury Markin, Sergey Lavrushkin, Dmitriy Vatolin, Anastasia Antsiferova. 2026 arXiv preprint v1, 1 October; venue unverified. [Full text](https://arxiv.org/html/2610.02010v1). Read §III algorithm/threat/bound, §§IV–V, Table I.

- **Setting/class:** image watermark removal using a public LDM and verifier; non-RL frequency replacement. State is encoded image; action is mask/channel/radius and blend coefficient; no learned reward.
- **Mechanism:** replace selected latent Fourier coefficients with Gaussian or regenerated-image coefficients, then decode. No attack gradients.
- **Comparator/effect:** across tested watermarks on DiffusionDB, diffusion replacement gives TPR@1%FPR .44, PSNR 28.4, LPIPS .043; ordinary diffusion regeneration .51, 21.7, .205. Gaussian replacement gives .36, 21.6, .119. Gaussian Shading remains difficult; diffusion replacement fails on MaxSive.
- **Pre-emption:** simple latent frequency control is an essential alternative to learned spatial/frequency attack policies.
- **Limits:** tested base model is SD2.1; this is not unseen-encoder transfer evidence. Mask selection uses knowledge/queries. The decoder-Lipschitz bound is qualitative, with no operational numerical constant.

## C12-03 — Watermarks Attack Watermarks: Re-Watermarking as a Generic Removal Strategy

Maria Bulychev, Neil G. Marchant, Benjamin I. P. Rubinstein. 2026 arXiv preprint v1, 16 May; venue unverified. [Full text](https://arxiv.org/html/2605.16796v1). Read §§3–6, especially policy training and Table 4.

- **Setting/class:** post-hoc and generation-time image victims; learned classifier plus deterministic interference-table policy, **not RL**. State: predicted watermark family; action: which public embedder to reapply; objective: erasure with low distortion, no sequential reward.
- **Comparator/effect:** versus regeneration/VAE/rinsing at comparable normalized quality damage, MS-COCO Pixel Seal TPR@1%FPR .029 versus .080 for diffusion regeneration; Tree-Ring .280 versus .960; WAM is a counterexample, .862 versus .346. RoSteALS bit accuracy .749 still coexists with TPR .992.
- **Pre-emption:** family identification followed by attack selection, generic re-watermarking, and an interference matrix already exist without RL.
- **Limits:** performance differs by victim and identification errors. Bit corruption is not detection failure. The attack uses a fixed family set and does not prove transfer to an unseen watermark. Re-watermarking beyond T3/T4/T5 is background only, not an authorized experiment here.

## C12-04 — Do Modern Post-Hoc Watermarking Methods Beat Broken-Arrows?

Enoal Gesny and Eva Giboulot. IH&MMSec 2026; arXiv v1, 26 May. [Full text](https://arxiv.org/html/2605.27135v1), DOI 10.1145/3785353.3815081. Read §§2–4 and experimental settings/results.

- **Setting/class:** post-hoc image detection; classical keyed hypercones versus whitened modern decoders. Non-RL; no policy state/action/reward. Attack choices are controlled comparison factors.
- **Comparator/effect:** 200 natural images, per-image randomized keys, all embeddings scaled to 42 dB. TrustMark/VideoSeal versus Broken-Arrows; gradient attack budget 250, black-box CGBA budget 2,000. White-box removal of modern marks approaches 60 dB versus about 40 dB for Broken-Arrows; black-box 100%-success thresholds differ by about 15 dB. Blind regeneration requires roughly 30 dB or worse across all three.
- **Pre-emption:** claims that modern learned carriers automatically dominate classical alternatives, or that decoder robustness equals security.
- **Limits:** zero-bit conversion, particular attacks and 200 images; no RL comparison or transferable ownership binding. Security conclusions depend on oracle access. The regeneration comparison is relevant to C12; conventional attacks are context only.

## C12-05 — ONRW: Optimizing inversion noise for high-quality and robust watermark

Xuan Ding, Xiu Yan, Chuanlong Xie, Yao Zhu. 2026 arXiv preprint v1, 24 January; venue unverified. [Full text](https://arxiv.org/html/2601.17388v1). Read §§3.1–3.2, 4.2–4.5, Tables 1, 3, 4.

- **Setting/class:** existing-image marking through inversion and diffusion reconstruction; non-RL gradient optimization. State/action/reward are not an RL formulation: optimize inversion noise with decoder loss, attention consistency and pixel/pseudo-mask constraints; train extraction with random distortions.
- **Comparator/effect:** §4.4 reports diffusion-reconstruction bit-accuracy advantages of 12/11/5 percentage points over Stable Signature/SSL/HiDDeN; exact operating-point dependence is not resolved by that prose. Clean COCO PSNR 27.11 dB versus Stable Signature 25.55. Removing null-text optimization gives PSNR 26.58 and bit accuracy .97182 versus .96545 with it.
- **Pre-emption:** optimizing pre-encoder/inversion noise and attention-constrained marking is occupied without RL.
- **Limits:** far below this project's strict >35 dB embedding requirement; bit accuracy is not bound detection or exact payload recovery. No independent-encoder generalization claim established. Table 1's ImageNet LPIPS .559 conflicts with surrounding quality language; do not silently correct it.

## C12-06 — Optimizing and Securing the Modern Watermarking Channel for Images

Enoal Gesny, Eva Giboulot. 2026 arXiv preprint v1, 28 September; venue unverified. [Full text](https://arxiv.org/html/2609.34744v1). Read §§2–6, Appendix H.2/Table 6.

- **Setting/class:** post-hoc neural image watermarking, SNW. Non-RL; no sequential policy/reward. Jointly learn aligned, isotropic encoding/decoding projections; secret semi-orthogonal key selects a subspace and embedding energy allocation.
- **Comparator/effect:** same architectural family as PixelSeal. On 200 MFlickr images, estimated capacity after eight SANA steps: SNW 111.5 bits versus PixelSeal 19.4, VideoSeal 21.5, TrustMark 2.3; after twenty steps all are about 0.7–0.9 bits. These are channel-model capacity estimates, not observed exact-message success rates.
- **Pre-emption:** carrier dimension, keying and coding efficiency can improve robustness without RL; statistical channel/security analysis is already active.
- **Limits:** PCA security is conditional on a statistical threat model, not universal forgery security. Training and decoder change, so this cannot establish what a fixed F5 reader permits. Finite SANA attacks do not certify arbitrary regeneration; quality-normalized comparison must be examined before importing effect sizes.

## C12-07 — RAVEN: Erasing Invisible Watermarks via Novel View Synthesis

Fahad Shamshad, Nils Lukas, Karthik Nandakumar. CVPR2026, verified on [author publication list](https://www.cse.msu.edu/~nandakum/publications.html); inspected [arXiv v1](https://arxiv.org/html/2601.08832v1), 13 January 2026. Read §§3–5 and Table 5; CVF supplement selection protocol inspected.

- **Setting/class:** no-detector-query removal of post-hoc and generation-time image marks. Non-RL. State: image latent; fixed/randomized actions: partial inversion, latent viewpoint translation, correspondence attention, color transfer; no learned reward.
- **Comparator/effect:** MS-COCO average TPR@1%FPR .026 versus UnMarker .078; FID 40.18 versus 49.85. Across v2.1/v2.0/v1.5 backbones TPR .026/.026/.029 and bit accuracy .523/.519/.547.
- **Pre-emption:** strong frozen-model regeneration and model-independent attack control are already available without RL.
- **Limits:** FID/CLIP averages do not enforce per-image semantic binding or strict quality. Different backbone versions are not proof of a genuinely excluded encoder family. The preprint inconsistently describes 14/15/16 watermark methods; retain the reported table comparison without harmonizing that discrepancy. Geometry-assisted regeneration is T3-relevant; isolated geometric attacks remain out of experimental scope.

## C12-08 — Disentangle and Drop: Robust Universal Removal of Image Watermarks via Reconstructive Grayscale Residual Decomposition

Qi Li et al. ([full author list and text](https://arxiv.org/html/2609.31693v1)). arXiv preprint v1, 18 September2026; venue unverified. Read §§3–7, Tables3–5.

- **Setting/class:** post-hoc/generation-time image removal, non-RL learned reconstruction. State/action/reward: no policy; encode grayscale structure and auxiliary residual, suppress residual, apply light diffusion reconstruction; supervised reconstruction/removal losses.
- **Comparator/effect (SOURCE):** fixed K=.925/U=.02/S=.04 gives six-family mean BER .400, PSNR28.98, SSIM.902. Tree-Ring removal .47 at27.57dB versus CtrlRegen .22 at21.68dB. Table4 includes two60-step diffusion baselines and learned compression; DnD does not win every metric.
- **Pre-emption (JUDGMENT):** explicit carrier/residual separation and global fixed attack settings already compete with adaptive policies.
- **Limits:** algorithmic zero-residual description differs from reported2% residual retention. BER approaching.5 only weakens the evaluated decoder; it is not an information-erasure proof. No equal-budget RL comparison, exact-payload endpoint, or general unseen-family guarantee.

## C12-09 — On the Robustness of Watermarking for Autoregressive Image Generation

Andreas Müller et al. ([authors/full text](https://arxiv.org/html/2604.11720v1)); inspected arXiv v1,13April2026. [Author page](https://and-mill.github.io/) reports NeurIPS2026 acceptance; accepted version not inspected. Read §§3–4, Table1.

- **Setting/class:** generation-time autoregressive image marks, non-RL attacks. No policy reward; choose nearby VQ tokens or optimize image perturbations to move encoder latents away from originals/toward a marked reference.
- **Comparator/effect (SOURCE):**100 images per target model, TPR@1%FPR. For IndexMark/WMAR/ClusterMark, black-box VQ regeneration TPR .03/.12/.39 versus ordinary regeneration .52/.36/.85; PSNR20.32/21.59/20.49 versus22.91/24.09/22.95. LatentOpt removal gives white-box TPR0/0/0 but unrelated-encoder .63/.42/.78 around32dB.
- **Pre-emption (JUDGMENT):** token-space attack control and latent-response optimization are occupied; transfer can degrade sharply despite white-box success.
- **Limits:** different generative task/reader, differing distortion, no RL or F5 ownership binding. White/grey/black access levels must not be pooled as independent-family success.

## C12-10 — ClusterMark: Towards Robust Watermarking for Autoregressive Image Generators with Visual Token Clustering

Denis Lukovnikov, Andreas Müller, Erwin Quiring, Asja Fischer. CVPR2026 ([author confirmation](https://and-mill.github.io/)); [arXiv v2](https://arxiv.org/html/2508.06656v2),10April2026 inspected §§3–4, Table1. First preprint8August2025: included as a2026 publication/update, not a new-in-window invention.

- **Setting/class:** generation-time AR images, non-RL. Cluster codebook tokens, hash preceding clusters into green sets, bias logits; optional supervised token/cluster classifier. State/action/reward: no learned control policy.
- **Comparator/effect (SOURCE):** LlamaGen-B regeneration AUROC/TPR@1%FPR .997/.972 with64clusters versus no-clustering .916/.710 and IndexMark .951/.761; FID6.12/5.90/5.84. LlamaGen-L clustered TPR .997 versus IndexMark .834. Evaluation includes2000marked+2000null and SD2.1 diffusion regeneration.
- **Pre-emption (JUDGMENT):** grouping stable carrier states can improve retention without RL.
- **Limits:** generator access and changed carrier/reader; not a post-hoc fixed-reader result. Hash-prefix tuning and classifier training cost must be counted; FID is not per-image strict quality or semantic binding.

## C12-11 — FeatMark: Feature-level Watermark Protection against Mimicry Attacks with Diffusion Models

Haoyang Li, Ruoxi Sun, Qingqing Ye, Benjamin Zi Hao Zhao, Yaxin Xiao, Jason Xue, Haibo Hu. arXiv preprint v1,25September2026; [full text](https://arxiv.org/html/2609.30980v1). Read §§3–4, Tables4–6, AppendixG; venue unverified.

- **Setting/class:** released images influence mimicry fine-tuning; private edited exemplars and reader. Non-RL selection: VLM evidence/executability selects semantic concept, localized edit plus gradient cloak; no sequential reward.
- **Comparator/effect (SOURCE):** VGGFace2 diffusion-attack bit-accuracy changes: FeatMark−.01, Tree-Ring−.21, Stable Signature−.99 (Table5); WMA-Diff60 FeatMark−.02 versus RivaGAN−.45 (Table6). Noisy-upscaling results include losses up to.31 (Table4), tempering the abstract's broad robustness language.
- **Pre-emption (JUDGMENT):** semantic feature banks and automatic pre-embedding feature choice already exist without RL.
- **Limits:** training-data attribution differs from F5 instance binding; reader and private side information change. Distributional fidelity/human study does not establish strict per-image PSNR or T4/T5. Method reporting alone does not show equal-cost advantage or independent-family transfer.

## C12-12 — Rel-Zero: Harnessing Patch-Pair Invariance for Robust Zero-Watermarking Against AI Editing

Pengzhen Chen, Yanwei Liu, Xiaoyan Gu, Xiaojun Chen, Wu Liu, Weiping Wang. CVPR2026, verified by [official repository](https://github.com/JerCCC7/Rel-Zero); [arXiv v2](https://arxiv.org/html/2603.17531v2),15June2026. Read §§3–5, Table1, AppendicesB/C/F/G.

- **Setting/class:** image fingerprint/zero-watermark with externally stored patch-pair indices; non-RL supervised MLP. State/action/reward: no policy; learn top50 stable relations from ViT features under SD1.4 VAE reconstruction, compare overlapping index sets at verification.
- **Comparator/effect (SOURCE):** reported deterministic-regeneration TPR@.1%FPR85.13%, versus ConZWNet.10%, FGPCET1.13%, VINE99.98%; no embedding distortion.
- **Pre-emption (JUDGMENT):** stable relational feature selection plus registry reference already exists. It is a substantial alternative to learned verification control.
- **Limits:** AppendixF assumes independent binomial matches; this is not demonstrated empirical adaptive FPR control. Shared patches induce dependence. Registry side information differs from blind decoding. Arnold permutation is not established cryptographic authentication. Runtime prose/table disagree on memory(.3/1.5GB); no timing imported. Semantic near-duplicate or adversarial collision security is unproven.

## C12-13 — Vanishing Watermarks: Diffusion-Based Image Editing Undermines Robust Invisible Watermarking

Fan Guo, Jiyu Kang, Qi Ming, Emily Davis, Finn Carter. arXiv preprint v1,24February2026; [full text](https://arxiv.org/html/2602.20680v1), venue unverified. Read §§3–5, Algorithm1, Table1.

- **Setting/class:** post-hoc image watermark removal; non-RL SD1.5 regeneration plus final latent gradient toward a dummy decoded payload. State/action/reward: no learned policy; one late gradient, lambda=.5.
- **Comparator/effect (SOURCE, unreliable endpoint):** on500COCO images, Table1 labels VINE regeneration/guided accuracy24.5%/1.6%, with mean attack PSNR31.8/30.5dB. These are recorded as paper claims, **not usable effect estimates**.
- **Pre-emption (JUDGMENT):** late decoder-guided diffusion optimization is described without RL, but stronger established references should carry this claim.
- **Limits:** §4 defines StegaStamp bit accuracy and other methods exact-message success; §5 then mixes them and calls7.4% correct bits chance-level. Chance for independent binary bits is50%, not7.4%. Prose says repeated denoising backpropagation while Algorithm1 updates only at t=1. Internal endpoint/algorithm contradictions block importing its quantitative conclusions or capacity claims.

## C12-14 — PECCVAI: Overcoming the Brittleness of AI Image Watermarking Under Visual Paraphrasing Attacks

Shreyas Dixit, Ashhar Aziz, Shashwat Bajpai, Vasu Sharma, Aman Chadha, Vinija Jain, Amitava Das. [CVPR2026 publication](https://openaccess.thecvf.com/content/CVPR2026/html/Dixit_PECCVAI_Overcoming_the_Brittleness_of_AI_Image_Watermarking_Under_Visual_CVPR_2026_paper.html). Inspected older [PECCAVI preprint v1](https://arxiv.org/html/2506.22960v1),28June2025, §§3–4/Table1; accepted PDF access failed. Publication-window entry, not a newly invented2026 method.

- **Setting/class:** post-hoc images, non-RL saliency/stability selection. State: regions surviving five paraphrases; actions: region/channel/frequency strength, random patch and quality blend; no learned sequential reward.
- **Comparator/effect (SOURCE):**100COCO sample: XRAI-top30 WDP .92/.87 at SDXL strengths.1/.2, PSNR29.56; WAM .63/.56,46.05dB; ZoDiac .81/.70,28.47dB (Table1).
- **Pre-emption (JUDGMENT):** P2 stable-region and multichannel allocation under regeneration already exists without RL.
- **Limits:** unequal embedding quality, below project's strict35dB. Maximizing patch/channel detection scores requires multiplicity calibration; WDP is not our C/J. Region discovery itself pays paraphrase cost. Cross-family training/testing separation and accepted-version differences remain unresolved.

## C12-15 — Decoupling Defense Strategies for Robust Image Watermarking

Jiahui Chen, Zehang Deng, Zeyu Zhang, Chaoyang Li, Lianchen Jia, Lifeng Sun. CVPR2026 ([CVF paper](https://openaccess.thecvf.com/content/CVPR2026/papers/Chen_Decoupling_Defense_Strategies_for_Robust_Image_Watermarking_CVPR_2026_paper.pdf)); inspected [arXiv v1](https://arxiv.org/html/2602.20053v1),23February2026, §§3–4, Algorithms1–2/Tables1–3.

- **Setting/class:** post-hoc images, AdvMark non-RL. Fine-tune encoder with conditional decoder updates, then ten-step gradient image optimization. State/action/reward: no policy; omit already-successful attacks from loss, enforce PSNR floor36, constrain distance to prior carrier.
- **Comparator/effect (SOURCE):** COCO bit accuracy under trained SD1.4/untrained SD1.5 regeneration .87/.87 versus MBRS .70/.70 and VINE .74/.75. AdvMark128px/30bits PSNR37.0 versus MBRS32.1. Without stage2 regeneration .54; without stage1 .88 but quality34.7 (Table3).
- **Pre-emption (JUDGMENT):** quality-aware stopping, dynamic attack-loss gating, constrained per-image optimization and two-stage defense are occupied.
- **Limits:** SD1.4→1.5 is not independent-encoder transfer. Models/resolutions/payloads differ; baselines are selectively fine-tuned. The robustness theorem assumes a certified local robust ball and bounds movement; empirical attack survival does not establish that assumption. No RL or content-bound T4/T5 evidence.

## Synthesis and count

Fifteen distinct full texts inspected, twenty-four actual discovery queries across arXiv, OpenReview, CVF, IEEE Xplore, ACM DL, DBLP and Semantic Scholar content plus general web. Two publication-window cards explicitly rely on preprints predating the window; no duplicate versions are counted. This is a literature update, not an exhaustive chronological census.

DRIFT directly occupies optional RL-guided refinement of a diffusion-watermark removal attack. It does not demonstrate RL writing a post-hoc content-bound mark with a fixed F5 reader, nor equal-total-budget superiority of the refinement. AdvMark, PECCAVI, FeatMark, SNW and ClusterMark occupy substantial adaptive-carrier/optimization ingredients without RL. Rel-Zero adds detector side information; it must not be presented as blind watermark recovery. Vanishing Watermarks supplies a concrete warning against converting ambiguous published accuracy into our acceptance endpoints.

## Excluded / pending leads

- Soft Binding under Real-World Image Transformations (arXiv:2610.04151): method inspected, but ordinary transformations without regeneration; excluded from C12 count rather than used to fill it.
- What Limits Robustness in Deep Image Watermarking (arXiv:2609.01050): PDF accessible; method/results still pending and direct regeneration relevance unestablished.
- CtrlRegen/Plus is arXiv:2410.05470, ICLR2025, not a 2026 discovery; excluded from this date window and passed to C2.
- RemTraceNet (arXiv:2609.31694v1): method/evaluation inspected as an adjacent forensic detector, not counted. Detecting prior watermark removal is neither recovering a watermark nor proving ownership. Its checkpoint is trained per known attack pipeline and its reported operating points are test-ROC based; no deployment FPR guarantee imported.
- PixelSeal (arXiv:2512.16874v1): method inspected; regeneration relevance not established from inspected sections, not counted.
- Latent-Mark (arXiv:2603.05310): audio-codec analogy only, UNINSPECTED; not an image robustness floor filler.
