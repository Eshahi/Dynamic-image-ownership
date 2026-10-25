# ISTS: instance selection, two-sided detection and threat scope

Author source note, 2026-10-25; outside completed WP6/E3 review scope. Relevant primary methods, experiments and appendices read. No new baseline, detector change or protocol amendment follows.

## Identity and source digest

Yifan Zhu, Yihan Wang and Xiao-Shan Gao, *Towards Robust Content Watermarking Against Removal and Forgery Attacks*, inspected [arXiv:2604.06662v1](https://arxiv.org/html/2604.06662v1), 2026-04-08. [Version metadata](https://arxiv.org/abs/2604.06662) and indexed [official CVF entry](https://openaccess.thecvf.com/content/CVPR2026F/html/Zhu_Towards_Robust_Content_Watermarking_Against_Removal_and_Forgery_Attacks_CVPRF_2026_paper.html) identify **CVPR 2026 Findings**, pp.8059–8069; this is not labelled the main conference track. Direct CVF access returned 403; publisher-text equivalence is not asserted.

Source digest (under 200 words): ISTS generates a clean image, uses CLIP and a learned 1,024-cluster selector to choose injection time/location, then generates its watermark-bearing counterpart. Detection selects parameters from the suspect, performs DDIM inversion and minimizes distance to positive/negative pattern orientations. SD2.1-base experiments use 100 attacked pairs and 1,000 ordinary pairs. At 1% FPR, Table 1's worst tested removal leaves TPR .18; Table 2's worst forgery accepts .37. These are separate tasks, not a combined security score. Appendix A.2 uses same-diffusion-model imprinting and an SD1.4 VAE for other attacks. Section 5.3 includes DiffPure, without recovered checkpoint/noise details establishing independent-AE regeneration. Section 3.2 assumes unknown model/algorithm, while A.2 permits the same model; A.4 proposes secret label permutation. Section 4.2 invokes null symmetry to motivate two-sided detection. The authors acknowledge unsatisfactory worst-case attack robustness.

## Local inference: symmetry does not preserve a searched null

Consider a symmetric scalar null `Z~N(0,1)`, a fixed positive pattern mu and threshold `0<tau<mu`. The one-orientation score is `d_plus=|Z-mu|`; the two-orientation score is `d_min=min(|Z-mu|,|Z+mu|)`. Both individual orientation scores have the same null distribution by symmetry. Their minimum does not.

The acceptance intervals around mu and -mu are disjoint. Therefore

`P(d_min<tau) = 2*[Phi(mu+tau)-Phi(mu-tau)] = 2*P(d_plus<tau)`.

More generally the two-sided probability is the sum of the two marginal probabilities minus their intersection. Symmetry equates the marginals; it does not make their union one event. Consequently a fixed numerical threshold is not automatically calibrated after adding the second orientation. This is a general counterexample to that inference, not a calculation of ISTS's actual FPR. Recalibrating the complete detector can control its operating point, and the paper reports thresholded/ROC comparisons; this note does not invalidate those empirical measurements. Data-dependent parameter selection additionally requires the full selector-plus-inversion-plus-orientation pipeline to define the null experiment. See the [searched-verifier note](../analysis/searched-detector-null.md).

## Local inference: hidden labels are not a demonstrated security parameter

A permutation of N labels has N! possibilities, whereas the permuted value of one known input label has at most N possibilities. Recovering every entry of the permutation and guessing the selected parameters for one image are different computational problems. In particular, with N=1,024, the latter candidate space is at most 1,024 labels before deterministic parameter mapping, rather than an exponential 2^1,024 per-image search justified only by the number of labels. This counting observation does not supply a working attack: candidate testing may require unavailable patterns, model access, an oracle or expensive inversion. It does show why a permutation-space size alone cannot certify resistance to the relevant per-instance objective.

Public semantic features are also not secret authentication. Selecting a carrier from content can help obstruct a mismatched-reference attack, but it does not prove resistance to a knowledgeable adversary seeking a compatible selector output. A secret selection rule, a fixed public algorithm and a secret key are different information models. The source's unknown-algorithm assumption and its same-model attack setup must be recorded separately. A more informed attacker can choose to emulate a less informed one, but a single specified gradient objective need not become empirically more successful merely because it uses the target checkpoint. Thus the reported same-model experiment does not establish a universal ordering of all grey-box attack outcomes.

## Relation to this study

The useful overlap is semantic parameter selection and acceptance under more than one candidate pattern. The inspected experiment does not identify independent encoder training as a cause, establish a fixed F5 mark's T3 survival, or resolve near-duplicate binding. Its .18 removal retention and .37 forgery acceptance preserve substantial negative outcomes despite favorable relative comparisons. Our existing C0/wrong-owner controls and proposed detector-free attacks remain distinct from adaptive authentication security. No new semantic selector, sign-search branch, owner key or threshold is introduced here.

## Inspection receipt

- Exact-title and instance-specific/two-sided primary-domain searches followed the broader AEON/HSQR/ROAR query batch in [search-log.md](search-log.md).
- Direct arXiv metadata and v1 HTML read: §§3.2–4.2, Algorithms 1–3; §§5.1–5.3, Tables 1–4 and limitation paragraph; Appendices A.1–A.4. Stable web-line ranges 93–207, 208–259, 339–421.
- Algorithm 3 supplies actual acceptance; §4.2 supplies the symmetry argument; A.4 supplies the permutation argument. All mathematical counterexamples above are local author analysis, not executed attacks or empirical source claims.
- No download, model access, detector invocation, experiment or scientific interpreter was used.
