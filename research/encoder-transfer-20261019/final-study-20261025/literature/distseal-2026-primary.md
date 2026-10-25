# DistSeal: primary-source card

Inspected 2026-10-25 by Codex agent. V2: full arXiv method and experimental text inspected; no code executed or downloaded.

**Identity.** *Learning to Watermark in the Latent Space of Generative Models*. Sylvestre-Alvise Rebuffi, Tuan Tran, Valeriu Lacatusu, Pierre Fernandez, Tomáš Souček, Nikola Jovanović, Tom Sander, Hady Elsahar, Alexandre Mourachko. [arXiv v1](https://arxiv.org/abs/2601.16140), 2026-01-22; only version listed. [PMLR](https://proceedings.mlr.press/v306/rebuffi26a.html) identifies ICML2026, 306:104101–104129 (Tran appears as Tuan A. Tran).

**Inspected evidence, compressed to respect source budget.** [Full text](https://arxiv.org/html/2601.16140v1): §4 embeds `z+epsilon W(z,m)`, decodes, and extracts bits from pixels; optional generator/decoder distillation fixes the message. §5.1: ImageNet, DCAE/UViT-H and RAR-XL; 64 bits, 600k training steps, 50k evaluation images. Table1 DCAE latent: PSNR31.06dB, average bit accuracy95.18%, combined84.28%; Table5 distilled diffusion94.78%, decoder96.77%. AppendixB/Table7 tests brightness/contrast/saturation/hue/grayscale/blur, flip/rotation/resize/crop, JPEG and JPEG–crop–brightness. AppendixE examines LoRA forgetting. AppendixH.1/Table14 switches to fine-tuned RAR decoders, not independently trained encoders. No full image-regeneration evaluation or fixed-FPR detection endpoint was found. §6 acknowledges strong-geometric and forgetting limitations. Generalization across separately trained systems is not demonstrated.

**Detector side information.** The [official repository README](https://github.com/facebookresearch/DistSeal), lines306–314 and366–374 as inspected, loads both a learned detector and `secret_msg`, passes normalized suspect pixels, and computes bit agreement. It expects RAR256×256 or DCAE512×512. No original image, registry, source latent, diffusion inversion or regenerating encoder appears in these detection examples. This is learned extractor plus expected-message side information, not evidence of a calibrated ownership verifier.

**Interpretation for this dossier.** F5 is the fixed image-domain encoder-directed writer specified in the task; the authoritative local STATE reports SD1.5 C60/57/39, SDXL0, and foreign-codec round-trip55/60. These local figures and DistSeal's bit accuracies measure different events. The useful overlap is investigation of which representations preserve an extractable signal. The operational difference is F5's fixed image writer versus DistSeal's trained latent embedder and optional model distillation. A same-ancestry decoder-switch experiment does not answer the independently trained encoder plus full-regeneration question. None of this establishes novelty priority or warrants adding a baseline or changing the protocol.

**Version/access boundary.** Proceedings landing page opened directly and its bibliographic record inspected. Its linked PDF (`https://raw.githubusercontent.com/mlresearch/v306/main/assets/rebuffi26a/rebuffi26a.pdf`) failed: unsupported `application/octet-stream`; the landing-page OpenReview click also failed resolution. Proceedings full-text equivalence to arXiv is therefore V1/unknown. Technical statements above refer only to the inspected arXiv v1.

**Exact retrieval log.**

- Direct open: `https://arxiv.org/abs/2601.16140`.
- Direct opens: `https://arxiv.org/html/2601.16140v1`; `https://github.com/facebookresearch/DistSeal`.
- Full-text direct-open windows at lines105,204,350,485; these covered §3–§6 and AppendicesA–J, including methods, experiment tables, evaluation transformations, forgetting and decoder switching. Figure captions were read; unseen figure pixels were not assessed.
- Exact search: `"Learning to Watermark in the Latent Space of Generative Models" DistSeal arxiv version regeneration`.
- Direct opens: `https://proceedings.mlr.press/v306/rebuffi26a.html`; linked raw PDF above (failed).
- PMLR landing-page link9 OpenReview click failed. Search snippets and abstract-only material supplied no technical assertions in this card.
