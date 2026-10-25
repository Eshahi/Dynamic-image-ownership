# PhotoGuard

- Title: Raising the Cost of Malicious AI-Powered Image Editing
- Authors: Hadi Salman; Alaa Khaddaj; Guillaume Leclerc; Andrew Ilyas; Aleksander Madry
- Year / venue: 2023 / ICML, PMLR 202. DOI: null (not verified).
- ID / citation key: arXiv:2302.06588 / salman2023photoguard
- [Primary final paper](https://proceedings.mlr.press/v202/salman23a/salman23a.pdf)
- Version inspected: PMLR proceedings PDF, 25 PDF pages. Access: 2026-10-25.
- Verification: **V2**. Read §3 Eq.4–5; §4.1–4.2, Table 1; §5 limitations; Appendix A Algorithm 1. Cache/hash in source-manifest.json.

**Direct evidence.** The encoder attack minimizes distance to a target latent under a pixel perturbation budget; the diffusion attack differentiates through part of generation. The evaluated model is SD1.5. Algorithm 1 specifies an infinity-norm budget 16/255, step 2/255 and 200 steps. In Table 1's 60-image edit comparison, encoder attack yields PSNR 14.91±2.78 versus 19.21±4.00 for matched-intensity random noise; these compare generated edits, not perturbation imperceptibility. §5 explicitly limits forward compatibility and resistance to transformations/purification.

**Author interpretation.** Encoder-directed small perturbations can disrupt a latent diffusion editor.

**Agent inference.** This motivates measuring directional encoder sensitivity for F5, whose objective instead embeds a readable carrier. It does not show that independent autoencoders remove that carrier, or that high encoder gain ensures survival after denoising.

**Open assumption / limit.** Transfer from immunization to watermark retention is unmeasured. No independent-autoencoder watermark experiment or watermark FPR is supplied here.
