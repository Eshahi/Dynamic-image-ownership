# LaWa: inspected method and evaluation

Evidence level **V2**. Inspected 2026-10-20; post-hoc eligibility is established in the method below. This is literature evidence, not a local outcome or execution approval.

## Source identity and inspected sections

Exact title: **LaWa: Using Latent Space for In-Generation Image Watermarking**. Version/date: arXiv:2408.05868v1 [cs.CV] 11 Aug 2024. Venue: ECCV 2024; official README confirms.

Authors: Ahmad Rezaei; Mohammad Akbari; Saeed Ranjbar Alvar; Arezou Fatemi; Yong Zhang. Year: 2024. DOI: not established for this inspected version.

Stable ID: `arxiv:2408.05868v1`. Citekey: `T3LaWa2408`. Canonical URL: https://arxiv.org/abs/2408.05868v1

Primary full text: https://arxiv.org/html/2408.05868v1

Cached text: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T3b/lawa.txt`
SHA-256: `bcccee962a53738a1ce11b0d755e99969285e8ba5ef7e6f0bbc744370bff7f4f`

Actually inspected: §§3.1–3.4,4.1–4.2,4.6–4.7 and Figure 7; official README/download.sh.

Full source and official-code cache hashes/URLs are in [deepening-manifest.json](../deepening-manifest.json); earlier release/weight metadata is retained in [manifest.json](../manifest.json). A cached abstract or repository listing alone does not establish V2.

## Mechanism and post-hoc applicability

A watermark-aware autoencoder decoder supports generation and an explicit post-hoc residual path: x + D_wm(E(x)) - D_orig(E(x)). Only that existing-image path qualifies for this post-hoc count.

## Native operating point and detector side information

The inspected setting uses 48 bits and a KL-f8 codec, trained at 256 and evaluated at 512 pixels. Equation 6's inclusive binomial tail and Equation 7's strict match inequality differ. The identification example uses N=10^5, target FPR 10^-6 and threshold 45/48 with a strict comparison. This must be resolved before implementation. Both codec decoders and the expected message are dependencies; the original image is used when embedding, not required as an enrolled detector reference.

## Code, weights, pinned release and licenses

vbdi/LaWa@251ac11aa223e6ff12553364a65a75add5b1aecf is the official repository. README/download.sh point to https://vbdai-notebooks.obs.cn-north-4.myhuaweicloud.com/lawa/pretrained-checkpoints/last.ckpt and first_stage_KL-f8.ckpt. No LICENSE was verified in the inspected tree; model permissions and artifact hashes are unresolved. The post-hoc route still needs the autoencoder even if SD1.4 generation weights are omitted.

## Published evaluation and regeneration conditions

Evaluation includes 1,000 generated 512-pixel images × 10 messages and a natural-image comparison. Figure 7 studies bmshj2018, cheng2020, KL-VAE and VQ-VAE attacks. Section 4.7 states KL-VAE f8 bit accuracy 85% versus Stable Signature 55%; this is not isolated post-hoc-only evidence and must not be assigned to the arbitrary-image arm. Exact per-condition counts, quality and graphical values are not fully tabulated. No diffusion-denoising regeneration tuple is established; generation-time editing in Section 4.5 is not a removal attack after embedding.

## Cost and uncertainty

Training at batch size 8 is reported to fit 32 GB; this is not inference memory. Post-hoc residual embedding needs an encoder and two decoder outputs, unlike a watermark inserted during an already-required generation pass.

## Limitation and design implication

An important latent post-hoc family that earlier taxonomy could miss. Keep post-hoc and generation-time results separate and resolve licensing before any proposal.

Disposition: **Literature coverage; excluded**
