# GS native versus terminal-sign readout: completed synthetic pilot

Exploratory B/B-LW1 evidence, 2026-10-04. Both detectors found the reference
message at the predeclared cutoff on all four C1 images in every declared
channel. The direct terminal-sign reader passed its clean and VAE carrier
screens, despite lower exact-message recovery than inversion. This supports a
bounded next design step; it does not complete the proposal, validate existing
photo preservation, prove content binding, or exhaust another design family.

## Inventory and mechanism

The completed native run `20261004-0000-gs-native` at
`6a46faad51d91b285d00bbb6b2a4563ef681c11b` contains all 112 planned condition
rows and 120 receipted PNGs (eight originals plus conditions), with 339.484 s
total duration. The separate completed reader run `20261004-0010-gs-lightweight`
at `8809c8d5dad67edfc83b914516dccbbf7fdbca58` evaluated the same 112 images in
18.844 s. Paired analysis `20261004-0012-gs-paired-analysis` at
`dc012fbc6a466f017fb3d837506ed1a0a8b079c6` is completed descriptive analysis;
both input analyses are complete with no recorded provenance errors or missing
cells. This report reads their saved JSON metadata, not images or models.

Four independent synthetic prompt/seed clusters are mountain lake (prompt-0,
1000), city street (prompt-1, 1001), fruit bowl (prompt-2, 1002), and dog/beach
(prompt-3, 1003). Each has paired C0/C1 generations with shared absolute Gaussian
noise magnitudes. C1 signs encode a 256-bit message repeated 64 times across
16,384 initial-noise coordinates, whitened by keyed/nonce SHAKE256 XOR. Sampling
is pinned SD1.5 fp16 DDIM, 50 steps, CFG7.5, eta0. This adapts Gaussian Shading;
it differs from the paper's model pins, cipher and legacy inverse implementation.
The source/adaptation details remain in `research/m1-gs-adaptation.md` and the
inspected primary-paper card under `research/literature/m1-latent-survey/`.

Native detection uses posterior-mode VAE encoding and 50 empty-prompt,
CFG1 DDIM inverse U-Net evaluations. B-LW1 uses one pinned VAE encode, scaled
terminal posterior mode, coordinate signs, the same dewhitening, and strict
64-chip majority (>32; ties decode zero). It uses no inversion, U-Net or text
encoder. Both receive the enrolled key and per-image nonce; extracted bits are
compared to the evaluator-only reference message. Presence is >=180/256
agreement (native fixed accuracy cutoff .7); exact means 256/256. These are
message-agreement screens, not blind recovery from public OwnerID.

Channels are saved clean images, one deterministic VAE cycle, and SD1.5
img2img empty prompt/CFG1/DDIM20/eta0 at strengths .05/.1/.2/.4 with seeds0/1/2.
The 20-step base schedule yields only 1/2/4/8 effective img2img denoising steps,
respectively. This bounded regeneration threat does not establish survival of
arbitrary regeneration, cross-model attacks or stronger prompt-guided edits.
Safety checks remained in the native generation/attack pipeline.

## Complete channel results

Every row below has C1 presence **native 4/4, LW 4/4**, C0 correct-key positives
**0/4 for each detector**, C1 wrong-key positives **0/4 for each detector**, and
C0 wrong-key positives **0/4 for each detector**. Missing counts are zero.
Individual match vectors are ordered prompt-0,1,2,3; divide by 256 for the four
individual accuracies. Means are accuracies, not a pooled subject-level TPR.
All paired C1 presence tables are both=4, native-only=0, LW-only=0, neither=0.

| Channel | Native matches /256, four clusters | LW matches /256, four clusters | Native mean accuracy | LW mean accuracy | Native exact /4 | LW exact /4 |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| clean | 256,256,256,256 | 237,256,254,256 | 1.000000 | .979492 | 4 | 2 |
| VAE | 256,256,256,256 | 240,256,253,255 | 1.000000 | .980469 | 4 | 1 |
| .05 seed0 | 256,256,256,256 | 239,256,252,255 | 1.000000 | .978516 | 4 | 1 |
| .05 seed1 | 256,256,256,256 | 238,256,254,256 | 1.000000 | .980469 | 4 | 2 |
| .05 seed2 | 256,256,256,256 | 239,256,253,255 | 1.000000 | .979492 | 4 | 1 |
| .1 seed0 | 256,256,256,256 | 231,256,249,253 | 1.000000 | .965820 | 4 | 1 |
| .1 seed1 | 255,256,256,256 | 225,256,247,251 | .999023 | .956055 | 3 | 1 |
| .1 seed2 | 256,256,256,256 | 224,256,252,254 | 1.000000 | .962891 | 4 | 1 |
| .2 seed0 | 249,256,254,256 | 224,256,244,247 | .991211 | .948242 | 2 | 1 |
| .2 seed1 | 247,254,252,256 | 220,256,241,249 | .985352 | .943359 | 1 | 1 |
| .2 seed2 | 251,256,253,256 | 222,253,249,251 | .992188 | .952148 | 2 | 0 |
| .4 seed0 | 230,250,243,243 | 206,251,235,226 | .943359 | .896484 | 0 | 0 |
| .4 seed1 | 227,243,239,247 | 199,248,232,235 | .933594 | .892578 | 0 | 0 |
| .4 seed2 | 231,248,241,246 | 202,248,234,228 | .943359 | .890625 | 0 | 0 |

Each regeneration strength has 12/12 repeated C1 presence outcomes for each
reader, but still only four prompt clusters. At .4 neither reader exactly
recovers any of the 12 repeated messages. The lowest LW agreement is 199/256
(.777344), prompt-0/.4/seed1, 19 bits above the cutoff. Prompt-1 can favor LW:
its .4 scores exceed native by 1,5,0 bits. Native is therefore not assumed better
on every image. Per-image differences remain in
`gs_lightweight-paired.csv`, including C0; vectors above also expose every C1
difference without selecting favorable cases.

For transparency, averaging all 14 prespecified channels within each cluster
gives the following exploratory summaries. This equal-channel descriptive
average was calculated for reporting, not an acceptance rule or a planned
significance test. There is no bootstrap or superiority inference with four
clusters.

| Cluster/seed | Native within-cluster mean | LW within-cluster mean |
| --- | ---: | ---: |
| prompt-0 /1000 | .971540 | .877790 |
| prompt-1 /1001 | .991908 | .993304 |
| prompt-2 /1002 | .984933 | .962333 |
| prompt-3 /1003 | .991071 | .968471 |

Across these four cluster means: native mean=.984863, median=.988002,
sample SD=.009411, range=.971540–.991908; LW mean=.950474, median=.965402,
sample SD=.050272, range=.877790–.993304. The pronounced cluster variation is
retained, not hidden by the 112 repeated conditions.

## Latency, quality and controls

Across 112 saved-image timings, native extraction mean/median/range is
2.185464/2.187000/2.140000–2.265000 s; LW encode+transfer+both-key decoding is
.053589/.047000/.046000–.453000 s. LW first call is .453 s on prompt-0 C0
clean. The remaining 111 timings have mean=.049991, median=.047000,
range=.046000–.063000 s. Ratios of measured means and medians are approximately
40.8 and 46.5, descriptive implementation observations on this GPU/runtime.
Native performs 50 U-Net evaluations per image; LW records one VAE encode,
zero U-Net and zero text-encoder evaluations. LW model load is .187 s. Timings
do not include all file verification, model startup or full run overhead; the
339.484 s native total includes generation and attacks, so dividing run totals
is not an extraction speedup. The reader is lightweight relative to inversion,
but still requires a GPU VAE here; no CPU latency or image-DCT implementation
was measured. Scaling introduced zero recorded sign changes over all images.
Four reconstructed fp16 source-noise selfchecks each recover 256/256; these
are deterministically reconstructed inputs, not retained original tensors.

The C1-versus-C0 clean generation comparisons are:

| Cluster | PSNR dB | SSIM | LPIPS |
| --- | ---: | ---: | ---: |
| prompt-0 | 9.575064 | .287237 | .782653 |
| prompt-1 | 8.401624 | .086309 | .630566 |
| prompt-2 | 8.497531 | .126973 | .704777 |
| prompt-3 | 11.023477 | .065526 | .800894 |

These are different generated counterfactuals, not watermark distortion of an
existing photograph; their strict quality conjunction is 0/4. Preserving
Gaussian noise marginals does not imply a fixed-seed image is unchanged. Attack
quality is separately referenced to the same-arm clean generation. C1 attacked
CLIP cosine exceeds the prespecified .85 semantic-retention proxy for every
channel; the smallest recorded value is .944977 at .4/seed1. This is an
evaluator proxy, not a human judgment. No existing-photo quality claim or
human visual verdict is available.

The largest observed C0 correct-key match count is 145/256 and largest wrong-key
agreement across both detectors/arms/channels is 150/256. These finite controls
do not establish a population FPR: zero positives among four clean C0 images
still gives a one-sided 95% binomial upper bound of about .527 under independence.
Repeating channels or querying the same images with another key does not create
new independent clean controls.

## Public-key erratum and scientific limits

The run uses deterministic keys published in the development manifest. The
native run's historical detector-side-information phrase "secret whitening key"
is retained unchanged in source metadata and corrected by this report.
References to a "secret" or "wrong secret" in older descriptions are only
fixture/query names and must not imply secrecy. No cryptographic security or
unforgeability follows from this public SHAKE whitening. Both decoder paths
also use enrolled nonce and evaluator message information. An attacker with
these fixtures can re-embed a known message; message presence alone cannot
authenticate origin or content. This corrects interpretation without changing
the frozen codec, cutoff or retained measurements.

Capacity is 256 distinct message bits, each repeated 64 times, not 16,384
independent identity bits. Most channels do not preserve an exact 256-bit
message under LW; no error-correcting outer code or reliably transported
signature capacity was measured. A presence threshold tolerating up to 76
errors is not a measurement of cryptographically verified payload recovery.
Strict-majority tie-to-zero creates an ideal fair-chip decoded-one probability
.4503266; the fixed-payload conditional tails documented in the prospective
diagnostic are arithmetic references, not measured real-image/public-forgery
FPRs. No post hoc cutoff or readout tuning occurred in this comparison.

The favorable native clean results validate this local baseline's clean codec
and inversion sufficiently for the declared attack comparison. The LW results
show that some message agreement survives in directly encoded terminal signs
on these four generations. They do not explain all causal transport or establish
universal capacity. The published latent method still differs from this SD1.5/
SHAKE/current-diffusers adaptation. B-LW1 contains no CLIP semantic signature,
DCT perceptual-hash binding, OwnerID signature or three decision states. T4
copy-paste localization and T5 semantic collisions were not tested. A content-
bound generated-image method or existing-photo enrollment would require a
separately frozen design and development evaluation. Passing these carrier
screens warrants that design work; it is not a protected-plan amendment,
method acceptance, confirmatory result or family-exhaustion judgment.

## Reproducible metadata provenance

All paths below are under MAIN `.thesis-build/dev-runs/`. The paired analysis
retains source manifests, source commit/config/errors, copied native snapshot
receipts, image hash joins and LW output hashes. Source artifacts remain
unmodified. Analysis input hashes and condition inventories are available in
`20261004-0012-gs-paired-analysis/run.json` and `analysis.json`.

| File | SHA256 |
| --- | --- |
| 20261004-0000-gs-native/run.json | d4679d013ecd97cf14951f328d90b01e21a09754e3d74a55c6b5624fa5c524d5 |
| 20261004-0010-gs-lightweight/run.json | 55b9edf853195abbd0c282442547442266d48570d5635da98e390fc89bd8789a |
| 20261004-0012-gs-paired-analysis/run.json | da8ed7809f2be9a29d7d55715c8d22c1b25a8ecbee6648079daf3056d9f38b1e |
| 20261004-0012-gs-paired-analysis/analysis.json | 8d1b23f315b8c17c99501c56bd15076da4615837f29e622e4411956cb5c67dc0 |

No new scientific run, GPU call, source-output edit, threshold selection or
held-out inspection was performed to write this report. Human verdict remains
missing. The report uses the preservation and cluster-counting principles of
the `thesis-results-analysis` skill on the already completed custom family
analysis; it does not claim the official confirmatory lifecycle or infer a gate.
