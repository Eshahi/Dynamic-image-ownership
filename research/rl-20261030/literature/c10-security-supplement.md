# C10 supplement: reproducibility, attribution and security precedents

Access date: **2026-10-30**. Five primary publications were inspected beyond their abstracts, specifically at the method and evaluation locations below. The fifth is the complete three-page AAMAS proceedings paper, explicitly an extended abstract; it is not the inaccessible TIFS journal extension. No project outputs, F6 outcomes, experiments, code downloads or installations were accessed. Numerical effects below belong to their original tasks, not watermarking.

## C10-S1 — DRL-FAS: A Novel Framework Based on Deep Reinforcement Learning for Face Anti-Spoofing

**Authors/year/venue:** Rizhao Cai, Haoliang Li, Shiqi Wang, Changsheng Chen, Alex C. Kot; TIFS 16 (2021), 937–951; DOI 10.1109/TIFS.2020.3026553. **Inspected version:** [arXiv:2009.07529v2, 18 September 2020](https://arxiv.org/html/2009.07529); publication metadata corroborated by the [author's publication page](https://rizhaocai.github.io/zh/publications/). Access: 2026-10-30. **Locations:** III-C/D, equations 2–5; IV-C3, Table IV; IV-C4, Tables V–VI.

**Setting/mechanism:** Face presentation-attack classification. REINFORCE selects sequential patches from a frozen pretrained backbone feature map. State is the GRU hidden representation; action is a patch location; terminal reward is log probability of the correct binary label, with zero intermediate reward. Global and recurrent local features feed classification.

**Comparison/effect:** With patch size 8 and eight observations, Table IV reports ROSE-YOUTU EER 1.79% for DRL, 2.14% for random selection and 3.29% for MAX-SCORES. All three obtain 0% on IDIAP. Thus RL's contribution is benchmark-dependent, not merely the benefit of adding local features.

**Limits/implication:** This establishes actual TIFS use of an RL component with relevant ablations; it does not establish equal total tuning cost or watermark robustness. Our inference: a sequential watermark controller needs random, greedy and fixed-action ablations with identical observation access and inference budget. Freeze the SD1.5 reader and test transfer separately.

## C10-S2 — A Hitchhiker's Guide to Statistical Comparisons of Reinforcement Learning Algorithms

**Authors/year/venue:** Cédric Colas, Olivier Sigaud, Pierre-Yves Oudeyer; arXiv preprint first submitted 2019. **Inspected version:** [arXiv:1904.06979v2, 29 August 2022](https://arxiv.org/html/1904.06979). Access: 2026-10-30. **Locations:** sections 3–5, especially 4.1–4.4 and supplementary Table 15. No peer-reviewed venue is asserted here.

**Setting/class:** Statistical methodology, not a new state/action/reward proposal. It compares six tests using synthetic normal, skewed and bimodal performance distributions plus 192 independent SAC and 192 TD3 runs on HalfCheetah-v2, each trained for two million steps. Null distributions are aligned and tests repeatedly resampled to estimate false-positive rates and power.

**Comparison/effect:** The empirical SAC–TD3 mean standardized effect is 0.93; roughly 10–15 samples are needed for 80% power with mean-comparison tests. With five samples, Welch's test needs an effect three to four times larger for that power. Under simulated skew/variance violations, even relatively robust tests can exceed nominal 5% false-positive rates.

**Limits/implication:** These are distribution-specific results, not a universal seed prescription; the studied bootstrap hypothesis test is not every bootstrap estimator. Our inference: preregister the estimand and sampling units, retain failed seeds, estimate power from development variability, and avoid treating repeated attack images as independent policy-training seeds. Statistical false positives here differ from detector false acceptances.

## C10-S3 — What Matters In On-Policy Reinforcement Learning? A Large-Scale Empirical Study

**Authors:** Marcin Andrychowicz, Anton Raichuk, Piotr Stańczyk, Manu Orsini, Sertan Girgin, Raphael Marinier, Léonard Hussenot, Matthieu Geist, Olivier Pietquin, Marcin Michalski, Sylvain Gelly, Olivier Bachem. **Year/version/venue:** [arXiv:2006.05990v1, 10 June 2020](https://arxiv.org/html/2006.05990), inspected preprint; later ICLR venue was not independently verified through an accessible primary venue page in this task. Access: 2026-10-30. **Locations:** section 2; sections 3.1–3.2, Figures 1–2 and the accompanying references to Figures 17/24.

**Setting/class:** On-policy continuous-control methodology; no new application MDP. A unified implementation exposes over 50 choices across five Gym/MuJoCo environments. Related choices and learning rate are sampled jointly. Each configuration uses three independent seeds and a learning-curve score, evaluated with 100 episodes per checkpoint.

**Comparison/effect:** Section 3.2 reports that smaller final-policy-layer initial weights increase Humanoid performance by 66%; tanh action transformation improves HalfCheetah by 30% relative to clipping. These are implementation comparisons within this design, not universal PPO advantages.

**Limits/implication:** Three-seed configuration medians and conditional hyperparameter analyses do not establish robust transfer. Our inference: match preprocessing, initialization and capacity; budget all hyperparameter trials; select configurations on development data before an excluded regenerator. Reward rescaling and quality constraints must be identical across policy and non-RL optimization comparisons.

## C10-S4 — Implementation Matters in Deep Policy Gradients: A Case Study on PPO and TRPO

**Authors/year/venue:** Logan Engstrom, Andrew Ilyas, Shibani Santurkar, Dimitris Tsipras, Firdaus Janoos, Larry Rudolph, Aleksander Mądry; ICLR 2020 version, confirmed by the [arXiv metadata](https://arxiv.org/abs/2005.12729). **Inspected version:** [arXiv:2005.12729v1, 25 May 2020](https://arxiv.org/html/2005.12729). Access: 2026-10-30. **Locations:** sections 3–5, Tables 1–3, Appendix A.1. The requested arXiv identifier is correct.

**Setting/class:** Policy-gradient attribution study on MuJoCo, not a new application state/action/reward specification. It crosses PPO/TRPO update rules with implementation optimizations, compares PPO-Minimal and TRPO+, and tests PPO without clipping. Appendix A.1 describes grid searches; Table 2 estimates use at least 80 agents and bootstrap confidence intervals.

**Comparison/effect:** On Humanoid-v2, Table 2 reports PPO 806 [785,827], PPO-Minimal 674 [656,695], TRPO 586 [576,596], and TRPO+ 1030 [979,1083]. The same task's maximal implementation effect is 444 reward units versus 224 for switching the update rule.

**Limits/implication:** Grid spaces differ between variants; these numbers are not an equal-cost watermark comparison. Our inference: use factorial ablations separating representation, action space, reward, optimizer and sequential feedback. Publish complete settings and matched tuning budgets before attributing a gain to RL rather than extra engineering.

## C10-S5 — Grey-box Adversarial Attack on Communication in Multi-agent Reinforcement Learning: Extended Abstract

**Authors/year/venue:** Xiao Ma, Wu-Jun Li; AAMAS 2023, pp. 2448–2450, extended abstract. **Inspected version:** [official complete proceedings PDF](https://www.ifaamas.org/Proceedings/aamas2023/pdfs/p2448.pdf). Access: 2026-10-30. **Locations:** sections 2.1–2.2, equations 3–4, section 3 and Table 1; page 2449's table was also requested as a screenshot.

**Setting/class:** Security of a communicative RL system, **not an RL-trained attack algorithm**. VSA uses FGSM on a controlled agent's model, treating it as a surrogate victim and using previous messages to avoid synchronous-message deadlock. It aggregates message perturbations and broadcasts the result. There is no newly learned attack state/action/reward policy; the attack objective reduces the surrogate's preferred-action probability.

**Comparison/effect:** Two CommNet agents pursue stationary prey on a 3×3 grid; one malicious agent, perturbation limit 0.3. Table 1 reports mean win rates over five random runs: clean 100.00±0.00%, model-based message attack 97.97±1.57%, VSA 72.82±3.11%.

**Limits/implication:** This is a tiny environment and asymmetric model access; the result cannot rank RL against gradients at equal information. Our inference: a watermark study must declare each optimizer's observations, gradients and queries. A strong non-RL adversary or optimizer can expose weaknesses that policy reward alone conceals; T4/T5 binding and false acceptance need independent evaluation.

## Related TIFS 2025 version: not counted as fully inspected

[Grey-box Adversarial Attack on Communication in Communicative Multi-agent Reinforcement Learning](https://cs.nju.edu.cn/lwj/paper/TIFS25_VSAA.pdf), Xiao Ma and Wu-Jun Li, DOI **10.1109/TIFS.2025.3560203**, is identified as a TIFS author-accepted version on its indexed first page and the [author's publication list](https://cs.nju.edu.cn/lwj/). Direct PDF opens repeatedly timed out. Search-index extraction exposed page 2's description of the extension and page 12's Tables IV/V and Figure 8, but **this is not a full-text-inspection claim**. The 2023 precursor above is the fifth qualifying card. Do not substitute the 2025 title/year for its numbers or silently count the two versions as independent evidence. The inspected precursor's attack is gradient-based; the journal version's full algorithm remains unverified here.

## Project-facing synthesis (research inference)

The evidence supports considering RL as a testable controller or training mechanism, not as a publication credential. A proposed SD1.5 fixed-reader method should beat its strongest non-RL comparator under equal total training, tuning and inference resources. Separate sequential feedback from one-shot selection, and policy optimization from representation or reward changes. Use frozen quality gates (PSNR > 35, SSIM > .9, LPIPS < .1), excluded independently trained regenerators, and separate T4/T5 binding and detector-false-positive tests. None of these papers supplies a predicted watermark effect size, a cryptographic ownership guarantee, or evidence about the frozen F6 outcome.

## Exact discovery-query log

All queries below used **general web search**, including `site:`-restricted discovery. None was a native arXiv, IEEE Xplore, OpenReview or other bibliographic-index search. Direct URL opens and within-document `find` operations are separately described afterward. Results unrelated to the primary sources were not used as technical evidence.

1. `"Grey-box Adversarial Attack on Communication" PDF`
2. `"DRL-FAS" "3026553"`
3. `"What Matters In On-Policy Reinforcement Learning" ICLR 2021`
4. `site:cs.nju.edu.cn/lwj/paper/TIFS25_VSAA.pdf "IV." "TABLE"`
5. `site:cs.nju.edu.cn/lwj/paper/TIFS25_VSAA.pdf "gradient" "MADDPG"`
6. `site:openreview.net "What Matters In On-Policy Reinforcement Learning?"`
7. `site:arxiv.org "DRL-FAS" "TIFS"`
8. `site:cs.nju.edu.cn/lwj/paper/TIFS25_VSAA.pdf "III." "gradient"`
9. `site:cs.nju.edu.cn/lwj/paper/TIFS25_VSAA.pdf "Algorithm 1" "loss"`
10. `site:cs.nju.edu.cn/lwj/paper/TIFS25_VSAA.pdf "Experiments" "baseline"`
11. `"TIFS25_VSAA" "gradient"`
12. `"victim-simulation" "PGD"`
13. `"Grey-box Adversarial Attack" filetype:pdf -site:cs.nju.edu.cn`
14. `"reinforcement learning" "TIFS" watermarking`
15. `"Grey-box Adversarial Attack on Communication in Communicative" "gradient"`
16. `"Grey-box Adversarial Attack on Communication in Communicative" "VSAA" "IV"`
17. `"Grey-box Adversarial Attack on Communication in Communicative" "FGSM"`
18. `"DRL-FAS" "IEEE" "2021" "Cai"`
19. `"What Matters In On-Policy Reinforcement Learning" site:research.google`
20. `"Hitchhiker" "1904.06979" site:arxiv.org`

**Direct-access audit:** Opened arXiv HTML for 2009.07529, 1904.06979, 2006.05990 and 2005.12729, plus relevant arXiv metadata pages. Inspected method/evaluation passages by line location and searches including `TABLE IV`, `REINFORCE`, `Figure 1`, `Table 1`, `Table 2`, `192`, `4.1 Methods`, and `A.1 Experimental Setup`. Opened the AAMAS PDF and read equations and experiments. TIFS25_VSAA.pdf attempts through HTTPS, HTTP, `?download=1`, and `#page=3` failed. The DRL-FAS DOI resolver was inaccessible, with journal metadata independently corroborated by primary author/conference sources. OpenReview forum/PDF `nIAxjsniDzg` returned a browser challenge, so it was not used to verify venue or technical content.
