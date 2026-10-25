# Threat model, endpoints and scope

Draft for the bounded ROUTE C article, 2026-10-25. Author: Codex agent (codex/root). This section distinguishes the completed development study from the proposed server study. It does not authorize execution, finalize a chapter or establish a security guarantee. The retained [article skeleton](../../article/route-c-skeleton.md) and [stage-2b results](../../results-2b.md) supply the empirical scope; the [final protocol](../07-final-experiment.md) governs future work.

## Objects and adversarial objective

Let \(x\) be an original image and \(u=W(x,o)\) its published, marked RGB8 version associated with a claimed owner \(o\) under a fixed writer configuration. A regeneration procedure produces a suspect \(y=A(u;\theta,\xi)\), with public model/settings \(\theta\) and declared random inputs \(\xi\). The evaluated removal objective is failure of the appropriate fixed detector endpoint while retaining stipulated fidelity to \(u\). Endpoint loss does not imply attribution to another owner, absence of every carrier, or loss of all information about the mark. Content-compatible detection can fail through unreadable payload, incompatible content, or both.

The completed study addresses T3 regeneration on 60 development sources. The wider thesis also considers T4 copy transfer and T5 semantic collision, but this study supplies no new test of either. Public-method re-embedding, owner impersonation, arbitrary detector-query optimization and legal ownership are outside the evaluated claim. A public owner identifier and a pattern derived from public configuration are not signing secrets. Withholding an owner or reader from a particular attack callable is an experimental access condition, not proof that a real adversary cannot obtain them. [TM01, TM02]

## Separate attacker, verifier and scientific predictor

The proposed informed attacks receive the published \(u\) and pinned public proxy/quality-model weights. They do not receive \(x\), residual \(u-x\), owner/query identifiers, payloads, target-reader scores, detector gradients or an enrolled record. They make zero detector-feedback queries during construction or selection. One callable and globally selected setting apply to every arm, without a method-label argument. The selector may distinguish anonymized arms solely to require acceptable quality in each. These are restricted, detector-free stress tests motivated by previously observed development behavior, not an exhaustive search for the strongest attack against a fully public method. [TM03]

The scientific transport predictor has substantially more information: original and marked inputs, an unmarked target-model trajectory, target-model/reader internals, and their derivatives under recorded randomness. The quality comparator also sees original-referenced clean-input and C0-output qualities. Neither is an attacker or a deployable reference-free verifier, and their computational costs are unequal. Two fitted quantities do not remove the capacity of the pretrained systems used by the predictor. Its obligation is to use only declared pre-outcome information and report the actual computation. [TM04]

| Role | Permitted information | Information withheld in this experiment |
|---|---|---|
| A/B attack callable | Published RGB8 input; public proxy/quality models; frozen settings and randomness | Original, residual, owner/query, payload, target detector/feedback and method label |
| Attack selector | Candidate outputs and quality against the published input; anonymized arm groups | Detector outcomes and original-referenced quality |
| Operational F5 verifier | Suspect, claimed owner/profile, semantic extractor and SD1.5 latent reader | Enrolled reference image for reported C |
| Operational v5 verifier | Suspect, claimed owner/profile, semantic extractor and image-domain reader | Enrolled reference image for reported C |
| WAM/VINE known-message evaluator | Suspect and candidate message | Message presence supplies no semantic binding or ownership assertion |
| Scientific predictor / quality comparator | Original/marked inputs and declared C0 information; predictor additionally has model/reader derivatives | Marked-target pixels, quality, chips, scores, descriptors and target-path derivatives before forecast sealing |

## Endpoints are not interchangeable

For F5 and v5, the primary compound endpoint is \(C=\mathrm{semantic.read}\land\mathrm{content\_match}\). The weaker \(S=\mathrm{semantic.found}\land\mathrm{content\_match}\) admits recomputed-only detection. Any-carrier \(A=\mathrm{semantic.found}\lor\mathrm{instance.found}\) is a union of tiers, not an instance-only outcome. Exact original semantic-code recovery Q is separate: C can hold without exact original-code recovery because it tests compatibility with the suspect's content. A stored decoded word is not necessarily readable at its search-adjusted threshold. Two content-derived 32-bit codes and 320 chips per tier are not 64 independent arbitrary message bits or 640 bits of payload capacity. [TM05]

WAM's fixed known-message rule requires at least 27/32 matching bits and preserves empty-mask abstention; native mask-only detection is a different endpoint. VINE-R requires at least 69/100 matching bits, including equality. Neither presence rule imposes the same content compatibility as C. Side-by-side counts therefore describe native tasks and operating points, not an equal-payload/security leaderboard. Strict clean quality is also unequal: F5/v5 pass on 60/60 sources, WAM on 58/60 and VINE-R on 31/60. No post-hoc threshold or embedding-strength change equalizes the historical comparison. [TM06]

The transfer reader uses no enrolled reference for C. The separate registry study uses trusted enrolled-record side information and remains failed overall under its own decision rule. Its evidence must not be merged into this detector's claims or interpreted as legal ownership verification. [TM07]

## Regeneration and causal interpretation

Historical measurements include SD1.5/SDXL .1/.2/.4 with three seeds, K3 .2, codec/resizing controls, a two-pass SDXL rinse and fixed smoothing. The earlier frozen F5 SDXL .2 rule determines the historical label; the later extension is descriptive. These whole-pipeline contrasts change encoders, denoisers, resolution, posterior conventions, arithmetic or schedules in combinations. They do not randomize encoder training while holding everything else fixed. A common numeric strength is not a common noise dose, and a common integer seed does not certify identical consumed random tensors. [TM08]

The proposed confirmation grid retains six SD1.5/SDXL cells and K3 .2. K3 is excluded from fitting/calibration, but its historical result is known. Optional FLUX requires access, exact assets, configuration, quality eligibility and derivative feasibility to be frozen before fitting. Its absence leaves the seven-cell core; failure after inclusion cannot be repaired with a favorable substitute. Stage measurements and explicit paired random tensors can narrow explanations within a pipeline without identifying independent encoder training as the sole cross-family cause. [TM09]

Attack A composes SDXL then SD1.5 reconstruction. B uses a fixed public-proxy latent objective inspired by MarkNull; it is neither a faithful reproduction nor a theorem-backed remover. A's first pass and B's codec/fidelity ablations are the scheduled future controls. Historical rinse/D1/D3 outputs are retained comparisons, not additional confirmation cells. Orthogonality in B's selected latent comparison or successful removal does not establish statistical independence, complete signal erasure or a unique mechanism. [TM10]

## Admissibility and failure accounting

Future A/B outputs are quality-valid when LPIPS≤.15, PSNR≥25 dB and SSIM≥.75 relative to published \(u\). These automated constraints are not human judgments of unchanged meaning or imperceptibility. Embedding quality against \(x\), attack quality against \(u\), and end-to-end quality against \(x\) remain separate. Original-referenced quality never selects an attack, and human perceptual ratings remain absent. [TM11]

Development uses finite grids and fixed coverage rules in every arm. Eligible settings are ranked by a predeclared quality-only score and cost/parameter tie-breaks. This selects how to spend distortion, not the largest observed removal rate. Both attacks freeze before any new detector results are released. An empty eligible set means inactivity. Failed computation, missing image, nonfinite quality or blocked output cannot count as admissible removal, and no identity fallback replaces it. [TM12]

The source is the analysis unit; three seeds are repeated observations. Proposed H5 requires a clean-positive source and completed non-detection with acceptable quality; for A, those properties must coincide on at least two of the same outputs. The quality target is also tested separately, and all planned sources remain in the denominator. Historical routing and prospective uncertainty serve different purposes: old all-attempt counts are preserved, while new inference bounds unavailable outcomes conservatively rather than interpreting them as observed removals. [TM13]

## Specificity and generalization

C0 and wrong-query controls test different failures. Zero observed false detections is not a zero-probability or cryptographic guarantee. F5's SDXL grid has 540 C0 and 540 wrong-owner calls but only 60 sources. Under the independent-source population model, zero source-any events among 60 gives a one-sided 95% upper bound about .0487. One VINE-R C0 call reaches its inclusive threshold. Random-message tails used to describe operating points do not establish natural-image calibration or security against adaptive adversaries. [TM14]

The proposed 200-source pool is a metadata-only, preassigned selection of licensed curated images, with 40 ordered acquisition reserves. It is not a random sample of all creators or Internet images. Exact metadata exclusions do not rule out near duplicates or foundation-model pretraining overlap. Later authorized acquisition/hash checks precede scientific outcomes. Population inference assumes independent source groups; hashing does not prove that assumption. The complete native forecast inventory is sealed before marked-target outputs are generated/released, with fitting, attack selection and eligibility frozen on development data. This protects the prediction test without making the already consulted development cohort blind evidence. [TM15]

## Draft evidence ledger

This local ledger is a drafting aid, not an amendment to the protected thesis claim ledger. Author for all entries: codex/root.

| ID | Claim kind | Evidence IDs / inspected local sources |
|---|---|---|
| TM01 | Scope/limitation | [Protocol §1](../07-final-experiment.md); [retained results](../../results-2b.md) |
| TM02 | Limitation | [Project threat model: T6/public method](../../../threat-model.md); [positioning](../02-positioning.md) |
| TM03 | Prospective method/limitation | [Attack information/selection contract](../05-informed-attacks.md) |
| TM04 | Prospective method/limitation | [Prediction barrier](../analysis/prediction-contract.md); [quality comparator](../analysis/quality-baseline-contract.md); [WP6 L3](../08-review.md) |
| TM05 | Implementation/interpretation | [Reader predicates and source locators](../analysis/reader-contract.md); saved union run 20261025-0128-encoder-transfer-stage2b |
| TM06 | Measured result/limitation | [T7 endpoint/capacity table](../../design-research/T7-fair-reporting/synthesis.md); [stage-2b quality](../../results-2b.md) |
| TM07 | Scope/limitation | [Final-report claim boundaries](../FINAL-REPORT.md); authoritative MAIN STATE preserved registry verdict |
| TM08 | Measured method/limitation | [Retained results](../../results-2b.md); [reader controls/RNG](../analysis/reader-contract.md); [schedule bounds](../analysis/schedule-bounds.md) |
| TM09 | Prospective method/limitation | [Protocol §§2–3](../07-final-experiment.md); [family audit](../06-third-family.md); [WP6 L5](../08-review.md) |
| TM10 | Prospective method/limitation | [Attack specification](../05-informed-attacks.md); [WP6 R2/L6](../08-review.md) |
| TM11 | Prospective method/limitation | [Attack fidelity region](../05-informed-attacks.md); [T7 quality reporting](../../design-research/T7-fair-reporting/synthesis.md) |
| TM12 | Prospective method | [Finite grids, selector and release barrier](../05-informed-attacks.md) |
| TM13 | Prospective inference | [H5/missingness](../analysis/confirmatory-statistics.md); [protocol](../07-final-experiment.md) |
| TM14 | Result/derived uncertainty/limitation | [Saved-journal analysis](../analysis/journal-analysis.md); [negative/background supplement](../analysis/negative-background-analysis.md); [T7 operating-point limits](../../design-research/T7-fair-reporting/synthesis.md) |
| TM15 | Prospective method/limitation | [Selection rule](../heldout-selection-rule.md); [metadata audit](../analysis/heldout-metadata-audit.md); [protocol](../07-final-experiment.md); [WP6 L1](../08-review.md) |

No new empirical result is claimed by this draft. The proposed study remains unexecuted; publication and chapter acceptance remain human decisions.
