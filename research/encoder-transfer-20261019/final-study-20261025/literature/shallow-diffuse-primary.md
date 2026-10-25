# Shallow Diffuse — primary-source check

Inspected 2026-10-25 by Codex research subagent. Research only; no execution, downloaded assets, baseline addition or protocol amendment.

## Identity and version

Wenda Li, Huijie Zhang and Qing Qu, **Shallow Diffuse: Robust and Invisible Watermarking through Low-Dim Subspaces in Diffusion Models**, NeurIPS 2025 main conference, volume 38. The [official proceedings entry](https://papers.neurips.cc/paper_files/paper/2025/hash/e23ea56888af722bfa601f7b47057dac-Abstract-Conference.html) verifies authors, venue and DOI 10.52202/085713-5147. The [authors' project page](https://www.huijiezh.com/shallow-diffuse/) labels it Spotlight. [arXiv metadata](https://arxiv.org/abs/2410.21088) records v1 on 2024-10-28 and latest v5 on 2026-02-12; its title uses “Low-Dimensional.” Do not conflate the 2024 initial preprint with the 2025 conference publication. The HTML rendering anomalously prints August 24, 2026 inside the document; use the submission history for version dating.

## Source digest (under 200 words)

[Full text, v5](https://arxiv.org/html/2410.21088v5), §§2.2–5, Appendix C.1 and E, was inspected beyond the abstract. Its posterior-mean-predictor Jacobian motivates shallow-timestep insertion near a low-rank regime. Both generation-time and post-generation DDIM-inversion insertion are supported; detection also requires diffusion inversion, key and timestep. The practical watermark uses masked Fourier rings. Theory assumes exact linearity, bounded Jacobian norm and a uniformly random sphere direction; consistency concerns PMP perturbation, and detectability bounds a one-step DDIM/inversion discrepancy. Neither theorem proves survival under arbitrary foreign regeneration. Practical structured patterns and nonlinear multistep execution require separate validation. SD2.1-base experiments use 5,000 generated images and 500 each from COCO/DiffusionDB. Table 1 reports PSNR 35.49, SSIM .96, LPIPS .02 and regeneration-average TPR .98 at 1% FPR; Table 4's Rinse4x TPR is .90. Appendix E adapts insertion to FLUX; it does not establish transfer of one fixed mark between independently trained autoencoders.

## Code-level access and checkpoint qualification

The [official arguments file](https://github.com/liwd190019/Shallow-Diffuse/blob/main/arguments.py#L9) defaults to `stabilityai/stable-diffusion-2-1-base`, 512 pixels, guidance 7.5 and 50 inference steps. The [official attack implementation](https://github.com/liwd190019/Shallow-Diffuse/blob/main/attackers.py#L16) initializes a separate `stabilityai/stable-diffusion-2-1` fp16 pipeline for diffusion regeneration with `noise_step=60`. Its `image_distortion_diffpure` uses the supplied `pipe`, encodes with `sample=False` and purifies at 0.3 of the inference-step count. These are mutable-main source observations, not a pinned reproduction or proof that every reported table used precisely this code revision. Different checkpoint names do not establish independently trained AE weights. No AE identity/hash or training-provenance isolation was verified here; the study cannot be credited as an independent-AE transfer experiment on this evidence.

## Local comparison and novelty consequence

This is substantive prior art for diffusion-Jacobian/subspace watermark reasoning. A broad claim that our study first explains watermark behavior through diffusion derivatives is untenable. The narrower distinction is an empirical question, requiring results rather than a novelty declaration.

Our fixed proposal in `analysis/theory-design.md` §5 and `03-hypotheses.md` predicts F5's 320-chip vector: `p_hat = b + kappa v`, where `b` is C0 background and `v` transports the exact clean-to-final-mark encoder displacement through the declared downstream sampler, decoder and reader around C0. Its inference then passes through the frozen nonlinear decoder and semantic proxy. This is an unmeasured, privileged prediction procedure with clean source, final marked input, C0 trajectory and target-model derivative access. It is not a proposed new insertion algorithm. Its critical tests are out-of-source/family prediction, approximation error, signed readout and compound detection, with the marked target output reserved as scored ground truth.

Thus the relevant contrast is the **object and endpoint of the derivative**, not a generic low-rank-versus-full-rank distinction. Existing local docs already separate latent displacement, transported chips and final C. Do not infer an F5 survival guarantee from a PMP null-space argument or identify rank with readable signed signal. Conversely, do not dismiss this paper merely as generation-time work: its user scenario directly prevents that dismissal. This card changes positioning evidence only; the frozen predictor and experiment remain unchanged.

## Exact locators and search receipt

- Search queries: `"Shallow Diffuse" watermarking` and `"Vj56Z9yNCr"`; 2026-10-25. Primary results: official NeurIPS proceedings, arXiv, author project and official GitHub. Search snippets were leads only.
- Requested [OpenReview PDF](https://openreview.net/pdf?id=Vj56Z9yNCr) returned a browser-verification page. Proceedings PDF fetch failed because the 17,336,540-byte response exceeded the web reader's limit. No local download was attempted. Conference identity is verified through proceedings; substantive inspection uses the explicitly versioned v5 arXiv HTML, not an assertion of bit-identical conference text.
- v5 §2.2, Eq. (2): Jacobian definition and local linearity; §3.1, Eqs. (3)–(5): insertion and PMP/DDIM distinction; §3.2, Eqs. (6)–(7): pattern and detector; §3.3: empty-prompt user insertion and detection.
- v5 §4, Assumption 1, Theorems 1–2, Eqs. (8)–(9): theorem scope; §5 evaluation datasets/metrics and Table 1; Appendix C.1 and Table 4: attacks; Appendix E/Table 12: FLUX adaptation. Web line locations in inspected rendering: 147–156, 198–250, 251–280, 287–311, 459–520, 561–572, 682–704.
- GitHub functions inspected in browser: `initialize_attackers`, `image_distortion_diffpure`; argument declarations `--model_id`, `--guidance_scale`, `--num_inference_steps`. No code was downloaded or executed.
