# Independent A5 initial-noise-path review

2026-09-23. Reviewer `/root/bridge_review`; author `/root`.

**ACCEPT partial candidate integrity only; no blocking findings.** Not A5 completion, selected-model acceptance, pipeline numerical equivalence, scientific feasibility, plan-gate approval or compute authorization. Read the evidence-audit skill fully. This is a manual documentary/code/algebra review, not the experiment evidence helper's schema: scientific run/analysis inputs do not exist and were not fabricated.

## Exact reviewed local SHA-256

| Artifact | SHA-256 |
| --- | --- |
| research/initial-noise-path.md | d57b9c76b50facdcc86d8a3ffcd0fd7d7122ddb0a23241ed8f5369fda7933251 |
| scripts/noise_path_reference.py | 8abe49272996eaeec24e4f096f41f451e8133ba16110e065ba3917b041acf9f9 |
| scripts/test_noise_path_reference.py | 4ba81fccbbb4fa80d83fb95e1a2752acf2c5644fa96b917f9f663dd19b8cb7ed |
| scripts/inspect_noise_sources.py | 0485ee956a127895eb182acef4211e35818401ebfe7a57100a4ac141f4e35178 |

HEAD during review: `5e01471f55b82bd2c041d858a553d3d555befd81`. Four reviewed artifacts were untracked; preexisting THESIS_GUIDE_OFFLINE.html was modified and not touched. Reviewer writes only this audit directory.

## Reproduction and source checks

Executed the verified project interpreter with `-X utf8 scripts/test_noise_path_reference.py`: **6 tests passed**, 0.001 seconds reported. These are scalar/index checks, not model experiments. Tests cover suffix examples/guards, initial-noise scaling, eta-zero consistency, final-alpha semantics and scalar guards. No scientific seeds, image inputs or model results exist.

After reading the fetch script, independently ran `-X utf8 scripts/inspect_noise_sources.py` using the same interpreter. It succeeded without an additional permission request. It fetches five fixed public text endpoints, caps each response at 200001 bytes, rejects oversized content, hashes/prints text, writes no files and executes no fetched code. All five hashes matched the note exactly:

- DDIM: `6bb3c830a7937a96acd9bfc3bbab6d75404ceda0189c423899d03c9d34da8599`, 24919 bytes.
- VAE config: `786a7d21647ddea6a04b9675c03d3cb45e90a2f3c6da5fbda2c54ade040036de`.
- UNet config: `78f474de6bab3d893868f37be97b636ae65c0df3073ed3256ca458ff599b5f96`.
- Scheduler config: `699cce92eb7c122e2eb7dfdea78e6187fda76a5ed4a8e42319b85610e620e091`.
- Model card: `2079161f9df7524bd9eca5e53ff5911271b8551e0f868b7b5a92b84776df28a3`.

Read DDIM lines 180-270 and 290-521, full three configs, card lines 1-150. The [pinned scheduler source](https://github.com/huggingface/diffusers/blob/0f252be0ed42006c125ef4429156cb13ae6c1d60/src/diffusers/schedulers/scheduling_ddim.py) supports scaled-linear betas, cumulative alpha, leading spacing, offset, preceding index, epsilon prediction, eta-zero update and additive-noise equations. The [pinned candidate repository](https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5/tree/451f4fe16113bff5a5d2269ed5ad43b0592e9a14) confirms native PNDM, absent VAE scaling factor, declared shapes, mirror warning, lossy VAE and safety-module expectation. DDIM is honestly an author adaptation, not native configuration.

The reviewer did not separately repeat model-API revision discovery, AutoencoderKL default-source inspection or linked mutable license-page inspection. Those remain author-inspected provenance assertions, not newly independently verified here. No weights acquired, package installed, loader run or model-license clearance granted.

## Mathematical and scope findings

The optimized delta enters additive noise before the first reverse suffix step. Its latent effect is scaled by sqrt(1-a_t); no pixel overwrite or decoder-state replacement is asserted. Frozen base image latent, noise, conditioning, weights and schedule make the matched unmarked comparison meaningful as a proposed control. Quality must still include original-image reconstruction loss, as the document requires.

Leading suffix construction matches the inspected first-order schedule and earlier img2img start policy. N=1000 is rejected because offset 1 yields invalid time 1000; rejecting the whole configured schedule even if a suffix could avoid that index is an explicit stricter guard, not an unnoticed mismatch. Fractional strength is discretized via floor(N*u); empty suffix is rejected. The final preceding alpha uses a[0], not 1, as declared. The scalar eta-zero formula is correct for epsilon prediction with disabled clipping/thresholding.

Image-conditioned suffix noise is expressly distinguished from terminal pure-Gaussian generation. This distinction remains a research interpretation requiring full-method review, not evidence that every interpretation of the proposal is fulfilled. Detector knowledge is unchanged, no gradient/safety bypass is instructed, and safety-flagged outputs remain failures. DDIM clipping/threshold flags are numerical scheduler choices, not replacement for the required safety module.

## Non-blocking warnings

W1: Reference tests do not cover Torch dtype/rounding, real graph connectivity, model memory, resolved VAE scale or installed-Diffusers numerical parity. A production path must validate those.

W2: N, strength, objective, signature stability, template/DCT construction and optimizer/resource bounds remain incomplete; the document is not executable configuration. No evidence of watermark performance exists.

W3: Mirror weight equivalence, component acquisition provenance and frozen license artifact remain unresolved. The mutable license reference and tag-linked VAE default are not a complete acquisition package.

No reviewer test/fetch failed in this bounded review. Earlier author-reported socket/web failures remain disclosed in source; this successful independent fetch does not rewrite their history.
