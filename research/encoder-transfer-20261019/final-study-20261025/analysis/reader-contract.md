# Frozen reader contract and proposed descriptive extraction

Prepared 2026-10-25 from source/configuration text only. No raw result journal was inspected, no project module was imported, and no experiment was executed. This document recommends a later stdlib-only extraction; it does not change endpoints, thresholds, missingness rules, or routing.

## Persisted fields and exact predicates

The journal call location is `row.detections[method][owner]`. Successful calls contain `status="ok"`, `raw`, and `endpoints` (`scripts/encoder_transfer_runtime.py:174-183`, `:693-719`). Clean embedding reports are separately at `row.embedding_report` (`:620`). Both F5 and v5 expose two channel dictionaries, `raw.semantic` and `raw.instance`, with the same score contract because F5 calls v5's `_key_test` and `_channel_result` (`scripts/f5_latent_codec.py:294-305`).

Each channel persists these exact fields (`scripts/revised_watermark_v5.py:1263-1278`):

| Field | Meaning |
|---|---|
| `recomputed_score`, `recomputed_threshold` | Current-image code's one-pattern score and roster-adjusted threshold |
| `decoded_score`, `decoded_threshold` | Best code over all 2^32 patterns and corresponding search-adjusted threshold |
| `score`, `threshold` | Selected branch: decoded if its threshold passes, otherwise recomputed, including when neither passes |
| `found`, `read` | OR of the two passing tests; decoded-test pass alone, respectively |
| `candidate` | `decoded` if readable and code distance is nonzero; `recomputed` if readable with distance zero or recomputed-only pass; null if neither passes |
| `decoded_code` | Hexadecimal best code, even if unreadable; never treat its mere presence as recovered payload |
| `code_distance`, `corrected_distance`, `decoding_error_rate` | Raw Hamming distance to current-image code; model-corrected distance; model-estimated error rate. All null when neither test passes. Recomputed-only pass sets distances to zero and leaves error rate null. |
| `log10_false_positive_bound` | Bound for the selected branch's number of patterns, not an empirical FPR |
| `content_status`, `content_match` | Added by detector public wrappers; match is `found` AND status rank zero |

F5 semantic additionally persists `soft_distance` (`f5_latent_codec.py:314`); v5 does not. `raw.semantic_code` is the current-image semantic code, not necessarily the original intended payload. `raw.perceptual_hash` is likewise current-image H. v5 exports `instance_tested_with_semantic_code`; F5 calculates the same branch locally but does not export that field (`f5_latent_codec.py:300-305`; `revised_watermark_v5.py:1335-1339,1370`).

The exact endpoint implementation is `scripts/m1b_e3_s1_analysis.py:70-84`, imported literally by `scripts/encoder_transfer_test.py:72-75`:

- `S = semantic.found AND semantic.content_match`.
- `C = semantic.read AND semantic.content_match`.
- `A = semantic.found OR instance.found`. A is a union, **not an instance-only endpoint**.
- `Q = semantic.read AND valid decoded semantic word equals valid target payload.q`.
- Auxiliary: `J=Q AND semantic.content_match`; `H=instance.read AND decoded H equals target H`; `D=Q AND H`; `F=(outcome=="both_match")`; `recomputed_only_S=S AND NOT semantic.read`.

Q is exact original-code recovery; C checks compatibility with the suspect's content and can be true with Q false. S also admits unreadable recomputed-only detections. None is an ownership-rights verdict. Do not replace these with a convenient score comparison or `watermark_found`.

Payloads differ (`encoder_transfer_runtime.py:154-168`): F5 q is the intended embedding q, but its H reference is the clean native decoder result, explicitly labelled `h_target_basis="native clean decoded h; intended h not exported"`. v5 H is native intended H. H/D comparisons across methods retain that limitation. Wrong-owner and C0 calls receive no target payload, making Q/H false by construction rather than observed recovery failure (`:176-180`).

## Branching and raw-state classification

Let `r = recomputed_score >= recomputed_threshold` and `d = decoded_score >= decoded_threshold`. Then `found=r OR d`, `read=d`. `read_without_found = read AND NOT found` is logically impossible under this implementation. Count it as a data-contract anomaly if found in saved raw calls; do not silently repair it or reinterpret it as a carrier state. The name is a recommended diagnostic, not an existing persisted field.

Use four exhaustive test states: neither (`!r,!d`), recomputed-only (`r,!d`), decoded-only (`!r,d`), both (`r,d`). Add an independent content-status category and exact-original-q flag. This exposes a stronger decoded branch with content mismatch separately from carrier loss. A readable mismatch is not an absent carrier. A recomputed-only content match is S true and C false. `candidate="recomputed"` alone cannot identify recomputed-only, because readable exact-current-code cases use the same string.

Content rules (`revised_watermark_v4.py:978-1018`): rank `unchecked=match=0`, `uncertain=1`, `mismatch=2`; with content checking enabled, distance <=6 matches, >=10 mismatches, and the middle abstains. Profile constants are `experiments/c4-v5-two-tier-regeneration-v1/profile.json`, decision block. Binding modes can deliberately produce `unchecked` that counts as content_match, so preserve `binding_mode`; historical transfer calls use combined mode (`scripts/journal_vae_probe.py:60-69`).

F5 soft semantic comparison uses maximum-likelihood angle times 32/pi when readable, checking enabled, and binding soft; otherwise it falls back to corrected Hamming distance (`f5_latent_codec.py:148-155`). It compares against the same 6/10 radii. v5 uses corrected Hamming distance. Both methods select the instance table using the decoded semantic code when a found semantic key is incompatible with content, and otherwise the recomputed code. Instance status inherits the worse semantic status when semantic is found, or unchecked when absent (`f5_latent_codec.py:300-310`; `revised_watermark_v5.py:1335-1349`). Thus the two channel content results are not independent.

The outcome table gives neither -> not_detected; any mismatch -> copy_paste; both good -> authentic; semantic good with instance absent -> regenerated; instance good with semantic absent -> unclassified; remaining found/uncertain cases -> unclassified. These labels are detector outputs, not externally established histories.

## Carrier geometry, normalization, and margin interpretation

F5 robust/semantic tier uses the pinned SD1.5 encoder's fp32 posterior mode, scaled by 0.18215, followed by orthonormal DCT on four 64x64 channels. Slots have radius [4,32), public weight `(radius/4)^1`, keyed assignment/signs, and per-chip divisor `sqrt(sum(slot_weight^2))` (`f5_latent_codec.py:45-107`). Its 320 chips are ten chips per each of 32 code bits. If latent DCT coefficients are c_j, public weights a_j and keyed signs e_j, projection p_i is `sum_{j assigned i}(c_j*a_j*e_j)/sqrt(sum_{j assigned i}a_j^2)`.

The F5 instance tier remains v5's full-resolution luminance fragile DCT carrier, bound to both q and H. It is not a second latent reader (`f5_latent_codec.py:232-245`). F5 deliberately has distinct carrier domains because its semantic tier seeks regeneration survival while its instance tier seeks sensitivity to instance changes. A survives if either carrier is found; it cannot establish survival of the latent semantic carrier. v5 semantic uses a coarse 128-side luminance representation, image-derived normalizers/activity and weighted DCT slots (`revised_watermark_v5.py:455-499`); its instance uses full-resolution DCT (`:828-839`). Shared thresholds do not imply shared signal geometry or shared robustness.

For either tier `_key_test` computes `sum(w_i*p_i)/sqrt(sum(p_i^2))` for a candidate sign pattern, and maximizes segmentwise for the decoded score (`revised_watermark_v5.py:1180-1200`). This is sqrt(320) times cosine alignment with a 320-sign vector; global positive scaling of all projections cancels. The two thresholds correct for roster_size and 2^32*roster_size respectively, at profile false_positive_target=1e-6 (`:1151-1170,1244-1247`). Read the persisted threshold fields instead of assuming a single threshold.

Embedding margins are `m_i = intended_ws_i*p_i`; their minimum, median and count below zero are saved **only in the clean F5 embedding report**, alongside target_margin=4 (`f5_latent_codec.py:255-261`). They are absolute signed projection amplitudes, not test margins. The writer minimizes squared hinge deficits relative to 4 under its pixel budget (`:175-215`). For the same intended pattern, candidate score is `sum(m_i)/sqrt(sum(p_i^2))`; a high median/minimum alone does not fix this ratio or decoding competition. Raw magnitude can increase while score falls through uneven energy. Further, current recomputed q can change, and each segment competes against its alternate pattern. Neither positive chip count nor clean embedding margin proves readable payload, compatible content, survival through another encoder, or future transfer. Existing attacked raw calls do not persist p_i or attacked signed chip margins; no such values can be recovered from the scalar scores alone. Keep any proposed future projection logging separate from retrospective analysis.

## Channel/control and RNG distinctions

Configuration sources: `research/encoder-transfer-20261019/stage2b-config.json:20-46,50-118,144-156,180-317,725-740`; frozen scheduling explanation: `research/encoder-transfer-20261019/protocol.md:44-46`.

| Contrast | Exact distinction and limit |
|---|---|
| R0 vs R1 | SD1.5 at 512 vs SDXL at 1024 then Lanczos back to 512; different encoders, denoisers, model family and pipeline. Both use explicit DDIM with 20 scheduled steps, empty prompt, CFG1, eta0; no isolated encoder intervention. |
| D1 vs R1 | D1 is SDXL VAE mode encode/decode without diffusion; R1 invokes native img2img encoding (posterior sampling), adds seed corruption, and denoises. D1 is not an ablation that removes only denoising from an otherwise RNG-identical R1. |
| R1-mode vs R1-smooth | Both bypass native sampled VAE encoding and supply a scaled posterior-mode latent to the same R1 .2 path. Smooth averages modes of clipped x +/- four public Gaussian arrays; mode uses unperturbed x. This is the matched P5 contrast. |
| R1-mode vs ordinary R1 | Deterministic mode versus native sampled posterior; bypassing the sampling call also changes RNG consumption before initial corruption. Same seed labels do not guarantee identical corruption draws. |
| D3 vs R3 | D3 is MoVQ encode `.latents` -> decode `force_not_quantize=True`, fp32 arithmetic from fp16-file weights, no diffusion. R3 is full Kandinsky3 img2img, fp16 variant, native DDPMScheduler, 20 scheduled/4 executed updates at .2, empty prompt with guidance1. Precision, scheduler and denoising differ. |
| R1-rinse | Reuses first R1 .1 output, then another .1 pass with seed+100; compares two-pass processing rather than a single .2 noise schedule. |

R0 DDIM config is explicitly constructed in `scripts/three_threat_models.py:28-36,94-110`; R1 replaces the native scheduler from config plus overrides (`encoder_transfer_runtime.py:452-466`). DDIM fields are 1000 train steps, beta .00085-.012 scaled_linear, clip_sample false, set_alpha_to_one false, steps_offset1, epsilon prediction, leading spacing, no thresholding/zero-SNR rescale. Eta0 does not remove posterior sampling or initial noise. Strengths .1/.2/.4 use 2/4/8 updates and starting timestep51/151/351 per frozen protocol; these are not universally comparable dose units across model families.

SDXL VAE encode/decode runs entirely fp32, expanded from the official fp16-file variant, with custom full upcast and guards; UNet/text remain fp16 (`encoder_transfer_runtime.py:83-102,453-483`). F5 reader is fp32 (`f5_latent_codec.py:89-107`). D3 computation is fp32 (`encoder_transfer_runtime.py:385-407`); R3 loads fp16 and precomputes its empty prompt through its own text encoder (`:430-450`). Equal checkpoint storage dtype and compute dtype are distinct facts.

Every regeneration call constructs a new CUDA generator seeded with the unit seed12/13/14 (`encoder_transfer_runtime.py:515-546`); model-specific consumption remains different. The global implementation seed42 resets Python, NumPy and torch before units (`:555-562,658`). P5 perturbations are NumPy default_rng/PCG64 float32, fixed noise_seed20261024, sigma2/255, four antithetic pairs, array-hash checked (`:410-417` and config p5 block). One averaged/control latent is cached per input and shared over its three seeds (`:645-669`). Smooth/mode remain stochastic in diffusion noise; posterior-mode construction alone is deterministic. Repository wrapper source and frozen protocol support these statements; bundled upstream diffusers internals were not independently inspected here.

## Recommended compact stdlib analysis schema

Retain one flattened record per `(stage,row_id,source_id,channel,strength,seed,arm,method,owner,tier)`. Preserve explicit row status, call status and missing reason; never map absent/null fields to zero or false. Record stage/version/config identity and input/output hash as joins, not as new rehash requirements.

For each tier copy all persisted fields above and derive only `recomputed_slack`, `decoded_slack`, `test_state`, `read_without_found`, `found_inconsistent`, `content_status`, `content_match`, and valid code distances to the saved target/current code. Slacks are score-minus-corresponding-threshold. Copy exact frozen S/C/A/Q/J/H/D/F separately at the call level and verify correspondence without replacing the stored endpoints. Add flags for `Q_without_C`, `C_without_Q`, and `recomputed_only_S`. A score's selected branch must always accompany the selected slack.

Use `json`, `math`, `collections`, `csv` only for extraction, cross-tabs, complete paired comparisons, medians/quantiles and source-majority reductions. Keep per-call descriptive states and per-source majority denominators distinct. Report counts planned/observed/missing and complete-pair coverage for each diagnostic. Three seeds are dependent repeat measurements within a source; do not inflate source n. Preserve historical routing and fixed-denominator endpoint handling; these diagnostics explain its outcomes without adding post-hoc success criteria. No inferential regression, causal mechanism conclusion, or inferred attacked-chip state is justified by this reader contract alone.
