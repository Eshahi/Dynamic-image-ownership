# Progressive carrier implementation parity preflight

Scope: a second bounded CPU implementation check, not an independent milestone review, a faithful GROW reproduction, or a measured watermark result. The retained GROW primary text was inspected again at sections 4.2.1–4.2.3, Algorithm 1 and 5.2. No model weights, generated scientific images, held-out inputs or GPU experiments were accessed. The design remains [the declared GROW-inspired SD1.5 amendment](m1-progressive-design.md).

## Formula and execution findings

| Item | Finding |
| --- | --- |
| DCT/loss | Orthonormal 64-point DCT; exactly 128 selected coefficients. The implemented derivative is 2 B^T[M(BxB^T-S)]B / 128, matching the declared masked mean-square normalization. The paper prints a squared norm while calling it MSE; /128 is an explicit adaptation, not claimed source parity. |
| Guidance eta | 25 and 100 affect the predicted clean latent, independently of DDIM sampler eta=0. Selected coefficient residual contracts by 1-2 eta/128 in a single fp32 update: .609375 and -.5625. Eta100 therefore overshoots once; this is declared, not a bug or evidence of divergence. |
| Noise rearrangement | Recomputing epsilon=(zt-sqrt(a) z0_guided)/sqrt(1-a) recovers the guided clean latent algebraically. Only channel zero is corrected. The noise is then cast to fp16 in actual GPU inference; CPU algebra tests do not remove that quantization or certify its size. |
| Schedule | The actual pinned DDIM schedule is 981,961,...,1. Guidance indices 0–24 correspond to times 981,...,501. The final 25 steps have no watermark correction. This is the declared descending-time/first-half interpretation of the paper's start ratio. |
| CFG order | Candidate corrects the already combined CFG prediction. The paper's text and Algorithm 1 guide the conditional prediction before CFG. This material difference is documented and retained. |
| Latent units | Guidance uses scaled SD latent units; final decoding divides by the VAE scaling factor. Native extraction posterior mode is multiplied by the same factor before DCT. The VAE cycle directly decodes the unscaled posterior mode, which is algebraically consistent. There is no pixel bypass or source-residual composition. |
| Paired source | A newly seeded torch Generator produces identical initial noise for C0 and every C1 at each same prompt/seed. C0 remains the matched generation counterfactual. This does not establish preservation of a preexisting photograph. |
| Reference boundary | The extracted word depends on latent coefficients/mask and tie rule, not the evaluated payload or wrong-payload hypotheses. Changing references changes accuracies only. CLIP and clean-reference quality are evaluator fields outside extraction. |
| Decisions | Eight signs per bit, strict majority >4, ties zero. Fixed .875 means >=14/16. Complement and 64 fixed SHAKE hypotheses remain descriptive, correlated queries; no FPR or ownership guarantee is inferred. |

The public payload, public mask, SD1.5 adaptation, post-CFG order, /128 normalization, seed/prompt fixtures and fp16 model arithmetic prevent a paper-faithful label. Generation/attack safety checker paths remain intact. No formula, strength, schedule, model, transformation, threshold or scientific outcome has been changed by this check.

## Metadata defects found and corrected with parent instruction

The earlier manifest guard accepted a nonempty subset of the declared four cases. It now requires the exact ordered four seeds/prompts and schema/config, preventing a shortened denominator. The earlier resume guard could accept duplicated completed IDs, duplicated artifact paths or empty nested score objects. It now requires the full 28 planned IDs, correct row variant/seed/control identity, unique attempt prefixes, unique completed IDs and exact four condition-to-artifact memberships.

Completed rows validate both decoder words, correct/complement decisions and counts, all 64 wrong-query scores/counts against their fixed hypotheses, finite timing, same-arm quality including CLIP, and paired C1/C0 quality. Finite numerical checks reject booleans and malformed values. Infinite PSNR is represented only by a true flag, zero MSE and null PSNR. Generation metadata must retain the exact schedule, guided indices, sampler eta0 and false safety flag. C0 original PNG and every scored artifact are hash-verified before reuse. Fresh condition/paired quality records also undergo these checks before a row can complete. Failed/interrupted attempts remain retained; they are never silently relabeled complete.

## CPU evidence and limits

Nine new tests in `tests/test_m1_progressive_preflight.py` pass, plus the existing eight tests in `scripts/test_m1_progressive_latent.py`. The new suite checks exact coefficient contraction/unselected coefficients, scheduler-time noise rearrangement, actual generation control-flow/body pairing and eta, final scaling, extraction reference separation, native posterior scaling versus image diagnostic, threshold/ties, all-28 failure inventory, and adversarial subset/duplicate/path/missing-score/nonfinite rejection.

The control-flow tests execute the actual function source with only CUDA device string literals mapped to CPU, use the installed real DDIM scheduler and deterministic fake U-Net/VAE components, and verify the 50 calls and guidance phase. They do not run pretrained inference, synthesize scientific images, estimate perceptual quality, or test fp16 GPU cancellation. A separately injected pre-model error writes temporary metadata and proves all 28 generation IDs remain incomplete, corresponding to 112 planned scoring conditions. Native scientific failure still stops the invocation; the retained planned/incomplete inventory supplies the denominator and a same-identity resume may retry only failed attempts with fresh paths.

This check supports implementation/config parity with the declared amendment. Carrier survival, quality, false findings and runtime remain empirical tasks. C is not counted as successfully tried until a retained committed scientific run exists.
