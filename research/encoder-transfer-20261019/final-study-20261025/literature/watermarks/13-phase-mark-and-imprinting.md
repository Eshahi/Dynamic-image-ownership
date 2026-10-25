# PhaseMark and Semantic Imprinting: original-source check

Date: 2026-10-25. Author: Codex literature subagent, bounded contribution to WP6; not an independent milestone review. No experiment, model, image, code download or local metric computation was performed. Main authoritative STATE was read once. No shared bibliography/search log was edited.

## Version and access ledger

| Work | Exact primary source | Read status | Decision |
|---|---|---|---|
| Sung Ju Lee and Nam Ik Cho, *PhaseMark: A Post-hoc, Optimization-Free Watermarking of AI-generated Images in the Latent Frequency Domain* | [arXiv:2601.13128v1](https://arxiv.org/html/2601.13128v1), 19 January 2026; [versioned abstract](https://arxiv.org/abs/2601.13128v1); [PDF](https://arxiv.org/pdf/2601.13128v1) | V2: original methods §§2.1–2.3 and experiments §§3.1–3.4 read in HTML. PDF opened, not downloaded. | Underlying paper is verified at this version. arXiv lists acceptance at ICASSP 2026. Publisher DOI supplied in the parent brief is 10.1109/ICASSP55912.2026.11463051; publisher full text was not accessed. Do not claim publisher-version identity. |
| Same authors, *The Semantic Imprinting Hypothesis: How Semantic Watermarks Survive Prompt-based Editing* | [OpenReview forum hNbkvSjEAD](https://openreview.net/forum?id=hNbkvSjEAD); [official workshop accepted-paper list](https://trustworthy-ai-workshop.github.io/iclr2026/papers) | V1: title, authors and workshop listing verified; original methods/experiments NOT read. Parent reported a browser-verification barrier at the forum; no attempt was made to bypass it. | Author profile links the same forum. Ordinary title/author/arXiv searches found no accessible independent original full text. Retain original SIH as unverified for detailed evidentiary claims. |
| Same authors, *Diffusion-Generated Image Watermarking: A Two-Axis Taxonomy and Three Protocol-Bounded Case Studies* | [arXiv:2610.09755v1](https://arxiv.org/html/2610.09755v1), 7 October 2026 | V2 for this taxonomy's own §§5–6 statements; NOT V2 for the inaccessible underlying SIH paper | Explicitly distinguish the later author's restatement from the earlier original. |

V1/V2 here mean identity/metadata checked versus method-and-experiment text inspected; they are evidence-access labels, not peer-review or replication grades.

## PhaseMark: verified original-paper extraction

PhaseMark encodes with the source LDM VAE, changes FFT phases in a central latent crop, enforces Hermitian symmetry and decodes. Four variants use hard/soft absolute/relative modulation. Detection re-encodes and thresholds bit agreement; it uses the VAE and expected payload, without DDIM inversion. Setup: SD2.1-base, 1,000 generated 512-square images per prompt dataset, 128 bits. Table 1 reports APM verification TPR@1%FPR of .996/.997/1.000 under VAE-B/VAE-C/diffusion regeneration; PCQ .918/.933/1.000. VAE-B and VAE-C reference learned image-compression codecs, not SDXL/FLUX diffusion autoencoders. The diffusion attack is described as 60 steps, without a named independent diffusion-backbone transfer grid. PCQ PSNR is 34.156 (§3.3). Tables separate verification from million-user, Bonferroni-corrected payload identification. Latency is .142/.050 seconds for embedding/detection (Table 2), hardware unspecified in inspected text. These are author-reported results, not replicated measurements. [Original §§2–3](https://arxiv.org/html/2601.13128v1).

## SIH: what is accessible and what remains unverified

The later taxonomy describes SD2.1-generated sources edited by SD1.5 InfEdit; seed independence retains source conditioning. Its §5.2 calls the feature carrier untested and recommends paired pre/post detection, conditional retention, fixed thresholds, fidelity controls and intervention. It does not identify a localized semantic carrier. Its Table 6 reports APM quality 31.715 dB/.129 LPIPS and PCQ 34.156/.037. These are **taxonomy-version** statements; the original SIH paper's sample construction, thresholds, controls and experiments remain unverified here. [Taxonomy §§5–6](https://arxiv.org/html/2610.09755v1).

## Consequences for the existing F5 transfer question (research interpretation)

1. **Closest representation is not equivalent implementation.** PhaseMark changes and decodes a VAE latent directly. F5 is the selected encoder-directed image-domain writer. Their computational paths and feasible perturbations differ, so proximity in a taxonomy neither predicts F5 performance nor makes F5 a latent insertion method.
2. **Do not equate codec regeneration with independent diffusion-encoder transfer.** The original PhaseMark attack names alone could invite this error. A compressor reconstruction and SDXL image-to-image generation intervene on different objects. Existing F5 results cannot be ranked against PhaseMark's reported TPRs without matched images, quality, detector calibration and attack implementation.
3. **Seed independence and encoder independence answer different questions.** A source-conditioned editor can convey image information while starting from fresh noise. That possibility is compatible with encoder-sensitive survival. SD-version changes must not be counted as proof of independently trained autoencoders without a separate lineage audit; no such audit was performed here.
4. **Retention is conditional, not causal.** Conditioning on successful pre-edit detection is useful descriptively but selects a detectable subset. High conditional retention does not identify the carrier, and a cross-editor difference does not isolate an encoder effect. Preserve the full attempted-source denominator alongside paired retention in the already planned server analysis.
5. **Quality remains a selection constraint.** A distribution-level FID change cannot establish the thesis's strict per-image quality gate. Even an average PSNR above a target would not establish an all-images pass. Do not use the attractive robustness operating point to relax the F5 quality requirement after seeing results.

This contribution adds literature context only. It proposes no new baseline, writer variant, experiment or execution infrastructure, and makes no publication-readiness claim.

## Search/open log (2026-10-25, public text only)

- Queries: `"PhaseMark" Lee Cho watermark`; `"Semantic Imprinting Hypothesis"`; `"11463051"` (mostly irrelevant results, discarded).
- Opens: arXiv HTML 2601.13128v1 and 2610.09755v1; PhaseMark abstract and versioned PDF; original PhaseMark method, detection, experiment and references sections.
- Queries: `"Semantic Imprinting" watermark Lee Cho`; `"hNbkvSjEAD"`; `site:arxiv.org "Imprinting" "watermark" "Lee"`.
- Opened [author GitHub profile](https://github.com/thomas11809); it links PhaseMark publisher/code and SIH OpenReview. No code link followed or downloaded.
- Queries: full SIH title; `"hNbkvSjEAD" arxiv`; `"Sung Ju Lee" "Semantic Imprinting" pdf`.
- Opened official workshop accepted list (poster 12 confirms title/authors). Its paper link returned an internal access error. Author homepage redirected to `https://thomas11809.github.io/personal-website/`; subsequent open returned inaccessible. No alternate SIH original was obtained.
- Search-discovered secondary aggregators and suspicious mirrored arXiv search pages were not used as evidence. The Korean journal source was a search lead only; its stronger carrier wording is not substituted for the scoped English taxonomy.

## Optional bibliography entries for root integration

```bibtex
@misc{lee2026phasemark,
  title={PhaseMark: A Post-hoc, Optimization-Free Watermarking of AI-generated Images in the Latent Frequency Domain},
  author={Lee, Sung Ju and Cho, Nam Ik},
  year={2026}, eprint={2601.13128}, archivePrefix={arXiv}, primaryClass={cs.CV},
  url={https://arxiv.org/abs/2601.13128v1},
  note={Version 1 inspected; arXiv states accepted at ICASSP 2026}
}
@misc{lee2026imprinting,
  title={The Semantic Imprinting Hypothesis: How Semantic Watermarks Survive Prompt-based Editing},
  author={Lee, Sung Ju and Cho, Nam Ik}, year={2026},
  url={https://openreview.net/forum?id=hNbkvSjEAD},
  note={ICLR 2026 Workshop on Principled Design for Trustworthy AI; identity verified, original full text not inspected}
}
```
