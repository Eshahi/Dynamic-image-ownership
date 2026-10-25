# Denoising/unsigning: hypothetical evidence and channel assumptions

Author source-boundary note, 2026-10-25. Primary methods, theoretical arguments and the experimental-style section were inspected. **The source supplies no measured experimental results.** This note is outside completed WP6/E3 reviews and changes no protocol, baseline or article text.

## Identity and bounded source digest

Fai Gu, Qiyu Tang, Te Wen, Emily Davis and Finn Carter, *When Denoising Becomes Unsigning: Theoretical and Empirical Analysis of Watermark Fragility Under Diffusion-Based Image Editing*. arXiv:2603.04696v1, 2026-03-05, preprint. [Version record](https://arxiv.org/abs/2603.04696v1), [inspected full text](https://arxiv.org/html/2603.04696v1). DOI: 10.48550/arXiv.2603.04696. No acceptance is established.

Source digest (under 200 words): Section 3 models encoder linearization followed by Gaussian corruption and denoising; Eq.10 divides perturbation energy by expected total noise energy. Algorithm 1 proposes common-seed clean/marked edits, comparing their outputs for watermark-induced fidelity. Section 4.1 explicitly identifies numerical results as hypothetical; Sections 5, 7.5 and Appendices B/E preserve that qualification. Named editors include TF-ICON, SHINE and DragFlow, with HiDDeN, StegaStamp, TrustMark and VINE watermark examples. Section 6 uses a Markov channel, a Gaussian KL mixture bound, an information-decay argument, a multi-step contraction claim and a full-message Fano bound. These are theoretical claims and a proposed evaluation structure, not executed trials or independently trained encoder evidence. No table value is imported as a result.

## Local mathematical and evidentiary interpretation

### Hypothetical tables cannot validate the mechanism

The explicit qualification is decisive regardless of empirical-sounding prose elsewhere. These tables cannot establish VINE fragility, a UNet-versus-DiT difference, a numerical quality tradeoff, a reproduction target or a power parameter. The paper can be recorded as a conceptual proposal. It is excluded from the session's minimum count of inspected **empirical** evidence sources. This is an evidence classification, not an accusation about author intent.

### A small per-dimension energy ratio need not mean indistinguishability

Consider two d-dimensional Gaussian distributions, `P0=N(0,sigma² I)` and `P1=N(a delta,sigma² I)`, with `delta=c e1`, fixed nonzero a,c and sigma. Their dimension-normalized shift/noise ratio is `a²c²/(sigma² d)`, which tends to zero as d grows. Yet the KL divergence is `a²c²/(2 sigma²)`, independent of d. The likelihood-ratio statistic uses only coordinate 1; all added coordinates contain irrelevant noise. Equal-prior optimal detection accuracy is `Phi(|ac|/(2 sigma))`, also independent of d.

Thus an energy ratio normalized by total noise dimension is an informative descriptive scale, but its smallness alone does not establish near-chance detection. A direction-aligned detector can ignore orthogonal noise. This example does not assert that a real F5 reader is optimal or that its shift is known. It explains why the [severity contract](../analysis/severity-contract.md) retains directional and total-energy quantities separately, and why the [conditional-information bound](../analysis/conditional-information-bound.md) has no automatic 1/d factor.

### Preserve valid Gaussian bounds; qualify stepwise contraction

For a common Gaussian channel, joint convexity of KL gives a valid upper bound using any specified coupling of the two input distributions. A product coupling of two unrelated natural images includes host variability; small watermark displacement does not make that product-coupled distance small. A common-host coupling can isolate embedding displacement if the construction really supports it. Content-derived messages and image-dependent prompts require their information dependencies to be stated.

The normalized multistep forward channel has cumulative coefficient `A=product_t alpha_t` and noise variance `1-A`, under independent standard increments. The direct Gaussian shift bound scales as `A/[2(1-A)]` times the coupled initial squared distance. It tends to zero as A tends to zero when that distance is finite. This does not establish a universal per-step KL contraction by alpha. For example, let two one-dimensional inputs have equal variance v and mean difference h. Their input KL is `h²/(2v)`; after one step their KL is `alpha*h²/[2(alpha*v+1-alpha)]`. The ratio is `alpha*v/(alpha*v+1-alpha)`, exceeding alpha whenever v>1. A schedule-independent assertion requires more conditions than an arbitrary Gaussian smoothing channel. A bound proportional to A can be recovered on a restricted range `A<=Amax<1` with an explicitly enlarged constant; that is distinct from the claimed per-step reasoning.

Data processing is conditional on a common downstream kernel with no extra source/message information bypassing the noisy state. Image references, masks and attention injection cannot be ignored merely because they are called editing controls. More reverse-solver steps at fixed starting noise are also not more forward-noising steps. Finally, the displayed Fano event is whole-message error, not a direct bit-accuracy bound, carrier-detection guarantee or content-binding result.

These conditional observations support the existing study's bounded prediction test. They neither prove universal watermark removal nor establish novelty of its chain-rule construction.

## Inspection receipt

- Discovery: the three direction-sensitive web queries in [search-log.md](search-log.md), 2026-10-25, restricted to arXiv/OpenReview/CVF.
- Direct metadata and v1 HTML opened; read Sections 3.1–3.6, 4.1–4.5, 5.1–5.7, 6.1–6.4, 7.5 and Appendices A–C/E. Stable locators: Eqs.8–10, 14–21; Section 4.1; Table 5 and its hypothetical caption.
- Browser text inspection only. No paper/data/model/image/code download, experimental run, scientific interpreter or additional source count claimed.
