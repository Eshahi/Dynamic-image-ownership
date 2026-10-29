# Round 3 prospective result interpretation

2026-10-29. Author interpretation guide, **not an independent review, result, new gate or execution approval**. Every outcome below is hypothetical. Use the actual pre-output chosen profile and exported analyzer verdict; this guide adds no variant, search axis, threshold or schema.

Read alongside the [Stage P protocol](../stage-p/PROTOCOL.md), [Stage S protocol](../05-stage-s-protocol.md), [gate analysis](r3-gate-analysis.md), [writer design](r3-denoiser.md) and [cost report](../stage-p/round3-cost.md). The effective default remains round1 unless the external pre-output choice selects round3-proposed. A favorable alternative-profile calculation never changes the effective profile after results.

## Read the package before the mechanism

| Future observation | Prospective interpretation and reporting consequence |
|---|---|
| Required parity, projection or finite-gradient check fails | The implementation has not qualified for this run. Preserve its exception and receipts; do not interpret missing native retention as a demonstrated method failure or change precision/conditioning to rescue this run. |
| OOM, time/disk forecast failure or paid deadline stops work | Report resource feasibility and the preserved partial inventory. Missing work is not an observed negative. An already demonstrated scientific gate failure remains a failure: the Stage S analyzer deliberately gives `SCIENTIFIC_KILL` precedence over a later resource stop. Otherwise its resource verdict is `RESOURCE_STOP`. |
| Required record, original reference, owner call, quality result or run identity is missing/invalid | Report `INCOMPLETE` where the frozen analyzer cannot establish a decisive failure. Numerical gate pass alone is insufficient for package GO. No missing VINE-B record becomes evidence of baseline weakness. |
| Candidate has high native counts but fails strict clean quality or clean F | The quality/clean-read constraint defeats this candidate under the chosen profile. Report the tradeoff, not “robustness success” without qualification. Nominal PSNR budgets do not override saved-image measurements. |
| A required C0/wrong-owner/eligible threat event is observed | It is an observed specificity/binding-screen failure, not missingness. Use the frozen eligibility and endpoint rules; do not exclude the source or redefine its denominator. Human semantic-distinctness labels remain separately missing where unprovided. |
| Stage P selects a candidate but its eight-source check fails | This bounded search ends. No runner-up, retuning, extra seed, default-writer fallback or check-to-tuning migration follows. Preserve all attempted candidates and reasons for elimination. |
| Stage P check passes | The nominated configuration survived a development veto. It has not established the Stage S threats, external comparisons, full inventory or article rule, and it supplies no execution authorization. |
| Stage S numeric gates pass but evidence inventory is incomplete | Report `numerical_thesis_gate_status` separately from the package verdict. This is neither full thesis GO nor article GO. |
| Complete Stage S meets the effective profile | Report a successful development screen under that profile, with all counts, achieved quality and control limitations. It is not fresh confirmation, security certification or journal readiness. |

Strict quality means PSNR **>35 dB**, SSIM **>.9**, LPIPS **<.1** on every required clean image; boundary equality fails. The Stage S clean-F minimum is 15/16. The source, not each seed, is the efficacy unit: two of seeds 0/1/2 establish a source majority. Report per-seed rows as repeated observations and the C/J source counts, not 48 independent images. C requires a content-consistent semantic read; J additionally requires recovery of the original semantic code. If C exceeds J, inspect the exported exact-code outcomes before describing original-code retention. Neither endpoint is interchangeable with mere carrier presence.

All 60 original images have historical development exposure. Round 3 divides them into 24 P images, 18 S donors and 18 S threat targets; partition disjointness does not erase that history. The eight P check images are untouched by the current nomination decision, **not fresh held-out confirmation**. They provide a single veto for one already nominated configuration. Do not pool P and S numerators or use the selected tuning maximum as an unbiased performance estimate.

In the executable K3-out branch, K3 is gradient-excluded and selection-seen. SD3.5 remains a prospective unseen-family test only while none of its outputs or performance diagnostics influence selection; it is not run or inferred here. The separate deferred K3-in proposal is not an available rescue branch after these outcomes. Source disjointness and regenerator-family exposure are different dimensions of generalization.

## What the arm contrasts can establish

Stage P allocation has a separate status policy from the final Stage S
conjunction. Every allocated candidate and required control must be accounted
for before selection can establish scientific exhaustion. A resource stop in
any of them takes precedence over an already observed candidate rejection;
otherwise missing required evidence yields INCOMPLETE. Candidate failure
reasons remain in the record. Neither status permits promotion or a
check-set replacement. This distinction prevents a failed candidate from
hiding resource exhaustion in its required comparator.

The following are descriptive readings of complete measured contrasts. Whether any contrast is a primary gate is determined only by the chosen profile.

| Future contrast | Supported reading | Unsupported stronger reading |
|---|---|---|
| F6 exceeds retained F5 but not `f5-budget` | The historical construction is weaker at its retained budget; extra distortion budget/implementation differences remain a sufficient competing explanation. Under round3-proposed, missing the required budget-control gain blocks GO. | That the surrogate provides benefit beyond the matched-budget control. |
| F6 exceeds both F5 controls with required achieved-quality comparison | Evidence for the selected F6 package beyond those two controls under the declared development conditions. | Equal compute, equal optimization opportunities, equal per-source quality, or population superiority. |
| x0 exceeds noise | The complete sampled-window denoiser surrogate performs better on the measured cells. | A causal denoiser-only effect: x0 samples the native window, whereas noise uses its first timestep. |
| Noise exceeds x0 despite valid implementation checks | The more expensive x0 design did not improve this bounded search/screen. Native/surrogate mismatch or optimization differences remain possible explanations. | That denoiser gradients can never help, or that a particular mismatch has been diagnosed. |
| x0/noise exceeds codec and generic controls | The tested composite design has an advantage over those measured controls at the frozen settings. | That denoising is the unique mechanism, or that every alternative regularizer is inferior. |
| Codec matches/exceeds x0/noise | Codec-based optimization remains a competing explanation; a claimed noise/denoiser-specific advantage is not established. | Statistical equivalence from a small count tie, or failure of all native retention. |
| Generic matches/exceeds x0/noise | The results do not distinguish the specialized surrogate from the tested generic robustness objective. | That any perturbation training works, or that the generic arm is the nominated replacement. |
| Candidate works on R0/R1 but falls below K3's bar | The required cross-family screen fails in the gradient-excluded family. | Success on all targeted native regenerators, or permission to drop K3. |
| Candidate works on K3 | Evidence extends to a family excluded from writer gradients but used in Stage P selection. | Performance on a selection-unseen family. |

All F6 variants have 150 robust updates plus 50 clean refinement updates, but **350 reader-gradient evaluations**: a clean and a surrogate reader evaluation in each robust update, then 50 clean refinements. `f5-budget` has **200** reader-gradient evaluations and no surrogate. x0 adds 150 denoiser graphs. Thus equal update count and declared PSNR budget do not match computation; the comparison does not isolate surrogate structure from extra reader evaluations. Codec/generic controls share the F6 reader count and narrow that explanation, but their operators still differ. Do not describe a matched-compute experiment.

Achieved paired quality is a separate comparison. Equal PSNR target does not guarantee equal final PSNR/LPIPS, and a passing paired median margin does not imply every image is quality-matched. Report distributions and paired deltas. Round1 retains its primary ablation and retained-F5 quality conditions. Round3-proposed instead requires gains versus retained and budget F5, quality comparison versus budget F5, and strict clean quality/F for candidate and budget control; ablation gains/quality remain reported secondary outcomes. A secondary ablation tie need not defeat proposed-profile GO, but it limits the mechanism claim. Do not soften 12/16 or switch profiles to resolve an inconvenient contrast.

## Why the x0 gradient is plausible, and why it can still fail

For the implemented R0/R1 epsilon-prediction surrogate, write `z=E(x)`, `z_t=a z+b epsilon`, with `a=sqrt(alpha_bar)` and `b=sqrt(1-alpha_bar)`. Its estimated clean latent is

\[
\widehat z_0=\frac{z_t-b\epsilon_\theta(z_t,t,c)}{a}.
\]

Holding timestep, conditioning and sampled noise fixed, in ideal differentiable arithmetic,

\[
\frac{\partial\widehat z_0}{\partial z}
=I-bJ_{\epsilon_\theta}(z_t).
\]

The full image-to-loss derivative additionally passes through encoder, decode, resize, reader and loss. The denoiser Jacobian can attenuate, amplify or rotate a perturbation direction; the identity does not ensure survival. Detaching epsilon would leave only the identity term at this latent stage, so a nonzero total image gradient alone would not verify use of the denoiser derivative. The exported separate epsilon-input probe addresses that specific failure mode.

The equation does not supply a singular-value bound, identify a safe signal subspace or promise native multistep robustness. The surrogate uses a posterior mode and float resizing, one sampled timestep and one denoiser evaluation. A later sampled timestep receives a newly noised encoding, not the actual intermediate state reached by earlier native steps. Native evaluation includes the native encoder sampling, scheduler trajectory and saved RGB8 processing. Repeated state-dependent Jacobians, nonlinearities, decoder behavior and quantization can erase a direction that the one-step objective favors. fp16 casts and finite precision further limit the ideal derivative argument. K3's native stochastic DDPM/MoVQ chain is evaluated but is absent from these writer gradients.

**First-step parity is a forward operator check conditional on a captured native noisy latent.** It checks conditioning, epsilon and x0 arithmetic at that point. It does not compare the complete writer preprocessing/posterior with native input formation; it does not validate a full attack gradient or the backward implementation numerically; and it does not certify later trajectory behavior. Exact C0 replay establishes reproducible native randomness/output, not that the surrogate models the native attack. Passing both supports implementation qualification within their scopes, not a promised scientific result.

## Diagnostics already exported: use and limits

The following fields exist in the current [writer](../../../scripts/tifs_writer.py), [denoiser helper](../../../scripts/tifs_denoiser.py), [runtime](../../../scripts/tifs_stage_s.py) and [analyzer](../../../scripts/tifs_stage_s_analyze.py). This table asks for interpretation of existing records, not additional instrumentation.

| Existing record | What it helps distinguish | What it does not establish |
|---|---|---|
| `rehearsal-checks.jsonl` and `rehearsal-checks/<source>.json`: `projection_max_abs_error` | Differentiable tensor projection versus unchanged reader projection disagreement. | Native attack or semantic-label validity. |
| Same receipt: `clean_input_gradient_norm`, `gradient_checks` with variant/family/strength/loss/norm/seed | Zero/nonfinite surrogate or clean gradient; which tested cell/variant failed. Successful receipt also requires frozen parameters without accumulated gradients. | Gradient accuracy, conditioning of the full Jacobian, optimization convergence or efficacy. |
| Same receipt: `denoiser_gradient_checks[].epsilon_input_gradient_norm` | The tested epsilon output has a finite nonzero input-gradient probe; catches a detached denoiser that the x0 identity term could conceal. | Every denoiser direction being useful or accurate. |
| `native.jsonl`: `x0_native_first_step_parity` with exact-conditioning flag, epsilon/x0 errors and rounding bound | Native conditioning/operator mismatch at the captured R0/R1 first step. | Whole-pipeline primal equality or native multistep backward parity. |
| Native `tape`, `tape_receipt`, `native_parity` and exact RGB8 replay status | Missing/inconsistent random draws or failure to reproduce the native C0 output. | Independent seeds/sources, or elimination of all implementation bugs. |
| `clean.jsonl` `embedding_report`: budgets, schedule, `sampled_windows`, conditioning/precision, operation counts, payload, verification and seconds | Wrong configuration/stream/schedule, clean-read failure, or unexpectedly expensive actual writes. | A measured loss trajectory or measured full-attack gradient; neither is exported here. |
| Per-unit `status`, `error`, `seconds`, `memory`; forecast/capacity and resource-stop records | Technical exceptions and resource shortfall versus completed scientific observations. | An automatic forecast refresh after each P rung; current P uses a frozen forecast plus paid-deadline checks. |
| Analyzer `native_sources`, `gains`, `clean`, `paired_medians`, `negatives`, `threats`, `inventory`, `unusable_evidence` and bound-carrier delivery | Which measured conjunct failed and whether its evidence is complete; observed no-read versus absent/malformed record. | A causal diagnosis of failure from counts alone. |

A complete valid run with failed retention/quality/security gates supports failure of the tested method package. It does not prove that every implementation bug is absent. Conversely, diagnostics that pass while native gains fail are not contradictory: a correct differentiable surrogate can optimize the wrong approximation. Preserve the difference between “qualified implementation did not meet this screen” and “the surrogate mismatch has been experimentally isolated.”

## Thesis success and the unchanged article ceiling

The [article decision implementation](../../../scripts/tifs_article_decision.py) evaluates VINE-B independently of which thesis profile was chosen. Article conditional GO needs complete thesis GO, C/J loss no worse than one source in every cell, paired quality within its fixed margins, and the prescribed edge: both C/J gains of at least three in one foreign cell **or** paired median LPIPS improvement at least .002 **and** PSNR improvement at least 1 dB. These are fixed development thresholds, not inferential superiority/noninferiority tests.

| Exported article outcome, if later observed | Claim consequence |
|---|---|
| `F6_GO_ARTICLE_CONDITIONAL_GO` | The comparative development screen supports continuing the article route; novelty, fresh confirmation, human quality and broader binding generalization remain unresolved. No acceptance/publication probability follows. |
| `F6_GO_VINE_B_DOMINATES_ARTICLE_NO_GO` | The candidate meets its thesis screen but a viable baseline meets the reverse comparative edge. Preserve the thesis result; the proposed article edge fails. |
| `F6_GO_NO_ARTICLE_EDGE` | Thesis screen passed; the prescribed article advantage was not established. Distinguish mixed tradeoffs from numerical parity using the exported parity fields. |
| `F6_KILL_VINE_B_VIABLE_NOT_NOVEL` or `BOTH_FAIL` | Report the separate candidate/baseline failure pattern. A viable generic bound carrier is not itself a new contribution. |
| `INCOMPLETE` or `RESOURCE_STOP` | Article evidence is unresolved under the exported status. Do not reinterpret unavailable baseline evidence as a candidate advantage. |

The probability grids in [r3-gate-analysis.md](r3-gate-analysis.md) are hypothetical finite-sum sensitivity calculations; they neither predict this run nor convert observed counts into a probability that the method is correct. Seed-majority probabilities, paired-control dependence, cross-cell dependence and omitted gates prevent a single retention rate from identifying whole-package GO. Likewise the [126-hour middle planning scenario](../stage-p/round3-cost.md) is not a measured completion guarantee; a resource stop tests the approved computational envelope, not the scientific null.

The report should name the selected writer/budget and effective profile, disclose all eight planned candidates and attempted rungs, separate source counts from seeds, retain achieved quality and both F5 controls, state K3's selection exposure, and quote the exported package/article outcomes with their limiting conjuncts. F6 remains an image-domain writer with the unchanged reader; this development screen does not establish the proposal's latent insertion method, cryptographic authentication or lawful ownership.
