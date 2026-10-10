# Frozen delivered-binding development probe

Prospective protocol, 2026-10-10. Implementation: `scripts/journal_binding_probe.py`. No experiment was executed while writing this protocol. This is exploratory mechanism evidence, not an M1/M2 gate or confirmatory run.

## Inputs and identities

Use only saved RGB8 C0/C1 images from MAIN `.thesis-build/dev-runs/20261005-0640-f5-gate-soft-views7`. Sorted adjacent numeric development IDs give six disjoint donor/recipient pairs: (1675,4795), (6012,25394), (80932,109798), (134882,147498), (177015,190676), (468505,499768). Lower ID is donor. Claim alpha is `qim-pilot-owner-alpha`; beta is a distinct experimental recipient label, not a legal ownership assertion or a beta watermark on C0.

The shared `journal_vae_probe.Evaluator` freezes the SD1.5 reader, CLIP, LPIPS and existing profile. Seven semantic views, soft matching, roster one, native match/mismatch radii 6/10, native decoded/recomputed thresholds 8.259326826136963/4.982033056390042. No calibration, held-out inspection, model download, sampler or profile change. Profile and public access assumptions are copied into run.json.

## Fixed arms

Each pair has five arms: legitimate saved D1 positive; unchanged recipient C0 sham; residual transfer at .5 and 1; one public fixed donor-payload synthesis. Residuals are `clip(round(r0 + scale*(d1-d0)))` with evaluator-only D0 access, a stronger diagnostic than the default published-D1-only threat.

Decode donor q and h from saved D1 under alpha before any optimization, retaining full donor decoding fields. Never substitute codes computed from D0. If q is unreadable, record synthesis as failed. If only h is unreadable, synthesize q alone and explicitly exclude a strict full-delivery claim. The raw decoded bits and their Hamming errors remain informative even when `read` is false, but do not count as delivery.

Public synthesis constructs donor-q semantic chips from the public table. Frozen PGD uses 52 dB budget, 150 steps, margin 4, no texture mask. Directly write fragile chips selected by fixed donor q/h; unlike normal `embed_rgb`, do not recompute recipient h. Perform one frozen refinement (58 dB, 50 steps) and repeat the same fixed fragile payload. This mirrors the F5 schedule while preserving donor h. The 52 dB budget concerns initial robust writing; fragile writing and refinement can change total distortion, which must be measured. No adaptive retries, detector-query search or thresholds chosen from outcomes.

Always run this public arm so delivery is measured rather than presumed. It is a local white-box public synthesis diagnostic with substantial encoder/model access and zero external detector queries. It is separately labeled from residual copy-paste.

One additional fixed example on the lowest recipient (4795) recomputes recipient q/h publicly under alpha, then uses the identical synthesis schedule. This demonstrates possible self-consistency without authorization. It is separately labeled `public_recipient_authorization_demo`; it is neither donor-binding failure, a default T4 forgery, nor a legitimate same-owner-image false positive. Total: 31 planned image rows, seven public synthesis attempts, no random seeds.

## Extraction and endpoints

Save PNG first and re-open it; compute seven-view recipient features and frozen VAE latent from saved pixels. Every mode sees identical pixels/features/latent: combined, semantic_only, perceptual_only, none. Native detector results are never overwritten with intended payloads. `none` can report both_match because unchecked statuses are acceptable; it is not authentication.

Strict semantic delivery requires `semantic.read` AND decoded q exactly equal to the fixed intended q. Strict both-tier delivery additionally requires `instance.read` AND decoded h exactly equal to fixed intended h. Report both denominators separately, q/h bit errors continuously, and weaker semantic/both found-presence counts. Recomputed-only found calls cannot establish donor delivery.

Checked semantic acceptance is `found AND read AND content_match`. Native full acceptance is combined `outcome == both_match`. False donor full acceptance is this native endpoint on residual/public-donor recipient arms only. Positives/shams and authorization demonstration retain their own endpoint counts. Native full acceptance may use recomputation fallback, so it must be reported separately from strict delivered full acceptance.

On identical combined-mode extracted signals also report content-disabled semantic/both presence and read-presence. Semantic rejection is the native semantic content status; instance-own rejection uses native corrected h distance before semantic status propagation. F5's q_bound affects instance extraction, and semantic rejection propagates into native instance status; shipped modes are not independent factorial ablations. Disabled controls are read-presence diagnostics, never authenticated attribution.

Summaries retain planned/completed/failed attempts and acceptance on all attempts, strict semantic-delivered and strict both-delivered subsets. Recipient PSNR, SSIM and LPIPS are retained for every saved output. Proxy coverage uses recipient LPIPS <=.20 primary and <=.30 sensitivity. For donor positives, recipient distance is merely a cross-image diagnostic and cannot mean marking fidelity; quality_donor provides positive clean marking quality. Human admissibility remains missing. A proxy-qualified strict-delivered false acceptance falsifies universal binding; zero false acceptance with zero delivery remains unresolved.

## Execution and retained output

Parent commits this code before execution. Example command from worktree: MAIN science interpreter `.thesis-build/a6-science-venv/Scripts/python.exe scripts/journal_binding_probe.py --output-dir <new MAIN development run directory>`. No new official runner is introduced. Parent monitors execution and records one development-log entry.

Retain `run.json` (commit, command, fixed config, empty seed list, development split, elapsed duration and completion/failure outcome), `rows.jsonl`, `summary.json` and all generated images. Row failures remain in denominators; a fatal setup failure writes all pending planned rows as failed. Each pair uses one 150-step robust attempt plus one 50-step refinement; expected GPU runtime is below 15 minutes on the existing local system, an estimate to verify, not an enforced time cap. The script offers no resumable or confirmatory infrastructure.
