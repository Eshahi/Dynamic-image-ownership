# M1 development evidence inventory

Snapshot: 2026-10-04, after completed progressive/P1 results and before A4b, B3-C and D expansion results. This is an exploratory package index, not a milestone verdict, scientific acceptance or family-exhaustion judgment. Only development-run JSON metadata and method/results documents were read; no held-out images, annotation values, model execution or mutable scientific results were inspected.

Every output directory below is relative to **`W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/`**; its `run.json` contains the full source commit, command/config/seeds/split and artifact provenance. Commits in tables are unique abbreviated receipts, not a replacement for the retained full hash. Durations are recorded run wall seconds, not per-image extractor latency. The `started` records have no final duration; their initialized zero is not elapsed runtime. Original and recovery attempts stay separate. Source clusters, conditions and repeated owner queries are different denominators.

## Reconstruction and feature diagnostics

|Output directory|Source commit|Outcome / retained count|Seconds|
|---|---|---|---:|
|20261003-1455-latent-reconstruction|3dbc6a6|Interrupted; stale `started`; four completed sources and a fifth partial attempt, of 12 planned|Not finalized|
|20261003-1507-feature-codes|8eecaaf|Completed feature-code diagnostic; three declared seeds|0.234|
|20261003-2255-latent-reconstruction-recovery|34f5ca0|Completed remaining eight sources, including fresh restart of the partial source|2244.250|
|20261003-2333-reconstruction-analysis|d619add|Completed descriptive merge: 12 unique sources at 200 steps|0.078|

The original interrupted attempt is qualified by [the pause receipt](m1-pause-artifacts-20261003.json), not silently converted to completion. Recovery selection is by the declared sequence, not best quality; the original partial attempt remains in analysis provenance. [Reconstruction results](m1-reconstruction-results.md) report mean source PSNR **28.5508 dB** (22.8365–31.2934), SSIM **.79348**, and clean quality **0/12**. This is a fixed reconstruction screen, not a global decoder floor. The longer-fit two-source diagnosis remains pending. The full-CLIP versus 32-sign ranking diagnostic reported AUC .982/.972 versus .649/.590; ranking on these pairs does not establish watermark transport, authenticity or detector FPR.

## Family A: latent optimization, pure and source-bypass routes

Pure and hybrid routes belong to **one design family**. Both optimize a latent against frozen dual-channel surrogate objectives; the hybrid amendment explicitly composes `source + D(z) - D(z_reference)`, followed by clipping. Its final verifier is image-DCT plus CLIP, without VAE or diffusion inversion, using public OwnerID, pinned CLIP weights and the versioned detector profile. Surrogate scores are not final detector decisions.

|Output directory|Source commit|Outcome / unique development sources|Seconds|
|---|---|---|---:|
|20261003-2333-A-pure-pilot|d619add|Failed pre-image launch: worktree-local CLIP asset path|6.031|
|20261003-2336-A-pure-pilot-retry|482d1dd|Failed pre-image launch: `a6_clip_visual` import/provenance KeyError|7.109|
|20261003-2337-A-pure-pilot-retry2|92705c2|Completed pure pilot: 1675, 4795|467.485|
|20261003-2347-A-hybrid-pilot|421787d|Completed hybrid: 1675, 4795|466.016|
|20261003-2355-A-pilot-analysis|c4f722e|Completed descriptive analysis of the two successful pilots and failure inventory|0.110|
|20261004-0012-A-hybrid-old2|dc012fb|Completed hybrid: 6012, 25394|466.250|
|20261004-0025-A-hybrid-recovery4a|dc012fb|Completed hybrid: 80932, 109798, 134882, 147498|924.141|
|20261004-0040-A-hybrid-recovery4b|ba94b54|Pending `started`; four planned sources: 177015, 190676, 468505, 499768|Not finalized|

|Completed shard / route|Clean source-quality pass|Clean `both_match`|VAE `both_match`|VAE `semantic_only`|
|---|---:|---:|---:|---:|
|Pure pilot|0/2|0/2|0/2|2/2|
|Hybrid pilot|2/2|2/2|1/2|1/2|
|Hybrid old2|2/2|1/2|1/2|1/2|
|Hybrid recovery4a|4/4|3/4|2/4|2/4|
|Eight completed hybrid sources, disjoint shards|8/8|6/8|4/8|4/8|

The recovery4a table is a direct count of its finalized `run.json` fields; source109798 has clean `content_uncertain`, while the other three clean cases have `both_match`. No moving A4b result is included. [Pilot results](m1-A-pilot-results.md) and [four-source content-consistency diagnosis](m1-A-content-consistency-diagnosis.md) preserve failed launches, source/counterfactual quality, controls and exact detector fields. Source6012 finds both clean carriers but its corrected instance distance **6.098384 > radius6** leads to content uncertainty; this differs from its VAE instance-carrier loss. Eight completed sources do not constitute 12-source success. Full T3 diffusion, T4 transfer and T5 semantic pairing assessment is pending: the prepared hybrid assessor plans 489 conditions and 1692 owner queries after all 12 enrollments finish. VAE cycle alone is not full T3.

## Family B: GS initial-noise carrier and forthcoming B3-C amendment

|Output directory|Source commit|Outcome / count|Seconds|
|---|---|---|---:|
|20261004-0000-gs-native|6a46faa|Completed: four generated prompt/seed clusters, 112 conditions, 14 channels|339.484|
|20261004-0010-gs-lightweight|8809c8d|Completed: the same 112 conditions, terminal-sign reader|18.844|
|20261004-0012-gs-paired-analysis|dc012fb|Completed paired descriptive analysis|0.125|
|20261004-0037-gs-probe|ba94b54|Completed sealed P1 implementation probe: 24 images, 72 foreign-nonce and 24 shift queries|13.812|

[GS paired results](m1-gs-paired-results.md) retain every channel and all four clusters. Native 50-step DDIM inversion and lightweight one-VAE sign/64-repeat-majority readers each have C1 presence **4/4 in every channel**, including strengths .05/.1/.2/.4 × three seeds. C0 and wrong-key positives are **0/4 per channel**. Native clean/VAE exact recovery is **4/4**; lightweight exact recovery is **2/4 clean, 1/4 VAE, 0/4 at strong regeneration**. Presence requires >=180/256 agreements and is not exact message recovery. Mean readout times are native **2.185464 s** versus lightweight **.053589 s**, a descriptive ~40.8 ratio; whole-run durations include other work and cannot substitute for readout latency.

GS marks newly generated images; paired clean C1/C0 quality passes **0/4**, with PSNR 8.402–11.023 dB. This counterfactual is not existing-photo preservation. Both readers use the enrolled key/nonce and reference message agreement; public development key fixtures are not secret-key security or public-OwnerID content binding. The [P1 results](m1-gs-lightweight-probe-results.md) independently reproduce **384/384 vote arrays**, 24/24 correct/wrong replication, and all predeclared implementation gates; foreign/shift controls share four clusters. This validates the implementation boundary, not a new threat result or independent population FPR.

**Pending B3-C:** [continuous blind-template design](m1-blind-noise-template-design.md), `scripts/m1_blind_noise.py`, and `research/m1-blind-noise-dev.json`, frozen at `fe02a46`, plan two existing-photo sources, three amplitudes (.025/.05/.1), pure/hybrid routes, **48 conditions / 192 owner queries**, and a 900-s run cap. No retained B3-C science run was available at this snapshot. It replaces exact derived bit keys with public continuous full-CLIP and CLIP×pHash templates, and uses one-VAE plus CLIP/hash readout with no enrollment record or inverse detector. Embedding inversion, source bypass, public forgery and content-binding limitations remain explicit prospective amendments. P1 is complete; B3-C is untried. NoisePrints/OSI inspected primary precedents preclude a novelty claim for direct VAE initial-noise readout.

## Family C: progressive denoising guidance

|Output directory|Source commit|Outcome / count|Seconds|
|---|---|---|---:|
|20261004-0031-progressive|eca1a53|Completed: four generated clusters, six variants, 28 generations, 112 conditions / 224 extractor observations|172.031|
|20261004-0036-progressive-analysis|eca1a53|Completed descriptive analysis|0.094|

[Progressive results](m1-progressive-results.md) report **0/96 C1 presence and 0/96 exact recovery** for both native one-VAE+DCT and image-DCT diagnostic readers; the cutoff is 14/16 bits. C0 true-payload presence is 0/16 for each. Alpha .1/eta25 passes generated-pair quality **4/4** but has native clean mean accuracy **.390625**; alpha .5/eta100 reaches **.671875** but quality only **1/4**. Six-variant quality counts are 4/1/3/1/3/1 out of four, respectively. The screen includes clean, VAE and T3 strengths .1/.4. It is an adapted GROW-inspired generated-image experiment, not existing-photo preservation, a faithful paper reproduction or family exhaustion. Complement/64-word controls retain false findings and correlated denominators. No dual content binding or T4/T5 evidence exists. Schedule diagnosis/amendment is prospective until its exact spec and new run are frozen.

## Family D: terminal phase, pure and residual routes

|Output directory|Source commit|Outcome / count|Seconds|
|---|---|---|---:|
|20261003-2355-phasemark-pilot|c4f722e|Completed pure terminal-phase pilot: two photo clusters, 16 conditions / 64 owner queries|24.453|
|20261003-2357-phasemark-analysis|c4f722e|Completed descriptive analysis|0.078|
|20261004-0030-phase-residual|eca1a53|Completed residual pilot: two clusters, 32 conditions / 128 queries|35.657|
|20261004-0031-phase-residual-analysis|eca1a53|Completed descriptive analysis|0.109|

[Pure PhaseMark results](m1-phasemark-results.md): APM and IPS each have clean/VAE presence **2/2** but clean source quality **0/2**. Mean source PSNR/SSIM/LPIPS is APM **23.584/.6372/.1532**, IPS **24.488/.6614/.1214**. Paired decoder-counterfactual quality also fails and remains a separate reference. [Residual results](m1-phase-residual-results.md): full-dose APM/IPS retain clean/VAE carriers **2/2** but quality **0/2**; capped APM has quality2/2, clean presence1/2 and VAE2/2. Frozen IPS quality-cap has source quality **2/2**, clean correct matches **89/99**, VAE **90/90**, and all unmarked/wrong-owner controls below82/128. Both capped source PSNRs are **35.2000 dB**. This is a two-source carrier/quality screen, not T3 diffusion evidence.

**Pending D expansion:** [implementation/spec](m1-phase-residual-expansion.md), `scripts/m1_phase_residual_expansion.py`, and `research/m1-phase-residual-expansion-dev.json`, frozen at `fe02a46`, plan the remaining ten development sources, **40 conditions / 160 queries**, unchanged IPS mask/128-bit public owner word/35.2-dB cap with 36 bisection steps, fresh per-source encoding, clean/VAE and four owners. No scientific expansion results are available here. The analyzer supports a provenance-compatible disjoint pilot+expansion merge of 12 sources, 48 IPS-cap conditions and 192 queries, with null gates for missing work; readiness does not establish those results. Pure and residual variants remain one phase family. Extraction is one FP32 VAE encode with zero U-Net calls; no CLIP+pHash binding, authenticated ownership or three decision-state result is established.

## Comparator and package limits

The v5 image-domain method remains a labelled comparator; see [retained mechanism diagnostic](v5-dev001-mechanism-diagnostic-20261003.md). Its safety failures/missing rows and distinct semantic-carrier versus joint carrier+CLIP denominators must remain visible; do not pool it with generated GS/C evidence or silently equate those metrics.

This index preserves different failure modes: pre-image launch failures; interrupted reconstruction; existing-photo reconstruction quality loss; content-radius abstention despite carrier detection; terminal-readout/generated-pair success with no photo guarantee; and progressive carrier failure. Conditions, attack seeds, owner hypotheses and source clusters cannot be counted as independent trials. Human visual assessments remain missing. Completed carrier screens do not establish public-key forgery resistance, causal history, legal ownership, full T4/T5 evidence or a measured universal ceiling. Method amendment/freezing, full development threats, confirmatory candidate/manifest/rehearsals and independent milestone review remain separate unfinished package work. Protected acceptance/source plans and official lifecycle gates are unchanged.

Refresh this index only from finalized run receipts and reproducible reports when A4b, B3-C, D expansion or subsequent diagnoses complete; retain failed/partial attempts and the present snapshot's limits.
