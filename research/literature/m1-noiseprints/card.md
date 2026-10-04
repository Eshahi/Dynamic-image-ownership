# NoisePrints primary-source card

Stable ID: `arxiv-2510.13793-v1`; citation key: `Goren2025NoisePrintsv1`.
Title: *NoisePrints: Distortion-Free Watermarks for Authorship in Private Diffusion Models*.
Authors: Nir Goren, Oren Katzir, Abhinav Nakarmi, Eyal Ronen, Mahmood Sharif,
Or Patashnik. Year: 2025. Source type/venue: arXiv preprint, inspected v1,
not a claim of conference-version inspection.
DOI: `10.48550/arXiv.2510.13793` (arXiv metadata DOI).
Canonical inspected URL: https://arxiv.org/html/2510.13793v1.
Access: 2026-10-04. Local artifact: `noiseprints-v1.html`, SHA256
`6d3b331aab0cb33a8da1907dc4c21a0c22b4f60afae070ecf1bc398dbc862f2a`.
License: CC BY-NC-SA 4.0, explicitly displayed in the primary HTML.
Verification: downloaded original HTML and inspected local method/security/
experiment text; verified provenance does not mean independent replication.

## Bounded primary evidence (direct evidence unless marked)

Generation hashes a secret seed before Gaussian sampling; no additional mark
is embedded. Verification compares regenerated initial noise with public-VAE
image latents by cosine, requiring seed, hash/PRNG specification, VAE and
threshold, without inversion (§3.3/Eq1). Disputes additionally require original
claims/alignment; ZKP optionally hides seeds (§§3.3–3.4).

The random-independent-seed spherical-cap null targets 2^-128, not adaptive
content forgery (§4). SD2.0 clean cosine=.482±.088, threshold=.101739,
pass rate1.00; SDXL/Flux pass=.99 (Table1). SD2.0 RTX3090 VAE encode
.037±.004s, cosine .182±.045ms versus inversion3.234±.075s (Table2).
Decode/re-encode changes SD2.0 cosine .4922→.4818 (AppendixE/Table3).

Regeneration uses SDXL SDEdit on SD2.0 outputs at noise levels .2/.4/.6;
Figure3 gives curves, not tabulated exact per-level TPR (§5.2). Targeted
inversion optimization uses100 steps, weights .3/.4/.5 (§5.2). Low-entropy
logos fail in SDXL/schnell (AppendixG). Public VAE availability and restricted
geometry limit applicability; real-image injection defeats real/fake use (§6).
These are generated-image results, not existing-photo preservation. Sample
counts are not specified in the inspected reliability text/Table1. No arbitrary
multi-bit payload or CLIP+DCT binding is demonstrated.

Inspected locators: HTML `S3.SS3`, `S3.SS4`, `S4`, `S5.SS1`, `S5.SS2`,
`S6`, `A3.SS4`, `A5`, `A7`; Tables1–3 and Figure3 caption/text. Robustness
curve images were not digitized; no numeric curve estimates are asserted.
Stance: supports plausibility of initial-to-terminal latent correlation;
inconclusive for proposal completion. Confidence: high in transcribed method/
table values, not a replication or unconditional security endorsement.

## Agent inference for M1 (separate from author evidence)

The local B-LW1 result in `research/m1-gs-paired-results.md` is mechanistically
plausible: direct encoded-latent readout need not lose every trace of starting
noise. This does not establish that coordinate-sign majority and a global
cosine are equivalent detectors or that their nulls transfer. Our public
development key/nonce/reference fixtures cannot inherit a secret-seed claim.
A follow-up could measure aligned noise–terminal correlation on development
metadata under a new frozen protocol, but should not silently recalibrate the
completed run. Source hashes and enrollment records must distinguish generated
counterfactuals from pre-existing photographs. Quality-preserving existing-photo
embedding, CLIP+pHash+OwnerID binding, T4 localization and T5 state separation
remain unresolved. The local SD1.5 VAE already exists; no additional weights
are required merely to implement a cosine diagnostic, but implementing or
running one is outside this literature task. ZKP circuitry is also outside
the current pinned environment and is not implied by a lightweight reader.

## Version and access boundary

The canonical [arXiv abstract record](https://arxiv.org/abs/2510.13793) currently
lists v2 dated2026-04-14; the inspected source is v1 dated2025-10-15. The newer
full text and ICLR2026/OpenReview PDF were not inspected here. Do not describe
this card as latest-version or accepted-paper verification. Author repository
https://github.com/nirgoren/NoisePrints is linked by the paper but was not
downloaded/executed/inspected in this bounded task. No binaries, models,
scientific data or held-out content were obtained.

The installed skill's `scripts/validate_literature.py` helper is absent from
this worktree. Local checksum, bibliography uniqueness, metadata and locators
were checked mechanically; no unavailable helper validation is claimed.
