# Method amendment v2: robust image-domain ownership candidate

Status: **engineering amendment and falsifiable candidate, 2026-09-29**. This file records the requested algorithm correction. It does not rewrite the original proposal, claim ledger, A5 `method-spec.md`, or the latent/noise candidate. The original route remains an explicitly labelled comparator and negative-feasibility branch until a separate gate decision changes that status.

The current A5 candidate is not an operational algorithm: no image-level embed/detect implementation, model-gradient check, weight receipt, or end-to-end result exists. More importantly, its central inference is unsupported: a shared seed between a latent carrier and an image-DCT template does not imply a useful transfer through a nonlinear diffusion decoder. Whole-code SHA-256 signatures also cause a complete template jump after one bit changes. The amendment removes both failure modes from the runnable candidate.

## What changes

| Existing candidate | Amendment v2 | Reason |
| --- | --- | --- |
| Initial diffusion-noise carrier optimized through an unmeasured latent-to-DCT bridge | Direct image-domain block-DCT QIM with a fixed, auditable detector | The embedder and detector operate in the same coefficient domain; no unproved bridge is needed. |
| SHA-256 of the complete semantic and perceptual code | Bit-level payload with repeated owner tag and perceptual binding | A local bit error does not replace the entire template. |
| 13 x 33 candidate-key enumeration per owner | One deterministic codeword and majority decoding | Removes candidate explosion and makes false-match calibration explicit. |
| Centered random correlation against host coefficients | Quantization-index modulation (QIM) in six mid-band coefficients per 8x8 block | QIM gives a direct decision margin at the decoder and a simple distortion control. |
| Diffusion/VAE/CLIP required for every verification | Verification uses the decoded image, OwnerID and public configuration | Runtime is independent of a diffusion checkpoint. A CLIP semantic feature can remain a separately reported binding feature. |

This is a material method change. It can be used as a practical candidate and a positive control for the proposed image-domain detector, but results must not be reported as validation of the latent/noise hypothesis. Claims about regeneration robustness, legal ownership, or cryptographic authentication remain unsupported until their own evidence exists.

## Comparable-work screen

The repository’s inspected source cards were used to choose the correction boundary. SEAL v4 combines semantic/caption-derived information with an inverse-diffusion detector; its inspected mechanism does not establish a latent-to-blind-DCT bridge. InvisMark uses a learned residual and a ConvNeXT decoder and is therefore a useful neural comparator, but its reported behavior cannot be transferred to this codec without a controlled reproduction. The inspected regeneration work reports conditional removal/utility bounds, not a guarantee that a watermark survives arbitrary regeneration. A metadata-only public-source screen also identified *Watermark Anything with Localized Messages* (arXiv:2411.07231, 2024) and the 2023 deep-learning watermarking survey (DOI:10.3390/app132111852) as relevant follow-up sources; these entries were not treated as reproduced performance evidence. The amendment takes the narrower, fully auditable DCT-QIM route first and leaves learned residual/decoder training as a separately preregistered comparator.

## Algorithm

The reference implementation is [`scripts/revised_watermark.py`](../scripts/revised_watermark.py). It deliberately uses only the Python standard library so that the codec and detector can be tested before model or dataset acquisition.

1. Canonicalize `OwnerID` with Unicode NFC and UTF-8. Derive a 48-bit public owner tag from `SHA256("rw-v2/owner/" || owner_bytes)`. This is attribution under a public derivation, not authentication: anyone who knows an OwnerID can reproduce the tag.
2. Compute a 16-bit low-frequency perceptual binding from pairwise comparisons of padded 8x8 block means and retain its most significant 12 bits. Because the payload changes only non-DC DCT coefficients, this binding is stable for admissible low-texture images up to the declared clipping policy; truly flat images are rejected for lack of luminance headroom. The payload is `version(4) || owner_tag(48) || perceptual_binding(12) || CRC8(8)`, for 72 logical bits.
3. Pad only the right and bottom edges to an 8x8 block grid. Compute an orthonormal 8x8 DCT on luminance. Use six fixed mid-band positions `[(1,2),(2,1),(2,2),(1,3),(3,1),(2,3)]`; the DC coefficient is never modified.
4. Assign every coefficient slot to `payload_index = slot_index mod 72`. Each logical bit is therefore repeated across all available blocks. A domain-separated SHA-256 carrier sign, derived from image dimensions, block coordinates, frequency and payload index, is XORed with the bit before QIM. The carrier is public and is used for spreading/synchronization, not secrecy.
5. For coefficient `c` and QIM step `Delta`, select the nearest quantization point `q*Delta` whose integer index parity equals the carrier-adjusted bit. The default candidate step is 4.0 coefficient units; it must be calibrated against the actual codec, image domains and quality targets before a scientific run.
6. Decode the saved output, recompute the same DCT, undo the carrier parity, and majority-vote each payload bit. Validate the version and CRC, compare the decoded owner tag with the claimed OwnerID, and compare the decoded 12-bit perceptual binding with the current image. The detector returns raw accuracy, binding distance, CRC state, dimensions and a boolean decision. Thresholds in the prototype are engineering smoke thresholds, not preregistered study thresholds.

The minimum working side is 160 pixels so that each payload bit has at least three repeated coefficient slots. A source-wide luminance range below 8 levels is rejected because a non-DC mark cannot be inserted into a flat black/white field without clipping; that rejection is a recorded processing failure, not a silently successful mark. Blocks whose candidate modification exceeds the declared clipping tolerance are also rejected. Real image I/O must apply the project’s canonical orientation, color and PNG round-trip policy before calling this codec. RGB input is converted to sRGB luminance; the current standard-library reference accepts a luminance matrix to keep the numerical contract dependency-free.

## Why this is a correction

The old design asked an optimizer to make an output DCT correlation large while the detector regenerated a discontinuous hash-derived template from the output. That allows the optimizer to improve a continuous oracle score while the final encoded image changes the code used by the real detector. The amendment puts the payload directly in the statistic being decoded and uses a local error-tolerant representation. A future PNG wrapper must pass the saved, decoded pixels to this reference detector so quantization is part of the test rather than an unmodelled post-processing step.

The direct codec also provides a necessary diagnostic split. If this positive-control path cannot separate C1 from C0/C2 at acceptable distortion, the detector/statistic or calibration is inadequate. If it succeeds while the latent path fails, that is evidence against the latent-to-DCT bridge under its tested conditions, not evidence for a different scientific claim.

## Controls and limits

- C0 is the unmarked image and its codec round-trip. C1 is the marked output with the enrolled OwnerID. C2 uses the marked output with a wrong OwnerID. C4 uses a different image with the same claimed OwnerID. All failures remain in the inventory.
- The first implementation test covers deterministic output, wrong-owner rejection, rejection of a marked image after a large content replacement, low-headroom failure, and small integer pixel noise. It does not test JPEG, resize, crop, regeneration, real RGB/PNG I/O, LPIPS, a learned comparator, or a locked dataset.
- The fixed 8x8 grid remains sensitive to arbitrary crop, rotation and resampling. A future synchronization extension may search a predeclared integer block phase or use a multi-scale pilot, but no transform robustness is claimed by this candidate.
- Public OwnerID and public derivation permit re-embedding. The result is a provenance/matching experiment under the declared threat model, not a proof of ownership or an authorization mechanism. A secret-key or signed enrollment variant would be a separate security amendment.
- The 12-bit content binding is deliberately smaller and error-tolerant than the previous avalanche-prone whole-code hash. It must be evaluated for collision and false attribution on the locked domains; the implementation does not invent those measurements.

## Evidence and next gate

The local literature review supports using learned residual/decoder methods such as InvisMark as a comparator and records that SEAL’s inverse-diffusion detector does not establish the latent-to-image-DCT bridge. Those observations motivate the correction but are not performance evidence for this codec. The next scientific package must freeze the image manifest, codec step, output encoding, owner roster, quality margin, FPR/TPR endpoints and attack transforms before any held-out run. A bounded independent review is required for acceptance of this exact amendment; no compute or plan gate is advanced by this document.

