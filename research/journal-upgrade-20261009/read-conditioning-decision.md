# Decision: a separate read-conditioned instance decoder

2026-10-10. Codex method-design agent, gpt-6-astra, high effort. This is a bounded development decision, written after an auxiliary diagnosis and incomplete R1–R4 results. It is not a prospective interpretation of the already running screen, an official gate change, or independent confirmation. No code, run output, shared state, threshold, protected file or historical F5 result is changed by this document.

## Decision and activation condition

**Finish all four original configurations under their frozen decoder first. If an original survivor exists, prioritize its original follow-up protocol. Only if no complete original configuration survives, activate the two new configurations below.** Missing configurations are unresolved, not demonstrated failures. The compute amendment governs completion of the old screen; this decision neither spends its unused budget on extra tuning nor excuses any old failure.

The justified repair is to condition the fragile reader on the semantic code actually read from the suspect, whenever that semantic read crosses the existing searched threshold. Name the resulting method **F5-RC1** and retain F5 r2 as a separate frozen comparator. Do not adjust the fragile write to the suspect's recomputed q, optimize a joint CLIP-sign preservation loss, search alternate conditioning codes, change h targets, or loosen thresholds in this round.

The new method fixes a writer/reader interface mismatch. It does not authenticate the declared owner, establish that h was historically intended, or resolve semantic collisions. Its empirical motivation is post hoc and must remain disclosed.

## Evidence inspected and its limits

Inspected code: `scripts/f5_latent_codec.py:detect_rgb` and `_semantic_status`; `scripts/revised_watermark_v5.py:_instance_table`, `_Fragile`, `_key_test`, `_channel_result`; `scripts/journal_readability_probe.py:payload`, `restore_fragile`, and screen execution; `scripts/journal_binding_probe.py:synthesize` and same-signal binding ablation. The readability, payload-definition and compute amendments are jointly authoritative for the original experiment; the latter two supersede its incorrect original-payload feasibility statement and original compute cap respectively. This decision relies on direct algebra and local source inspection, not a new literature claim.

MAIN denotes `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5`. The completed auxiliary snapshot at MAIN `.thesis-build/dev-runs/20261010-1003-instance-diagnostic-snapshot`, commit `2b9ef69`, reproduces native extraction and reports:

| Images | Diagnosed | Native exact readable h | Forced intended-q exact readable h | Forced decoded-q exact readable h |
|---|---:|---:|---:|---:|
| Frozen F5 clean | 12/12 | 12/12 | 8/12 | 8/12 |
| R1 clean | 12/12 | 9/12 | 12/12 | 12/12 |
| R2 clean, incomplete | 9/12 | 7/9 | 9/9 | 9/9 |

R3 and R4 have no diagnosed rows in that snapshot. These are exact-readable **h** results, not full configuration passes. The parent reports R1 joint semantic q counts of 11/12 SD1.5 and 3/12 SDXL, and 9/9 in each channel for the incomplete R2 subset. This author does not extrapolate the missing three R2 sources. The original screen at `6a25cd5` remains running and unaltered.

Update received from the parent after this document's initial write: R2 is now complete, with strict clean quality 12/12, clean/SD1.5/SDXL joint q 12/12 each, zero negatives in 72 calls, but only 9/12 clean combined eligibility because of h. R1 has clean q 12/12, strict quality 12/12 and clean combined eligibility 9/12; R3 has just started and R4 is unrun. These are parent-reported ongoing-run counts, not a newly inspected completed snapshot. They strengthen the routing hypothesis without changing the two configurations or permitting early activation. All four original configurations must still finish.

The frozen clean h target is defined by native clean extraction. Its 12/12 native agreement is therefore partly definitional. Forced-q extraction on those old pixels need not recover it: the old writer could have used a different conditioning code, and its original h was not recorded. In contrast, each new R image explicitly writes the declared original-q/operational-h pair. Recovery of that pair using the matching table on R pixels is an identifiable delivery test. The diagnostic supports a routing explanation for the observed h failures; it does not prove future robustness or original-payload recovery.

Frozen F5 remains historically clean/SD1.5/SDXL intended-q joint exact 10/11/3 of 12, versus its native checked counts 12/12/10. The historical M1a counts 29/28 versus v5 27/18 use eligible denominators 29/28 and do not become 36-per-strength results by relabeling.

## Mechanism and rejected alternatives

Let `t[j,q_j,h_j]` be the independent-domain ten-chip instance pattern for segment j. The new writer restores `t[j,q_target_j,h_target_j]`. The frozen reader uses decoded semantic q only on found semantic content mismatch; otherwise it chooses recomputed `q_now`. Soft semantic matching can accept content while some signs in `q_now` differ from the carried q. Thus content agreement is being used to select a physically different codebook.

If a chip vector is approximately `a*t[j,q_target_j,h_target_j] + n_j`, the correctly conditioned raw bit gap has signal term `a*(10 - dot(t_correct,t_other))`. With the wrong q bit, both offered h patterns are different pseudorandom patterns; their signal gaps have no corresponding positive mean under an independent-sign idealization. One q sign change can therefore erase evidence for one h bit even though the semantic payload is readable and content matches. This is a model explanation, not a measured independent Gaussian noise law or a guarantee for a fixed table.

Read conditioning makes the physical codebook depend on transmitted evidence and leaves content checking to the content predicates. It uses no target or original source at detection. When semantic q is wrongly decoded, its errors can still propagate into h extraction; read is not a guarantee of exactness. This is why exact q and h remain separate measured endpoints.

Writing fragile chips against pre-write `q_now` would retain the old decoder but change which semantic message the instance tier binds to. The write can itself move `q_now`; solving that fixed point needs extra passes or adaptive stopping. It also makes donor transfer comparisons depend on recipient recomputation. No such schedule is selected here. Jointly forcing all CLIP projection signs to remain equal to q_target would attack the quantization instability rather than the interface, introduce another loss and expensive gradient path, and still require survival of those signs after transformation. Neither alternative is disproved; both are excluded from this bounded test because the existing diagnostic already supplies the cheaper mechanistic intervention.

## Exact new decoder contract

Retain semantic extraction, semantic content checking, instance h checking, status propagation, decision table, all radii and numerical thresholds, owner roster, carrier projections, bit tables, models and profile unchanged. Replace only the codebook routing:

```text
if semantic.read:
    q_bound = semantic.decoded_code
    routing = "decoded_semantic_read"
else:
    q_bound = q_now
    routing = "suspect_semantic_recomputed"
```

Run exactly one instance-table extraction with that q_bound. Do not fall back to another q when h fails; do not select the higher score, enumerate Hamming neighbors, consult q_target/h_target, or use source features. The rule is independent of binding mode and content-match status, so all ablations can share the same extracted signals. Recomputed-only semantic presence cannot select a noisy best-decoded q. Retain h_now as the existing suspect-derived h comparison and tie-break code; do not replace it with h_target.

Expose the method/routing revision separately from the existing profile/configuration bytes: changing those bytes would rederive the pseudorandom patterns and invalidate cached images. Record semantic read, q_now, decoded q, q_bound, routing, instance scores, h_now, decoded h, and content statuses. The payload targets appear only in writer/evaluator records. The detector's side information remains public owner/profile, pinned CLIP weights and pinned SD1.5 encoder. SDXL remains an embedding-time seen development channel, not additional detector side information. No owner secret or original image is introduced.

## Two fixed new configurations and cached-pixel use

Freeze these choices before running the new decoder, including before evaluating cached outputs with it:

| New configuration | Exact existing writer schedule | Decoder |
|---|---|---|
| RC2 | R2: identity + SDXL, additional 52 dB, 100 logical steps, one final fixed q/h fragile restoration | F5-RC1 |
| RC3 | R3: identity + SD1.5 + SDXL, additional 52 dB, 100 logical steps, one final fixed q/h fragile restoration | F5-RC1 |

R2's incomplete success motivates RC2, so it is explicitly outcome-informed development. RC3 tests whether adding the matched SD1.5 branch protects continuity at the same perturbation budget. No RC1/R1 or RC4/R4 candidate, per-source mix, new strength, further robust pass, third new schedule or best-checkpoint selection is allowed. R4 results remain informative about the old embedding-only family, not an undeclared reserve candidate.

Reuse complete saved R2/R3 clean and VAE pixels: their deterministic writer objectives and final restoration do not depend on decoder routing. A new decoder does not require gratuitous re-optimization of identical pixels. Reuse saved clean quality too, with explicit source-record links. However, recompute every detector call under F5-RC1, including all C0 and wrong-owner controls; do not combine new positive calls with old negative calls. Retain a new run record and new method-labelled results, code committed before evaluation. Old outputs are immutable. This is a paired post-hoc decoder intervention on development data, not an independent validation sample. Running the same pixels again cannot cure selection bias.

On each cached image retain frozen/native and F5-RC1 outcomes side by side where available. Re-read the frozen clean C1 set with F5-RC1 as a descriptive compatibility control, without modifying its marks or expecting preservation of native operational h. A detector-only loss on these old images does not get hidden, but those pixels are not the RC2/RC3 writer output. Forced-target diagnostics remain auxiliary and cannot certify the new detector.

## Prospective advancement and kill rules

Use all twelve fixed development IDs and all three existing conditions. Each new configuration must meet exactly the existing strict screen: clean PSNR >35, SSIM >.9 and LPIPS <.1 on all twelve; both read flags, exact declared q/h and `both_match` on all twelve; SD1.5 joint exact-q/read/content 12/12; SDXL at least 11/12; zero any-channel detections in every declared C0 and wrong-owner call. No missing row may be dropped. Rounding/restoration and h content mismatch remain genuine failure routes.

Both complete configurations are evaluated before ranking. Rank survivors by SDXL joint exact-q count, then minimum fixed-q score over both VAE conditions/all sources, then lower mean clean LPIPS, then RC2 before RC3. This retains the old selector's logic without choosing source-specific winners. Select at most one final global configuration. If neither survives, kill this amendment and report its ceiling; do not reinterpret a forced read, fallback match or h-only success as passage. This is failure of this repair experiment, not a proof against all latent-watermark methods.

The cheapest decisive next computation is the paired cached-image decoder screen, before any new diffusion synthesis. It needs no optimization, new dataset or new runner. If a survivor fails a later test, retain the failure and try only the next pre-ranked survivor. Implementation bugs may be repaired transparently before a fresh result; changing scientific parameters after a failure requires a separately declared future design and cannot be presented as part of this finite test.

## Matched T3, T4 and T5 follow-up

For each advancing survivor, use exactly the retained matched SD1.5 DDIM img2img identities, strengths .1/.2, seeds 0–2, all twelve sources: 72 marked attacks. Reuse matching deterministic C0 attack pixels. Reuse C1 attack pixels only if they already exist for byte-identical candidate marks and pinned attack identities; changing the decoder alone does not alter the attack. Otherwise generate them once. No held-out images, new attack strengths or JPEG/crop work.

Evaluate the new method and its paired frozen-decoder intervention on those candidate pixels. Compare with retained frozen F5 and v5 on the original matched identities. Use the existing terminal and dual-threat assessors with explicit new method labels and unchanged endpoint meanings. Require the original M1a advantage over v5 at both strengths, no loss against frozen F5 semantic success on the historical eligible pairs, and no loss of exact-q readable/checked successes on same-identity frozen results wherever available. Report all 36-per-strength counts and the separate eligible paired counts. Retain semantic checked, assumed/recomputed-only, exact readable q, full acceptance and h delivery separately; no requirement that the fragile h survive diffusion is invented. Zero negative calls remains mandatory. The new method can earn development continuity, never retroactively replace the historical M1a/M2 verdict.

Repeat existing T4/T5 development identities with candidate donor marks, same ownership exclusions and residual scales .5/1, all original controls and no new threshold. Require no new false donor full attribution, no T5 false match, and no decline in matched donor semantic/both delivery against the frozen controls; report both delivered and attempted denominators even if zero. Rejection caused by unreadability cannot count as stronger binding.

For the six fixed public donor-synthesis pairs, first run the new decoder on all 31 saved binding-probe images as an inexpensive paired stress test. In this cached comparison retain the exact original synthesis targets from those rows (decoded-donor provenance), including any difference from intended q. Require no new false acceptance and retention of each of the five previously exact both-tier deliveries with positive same-signal disabled-binding read controls before claiming preservation of that specific historical binding evidence. Failure is a binding-continuity failure for this bounded method, not a reason to redefine delivery.

Then repeat the same six donor/recipient identities using the final candidate's declared intended q and operational h. This is a **new payload-origin arm**, not automatically the same five-of-six denominator. Fix donor targets before recipient synthesis. Use the existing public fixed-payload synthesis once to initialize the recipient, then the selected RC2/RC3 refinement once with exactly its declared objective/budget/steps and one final fixed fragile restoration; C0 recipient supplies the same total-quality constraint. No query-driven retries or replacement pairs. Record base synthesis and added refinement distortion separately. Require at least five exact both-tier delivered attempts and rejection of every exact delivery, with positive same-signal disabled read controls. Also report acceptance across all attempts, per-tier delivery, own-h rejection before semantic propagation, LPIPS <=.20/.30 proxy subsets, and all failed or inadmissible attempts. Less than five is insufficient delivered-binding evidence for advancement in this bounded protocol, even when all delivered attempts reject.

Use the identical extracted q/h signals for semantic-only, h-only and combined predicate ablations, keeping routing fixed. Report whether h independently rejects, whether semantic binding alone already rejects everything, and whether combined checking adds any observed rejection. Do not claim a combined benefit when none is measured. Repeat or re-evaluate the existing public-recipient construction demonstration separately: public recipient re-embedding remains a known authorization counterexample. Neither successful rejection of donor payloads nor a repaired decoder removes it.

## Search, FPR and calibration consequences

The semantic search remains 2^32 messages. For a **fixed conditioning q**, instance search remains 2^32 h values over 320 chips, with the same two offered ten-chip patterns per segment. F5-RC1 executes one q route, not a maximum over two q routes or 2^64 explicit candidates. It adds no payload bits, redundancy or source-side detector information. Any route which tried q_now and decoded q and accepted either would add a multiple-testing issue; that route is forbidden.

Nevertheless, one executed route does not prove the old null bound. The selected q is data-dependent, derived from the same image under a public profile. Under an ideal model where the selected q and instance projections are jointly independent of the domain-separated instance codebook, conditioning on that selection would retain the fixed-q 2^32 search argument. The actual fixed public codebook, carrier selection, shared image statistics and adaptive attacker do not establish that model. An unconditional finite-pattern union argument could range over all 2^32 q values and 2^32 h values, plus recomputed tests; its nominal multiplicity can be as large as 2^64 for the searched tier. That is a conservative accounting possibility, not a claim that this decoder searches 2^64 or that the bound is tight. Even such a bound needs the underlying random-sign/null assumptions and cannot certify adversarial public construction.

Keep 8.259326826136963/4.982033056390042 and roster one as **frozen exploratory numerical thresholds**. Their existing per-channel bound fields are legacy model-based statistics, not a newly validated system FPR certificate; flag that in new outputs/reporting. Do not assert nominal .001 or 1e-6 system FPR from this screen. Any-channel acceptance is a union across channels, fallback paths and tested owners; those factors also need explicit accounting. Negative C0/wrong-owner calls reuse sources and transformations and are correlated. Zero observed detections here is a development kill criterion, not population calibration.

A new independent calibration and subsequent untouched confirmation are required before population error or matched-FPR baseline claims: freeze the candidate and routed statistic first, then use a separately fixed non-held-out calibration panel and predeclare the owner roster, channel union, image-level endpoint, threshold-selection method and confidence bounds. Evaluate the calibrated rule on untouched confirmation data only after its authorized stage. Do not inspect or create those data/manifests now. Existing WAM native exact 12/5/7 and mean clean PSNR 38.32 are contextual baselines, not matched-FPR superiority. If calibration later demands a stricter threshold, it creates a new version needing performance checks; this document permits no threshold relaxation to rescue development outcomes.

## What a successful result would mean

Success would support a narrow claim: on twelve reused development sources, a declared pixel-refinement writer and a source-blind read-conditioned fragile decoder improve exact semantic delivery through the tested VAE channels while retaining the specified clean, matched T3 and binding checks. It would distinguish routing loss from physical fragile-payload loss on paired pixels. It would not verify an unknown original h, prove generalization, authenticate ownership, demonstrate a latent-generation method, certify population FPR, establish full SDXL diffusion robustness or validate the historical method under a new endpoint. Freeze a successful candidate before any fresh development panel or calibration; leave frozen F5 and all failed screens intact.
