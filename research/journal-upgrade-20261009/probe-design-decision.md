# Two decisive development probes

2026-10-10, Codex design agent. Prospective scientific decision; no execution or official gate verdict. Preserve frozen F5 r2 and historical M2. Use only the twelve canonical development sources and saved C0/C1 images in MAIN `.thesis-build/dev-runs/20261005-0640-f5-gate-soft-views7`. No new calibration, held-out access, or infrastructure.

## 1. Independent-VAE survival

**Run SDXL VAE-only reconstruction first.** It directly tests whether a signal optimized against SD1.5 survives another autoencoder's image manifold. It is a cheap falsifier of broad autoencoder robustness, not evidence about SDXL diffusion and not a monotonic predictor of later denoising. Establish checkpoint/weight provenance: a renamed or precision-converted SD1.5 VAE is not independent; architecture similarity alone neither establishes nor refutes independent training. Record the exact SDXL VAE provenance and any shared ancestry.

Use all twelve saved C0/C1 pairs, unchanged 512×512 resolution, deterministic posterior mode, float32, RGB8 final rounding. Encode normalized RGB, decode the *unscaled* posterior mode directly; do not apply SD1.5's latent scale to SDXL. Run the same reconstruction with SD1.5 as a matched control. This is 48 reconstructions, no random seeds. The existing reconstruction recipe is `scripts/f5_gate.py:146–150`; the frozen detector always retains its SD1.5 encoder (`scripts/f5_latent_codec.py:88–107`). Changing the detector VAE would test a new method.

For clean and reconstructed images record:

- C1 correct-owner checked semantic acceptance = `found AND content_match AND read`; raw semantic presence, assumed acceptance without `read`, full `both_match`, scores and code errors separately. This matches `scripts/m1b_coco512_analysis.py:30–46`.
- C0 correct-owner and C1 one fixed wrong-owner call; report any-channel detections. Reuse identical pixels across owner calls.
- PSNR, SSIM and LPIPS against each attack input; clean C1 quality against C0. Strict marking quality remains PSNR >35, SSIM >.9, LPIPS <.1. Reconstruction is an attack, not a new marked image required to meet those clean limits.

Use LPIPS <=.30 as the numerical admissibility proxy, with <=.20 sensitivity. Human admissibility remains missing; never label proxy-qualified images human-validated. Preserve all twelve denominators and give proxy-qualified counts alongside all-source results.

**Routing fixed before results:** if SDXL gives >=11/12 checked successes, proceed to full independent-backbone .2/.4, seeds 0–2. If <=10/12, broad VAE robustness has missed this engineering screen: retain the negative and diagnose carrier-read loss versus binding rejection. If SD1.5 also fails, check preprocessing once before interpreting generalization. If SDXL loses detection only on high-distortion reconstructions, the admissible-removal conclusion is unresolved. Do not change thresholds or regenerate favorable marks.

A VAE-screen failure warrants a narrow .2, seed-0 grid on all twelve sources if the full model is freely available locally: denoising might restore or further destroy acceptance, so reconstruction alone cannot logically settle diffusion survival. Expand to the three-seed .2/.4 grid only if that narrow grid reaches 11/12 checked successes; otherwise revise the mechanism before a larger grid. This is a development triage policy, not a statistical gate.

Full grid: 12 sources × 2 controls × 2 strengths × 3 seeds = 144 generated images; wrong-owner calls reuse C1. Pin sampler, steps, effective timesteps, prompt, guidance, model revision, VAE and resolution; retain SD1.5 continuity results. At 512 resolution label SDXL's resolution regime explicitly. The roadmap's >=.90/.70 targets translate to >=11/12 and >=9/12 source-majority successes (at least two seeds). They do not establish population bounds, a carrier advantage, or equal attack severity across models. Report measured distortion and common proxy-qualified comparisons.

## 2. Delivered-mark binding

**Keep the interface claim narrow:** suspect RGB + claimed OwnerID provides self-consistency checking, not enrollment-aware instance verification. Another legitimately marked image under the same owner is not false owner attribution. Freeze existing decoded/recomputed thresholds 8.259326826136963/4.982033056390042, soft matcher, seven views, match/mismatch radii 6/10, roster 1. Nominal .001 calibration belongs to a later study.

Sort the twelve numeric source IDs; pair adjacent IDs, lower ID donor, higher recipient: six disjoint pairs, fixed without outcomes. Assign donor claim alpha and a distinct recipient ownership label beta for the adversarial scenario. These are experimental identities, not assertions of legal rights. This pilot can falsify a mechanism but cannot establish low error rates or the roadmap's 100-delivered-pair criterion.

First reuse the existing residual diagnostic: `clip(round(r0 + a*(d1-d0)))`, a=.5,1, twelve outputs. Unmarked donor access is evaluator-only, stronger than the default published-marked-donor threat (`scripts/f5_t4.py:63–88`). Include unchanged r0 sham and legitimate d1 positive. Evaluate the same saved pixels in combined, semantic-only, perceptual-only and none modes. Do not count `none`'s `both_match` as authentication: unchecked statuses intentionally count as acceptable (`scripts/revised_watermark_v4.py:977–1009`).

Crucially, `semantic_found` is insufficient donor delivery. Recomputed-only detection assumes the recipient's own code; require `semantic.read` and decoded code exactly equal to the intended donor q for the strict delivery subset. Report Hamming errors continuously and weaker presence separately. For full binding require both tiers read and recover intended donor q and h. Failure to deliver either tier is not successful combined binding. `_channel_result` documents the recomputation fallback at `scripts/revised_watermark_v5.py:1232–1277`.

**If residual delivery is weak, publicly re-embed a fixed donor payload.** The frozen profile is public-derived (`scripts/revised_watermark_v5.py:304–314`). Decode q/h from d1 under alpha, requiring readable codes; do not substitute evaluator-known C0 codes silently. Construct donor semantic chips from the public table and optimize them onto r0 using unchanged F5 PGD. For the full diagnostic, write the donor q/h fragile pattern and perform the same fixed refinement schedule. Do not call ordinary embedding with donor features and assume it preserves donor h: `embed_rgb` recomputes recipient h at `scripts/f5_latent_codec.py:233–250`. If h is unreadable, retain a semantic-only diagnostic, not a full-binding result.

Use one fixed attempt per pair, frozen 52 dB robust budget, 150 steps, margin 4, one refinement; no threshold search. Public gradient optimization is a white-box synthesis attack, separately labeled from default copy-paste. It has zero external detector queries but substantial local model access. Delivery cannot be guaranteed within fidelity constraints: measure it. The experiment is non-tautological because the donor payload is fixed before optimization, the detector re-extracts from saved pixels, and content checks see recipient features; never inject decoded values into detector results.

For every arm report delivery/all attempts, exact donor recovery, enabled acceptance/all attempts, and enabled acceptance/strict delivered subset, plus recipient LPIPS <=.20 proxy coverage (.30 sensitivity). Compare acceptance with content predicates disabled on identical extracted signals; separately report semantic rejection and instance rejection. Preserve shipped mode outputs too: F5 propagates semantic status into instance status (`scripts/f5_latent_codec.py:290–311`), so those modes are not fully independent factorial components.

Any proxy-qualified delivered false acceptance defeats a universal binding claim. Zero acceptances with zero delivery is unresolved. Delivered rejection with a positive disabled-binding control licenses a larger mechanism study only. Finally, public re-embedding with *recipient* q/h under victim alpha can produce self-consistent marks without authorization; test one fixed example if needed to demonstrate the limitation. That is public synthesis, not donor-binding failure or a same-owner legitimate-image false positive. No outcome establishes cryptographic ownership.

Commit probe code before execution; retain run.json, all failures and one dev-log entry. No official gate or human verdict is changed.
