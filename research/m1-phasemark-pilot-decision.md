# D next diagnostic: transport the phase residual at fixed source quality

Version **`m1-phasemark-residual-v1`**, 2026-10-04; design escalation **xhigh**. This is an exploratory amendment made after the two-image pure-decoder PhaseMark pilot. It freezes the next diagnostic before its outputs. It does not replace that negative quality result or claim this family is exhausted. Parent implements and executes; this document performs no GPU work.

**Run a source-bypass residual diagnostic on the same preselected sources 1675/4795, both unchanged APM/IPS carriers, at lambda=1 and a deterministic RGB8 PSNR35.2 cap.** This is inexpensive and separates baseline VAE reconstruction loss from phase-carrier distortion. Call the amended output `phase-latent-residual-source-bypass`; it is not pure VAE decoding or an initial-noise method.

## Evidence and choice

The inspected source run is MAIN `.thesis-build/dev-runs/20261003-2355-phasemark-pilot`, commit `c4f722e5ae0512e872ebaef0bd4b71228ea95f29`, completed in 24.453 s. Its `run.json` SHA-256 is `0fd2f7f8a1cdb34e6a129f753eb1f090e279cd8c1018a774a262a84bb7a123c8`. The [results report](m1-phasemark-results.md) and all 16 condition records were inspected; the terminal JSON hash was independently checked.

| Source | Unmarked pure C0/source PSNR | APM C1/source PSNR | APM C1/C0 PSNR | IPS C1/source PSNR | IPS C1/C0 PSNR |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1675 | 26.692 | 23.687 | 25.517 | 24.794 | 27.790 |
| 4795 | 25.204 | 23.480 | 26.594 | 24.182 | 28.677 |

Both arms recover the correct public payload above the frozen >=82/128 cutoff on 2/2 clean and 2/2 VAE-cycle images; all sampled unmarked/wrong-owner queries stay below it. Both arms have clean source-quality conjunction 0/2. The original VAE alone already misses source fidelity, and phase insertion adds substantial distortion even relative to its matched decoder output. Refining the baseline alone therefore does not remove the measured phase perturbation. Source-bypass A also provided practical evidence that separating reconstruction error from a decoder-generated perturbation can preserve source details. These facts justify this diagnostic, not a guarantee of D's channel survival.

The step-200 refined pure reconstructions on these photos still miss the strict 35 dB/.9/.1 requirements. Applying phase to them is an untested alternative; it is not ruled out, and longer reconstruction fitting remains separately planned. Defer that less diagnostic branch until this cheap residual/attenuation test is measured. Do not count APM versus IPS or lambda settings as distinct design families.

## Frozen construction and exact cap

Use the original pilot's saved scaled fp32 posterior-mean `z0` and phase-marked `zm`, including their pinned scale .18215. Verify all source/latent/manifest/model hashes before loading. Define

`D01(z) = clip((VAE.decode(z/.18215) + 1)/2, 0, 1)`

`delta = D01(zm) - D01(z0)`

`Y8(lambda) = uint8(rint(255 * clip(I8/255 + lambda*delta, 0, 1)))`.

Decode in the pilot's fp32 settings, then convert decoder outputs to float64 CPU arrays for composition and budget computation. Keep delta's signed values; do not subtract saved RGB8 PNGs or use an alternative baseline reconstruction. Before composing, rounded decoded `z0/zm` outputs must exactly reproduce the corresponding pilot RGB8 pixels; PNG container bytes may differ, pixel hashes must not. A mismatch is a preflight failure requiring a documented diagnosis.

The **full** profile is exactly `lambda=1`, even when its quality fails. The **quality-cap** profile uses only original RGB8 pixels and delta, never any extracted bits, CLIP, LPIPS, SSIM or owner score. Let `B=255^2 * 10^(-35.2/10)`. If `MSE(I8,Y8(1)) <= B`, use lambda=1. Otherwise initialize `lo=0, hi=1`, perform exactly **36 binary-search iterations**, evaluating integer-pixel differences after casting to float64, and retain the feasible `lo`: at each midpoint, replace lo if MSE<=B and hi otherwise. Serialize `Y8(lo)` with the same `rint` convention; save lambda, lo/hi, B and actual integer SSE/MSE.

This search is a deterministic distortion limiter, not detector tuning. Each pixel moves monotonically away from its original integer value along a fixed signed residual as lambda increases, including clipping/rounding; total RGB8 MSE is therefore nondecreasing. The feasible lower endpoint gives a saved-image PSNR of at least35.2, subject to checked finite arithmetic. This avoids claiming that a 35.2 dB floating-image norm cap alone guarantees the RGB8 boundary after rounding. A zero residual uses lambda=1 and remains a valid negative carrier outcome. If both profiles give identical PNGs, retain both planned rows and flag the duplicate; it is not extra independent evidence.

Keep the original 128-bit owner-alpha payload, APM/IPS phase rules, spatial crop [10:54,10:54], exact block list, Hermitian repair, extractor and four-owner roster. No new phase target, masks, optimized frequency weights, payload shortening, seed, threshold or extractor adaptation. C0 for either profile is the source I8 itself. Its VAE cycle is D(E(I8)); the old pure C0 remains a separate historical comparator.

## Inventory, decisions and provenance

Plan **32 logical conditions**: two sources × two arms × two profiles × C0/C1 × clean/one-VAE-cycle. This corresponds to at most20 distinct PNGs: four marked outputs plus one shared C0 per source, each clean/cycled. C0 duplicates across profiles/arms share file receipts; APM/IPS queries still use their own extractor. Every condition has four owner queries, giving128 logical queries with only two independent source clusters. Preserve missing/failed rows in the full32 denominator and identify shared hashes explicitly.

The attack is exactly the pilot's deterministic posterior-mean VAE cycle of each saved/reopened RGB8 image. Extraction stays one VAE encode plus the original phase rule; it receives suspect image, public owner payload and pinned model/profile, without source image or original latent. Score all planned outputs, including low-quality lambda1 outputs. Record saved-source quality, same-arm clean-reference attack quality, every match count/decision, bit vectors, zero magnitudes, extraction timing and missing human judgments. Use float-correct PSNR and unchanged SSIM/LPIPS implementations.

For each arm/profile, carrier gate requires correct-owner presence on both clean and both cycle C1s, no marked wrong-owner positives, and no C0 roster positives. Clean quality gate separately requires both source images satisfy PSNR>35, SSIM>.9, LPIPS<.1. The quality-cap profile is the primary operating candidate; lambda1 is a mechanism control and cannot be promoted merely because its presence is better. Keep >=82 matches: testing more profiles expands the query family, so neither the old binomial heuristic nor these few controls implies a global1% FPR. No threshold search is introduced.

Fresh output only, source runs read-only. Retain the original run and input receipt hashes, all six input latent receipts, raw/source PNG hashes, model and upstream source/license receipts, code commit, exact composition arithmetic, delta norm/hash, both lambdas, serialized outputs and append-only failure journal. Cap at600 seconds,10 GiB allocated GPU,16 GiB process RAM and250 MiB new artifacts. Only VAE forwards and CPU metrics are needed; there are no optimization updates or new diffusion generations.

If a quality-cap arm passes both gates, expand that unchanged profile to the remaining ten reserved sources before frozen T3 assessment. If both do, retain both with multiplicity/compute declared; do not choose the better two-image score. If lambda1 retains presence but the cap loses it, report an observed power-versus-readout tradeoff on these sources. If even lambda1 fails, source-bypass transport disrupted this carrier; that is not proof that terminal phase embedding is generally impossible. A refined baseline, joint phase/quality optimization, magnitude-aware block choice or another phase code remain untested alternatives requiring an explicit later decision.

This is still a public128-bit presence carrier with no CLIP/pHash binding. Successful quality and VAE gates alone do not establish T3 diffusion survival, T4 transfer rejection, T5 discrimination or a three-state ownership method. Those requirements must remain visible before any M1 exit claim.
