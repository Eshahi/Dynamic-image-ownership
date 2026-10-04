# A hybrid source-bypass: fixed development threats

The twelve-source hybrid amendment preserves clean numerical image quality on 12/12 sources, but clean authoritative `both_match` is 10/12. Semantic found/content-match survives VAE on 12/12 and diffusion strength .05 on 36/36 source/seed conditions; it falls to 3/36 at .1 and zero at .2/.4, with safety-blocked conditions retained. T4/T5 public transfers produce no `both_match`, but independent delivery controls and adequate semantic-near coverage are absent. This package does not establish joint threat support, secure ownership, a causal three-state detector, or superiority over v5.

This is an authored descriptive report, not the independent M1 milestone review. No threshold, algorithm, old output, shared state, or experiment was changed. All work here was CPU metadata/hash inspection.

## Exact receipts and fixed denominators

Source directory in MAIN: `.thesis-build/dev-runs/20261004-0900-A-hybrid-threats`; commit `9267e6e4879c7f9101dee9ca75ecc49195b6aa94`, elapsed 1093.156 s, outcome **incomplete**. Analysis: `.thesis-build/dev-runs/20261004-0920-A-hybrid-threat-analysis`; commit `af32f3d59f9144a1fd27c4dc8b676207c42fb5ff`, elapsed .110 s, outcome **incomplete**. The analyzer's retained error is `Source run not completed: incomplete`; there are 472 complete source conditions/records and 17 failed planned conditions, not an empty or rejected inventory.

| Receipt | SHA-256 |
|---|---|
| Assessment run.json | `7929d9cbbf7a9314f7959d85144fe26d99324ffd7ecc10e40455f5f623ce07a6` |
| Assessment conditions.json | `404aefbe30d934b8405732cf62a3765da4550fba30e5ee7f4030a11eeb5a5b4e` |
| Assessment rows.jsonl | `13747e628e09ee2af1903c89236bff2b6bc6a7d3d95555805e7732833a44795f` |
| Assessment journal.jsonl | `859c98eef4bfa7d38608701624b52c28ccc894bc52b995394cb49ed76f8fe2e8` |
| Frozen assessment manifest | `7ff2ba30bf0004c5abc2f5ac33b2ddd60da1d69140def2c586bdbf5013ac52c6` |
| Analysis run.json | `e2f8bf1e5eae181b3c76ac52a494e6ceee3f0a82041744ba6395cb9b8cd0c728` |
| Analysis conditions.csv | `023c9f91639f260d9d61f6b82c50572d987239e64ef7b2253d0fb93d3d0f71e0` |
| Analysis summary.csv | `d1fb594ffed193745f423112342258534fd45c6379d9aaaaf125a7d6360971a6` |
| Analysis missing-or-failed.csv | `6243353ba9580cd1d156690d41d5312ea10967789a196bba3753fe1847796e99` |
| Frozen agent semantic labels | `89dd92ebbd1c0807880178146ae1ff7dd5b1dfb682229f45a7524656b6f7ceae` |

All six analyzer input hashes, four declared analysis output hashes, three assessment output hashes, and 406 retained PNG hashes were independently verified. The four chronological enrollment run receipts also match: pilot `0e56178cbdf483ac790bef3c2b575ca9e072b3a4ca0f65a93a4a20f93848a677`; old2 `8c435eeaf94bae86ab476692f4a2894606fe588f538560e71b2765da1d56da4d`; recovery4a `e7fcedbaf644a3a557dd9ba817e272fca183c6a3b886ecf5b3a54ea03bfd0d8c`; recovery4b `7a3f110221e68fec463f74e54ac00dff311bee85de6ad27e65efdec3bea77eab`. Different initialization/recovery histories remain in those enrollment records; no best-shard selection was made.

The fixed inventory is 489: clean24, T3 312, T4 80, T5 component pairs66, same-topic T5 transfers7. Of 423 planned image conditions,406 completed; these supply1624/1692 planned owner calls, with68 calls missing. The66 component pairs are complete. Independent development units are12 source images; diffusion seeds, overlapping pairs and four owner calls on one suspect are dependent repetitions.

Every failure is `safety_checker_blocked_output`, on source6012 only. For C0, all three seeds at .1/.2/.4 are blocked (nine). For C1, all three at .1/.2 are blocked, and seeds0/2 at .4 are blocked (eight); .4 seed1 completes. No blocked image is replaced by a success, a negative detector call, or a black image. Both final outcome receipts remain incomplete.

## Clean behavior and suspect-only extraction

The selected operator is `hybrid-source-bypass`: source plus decoded latent displacement, clipped to RGB8. Its matched C0 equals the saved canonical source, so clean paired-family and source-preservation qualities coincide here. This source bypass is an explicit amendment, not pure latent decoding or an initial-noise method. The unchanged image-DCT/CLIP verifier recomputes CLIP from each saved suspect on CPU, with no inversion, VAE, original/reference image, or enrollment vector supplied to verification. Public OwnerID/profile/weights are side information.

| Source | PSNR dB | SSIM | LPIPS | Clean alpha outcome | Semantic/instance C0→C1 drift |
|---:|---:|---:|---:|---|---|
| 1675 | 38.628993 | .985181 | .007618 | both_match | 0 / 3 |
| 4795 | 38.255458 | .982948 | .009204 | both_match | 0 / 1 |
| 6012 | 38.104299 | .985960 | .005320 | content_uncertain | 1 / 3 |
| 25394 | 39.430214 | .982597 | .007273 | both_match | 1 / 0 |
| 80932 | 38.010706 | .974569 | .011308 | both_match | 0 / 0 |
| 109798 | 38.268541 | .986129 | .005699 | content_uncertain | 0 / 4 |
| 134882 | 38.745634 | .983454 | .006656 | both_match | 0 / 1 |
| 147498 | 39.371580 | .988323 | .006155 | both_match | 0 / 2 |
| 177015 | 38.603938 | .975385 | .007370 | both_match | 1 / 1 |
| 190676 | 37.698296 | .985431 | .006619 | both_match | 1 / 0 |
| 468505 | 37.464439 | .987455 | .006895 | both_match | 0 / 0 |
| 499768 | 36.721392 | .983821 | .008779 | both_match | 0 / 0 |

All12 satisfy strict PSNR>35,SSIM>.9,LPIPS<.1. Mean/median/sample SD/range are PSNR38.275291/38.261999/.768394/36.721392–39.430214; SSIM.983438/.984501/.004319/.974569–.988323; LPIPS.007408/.007084/.001670/.005320–.011308. Same-instance semantic drift is0–1 (mean.333333), instance drift0–4 (mean1.25), satisfying the <=6 component condition on all12.

Both clean abstentions have semantic found/content-match and instance found, but instance content-match is false:6012 corrected distance6.098384,1097986.168396. Thus a successful component-drift check does not guarantee authoritative joint decoding. Clean alpha semantic-match is12/12, instance-match10/12, outcome both_match10/12 and abstain2/12. All48 clean C0 calls and36 clean C1 wrong-owner calls are negative. Across all406 completed images, all1218 wrong-owner calls have zero watermark_found and zero both_match. This small dependent control set does not calibrate a population FPR.

## T3: full planned strata, no favorable-dose pooling

Attacks use pinned SD1.5 DDIM20, empty prompts, CFG1, eta0 and fresh seeds0/1/2; VAE mode is deterministic. Semantic success below requires both `semantic.found` and `content_match`; joint detection is the authoritative `both_match` outcome, not two separately counted marginals.

| C1 stratum | Planned / complete | Semantic success | both_match | semantic_only | neither_match | Missing | All-seed semantic source groups /12 |
|---|---:|---:|---:|---:|---:|---:|---:|
| VAE mode | 12 /12 | 12 | 5 | 7 | 0 | 0 | 12 |
| Diffusion .05 | 36 /36 | 36 | 11 | 25 | 0 | 0 | 12 |
| Diffusion .1 | 36 /33 | 3 | 0 | 3 | 30 | 3 | 0 |
| Diffusion .2 | 36 /33 | 0 | 0 | 0 | 33 | 3 | 0 |
| Diffusion .4 | 36 /34 | 0 | 0 | 0 | 34 | 2 | 0 |

All three .1 survivors are (source,seed)80932/2,468505/1,468505/2, with same-arm CLIP.975045,.950167,.979133. Thus .1 has no source with success on all three planned seeds, even though three individual conditions survive. Missing safety outputs remain in36. No observed genuine regenerated C1 is labelled content_mismatch, but `both_match` persists on5 VAE and11 .05 conditions, so the operational labels do not identify regeneration history. Human retention remains missing.

C0 complete counts are12/12 VAE,36/36 .05,33/36 .1,33/36 .2 and33/36 .4; all evaluated C0 owner calls are negative. Same-arm numerical quality conjunction is0 on every completed T3 C1 image. Mean PSNR and range: VAE25.337170 (19.700325–27.554250), .05 25.207509 (19.618245–27.463229), .1 23.903839 (18.994554–26.137891), .2 22.394010 (18.218372–24.867748), .4 19.999827 (16.956651–23.340278). These are attack-output fidelity metrics, distinct from clean embedding admissibility.

The exploratory semantic-match AND same-arm CLIP>=.85 counts equal12/36/3/0/0 in that stratum order; they also equal those counts at.90. Every completed .1 C1 has CLIP>=.950167 and every .2 C1>=.918628 despite broad/no semantic watermark recovery. These are numerical content-retention proxies and removal observations, not human-confirmed retention or survival at strict pixel-quality parity. No new threshold was selected.

## T4: completed transfers, restricted security interpretation

All80 planned attempts complete:20 directed donor-recipient pairs for each arm, covering10 donors/recipients; public constructions use zero detector queries. Quality is against the recipient's matched C0. All combined both_match counts are zero.

| Arm | Attempts | Strict recipient quality | Semantic found | Semantic content-match | Semantic match AND quality | Combined both_match | Alpha outcomes |
|---|---:|---:|---:|---:|---:|---:|---|
| Donor residual ×.5 | 20 | 20 | 6 | 1 | 1 | 0 | mismatch1, uncertain4, neither14, semantic_only1 |
| Donor residual ×1 | 20 | 18 | 8 | 1 | 1 | 0 | mismatch8, uncertain2, neither10 |
| Public projection | 20 | 19 | 20 | 6 | 5 | 0 | mismatch16, semantic_only4 |
| C0 projection sham | 20 | 19 | 0 | 0 | 0 | 0 | neither20 |

These counts reveal transferred semantic evidence, including four public-projection semantic_only outcomes, without full joint donor acceptance. However, this assessor runs only combined verification for four owners. It does **not** retain v5's separate binding=none delivery call or semantic_only/perceptual_only ablation calls. Semantic found is a disclosed channel observation, not an interchangeable independent delivery denominator. Therefore the frozen T4 criterion requiring admissible delivered examples spanning at least10 recipients is not established here. Zero combined acceptance without that delivery/control evidence is insufficient for secure-forgery-resistance support, particularly with public keys and no adaptive attacker search. The sham provides a useful negative construction but does not fill the missing binding-mode controls.

## T5: frozen agent labels and component separation

All66 pairs remain:7 same-topic,57 different,2 uncertain. Labels are frozen agent judgments, not human ground truth. The retained v5 criterion is at least5 same pairs with semantic Hamming q<=6 AND instance Hamming H>6, at least5 different pairs, all12 same-instance q/H<=6 and no joint near-collision among same pairs. Same-topic coverage is only2/7 in both A C0 and C1; minimum5 is unmet. Zero joint near-collisions is not meaningful security support without adequate semantic-near coverage.

| Same-topic pair | C0 q /H | A C1 q /H | Meets q<=6,H>6 after marking |
|---|---|---|---|
| 1675–4795 | 9 /14 | 9 /14 | No |
| 1675–134882 | 12 /19 | 12 /19 | No |
| 1675–177015 | 14 /17 | 15 /15 | No |
| 4795–134882 | 11 /17 | 11 /19 | No |
| 4795–177015 | 5 /11 | 6 /13 | Yes |
| 80932–468505 | 6 /14 | 6 /14 | Yes |
| 134882–177015 | 10 /14 | 11 /12 | No |

For same-topic pairs, C0→C1 mean q9.571429→10 (ranges5–14→6–15), mean H15.142857→15.142857 (11–19→12–19), mean CLIP.668570→.663777. Different-pair C0→C1 mean q11.245614→11.017544 (5–17 both), H15.947368→15.929825 (9–21→10–22), CLIP.474821→.476097. One C0 and two C1 different pairs are semantically near atq<=6, but no same/different/uncertain pair is jointly near in q and H. The two uncertain pairs have q9→8,H15–17 both, and are excluded from binary interpretation without relabelling. These overlapping pair counts are not independent trials.

All7 same-topic public transfers complete and meet strict recipient quality; all7 have semantic found,3 semantic content-match,0 instance content-match and0 combined both_match. Outcomes are4 content_mismatch,2 content_uncertain,1 semantic_only. Binding=none delivery and ablation controls are again absent, so seven quality-admissible transfer outputs do not establish the required five independently delivered end-to-end examples. T5 remains coverage/control-limited.

## Matched-source/seed comparison with the retained v5 image comparator

The actual v5 source is MAIN `.thesis-build/v5-study-runs/C4-v5-two-tier-development/c4-v5-two-tier-dev-001/outputs/results.json`, SHA-256 `58766c579377f344770887e6cad8bf4ed779ee207c2b6872b4a24ac4a90b9b4d`, verified against [its retained report](../experiments/c4-v5-two-tier-regeneration-v1/results-dev-001.md). Only C1 and the common10 T3 source IDs are joined by source/dose/strength/seed; the two extra A sources do not enlarge the comparator denominator.

| Matched C1 stratum | Planned shared identities | Complete A /v5 /both | Semantic successes A /v5 over planned | both_match A /v5 |
|---|---:|---:|---:|---:|
| VAE | 10 | 10 /10 /10 | 10 /10 | 4 /0 |
| .05 | 30 | 30 /30 /30 | 30 /30 | 10 /0 |
| .1 | 30 | 27 /29 /27 | 3 /27 | 0 /0 |
| .2 | 30 | 27 /28 /27 | 0 /18 | 0 /0 |
| .4 | 30 | 28 /28 /28 | 0 /2 | 0 /0 |

On mutually completed .1 identities,3 succeed in both,22 fail A while succeeding v5,2 fail both, and0 succeed A alone. At.2 the corresponding counts are0/17/10/0; at.4,0/2/26/0. Safety failures are separately retained, not removed to manufacture a common complete-cohort rate. A adds low-dose joint instance survival but loses substantially more robust semantic recovery at higher strengths in these matched records. This does not establish a causal method effect or statistical superiority/inferiority.

Both use unchanged v5 revision3 profile mathematics, but the retained v5 C0/C1 calls use owners_tested4 while A makes four independent owners_tested1 calls. For example, clean6012 decoded semantic thresholds are8.423231 for v5 versus8.259327 for A. Thresholds were inherited, not tuned in this report; the roster difference prevents an exact same-threshold detector comparison. A's lower call threshold does not explain away its worse higher-strength semantic counts. Side information, embedding routes, profile call structure and initialization also differ.

Across the same12 clean sources, v5 has12 both_match versus A10. Paired A-minus-v5 source-quality differences are mean PSNR+1.158325dB (range−1.338905 to+3.488772), SSIM+.004417 (−.007952 to+.014227), LPIPS−.010213 (−.032175 to−.004003). These are per-source differences, not a comparison of unpaired cohort means, and represent a measured clean-quality/detection tradeoff rather than support for latent superiority.

The v5 T5 component report has C0 coverage2/7 and C1 coverage1/7; A C1 has2/7. Both miss the minimum5 and use the same earlier agent labels; one extra qualifying pair is not new independent coverage. v5 also retains binding-mode delivery controls missing from this A assessor, so its T4 delivery numbers cannot be substituted for A's absent fields.

Correct-owner extraction averages.394766s across406 completed images, plus suspect CLIP extraction mean.024071s; each suspect's CLIP vector is reused across its four owner calls. These costs are separate from diffusion generation and include the implementation's CPU verifier/cache behavior. Human quality/content verdicts remain null throughout. This developmental evidence preserves the route's negative results and limitations; it advances no lifecycle gate and does not declare the family exhausted.
