# Residual transferability: primary-source card

Inspected 2026-10-25 by Codex agent. Research only; no execution, downloads, baseline changes or protocol changes.

## Identity and access record

Dong, Ziping; Li, Qi; Wang, Xinchao. *Residual Transferability in Neural Image Watermarking*. arXiv:2609.32241v1, submitted 2026-09-26 04:59:33 UTC; preprint.

- [Version record](https://arxiv.org/abs/2609.32241v1)
- [Primary full text read](https://arxiv.org/html/2609.32241v1)
- Discovery: parent-supplied exact URL, opened directly; no search query.
- Read scope: full methods and experiments, Sections 2–5; Appendices A–G. Abstract is not the evidence basis.
- Source-derived digest below is deliberately bounded to fewer than 200 words; subsequent interpretation is local reasoning, not additional paper reporting.

## Bounded source digest

Sections 2.3/3.1: practical attackers see marked references, without encoder/decoder parameters or encoder queries; oracle RT additionally uses clean originals. RT@s=max(2×meanBitAcc−1,0), averaging s residuals; defaults s=100, five messages, 100 disjoint targets (500 message-target evaluations).

Section 4: CoverLock embeds m XOR b(x), then unwraps decoded payload using b(received-image). Frozen DINOv2 patch mean/std, trained projector and fixed orthogonal projection produce b; training excludes watermark models/forgeries. Verification needs received-image features and candidate message, not original pixels.

Appendix E: distortion-free matched retraining controls training differences. HiDDeN RT@100: original .214; remove broadcast .228; remove GAP .313; remove both .985. RivaGAN attention replacement: RT .077→.944, PSNR 42.12→42.11. MBRS/CIN BG additions reduce RT but PSNR falls 42.32→27.07/41.55→21.71; VINE fails training.

Sections 5.1–5.3: Bernoulli-null FPR<10^-6; Table 2 mean ASR (%) GT@1/100-reference averaging/WMForger: .243/.015/.059, three seeds; denominators unspecified. Six-distortion mean CoverLock BitAcc CIN/MBRS/VINE: 94.60/89.40/87.75%. Appendix F: zero accepts/50,000 ImageNet negatives. Appendix A leaves adaptive attacks/distribution shifts open.

## Local interpretation and limits

### What “transfer” means here

The transferred object is a pixel residual between a marked source and its original, or an estimate of that residual, added to an unrelated target image. Source and target are image roles. They are not source/target diffusion models or independently trained autoencoders. This paper therefore cannot supply evidence that an SD1.5-directed F5 signal survives SDXL, FLUX or MoVQ regeneration. Its architectural interventions concern watermark encoders and decoders; retraining separate seed instances is not an independent-regenerator-encoder control.

The oracle access distinction matters. Computing an exact residual requires the clean source, which a real attacker who only has a released marked image may lack. RT is a system diagnostic under privileged access, not automatically an operational black-box attack success rate. Conversely, a low estimated-attack ASR may reflect estimation failure; it does not alone establish low oracle RT. The 500 message-target evaluations reuse residuals and images, so they should not be treated as 500 independent experimental units.

### Architecture and causal interpretation

Matched retraining and the two-factor removal design support a local architectural intervention claim. They do not establish that architecture explains every difference among original deployed systems. The nearly unchanged RivaGAN PSNR makes its attention replacement a cleaner quality comparison than BG insertion into MBRS/CIN. Large quality losses or failed training prevent interpreting all reduced RT values as a free security improvement at fixed utility. Distortion-free interventions also cannot be transported unchanged to a regeneration-robust deployment claim.

### Presence, binding and the thesis endpoints

In the project, F5 is a fixed image-domain encoder-directed writer. Its semantic C endpoint combines a content-derived payload and a threshold. Successful carrier/presence recovery and successful content binding are different events. A residual that remains decodable on an unrelated image threatens binding even if presence detection is strong; a binding defense can reduce final acceptance without reducing residual recovery itself. CoverLock's wrapper is conceptually relevant to that decomposition, but it is not evidence that F5's existing content mechanism provides the same protection.

Unrelated-image transplantation maps primarily to T4 copy-paste/forgery. It may expose a T5 acceptance failure if unrelated or look-alike content is accepted, but this paper's unrelated targets do not by themselves resolve near-duplicate semantic collision. T3 is regeneration of the marked image; conventional-distortion BitAcc and residual-transfer ASR cannot replace that endpoint. No new experiment or CoverLock baseline is proposed by this card.

### Information and false-positive limits

Recomputing a learned hash from the suspect avoids a stored original image at verification, but still adds a feature extractor, learned hash state and a candidate message to the detector's information requirements. XOR wrapping is not a cryptographic signature, proof of rightful ownership or guarantee against adaptive content collisions.

The claimed FPR level is a model-calibrated tail probability, not an empirical million-negative certificate. Zero accepts among 50,000 negatives gives a one-sided 95% binomial upper bound of about 5.99×10^-5 under independent sampling, from 1−0.05^(1/50000). Thus the negative sample alone cannot validate 10^-6. Report ASR as adversarial acceptance separately from ordinary-image FPR. The unspecified Table 2 per-cell trial count prevents converting rounded rates into exact event counts or confidence intervals.

## Claim boundary

Use this source to motivate separating residual transport, decoder presence and image binding, and to warn that image-shaped residuals need not be binding evidence. Do not use it to certify independent-encoder regeneration survival, the thesis's strict PSNR/SSIM/LPIPS quality gate, near-duplicate safety, cryptographic binding or lawful ownership.
