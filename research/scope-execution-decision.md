# Scope execution decision: solo MSc, three-week system target

Date: 2026-09-22. Target: 2026-10-13 (21 calendar days from this decision).
Decision: **APPROVE the bounded research scope below for continued specification and development through the existing downstream gates.**
Run: `d916749c`. Gate: `scope-acceptance`.
Decision maker: Codex, acting under Soroush's explicit delegation in the current authenticated task.

## Authority and constraints

The user explicitly asked Codex to make the scope decision, considering one researcher, an MSc thesis with a subsequent paper goal, no university hardware, a system ready within three weeks, and an upgrade from ChatGPT Plus to Pro. This is a faithful English summary of the user's instruction in task `01a0b9bd-fd47-7cf1-8123-ff77a4ca9dd8` on 2026-09-22.

This instruction expressly delegates this scope decision, overriding the workflow skill's usual requirement for a user-authored verdict naming the gate. The decision is attributed to Codex under delegation, not represented as a verbatim user verdict. It is limited to this gate; subsequent gates retain their existing requirements. No university or supervisor approval is asserted.

The original proposal, titles, questions, and `claims.csv` remain the source record. This document supplies the current project execution decisions and explicit limitations; it does not retroactively change the proposal. Any eventual institution-required amendment must be handled with the supervisor before presenting the changed scope as institutionally approved.

Observed local hardware: NVIDIA GeForce RTX 5070 Ti Laptop GPU, 12,227 MiB total VRAM reported by `nvidia-smi` on 2026-09-22. User-reported resources: ChatGPT Pro, Perplexity Plus, and optional future RunPod rental. Paid remote compute has no approved budget and is not assumed available for meeting the deadline. ChatGPT Pro is recorded as an assistant resource, not GPU capacity for experiments. Live RunPod provisioning is currently blocked by the installed runner; implementing a cloud provider is outside this three-week scientific scope.

## What must be ready in three weeks

A runnable, documented research system with an end-to-end image enrollment/embedding/verification path, a minimal ownership-transition demonstration, reproducible evaluation commands, immutable configurations, and initial controlled results with failed runs retained. It must be usable for the subsequent thesis experiments and writing.

This is a delivery target, not a claim that the scientific hypotheses will succeed or that complete publication evidence can be guaranteed in 21 days. A failed hypothesis can be a valid recorded result; a failed core pipeline is not a completed system. Full chapters and paper drafting follow this milestone, while provenance, literature notes, and experiment records are written during implementation.

## Scientific scope decisions

| Area | Execution decision | Claim boundary |
| --- | --- | --- |
| Main contribution | Evaluate combined semantic/perceptual content binding and resistance to copy-paste false attribution. | Prioritize RQ1 and RQ4; novelty and security remain hypotheses. |
| Embedding and detection | Test the proposed latent/noise embedding to image-DCT detection connection immediately; retain RQ2 and RQ3 as explicit comparisons. | A negative result must be reported; a spatial watermark fallback cannot be relabeled as successful latent embedding. |
| Dynamic ownership | Implement a small trusted local registry with an image record, current owner, version, and append-only transition events. A transfer checks the current owner's credential, records the new owner/version, and enrolls/re-embeds a new marked copy. Verify both watermark evidence and current registry state. | A controlled single-authority demonstration, not decentralized ownership, legal proof, or deletion of old distributed copies. An old mark may remain detectable while its owner is no longer current in the registry. |
| Supported inputs | Preserve both camera-originated and generated-image evaluation. Define an image-conditioned reconstruction/embedding route for existing images and a separate generation route only if feasible. | Reconstruction distortion counts against quality. Using captions to generate a different image does not count as watermarking the source image. |
| Training | Reuse inspected pretrained components; no diffusion foundation-model training from scratch. Permit only a small adapter/decoder experiment if pilot measurements and the later compute approval support it. | No unmeasured assumption that training fits memory or schedule. |
| Product surface | Python CLI, configs, local artifacts, and a minimal demonstration. | No web platform, blockchain, marketplace, distributed service, new messaging stack, or elaborate orchestration layer. |
| Threat model | Include JPEG compression, resize/crop, noise, one reproducible regeneration family, copy-paste, unmarked images, wrong keys, wrong owners, and semantically similar negative examples. | Adaptive white-box and unrestricted attacker claims are outside the initial evaluation; record that limitation. |

The ownership decision resolves U-01 for project implementation. U-02 and U-03 are bounded above; A3 must specify interfaces, registry trust assumptions, and the distinction between presence, current-owner attribution, instance binding, and semantic similarity. U-04 through U-12 are delegated technical specification work inside these bounds, not reasons to request a new scope decision for every parameter. U-13 remains subject to explicit compute authorization.

## Feasibility checks before expanding implementation

By day 3, after the necessary literature inspection, design, and local-compute approval, use a small manifest of 32 source images for engineering checks. This size is an execution pilot, not statistical evidence for a security claim.

1. Demonstrate a measurable relation between the injected latent/noise pattern and the proposed image-DCT detector. Inspect marked, unmarked, wrong-key, and same-seed reference outputs.
2. Check signature stability under benign changes. Cryptographically hashing slightly different feature vectors does not establish a stable identity; specify quantization, matching, or enrollment-reference behavior and measure its failure modes.
3. Check that existing-image reconstruction preserves image identity and report PSNR, SSIM, and LPIPS against the correct source/reference.
4. Measure peak VRAM and embedding, attack, and verification times. Estimate the full run matrix from those measurements, with an explicit operational margin and available host time.

If a core feasibility check fails, record it and time-box diagnosis. Select an explicitly labeled revised method for review; do not silently substitute a different embedding domain or eliminate a research question to keep a positive story. Failure to resolve the core path by day 5 triggers a concrete scope/deadline revision before further scale-up.

The domain-connection concern is an inference motivating a check, not an impossibility claim. Tree-Ring's described detector uses inversion of generated images back to noise ([paper](https://arxiv.org/abs/2305.20030)); Stable Signature uses a watermark extractor associated with its decoder modification ([paper](https://arxiv.org/abs/2303.15435)). These abstract-level inspections motivate candidate comparators; they are not completed literature validation or novelty clearance.

## Evidence required for a defensible thesis and potential paper

- Keep all four approved research questions visible in traceability, with supported, contradicted, or inconclusive outcomes.
- Use a simple spatial watermark baseline and one reproducible relevant diffusion baseline; inspect the proposal's SEAL reference before committing to reproducing it. Comparator compatibility and runtime must be verified before freezing the final plan.
- Include semantic-only, perceptual-only, combined-signature, and binding-disabled ablations. Compare embedding domains and detector cost where the methods support matched comparisons; disclose architecture differences.
- Split by source image before making attacks or variants. Keep duplicates and related variants in the same split. Choose parameters and thresholds using development/validation data, then freeze them before held-out evaluation.
- Report detection and attribution separately, including false positives/false attribution, ROC/AUC, quality, synchronized latency, peak memory, uncertainty, and failed cases. Retain the proposal's visual-quality targets as targets rather than measurements.
- Use image-level or appropriately grouped uncertainty estimates; repeated attacks/seeds on one source are not independent images. Do not claim a very low false-positive rate from a small negative sample. The final sample-size and analysis plan belongs in preregistration.
- Pin source IDs, models, code commits, seeds, configurations, and dependencies. Archive all scheduled runs, including failures and negative outcomes.

Publication is an objective conditioned on inspected novelty, sound comparisons, and results, not an acceptance guarantee. A narrower well-evaluated contribution is acceptable; claims must match the evidence.

## Dataset and workload policy

The proposal's full reference counts remain 1,000 MS-COCO, 800 training plus 100 validation DIV2K, and 5,000 DiffusionDB images. Release pins, licenses, image IDs, and deduplication must be resolved before acquisition.

Approve staged use: 32 images for engineering feasibility, then a deterministic balanced pilot of up to 300 source images (up to 100 per named dataset) for runtime estimation and debugging, followed by the preregistered held-out study. These are development sets; they must not leak into confirmatory test data. The 300-image pilot is not a replacement for the proposal's full counts and does not establish power or low-FPR performance.

Full-dataset runs may continue after the three-week system milestone. Preserve 2K DIV2K evaluation as a separate high-resolution check; resized pilot images must be identified as resized and cannot support native-2K claims. If measured cost requires reducing the final evaluation, record the proposed amendment and scientific effect explicitly before treating reduced results as fulfilling the original dataset commitment.

## Calendar and exit criteria

| Dates | Work | Observable exit |
| --- | --- | --- |
| Sep 22-24 | A3 interfaces/threat model, critical literature inspection, model/environment pins, feasibility design and approved pilot | Core-path feasibility report and measured resource estimate. |
| Sep 25-28 | End-to-end prototype, simple baseline, enrollment/current-owner/transfer demonstration | Repeatable CLI from input image to scored verification; named tests and failure cases. |
| Sep 29-Oct 4 | Comparative baseline, signature ablations, attacks, deterministic data/split manifests | Frozen experiment matrix and analysis plan with measured completion estimate. |
| Oct 5-9 | Approved controlled evaluation, bug fixes, negative-case review | Initial reproducible tables/figures and retained run inventory. |
| Oct 10-12 | Clean-environment rerun, packaging, demonstration, final correctness fixes | Release candidate and writing-ready evidence inventory. |
| Oct 13 | System milestone and remaining-study handoff | Runnable release, documented limitations, and explicit list of any incomplete full-scale experiments. |

These dates assume needed downloads, access, review decisions, and host availability occur in time. Update the measured forecast after the pilot; do not report completion based on calendar passage. Reuse the 38-task plan and its dependencies, grouping work into these timeboxes rather than inventing another scheduler. Prioritize the critical path; defer polish and optional extensions.

## Approval effect

The scope gate may advance on this delegated decision. It permits the next research/specification stages within the boundaries above. Evidence acceptance, experiment-plan acceptance, actual compute execution/spending, result acceptance, claim acceptance, and thesis finalization retain their own gates. No scientific success or university approval is implied.
