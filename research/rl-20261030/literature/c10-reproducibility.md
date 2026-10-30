# C10: reproducibility and simpler baselines

Access date: 2026-10-30. Five full-text inspections here plus five distinct cards in `c10-security-supplement.md` constitute this cluster. SOURCE statements summarize the cited version; implications are JUDGMENT. No experiments reproduced. These are control/image/text-task analogies, not watermark effect estimates.

## C10-01 — Deep Reinforcement Learning That Matters

Peter Henderson, Riashat Islam, Philip Bachman, Joelle Pineau, Doina Precup, David Meger. AAAI 2018; [publisher metadata](https://ojs.aaai.org/index.php/AAAI/article/view/11694), DOI 10.1609/aaai.v32i1.11694. Inspected [arXiv 1709.06560v3, 2019-01-30](https://arxiv.org/html/1709.06560v3), Technical Background, Experimental Analysis, Tables 1–3, Random Seeds and Trials.

Setting: continuous-control evaluation, neither watermark insertion regime. Class: methodological comparison of R-full PPO/TRPO/DDPG/ACKTR, not a new policy. States are simulator observations, actions controls, rewards task returns. Five fixed seeds usually, 2M training samples. Changing only PPO policy architecture on Hopper changes final return from 2790±62 (64,64) to 61±33 (400,300), mean±SE. On HalfCheetah, the same architecture contrast changes 2201±323 to −1180±444. A ten-run split into two groups of five illustrates seed sensitivity. This pre-empts treating one favorable seed or unmatched implementation as an algorithmic advance. It does not establish a universally sufficient seed count; its significance example is descriptive, not our recommended sequential test. JUDGMENT: watermark policy evaluation must separate training seeds, regeneration seeds and source units, and tune the comparator fairly.

## C10-02 — Deep Reinforcement Learning at the Edge of the Statistical Precipice

Rishabh Agarwal, Max Schwarzer, Pablo Samuel Castro, Aaron Courville, Marc G. Bellemare. NeurIPS 2021. Inspected [arXiv 2108.13264v3, 2021-10-13](https://arxiv.org/html/2108.13264v3), §§2–5, Figures 2–6 and Table 1.

Setting: evaluation of R-full agents on Atari/Procgen/control, not watermarking; no new state/action/reward design. Method: stratified bootstrap intervals, performance profiles, interquartile mean (IQM), and probability of improvement. Atari 100k study uses 100 independent training runs per algorithm across 26 games, then subsamples. SPR's median bias between five and 100 runs is .03, about 36% of its .08 improvement over DrQ(epsilon). Protocols selecting maximum scores can reverse comparisons; IQM reduces interval width relative to median. Three-run bootstrap intervals can under-cover. This pre-empts reporting only a best seed or a single aggregate. Limits: task-specific simulations do not make ten seeds universally adequate; uncertainty over fixed tasks differs from unseen-family uncertainty. JUDGMENT: use paired source-level effects with intervals, retain failures, and expose all tuning/selection; do not replace C/J or security gates by a favorable IQM.

## C10-03 — Simple random search provides a competitive approach to reinforcement learning

Horia Mania, Aurelia Guy, Benjamin Recht. 2018 preprint (later NeurIPS venue not independently inspected here). Inspected [arXiv 1803.07055v1, 2018-03-19](https://arxiv.org/pdf/1803.07055), §§2–4.4, Algorithms 1–2, Tables 1–4, hundred-seed evaluation.

Setting: continuous-control linear policies. Under this brief's taxonomy, ARS is a non-RL random-search comparator, although solving an RL control problem. Policy state is normalized simulator state; action is a linear control; objective is rollout return. Antithetic parameter perturbations, reward-SD normalization and top-direction selection update weights. Hopper threshold 3120 takes 1973 ARS V2-t episodes versus 10000 reported TRPO; Walker2d threshold 4390 takes 24000 versus 14250, preserving the negative comparison. Hyperparameters were selected over the same three initial evaluation seeds; the subsequent 100-seed study succeeds only 20% on Walker2d. These results pre-empt calling a simple policy's success proof of actor-critic necessity. Limits: cross-paper comparators, selected hyperparameters and task-specific thresholds; no equal-total-cost watermark evidence. JUDGMENT: low-dimensional random or evolutionary policy search belongs beside RL, not inside its claimed gain.

## C10-04 — Evolution Strategies as a Scalable Alternative to Reinforcement Learning

Tim Salimans, Jonathan Ho, Xi Chen, Szymon Sidor, Ilya Sutskever. 2017 preprint. Inspected [arXiv 1703.03864v2, 2017-09-07](https://arxiv.org/pdf/1703.03864v2), §§2–4, Algorithms 1–2, Table 1 and Figure 1. HTML conversion lacked the paper, so PDF was inspected.

Class: non-RL NES comparator under the brief; sequential task policies are optimized through parameter perturbations and episode return. Observations/actions are simulator states/controls or Atari pixels/buttons. Gaussian score-function estimates, antithetic samples, rank shaping and shared random seeds enable parallelism. To reach TRPO's final performance, ES/TRPO timestep ratios are .58 HalfCheetah, 6.94 Hopper and 7.88 Walker2d. Atari ES beats published A3C in 23/51 games, loses 28, with 1B versus 320M frames and roughly comparable neural computation claimed. Humanoid's ten minutes uses 1440 cores; 18 cores take 657 minutes. This pre-empts interpreting wall-clock speedups as cheap learning. Limits: different hardware, approximate compute equivalence and limited seeds; theoretical horizon-variance intuition assumes weak return/action correlation. JUDGMENT: benchmark total device-time and information access, and keep ES distinct from RL attribution.

## C10-05 — Random Search and Reproducibility for Neural Architecture Search

Liam Li, Ameet Talwalkar. UAI proceedings, PMLR 115:367–377, publication 2020 (35th UAI). Inspected [publisher PDF](https://proceedings.mlr.press/v115/li20c/li20c.pdf), §§2–4.1.3, Tables 1–3; [metadata](https://proceedings.mlr.press/v115/li20c.html).

Setting: image classification and language-model architecture search, neither watermark insertion regime. Class: non-RL; random DAG choices plus shared-weight gradient training and separate architecture evaluation. No MDP state/reward; selection objective is validation performance. CIFAR-10 random weight-sharing yields 2.85±.08% test error in 9.7 P100 GPU-days versus reproduced second-order DARTS 2.78±.12% in ten days; random ASHA 3.03±.13% in nine days. Ten final-training seeds; six independent random-search runs average 2.92%. Thus random is competitive, not uniformly better. This pre-empts comparisons against one randomly chosen candidate or uncharged selection. Limits: tuned meta-hyperparameters, architecture-size differences, unstable early rankings, and stage-(1) text explicitly says test-set scoring—do not copy that practice. JUDGMENT: budget search, refinement, selection and final fitting equally; a strong null comparison is scientifically informative but needs its own domain contribution.

## Exact query ledger

All queries are web search, including site-restricted discovery; these are not authenticated/native index sessions. Queries Q01–Q12 were executed before this context continuation; their strings and outcomes were retained in the session summary. Q13–Q20 were executed during this continuation. Opens and find calls are not queries.

| ID | Exact query | Outcome |
|---|---|---|
| C10Q01 | `site:arxiv.org "Deep Reinforcement Learning that Matters"` | Henderson 1709.06560 |
| C10Q02 | `site:proceedings.neurips.cc "Deep Reinforcement Learning at the Edge of the Statistical Precipice"` | NeurIPS 2021 listing; arXiv independently recovered |
| C10Q03 | `site:openreview.net "Implementation Matters" "Policy Gradients"` | Engstrom lead, assigned supplement |
| C10Q04 | `site:proceedings.mlr.press "Random Search and Reproducibility for Neural Architecture Search"` | Li/Talwalkar full PDF |
| C10Q05 | `site:arxiv.org "Simple random search provides a competitive approach"` | ARS 1803.07055 |
| C10Q06 | `site:arxiv.org "Evolution Strategies as a Scalable Alternative"` | ES 1703.03864 |
| C10Q07 | `site:dl.acm.org "reinforcement learning" "steganography" "SPAR"` | No eligible accessible ACM fulltext |
| C10Q08 | `site:ieeexplore.ieee.org "An Automatic Cost Learning Framework"` | No accessible IEEE fulltext |
| C10Q09 | `"An Automatic Cost Learning Framework" pdf` | SPAR institutional private PDF / request-only page; UNINSPECTED |
| C10Q10 | `site:arxiv.org "TIFS" "reinforcement learning" security` | No specific eligible arXiv result; IEEE TOC DRL-FAS lead |
| C10Q11 | `site:dblp.org "What Matters In On-Policy Reinforcement Learning"` | arXiv2006.05990 lead, supplement |
| C10Q12 | `site:arxiv.org "A Hitchhiker's Guide to Statistical Comparisons" reinforcement` | Colas1904.06979 lead, supplement |
| C10Q13 | `"DRL-FAS" arxiv` | 2009.07529 |
| C10Q14 | `"TIFS" "deep reinforcement learning" "face anti-spoofing"` | DRL-FAS metadata; other uninspected leads |
| C10Q15 | `"reinforcement learning" "TIFS" "adversarial" full text` | TIFS25 VSAA author PDF; supplement |
| C10Q16 | `"statistical precipice" arxiv 2108` | 2108.13264 |
| C10Q17 | `site:aaai.org "Deep Reinforcement Learning that Matters"` | Official AAAI metadata/PDF |
| C10Q18 | `site:proceedings.neurips.cc "Simple random search provides"` | No new useful result in batch |
| C10Q19 | `site:proceedings.neurips.cc "Statistical Precipice"` | No new useful result in batch |
| C10Q20 | `site:proceedings.mlr.press/v115/li20c.html` | PMLR official metadata |

No exhaustion claim is needed if the supplement completes five eligible inspections. SPAR remains a priority uninspected source, not evidence of absence or a counted card. An accepted RL security paper is evidence of precedent and evaluation practice, not the probability that this project's RL variant will be accepted.
