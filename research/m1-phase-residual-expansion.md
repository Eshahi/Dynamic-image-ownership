# Frozen IPS quality-cap development expansion

Implementation: `scripts/m1_phase_residual_expansion.py`; schema
`m1-phasemark-residual-expansion-v1`; frozen manifest
`research/m1-phase-residual-expansion-dev.json`. It implements the existing
conditional expansion decision in `m1-phasemark-pilot-decision.md` after the
IPS/quality-cap2-source screen passed (see `m1-phase-residual-results.md`).
No payload, threshold, carrier layout or composition parameter is retuned.

The remaining ten sources are6012,25394,80932,109798,134882,147498,177015,
190676,468505,499768, with exact paths/hashes copied from the development
reservation `m1-reconstruction-dev.json`. Validation rejects any changed
manifest, source path/hash, split, arm, cap or threshold. No test split or
annotations are used. Image policy exactly repeats the original PhaseMark
pilot: RGB required, EXIF transpose, embedded ICC conversion to sRGB with
intent0/flags0, then bicubic512×512.

For each source freshly encode fp32 posterior mean z0 times.18215, insert the
unchanged128-bit public owner-alpha IPS phase word to obtain zm, and decode
both with the pinned fp32 SD1.5 VAE. Use signed float64 D01(zm)−D01(z0),
not RGB8 decoder PNG differences. `source_bypass` calls the original vetted
36-step RGB8 cap directly; zero residual is a valid lambda1/noop. The output
adds source pixels explicitly. C0 is the resized source, and clean C1 is the
capped residual output. Saved/reopened RGB8 feeds each deterministic VAE
cycle and the suspect-only extractor. No old latent or reconstructed optimizer
checkpoint is substituted; fresh z0/zm tensors and SHA receipts are retained.

Plan40conditions:10sources ×C0/C1 ×clean/VAE. Four public owner queries per
condition yield160 correlated query outcomes, with10source clusters. Retain
all missing/failed conditions, no best-attempt or threshold selection. The
extractor is one VAE encode plus original IPS phase readout, no UNet. Record
128bits, soft scores, zero amplitudes, correct/wrong matches at>=82/128,
source and same-arm quality, composition lambda/budget/SSE/MSE/delta hash,
image/source/latent receipts and timing. No CLIP+pHash binding or three-state
claim is added. Human visual assessment remains null.

The CLI remains `--manifest ... --output-dir MAIN/.thesis-build/dev-runs/<fresh>`.
It refuses existing outputs. Code, manifest, source reservation, helper code,
model inventory, decision document and official PhaseMark source snapshots
must match committed Git blobs (CRLF-aware `phase.require_committed`) before
model loads. Model assets are pinned/offline. Started/final/error/interrupted
run records and append-only row events retain terminal conditions; interrupted
rows become not_completed_after_stop. This bounded900s run does not implement
resume: any retry requires a new output preserving the interrupted attempt.
Limits:10GiB GPU allocation,16GiB process RAM,250MiB artifacts. No run was
executed while implementing.

Seven new CPU tests pass, plus six original cap tests: exact40/160 inventory,
remaining-ten metadata, frozen payload/layout, rejected changed manifests,
source-noop equivalence, float residual/cap equivalence with feasible lower and
infeasible upper endpoints, malformed arrays, synthetic IPS phase roundtrip,
and pre-model KeyboardInterrupt receipt with all40 conditions retained.
These test mechanics, not scientific image performance. CLI help is checked.
The analyzer expansion adapter is a subsequent mechanical task; the existing
D-residual adapter deliberately accepts only its original2-source schema.
