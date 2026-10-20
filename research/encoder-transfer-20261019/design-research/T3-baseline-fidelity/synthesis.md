# T3: faithful post-hoc baselines and conditional regeneration evidence

Updated 2026-10-20 by Codex agent. This is a research-only stage 1b package. It contains **24 distinct post-hoc methods with V2 cards**: their method and evaluation sections were inspected. A second paper version, checkpoint, payload setting or generation-time variant does not add a method to that count. The source texts stay outside git. No weights, images, GPU experiments or new scientific outcomes were produced.

The practical conclusion is unchanged: preserve the approved **WAM 32-bit and VINE-R 100-bit core arms**. Recommend **P1 TrustMark Q first** if the user authorizes an additional baseline. **P9 Pixel Seal** is a useful second addition, restricted to its proposed small grid. Neither is currently part of the core. The wider search found additional relevant methods, but publication, a public repository and a faithful runnable checkpoint are separate facts.

## Evidence and reading map

[methods.json](methods.json) and [method-comparison.csv](method-comparison.csv) contain the complete method, native setting, release/license, regeneration, cost and limitation records. [deepening-manifest.json](deepening-manifest.json) connects the 24 cards to exact source versions, cached paths and SHA-256 values. [references.bib](references.bib) has 24 inspected arXiv-version records plus the separately inspected final TrustMark paper. [search-log.md](search-log.md) distinguishes discovery from file inspection and unsuccessful access. [floor-audit.md](floor-audit.md) reports counts without treating this author's check as an independent review.

| Distinct method | Post-hoc path and relevant evidence | Present disposition |
|---|---|---|
| [WAM](cards/WAM.md) | Residual image writer, localized 32-bit extraction; own DiffPure/VAE bit-accuracy curves use paper COCO weights | Approved MIT SA-1B core release; native and queried-message endpoints separate |
| [VINE](cards/VINE.md) | Generative-prior residual writer; direct SD2.1 regeneration ROC evidence | Approved VINE-R core; actual constructor uses SD-Turbo |
| [TrustMark](cards/TrustMark.md) | Residual encoder and ResNet decoder; final ICCV denoising plus third-party results | P1 first addition; native Q ECC must be preserved |
| [StegaStamp](cards/StegaStamp.md) | Physical-channel residual writer; regeneration comes from other studies | P2 deferred for legacy runtime/checkpoint verification and low quality |
| [InvisMark](cards/InvisMark.md) | High-resolution residual writer; small 10-image SD2.1 regeneration study | Literature comparator; checkpoint provenance remains incomplete |
| [RoSteALS](cards/RoSteALS.md) | Secret offsets in frozen image-autoencoder latents | No direct original diffusion-regeneration result |
| [ZoDiac](cards/ZoDiac.md) | Optimize existing-image latent ring; inversion-based zero-bit detector | Different payload/compute/detector class; no new proposal |
| [PhaseMark](cards/PhaseMark.md) | Optimization-free phase encoding in autoencoder latent frequency domain | P3 deferred for dependency/artifact permission and fidelity work |
| [MBRS](cards/MBRS.md) | Learned image writer with mixed real/simulated JPEG training | Conventional-distortion evidence does not establish regeneration |
| [SSL](cards/SSL.md) | Per-image optimization in self-supervised feature space | Different compute and detection geometry; no new proposal |
| [SimuFreeMark](cards/SimuFreeMark.md) | Post-hoc image mark trained without an editing simulator | Published primary evidence; no verified released implementation/checkpoint license |
| [SpecGuard](cards/SpecGuard.md) | Spectral-projection image mark; robustness depends on attack conditions | Literature comparator; card preserves attack/code limitations |
| [Pixel Seal](cards/Pixel-Seal.md) | Released 256-bit image writer; own conventional tests and conditional third-party regeneration evidence | P9 second addition, limited grid only |
| [JigMark](cards/JigMark.md) | Black-box robustness training against diffusion edits | Direct editing evidence is not matched SDXL transfer |
| [Robust-Wide](cards/Robust-Wide.md) | Instruction-editing-aware image watermark | Editing settings and native quality must remain visible |
| [SpreadMark](cards/SpreadMark.md) | Spread-spectrum image mark with learned receiver | Recent robustness evidence; inspected v2 supersedes only explicit v1 content |
| [NAWE](cards/NAWE.md) | Classical watermark with neural-assisted extraction | Native operating point and available code limits differ from learned residual arms |
| [LaWa](cards/LaWa.md) | Explicit existing-image residual from original and marked autoencoder decoders | Count only post-hoc path; generation-time attack results are not reassigned |
| [Chunky-Seal](cards/Chunky-Seal.md) | Distinct scaled 1,024-bit image model, officially advertised in VideoSeal | Release omission corrected; large model and missing direct regeneration limit priority |
| [GenPTW](cards/GenPTW.md) | Shared latent framework with a separately evaluated post-hoc path | Post-hoc quality is 35.56/.864, not generation-path quality |
| [DistSeal](cards/DistSeal.md) | Direct existing-image latent embedding, separate from distilled generation | MIT release; module timing excludes codec roundtrip; no direct diffusion test |
| [EditGuard](cards/EditGuard.md) | Existing-image bit mark plus reference-based tamper localization | Local editing and dual-watermark side information limit comparability |
| [OmniGuard](cards/OmniGuard.md) | Existing-image robust-bit path trained with SD1.5 VAE surrogate | Strong relevant regeneration evidence; partial demo/release and licensing unresolved |
| [SNW](cards/SNW.md) | PixelSeal-family continuous channel with keyed subspace encoding | Recent distinct method; capacity estimates and whitening differ from presence tests |

## What changed after deeper reading

**Faithfulness precedes equalization.** WAM's released aggregation averages raw bit logits and compares with .5, while its paper describes probabilities. Its native image-presence threshold is mask-positive area >.07, separate from known-message agreement. Empty masks must abstain. VINE's paper/README says SDXL-Turbo, but the released constructor loads `stabilityai/sd-turbo`; its SD2.1 attack scripts do not demonstrate independent SDXL-encoder transfer. VINE's evaluation count statements conflict: Table 1 says 5,000 per editing method, Section 4.2 says 1,000 per regeneration family, and Section 4.3 describes severity-expanded samples. All are retained rather than silently reconciled.

**TrustMark Q is an ECC baseline.** The pinned Python encoder resizes to 256 and decoder to 245 using PIL bilinear. BCH_5 carries 61 payload bits, 35 parity bits and four header bits. `use_ECC=False` sets `detected=True` unconditionally. P1 must therefore retain native ECC and report native detected/schema, expected 61-bit equality and descriptive raw agreement separately. A Binomial(100,.5) null does not follow for a structured codeword/header. No empirical image FPR is established by BCH validity. The final ICCV paper supersedes the old preprint where explicit: Table 3's sigma=.3 denoising gives BA .660 at attacked PSNR 9.23, not a matched SDXL result. The final PDF was already successfully cached and visually checked; a later T3b HTTP 403 is a separate failed refresh.

**Recent latent methods change the taxonomy, not the core.** LaWa, GenPTW and DistSeal all have actual existing-image paths. LaWa's generation-time results cannot be assigned to that path. GenPTW post-hoc SSIM .864 and DistSeal DCAE post-hoc PSNR 31.06 are below the thesis's strict clean gate. DistSeal's 3 ms versus 63 ms CPU comparison times the watermark module in a latent representation, not an image codec roundtrip. These observations justify literature inclusion without predicting a favorable transfer result.

**Dual-watermark methods were an important omission.** EditGuard and OmniGuard now have independent cards. OmniGuard's full title is *OmniGuard: Hybrid Manipulation Localization via Augmented Versatile Deep Image Watermarking*. Its Table 3 uses 1,000 512-pixel UltraEdit images; SD Inpaint* bit accuracy is .989 for bit-only and .988 for dual marking, with different clean quality. Its mask-conditioned regeneration, missing exact strength/sampler/steps/revision and uncalibrated bit accuracy cannot be equated to our empty-prompt SDXL img2img test. The inspected demo uses WAM through a local path and is not a self-contained faithful adapter. Training fit on an 11 GB GPU is not inference memory.

**ChunkySeal is released.** An earlier exact-name search missed the official VideoSeal model zoo. The pinned README and dedicated `chunkyseal.yaml` advertise a checkpoint under MIT code/model terms. Its mutable weight URL remains unhashed and unmeasured. Parameter-only fp32 storage is about 7.19 GB before activations; this is a derived storage lower bound, not peak VRAM. No direct own diffusion-regeneration result was established. This correction is reflected in the card and matrix.

**SNW supplies useful but conditional third-party PixelSeal evidence.** SNW's September 2026 primary full text was inspected after discovery. Table 6 uses 200 MFlickr images, 48 dB residual rescaling and whitening estimated from one million unmarked images. PixelSeal's reported capacity falls from 240.5 bits at identity to 142.0 after VAE and 6.4 after Sana 10 steps; SNW's corresponding values are 684.7, 380.3 and 52.2 bits. These are independent-bit Shannon-capacity estimates. The table's rate is not bit accuracy, and neither capacity nor rate is calibrated image TPR or recovered ECC payload. Exact attack checkpoints, prompt, sampler, seeds and correspondence to SDXL strength remain unresolved. SNW's security result addresses a specified covariance/PCA model; its own Section 2.3 separates adversarial robustness from that scope.

## Costed choices for the user

These are unmeasured planning assumptions and conditional proposals. Only WAM and VINE-R are approved external core arms. They do not enlarge the current 15-hour/USD15 budget or authorize spending. At the illustrative USD1/hour rate, hours and dollars have the same numerical range. Integration effort, weight access and smoke timing can invalidate an estimate before execution.

| Proposal | Scope and hours assumed | Recommendation |
|---|---|---|
| P1 TrustMark Q | Limited: 60 clean + deterministic D1 + 180 marked R1 strength-.2 units, shared C0 reads; .4–1 hour. Full added grid: 1.2–3 hours. | First addition, after faithful ECC adapter and budget revision |
| P9 Pixel Seal | Exactly 60 clean + 180 R1 strength-.2 marked regenerations, seeds 12/13/14, shared C0 and wrong-message readouts; .55–1.25 hours | Second addition; 256-bit native message and no extra strengths/rinse/generators |
| P2 StegaStamp | Approximately .6–1.5 hours for a limited run, conditional on official checkpoint and legacy runtime | Defer; lower clean quality and runtime uncertainty |
| P3 PhaseMark | Approximately .5–1.5 hours for a limited run, conditional on artifact/dependency/license verification | Defer; do not equate code availability with a cleared runnable stack |

P9 arithmetic is 180 regenerations at an assumed 8–20 seconds plus .15 hour for marking/readout, or .55–1.15 hours before the rounded .55–1.25 planning allowance. The other ranges are scenario allowances, not measured throughput. No P11 or additional core proposal is introduced by the wider survey.

## Comparison rules and limits

Keep clean PSNR/SSIM/LPIPS, raw bit accuracy, exact useful-payload recovery, native presence and common queried-message presence in separate columns. Retain each native payload and quality setting. A 32-bit WAM mask, 61-bit ECC payload, 100 raw VINE bits, 256 PixelSeal bits and a zero-bit ring are not interchangeable. Do not tune residual strength or detection thresholds after seeing outcomes to make them appear equal.

Published BA, ROC TPR at .1% FPR, binomial query tails, mask thresholds, word accuracy allowing errors, tamper F1 and channel capacity answer different questions. The common WAM/VINE fair-query rules do not certify empirical C0 FPR, and correlated calls across images/seeds are not independent false-positive trials. Public message extraction does not prove lawful ownership or prevent forgery. Detector side information includes the queried message/key and sometimes a codec, inversion model, localization reference, whitening corpus or codebook; there is no registry in this study.

Paper/model revision, image count, resolution, strength/noise schedule, sampler, steps, guidance, prompt, seeds, quality and metric must accompany a regeneration claim where established. A missing field stays missing. Partial denoising, mask-conditioned inpainting, VAE roundtrip and conventional corruption do not establish the same mechanism or severity. No inspected baseline result is a measured outcome of the proposed independent-encoder experiment.

## what we might still have missed

Two newly discovered 2026 journal leads remain full-text inaccessible: *Semantic-aware attention-guided digital watermarking for diffusion models* (DOI 10.1016/j.image.2026.117672) and *LatentShield: A robust latent watermarking framework for diffusion-generated images with multi-objective optimization* (DOI 10.1016/j.iswa.2026.200719). Publisher acquisition returned HTTP 403. Abstracts/search snippets were not promoted to V2, and their post-hoc eligibility, methods, numbers and releases are not counted. A later primary full-text acquisition could change the survey.

WaTeRFlow is an image-to-video-specialized lead outside this image-regeneration comparison; generation-only initial-noise/signature methods and text/code watermarks do not fill the post-hoc floor. The failed arXiv API requests mean that route did not independently establish coverage; successful web, OpenAlex and official repository discovery did. No search is a proof of absence, especially for recent releases. Unindexed work, alternate titles, inaccessible supplements, updated checkpoints and untested dependency permissions remain plausible gaps. The 24 cards exceed a minimum floor; they are not a census or a claim of publication readiness.
