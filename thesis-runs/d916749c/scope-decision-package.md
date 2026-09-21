# Scope Decision Package for Run d916749c

## Decision context

This package is for the `scope-acceptance` human gate that follows the current `intake-scope` step. It records what is actually available, what the proposal states, and which scientific requirements remain unspecified. It does not supply, recommend, or infer an approval verdict. The verdict must remain blank until the named run and gate are reviewed in the authenticated Codex task.

Run ID: `d916749c`  
Current workflow step: `intake-scope`  
Next gate: `scope-acceptance`  
Human verdict: **not provided**

## Reviewed execution profile

The `thesis-38` profile was derived with the pinned importer from the committed immutable 58-task guide. The committed source guide has SHA-256 `1ea21a525138d1f2de5927d5ab75639b343c378e8206409b68f7de8e3a58c91b`; the normalized source plan has SHA-256 `f401a92a903111960adbc32ca6b2d8862db1bb3f900fc31a39b438d9d89d5210`.

Verification passed:

- 38 unique reduced tasks cover 58 unique source task IDs exactly once.
- Five milestones contain 7, 6, 11, 9 and 5 tasks, respectively.
- Every reduced task occurs in exactly one milestone and exactly once in the topological order.
- All dependency targets exist.
- The corrected sequences are `A2a -> A3 -> A2b` and `C3a -> C2 -> C3b`.
- `D6` follows `D2`, `D3`, `D4`, `D5` and `D9`; the representative rerun belongs to `E4`.
- Seven lifecycle gates remain intact.
- The generated plan is semantically identical to the reviewed fixture.

The complete mapping and machine checks are in `mapping-verification.json`; the executable profile is in `guide-plan-38.json`.

The working-tree `THESIS_GUIDE_OFFLINE.html` is modified relative to the committed source and now embeds a 38-task viewer. Its SHA-256 is `fdba83a7d1aec198a0e7654fb3ce04f26b101292005f614e784e919f7d8e460e`. It cannot be used as the immutable 58-task importer input because the required source declaration is absent. It was not overwritten.

## Proposal scope actually present

The original Persian proposal is present as `پروپوزال 2.docx` with SHA-256 `15a02877be74f5118cc7b3d3ded9ab447cc07551773486264ac4755119adfeff`. A mechanical extraction and provenance record are present under `inputs/`.

The proposal states a hybrid neural-watermarking research direction with four research questions and four corresponding hypotheses:

1. Combine CLIP semantic features and pHash perceptual features to produce a unique but edit-tolerant image signature.
2. Test whether latent-space embedding improves watermark survival under regeneration attacks.
3. Test whether statistical analysis of mid-band DCT coefficients can detect the watermark competitively but faster than neural or inversion-based decoders.
4. Test whether content binding distinguishes an original image from a forged image bearing a copied watermark.

The proposed pipeline consists of semantic and perceptual signature generation, watermark injection into diffusion-model initial noise or latent processing, and lightweight DCT-based extraction. The proposal names three planned data groups: 1,000 MS-COCO images, DIV2K's 800 training and 100 validation images, and 5,000 DiffusionDB images. It names quality targets of PSNR above 35 dB, SSIM above 0.9 and LPIPS below 0.1, plus detection rate, regeneration robustness, forgery-detection ACC/AUC and inference time.

These statements are proposal commitments or hypotheses, not validated findings.

## Source inventory and evidence status

The proposal bibliography contains six citation strings: four DOI locators and two arXiv identifiers. No source PDFs or inspected-source records are present. Consequently, the literature statements and novelty language are unverified source claims and cannot yet support thesis claims.

Seven Office Math elements and seven figure placeholders require inspection in the original DOCX. The extracted Markdown does not preserve notation, figure meaning, pagination or exact layout. No visual rendering was available through the required bundled renderer, so layout and glyph fidelity remain unverified.

No thesis datasets, data manifests, method implementation, model manifests, checkpoints, experiment design, run outputs or results are present. The `thesis-agent-skills` tree is workflow infrastructure and synthetic fixtures; it is not scientific implementation or evidence for this thesis.

## Scientifically unspecified requirements

The following choices materially determine the experiment and must not be guessed or implemented before an explicit scope decision records them.

### Scope boundary

- Whether ownership transfer or dynamic ownership is an implemented protocol, a narrative motivation, or explicitly out of implementation scope. The proposal discusses dynamic ownership and transfer, while the reviewed execution profile guards against silently adding a transfer or ledger system.
- Whether the core claim is watermark presence, owner attribution, instance binding, semantic binding, regeneration provenance, or a defined subset of these distinct claims.
- Whether the method must support real camera images, generated images, or both through one pipeline, and what evidence is required for cross-domain generalization.

### Method and detector contract

- Exact CLIP model, checkpoint, preprocessing, feature layer, normalization and embedding dimension.
- Exact pHash definition, hash length, resize/color-space policy and robustness expectations.
- Owner identifier format, secret/key model, hash or KDF, collision policy and wrong-owner/wrong-key behavior.
- Exact diffusion model, checkpoint, sampler, scheduler, resolution and latent/noise injection rule, strength and payload mapping.
- Exact DCT block/color channel, coefficient band, synchronization, score calculation and decision thresholds.
- Detector inputs and knowledge: whether it receives the original image, reference features, owner ID, keys, model access or prompts.

### Data contract

- Exact MS-COCO release and image IDs; the proposal phrase "2020 or newer" is not an operational version pin.
- Whether all stated DIV2K images are mandatory; the proposal explicitly allows hardware-driven change, which requires a human scope decision rather than silent reduction.
- DiffusionDB subset selection, version/snapshot, deduplication, prompt/model stratification and stable identifiers.
- Train/development/validation/test splits, grouping, leakage checks, licenses and immutable checksums.

### Threat model and attacks

- Benign transform ranges and crop, noise, compression and geometry parameters.
- Regeneration model, edit strength, prompt policy, stochastic seeds and attacker access.
- Operational copy-paste attack construction and success rule.
- Inclusion or exclusion of adaptive, white-box, asymmetric-geometry and composite attacks.
- Attack budgets, quality constraints, query counts and false-attribution multiplicity.

### Evaluation and statistics

- Primary endpoint and endpoint family for each research question.
- Analysis unit, independence or clustering assumptions, number of owners/keys, seeds and repeats.
- Baseline identities, versions, checkpoints and equalized attack/quality budgets, including whether SEAL can be reproduced.
- Validation-only threshold selection, target FPR, positive/negative controls and wrong-owner/wrong-key controls.
- Sample-size justification, effect or precision target, confidence intervals, multiplicity policy and negative-result rule.
- Practical margins and pass/fail criteria for security, robustness, runtime and collision outcomes. The three visual-quality thresholds alone do not resolve these decisions.

### Resources and governance

- Available local hardware and an exact compute estimate.
- Any remote provider target, maximum duration and spending limit. No compute or spending is authorized at this stage.
- Current official university requirements, redistribution permissions, ethics/privacy constraints, similarity policy and AI-disclosure rules.
- A source-of-truth record confirming which proposal version and amendments received human approval.

## Gate readiness

The package is complete enough to expose the scope decision, but the scientific contract is not yet executable. Work must stop before literature claims are accepted, datasets are acquired, method code is written, thresholds are chosen, experiments are designed, or compute is started.

The reviewer should either provide the missing decisions and artifacts for a revised scope package or issue an explicit gate verdict using the exact run and step identifiers required by the workflow controller. This package intentionally contains no verdict.

## Files for review

- `guide-plan-38.json` — derived execution profile
- `mapping-verification.json` — full task-to-source mapping and validation checks
- `artifact-inventory.json` — present and missing artifacts
- `handoff.md` — stage boundary and next authorized action
- `../../inputs/proposal-source.json` — proposal provenance and extraction limitations
- `../../inputs/proposal-text.md` — non-translated mechanical extraction
- `../../پروپوزال 2.docx` — authoritative proposal document
