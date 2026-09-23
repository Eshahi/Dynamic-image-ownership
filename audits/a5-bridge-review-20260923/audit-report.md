# Independent partial A5 bridge review

Date: 2026-09-23. Reviewer: `/root/bridge_review`; author: `/root`.

Recommendation: **ACCEPT integrity of this partial analytical design only**. No blocking findings for that limited scope. This is not A5 completion, method feasibility, preregistration, plan-gate acceptance, compute approval, or academic acceptance. No source artifacts were edited or scientific execution performed by this reviewer.

## Exact reviewed artifacts (SHA-256)

- `research/bridge-design-options.md`: `91d647f76121f4b8b2fe8054a8f6689794d75b22a94ae40fc608cbfd55452855`
- `research/io-spec.md`: `9c257f7bd5101c51f7bdd15859ca21b969be9c3e3028df4b93c3746abd4eb27a`
- `research/scope-guard.md`: `c8c6af9d5349cd9a194d7594fe84c02679e79592f581d14392447cd4b6fea833`
- `research/research-contract.md`: `4ff8f58a808d5b50a7f1ce4ab90dba6416930d25be6715b0a261bf7790b28679`
- `inputs/proposal-text.md`: `382b950cf0b9dcf460ed84085a5cbf7b625c3c5ab3346b6866ca74599049080d` (relevant Table 8 method excerpt inspected; original DOCX/figures not independently reopened)
- `thesis-runs/d916749c/guide-plan-38.json`: `f874350c24923095834bd02f31f39778c762ccfb9e59af41701f1937fde1a92e` (A5 inspected in full)

Read AGENTS.md, approval-policy.md, continuation.md and thesis-evidence-audit skill. Audit is manual documentary/mathematical review, not output from the experimental evidence helper: helper `--help` was inspected, but required run/analysis manifests do not exist for this deliberately non-experimental artifact. No synthetic run inputs were constructed to force helper success.

## Semantic checks

1. Sign-quantization margin bound follows directly from Cauchy-Schwarz, with strict inequality excluding zero-margin ambiguity. All bits must satisfy the bound for whole-code equality. The text does not turn cosine similarity or hypothetical independent bit survival into empirical stability evidence. Additional pHash equality for Wi is preserved.
2. First-order image coefficient transfer has dimensions A=[r,n], p=[n], t=[r]. Correlation change is alpha t^T A p. Sharing a seed or shape imposes no general alignment constraint. This is a valid counterargument to dimensional reasoning, not a universal impossibility theorem.
3. Gradient of the fixed unnormalized linear template objective is A^T t; the directional first-order gain with delta=eta A^T t is eta||A^T t||^2. The document explicitly avoids finite-step, normalized-score, resource, quality or robustness guarantees. Differentiability is an assumption still requiring implementation inspection.
4. L0 and L1 modify the initial state, not decoded pixels. L1 is an unselected candidate, consistent with A5 permitting analyzed existing-image optimization. Whether a particular implementation actually modifies initial diffusion noise remains unresolved and must be demonstrated before adoption. Image-domain guidance alone is not a pixel-domain injection; replacing the variable with a decoded latent would require reassessment.
5. Detection uses suspect image, public OwnerID and frozen configuration, not original keys/image, prompts, decoder or enrollment. Embedding key instability, encoded-output verification, host contamination and dependent null scores are disclosed. Original-key residual results stay oracle-only.
6. Proposal high robustness/attribution assertions are not promoted into conclusions. Both-match is not legal ownership; semantic-only is not a regeneration diagnosis. Dataset commitments and comparator obligations remain untouched.

## Non-blocking warnings / unresolved downstream obligations

- W1: No pinned differentiable pipeline, concrete objective, shapes, coefficient layout or hard runtime/memory budget exists yet. L1 cannot be called implementable or hardware-feasible from these equations.
- W2: Hash-code equality during embedding and benign edits remains unmeasured; direct carrier transfer and attack survival remain unverified. Retrying or source-key substitution would change the evidence/knowledge contract.
- W3: A5 outputs method-spec.md and method.schema.json, A4 calibration/power/stopping and manifest-specific compute approval are still required. This document cannot accept plan-acceptance.

Useful next work is the proposed read-only pinned implementation/license/injection-path inspection, then a single exact candidate with failure semantics and independent review. Do not spend scientific compute or close issue #6 solely on this audit.

## Check limitations and failures

The first plan-print command failed with Windows cp1252 UnicodeEncodeError; repeated successfully using the verified interpreter with `-X utf8`. No scientific test was run. Git status at inspection showed preexisting modified THESIS_GUIDE_OFFLINE.html and untracked bridge analysis; neither was changed by reviewer. Controller/GitHub state assertions in the source were not independently queried by this bounded reviewer and are not accepted as new state evidence here.

## Added pinned-source preflight review

On the author's bounded follow-up request, also read `research/diffusers-img2img-preflight.md`, SHA-256 `713261c0e0bcc612e11229ae45251c7158945f67368ed070be6c4b60e790e442`.

Independently opened the [commit-pinned raw source](https://raw.githubusercontent.com/huggingface/diffusers/0f252be0ed42006c125ef4429156cb13ae6c1d60/src/diffusers/pipelines/stable_diffusion/pipeline_stable_diffusion_img2img.py), focusing on get_timesteps, prepare_latents and the public call (lines 659-807), and the [pinned license](https://raw.githubusercontent.com/huggingface/diffusers/0f252be0ed42006c125ef4429156cb13ae6c1d60/LICENSE). The stated strength-based start, image encoding/scaling, same-shape noise and scheduler noise addition are supported. The no-grad decorator and lack of an explicit replacement-noise argument support the qualified inference that the public call is not itself the required differentiable optimizer. This is not proof of global nondifferentiability or prohibition of a separately reviewed component implementation.

The code-license/checkpoint-rights distinction and unselected status are appropriate. No blocker to this documentary preflight. Tag dereferencing, author-reported byte identity/SHA and overview page were not separately re-fetched/rehashed by reviewer; acceptance is limited to the inspected commit's code semantics and honest inference boundaries, not independent reproduction of those additional provenance checks. Source code was not executed or copied into the repository.
