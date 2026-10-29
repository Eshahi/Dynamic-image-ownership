# Stage P: bounded development tuning before Stage S

STATUS: PRE-OUTPUT PROTOCOL; no scientific outputs exist. This file records a proposed server experiment, not a run approval or an approved gate amendment. The effective thesis profile remains `round1`; the round-2 F6-versus-VINE-B article rule is unchanged.

## Sources and isolation

The committed `source-manifest.json` and `source-manifest.sha256` define exactly 24 sources: the 60-source encoder-transfer development pool minus all four Stage S partitions (16 donors + 16 targets + 2 rehearsal donors + 2 rehearsal targets). Exclude the source-list's separate smoke array. Sort the remainder by lowercase SHA256 of UTF8(`tifs-stage-p-v1/20261029/` + source_uid), ties by source_uid. First 16 are tuning sources; last eight are a veto-only check partition. Both partitions remain development data. The phrase untouched check means untouched by this Stage P selection, not a new held-out confirmatory sample; these sources have prior development history.

Tuning order: 544, 1355, 902, 599, 370, 1779, 1637, 309, 723, 1180, 693, 508, 1397, 1670, 1398, 1323. Check order: 1785, 450, 1737, 1774, 1404, 30, 1408, 73. No replacement or reordering after outcomes. Every source retains its raw, canonical-PNG and RGB8 SHA256, UID, licence and provenance from the existing pool.

The manifest records metadata-only exclusion checks against all 36 Stage S identities/hashes, all 200 Phase B primary plus 40 reserve identifiers, the acquired Phase B 200-source raw/RGB8 hashes, and all 120 Stage C primary plus 40 reserve identifiers. All exact intersections are zero. Commons page IDs are namespaced and are never compared as bare COCO integers. No held-out images were opened. Phase B reserves and Stage C sources have no available SHA256: their Commons SHA1 values cannot be compared with the development SHA256 values. Therefore their identifier disjointness is established; their byte/pixel disjointness remains unverified until future approved acquisition. Hash disjointness cannot rule out perceptual duplicates.

No Stage P row enters a Stage S/Stage C numerator, denominator or confidence interval. No Stage S donor, target or rehearsal source is usable for Stage P calibration, timing-driven parameter selection or replacement. Stage C remains inaccessible except for identifier/hash exclusion metadata.

## Fixed search space

The executable search consists of eight candidates, all with K3 excluded from optimization:

| Candidate ID | Surrogate | Robust-stage PSNR target | Refine target |
|---|---|---:|---:|
| f6-noise-p52 | f6-noise | 52 | 58 |
| f6-noise-p46 | f6-noise | 46 | 58 |
| f6-noise-p42 | f6-noise | 42 | 58 |
| f6-noise-p38 | f6-noise | 38 | 58 |
| f6-x0-p52 | f6-x0 | 52 | 58 |
| f6-x0-p46 | f6-x0 | 46 | 58 |
| f6-x0-p42 | f6-x0 | 42 | 58 |
| f6-x0-p38 | f6-x0 | 38 | 58 |

Use 150 robust updates + 50 clean refinements, one EOT realization per update, two fragile writes, seven semantic views and unchanged F5 reader/config/profile, except the explicit surrogate and robust-budget fields. Other writer settings remain pinned in `stage-s/frozen-config.json`. Refinement stays 58 dB to avoid adding a second budget axis. There is no k-step, step-count, EOT-count, prompt, guidance, threshold, detector or latent-distribution search. Surrogate schedules/conditioning follow the round-3 writer specification. Shared writer random seeds use the existing source/update-derived stream; configuration ID never becomes an extra seed search axis. Native regeneration uses seeds 0, 1, 2.

K3-in is a deferred design proposal, not an executable ninth candidate. Its potential implementation would add K3's native conditioning and schedule to optimization and require a separately frozen allocation/cost before any Stage P output. It is unavailable in the present search and cannot be activated retrospectively. The recommended present package keeps K3 optimization-excluded. Because K3 outcomes rank Stage P candidates, K3 is **selection-seen** and must never be called selection-unseen or prospectively unseen. SD3.5 in Stage C remains the prospective unseen-family design.

All four native cells run at every rung: R0 .2, R1 .1, R1 .2, K3 .2. Keep the Stage S native preprocessing, scheduler, prompts, guidance, conditioning and paired C0 random-tape replay. The source is the unit; a source-positive C or J majority requires at least two positive seeds out of three. C and J use their existing distinct Stage S definitions. Do not replace J with an owner-only or code-presence endpoint.

## Allocation and recorded controls

| Phase | Cumulative tuning sources | Maximum candidates entering | Maximum survivors |
|---|---:|---:|---:|
| Rung 1 | first 4 | 8 | 4 |
| Rung 2 | first 8 | 4 | 2 |
| Rung 3 | all 16 | 2 | 1 |
| Check | separate 8 | nominated winner only | none; veto only |

Rows from earlier rungs are reused; later rungs add sources, not fresh seeds or rewrites. If fewer eligible candidates remain, advance all of them, up to the listed cap. Never promote an eliminated candidate because a later candidate fails. Candidate source-write maximum is 8*4 + 4*4 + 2*8 + 1*8 = 72; candidate native-attempt maximum is 72*4*3 = 864.

Run retained F5 r2 once on each source reached (at most 24 marks and 288 native attempts), with no edits to retained code/config/artifacts. The runtime uses one directory per candidate (candidate + C0), one shared retained-F5 control directory (F5 + C0), and separate finalist-budget control directories (f5-budget + C0). Thus C0 regeneration is duplicated across directories: count up to 136 C0 source-directory units and 1,632 C0 native attempts. Within a directory each source/cell/seed captures C0 once and replays its exact tape for its marked arm; matching deterministic settings produce paired draws across directories. Share retained-F5 results across candidates only when source/native settings, hashes, owner/profile and tape identity agree; never claim the duplicated C0 computation was cached globally. Candidate wrong-owner calls are required for every clean/native image; C0 receives the same F5 reader under alpha and beta owners. Save individual C/F outcomes, not just aggregate counts.

For proposal attribution, run a separately labelled `f5-budget` arm at each distinct finalist budget on all 16 tuning sources, then at the nominated budget on the eight check sources: at most 2*16 + 8 = 40 marks and 480 native attempts. If both finalists share a budget, reuse that budget control once per source. Its objective disables the surrogate and delegates to the retained F5 robust objective at the specified robust PSNR budget, with the same fixed refinement/fragile settings. Require a pure-mock equality/dispatch test at the original 52/58 budget before deployment; actual numerical equality remains a server verification item. Never rename this arm F5 r2 or alter retained F5. These controls are evaluated after the two finalists are fixed and before final winner nomination. Under a prospectively chosen proposed profile, their results determine finalist eligibility; they never revive an eliminated configuration or switch the profile. Under round1 they are reported as diagnostics and do not change winner selection. An inability to establish the chosen profile's comparator requirements blocks advancement, not permission to relax them.

The maximum scientific inventory is therefore 136 marked images (72 candidate + 24 retained F5 + 40 budget F5), 136 C0 source-directory units, and 3,264 native attempts (864 candidate + 288 retained F5 + 480 budget F5 + 1,632 repeated C0). There are only 24 unique original images; source-directory C0 units measure actual repeated work, not independent sources. Clean/native quality/read work, repeated owner calls, model setup, surrogate-gradient work, timing rehearsal and retrieval have additional costs. This count is not a GPU-hour prediction. Do not add T4/T5, secondary distortions, external baselines or binding ablations to Stage P; they stay required in Stage S. Accordingly Stage P cannot establish the thesis specificity/binding gate or the article rule.

## Eligibility, ranking and missingness

For each candidate at a rung require observed clean PSNR >35 dB, SSIM >.9 and LPIPS <.1 on **every** source, finite valid measurements, and clean F on at least ceil(15*n/16) sources. This gives 4/4, 8/8 and 15/16 at the three tuning rungs, and 8/8 on the independent check. Require zero observed C or F events across every applicable candidate wrong-owner and C0 alpha/beta clean/native call. A positive forbidden event is a scientific rejection. Missing quality, references, expected native attempts or required negative calls makes the candidate INCOMPLETE and prevents advancement; absence is never recorded as an observed negative. Do not silently delete a failed seed or source from the denominator. Existing journal retry policy is for the identical frozen unit only; no scientific seed/config substitution.

The effective gate profile is fixed by the user/Claude receipt **before any Stage P or Stage S scientific output**, with round1 the unchanged default. Never choose a profile after observing Stage P. In round1, paired quality parity against retained F5 is an additional eligibility condition at every rung. In a prospectively selected round3-proposed profile, rungs 1/2 use absolute quality and the same clean-F/negative conditions; rung 3 additionally requires the proposed f5-budget comparisons below before final nomination. The proposed profile cannot be enabled without the committed user decision.

Among complete candidates eligible under that one preselected profile, rank using this exact lexicographic key (descending unless stated otherwise):

1. Minimum of the six foreign source-majority counts: C and J in each of R1 .1, R1 .2, K3 .2.
2. Sum of those six counts.
3. Minimum of R0 .2 C and J counts.
4. Sum of R0 .2 C and J counts.
5. Lower median clean LPIPS.
6. Higher median clean PSNR.
7. Higher median clean SSIM.
8. Ascending literal candidate ID.

There is no outcome-dependent weight, endpoint switch, new cutoff, extra seed, extra rung or manual visual override. Quality tie-breaks are achieved saved-RGB8 measurements, not nominal writer PSNR targets. Do not infer achieved matching from equal target PSNR. Retained F5 quality parity and the proposed budget-control conditions are both reported; only the preselected profile determines eligibility. They do not generate separate winners or check-set candidates.

Compute effective-round1 compatibility at each rung using complete paired source differences versus retained F5: median(LPIPS_candidate - LPIPS_F5) <= .005 and median(PSNR_candidate - PSNR_F5) >= -1 dB. For R0 require C and J no more than one source below retained F5 at n=16; at n=8 check require no more than one source loss as a conservative small-screen diagnostic, with raw fractions reported. Round1 compatibility does not constitute the remaining Stage S ablation/binding/article gates. For round3-proposed finalist eligibility, require paired median LPIPS delta <=.005 and PSNR delta >=-1 dB versus `f5-budget`; require C and J gains at least 4/4/3 over that control in R1 .1/R1 .2/K3 .2 on n=16, as well as the retained-F5 gain requirements of the chosen Stage S profile. On the n=8 check use the prospectively scaled minima ceil(n*gain/16), namely 2/2/2. Report all achieved quality distributions and gains against both controls. These additional conditions apply only if the chosen proposed profile contains them, and its frozen config is authoritative if a pre-output integration correction is needed. Proposal profiles cannot become effective because a candidate fails round1 parity.

## Fixed futility and check rules

Rungs 1 and 2 allocate the search; their small counts do not themselves establish efficacy or futility. If no complete absolutely eligible candidate remains, stop with SCIENTIFIC_STOP when observed disqualifications exhaust the set, or INCOMPLETE when a missing required result could alter the survivor set. Do not move to Stage S. Resource exhaustion is RESOURCE_STOP and cannot become an efficacy result.

At rung 3 apply the chosen profile's full finalist eligibility conditions, then nominate exactly one winner by the ranking above, then freeze its full configuration, configuration hash, nomination time and tuning-row digest before any check read. No check image is marked or evaluated before this nomination. If the winner has either C or J below 12/16 in any foreign cell, stop before the check and Stage S. A minimum <=9/16 is labelled CLEARLY_BELOW_STAGE_S_BAR; 10/16 or 11/16 is BELOW_SCREEN_BAR. For context, under independent Bernoulli source majorities with p=.75, P[X<=9; n=16]=.0795573. This is a descriptive futility calibration, not a valid selection-adjusted p-value or a guarantee of future Stage S performance. All six endpoints and their dependence remain reported.

Also stop if either R0 C or J is below 12/16, or violates the retained-F5 R0 loss rule. These retention requirements protect the home-family capability; they do not replace the later Stage S rule. A failed required quality/control condition rejects a finalist before nomination or vetoes the nominated winner at check; it cannot trigger a post-check replacement or profile switch.

If tuning passes, evaluate that single fixed winner on the eight check sources. Require C>=6/8 and J>=6/8 in **each** foreign cell, C>=6/8 and J>=6/8 for R0, the strict per-source quality/clean-F/negative requirements above, and all necessary control rows. A foreign minimum <=3/8 is CLEARLY_BELOW_STAGE_S_BAR (P[X<=3; n=8,p=.75]=.0272980); 4/8 or 5/8 is BELOW_SCREEN_BAR. Six of eight is the same .75 target as 12/16, not evidence of exact predictive equivalence. Missing rows give INCOMPLETE. A failed check ends this Stage P search: no runner-up, retuning, check-to-tune migration, source replacement or best-seed selection. Passing the check permits a proposal to proceed, subject to the effective gate/authorization and resource rules; it does not approve execution or imply Stage S success.

## Selection output and Stage S consumption contract

Reuse `scripts/tifs_stage_s.py` runtime/journals/readers/quality/native replay through Stage P mode; do not fork an experiment framework. A candidate tuning directory has one immutable effective config and full16 tuning-source identity throughout all rungs. Its `stage_p` metadata binds configuration_id, complete parameter hash, gate_profile and full plan/manifest digest. The CLI rung filters only the first4/8/16 committed sources; it must never change journal identity, rewrite old records or run a source outside that prefix. A separate check directory/identity is created only after nomination, contains exactly the eight check sources, and binds the nomination receipt. Shared retained-F5 and per-budget control directories use the same source partition and independent immutable identities. Detect/quality use the actual active-source inventory; no threat/secondary stage is valid in Stage P.

Source schema contract: `tifs-stage-p-sources-v1`, `tune_sources` array of16 rows, `check_sources` array of8 rows, `data_split=development`, `held_out_allowed=false`; each row preserves Stage S-compatible source_id/source_uid/filename/raw_sha256/canonical_png_sha256/rgb8_sha256 and provenance. `tuning_rungs` records cumulative source counts and entrant/survivor maxima. Runtime may map the active partition to its existing donor list, but must not read targets from Stage S or invent targets. Check identity excludes every tune source. Validate the separate SHA256 sidecar against exact manifest bytes. The selection script is stdlib-only and reads saved structured outputs. It must validate manifest/configuration hashes, expected identities, explicit finite measurements, complete seed sets and negative inventories before writing a decision. It records every attempted configuration, including failed/incomplete/resource-stopped/eliminated configurations and all actual compute consumed. Disclose eight planned candidates, the number attempted, each rung's survivors, 16 tuning sources, eight check sources and the selection rule in thesis/article reporting; neither the tune nor check subset is confirmatory.

`stage-p/selected-config.json` is created only by analysis of real server results; no placeholder winner is committed. Required content: schema/version; protocol and source-manifest SHA256; parent frozen-config SHA256; exact source UIDs and role; ordered attempted candidate IDs with parameter hashes, rungs/status/rejection reasons; observed/missing counts; selected candidate ID and full writer overrides; pre-check nomination digest/time; check status; effective profile and approval-receipt reference if one exists; separate round1/proposed compatibility results; retained-F5 and f5-budget achieved quality deltas; per-cell C/J counts and gaps; completed evidence file digests; explicit `execution_authorized: false` and a machine-readable Stage S eligibility result. An analysis output never supplies human approval.

Only one selected writer configuration exists. Stage S may consume it only if the check passed and that configuration satisfies the effective approved profile's compatibility requirements. A candidate that fails the preselected profile's requirements is not usable. In particular, failure of round1 quality parity cannot be rescued by choosing a proposed profile after Stage P outcomes. User choice, when needed, must have been recorded by Claude before any server scientific output. No approval is inferred from this protocol or from a model-written selection JSON. The unchanged article rule remains independently evaluated.

If the user declines Stage P **before any Stage P scientific output**, Stage S may use the current frozen F6 default without a selection file. A completed, failed or incomplete Stage P must never be hidden by deleting/ignoring its selection file and silently running the original default. Keep the search record and stop for the planned user decision. Any future new search requires a new pre-output design; the eight check sources are then permanently selection-exposed.

## Prospective calibration and shared-session amendment

Before rung1 completes, run retained F5, noise52 and x052 on exactly the first two tuning sources (544,1355). These are ordinary tuning outputs, reused by rung1, not new sources or a separate validation set. Capture complete saved-image reader/quality rows, native C0 exact replay, x0 first-step conditioning/epsilon parity, gradient checks for each candidate variant and peak-memory/model-load timing. All three must be complete for a forecast; a scientific quality failure remains a failed candidate, not a missing timing row. The hard paid-clock deadline with one-hour collection reserve applies even before empirical timings exist.

The Stage P forecast uses the full136-mark upper allocation and actual calibration costs, including the slower measured candidate cost for every candidate and budget-control write, a1.5 factor in per-operation bounds, repeated model loads and invocation overhead. It covers P only. The full Stage S rehearsal and forecast occur after the winner is frozen; they include already elapsed setup, P and freeze time. No P forecast certifies the unmeasured VINE/WAM/threat workload. Failure of either resource forecast is RESOURCE_STOP, never a partial-inventory scientific result. No Stage S source is used for P calibration.
