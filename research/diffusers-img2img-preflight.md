# A5 existing-image implementation preflight

Inspected 2026-09-23 by `/root`; read-only public source inspection, no installation, weight acquisition or model execution. Candidate only, not an environment/model selection or A5 completion.

Reference: Hugging Face Diffusers tag `v0.35.1`, annotated tag object `e116b12bed30c0dc756575b8cdc8f35b3f3199b7`, dereferenced commit `0f252be0ed42006c125ef4429156cb13ae6c1d60` via the GitHub git-reference/tag API. This is a pinned inspected release, not a claim that it is newest.

Raw source bytes were fetched read-only at both the tag and commit: identical, 59,513 bytes, SHA-256 `4e1de04f178a3509c01e39cf1760e0001edd287ccbb16359eb2a06c355ced3de`. No upstream source file was copied into the repository.

## Inspected implementation

The [pinned image-to-image source](https://github.com/huggingface/diffusers/blob/0f252be0ed42006c125ef4429156cb13ae6c1d60/src/diffusers/pipelines/stable_diffusion/pipeline_stable_diffusion_img2img.py) has three relevant boundaries:

- Lines 659-667 select the starting timestep from strength.
- Lines 669-727 encode/scale the supplied image (or accept four-channel latents), create noise matching the latent shape, and call the scheduler's noise-addition operation.
- Lines 779-807 decorate the public call with disabled gradient recording; its signature does not expose a replacement noise tensor.

Inference: L1 cannot simply use that public call as a differentiable noise optimizer. An explicit reviewed component-level path would be required. Shape, gradient continuity and exact scheduler behavior still need verification; editing only decoded latents would not establish initial-noise injection.

The [official overview](https://huggingface.co/docs/diffusers/api/pipelines/stable_diffusion/img2img) describes a reference-image/strength tradeoff. Do not equate image-to-image generation with faithful preservation or with pure-noise prompt generation.

The [repository license](https://github.com/huggingface/diffusers/blob/0f252be0ed42006c125ef4429156cb13ae6c1d60/LICENSE) is Apache-2.0 for this code; checkpoint/data rights need separate inspection.

## Remaining decisions

No checkpoint, strength, step count, precision, feature encoder, prompt policy, gradients implementation, or resource budget is approved here. Next inspection must trace a fixed scheduler's noise equation and gradient-compatible denoising path, resolve the meaning of initial noise for the existing-image route under the scope guard, and inspect an exact candidate model revision/configuration/license without fetching weights. Model feasibility and scientific execution remain unapproved.
