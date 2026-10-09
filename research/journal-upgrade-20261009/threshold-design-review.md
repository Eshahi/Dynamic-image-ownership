# Proposed thresholds and decisive follow-ups

Date: 2026-10-09. Independent methodological planning review by Codex agent. **Proposals only:** no execution, approval, revised M2 verdict, or claim of journal acceptance. Scope: T3 regeneration, T4 copy-paste, T5 semantic collision. All numerical targets below are engineering decisions for future preregistration, not universal literature standards or Q1 requirements.

## 1. What the present evidence permits

Reviewed `research/f5-r2-spec.md`, `research/m2-independent-review.md`, authoritative `STATE.md`, `research/threat-model.md`, and `scripts/f5_latent_codec.py:265–326`.

F5 clean both-match is 299/300; joint quality 298/300. T3 source-majority semantic counts at .1/.2/.4 are 30/30, 30/30, 21/30 versus v5 29/30, 22/30, 5/30; checked-only at .2/.4 is 27/30, 17/30 versus 10/30, 3/30. Full both-match disappears after regeneration. T4 rejection 0/29 and T5 rejection 0/27 do not isolate binding; donor delivery is only 4/30 versus v5 8/30. Three clean negative cells each contain 0/300; their 900 calls share sources.

Preserve these results and original thresholds. Once used to motivate revisions, M2 is historical evaluation evidence, not a fresh test of the revised method. Use separate development, calibration, and newly reserved confirmation groups; disjointness includes duplicates, source families, and reused attack donors. Do not inspect remaining held-out images to select that division.

## 2. Four separate kinds of threshold

| Kind | Proposed future setting | Interpretation |
|---|---|---|
| Detector operating point | Primary nominal FPR .001; secondary .01 and .0001 | Calibrate each method independently on calibration negatives; freeze before confirmation. Keep original F5 operating point as a separate historical comparison. |
| Attack intensity | Grids below | Strength is a pipeline parameter, not a probability or universal distortion scale. |
| Attack admissibility | Quality/content rules below | Determines whether removal or forgery preserves the intended use; never tune from detection outcomes. |
| Scientific acceptance | Gates in section 6 | Determines which narrow claim has sufficient evidence; failure does not invalidate honestly reported research. |

Report any-mark detection, checked semantic acceptance, full both-match, and explicit instance verification separately. Primary T3 endpoint should be **checked semantic acceptance**; raw semantic presence remains secondary. Neither means full-instance authentication.

## 3. Error rates, confidence, and dependence

For zero errors in n independent Bernoulli units, the one-sided 95% exact upper bound is `1 - .05^(1/n)`. Required sample sizes are:

| Claimed upper error bound | One prespecified cell | Three simultaneous cells, Bonferroni |
|---|---:|---:|
| 1% | 299 | 408 per cell |
| .1% | 2,995 | 4,093 per cell |
| .01% | 29,956 | 40,942 per cell |
| .0001% = 1e-6 | 2,995,731 | 4,094,343 per cell |

Thus 0/300 supports approximately <.994%, 0/29 <9.81%, and 0/27 <10.50%, individually. The 900 calls cannot be treated as 900 independent images. Different owners, seeds, or attack attempts on one source are not new population units. Synthetic key trials may assess conditional key randomness; they do not replace diverse independent images for deployment FPR.

Propose 10,000 separate calibration negatives and 5,000 fresh confirmation source groups per target population, with the three negative conditions applied to each. Freeze thresholds using calibration only; confirm each cell with exact intervals and simultaneous coverage. Zero/5,000 meets the three-cell .1% bound; observed errors require the actual bound. Additional domains/endpoints require a larger multiplicity family or explicitly separate claims. Calibration to .001 does not guarantee a .001 confidence bound; design conservatively and report a failed bound without retuning.

F5's profile `false_positive_target=1e-6` is a model-based target, not empirical verification or cryptographic security. Validate null assumptions, score/key dependence, code selection, and all search branches. A theoretical independent-bit binomial calculation or concentration bound applies only under its assumptions. Public-derived keys permit adversarial dependence; natural-image null validation cannot prove unforgeability.

Let R be owners tested, K attack candidates, Q feedback queries. For nonadaptive fixed tests with valid marginal error bound p, a union bound is at most `min(1,R*K*p)`; independence is unnecessary. It does not certify adaptive searches. Primary R=1, Q=0; exploratory roster R=10/100 gets separate calibration and reporting. Count evaluator calls separately from Q.

## 4. Attack grids and admissibility

**T3:** retain SD1.5 DDIM for continuity; add one different diffusion backbone sharing a VAE and one independently trained VAE/backbone. Pin actual checkpoint hashes: model names alone do not establish independence. Include VAE-only reconstruction, strengths .05/.1/.2/.3/.4/.5/.6, seeds 0–2. Development kill-test: twelve reserved sources, .2/.4, three seeds, independent VAE model first. Expanded confirmation proposal: 300 independent sources per declared domain, three seeds, frozen grids. More seeds improve within-source estimation, not source sample size. K=3 at each dose; K=21 for seven-dose any-attempt summaries per model. Q=0. Log effective timesteps, sampler, guidance, prompt policy and resolution. Equal strength across models is not equal attack severity; compare quality-conditioned curves too.

Proposed T3 admissibility: LPIPS <=.30 against marked input **and** blinded majority agreement by three raters that main entities, actions, and scene identity are preserved. LPIPS <=.20 is a prespecified strict sensitivity analysis. Report PSNR/SSIM and independent semantic similarity continuously; do not gate with the same CLIP used by the detector. Human verdicts must actually be obtained. Count all outputs; report admissibility coverage, joint admissible-removal frequency, and conditional removal. For paired method comparisons show all outputs plus the intersection admissible for both methods, with its denominator. Never discard difficult seeds silently.

**T4:** square patch area fractions 1/64, 1/16, 1/4; alpha .25/.5/1; two deterministic locations chosen without detector outcomes: K=18, Q=0 per disjoint donor-recipient pair. Add no-transfer sham. Preserve default attacker access: published marked donor, no unmarked donor residual. A residual-transfer positive control may use evaluator-only access, explicitly labeled a mechanism diagnostic. Require recipient identity preserved by blinded majority and LPIPS <=.20 against recipient; .30 sensitivity only. Report transfer delivery before binding, false full acceptance overall, and rejection conditional on delivery. Use the same delivered signals for binding ablations; otherwise lost signal masquerades as effective binding.

**T5:** preregister one semantic-nearest distinct candidate (K=1), then K=10/100 search budgets within a separately defined candidate pool; Q=0. Select using independent semantics and duplicate checks, never detector score. Report random dissimilar controls and same-owner/different-owner conditions. No image modification: admissibility is distinct instance identity. Reused targets induce dependence; primary confirmation uses disjoint source-pair clusters.

## 5. Binding and fair comparisons

Current detector inputs contain no claimed enrolled-instance identifier/reference. A different legitimately marked image from the same owner is a true owner positive. Calling that a false owner attribution would be incorrect. **Before claiming enrolled-instance binding**, specify an enrollment-aware verification endpoint and its side information, or narrow the claim to self-consistent content binding. This is an interface/claim decision before experimentation.

Cross same/different owner with similar/dissimilar content, marked/unmarked recipient, sham/transfer. Compare combined, semantic-only, perceptual-only, and binding-disabled verification on identical marks and delivered signals; distinguish detector ablations from re-embedding changes. A binding-disabled detector that never accepts transferred signals is an uninformative comparator.

Compare full F5 and v5 systems, then matched carrier ablations with views, matcher, payload, quality budget, and optimization held constant. Use matched observed quality curves as well as fixed budgets. Include an applicable post-hoc baseline; generative-only methods belong in a separate setting. Report original-image/latent/prompt/key access, inversion steps, training, VAE/CLIP passes, latency, memory, hardware and payload. Shared VAE performance is family-specific evidence, not cross-model generalization.

WAVES motivates TPR@.1%FPR and performance-versus-quality evaluation; it does not prescribe our acceptance targets. See [WAVES v2, sections 3.1–3.2](https://arxiv.org/html/2401.08573v2#S3). ZoDiac illustrates the operating-point problem: its threshold table reports Zhao23 WDR .988 at FPR .062, versus .938 at FPR .004. These are not directly comparable with F5 counts at another detector threshold, attack or quality level. See [ZoDiac v2, Table 3 and section 4](https://arxiv.org/html/2401.04247v2#S4).

## 6. Proposed go/no-go decisions

| Claim or stage | Frozen future criterion | If unmet |
|---|---|---|
| Clean fidelity/reliability | Every confirmation image PSNR >35, SSIM >.9, LPIPS <.1; clean both-match one-sided lower bound >=.95 | Reject universal sample-quality claim; report failures. All-pass sample is not proof of universal population quality. |
| Low-FPR claim | Each primary negative cell simultaneous upper bound <=.001 | Report achieved bound; no threshold adjustment on confirmation. |
| Cross-model T3 | Checked source-majority point estimate >=.90 at .2 and >=.70 at .4, plus paired improvement over matched pixel ablation >=10 percentage points and multiplicity-adjusted lower difference bound >0 | Narrow to tested family or report negative carrier hypothesis. All-source endpoint primary; admissibility-qualified results alongside. |
| Binding mechanism | >=100 delivered independent pairs; paired false-acceptance reduction >=10 points and adjusted lower difference bound >0 versus disabled binding | No efficacy claim; low delivery means unresolved mechanism. |
| T4/T5 bounded error | Three prespecified attack cells: 408 independent clusters each with zero errors, or exact simultaneous upper bounds <=.01 | No below-1% claim. K fixed as part of the endpoint. |

The 100 delivered pairs test binding efficacy, not a rare-error bound. These three attack cells must be named before confirmation; an enrollment-aware same-owner instance cell is applicable only if that endpoint is implemented. The 90%/70% T3 targets are point-estimate targets, not confidence guarantees.

Use source-cluster paired intervals and exact paired tests for binary source-majority outcomes; seed-level curves are descriptive. Prespecify a small primary contrast family and Holm control at .05; perform development-based power analysis before freezing sample size. Three hundred is a precision planning floor, not guaranteed power. No pooling domains to hide failure.

Priority: (1) resolve instance semantics and test same-owner binding with positive delivery controls; (2) run independent-VAE .2/.4 kill-test; (3) isolate carrier with matched ablations; (4) calibrate negatives and evaluate applicable baselines; (5) only then design fresh confirmation and human admissibility assessment. This avoids scaling an unidentified mechanism or model-specific effect.
