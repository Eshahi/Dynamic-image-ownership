# C9: sequential verification, active observation and error control

Inspected online 2026-10-30. Eight distinct full-text cards; no exhaustion exception. Primary methods and evaluations were opened, not inferred from abstracts. Journal DOI/status not independently verified unless stated. SOURCE describes the paper; INFERENCE describes this project. No experiments reproduced. Sequential statistical validity is not itself reinforcement learning.

## C9-01 — Time-uniform, nonparametric, nonasymptotic confidence sequences

Steven R. Howard, Aaditya Ramdas, Jon McAuliffe, Jasjeet Sekhon. arXiv:1810.08240v9 (2022 revision of 2018 submission); journal metadata/DOI not reverified. [Full text](https://arxiv.org/html/1810.08240v9). Inspected §2, §4.1 Theorem 4, §5 Figure 7, §6.

SOURCE: Non-RL sequential inference. Observations are adapted to a filtration; the target can be their average conditional expectation. Bounded observations and predictable predictions give empirical-Bernstein confidence sequences; sub-psi supermartingale assumptions support other boundaries. State is accumulated evidence, action is continue/stop, and there is no learned reward policy. Theorem 4 provides simultaneous coverage over all times, including optional stopping. Figure 7 uses 1,000 simulations of 100,000 observations. For rare Bernoulli and asymmetric three-point distributions, naive variance substitution undercovers; empirical-Bernstein boundaries retain coverage with useful width. Fixed-time intervals are the relevant comparator, with a width cost for anytime validity.

INFERENCE: A learned verifier must preserve conditional null validity; correlated transformed views are not fresh independent tests. These results support a non-RL stopping baseline and preempt novelty claims based solely on optional stopping. They do not calibrate F5's score or prove ownership binding.

## C9-02 — False discovery rate control with e-values

Ruodu Wang, Aaditya Ramdas. arXiv:2009.02824v5, 2021 revision; journal DOI not reverified. [Full text](https://arxiv.org/html/2009.02824v5). Inspected §4 equation 5, §5, §7 Tables 1–2.

SOURCE: Non-RL multiple testing. Each null e-value is nonnegative with expectation at most one. Base e-BH sorts decreasing evidence and rejects the largest qualifying set; arbitrary dependence is allowed. Sequential products require conditional expectation control, not merely marginal calibration. The ordered-bandit illustration stops each arm when it yields a rejection or exhausts its budget; no reward-learning policy is fitted. Default simulation: 500 arms, 50 pulls maximum, 500 trials, nominal FDR .05. e-BH gives 73.2 true discoveries and 11.42% unused budget versus BY's 70.4 and 10.06%; observed FDP is 1.58% versus .31%. BH is more powerful here but lacks the required guarantee under induced dependence.

INFERENCE: FDR across claimed owners is not per-image false-positive probability or familywise error. Calling reader margins e-values cannot manufacture validity. This is a strong statistical comparator/constraint for adaptive verification, not evidence that RL improves C or J.

## C9-03 — Conformal Risk Control

Anastasios N. Angelopoulos, Stephen Bates, Adam Fisch, Lihua Lei, Tal Schuster. arXiv:2208.02814v4, 2025 revision; ICLR2024 lead, venue/DOI not independently reverified here. [Full text](https://arxiv.org/html/2208.02814v4). Inspected §§1.1,2.1–2.4,3.1–3.2.

SOURCE: Non-RL calibration of a fixed predictor. Choose the least conservative parameter satisfying n/(n+1) times empirical risk plus B/(n+1) ≤ alpha. Theorem 1 assumes exchangeable loss functions, monotonicity, right-continuity, bounded loss and a feasible conservative endpoint. It controls expected future loss; it is not a high-probability guarantee for each fitted calibration set. State/action/reward are inapplicable; calibration observations select a threshold once. Over 1,000 splits, tumor segmentation FNR is .0987±.0114 at alpha=.1 (1,000 calibration, 781 evaluation); COCO multilabel FNR is .0996±.0052 (4,000/1,000). These are demonstrations of calibration, not RL comparisons.

INFERENCE: A verification policy needs a separate calibration set and a defined null/risk. Unknown encoder shift and adaptive attackers need additional assumptions. Generic conformal wrapping is occupied prior art; it cannot turn seven dependent F5 views into authenticated ownership evidence.

## C9-04 — Active Testing: Sample-Efficient Model Evaluation

Jannik Kossen, Sebastian Farquhar, Yarin Gal, Tom Rainforth. ICML2021, PMLR139; DOI not supplied. [Paper](https://proceedings.mlr.press/v139/kossen21a/kossen21a.pdf). Inspected §§2.2–3.4, Algorithm 1, §§5.1–5.2 Figures 3–4.

SOURCE: Non-RL adaptive importance sampling for evaluation, not model training. State contains the unlabeled pool and acquired labels; action samples a point with logged probability; acquisition approximates expected loss through a surrogate. LURE weights correct adaptive selection bias. An oracle samples proportional to true loss; practical surrogates trade acquisition compute against label savings. In a synthetic regression example, five labels yield standard deviation comparable with 40 uniform labels. In Fashion-MNIST, entropy sampling from the original ResNet can perform worse than uniform, while a retrained random forest surrogate performs best among the illustrated choices. Large comparisons report hundreds of repeated acquisitions, not a universal speedup.

INFERENCE: Adaptive allocation of regeneration measurements already has a strong non-RL route. Every sampled source's selection probability matters for unbiased population estimates. This cannot retrospectively randomize fixed historical arms or justify selection on held-out sources. Label savings do not establish equal-total-compute savings after surrogate fitting.

## C9-05 — Better Aggregation in Test-Time Augmentation

Divya Shanmugam, Davis Blalock, Guha Balakrishnan, John Guttag. ICCV2021; arXiv:2011.11156v2 (11 October 2021). DOI10.1109/ICCV48922.2021.00125 metadata lead, not independently resolved. [Full text](https://arxiv.org/html/2011.11156v2). Inspected §§3.1,4,5 Tables 1–2.

SOURCE: Non-RL supervised, nonnegative gradient-learned aggregation weights per augmentation or augmentation/class. No sequential transition or reward policy; all chosen transformed predictions are available. Thirty standard or 128 expanded transforms are evaluated. Released test data are repartitioned 40/10/50% for fitting, selection and evaluation; GPS receives the same labeled amount. Standard-policy Flowers/MobileNet accuracy is 92.62±.10 versus mean90.47±.20 and GPS88.28±.17. Gains are not universal: ImageNet/MobileNet learned72.43 versus mean72.69; expanded CIFAR100 learned73.18 versus GPS75.07. Results use five random subsamples. Training is 30 epochs and view evaluations have costs.

INFERENCE: Learned F5 view weights are not a new RL contribution. This is a mandatory gradient/simple-greedy comparator for verification selection. Changing aggregation changes the reader and null calibration. Accuracy gains for classification say nothing about T4/T5 instance binding or regeneration survival.

## C9-06 — Test-time augmentation improves efficiency in conformal prediction

Divya Shanmugam, Helen Lu, Swami Sankaranarayanan, John Guttag. CVPR2025; arXiv:2505.22764v1, 2025. DOI unavailable here. [Full text](https://arxiv.org/html/2505.22764v1). Inspected §§3–5, Table 1, exchangeability paragraph.

SOURCE: Non-RL TTA weight learning followed by APS/RAPS calibration. Twenty percent of validation data fit weights; the remaining 80% calibrate, preserving exchangeability for a fixed transform. Each added view costs a classifier forward pass. Actions/rewards/horizon of an RL policy are absent. Across ten random splits, ImageNet at alpha=.01 has mean set size37.751±2.334 for RAPS,35.600±2.200 for expanded TTA averaging,31.248±2.177 for learned expanded TTA. Simple TTA averaging31.681 beats learned32.702, illustrating that added fitting is not always best. Experiments also cover iNaturalist and CUB, with paired tests and multiplicity correction.

INFERENCE: Prediction-set efficiency is not ownership detection power. Separate policy-training and calibration data are already an established requirement, not an RL innovation. Validity under exchangeability does not guarantee robustness to an independently trained regeneration family or adaptive forgery. This preempts a generic “learn views then conformally calibrate” claim.

## C9-07 — Reinforcement Learning for Visual Object Detection

Stefan Mathe, Aleksis Pirinen, Cristian Sminchisescu. CVPR2016, accepted paper; DOI not verified. [Full text](https://www.cv-foundation.org/openaccess/content_cvpr_2016/papers/Mathe_Reinforcement_Learning_for_CVPR_2016_paper.pdf). Inspected §3, equations15–17, §4 Table1.

SOURCE: R-full. State tracks inspected/evidence regions and fixation history. Actions fixate an image location or stop; new regions reveal features. Terminal reward uses confidence and ground-truth overlap (or penalizes confidence on negatives), with per-region observation cost. Score-function gradients and BFGS fit the policy. PascalVOC2012 evaluation averages107 inspected regions and38.7seconds, versus2691seconds sliding windows:69.6-fold speedup, including proposal/policy overhead. But mean AP falls from31.2(sliding) or30.3(region proposals) to27.0. Average fixation count is3.1. Training overhead is not included in deployment speedup.

INFERENCE: This is a genuine delayed information-acquisition analogy for active verification. It establishes an accuracy/cost tradeoff, not free superiority. F5 has only seven predetermined views, so exhaustive or greedy evaluation may be cheaper than policy learning. Neither fixed false-positive control nor content binding is provided by the detector-search reward.

## C9-08 — Active Vision for Early Recognition of Human Actions

Boyu Wang, Lihan Huang, Minh Hoai. CVPR2020, accepted author PDF; DOI10.1109/CVPR42600.2020.00116 metadata lead, not independently resolved. [Full text](https://minhhoai.net/papers/viewSel_cvpr20.pdf). Inspected §§3–4.3,5.1,5.4 Table3.

SOURCE: R-full camera selection under a one-view-per-step constraint. Belief state combines recurrent hidden states and time since each observation; action selects a camera, transition reveals its frame. Reward is true-class log probability across time; A2C uses discount .9. Missing-frame RNNs and learned fusion accompany the policy. NTU mean early accuracy58.01 versus cyclic56.31, random54.81 and best fixed54.94; at40% observation54.55 versus cyclic51.69. All-views61.77 uses extra observations. NTU uses skeleton features and cross-subject splitting; other datasets use different features. The table does not price the policy's full training search.

INFERENCE: Useful evidence for history-dependent selection when new observations matter. Static watermark views lack moving-scene dynamics, and fusion/representation improvements must be isolated from RL. A matched-budget greedy uncertainty controller and fixed order remain necessary. Classification accuracy does not establish calibrated ownership decisions.

## Search log

Eighteen actual distinct queries. All index searches below used general web search restricted to the named scholarly domain; these are indirect indexed-content searches, not native-index API sessions. More than four indexes were attempted; accessible primary content came from arXiv, PMLR and CVF/author mirrors, while OpenReview, IEEE and DBLP supplied discovery metadata. ACM produced no eligible sequential-image lead. Open calls and mirror retries are not counted as queries.

| ID | Exact query | Returned lead / disposition |
|---|---|---|
| Q01 | site:arxiv.org "Time-uniform, nonparametric, nonasymptotic confidence sequences" | C9-01 |
| Q02 | site:proceedings.mlr.press "Active Testing" "Sample-Efficient" | C9-04 |
| Q03 | site:proceedings.mlr.press "Better Aggregation in Test-Time Augmentation" | No exact PMLR venue; corrected to CVF/arXiv |
| Q04 | site:openaccess.thecvf.com "test-time augmentation" "policy" | C9-05/06 and related policy selection |
| Q05 | site:openreview.net "Conformal Risk Control" | C9-03; OpenReview PDF blocked, arXiv recovered |
| Q06 | site:arxiv.org "Hypothesis Testing with E-values" | E-value book lead, not counted; C9-02 more specific |
| Q07 | site:ieeexplore.ieee.org watermark sequential detection probability ratio test | Physical replay-attack watermarking, not image ownership; excluded |
| Q08 | site:openaccess.thecvf.com active visual recognition reinforcement learning sequential verification | C9-07/08 and FLAR; only two counted |
| Q09 | site:arxiv.org "False discovery rate control with e-values" | C9-02 |
| Q10 | site:dblp.org "Better Aggregation in Test-Time Augmentation" | C9-05 metadata |
| Q11 | site:openreview.net "sequential" "watermark" "false" | Text watermarking leads, no additional image card |
| Q12 | site:dl.acm.org watermark sequential verification reinforcement learning | No eligible full-text image sequential-verification lead |
| Q13 | "Conformal Risk Control" arxiv | C9-03; 2026 non-monotone extension not inspected/countable |
| Q14 | "Better Aggregation in Test-Time Augmentation" arxiv | C9-05 v2 recovered |
| Q15 | "Reinforcement Learning for Visual Object Detection" arxiv | C9-07 CVF source |
| Q16 | "Active Vision for Early Recognition of Human Actions" arxiv | C9-08 CVF metadata |
| Q17 | "Reinforcement Learning for Visual Object Detection" pdf -site:openaccess.thecvf.com | cv-foundation mirror recovered |
| Q18 | "Active Vision for Early Recognition" pdf -site:openaccess.thecvf.com | Author PDF recovered |

Access limits: openaccess.thecvf.com PDF fetches for C9-05/07/08 returned403; arXiv/official CVF mirror/author PDF respectively supplied inspected full texts. OpenReview C9-03 returned a challenge. IEEE physical watermarking and FLAR were not inspected and do not count. No exact RL image-ownership verifier under independently trained diffusion regeneration was established by this cluster; that is a bounded search result, not proof of absence.
