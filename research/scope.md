# Approved Claims and Operational Scope

## Status and authority

**Current policy:** [Approval policy](approval-policy.md) records the user's continuing-work delegation and the milestone audit correction: a transfer/registry demo is not a required system deliverable. The proposal's dynamic-ownership conflict remains explicit for the research contract. The original scope decision is retained below as history.

**Execution update, 2026-09-22:** The delegated decision in [scope-execution-decision.md](scope-execution-decision.md) approves a bounded solo-MSc implementation with a three-week system target. It resolves the project-level ownership-transfer boundary and assigns the remaining technical specifications. The sections below preserve the original A2a proposal interpretation and its pre-decision gaps; consult that decision for current execution authority. Institutional amendment approval is not asserted.

This document operationalizes the approved proposal for task `A2a`. The authoritative source remains `پروپوزال 2.docx`, identified by SHA-256 `15a02877be74f5118cc7b3d3ded9ab447cc07551773486264ac4755119adfeff`. `inputs/proposal-text.md` is a traceable mechanical extraction, and `research/claims.csv` separates short approved text from operational readings and unresolved issues.

Nothing in this document is an experimental result, a literature-validated novelty claim, or a workflow-gate approval. Unspecified scientific choices remain unresolved rather than being filled by implementation convenience.

The ledger contains 42 records, including all four research questions, all four hypotheses, and all three dataset commitments. In `approved_text`, ` ... ` marks omitted source text; operational interpretation appears in a separate column. Source spelling is retained, including the mixed Persian/Latin digits in the MS-COCO count. The two key-symbol rows use the equation transcription checked in `thesis-runs/d916749c/proposal-visual-verification.json`; the extraction represents those equations as placeholders.

## Approved scope

### Approved title

Persian title:

> سامانۀ پویای تملک تصویر با بهره‌گیری از نشانه‌گذاری عصبی مقاوم

English title:

> Dynamic Image Ownership With Robust Neural Watermarking

The titles are preserved exactly as proposal commitments. The word “dynamic” does not by itself define an implementable ownership-transfer protocol.

### Problem addressed

The proposal identifies three technical weaknesses to investigate:

1. Copy-paste transfer of a watermark from protected content to different content.
2. Removal or degradation of a watermark during model-based regeneration or denoising.
3. Semantic collision between distinct images with similar high-level content.

It also describes weak cross-domain generalization between camera-originated and model-generated images and narratively motivates secure ownership change, transfer, and owner history. These statements define scope pressure, but only the three-phase method in §4-4 defines the current technical core.

### Approved research questions

The four approved questions are preserved verbatim:

1. چگونه می‌توان با تلفیق بردارهای معنایی و کدهای هش ادراکی، امضایی برای تصویر تولید کرد که همزمان با حفظ یکتایی، در برابر ویرایش‌های مجاز پایدار باقی بماند؟
2. آیا انتقال محل جاسازی واترمارک از فضای پیکسل به فضای پنهان در مدل‌های انتشار، تأثیر معناداری بر افزایش نرخ بقای واترمارک در برابر حملات بازتولید خواهد داشت؟
3. چگونه می‌توان با تحلیل آماری ضرایب فرکانسی میانی، وجود و صحت واترمارک را با دقتی قابل رقابت با دیکودرهای عصبی اما با سرعت بیشتر تشخیص داد؟
4. آیا معماری پیشنهادی توانایی تفکیک میان تصویر اصلی و تصویر جعلی که دارای واترمارک کپی‌شده است را دارا می‌باشد؟

No additional research question is introduced here.

### Approved hypotheses

The proposal makes four hypotheses corresponding to the four questions:

1. Combining CLIP-derived semantic features with pHash-derived perceptual features will reduce semantic collision between distinct but semantically similar images.
2. Moving embedding from the pixel domain to the diffusion latent domain will increase survival under regeneration attacks.
3. DCT-statistical extraction will reduce runtime and compute cost relative to inversion-based decoders without a practically important loss in accuracy.
4. A mathematical dependency between content and watermark will expose copy-paste transfer through a signature mismatch.

These are hypotheses to falsify. They are not accepted conclusions.

## Implementation boundary

### Core method authorized by the proposal

The current core method is limited to the following traceable chain:

1. Accept an input image `I` and an owner identifier.
2. Derive semantic feature vector `E` using a pretrained encoder such as CLIP.
3. Derive perceptual binary representation `H` using a DCT-based pHash.
4. Derive semantic key `W_s` from semantic information and the owner identifier.
5. Derive instance key `W_i` from semantic information, perceptual information, and the owner identifier.
6. Embed a watermark signal through the diffusion model's initial-noise or latent process.
7. For a suspect image, recompute candidate semantic and instance keys.
8. Divide the image into 8-by-8 blocks, apply an image-domain DCT, and compare mid-band coefficients with expected key-derived patterns.
9. Distinguish at least three proposal-described outcomes: both keys detected, semantic key only, or a watermark/signature mismatch.

Steps 4 through 9 are architectural intentions, not executable specifications. Exact serialization, cryptography, model revisions, tensor shapes, channels, coefficient indices, scores, and thresholds must be defined in later specification tasks before implementation.

### Data commitments

The proposal names three evaluation groups:

- A 1,000-image subset of MS-COCO, described as “2020 or newer.”
- DIV2K with 800 training and 100 validation images at 2K resolution, while noting that hardware constraints may motivate a later human-approved change.
- A 5,000-image subset of DiffusionDB.

No release, item identifiers, immutable snapshot, sampling rule, deduplication rule, split, or checksum is yet approved. Counts must not be silently reduced.

### Evaluation commitments

The proposal states the following measures:

- Visual quality: PSNR above 35 dB, SSIM above 0.9, and LPIPS below 0.1.
- Robustness and security: detection rate after common transformations, regeneration robustness, and copy-paste forgery ACC and AUC.
- Efficiency: extraction time in milliseconds compared with an inversion-based approach such as SEAL.

The three visual-quality numbers are proposal targets. They are not results or universal acceptance rules. Aggregation, confidence intervals, primary endpoints, practical margins, family-wise analysis, sample units, and pass/fail rules remain unresolved.

## Core method versus related work

The following items appear as background, alternatives, or comparators and are not automatically part of the implementation:

- Classical DWT, DCT, SVD, and chaotic-map watermarking are related-work families. Only the proposal's pHash and image-domain DCT roles are in the current core.
- End-to-end encoder/decoder neural watermarking is a related-work family and possible comparator; the proposed extraction path is explicitly intended to avoid a heavy neural decoder.
- SEAL is cited as semantic-aware inspiration and an inversion-based comparison point. Its full pipeline is not automatically adopted.
- DRM and ownership-management systems appear in the literature taxonomy. No DRM, blockchain, ledger, marketplace, or rights-transfer service is specified as a core component.

## Ownership transfer boundary

The title and problem statement refer to dynamic ownership, ownership transfer, and owner history. The proposed method section defines owner-bound keys and watermark verification but does not define:

- a transfer request or authorization operation;
- replacement, revocation, or coexistence of old and new owner credentials;
- an owner-history representation or trusted store;
- a dispute or recovery process;
- a verification rule for a chain of owners.

Therefore ownership transfer cannot be declared implemented or excluded as irrelevant. Its status is `UNRESOLVED_SCOPE_CONFLICT`: it is narratively in scope but not operationally specified. Until a human decision is recorded, task `A2a` authorizes documenting the conflict only, not inventing a transfer or ledger protocol.

## Provisional exclusions and non-authorizations

These boundaries prevent silent scope growth; they do not amend the approved proposal:

- No blockchain, distributed ledger, DRM platform, marketplace, or legal-rights adjudication system is authorized by the current method section.
- No adaptive, white-box, asymmetric-geometry, or composite attack is automatically included or excluded; each requires an explicit threat-model decision.
- No dataset substitution or one-sided count reduction is allowed without a recorded scope decision.
- No exact model, checkpoint, threshold, attack budget, statistical test, or secret-management scheme may be selected merely for coding convenience.
- No proposal hypothesis, novelty statement, or performance phrase may be reported as a finding before evidence exists.

## Unresolved conflicts and required downstream decisions

| ID | Unresolved item | Why it matters | Required downstream owner |
| --- | --- | --- | --- |
| U-01 | Dynamic ownership and transfer protocol | The title and problem statement promise dynamic ownership, while the core method does not specify transfer. | Human scope decision before method freeze |
| U-02 | Existing-image route versus generation route | Real-image evaluation is required, but the embedding description relies on diffusion initial noise or latent processing. | I/O and architecture specification |
| U-03 | Claim type | Watermark presence, owner attribution, instance binding, semantic binding, and regeneration provenance are distinct claims. | Research contract and threat model |
| U-04 | CLIP contract | Model, checkpoint, layer, preprocessing, normalization, and dimension are absent. | Architecture specification |
| U-05 | pHash contract | Implementation, resize, color space, hash length, and stability policy are absent. | Architecture specification |
| U-06 | Owner and key contract | OwnerID format, secret model, hash/KDF, serialization, collision policy, and wrong-owner behavior are absent. | I/O, notation, and threat model |
| U-07 | Diffusion embedding contract | Model, checkpoint, sampler, injection location, tensor shape, strength, and payload mapping are absent. | Architecture specification |
| U-08 | DCT detector contract | Channel, padding, synchronization, mid-band indices, statistic, normalization, and threshold are absent. | Architecture specification |
| U-09 | Dataset identity and splits | Releases, stable IDs, selection, deduplication, licenses, and leakage-safe splits are absent. | Data specification |
| U-10 | Attack protocol | Transformation ranges, regeneration procedure, copy-paste construction, budgets, and success rules are absent. | Threat model and preregistration |
| U-11 | Evaluation and statistics | Primary endpoints, analysis units, target FPR, sample sizes, confidence intervals, multiplicity, and negative-result rules are absent. | Acceptance and sample-size specification |
| U-12 | Comparator contract | Baseline identities, versions, checkpoints, equalized budgets, and SEAL reproducibility are absent. | Literature review and experiment design |
| U-13 | Compute boundary | Local feasibility, remote provider, duration, and spending limits are not approved. | Compute estimate and explicit execution approval |

## Completion interpretation

Task `A2a` is complete when every approved research question and material commitment has a traceable row in `research/claims.csv`, the boundaries above are preserved, and unresolved items remain explicit. Completion of this document does not approve the paused `scope-acceptance` gate and does not authorize literature acceptance, data acquisition, method implementation, experimentation, remote compute, or spending.
