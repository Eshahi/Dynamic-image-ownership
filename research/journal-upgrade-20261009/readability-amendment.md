# Bounded amendment: readable fixed payload through VAE reconstruction

2026-10-10. Prospective design by Codex design agent. No experiment or new gate verdict is recorded here. Frozen F5 r2, its reader and historical M2 remain unchanged. This is a four-configuration development screen of an **embedding-only refinement**, not a new detector, calibration, latent-generation method, or authorization mechanism.

**Pre-execution corrections:** [payload amendment](readability-payload-amendment.md) supersedes the original-h and already-feasible exact-clean assumptions below: q is the recorded intended code, h is the frozen native-decoded operational target, and original embedded h is unknown. [Compute amendment](readability-compute-amendment.md) supersedes the 60-minute optimization cap with 10,800 seconds and specifies identical-forward checkpointing and exact stationary shortcuts. The historical text below is retained to make those corrections visible. Neither correction changes numerical detector thresholds or the four fixed configurations.

## Decision and evidence

Use a differentiable reconstruction channel in the per-image embedding objective, targeting the actual fixed-payload correlation and all 32 decoding decisions. Start with the existing F5 mark and retain its exact q and h. Do not increase chip amplitude indiscriminately, replace q with the reconstructed image's code, reduce payload length, change the DCT band, add redundancy, or lower thresholds.

The retained discovery has F5 clean/SD1.5-VAE/SDXL-VAE checked acceptance 12/12, 12/12, 10/12; v5 has 12/12 throughout. SDXL failures 4795 and 6012 have decoded scores 7.86278 and 6.74483 below 8.259326826136963, but recomputed scores above 4.982033056390042. These observations locate a read failure; they do not yet identify its physical cause. Both clean methods meet strict quality on all twelve. See [discovery-report.md](discovery-report.md) and the original MAIN `20261010-0903-journal-vae` run.

Literature basis: the already inspected [FreqMark v1](https://arxiv.org/html/2410.20824v1), sections 4.4–4.5, optimizes a perturbation through frozen networks and applies message losses to clean and perturbed images. Its section 4.5 specifically uses latent and pixel Gaussian perturbations. I reopened those method sections from `research/literature/journal-upgrade-20261009/sources/freqmark-v1.html` for this decision. The direct VAE-channel objective below is our hypothesis, not their reported implementation or an inferred guarantee. Its existing card and bibliography entry `Guo2024FreqMarkv1` are retained without adding a duplicate reference. Their distortion and bit-accuracy results are not the present acceptance endpoint. No new paper or factual claim requiring another literature entry is introduced.

Code inspected: `scripts/f5_latent_codec.py` (`Reader`, `Layout`, `robust_pgd`, `embed_rgb`, `detect_rgb`), `scripts/revised_watermark_v5.py` (`_key_test`, `_channel_result`), and both journal probe scripts. The current writer uses a 52 dB/150-step robust pass with chip margin 4, a fragile write, a 58 dB/50-step refinement, and a final fragile write. Its clean chip-hinge objective does not explicitly protect round-trip readability. The reader uses normalized correlation: scaling every projection cannot improve its score.

## Frozen identities and data

Use sorted IDs **1675, 4795, 6012, 25394, 80932, 109798, 134882, 147498, 177015, 190676, 468505, 499768**, with canonical C0 paths from `scripts/f4_transfer_probe.py:SOURCES`. No subset based on these results, new source, held-out pixel, threshold fitting or feature-model change is allowed in this screen.

Reference C1 is MAIN `.thesis-build/dev-runs/20261005-0640-f5-gate-soft-views7/images/clean-{id}-C1.png`. Before optimization, extract q and h from that saved C1 using the frozen combined reader and require both read flags. Store the hex values and exact extraction result. Verify consistency with the original semantic code where recorded; investigate a disagreement instead of silently substituting a code. Both payloads remain constant for that source across every configuration and transformation. This fixed-payload intervention is intentionally different from calling `embed_rgb`, which recomputes h.

Keep owner alpha and the existing wrong-owner labels, profile, public key derivation, 320 chips, 32 semantic bits, instance construction, band (4,32), whitening 1, seven semantic views, soft binding, radii 6/10, roster 1 and both thresholds frozen. Evaluation recomputes CLIP features from the saved suspect image; source features or original codes are diagnostic side information only, never detector inputs. SDXL is now a **seen development transformation**, even for a configuration that does not optimize against it. Future new images cannot restore an unseen-model claim.

## Cheapest diagnostic: separate signal loss from host interference

Before changing pixels, reuse saved C0/C1 and their saved SD1.5/SDXL reconstructions from the discovery. No diffusion generation is needed. Let P(y) be the frozen SD1.5 reader plus the existing Layout, giving 320 real projections. For A in identity, SD1.5 reconstruction, SDXL reconstruction, compute

`b_A = P(A(C0)); p_A = P(A(C1)); d_A = p_A - b_A`.

This is an exact finite-difference decomposition at the measured images, not an assumption that the VAE is linear. Let w be the fixed q's 320-chip pattern, N=320, `alpha_A = dot(w,d_A)/N`, `h_A = dot(w,b_A)/N`, and `r_A = d_A - alpha_A*w`. Record these signed quantities, `norm(d_A)`, `norm(r_A)`, `norm(b_A)`, and carrier gain `alpha_A/alpha_identity` when its denominator is nonzero. Also record displacement alignment `dot(d_A,d_identity)/(norm(d_A)*norm(d_identity))`; label undefined ratios explicitly. Do not use absolute gain to hide a sign reversal.

For every bit j, separately log correct-minus-alternative pattern gaps from b_A and d_A. Their sum is exactly the observed gap in p_A. This identifies whether a lost bit reflects reduced positive mark contribution, a more adverse host contribution, or both. Compare fixed-q score `dot(w,p_A)/norm(p_A)`, searched decoded score, q Hamming errors, recomputed score, minimum bit gap and all native read/content flags. A high searched score with wrong q is not successful recovery. Quantization is part of the measured channel.

Interpretation is descriptive, without tuning a routing cutoff: attenuation is supported by reduced alpha or correct-bit displacement; host interference by worsening host gaps or orthogonal host energy. Both may coexist. A fixed payload removes changed semantic features as an explanation of its carrier score; features can still separately cause content-binding rejection. This diagnostic costs roughly 72 frozen-reader encodes if nothing is cached and does not require a new attack pipeline.

## Objective and capacity argument

For fixed payload q, define `s(p)=dot(w,p)/max(norm(p),1e-8)` and `sigma(p)=max(norm(p)/sqrt(320),1e-8)`. For segment j with its ten-chip correct and alternative patterns, define

`g_j(p) = dot(w_correct_j - w_alternative_j, p_j) / sigma(p)`.

The segment decoder recovers q exactly when every raw gap is positive; positive g_j is equivalent. This condition alone does not establish readable detection. Conversely, crossing the searched threshold alone does not establish exact q. Optimize both, using the fixed dimensionless surrogate

`L(p) = relu(9.0 - s(p))^2 + mean_j(relu(1.0 - g_j(p))^2)`.

Nine is a prospective optimization target above the unchanged 8.2593 decision threshold; one is a prospective bit-gap buffer. They are not new acceptance thresholds or a fitted probability model. Unlike a raw chip-margin loss, this objective penalizes score loss caused by the projection-energy denominator. Do not maximize the searched score: that could reward a different payload.

For an exact decomposition `p=c*w+n`, with `dot(w,n)=0` and c positive, the score is `sqrt(N)*c/sqrt(c*c+norm(n)^2/N)`. Readable fixed-q evidence requires the deterministic ratio `c*c/(norm(n)^2/N) >= t*t/(N-t*t)`, approximately .271 for t=8.2593. This is a geometry threshold, not measured stochastic SNR or a guarantee of exact bits. It demonstrates why aligning the displacement and suppressing adverse host components can help when uniform amplitude scaling cannot. At t=9 the ratio is approximately .339. N and all 2^32 searched alternatives are unchanged; no increased payload capacity or improved false-positive bound follows.

For differentiable optimization, define `Q(u)=u+(round(255*u)/255-u).detach()` after clamping to [0,1]. Forward Q is RGB8 quantization and backward is straight-through; acknowledge its approximate gradient. Identity branch uses `P(Q(u))`. VAE branch uses

`P(Q(clamp((D_A(mode(E_A(2*Q(u)-1)))+1)/2,0,1)))`.

The A encoder/decoder uses its **unscaled** posterior mode directly, matching the probe. Only the terminal frozen SD1.5 Reader applies SCALE=.18215. Models stay eval and frozen; gradients flow through their operations into u. No stochastic posterior samples, diffusion UNet, CLIP gradient, feature-target modification, transformed-source subtraction at detection, or learned detector is introduced.

Minimize the maximum L over the configuration's branches. Compute detached branch losses sequentially, then recompute only the largest branch with gradients; deterministic tie order is identity, SD1.5, SDXL. This implements a subgradient of the worst-branch objective without retaining three graphs. At a branch switch, no optimizer momentum is carried.

## Four configurations, fixed implementation

Each configuration starts independently at saved F5 C1, never at another configuration's result. The frozen C1 and retained v5 are controls, not additional tuned candidates.

| ID | Objective branches | Additional RGB perturbation budget relative to saved C1 | Steps |
|---|---|---:|---:|
| R1 | identity | 52 dB | 100 |
| R2 | identity, SDXL VAE | 52 dB | 100 |
| R3 | identity, SD1.5 VAE, SDXL VAE | 52 dB | 100 |
| R4 | identity, SD1.5 VAE, SDXL VAE | 46 dB | 100 |

R1 controls additional optimization; R2 tests direct channel protection; R3 tests conflict between channels; R4 checks whether six dB more refinement energy rescues the same mechanism while respecting final quality. R2 versus R3 estimates an objective-support effect at equal budget, not a change of carrier location. Run all twelve in sorted order for each configuration; do not specialize settings to 4795/6012. There are no per-source parameter choices, restarts, best-checkpoint selections, extra noise strengths, or unlisted fifth/sixth configurations in this round.

Use mask power zero and normalized steepest descent as in `robust_pgd`, with `B=sqrt(3*512*512)*10^(-budget_db/20)`, learning rate .2B for steps 0–49 and .05B for 50–99. Project the additional delta onto its L2 ball and RGB box after every update. Also constrain total continuous RMS against C0 to PSNR >=35.1 dB using successive projections onto both balls and box; if numerical feasibility is unresolved, reject the update rather than enlarging either ball. The much smaller additional budget is not a claim about final total PSNR.

After step 100, round once and restore the **same fixed q/h** fragile pattern once using the existing `_Fragile`, `_instance_table` and `_embed_fragile` sequence demonstrated in `journal_binding_probe.synthesize`. Do not call ordinary `embed_rgb`; do not recompute h; do not run another robust pass after that restoration. The final fragile write can hurt robust readability or violate quality, and that is a measured failure of this schedule. The reported additional-budget cap applies to the gradient pass; report the final restoration's separate RMS and final C1-relative RMS, rather than claiming the final image obeys that auxiliary cap.

Save final RGB8 and evaluate it through the unchanged reader. Final clean acceptance requires **all twelve** PSNR>35, SSIM>.9 and LPIPS<.1 against canonical C0, exact original q/h with both read flags, and clean `both_match` on all twelve. These are hard whole-configuration eligibility constraints; no substitution of old marks on failed sources, interpolation until a source passes, or threshold relaxation is allowed. The frozen marks meet these constraints, so this stricter clean retention test has a feasible reference. Transformed-image quality remains an attack-admissibility measurement, not the clean marking gate. Report attack-input LPIPS <=.30 and <=.20 proxy subsets and keep all twelve denominators; human verdicts remain missing.

## Screening, selector and kill route

For every configuration evaluate identity, SD1.5-VAE and SDXL-VAE on all twelve C1 outputs; reuse unchanged C0 transformations. Retain every native outcome plus exact fixed-q success `read AND decoded_q==original_q`, and the stronger joint endpoint `read AND decoded_q==original_q AND content_match`. Frozen discovery's 10/12 is a checked endpoint, so compute its exact-q baseline before presenting an exact-q improvement claim.

A VAE-screen survivor must have zero C0 and wrong-owner any-channel detections, meet every clean constraint, preserve **12/12** SD1.5 joint fixed-q successes and achieve at least **11/12** SDXL joint fixed-q successes. Missing/error rows count as unresolved failures, never disappear from denominators. A configuration missing any condition is killed for advancement in this round. Do not lower the 11/12 target after seeing results.

Rank survivors globally by (1) SDXL joint exact successes, (2) minimum fixed-q score across both reconstructed conditions and all twelve, (3) lower mean final clean LPIPS, (4) R1 before R2 before R3 before R4. Try the highest ranked survivor first in the matched SD1.5 .1/.2 seeds 0–2 T3 grid, with existing assessor identities and the retained v5 dev-001 comparator. Reuse deterministic C0 attacks from the identical pinned pipeline where available; generate all 72 C1 identities. Record the complete 36-per-strength counts **and** the historical eligible-row paired counts. Frozen 29/28 versus 27/18 was based on 29/28 eligible identities, so do not mislabel those as denominators of 36.

The continuity gate requires the original M1a comparisons against v5, no decrease versus frozen F5 in matched semantic success at either strength, and no decrease in exact-q/read-checked successes where the frozen values are extractable on the same identities. Readability is the amendment endpoint; historical assumed matches are reported separately. Use `m1_assess_terminal_e2e.py` and `m1_assess_dual_threats.py` as applicable, without silently redefining their endpoints. A scientific adapter may expose the already computed fields; no new execution infrastructure is needed.

Before selecting the amendment, rerun the existing development T4/T5 identities and controls with final candidate marks and the frozen extractor, retaining v5 and frozen F5 comparisons. Require no new false full donor attribution or T5 false match, and no reduced delivery relative to the matched frozen F5 controls; report delivery separately so an apparent security improvement cannot come from unreadability. Reuse the existing T4 residual scales .5/1 and the fixed T5 pairs/ownership exclusions. Also repeat the six predeclared public fixed-donor-payload synthesis pairs using this refinement schedule: retain attempted and exactly delivered denominators, require enabled rejection on every exact delivery with a positive disabled-binding read control, and no loss of the existing five exact deliveries before claiming retained binding evidence. Public recipient re-embedding remains an authorization counterexample; this amendment does not fix it.

If the top survivor fails continuity or T4/T5, retain that failure and try the next pre-ranked survivor within the same fixed budget. Do not retune it. Select at most one global configuration. If none survives, stop this amendment and report its measured ceiling by configuration, per-source score/gap failures and quality margins. Proceed to the independent WAM baseline and separately planned method alternatives; do not label failure of this small refinement family a proof that all latent carriers fail, or request paid compute just to rescue it. If one survives, freeze it before a new, independently selected development panel and fresh calibration/confirmation planning. No new source acquisition or confirmatory manifest is part of this file.

## Compute and implementation bounds

Local RTX 5070 Ti Laptop, 12 GB; MAIN `.thesis-build/a6-science-venv/Scripts/python.exe`; pinned SD1.5 assets and SDXL VAE revision `6f5909a7e596173e25d4e97b07fd19cdf9611c76`. No download or paid compute is needed. Maximum screen work is 4,800 gradient iterations across 48 refinements, plus 96 C1 VAE reconstructions and frozen-reader evaluations. There is no diffusion backward pass and no model training. One transformation branch comprises A encoder, A decoder and terminal SD1.5 encoder, so fp32 activation memory, not model weights, is the uncertain cost.

Run a single gradient/finite-loss smoke on the first source with R3, then discard its trial update and begin the declared sequence from the saved mark. Record peak allocated/reserved CUDA memory and seconds per iteration. Keep CLIP/LPIPS on CPU or off GPU while optimizing; batch size one; sequential branches; release graphs immediately. If ordinary execution exceeds memory, use activation checkpointing through VAE blocks with the identical forward function and verify a finite input gradient. Do not use inference_mode/no_grad around the active path or switch fp16/bfloat16 to make it fit. Tiled VAE execution may change outputs and is not an authorized silent substitution. The 12 GB fit is a feasibility hypothesis until this smoke, not a promised measurement.

Cap this round at **60 minutes of active GPU optimization**, plus **45 minutes for VAE evaluation and the ranked continuity/T4/T5 follow-up**, with per-source/configuration completion records. If projected work exceeds the cap, retain the completed rows and label remaining configurations unrun for budget; do not shorten steps or select a partially evaluated winner. This is local computation, so a compute-limited outcome does not require a paid upgrade. Use existing run.json/rows logging and simple resume-by-completed-source behavior if execution spans an hour; build no launcher, broker, rehearsal or provenance framework. Commit implementation before running; record command, configurations, exact payloads, sources, model revisions, duration, memory and every failure in the development run and log.

The amendment may increase embedding cost while extraction cost stays unchanged. Its only prospective benefit is stronger exact readable semantic recovery under the tested channels at retained quality and threat checks. No cryptographic unforgeability, population FPR, unseen-model transfer, full SDXL diffusion, human quality or journal-superiority claim follows.
