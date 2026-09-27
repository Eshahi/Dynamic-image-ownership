# C4 preservation localization package before repair selection

Issue #18, exploratory development only. Applies method-spec.md,
research-contract.md and scope-guard.md. Direct user requested fixing the observed
quality loss; that authorizes software/design work, not unbounded scientific
execution or silently replacing diffusion latent/noise embedding.

The reviewed retained candidate/source and control/source both failed all three
quality targets. Candidate/control similarity is not source preservation. The
current evidence does not separate VAE compression from the fixed two-step DDIM
suffix/noise/conditioning effects. Keep the original config and failed evidence.

One prospective coherent run holds source109798, all components, empty condition,
native pad/crop, VAE scale, seed0 and DDIM[101,1] fixed. Exactly three arms share
one encoded source: VAE-only decode; DDIM with zero initial noise; unchanged
DDIM with deterministic prior base noise. No watermark, optimizer, new image,
strength search, substitution or held-out data. Zero noise is an ablation, not
an identity: add_noise still scales the latent. None is a replacement candidate.

All three saved PNGs use existing ties-to-even native-grid IO. Classical quality
is saved durably immediately, then the same CUDA safety checker is restored and
run on each saved arm. Flagged content remains restricted and blocks continuation;
it is not replaced by black pixels. After SD is released, all three source-referenced
LPIPS outcomes are computed in one batch. Model/source/condition identity, partial
cells, saved PNG digests, source metrics, safety flags, replay and resource values
are retained. On a later error earlier outcomes stay durable; no terminal report
means interrupted/incomplete, never a clean negative or success.

The unchanged base-noise arm must match prior control canonical RGB bytes exactly.
A mismatch is a profile/replay failure; preserve all new PNGs/classical outcomes
but stop before further comparison claims. This is stricter than closeness and
does not establish numeric model parity by itself. No CLIP image extraction or
pHash rerun is needed for localization. SD's text/safety components remain used.

Resources are prospective estimates: local USD0,20-minute outer cap,9GiB fixed
Torch allocation (not whole GPU/OS cap),12GiB RAM estimate,4GiB disk for checked
model snapshot and outputs. Require10GiB measured free VRAM,13GiB available RAM,
4GiB free disk; stop if unavailable. Phase residency/checkpoint decoder reuse
preserves fp32 arithmetic. Windows C1 schema validation bridges exact config
bytes into the pinned Linux62-distribution science environment. Network defense
is Python socket blocking/offline flags, not an OS hostile-code sandbox.

This hypothesis is falsifiable: VAE-only may also fail source targets. No result
is guaranteed and no scientific claim is accepted now. The generic paired-seed
analysis helper is not used to aggregate dependent arms into independent N3 or
manufacture a CI; report every unaggregated source comparison and failure.

Before execution: complete owned CPU tests and independent exact full-package
review, finalize a clean commit and canonical manifest, official design helper
and dry runner preview, independent final binding, then one actual user decision
for that exact package. Consumed run003/saved-pair001 approvals do not apply.
Only after localization evidence may a separately reviewed and approved repair
candidate change ordinary method parameters; no automatic pixel-space replacement,
original-assisted detector, weaker target, paid RunPod or dataset reduction.
