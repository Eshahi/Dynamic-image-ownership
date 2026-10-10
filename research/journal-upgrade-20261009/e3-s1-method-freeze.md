# E3-S1 method freeze for M1b

2026-10-10, Codex agent. The scientific callable is frozen at `27e2c84`; M1b integration must call it without altering its numerical recipe. Full source-to-mark development qualification is recorded in [the M1a assessment](e3-s1-m1a-assessment.md). The separate [confirmation design](e3-s1-confirmatory-design.md) defines new sources, evaluation seeds, endpoints and missingness. Packaging is not confirmatory execution or a human gate decision.

## Interface and signal location

`scripts/journal_e3_writer.py` exposes `supply_f5(source, evaluator, output_dir, budget)` and `embed(source, owner, q, h, evaluator, sdxl_vae, ddim_channel, output_dir, budget)`. Source is canonical 512 x 512 x 3 RGB8. The only supported legitimate owner is `qim-pilot-owner-alpha`; q and h are unsigned 32-bit integers. Rejected types/ranges fail before output construction. Output directories are new, never silently reused.

E3 modifies image pixels through gradients of model-based objectives. The semantic signal is optimized in the SD1.5 VAE representation, but this remains an image-domain writer, not latent insertion in a generating diffusion process. Extraction requires the pinned SD1.5 VAE encoder and seven CLIP views. The original lightweight-extractor hypothesis remains untested. The fragile instance component is image-domain and does not survive the measured T3 channels.

## Fresh target supply

Run one F5 r2 bootstrap on the original canonical source: 52 dB, 150 normalized-gradient PGD steps, margin 4, mask power 0, band 4..32, whitening 1, one refinement round, soft binding and seven-view CLIP. The existing refinement adds 50 steps at 58 dB. Save and reload the bootstrap. Decode it once with its native combined F5 reader at roster size one. Both channels must be readable.

q is the bootstrap report's intended semantic word; h is its saved-image native decoded operational instance word. h is not relabelled an original intended hash. No bootstrap strict-quality, full-match or exact-q inclusion filter is added. There is no alternative pair search, retry or historical-target fallback. Bootstrap pixels are retained as provenance and never become E3's initializer.

## Writer

Start again from canonical C0. Run fixed-q F5 optimization at 46 dB for 150 steps, RGB8 rounding and fixed-q/h fragile restoration; then 52 dB for 50 steps and the second fixed-q/h restoration. Save and reload. Qualify this initializer by exact native q/h reads, full acceptance, strict PSNR >35 dB, SSIM >.9, LPIPS <.1 and the declared norm balls. Invalid initialization skips refinement but still reaches the fixed quality branch.

A valid initializer has 20 logical minimax iterations over nine branches: clean, SD1.5 VAE, SDXL VAE, and SD1.5 DDIM img2img strengths .1/.2 with seeds 0/1/2. Branch losses use the existing score and 59 coded-symbol hinges. Differentiate the first worst branch. The added L2 budget corresponds to 52 dB and the total budget to 35.1 dB, with the [0,1] box. Proposal fractions are [.1,.5,1] for iterations 0–9 and [.025,.125,.25] for 10–19.

Each proposal is rounded, saved and reloaded. Evaluate all nine losses even if it fails another eligibility condition. Eligibility requires continuous and rounded norm feasibility, strict clean quality, exact q/h and full acceptance, and decrease at least `max(1e-6, 1e-4 * current_max_loss)`. Select the lowest eligible maximum, ties by proposal order. Otherwise retain the current RGB8. There is no continuous-state accumulation or fragile restoration after initialization. Only exact inactive-hinge or identical same-phase no-op shortcuts skip work; changed second-phase lengths are still tested. Invalid gradients stall and remain reported.

After refinement, retain the image if it satisfies strict quality. Otherwise contract its integer difference from C0 once by .8, using `sign(d) * ((4 * abs(d) + 2) // 5)`. This choice uses quality only, not detection. There is no post-contraction repair or alternative contraction search. Final admission again requires strict quality, exact q/h and full acceptance. Failed admission remains a measured result with returned pixels preserved; construction exceptions remain execution failures with the recorded traceback.

## Detector and evaluator separation

`scripts/journal_bch_readout.py` receives suspect pixels/latent, claimed public owner, profile and suspect semantic features. It receives no enrollment reference, original source or intended q/h. The semantic carrier is a shortened BCH(59,32) code with correction radius five and 320 chips, not 64 freely selectable message bits. The instance route is RC1: use the decoded semantic word when readable, otherwise the suspect-recomputed word. Binding is soft and the S1 roster size is one.

The frozen profile's nominal false-positive parameter is 1e-6. It produces semantic decoded/recomputed score thresholds about 8.5661388637 / 5.3867722689 and the legacy instance decoded threshold about 8.2593268261. These are operating thresholds, not an empirically calibrated population FPR guarantee. The sign bound is explicitly hypothetical for this public, adaptive construction. No threshold is tuned in M1b or on held-out data.

Exact recovery Q/H and donor-delivery D are computed outside detection using the frozen supplier or native comparator targets. Full acceptance F and semantic content acceptance S are native detector outputs. Recomputed-only semantic acceptance is never called an exact decoded recovery. Each reported negative unit preserves owner, arm, method, roster size and availability.

## Scientific environment and artifacts

The existing profile is `experiments/c4-v5-two-tier-regeneration-v1/profile.json`; F5 supplier settings remain `configs/f5-r2.json`. `configs/e3-s1.json`, the SDXL asset lock and environment lock bind this prose to the package. Model hashes and installed package versions are part of the scientific core. The SDXL VAE revision is `6f5909a7e596173e25d4e97b07fd19cdf9611c76`; the differentiable DDIM channel uses fp16, the reader and SDXL VAE fp32. Evaluation retains the actual pinned pipeline safety checker.

Construction records include source, bootstrap, both initialization states, final state, selected output, proposal images, iteration log, native calls, metrics, target basis, branch, admission and duration. Completed units and scientific failures are immutable. An interrupted unfinished unit can be retried only through a recorded infrastructure continuation; existing artifacts are preserved. This is one realized GPU experiment, not a bit-exact replay promise.

## Scope and verification

The eleven CPU control-flow tests in `scripts/test_journal_e3_writer.py` passed on 2026-10-10. They exercise target/owner rejection, supplier failure and target basis, invalid initialization, exact logical shortcuts, both proposal phases, all-nine-loss evaluation, strict boundaries, quality-only contraction and no payload-guided retry. These tests use controlled objectives and readers; they do not substitute for the real-model development evidence or synthetic official-runner rehearsals.

The 12-source M1a result establishes finite development feasibility only. All optimization sources and six writer DDIM identities were seen; SDXL VAE was also in the objective. Owner-generic construction, matched-FPR superiority, independent-model robustness, cryptographic authorization, reference-specific same-owner attribution, population error <=.001 and incremental combined-binding benefit remain unsupported. Human visual/semantic verdicts remain missing. No file under the protected proposal, source plan, claim ledger or retained run directories is changed by this freeze.
`nOperational refinement (2026-10-10): enforce a 9 GiB CUDA allocation cap and declare 9216 MiB to the existing runner. Development peak was 7,068,902,400 bytes (6.58 GiB). The original 10 GiB reservation failed the official 1 GiB availability headroom on the occupied desktop; the smaller enforced cap preserves that headroom and all science settings. RAM remains 16 GiB, retained outputs across attempts 12 GiB, free storage 20 GiB, aggregate time 24 hours.
