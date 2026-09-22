# A3: claims, attacker access, and controls

Status: **SPECIFICATION**, no measured security result. Source tasks `contract-2`, `contract-3`, issue #3. Proposal anchors: `PROB-01..03`, `RQ-01..04`, `METHOD-07..09`, and `METRIC-04..07` in `claims.csv`. Read `io-spec.md` for detector inputs and `approval-policy.md` for current scope. Scenario definitions below are operational proposals, not claims that the source fixes attack budgets or proves security.

## Assets, trust and claim separation

The protected unit is one source image and its enrolled marked output for a claimed owner in a controlled research setting. The legitimate operator controls enrollment and provenance. OwnerID is public. The adversary receives published marked images, public method/configuration descriptions, and public pretrained-model information as specified per scenario. Dataset ground truth, clean references and test labels belong to the evaluator, not automatically to the detector or attacker.

The baseline signature profile is public-derived: no cryptographic secret is specified by the proposal. Thus possession of an OwnerID is not authorization, and public reproducibility of key derivation is not cryptographic unforgeability. If a keyed variant is later introduced, it must have separate access assumptions and wrong-secret controls. Do not assert secrecy of `W_s/W_i` merely because the proposal calls them keys.

| Claim | Operational meaning | Scenarios and controls | Limit |
| --- | --- | --- | --- |
| Watermark presence | Evidence of an inserted mark under a declared detector/profile | T0,T1,T2,T3; C0,C1,C3 | Candidate mismatch alone does not prove absence; a general presence witness is TBD IO-06. |
| Owner attribution | Correct match for the tested owner against wrong-owner candidates | T0,T4,T5,T6; C1,C2,C3 | Conditional attribution in a defined candidate set, not legal ownership or authorization. |
| Instance binding | Reject matching a copied mark or semantically similar different image to the enrolled instance | T4,T5; C2,C4,C5 | Must distinguish instance rejection from any-mark presence. |
| Semantic binding | Stability for declared permitted edits with separation from incompatible content | T1,T3,T5; C1,C4 | Similar semantics are not identity. Semantic-only detection does not prove regeneration. |

## Shared measurement rules

Each attack manifest must pin attacker knowledge, model/checkpoint, actions/parameter grid, query budget `Q`, candidate count `K`, randomness, quality constraints, source/target IDs, split, and success rule before test evaluation. `Q`, `K`, severities and numeric success thresholds are currently `TBD` pending A5/design; a scenario with these missing is **BLOCKED_DECISION for execution**, not silently assigned defaults.

Keep attack construction, evaluator scoring and attacker feedback distinct. Nonadaptive attacks receive no detector feedback during construction; final evaluator calls are still counted. Report per-candidate and any-of-K false attribution, with the actual candidate/query counts. Use fixed validation thresholds; no best-of-test threshold, hidden retry selection, or success-only seed retention.

For same-content removal/benign attacks, assess quality against the legitimate marked source J's parent `I_w`, and report end-to-end distortion against I separately. For copy-paste, assess quality against the intended recipient/target image, not the watermark donor. For regeneration, report both image quality and content preservation; pixel similarity alone does not establish preserved meaning. The proposal's PSNR/SSIM/LPIPS embedding targets are not automatically attack-admissibility thresholds. Attack-specific numeric budgets need preregistration. Inadmissible attacks remain logged but do not count as successful admissible attacks.

## Scenario contracts

| scenario_id | attacker_knowledge | allowed_actions | budget | success_rule | quality_constraint |
| --- | --- | --- | --- | --- | --- |
| T0 clean verification | Evaluator knows enrollment/owner; no attacker | Score untouched I_w for correct and wrong candidates | K and repeats TBD; log every call | Control expectation: correct owner/component scores pass frozen rules; quantify failures | Report I_w versus I and optional matched reconstruction I_ref. |
| T1 benign transformations | Published I_w and public transform families; no secrets or feedback | JPEG, resize, crop and additive noise, tested separately | Severity grid/repeats TBD; attacker Q=0 for feedback; evaluator calls logged | Legitimate-content survival at fixed thresholds; not a malicious-forgery count | Pin family-specific admissibility against I_w and report against I. |
| T2 removal | Same as T1; knows public detector design but no oracle feedback | Nonadaptive filtering/recompression/denoising within declared family | Parameter grid and attempts TBD; feedback Q=0 | Correct-owner detection lost while attack remains admissible; do not equate this with attribution to another owner | Predeclared quality/content bound against I_w, plus end-to-end report. |
| T3 regeneration | Published I_w, chosen public regeneration model; no signing secrets | One pinned image-conditioned regeneration family | Model, prompts, strength grid, seeds/attempt count TBD; feedback Q=0 | Measure both component survival/loss and admissible removal; regeneration ground truth comes from attack provenance, not detector label | Quality and content-preservation protocol TBD; retain severe/nonpreserving outputs as inadmissible evidence. |
| T4 copy-paste forgery | Published donor I_w, target image, public donor OwnerID and method; no private source residual by default | Declared patch/signal transfer from donor to different target | Donor-target sampling, transfer size/strength and attempts TBD; feedback Q=0 | Target is accepted as donor's protected instance/owner at frozen thresholds and remains admissible | Target fidelity measured against recipient; exclude accidental source/target duplicates. |
| T5 semantic collision | Public images and semantic-family criteria; no detector feedback | Evaluate distinct semantically similar targets and dissimilar negatives | Selection rule, pair count and K TBD; feedback Q=0 | False instance/owner acceptance of a distinct image; semantic resemblance alone is not success | No image manipulation required; independent instance identity and duplicate checks. |
| T6 public-method re-embedding | Attacker knows the full public derivation and has public embedding/model access plus target image and victim OwnerID | Attempt fresh marking of target for victim ID in the public-derived profile | Feasibility/resource plan and attempts TBD; feedback Q=0 | Unauthorized target receives victim attribution despite never being legitimately enrolled | Target fidelity/content limits TBD; distinguish identity spoofing from copy-paste T4. |
| T7 adaptive white-box | Full detector internals/gradients or feedback beyond above | EXCLUDED_WITH_REASON from initial three-week evaluation; log as limitation | No execution budget granted | No robustness or unforgeability claim against this adversary | Outside evaluated scope; never imply general security. |
| T8 asymmetric geometry | Attacker can apply spatially varying warps | EXCLUDED_WITH_REASON pending synchronization feasibility; ordinary uniform crop/resize remain T1 | No execution budget granted | No general geometric-robustness claim | Distinguish local warps from included uniform transforms. |
| T9 composite/adaptive chains | Multiple transformations/optimized ordering | EXCLUDED_WITH_REASON from initial isolated-effect matrix; later preregistered extension only | No execution budget granted | No claim of resistance to arbitrary compositions | Single-family results do not establish joint robustness. |

T6 is a required threat analysis/control candidate because the default profile has no secret. It is not evidence that the method has already been broken, nor a newly approved expensive attack experiment. If rejected as outside an experiment, its implication for owner-authentication claims must remain explicit. Exclusions T7-T9 bound the initial evidence; they do not amend a stronger institutional requirement by assertion. A2b must compare them to the proposal.

For T4, a residual attack requiring the unmarked donor is a separate stronger-access variant. Declare it explicitly if used; do not give the attacker evaluator-only reference images without changing the access record. The absence of a correct candidate match cannot identify copy-paste specifically (IO-06).

## Required controls

| ID | Control | What it checks |
| --- | --- | --- |
| C0 | Unmarked real/generated sources and matched unmarked reconstructions | False positive baseline, including artifacts introduced by the model itself. |
| C1 | Untouched marked output, correct OwnerID and declared profile | Positive detection and enrollment-to-detection feature stability. |
| C2 | Same image with wrong public OwnerID | Owner separation; correct feature path with a wrong owner. |
| C3 | Wrong expected pattern/key oracle diagnostic; wrong secret only if a keyed profile exists | Pattern specificity; do not label an impossible input to the core API as a core-detector run. |
| C4 | Distinct semantically similar and dissimilar unmarked/marked instances | Semantic versus instance confusion and impostor-owner trials. |
| C5 | Donor-target pairs without transfer, and the declared transferred version | Incremental effect of the transfer; identical selection/quality criteria. |
| C6 | Semantic-only, perceptual-only, combined, and binding-disabled ablations | Whether improvements arise from content binding rather than an unrelated detector/embedding change. |

A3 is complete as a documented contract only: interfaces, source identities, visibility assumptions, scenarios, claims, and unresolved choices are explicit. Experiment execution remains blocked on the indicated architecture/design/compute prerequisites. No security conclusion is accepted at this stage.
