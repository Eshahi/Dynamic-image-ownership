# OSI primary-source card

Stable ID: `arxiv-2602.09494-v1`; citation key: `Chen2026OSIv1`.
Title: *OSI: One-step Inversion Excels in Extracting Diffusion Watermarks*.
Authors: Yuwei Chen, Zhenliang He, Jia Tang, Meina Kan, Shiguang Shan.
Year/source: 2026 arXiv preprint; no accepted-venue claim.
Canonical inspected full text: https://arxiv.org/html/2602.09494v1.
DOI: `10.48550/arXiv.2602.09494`. Version: v1, 2026-02-10.
Access: 2026-10-04. Local original HTML: `osi-v1.html`.
License: arXiv.org perpetual non-exclusive license, explicitly linked at the
original HTML header; this is not a Creative Commons license.
SHA256: `61df37a758ec308c4ce1223c99de54548d28e6e893b63a537c13d76b0456efd6`.
Verification: inspected downloaded original methods and experiments; source
inspection does not independently validate the authors' measurements.

## Bounded primary evidence

OSI retains Gaussian Shading generation, but trains a VAE encoder and
backbone-initialized sign classifier using BCE and encoded-latent MSE
(§3.2/Eqs3–6). Extraction needs learned weights, cryptographic key, repetition
layout and decision rule; generation remains unchanged. Training uses synthetic
noise/image/latent triplets (§3.3), not existing-photo enrollment.

AppendixD.1/Figure7 explicitly defines Step-0 as encoder output: clean message
bit accuracy exceeds98% at spatial repetition f_hw=8, before any UNet pass.
This is repeated-message accuracy, not raw latent-sign accuracy, exact-payload
probability or an attacked Step-0 TPR.

For SD2.1, trained OSI f_hw=8 clean/adversarial bit accuracy is1.0000/.9939,
versus GS1.0000/.9728 (Table1). Adversarial denotes standard distortions;
advanced tests cover quantized-VAE compression and constrained ResNet/CLIP
embedding perturbations (§5.2/AppendixC.2), not diffusion-regeneration strengths.
A100 extraction is.06s/1.92TFLOPs versus50-step GS1.52s/41.3TFLOPs (Table1).
Training takes approximately15hours on8A10040GB GPUs (§5.2).

SDP's first1000 prompts are evaluated; approximately72000 remaining prompts
supply training triplets (§5.1). COCO evaluation also generates images from
prompts. These preprint measurements do not establish existing-photo quality,
content binding, public-forgery resistance, T4 localization or T5 separation.

Inspected locators: HTML `S3.SS1`, `S3.SS2`, `S3.SS3`, `S4`, `S5.SS1`
and its implementation-detail children, `S5.SS2` and its performance/cost/
attack children, `S5.SS3`, `A3.SS2`, `A4.SS1`–`A4.SS5`; Table1 and
Figure7 caption/text. Figure7 was not digitized: only the textual >98%
statement is reported. Stance: supports direct encoded-latent readout as prior
art; inconclusive for the proposal's full requirements. Confidence: high for
transcribed method/table statements, without a replication claim.

## Agent inference for M1 (separate from author evidence)

The encoder-only B-LW1 diagnostic has direct prior art here, so the local
observation must not be presented as discovery of an otherwise unknown
zero-inversion channel. OSI's Step-0 ablation and its trained one-step
classifier are different procedures: our zero-UNet assay does not inherit
trained OSI accuracy, latency or robustness. SD1.5 with our fixed sign
layout, public development key and 180/256 threshold also differs from the
paper's SD2.1 experiment. Repetition can improve message recovery while
individual latent signs remain noisy; presence and exact payload are separate
outcomes. No population false-positive bound transfers from four local prompt
clusters or the paper's threshold to our assay. Public fixture whitening does
not authenticate authorship or bind CLIP+pHash+OwnerID to an image.

The pinned local VAE permits a zero-UNet diagnostic without extra weights;
faithful learned OSI requires a trained detector and its training protocol.
No weights were obtained, and the reported eight-A100 training schedule is
not evidence of immediate feasibility on the local12GB GPU. This card does
not propose or execute training. Existing-photo preservation and T3/T4/T5
remain independent development requirements.

## Artifact and validation boundary

The canonical abstract metadata https://arxiv.org/abs/2602.09494 lists only
v1 at access. No newer full text, author code, models, binary artifacts or
held-out data were obtained. The literature helper
`scripts/validate_literature.py` is absent from this worktree; checksum,
source metadata, source locators and bibliography uniqueness were checked
mechanically, without claiming unavailable helper validation.
