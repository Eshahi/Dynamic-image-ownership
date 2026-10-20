# Core budget and proposals for the user's stage-1 decision

2026-10-19; reopened 2026-10-20. **Prior stage-1 proposal package under section 1b revision; no spending authorized by this document.** These are transparent engineering estimates, not measured GPU timings or live rental quotes. No server was contacted. Let p be the actual all-in instance hourly price; total cost is p×instance-hours plus any separately charged transfer/storage. Obtain that actual price before execution. The unchanged core ceiling is **15 instance-hours or USD15, whichever arrives first**, including setup and return of results.

## Core

Recommend one fast CUDA12.8-compatible GPU with at least24GB VRAM (32GB preferred), at least32GB host RAM (64GB preferred) and at least100GB free disk for models, environment and outputs. Serial loading avoids simultaneous F5/VINE/SDXL residency. The memory figures are planning allowances, not measured compatibility guarantees. A higher-priced GPU can make the dollar deadline shorter; a slow cheap GPU can make the hour deadline binding.

The final schedule includes **C0**, which some topic-local estimates omitted: 2,700 R0 +2,700 R1 +900 extra rinse diffusion calls,300 D1,300 each X1/X2,300 clean units =7,500 total. Smoke adds250 units on two disjoint sources. R0/R1 each require12,600 denoiser updates; rinse adds1,800. Four arms have240 native marks, and C0 is read by all detectors. Wrong-owner and wrong-message calls, LPIPS/CLIP, serialization and transfer are included in overhead.

| Component | Planning instance-hours | Basis, not a benchmark |
|---|---:|---|
| R0 regeneration |1.0–1.5|2,700 outputs at assumed1.3–2.0s/output, including VAE and I/O |
| R1 regeneration |4.0–6.0|2,700 outputs at assumed5.3–8.0s/output with full fp32 VAE |
| Rinse second pass |0.8–1.3|900 short .1 calls, cached first pass |
| Native embeddings and D1 |0.5–1.0|F5 optimization and native baseline generation; no measured server time |
| Detection, metrics, resize, writing |1.0–1.7|CPU CLIP/LPIPS and serial GPU readers; host speed matters |
| Download, install, model loads and smoke |1.0–1.5|20.206GB core assets plus environment, direct server download |
| Return results and stop reserve |0.5|Copied data and verified return before shutdown |
| **Arithmetic envelope** |**8.8–13.5**|No guarantee every component simultaneously hits its upper estimate |

Use **10–14 hours** as the practical rounded planning range. At hypothetical p=$0.80/hour that is **$8–$11.20**; at p=$1/hour, **$10–$14**. These examples are not market prices. The runtime smoke projection, with30% allowance and loading reserve, governs whether the full grid actually fits. At p>$1/hour the allowed time is15/p hours and may require declared reductions or a different user rental choice. No spend beyond the cap is implied.

Download manifest:53 immutable files,20,206,018,703 bytes. Plus62 recorded development JPEGs, a small pinned VINE checkout, and Python packages. Allocate40GB for assets including retransmissions,20GB package wheelhouse and20GB other/code, absolute80GB total downloaded. Do not download optional models as speculative preparation. SDXL selected files are6.941GB; VINE's encoder/decoder/native SD-Turbo stack is approximately9.534GB. Storage footprint and transfer can exceed downloaded model bytes once outputs exist. Stop at the earlier deadline; do not silently convert a download allowance into permission to spend more.

If smoke predicts an overrun, apply only the brief's order: R2 (already disabled), D2 (already disabled), then .1 in R0/R1 and the dependent .1+.1 rinse. This removes2,700 diffusion calls from the present full grid, leaving4,800 planned units. Keep n60, R0/R1 .2/.4, diagnostics and native arms. If that still cannot fit, report a resource blocker. Never choose reductions by detection results. No n120 option is part of the core.

## Ranked proposals, excluded from the core

All costs below are **incremental**, at hypothetical p=$1/hour; at another rate multiply hours by p. They are not included in the $15 core authorization. Approving a scope extension requires a pre-outcome protocol amendment, its own exact settings and an explicit combined money/time ceiling. No proposal has been approved here. Evaluation counts include C0 where relevant; baseline additions reuse existing C0 images but add detector calls.

| ID | Proposal and scoped workload | Extra hours / dollars at $1/h | Recommendation and remaining condition |
|---|---|---:|---|
| P1 | **TrustMark Q**, native checkpoint, initially clean+D1+R1 .2,60 sources×3 seeds for its marks; read shared C0. Full-grid expansion is optional separately. |0.4–1.0h /$0.40–$1; full grid1.2–3h /$1.20–$3 | Highest-priority extra baseline if the user wants one. Public practical post-hoc comparator; exact native checkpoint/threshold/license must be frozen in amendment. No new baseline code is in core. |
| P2 | **StegaStamp**, same limited evaluation cells as P1. |0.6–1.5h /$0.60–$1.50; full grid1.5–3.5h | Second priority for broad recognition; legacy runtime setup is a real uncertainty. Native payload/quality may differ substantially. |
| P3 | **PhaseMark**, same limited cells, subject to complete compatible public release. |0.5–1.5h /$0.50–$1.50; full grid1.3–3.5h | Useful recent regeneration comparator after P1; conditional on code/weight/license preflight. BiSLW is close theoretical prior but its release/compatibility needs resolution before a credible runnable price. |
| P4 | **Kandinsky3/MoVQ** independent family, .2 only,900 outputs including C0 plus300 deterministic MoVQ round trips. |3–7h /$3–$7; full .1/.2/.4 grid about7–17h | Best additional encoder-diversity proposal; do not insert within the existing cap. Selected fp16 assets28.391GB, text encoder21.739GB, needs CPU offload/64GB RAM or larger VRAM. Timings are broad because offload can dominate. KD2.2 is a lower-memory alternative (~15.86GB plus prior) at2.5–6h for limited cells, but native512 adds a resolution confound. Choose one, not both. |
| P5 | **Fixed encoder-aware smoothing**,8 antithetic Gaussian perturbations at2/255 before SDXL posterior-mode encoding; average latent, then .2 regeneration,900 outputs. |1.6–4.6h /$1.60–$4.60; requested ceiling5h/$5 | Scientifically useful optional adaptive T3 arm; detailed no-tuning construction is in T4.2,400 encodes can be cached. Would test a different attacker, not certify adaptive robustness. Prefer after the core unless approved now as one prespecified extension. |
| P6 | **Caption-prompted SDXL .2**,900 outputs, one frozen source-caption rule/model. |1.5–3h /$1.50–$3 | Lower priority than P1/P4. Covers prompt-policy sensitivity; would be the second standard variant. Caption source/model and dependencies must be fixed before any outcomes; no best-caption search. |
| P7 | **Pixel-space regenerator feasibility + limited .2-equivalent grid** (PRX Pixel preferred research lead, or domain-limited DDPM256). |Provisional4–12h /$4–$12, not execution-ready | Defer. No inspected standard native1024 img2img/strength API was qualified. Requires a separate adapter/noise protocol and development validation. DDPM256's domain/downsampling is a serious confound. This is a feasibility allowance, not a promised valid comparison. |
| P8 | **Learned robustified SDXL attack encoder** plus900-output evaluation. |10–29h /$10–$29, provisional | Decline for this experiment. Requires a separate training objective, calibration split and compatibility study; no ready verified drop-in model removes that work. |

Other surveyed baselines are considered but not recommended for added spend in this small study: InvisMark/RoSteALS have native runtime/quality tradeoffs, ZoDiac is slow with a license gap, SpecGuard has incomplete reproducible release details, and the exact SimuFreeMark lead was not verified. These have no credible executable cost until release/license gaps close; no zero-cost or availability claim is made. FLUX remains excluded while gated; SD3/3.5 and large Qwen/newer families do not solve access, lineage and budget issues cheaply. Shared-autoencoder PixArt/Playground/Hunyuan variants add generator diversity without necessarily adding an encoder family.

Priority for a limited additional budget: P1 first, P4 for the central mechanistic uncertainty, then P5 for a prespecified adaptive limitation; P2/P3 only if broader baseline context is worth the setup. Keep the original core decision rule unchanged under all proposals. The original design review is historical. Section 1b requires a new independent floor audit and design review before re-freeze. Claude/user stage-1 review and the user's subsequent server message still precede paid execution.
