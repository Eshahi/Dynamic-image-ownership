# A3: pipeline interfaces and detector knowledge

Status: **SPECIFICATION**, not implementation or experimental evidence. Source tasks: `contract-2`, `contract-3`; GitHub issue #3. Authority: `claims.csv`, `scope.md`, and `approval-policy.md`. Source: `inputs/proposal-text.md`, Table 8, lines 194-214; key symbols are cross-checked in the A1 visual-verification record. The guide's `inputs/approved-proposal.docx` input denotes the actual local `پروپوزال 2.docx` recorded in `inputs/proposal-source.json`.

This document fixes interface roles, not scientific parameters missing from the proposal. `TBD` below is an explicit downstream architecture obligation (source task `repair-4`, reduced task A5), not an executable default. A configuration with a required TBD must fail validation before scientific execution.

## Image and feature types

| Type / field | Dtype and shape | Range, units, color space | Role and authority |
| --- | --- | --- | --- |
| `Image.rgb` | float32 `[3,H,W]`; positive H,W | finite `[0,1]`, sRGB; dimensionless | A3 API convention; decode orientation/color profile explicitly, record conversions, retain source bytes/hash. No implicit resize. |
| `Image.id` / `sha256` | UTF-8 string / 64 hex characters | identifiers | Immutable source identity; separate from image content signature. |
| `I` | `Image` | as above | Input/reference content supplied before signing. Includes real photos and previously generated images. |
| `prompt` | optional UTF-8 string | text, not pixels | Generation/attack conditioning; never a substitute for `I`. Provenance only unless the pinned method requires it. |
| `E` | floating vector `[d_E]`; precision TBD | normalization/range TBD | Semantic extraction of I; checkpoint, preprocessing, layer and dimension must be pinned. |
| `H_p` | bool vector `[b_H]` | bits `{0,1}` | Perceptual code; length, internal grayscale transform/resize/coefficients TBD. Distinct from image height H. |
| `OwnerID` | canonical byte string; encoding rule TBD | public identifier | Claimed owner, not a secret or proof of legal ownership. |
| `secret_ref` | optional opaque local key identifier | never key bytes in public records | No secret is specified in the proposal. Null means the public-derived-key profile; adding a keyed profile needs an explicit research contract. |
| `W_s`, `W_i` | byte strings `[L_s]`, `[L_i]`; lengths TBD | byte values 0..255 | Semantic/instance signatures derived from features and OwnerID; hash/encoding/KDF TBD. Calling them keys does not make them secret. |
| `z`, `P_lat` | floating tensors `[C_z,h_z,w_z]`; precision TBD | latent/noise scale TBD | Model noise/state and compatible injected pattern; model contract must fix all axes and normalization. |
| `I_w` | `Image` | canonical RGB representation | Watermarked output, a new artifact with parent source identity. |
| `J` | `Image` | canonical RGB representation | Suspect/attacked image; dimensions may differ from I. |
| `C_J` | floating array `[N_blocks,8,8]` per selected channel | DCT normalization/units TBD | Image-domain DCT coefficients; channel, padding, block origin and synchronization TBD. |
| `T_s`, `T_i` | floating patterns `[N_blocks,K_mid]`; construction TBD | same scoring domain as selected coefficients | Expected image-domain detection patterns derived from candidate keys, not latent tensors reused by assumption. |
| `score_s`, `score_i` | finite real scalars | scale/sign TBD; higher-is-match convention must be explicit | Continuous scores retained for ROC; not calibrated probabilities. |
| `tau_s`, `tau_i` | real scalars | same score units | Validation-frozen thresholds; test data cannot set them. |

## Function contracts (proposed signatures)

```text
decode_image(path, io_config) -> Image
semantic_features(image: Image, semantic_config) -> E
perceptual_features(image: Image, phash_config) -> H_p
derive_keys(E, H_p, OwnerID, key_config, secret_ref=None) -> KeyPair(W_s, W_i)
latent_pattern(keys: KeyPair, latent_shape, embedding_config) -> P_lat
image_patterns(keys: KeyPair, block_layout, detector_config) -> (T_s, T_i)
image_coefficients(J: Image, detector_config) -> (C_J, block_layout)
embed_existing(I: Image, keys: KeyPair, model_config, embedding_config,
               seed: int, prompt: str | None) -> EmbedResult
detect(J: Image, OwnerID, feature_config, key_config, detector_config,
       thresholds, secret_ref=None) -> DetectionResult
evaluate(original: Image, reference: Image | None, marked: Image,
         attacked: Image | None, results, evaluation_config) -> MetricRecord
```

`EmbedResult` carries `I_w`, the exact input artifact ID, seed, configuration/model/code hashes, transformation log, and (when feasible) an unmarked model reconstruction `I_ref` produced under matched conditions. It must identify the route and output-to-input mapping. Any image returned at a different resolution requires a recorded quality-comparison alignment protocol; do not silently interpolate away distortion.

`DetectionResult` carries tested OwnerID/key-profile/config IDs, feature/candidate-key IDs (not secret material), continuous scores, threshold version, matched-component flags, outcome, diagnostic reason, and timing boundaries. Outcomes: `both_match`, `semantic_only`, `instance_only`, `neither_match`, `invalid_input`, or `unsupported_configuration`. For the last two outcomes, scores and matched-component flags are nullable and must be absent/null when not evaluated; a diagnostic reason is required. Missing required metadata produces an error/unsupported result, not a clean negative or a fabricated score. These are detector observations; `semantic_only` alone does not prove regeneration and `both_match` alone does not establish legal ownership.

## Data flow and route limits

1. `I -> E,H_p -> W_s,W_i -> P_lat -> model process -> I_w`. The injected pattern must match the chosen model tensor. The model output must decode to `Image` before evaluation/detection.
2. `I_w -> attack -> J -> E_J,H_p_J -> W_s',W_i' -> T_s,T_i`; independently `J -> selected channel -> 8x8 DCT -> selected coefficients`. Score only compatible coefficient/pattern shapes.
3. A5 must specify and test the link between `P_lat` and image-domain `T_s,T_i`. Dimensional compatibility does not demonstrate watermark survival through the diffusion decoder.
4. Real photos and pre-existing generated images use `embed_existing`; the image-conditioned/inversion/reconstruction mechanism remains `BLOCKED_DECISION(A5)`. An unrelated prompt-generated output does not satisfy preservation of the supplied image.
5. Prompt-only fresh generation is a separate unresolved route: the proposal derives keys from an image before embedding, so the signed content must be defined before generation. Do not invent a two-pass signing algorithm or sign the final image after the fact and call it initial-noise embedding. This branch cannot execute until A5 resolves the order and its claim implications.
6. Enrollment stores source/output/config references for evaluation. It is not an ownership-transfer registry. No transfer/ledger API is required under the current approval policy.

## Detector knowledge and evaluation separation

| Information | Proposal-faithful core detector | Evaluator / diagnostic alternative |
| --- | --- | --- |
| Suspect image J | Required | Required |
| Claimed OwnerID | Required explicit input, public | Ground truth can identify valid/wrong owners. |
| Original image I or enrollment features | Not supplied to the core recomputation route | Evaluator may hold I; an enrollment-reference detector must be labeled a separate diagnostic/baseline, not the proposal method. |
| Original keys | Not supplied; recompute candidates from J | May be used for an oracle diagnostic only, with separate results. |
| Prompt, seed, generator checkpoint | Not detector inputs | Evaluator stores them; an inversion baseline may require its own disclosed inputs. |
| CLIP/feature extractor and pHash definition | Required | Their cost is part of end-to-end verification. |
| Diffusion decoder / inversion | Not required by the intended DCT detection path | Baseline-specific; if the proposed method needs it, report a method deviation. |
| Secret | None in public-derived profile | Any keyed variant must define access, independent key controls, and costs separately. |
| Detector configuration/thresholds | Required, frozen versions | Validation chooses thresholds; evaluation consumes fixed values. |

The intended detector is inversion-free, not model-free: semantic extraction uses a pretrained model. Time both the complete verification pipeline and a separately labeled DCT-only component; do not compare component-only latency against a full baseline.

## Blocking technical choices and failure behavior

| ID | Missing item | Dependency and handling |
| --- | --- | --- |
| IO-01 | E dimensions/normalization and pHash preprocessing/length | A5; reject incomplete feature config. |
| IO-02 | Stable quantization/matching, serialization, hash or keyed profile | A5 and later key tasks; hashing nearby floats does not establish stable candidates. Measure original-to-marked and benign-edit stability. |
| IO-03 | Existing-image route, latent shape, injection point and strength | A5/feasibility; no latent or image-space placeholder implementation. |
| IO-04 | Latent-pattern to image-pattern relationship | A5/feasibility; a failed detection link must remain a failed hypothesis. |
| IO-05 | DCT channel, padding, synchronization, band, scores, thresholds | A5/preregistration; all affect results and remain TBD. |
| IO-06 | Independent watermark-presence witness for mismatch attribution | A5/threat model: a failed candidate match cannot distinguish an unmarked image from a transferred mark. `neither_match` is not automatically `copy_paste`. |
| IO-07 | Prompt-only generation/signing order | A5; unsupported route until specified. |

A3 records these missing scientific choices as its required output. It does not mark the method implementable or pass a feasibility gate. Nondependent specification and literature work may continue.
