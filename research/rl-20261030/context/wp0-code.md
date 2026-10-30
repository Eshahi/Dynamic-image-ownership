# WP0: frozen code, reader semantics and existing allocation

Scope: source reading only on 2026-10-30, checkout HEAD `861291ce8529191dc911fe5d1e7c09420e0be3db`. `PHASE_B_JOURNALS=off`. This is context for later work packages, not a proposed change or an F6 outcome assessment. All factual entries below are SOURCE unless explicitly labelled DERIVED or JUDGMENT. No science code was executed, no results journals or images were opened, and no Stage C/reserve identifier files were inspected.

Files read in full: `research/rl-20261030/BRIEF.md`; `scripts/tifs_writer.py`; `scripts/tifs_denoiser.py`; `research/f5-r2-spec.md`; `research/threat-model.md`; `research/tifs-20261028/stage-p/PROTOCOL.md`. MAIN STATE and AGENTS were not reread by this bounded context reader.

## The retained system and the frozen F6 writer

| Component | What the inspected source actually fixes | Locator |
|---|---|---|
| Retained F5 r2 | Frozen code/profile; SD1.5 posterior-mode VAE, fp32; latent 64, scale 0.18215; DCT radial band 4–32, 3,272 slots mapped into 320 chips; radius/4 public weights and owner-derived signs. | `research/f5-r2-spec.md:3–12` |
| Retained F5 robust objective | 150 normalized-gradient PGD updates through encoder; squared hinge at margin 4; L2 budget corresponding to 52 dB; [0,1] box and RGB8 rounding. Fragile luminance tier at 47 dB, followed by one refinement. This is an image-domain writer using encoder gradients; its historical name containing “latent” does not establish the proposal's latent method. | `research/f5-r2-spec.md:7–9`; `BRIEF.md`, honesty rule |
| F6 variants in implementation | `f6-noise`, `f6-codec`, `f6-generic`, `f6-x0`, `f5-budget`; these are not all Stage P candidates. Robust PSNR choices 52/46/42/38. | `scripts/tifs_writer.py:19–30` |
| Input and owner | Exactly RGB8 512×512×3; writer fixes owner to imported `ALPHA`, resolves unchanged F5 profile/config, and constructs F5 layout with band [4,32], whitening 1. | `scripts/tifs_writer.py:123–157,400–406` |
| Content code | Original source's seven-view CPU CLIP features produce fixed semantic code q and desired chip vector w. q is held through robust insertion, fragile insertion, refinement and final fragile insertion. | `scripts/tifs_writer.py:145–152,410–420` |
| Surrogate schedule | Round-robin `(R0,.2),(R1,.1),(R1,.2)` over 150 robust updates; one surrogate realization per update. R0/R1 prompts must be empty and guidance 1.0, with 20-step native schedules. K3 is absent from this optimization cycle. | `scripts/tifs_writer.py:21,84–88,167–181,355–366`; `stage-p/PROTOCOL.md:30–34` |
| F6 objective | For each robust update, compute clean squared-hinge reader loss and its input gradient, free that graph, then compute surrogate reader loss and add its gradient. Equal additive clean/surrogate weights. Refinement uses clean loss only. | `scripts/tifs_writer.py:245–256,343–380` |
| Update and projection | Normalize summed gradient; step size `budget*.2` for first half, `budget*.05` for second half; project clamped perturbation back to L2 ball after every step. Robust stage has 150 updates; refinement has 50 at 58 dB. | `scripts/tifs_writer.py:343–380` |
| Finalization | Robust RGB8 round → fragile luminance embedding → 50-step clean refinement → RGB8 round → second fragile embedding → unchanged reader verification. | `scripts/tifs_writer.py:382–424` |
| Budget comparator | `f5-budget` delegates directly to retained `robust_pgd` with same update/projection order. At original 52/58 settings the calls are intended to match retained F5; actual numerical equality is a server verification item, not a result established here. | `scripts/tifs_writer.py:347–350`; `stage-p/PROTOCOL.md:49` |

DERIVED: clean and surrogate gradients are accumulated with coefficient 1 each; there is no learned weighting, policy, value function, replay buffer or policy-gradient estimator in this inspected loop. Its current optimizer is projected gradient descent, not RL.

## What each surrogate computes

SOURCE: `f6-codec` encodes by posterior mode and decodes. R0 uses retained F5 VAE; R1 differentiably upsizes 512→1024, normalizes RGB to [-1,1], casts through fp16 then back to fp32 before SDXL VAE encoding, and differentiably downsizes decoded output back to 512. VAE decode and clip to [0,1] are in the input-gradient path. (`scripts/tifs_writer.py:263–296`; float Lanczos approximation explicitly reported at `:449`.)

SOURCE: `f6-noise` adds Gaussian noise at the *first executed native timestep* for the scheduled family/strength: `z_t = sqrt(alpha_bar)*z + sqrt(1-alpha_bar)*epsilon`, then directly decodes the noisy latent. It is not a full native regeneration trajectory. (`scripts/tifs_writer.py:167–181,263–296`.)

SOURCE: `f6-x0` samples a timestep from that family's executed native window using a source/family/strength/update/stream hash. It adds noise at that timestep, makes one native conditional epsilon prediction, computes `x0=(z_t-sqrt(1-alpha_bar)*epsilon_hat)/sqrt(alpha_bar)`, then decodes. Its timestep is not necessarily the first native step. (`scripts/tifs_denoiser.py:14–37,86–110`; `scripts/tifs_writer.py:212–238,263–296`.)

SOURCE: windows are obtained from pinned pipeline `get_timesteps`, not interpolated; supported scheduler is 20-step, epsilon-prediction DDIM, order 1, no clipping or thresholding. Exact numeric timesteps/alphas depend on retained scheduler config and are not printed in these files. Do not invent them from strength alone. (`scripts/tifs_denoiser.py:14–28`.)

SOURCE: x0 conditioning mirrors native empty-prompt encoding. Guidance 1 means no classifier-free negative branch; SDXL also supplies pooled text and size/crop time IDs (1024×1024, zero crop). UNet is frozen eval fp16; casts retain gradients; x0 arithmetic and decode are fp32. Text embeddings are cached without gradients. (`scripts/tifs_denoiser.py:50–145`; `scripts/tifs_writer.py:212–238,441–448`.)

SOURCE: generic baseline cycles Gaussian blur (sigma 1.5, 11×11 reflect padding), bilinear 512→256→512 resizing, and clipped Gaussian RGB noise sigma .02. These are differentiable transformations in the writer's surrogate path; they do not add T1/T2 threats to the primary verdict. (`scripts/tifs_writer.py:298–324`; `BRIEF.md`, threat-scope rule.)

SOURCE: optimization noise seeds include source, variant, update and stream; diagnostic and optimization streams are separated. Robust budget/candidate ID is absent, so within a variant budget candidates share draws. x0 timestep selection has a separate deterministic hash domain. No independent seed axis is selected by Stage P. (`scripts/tifs_writer.py:91–97,258–261,332–341`; `scripts/tifs_denoiser.py:31–37`; `stage-p/PROTOCOL.md:30`.)

## Gradients: availability is not measured price

| Interface | Gradient actually available from the inspected implementation | Boundary or qualification |
|---|---|---|
| RGB perturbation → fixed F5 chip-margin loss | Yes: `reader.encode` preserves the input graph, tensor DCT/index accumulation and squared hinge feed `autograd.grad`. | Reader model parameters remain frozen. A zero-loss region may yield no useful gradient; no prevalence is measured here. (`tifs_writer.py:245–256,355–359`.) |
| RGB → codec/noise surrogate → fixed reader | Yes through encode/decode, scale, sampled additive noise, resizing and clipping. | Posterior mode and differentiable float resize are approximations; native RGB8/posterior sampling is not claimed identical. (`tifs_writer.py:263–296,365–367,527`.) |
| RGB → one-step x0 → fixed reader | Yes through frozen UNet input; explicit fp16 casts are differentiable. | This is one denoiser evaluation, not differentiation through the full native attack. (`tifs_writer.py:212–238,285–289`; `tifs_denoiser.py:1–4,86–110`.) |
| Native epsilon prediction | Rehearsal explicitly probes epsilon-input gradient so the x0 identity term cannot hide a detached denoiser. | A code check is not evidence that a real server rehearsal passed. (`tifs_writer.py:225–234,462–527`.) |
| Semantic q and fragile h/codes | Source q is computed outside the torch optimization and held fixed; fragile body uses discrete code/table operations and RGB8 rounding. | No end-to-end differentiable graph through CLIP-code selection, fragile embedding or final detector decisions is supplied by these files. (`tifs_writer.py:382–424`.) |
| Whole native regeneration, C/J/F decision, final strict quality | No gradient interface is shown in these two modules. | Their external runtime/readers must be inspected separately before claiming either mathematical nondifferentiability or logged-field semantics. The writer optimizes chip margins, not the exact boolean end-to-end endpoint. |

SOURCE: report counters are 350 reader-gradient evaluations for F6 (150 clean + 150 surrogate + 50 refinement), 150 surrogate gradients, 150 codec gradients except generic, and 150 UNet gradients only for x0; `f5-budget` has 200 reader and zero surrogate/codec/UNet gradients. (`scripts/tifs_writer.py:430–443`.)

SOURCE: the writer reports total embedding seconds but no per-gradient timing in these files. Frozen-eval VAE/UNet checkpointing and serial graph accumulation trade memory for recomputation; codecs/UNets move to CPU between graphs and model loading adds cost. (`scripts/tifs_writer.py:33–69,196–238,313–317,355–371,407,429–452`; `scripts/tifs_denoiser.py:113–145`.)

JUDGMENT: call counts are a defensible inventory, not a conversion to seconds. F6 measured gradient/write time remains unknown under this session's outcome blindness. The brief's F5 732-second shared-machine median and F6 361–723-second planning anchor are brief-supplied claims, not measurements verified by this reader; the latter must not become measured evidence. Equal update counts also do not imply equal GPU cost across F5, codec, noise and x0.

## Detector, endpoint and owner semantics

SOURCE: retained F5 side information includes public OwnerID/profile and pinned CLIP and SD1.5 encoder weights. Its seven fixed CLIP views are full, mirror, four corners and center at 7/8; mean embeddings are renormalized before keyed Rademacher projections yield 32-bit q. Soft angle likelihood, radii 6/10 and v5 decision table are retained. (`research/f5-r2-spec.md:9–12,20`.)

SOURCE: F6 verifies the final saved RGB8 image using exactly F5 `detect_rgb`, latent from that image, correct owner, seven-view suspect semantics, band [4,32], whitening 1 and `binding="soft"`. `verified` is `verification["outcome"] == "both_match"`. Reported q is original source q; reported payload h comes from native clean *decoded* h, while intended h is exported separately. This distinction avoids silently treating intended fragile payload as recovered payload. (`scripts/tifs_writer.py:422–440`.)

SOURCE: Stage P requires source majority ≥2/3 native seeds for C and J, retaining their distinct Stage S definitions. It explicitly prohibits replacing J with owner-only or code-presence success. It also uses clean F and zero C/F on wrong-owner/C0 calls. (`stage-p/PROTOCOL.md:34,47,55`.)

Unresolved interface: the inspected files do not define the complete runtime mapping of C/J/F or exact `calls.<owner>.raw.semantic/instance.{score,threshold,code_distance,content_match}` meanings. The brief's vocabulary is a starting guide; WP3 must inspect the actual reader and journal producer before calculating margins. In particular, do not equate `both_match`, clean F, exact-original-code J and content-compatible C merely because they are correlated or share a detector.

SOURCE: the threat model says OwnerID and derivation are public; there is no specified secret, no cryptographic unforgeability, and no implication that possessing OwnerID authorizes marking. Attribution is conditional on tested candidates, not legal ownership. Semantic similarity is not instance identity; semantic-only detection does not diagnose regeneration. (`research/threat-model.md:7–16`; `research/f5-r2-spec.md:21`.)

SOURCE: controls distinguish unmarked/matched reconstructions, correct owner, wrong public owner, wrong-pattern diagnostic, distinct similar instances, donor-target sham/transfer, and binding ablations. Per-candidate and any-of-K attribution and actual query counts must be separated. (`research/threat-model.md:20–24,45–55`.)

## Stage P already occupies adaptive allocation

SOURCE: eight candidates are `{noise,x0} × {52,46,42,38}` robust PSNR; refinement remains 58 dB. No prompt/guidance/threshold/detector/EOT-count/step-count/k-step search. Sixteen existing development sources tune; a separate eight-source development partition only vetoes the nominated winner. Neither partition is new confirmation. (`stage-p/PROTOCOL.md:7,17–34`.)

SOURCE: successive halving uses cumulative 4/8/16 tuning sources with entrant/survivor caps 8→4, 4→2, 2→1; separate eight-source check evaluates one fixed winner. Earlier rows are reused and sources are added; no extra seeds, rewrites, eliminated-arm revival or post-check fallback. (`stage-p/PROTOCOL.md:38–45,86–102`.)

SOURCE: ranking is lexicographic: minimum then sum of six foreign C/J counts across R1 .1/R1 .2/K3 .2; minimum then sum of R0 .2 C/J; lower median LPIPS, higher PSNR, higher SSIM; candidate ID. K3 is optimization-excluded but explicitly selection-seen. (`stage-p/PROTOCOL.md:32,59–70`.)

SOURCE: maximum inventory is 72 candidate writes + 24 retained F5 + 40 budget-control F5 = 136 marks; 136 repeated C0 source-directory units; 3,264 native attempts including those repeats. These are only 24 unique originals. Wrong-owner/C0 calls, quality/reader work, setup, gradients and retrieval add cost. T4/T5 and external baselines are not evaluated in P; they remain Stage S requirements. (`stage-p/PROTOCOL.md:45–51`.)

SOURCE: absolute per-source quality is PSNR >35, SSIM >.9, LPIPS <.1; clean F is 4/4, 8/8, 15/16 and 8/8 at rungs/check; missing required measurements and negative calls block advancement. Gate profile must be fixed before outputs. Round1 uses retained-F5 quality parity; prospectively approved proposed profiles add finalist budget-control requirements. Nominal writer PSNR cannot substitute for observed saved-image quality. (`stage-p/PROTOCOL.md:55–72`.)

SOURCE: nomination needs every foreign and home C/J count ≥12/16, then every check C/J count ≥6/8. Those small-screen thresholds and listed binomial tail examples are not selection-adjusted inference. RESOURCE_STOP and INCOMPLETE remain separate from scientific failure. (`stage-p/PROTOCOL.md:76–90`.)

JUDGMENT: this is already fixed, bandit-style allocation and must be compared as the existing successive-halving comparator. Calling it a new RL contribution would relabel prior work. Its adaptivity is which configurations receive further data, not a trained within-image policy.

## Care points for the main synthesis

1. SOURCE/JUDGMENT: Stage P's header still says proposed/pre-output, round1 effective (`PROTOCOL.md:3`), while the RL brief records a later approved F6 package. Treat the protocol as mechanism/design evidence; root must use its already-inspected decision/amendment evidence for effective authorization/profile. Do not infer a current run state or outcome from an older status line.
2. SOURCE/JUDGMENT: F5 spec's “other encoders untested,” exploratory-only status and original quality bar are historical freeze statements (`f5-r2-spec.md:13,19,22,24–32`). They cannot override later Phase A/B source reports or the present strict quality rule. The spec was read for the frozen mechanism, not as a current results summary.
3. SOURCE/JUDGMENT: general threat model lists T1/T2/T6–T9, but this session's verdict is T3/T4/T5 only. Adaptive red-team policies in the brief must disclose that original T3/T4/T5 contracts specify Q=0 feedback; adaptive white-box and composite chains were initially excluded (`threat-model.md:22,33–41`). Researching an extension does not retroactively validate it under the old nonadaptive protocol.
4. SOURCE/JUDGMENT: differentiable surrogate ≠ full native trajectory; epsilon/x0 parity is restricted to a captured native first noisy latent and conditioning, not image/preprocessing/posterior parity (`tifs_denoiser.py:148–154,205–210`). Rehearsal checks existing in code are not measured success.
5. SOURCE/JUDGMENT: robust and refinement budgets are centered at different stage inputs, and fragile writes/rounding occur between/after them (`tifs_writer.py:352–380,415–421`). Thus final PSNR is neither guaranteed equal to robust budget nor identical across equal nominal-budget methods.
6. SOURCE/JUDGMENT: a successful P screen cannot establish T4/T5 binding or the article rule; those studies are deliberately absent there (`PROTOCOL.md:51`). Every RL assessment must preserve the separate quality, C/J, wrong-owner/C0 and binding endpoints.
7. SOURCE/JUDGMENT: public-derived owner patterns cannot support a secret-key security claim; wrong-owner rejection and protection against copying do not establish authorized identity or resistance to re-embedding (`threat-model.md:9,14,36–43`).

No implementation amendment, WP1 candidate design, execution recommendation or F6 outcome conclusion is made in these notes.
