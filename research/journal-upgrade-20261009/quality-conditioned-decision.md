# E3 decision: quality-conditioned BCH construction

2026-10-10. Codex method-design agent, gpt-6-astra/high. Select one development candidate, **E3-BCH59-Q080**, with the rule below frozen before its new T3 evaluation. This decision uses observed E1/E2 outcomes; its cached prerequisites are deliberately retrospective development selection. It supplies no independent validation, human verdict or lifecycle transition.

## Decision and mechanism

Retain the final E1 mark unchanged when it meets the existing strict clean quality predicate. Otherwise contract its complete residual once by the exact E2 factor 0.8. Never choose between outputs using detector results, a VAE endpoint, source identity or a dose search. Recheck the selected output and fail if its quality or clean payload is unacceptable. There is no third branch.

This is a different construction rule from E2's uniform contraction: its distortion intervention depends on the source/mark pair's measured perceptual quality. It spends an already acceptable distortion budget on channel margin rather than reducing every mark indiscriminately. This is not a new independent design family: E1, E2 and E3 remain image-domain BCH carrier variants. It does not reopen D3, change the BCH code, relax a threshold or retroactively promote E1.

E1 B completed all twelve (two inherited from A): strict quality 11/12, clean exact q/h/both 12/12, both VAE joint-q endpoints 12/12, negatives 0/72. Source 147498 alone failed LPIPS (.1167193279), despite PSNR 41.8577 and SSIM .9626128. E2's uniform contraction gave strict quality and clean exact q/h/both 12/12, SD1.5 VAE J 12/12, SDXL J 11/12 and negatives 0/72. It repaired 147498 to LPIPS .0761581957 with both VAE J true. But 6012 lost SDXL detection: five hard errors were BCH-correctable to the right q, while corrected-word score 8.3561064 was below 8.5661389 and recomputation 3.2850998 was below 5.3867723. This is insufficient delivered correlation, not a reason to accept a corrected codeword below threshold. E2 closes without T3.

These observations support a heterogeneous distortion/channel-margin hypothesis. They do not establish that the quality predicate predicts diffusion robustness. E3's already-known cached clean/VAE success is an engineering consistency check; only the still-unseen complete E3 T3 panel can now falsify its regeneration-preservation hypothesis on these development identities.

## Exact writer contract

Let x be the canonical RGB8 source and m the **final** E1 RGB8 output. Freeze the E1 writer schedule and initialization in `journal_bch_probe.py` at 4bbc427: two fixed semantic PGD/restoration stages, existing clean qualification, conditional nine-branch refinement, twenty logical steps, existing projection/acceptance rules and exact stationary shortcuts. This schedule receives the same intended q and operational h as before. No earlier intermediate or alternate mark may replace m.

Define `quality(x,z)` using the existing evaluator, metric implementations and pinned LPIPS weights: PSNR >35 dB, SSIM >.9 and LPIPS <.1, simultaneously. Infinite PSNR passes its component; absent, NaN or otherwise invalid metrics fail qualification. Threshold equality fails. No rounding of reported metric values precedes comparison.

```
m = fixed_E1_writer(x, q, h)  # Final RGB8 artifact, not a chosen checkpoint.
if execution_failed_or_no_final_artifact:
    return construction_failure
if quality(x, m):
    y = m
    branch = "retain"
else:
    d = int32(m) - int32(x)
    y = uint8(int32(x) + sign(d) * ((4 * abs(d) + 2) // 5))
    branch = "contract_once"
save_and_reload_RGB8(y)
if not quality(x, y):
    return quality_failure_with_saved_output
if normal_clean_detector(y) lacks exact q, exact h or both_match:
    return clean_payload_failure_with_saved_output
return y
```

The branch reads only the final E1 quality metrics. Detection verifies the selected output and can reject it, but cannot change the branch. A quality-passing mark with failed q/h is rejected unchanged; it does not receive contraction. A contracted mark with poor quality, poor clean decoding or later failed VAE/T3 is rejected without restoration, further optimization, dose fallback or source substitution. Quality measurement failure is an execution failure, not permission to contract blindly. E1's preserved invalid-quality initializer remains a usable final artifact only when the existing writer completed normally with `invalid_initializer_no_refinement`; E3 evaluates its own final quality and does not require E1 initializer qualification. Exceptions, OOM and unfinished sources cannot masquerade as this branch.

The integer contraction is exactly E2's, including rounding. Before rounding its MSE is .64 times E1's; after rounding its absolute residual cannot increase. Neither LPIPS, SSIM nor diffusion correlation has a corresponding monotonicity guarantee. Retain uses the original bytes and adds no image distortion. These are the only mathematical guarantees needed to motivate this allocation rule.

The writer is a generic source/mark-quality rule. Development source IDs may index experimental records, but must not appear in branch logic or a deployed lookup. The historical writer/evaluator uses original recorded 32-bit q and frozen clean-decoded operational h; h is still not asserted to be the originally embedded h. No selected output may redefine either target. The general writer interface accepts its declared q/h inputs; this experiment does not validate a new deployment payload-generation policy.

Detection remains fully source-blind: suspect RGB8, public OwnerID/profile, pinned CLIP and SD1.5 VAE encoder only. No original image, quality branch, source ID, clean message, clean detector result or cache enters detection. Keep the E1 carrier domain/profile bytes, shortened (59,32) BCH code, radius-five unique algebraic candidate, corrected-word score, recomputation branch, RC1 routing, instance channel and content predicates. Semantic thresholds remain 8.566138863740473 and 5.386772268905419; instance thresholds and content radii stay fixed. No candidate list is added to detection. The hypothetical sign-bound assumptions and public-construction limitation remain unmet; there is no new FPR or authentication claim.

## Finite development protocol

Only the same twelve development sources, original payloads, pinned models and official matched attack settings are eligible. Keep all planned sources and failures in denominators. All stages cost USD 0. Freeze ascending numeric source order: 1675,4795,6012,25394,80932,109798,134882,147498,177015,190676,468505,499768. Record committed implementation, command/config, paths, seeds, duration and outcome in ordinary run.json/dev-log records; no new execution infrastructure.

**A: cached CPU composition, 60 seconds inclusive, no GPU or model loading.** Evaluate the exact quality predicate from recorded E1 final clean metrics, choosing the entire E1 row for retain or corresponding final E2 row for contract. Verify ordinary identity, payload, condition and detector-config compatibility and final image existence. Record per-source branch, deciding metrics, chosen image, original run/row and whether each call is inherited. Use E1 Stage A final rows for its two sources and completed B final rows for the other ten. A contract row must explicitly trace to the same E1 final input and the fixed E2 rule. This is ordinary input consistency, not a bit-exact replay or a rehash audit.

Reuse all selected clean/VAE calls and their negative controls: 36 selected clean/VAE C1 conditions, 36 C0 and 36 wrong-owner calls. Do not concatenate parent negatives or claim these as 72 new detector calls. C0 pixels are method-independent but each counted call must have explicit selected lineage. Report construction/measurement reuse, zero new calls, and expected branch counts only after computing the rule. The known expected result is eleven retain and one contract; this is an expectation from observed metrics, not an implementation table. Require strict quality, clean exact q/h/both and SD1.5/SDXL J each 12/12, all D2-positive VAE identities retained, negatives 0/72, complete compatible records. Failure closes E3 at this stage until an actual implementation inconsistency is fixed; it does not authorize changing the rule to fit the table.

**B: decisive full matched T3, 900 seconds inclusive.** Use the existing scientific Stage C adapter with all 72 E3 C1 identities freshly generated, including retained E1 marks: twelve sources, strengths .1/.2, seeds 0..2, official SD1.5 DDIM20, CFG1, eta0, empty prompt and unchanged safety checker. Regenerating the complete panel gives a simple complete E3 run; repeated E1 A identities are reproducibility/retention checks, not independent samples. No inheritance of C1 T3 results in this stage. Matched retained C0 attack pixels may be reused, with fresh fixed-decoder calls; run wrong-owner calls on every available E3 output. Preserve safety blocks and missing/failed cells in planned denominators, without pre-checker substitution.

Require full planned Q and J >=36/36 at .1 and >=31/36 at .2. Preserve every D2 and frozen-F5 S/Q/J positive on the fixed comparator intersections, plus all measured E1 A positives for both sources (six per strength). On the fixed v5 comparison intersection require semantic S 29/29 and 28/28 versus v5 27/29 and 18/28. Report full 36-per-strength S/Q/J, exact lost/gained identities, available and blocked call counts, raw 59-bit error histograms, algebraic failure, corrected-q error, corrected-word/recomputed scores and content decisions. Failed algebraic decoding is not zero raw error. Require zero observed any-channel C0/wrong-owner detections and no unexplained missing call. A failure closes this fixed candidate; no second dose, quality cutoff, threshold, cap extension or alternate source panel follows automatically.

Use at most 10 GiB allocated GPU memory, actual available memory minus headroom if smaller, and sequential model work as in existing scripts. Budget RAM below 16 GiB and additional disk below 1 GiB. Caps include startup/model loads, calls and finalization. Inspect resource availability before execution; cap/OOM is a finite execution failure. CPU composition is expected to take seconds, and full T3 should fit the existing 900-second allocation; these are estimates, not measured E3 cost.

**C: only after B passes**, derive and freeze the finite T4/T5 preservation panel through the existing `m1_assess_terminal_e2e.py`, `m1_assess_dual_threats.py`, v5 dev-001 records and default threat definitions. T4/T5 acceptance cannot be inherited from source marks or VAE success. Their finite budget and panel must be fixed before that experiment; no such experiment runs now. Original M1a stays unchanged, including strict quality all twelve, clean both_match >=11, semantic superiority over v5 at both strengths, zero declared negatives and T4/T5 no worse than v5. E3's stricter prerequisites do not rewrite that contract. No M1b or confirmatory infrastructure before actual M1a passage.

## Cost and interpretation boundaries

The cached A cost is incremental CPU composition only, not end-to-end embedding cost. Report three separate quantities: E3's newly measured stage costs; reused ancestry costs; and any genuinely measured fresh writer cost. E1 A/B wall times were 185.100 and 811.908 seconds (996.008 combined, including their evaluations/T3/startup). E2 process time is 71.859 seconds; parent outer wall time is 72.6446495 seconds. E2 measured all twelve contractions/endpoints, so charging that total as E3's one contraction would be misleading. Do not add process and outer wall times or multiply reused calls into an effective sample size. Writer component timings may be extracted from existing rows as an explicitly historical estimate, never reported as a newly timed E3 writer.

No fresh E1 writer rerun is required to decide B. If end-to-end cost/reproducibility later needs direct characterization, use the same generic writer contract and a separate all-twelve 4,200-second inclusive construction/clean/VAE cap, with zero added refinements or repairs; T3 retains its own 900-second cap. This freezes a bounded future characterization, not an instruction to run it before the cheapest decisive T3. A cached composition cannot establish fresh-writer timing, general-source quality or deployment performance.

New T3 can falsify the untested claim that the quality-conditioned selected marks retain every required regeneration positive, especially the contracted source never tested under E3 diffusion. It can also expose fragile routing/content loss or negative detections. Passing would establish only this selected image-domain writer's development performance under the frozen channels. The diffusion-aware E1 ancestry already optimized these six seeds; the full T3 is not held-out or independent support, even where new output pixels are generated. Neither outcome isolates ECC versus antipodal geometry, establishes population FPR, human admissibility, native latent robustness or cryptographic ownership. E1 and E2 remain failed candidates, and this is not a three-family negative exit.

Inspected: authoritative MAIN STATE once; `coded-carrier-decision.md`; `e1-quality-decision.md`; completed E2 rows/summary/run at MAIN `.thesis-build/dev-runs/20261010-1410-e2-attenuation-screen` (f7fb94e); `journal_bch_probe.py`, `journal_bch_attenuation.py`, `journal_bch_t3_screen.py` and source-blind readout interface. This decision derives an allocation rule without relying on new literature claims. This agent writes only this file; no GPU, code, state, log, protected file or commit changes.
