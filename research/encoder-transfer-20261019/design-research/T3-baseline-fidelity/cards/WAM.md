# WAM: faithful released implementation and two detectors

Inspected 2026-10-19. Extend dossier `Sander2025WAM.md`. [Paper v2](https://arxiv.org/html/2411.07231v2) §§3–5, Eq1–2, §5.3, Appendix G.3/Table9 are V2, reread for this adapter decision. Official release pinned to [2c08af04d037d5667c02f6ddebbda9ff04581c3e](https://github.com/facebookresearch/watermark-anything/tree/2c08af04d037d5667c02f6ddebbda9ff04581c3e).

Use the existing `research/journal-upgrade-20261009/wam-download.json`: SA-1B MIT checkpoint [wam_mit.pth](https://dl.fbaipublicfiles.com/watermark_anything/wam_mit.pth), 377,825,938 bytes, SHA256 `90ef232384e023bd63245eb0c131abd69d2afc7b8f17a71ccedceb542bf009e2`. Do not substitute the differently licensed COCO checkpoint. Source archive SHA256 `7baaa18c6774d1397207b262cd077f588150e846fada9c7c7b5ce7d0239ef0b6` is inherited from that manifest; no new weights/source archive downloaded.

## Native parameters and preprocessing

`checkpoints/params.json`: nbits32, scaling_w2.0, scaling_i1.0, img_size256, img_size_extractor256, vae_small embedder, sam_base extractor, JND `jnd_1_3_blue`. Use one full-image message, not DBSCAN/multiple watermarks. No tuning or quality_w0p5 arm is part of this core.

RGB512 -> ToTensor [0,1] -> ImageNet normalization mean[.485,.456,.406], std[.229,.224,.225]. `Wam.embed` internally bilinear-resizes to256, generates residual, resizes residual back to512 with antialias=True, and blends with native JND and scales. `Wam.detect` internally bilinear-resizes normalized input to256, returns B×33×256×256 logits. Pin torchvision behavior; do not apply an external 256 PIL resize instead.

Native README saves unnormalized image through `torchvision.utils.save_image`, which clamps after multiply255/add.5 and converts to uint8. Existing `journal_wam_probe.py` uses np.rint; this differs at exactly half-integer ties. For the new experiment use the official saving rule consistently and score reopened RGB PNG. The existing historical probe remains untouched and is not the new arm's output.

## Native detection is not nonempty mask

Paper Eq1 defines s_det as the fraction of pixels passing a pixel threshold. §5.3 flags a whole image if **s_det > .07**, described as approximately matching a theoretical 2.6e-4 bit-null FPR; Table 2a actually reports 0.04% empirical FPR on COCO. Use released README's pixel threshold **sigmoid(mask_logit) > .5** and strict image threshold >.07, reporting the raw fraction. Neither mean mask confidence nor any-positive-pixel is the native image-level detector.

**Calibration qualification:** the paper's experiments use COCO-trained weights; the frozen arm is MIT SA-1B. Applying (.5,.07) is a transferred published operating rule, not proof that the SA-1B release achieves the paper's FPR. Report observed C0 false positives and intervals. No held-out training pixels are accessed or calibrated here. Native localization/presence and known-message recovery are different endpoints.

## Decoder fidelity and paper/code discrepancy

`README.md:139–145` applies sigmoid only to mask logits, then passes **raw bit logits** into `msg_predict_inference`. Pinned `watermark_anything/data/metrics.py:150–195`, default semihard:

- select pixels whose supplied mask probability is >.5;
- average each raw bit logit across selected pixels;
- output true iff that average is **>.5** (not >0).

Paper Eq2 instead describes averaging bit probabilities and thresholding at .5. Preserve the released-code rule as the native implementation, record the discrepancy explicitly, and do not silently apply a sigmoid to bit logits or change the threshold. The current `journal_wam_probe.py` follows the pinned README's raw-logit semantics, despite the surprising threshold. The optional `threshold` argument is not used by semihard's final comparison; passing threshold=0 does not fix/change it. Empty masks must yield explicit abstention, decoded_message=null, presence false, common presence false; otherwise the upstream NaN comparison can manufacture an all-zero decoded message.

The current adapter's strict tensor state_dict loading, ImageNet preprocessing, Wam construction and unused Identity training augmenter are suitable. Add native image presence >.07, integer agreeing-bit count, common presence, exact-message recovery, independent random wrong-message schedule, and explicit empty-mask abstention. Its existing `native_mask_nonempty_diagnostic` is correctly diagnostic only, never a calibrated detection result. Preserve FP32 inference and finite output checks.

## Common operating point

For a decoded native32 message, common presence = at least **27/32** matches (one-sided exact Binomial tail 0.00005653710104525089). This tests agreement with the known per-source message; no registry matching is given to WAM. Do not require native image detection additionally for this endpoint: native zero-bit presence is reported separately. Empty-mask abstention fails both. The theoretical tail assumes a uniform independent candidate message under null; observed C0/wrong-message results remain mandatory and correlated seed/image calls are not independent FPR trials.

## Published regeneration evidence

Table9 reports WAM bit accuracies100.0/99.4/71.3/49.1% at DiffPure recovered-image PSNR30.1/28.4/27.0/24.9 dB; VAE attacks100.0/99.8/98.6/53.7% at32.9/32.4/28.6/25.5dB. These are bit accuracies for the paper model, not TPR for the released MIT checkpoint or SDXL strength.2. The same table's TrustMark DiffPure accuracies100.0/98.3/74.9/54.3% demonstrate why ordinary-distortion robustness cannot stand in for regeneration survival.










<!-- STAGE1B DEEPENING -->

# WAM: inspected method and evaluation

Evidence level **V2**. Inspected 2026-10-20; post-hoc eligibility is established in the method below. This is literature evidence, not a local outcome or execution approval.

## Source identity and inspected sections

Exact title: **Watermark Anything with Localized Messages**. Version/date: arXiv:2411.07231v2 [cs.CV] 22 Jul 2025. Venue: ICLR 2025; inspected arXiv v2 is the evidence version.

Authors: Tom Sander; Pierre Fernandez; Alain Durmus; Teddy Furon; Matthijs Douze. Year: 2024. DOI: not established for this inspected version.

Stable ID: `arxiv:2411.07231v2`. Citekey: `T3WAM2411`. Canonical URL: https://arxiv.org/abs/2411.07231v2

Primary full text: https://arxiv.org/html/2411.07231v2

Cached text: `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/q1-research-20261018/cache/T3b/wam-reused.txt`
SHA-256: `24ec9c24afc63108df55aaf207b5bab90a4d3b55dc6c8eaf32a240e7ecbdeb1d`

Actually inspected: Method §§3–4, Eqs. 1–2; evaluation §§5.1–5.3; Appendix G.1–G.3, Table 9; pinned README, params.json, embed/detect and metrics.py.

Full source and official-code cache hashes/URLs are in [deepening-manifest.json](../deepening-manifest.json); earlier release/weight metadata is retained in [manifest.json](../manifest.json). A cached abstract or repository listing alone does not establish V2.

## Mechanism and post-hoc applicability

A message-conditioned autoencoder writes a residual; a ViT-based extractor predicts one mask logit and 32 message logits per pixel. Full-image single-message embedding is the relevant post-hoc use. Localization and several messages are additional capabilities, not owner authentication.

## Native operating point and detector side information

Native released MIT SA-1B model: 32 raw bits, processing size 256, scaling_w=2.0, scaling_i=1.0 and JND jnd_1_3_blue. RGB input at 512 is ImageNet-normalized; internal bilinear resizing and antialiased residual upsampling preserve the original image. The paper trains on COCO with alpha=.3 and high-resolution JND scaling; those weights differ from this release. Pixel mask uses sigmoid >.5; paper image presence is mask-positive area >.07, described as approximately matching a nominal 2.6e-4 bit-null target; empirical COCO FPR in Table 2a is 0.04%. Released README passes RAW message logits to semihard aggregation: select mask >.5, average logits, then compare the average >.5. This differs from averaging probabilities in paper Equation 2; retain the released behavior. An empty mask is an abstention. Official save_image multiplies by 255, adds .5, clamps and converts to uint8. Common known-message presence uses at least 27/32 matches (analytic fair-query tail 5.6537101045e-5); this is a separate endpoint and must not be conjoined with the native image detector. COCO calibration does not automatically transfer to SA-1B weights.

## Code, weights, pinned release and licenses

Official facebookresearch/watermark-anything@2c08af04d037d5667c02f6ddebbda9ff04581c3e; MIT code and chosen SA-1B checkpoint. https://dl.fbaipublicfiles.com/watermark_anything/wam_mit.pth is 377825938 bytes; inherited metadata SHA256 90ef232384e023bd63245eb0c131abd69d2afc7b8f17a71ccedceb542bf009e2. Source archive SHA256 7baaa18c6774d1397207b262cd077f588150e846fada9c7c7b5ce7d0239ef0b6. No new binary download. COCO-weight licensing is distinct and those weights are not substituted.

## Published evaluation and regeneration conditions

Primary Table 9, Appendix G.3: DiffPure attack PSNR 30.1/28.4/27.0/24.9 dB corresponds to bit accuracy 100/99.4/71.3/49.1%; VAE attack PSNR 32.9/32.4/28.6/25.5 corresponds to 100/99.8/98.6/53.7%. These are bit accuracies, not TPR at our threshold. The appendix does not specify enough to reproduce model revision, diffusion strength/noise schedule, sampler, prompt, exact evaluation count or every attack resolution; do not infer them from the main 10,000-image COCO/DIV2K evaluation. These curves use COCO weights. VINE and SpreadMark comparisons use different payload, quality and attack conditions; they do not establish this release's R1 outcome.

## Cost and uncertainty

The paper reports approximately 1.1M embedder and 96M extractor parameters. Checkpoint size is storage, not peak VRAM. Inference needs an embedder and a ViT forward; target-server time and memory remain unmeasured. The core cost remains within the parent budget; this is not a new timing claim.

## Limitation and design implication

Maintain separate native mask-presence, common queried-message presence, exact recovery and clean quality columns. Do not silently fix the paper/code threshold discrepancy. Preserve native quality; no outcome-based residual scaling.

Disposition: **Core: already user-approved; no new arm.**
