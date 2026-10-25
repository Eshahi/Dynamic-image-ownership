# GhostVAE: primary-source threat-boundary card

Recorded: 2026-10-25 17:00 UTC. Research only; no experiment proposed or executed.

## Source identity and access

- Stable ID / citation key: `liu2026ghostvae`.
- Title: *Robust Watermarks Meet Backdoored Models: Evading Diffusion Semantic Watermarks via Stealthy Backdoor*.
- Authors: Jinyuan Liu, Tianshuo Cong, Pei Li, Tianrui Wang, Xinlei He, Anyu Wang, Xiaoyun Wang.
- Venue/version: USENIX Security 2026 proceedings, pp. 281–300; official 21-page PDF includes cover. DOI: unknown/null.
- Canonical [presentation page](https://www.usenix.org/conference/usenixsecurity26/presentation/liu-jinyuan); inspected [official PDF](https://www.usenix.org/system/files/usenixsecurity26-liu-jinyuan.pdf).
- Verification: primary full-text browser inspection, not locally checksum-verified. No local paper, model, code, weights, dataset or image download; no code execution. This bounded card does not assert the literature skill's stronger local-artifact verification status.

## Direct evidence (under 200 words, excluding bibliographic metadata)

The supplier has white-box pipeline control; users receive a universal image trigger. The supplier retains a backdoored **verification VAE encoder**. Generation decoder weights are outside the modification (§§3, 4.1–4.2, pp. 284–286). Training uses 8,000 unwatermarked generated images; evaluation uses 1,000 disjoint prompts. Trigger learning targets latent sign reversal with spectral regularization; encoder fine-tuning preserves clean responses and aligns parameter distributions (§§4.2–5.1).

Targets: Tree-Ring, Gaussian Shading, PRCMark; SD-2.1-base, SDXL-base-1.0, FLUX.1-dev. Default trigger budget: 8/255; evaluation images: 512×512 (§5.1). Table 3 ASR percentages, scheme order above: SD2.1 **88.2/86.0/100.0**; SDXL **97.1/93.8/99.0**; FLUX **99.1/92.5/96.0**. ASR means triggered watermarked images escaping detection, not conditional success among originally detected images. Table 4 clean GhostVAE TPRs: **93.5/98.7/100.0; 90.1/87.0/86.4; 94.0/100.0/99.6**. Thus **94.6%** and **94.4%** summarize nine triggered-ASR and clean-TPR cells respectively (§5.2, p. 288).

Crucial ablation: SD2.1/PRCMark at 8/255 gives **31.6% without encoder training**, **100% with it** (Table 5). Thresholds are setting-specific (Appendix B.1).

## Agent inference and reporting boundary

Stance: supporting a detector-integrity limitation; inconclusive for fixed trusted-detector regeneration resistance. Confidence: high for this boundary, conditional on the inspected proceedings version.

The main headline combines an altered verifier with an image trigger. It does not establish 94.6% evasion when an adversary can change only the suspect image and the verifier remains independently trusted and fixed. Conversely, the input-only ablation prevents claiming the trigger is wholly ineffective against an unchanged encoder. The generation-side model names identify evaluation backbones; they do not turn the headline into an independent-regenerator transfer test.

For this thesis, treat compromised verification weights as an additional supply-chain assumption outside the fixed-detector T3 comparison. Do not pool these percentages with F5 regeneration counts, identify the altered verification encoder with the attack regenerator, describe high ASR as proof that the embedded signal was physically erased, or infer an ownership/content-binding guarantee. No new experiment or attack implementation follows from this card.

## Arithmetic check (agent calculation, not a new scientific result)

Equal-weight means of the displayed cells: ASR = 851.7/9 = 94.6333%; clean TPR = 849.3/9 = 94.3667%. They round to the headline figures. These are averages over model–scheme cells, not worst-case performance or a confidence bound. Equal per-cell prompt counts make the unweighted arithmetic compatible with an equally sized pooled denominator; the card does not infer independence across prompts, schemes or models.

## Inspection record and limitations

- Exact search queries: none. Direct opening of the supplied official presentation URL; clicked its “Liu PDF” link to the official PDF URL above.
- Browser text inspected: §§3–4.2 (threat model and full two-stage method), §§5.1–5.5 (setup, main tables, ablations, sensitivity and baseline comparison), §6 including cross-encoder verification, §7 discussion, and Appendix B.1 threshold text/Table 11. Browser page-8 screenshot requested for Tables 3–4; numerical verification here rests on the returned primary PDF text.
- Direct PDF line opens: 470, 610, 730, 799, 855, 925, 1060, 1111, 1490, 1680; within-PDF searches: `B.1`, `Threshold`. The browser returned surrounding ranges, not just isolated lines. Physical PDF pages are one greater than article-internal page offsets because of the proceedings cover.
- Access limits: no executable artifacts, replication, author correspondence or independent measurements inspected. Detailed defense numbers are intentionally not reproduced within this card's source-paraphrase budget. The displayed thresholds have not been independently validated. Source-derived factual summary is confined to the direct-evidence block; other sections identify access or explicitly separate inference/arithmetic.
- Skill handling: followed `thesis-literature-synthesis` evidence categories; the parent instruction authorizes only this one file, so its multi-file synthesis/validation pipeline was not run. No protected ledger or bibliography was modified.
