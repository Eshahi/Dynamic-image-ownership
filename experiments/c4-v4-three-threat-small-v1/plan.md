# Small v4 study of the three proposal threats

This prospective exploratory study tests unchanged v4 as an image-domain comparator, not latent embedding or legal ownership. It applies research/research-contract.md and research/scope-guard.md and is linked to issue18 and draftPR67. Prior v2 outcomes and v4 synthetic results are known; no new study outcomes have been inspected. The original proposal, 38-task plan, 35dB/.9/.1 quality goals, native2K and 6900-source obligations remain unchanged.

## Method and inputs

Use the public-derived profile only. Freeze target42dB, semantic energy share.6, design noise8, three passes, alpha1e-6 and both32-bit radii6. The only example-profile change is semantic_source=external:clip-vit-b32-a6-40d365715913. This uses the existing pinned512-dimensional CLIP ViT-B/32 embedding, L2-normalized with the official224-pixel transform. Proxy features are forbidden. No keyed-profile adoption or secret is implied.

Canonicalization remains native EXIF/ICC to RGB8 then512square BICUBIC, saved/reopened PNG. Clean/T5 use the already approved twelve local COCO development IDs; T3/T4 use the original ten. Reuse the frozen66pairlabels, not the old method's scores. Rights restrictions and raw hashes remain those of the existing cohort files. No new data acquisition or held-out unlock occurs.

The embedding wrapper keeps internal source-feature verification as diagnostic only. It calls strict=False to retain returned pixels even on failed self-verification, saves/reopens those pixels, recomputes CLIP on them and obtains the authoritative suspect-only detection. Failure outputs remain measured; descendants of failed embeddings are declared prerequisite failures, never dropped or replaced. Detector inputs are suspect luminance, claimed public owner, pinned profile and CLIP of that same suspect. No reference/source embedding/semantic label enters the detector.

## Fixed inventory

| Axis | Rows | Detector calls | Knowledge |
| --- | ---: | ---: | --- |
| Clean C0/C1 on12sources | 24 | 96 | Four fixed owner claims with roster_size4 |
| T3 on10sources | 260 | 1040 | Four owners on each C0/C1 output |
| T4 on20directed donor recipient pairs | 180 | 720 | Intended owner with four binding modes |
| T5 component pairs | 66 | 0 | Evaluator only |
| T5 same-semantic projection transfers | 7 | 28 | Intended owner with four binding modes |
| Total | 537 | 1884 | Internal embedding checks reported separately |

For all T4 and T5 transfers the four modes are combined, semantic_only, perceptual_only and none on identical saved output pixels. Mode changes do not create independent samples. Clean/T3 use combined only. Claimed owners are the fixed alpha/beta/gamma/delta roster from the existing pilot; wrong-owner-590 is not carried forward as a current-owner collision.

## Regeneration dose response

Twenty deterministic VAE-mode round trips are C0/C1 for10sources. Encode latent_dist.mode(), decode the same unscaled latent, use the intact pipeline safety checker and normal postprocessing; no diffusion/noise/prompt/seed is involved. Do not mislabel this as strength0 or sample the latent distribution.

Diffusion outputs are10sources x2controls x4strengths(.05,.1,.2,.4) x3seeds(0,1,2)=240. Retain the already pinned local SD1.5fp16 pipeline and explicit DDIM20/eta0/guidance1/empty positive and negative prompts. Fresh CUDA generators with equal paired C0/C1 seeds; no outcome-guided tuning/retry. VAE posterior sampling is part of this pipeline, distinct from the mode round trip. Safety failures and missing C0s remain in the planned denominator. No bypass of the checker or model downloads.

For every saved output measure source CLIP cosine, RGB PSNR/SSIM/LPIPS against both immediate input and original canonical source. CLIP>=.90 is only a numeric retention screen; two independent principal-content assessments are still necessary. Model boundary expectation: v4 is hand-crafted image-domain watermarking and may fail regeneration, including VAE alone. This expectation cannot determine its measured verdict.

## Copy paste and stronger public transfers

Keep20fixed directed edges from the original ten sources (offset1 and5). Central patches128/256 yield40publicmarked and40unmarkedsham attempts. Clean-donor residual scales.5/1 yield40stronger-access attempts, with separate reporting. Do not pool public-patch and access-to-clean-donor evidence.

Add20fullcarrier-band copies,20unmarkedbandshams and20publicprojection transfers. Band copies replace only the twelve carrier positions; DC and the two descriptor-detail positions remain untouched. Projection transfer copies the donor's observed640public projections into the recipient's public carrier, with three predetermined quantization-correction passes and no detector/metric selection. It is a method-aware, zero-query, single-target transplant using marked donor and unmarked recipient; it is not fresh victim re-embedding/T6. Public carrier knowledge is explicit. Delivery is measured afterward using watermark_found and binding_mode=none, not merely present.

All attacks share native clipping/quantization specified by their constructor and savedRGB8 measurement. Numeric admissibility is recipient PSNR>35/SSIM>.9/LPIPS<.1; two content assessments remain separate. Weak or inadmissible delivery cannot establish content-binding resistance. Record attack cost, delivered keys, continuous channel scores, all outcome states and successful false attribution.

## Semantic collision

Attack timing includes input reads, construction/model inference and saving for each successful attack. Failed attempts retain errors but have no complete construction-cost measurement. Detector cost includes fresh CLIP extraction: a standalone owner claim costs CLIP plus that detector call; a cached four-owner roster costs CLIP once plus all four calls. Report both conventions, and keep embedding internal-verification time separate. No detector cost is reported as end-to-end without CLIP.

Reuse7same/2uncertain/57different labels frozen before this experiment. Measure source and marked q/H distances, CLIPpaircosines and same-instance drift. Count q/H near-collisions at frozenradius6, exact collisions, joint collisions and conditional H separation among near-q pairs. These are dependent component diagnostics, not full detector accuracy.

Each of the7same pairs gets one directed publicprojection transfer (lowerIDtohigherID) with the four modes. This tests binding on actual delivered marks, separately from code-distance counts. If fewer than5same pairs have q-distance<=6, semantic-near-code coverage is insufficient; do not expand/tune the cohort after scores. Uncertain pairs remain separate.

## Analysis and claim limits

Unit is source group or directed pair; seeds/modes/pairs sharing a source are correlated. Give planned/completed/failed counts, raw per-source/per-seed outcomes and descriptive mean/median/SD/range. No p-values, superiority, pooled accuracy or population FPR; no unplanned seed bootstrap with3seeds. Missing evidence blocks support. T3reports watermark_found, semantic.found+content_match, instance state, both_match and ground-truth classifier confusion separately. semantic_only is an observation, not proof of regeneration.

The codec's log10_false_positive_bound is conditional/unvalidated here. Fixed public patterns, adaptive image/helper-derived codes and either-channel union events lack an established unconditional FPR guarantee. Report nominal thresholds unchanged and empirical C0/C2counts; do not assert FPR<=alpha or attack complexity1/alpha². Existing amendment text is historical author material, not accepted statistical certification.

## Execution boundary

Fixed batch only, local existing Windows workflow Python and pinned WSL scientific runtime. Planning envelopes6GiBRAM/8GiBVRAM,2GiBdisk,$0;86400seconds is an operational watchdog, not a user time deadline or a measured runtime forecast. Estimated1to6hours is provisional and not a promise. The prior batch peaked at3.89GiB RSS; current host freeRAM was6.90GiB, WSL MemAvailable14.50GiB and freeVRAM10.63GiB. Check availability again before dispatch; polled guards are not OS allocation caps. No downloads/installs/paidcompute/publicpush, profile tuning or historical-run retry.

Finalize exact clean commit, code/runtime/asset/raw-input hashes, model-free tests and bounded independent whole-package review before making a manifest-specific execution decision. Official controller remains paused; do not fabricate gate acceptance or reuse prior consumed authorization. Design is not execution approval.
