# M1 development evidence inventory

Snapshot: 2026-10-04, updated after finalized A4b/A12 analysis, B3-C and D expansion/combined analysis; A full-threat0900/0920 and C-L1000911/0921 are finalized. This is an exploratory package index, not a milestone verdict, scientific acceptance or family-exhaustion judgment. Only finalized development-run JSON/CSV analysis, run metadata and method/results documents were read; no held-out images, annotation values, model execution or mutable scientific results were inspected.

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
|20261004-0040-A-hybrid-recovery4b|ba94b54|Completed hybrid: 177015, 190676, 468505, 499768|925.422|
|20261004-0057-A-hybrid-twelve-analysis|e56ef8c|Completed descriptive merge: 12 unique hybrid sources, five declared channels|0.156|
|20261004-0900-A-hybrid-threats|9267e6e|Incomplete final receipt: 472/489 conditions, 17 retained safety failures / 1624 of 1692 owner queries|1093.156|
|20261004-0920-A-hybrid-threat-analysis|af32f3d|Incomplete descriptive analysis preserving all489 planned conditions|0.110|

|Completed shard / route|Clean source-quality pass|Clean `both_match`|VAE `both_match`|VAE `semantic_only`|
|---|---:|---:|---:|---:|
|Pure pilot|0/2|0/2|0/2|2/2|
|Hybrid pilot|2/2|2/2|1/2|1/2|
|Hybrid old2|2/2|1/2|1/2|1/2|
|Hybrid recovery4a|4/4|3/4|2/4|2/4|
|Hybrid recovery4b|4/4|4/4|1/4|3/4|
|All twelve hybrid sources, disjoint shards|12/12|10/12|5/12|7/12|

The recovery4a/4b rows are direct counts of finalized `run.json` fields. Source109798 and6012 have clean `content_uncertain`; all other clean cases have `both_match`. All12 clean semantic/instance carriers are found, but only10 satisfy dual content consistency. Finalized A12 `dual-summary.csv` gives clean mean PSNR **38.275291**, SSIM **.983438**, LPIPS **.007408** and quality12/12. VAE semantic carriers remain12/12 while instance carriers/content match are5/12; VAE source-quality conjunction is0/12, a separate reference. All C0 and wrong-owner watermark-found counts are zero in these five enrollment channels. [Pilot results](m1-A-pilot-results.md) and [four-source diagnosis](m1-A-content-consistency-diagnosis.md) retain earlier receipts; A12 analysis is the complete-cohort descriptive source. Source6012's corrected distance **6.098384 > radius6** distinguishes content uncertainty from its VAE instance-carrier loss. The finalized [A full-threat report](m1-A-hybrid-threat-results.md) retains17 safety failures, all at source6012. C1 diffusion .05 has semantic36/36 and both11/36; .1 has semantic3/36 and both0/36 with3 missing; .2/.4 have semantic0/36 with3/2 missing. T4 has80/80 completed and0 dual false matches, but missing delivery/ablation controls prevent a forgery-resistance claim. T5 retains7 same/57 different/2 uncertain labels and7 same-pair transfers, all quality-admissible with0 dual false matches; exact separation and limits remain in the report. VAE alone is not full T3.

The prospective [terminal continuous-reader A-C amendment](m1-terminal-continuous-design.md) remains within family A. It reuses B3's blind continuous geometry/readout with terminal-latent optimization. No A-C science result exists in this snapshot; it is not an additional independently tried family.

## Family B: GS initial-noise carrier and B3-C amendment

|Output directory|Source commit|Outcome / count|Seconds|
|---|---|---|---:|
|20261004-0000-gs-native|6a46faa|Completed: four generated prompt/seed clusters, 112 conditions, 14 channels|339.484|
|20261004-0010-gs-lightweight|8809c8d|Completed: the same 112 conditions, terminal-sign reader|18.844|
|20261004-0012-gs-paired-analysis|dc012fb|Completed paired descriptive analysis|0.125|
|20261004-0037-gs-probe|ba94b54|Completed sealed P1 implementation probe: 24 images, 72 foreign-nonce and 24 shift queries|13.812|
|20261004-0059-blind-noise|9267e6e|Completed B3-C: two existing-photo sources, 48 logical conditions / 192 queries / 500 U-Net calls|64.000|
|20261004-0900-blind-noise-analysis|9267e6e|Completed descriptive analysis: all six route/amplitude gates fail|0.875|

[GS paired results](m1-gs-paired-results.md) retain every channel and all four clusters. Native 50-step DDIM inversion and lightweight one-VAE sign/64-repeat-majority readers each have C1 presence **4/4 in every channel**, including strengths .05/.1/.2/.4 × three seeds. C0 and wrong-key positives are **0/4 per channel**. Native clean/VAE exact recovery is **4/4**; lightweight exact recovery is **2/4 clean, 1/4 VAE, 0/4 at strong regeneration**. Presence requires >=180/256 agreements and is not exact message recovery. Mean readout times are native **2.185464 s** versus lightweight **.053589 s**, a descriptive ~40.8 ratio; whole-run durations include other work and cannot substitute for readout latency.

GS marks newly generated images; paired clean C1/C0 quality passes **0/4**, with PSNR 8.402–11.023 dB. This counterfactual is not existing-photo preservation. Both readers use the enrolled key/nonce and reference message agreement; public development key fixtures are not secret-key security or public-OwnerID content binding. The [P1 results](m1-gs-lightweight-probe-results.md) independently reproduce **384/384 vote arrays**, 24/24 correct/wrong replication, and all predeclared implementation gates; foreign/shift controls share four clusters. This validates the implementation boundary, not a new threat result or independent population FPR.

**Completed B3-C:** [design](m1-blind-noise-template-design.md) and [results/branch decision](m1-blind-noise-results-decision.md) retain three amplitudes (.025/.05/.1), two sources and pure/hybrid routes. All24 true-owner C1 logical rows are below both score thresholds4. Hybrid clean quality passes **1/6** source-dose cells; pure **0/6**; all six two-source route/dose joint gates fail. All168 logical C0/wrong-owner queries are negative, with reused C0 artifacts. The sole quality-admissible hybrid cell (1675/.025) has semantic/instance scores **1.618/.371**. Largest hybrid clean scores **3.704/2.390** occur at1675/.1 with PSNR27.609, not admissible quality. Retained arithmetic verifies55 artifact hashes and correct template/noise placement, without a universal initial-noise ceiling. This failed existing-photo experiment differs from generated GS transport. It uses public continuous full-CLIP and CLIP×pHash templates, one-VAE+CLIP/hash blind readout, no enrollment or detector inversion, but embedding inversion/source bypass. NoisePrints/OSI preclude novelty for direct VAE readout; public forgery/content-authentication limits remain.

## Family C: progressive denoising guidance

|Output directory|Source commit|Outcome / count|Seconds|
|---|---|---|---:|
|20261004-0031-progressive|eca1a53|Completed: four generated clusters, six variants, 28 generations, 112 conditions / 224 extractor observations|172.031|
|20261004-0036-progressive-analysis|eca1a53|Completed descriptive analysis|0.094|
|20261004-0911-progressive-phase|cf373b2|Completed C-L100: 16 generations / 32 conditions, replay verified|98.875|
|20261004-0921-progressive-phase-analysis|66c7d97|Completed CPU stage/endpoint/receipt analysis|1.734|

[Progressive results](m1-progressive-results.md) report **0/96 C1 presence and 0/96 exact recovery** for both native one-VAE+DCT and image-DCT diagnostic readers; the cutoff is 14/16 bits. C0 true-payload presence is 0/16 for each. Alpha .1/eta25 passes generated-pair quality **4/4** but has native clean mean accuracy **.390625**; alpha .5/eta100 reaches **.671875** but quality only **1/4**. Six-variant quality counts are 4/1/3/1/3/1 out of four, respectively. The screen includes clean, VAE and T3 strengths .1/.4. It is an adapted GROW-inspired generated-image experiment, not existing-photo preservation, a faithful paper reproduction or family exhaustion. Complement/64-word controls retain false findings and correlated denominators. No dual content binding or T4/T5 evidence exists. The completed C-L100 schedule diagnosis at0911 and [independent stage/endpoint analysis](m1-progressive-phase-analysis.md) at0921 retain16 generations and32 conditions. All8 late-guided carriers recover16/16 bits at terminal/float-cycle/RGB8/extra-VAE endpoints and C0 intended presence is absent, but matched-counterfactual clean quality passes0/8 (PSNR24.9359�33.0205 dB). This demonstrates schedule-dependent carrier transport in this bounded generated-image intervention, with no existing-photo quality guarantee or family-exhaustion claim.

## Family D: terminal phase, pure and residual routes

|Output directory|Source commit|Outcome / count|Seconds|
|---|---|---|---:|
|20261003-2355-phasemark-pilot|c4f722e|Completed pure terminal-phase pilot: two photo clusters, 16 conditions / 64 owner queries|24.453|
|20261003-2357-phasemark-analysis|c4f722e|Completed descriptive analysis|0.078|
|20261004-0030-phase-residual|eca1a53|Completed residual pilot: two clusters, 32 conditions / 128 queries|35.657|
|20261004-0031-phase-residual-analysis|eca1a53|Completed descriptive analysis|0.109|
|20261004-0057-phase-residual-expansion|e56ef8c|Completed remaining-ten IPS-cap sources: 40 conditions / 160 owner queries|57.406|
|20261004-0059-phase-residual-combined-analysis|9267e6e|Completed disjoint merge: 12 sources / 48 IPS-cap conditions / 192 queries|0.281|

[Pure PhaseMark results](m1-phasemark-results.md): APM and IPS each have clean/VAE presence **2/2** but clean source quality **0/2**. Mean source PSNR/SSIM/LPIPS is APM **23.584/.6372/.1532**, IPS **24.488/.6614/.1214**. Paired decoder-counterfactual quality also fails and remains a separate reference. [Residual results](m1-phase-residual-results.md): full-dose APM/IPS retain clean/VAE carriers **2/2** but quality **0/2**; capped APM has quality2/2, clean presence1/2 and VAE2/2. Frozen IPS quality-cap has source quality **2/2**, clean correct matches **89/99**, VAE **90/90**, and all unmarked/wrong-owner controls below82/128. Both capped source PSNRs are **35.2000 dB**. This is a two-source carrier/quality screen, not T3 diffusion evidence.

**Completed D expansion:** [results](m1-phase-residual-expansion-results.md) verify the frozen remaining-ten run and complete disjoint12-source IPS-cap analysis. Clean quality passes **12/12**; correct-owner presence is **9/12 clean**, **9/12 VAE**, and **8/12 both**. All C0/wrong-owner queries are negative; the expanded carrier gate fails. All ten newly saved marked latents carry128/128 bits in direct insertion diagnostics, so those failures occur later in decode/composition/re-encode, without a causal decomposition. VAE source-quality conjunction is **0/12**, separately from clean quality. Unchanged public128-bit word,35.2-dB cap/36-step bisection and fresh encoding remain in [spec](m1-phase-residual-expansion.md). Pure/residual variants remain one family. Extraction is one FP32 VAE encode, zero U-Net calls; no CLIP+pHash binding, authenticated ownership, diffusion T3, T4/T5 or three-state result follows.

## Comparator and package limits

The v5 image-domain method remains a labelled comparator; see [retained mechanism diagnostic](v5-dev001-mechanism-diagnostic-20261003.md). Its safety failures/missing rows and distinct semantic-carrier versus joint carrier+CLIP denominators must remain visible; do not pool it with generated GS/C evidence or silently equate those metrics.

This index preserves different failure modes: pre-image launch failures; interrupted reconstruction; existing-photo reconstruction quality loss; content-radius abstention despite carrier detection; terminal-readout/generated-pair success with no photo guarantee; and progressive carrier failure. Conditions, attack seeds, owner hypotheses and source clusters cannot be counted as independent trials. Human visual assessments remain missing. Completed carrier screens do not establish public-key forgery resistance, causal history, legal ownership, full T4/T5 evidence or a measured universal ceiling. Method amendment/freezing, full development threats, confirmatory candidate/manifest/rehearsals and independent milestone review remain separate unfinished package work. Protected acceptance/source plans and official lifecycle gates are unchanged.

Refresh this index only from finalized run receipts/reports when A-C or subsequent prospective diagnoses finish; retain failed/partial attempts and the present snapshot's limits.
