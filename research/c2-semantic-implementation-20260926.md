# C2 semantic-key implementation, no real-image execution yet

Issue #16 is ready after B4/#11 actually merged in PR #64 at
`884bf937eec0642de9a83398b97c5854d5e35e43`. Dependencies #6, #14, #15 and #11 are
closed. The reused managed checkout is now `codex/16-semantic-key`. Original
proposal, 38-task graph, research contract and scope guard remain unchanged.

`src/signatures/semantic.py` implements A5's 512-element CLIP image feature,
explicit Torch float32 norm/division, float64 ordered 12x512 SHAKE256 projections,
low-bit-first 12-bit code, nonnegative tie rule, projection margins, and public
OwnerID-bound Ws. The existing B2 arithmetic reference and C3a public-owner
protocol provide independent regression comparisons. Raw floats are never hashed
into a signing key. Code collisions, margins and drift remain measured outcomes,
not assumed robustness.

Import is model-free. The explicit `PinnedClipEncoder.from_checkpoint` load path
uses A6's existing hash-checked official source/checkpoint adapter and exact CLIP
image transform, disables TF32/autocast, and checks deterministic flags again
before extraction. It introduces no downloader, text tokenizer, host-policy
change, substitute generation or alternate model. Study-image calls require the
reviewed runner's separate exact-manifest approval; the class is an algorithm API,
not a replacement approval mechanism.

The local feature cache binds fresh canonical pixel identity, model checkpoint,
official source digests, preprocessing, arithmetic/device/runtime and implementation
bytes. Cache feature payloads are exact widened float32 values with a byte digest.
Cross-version entries are misses; wrong identity, corrupt payload, linked paths,
and overwrite attempts fail and preserve evidence. Feature caching is independent
of OwnerID; public signature derivation happens after retrieval.

Independent reviewer `/root/b3_intake_review` reproduced a candidate-cache
substitution at exact `0dacbb9bfed42f5c8cdc3b8454d5a3349d3e5ac2`: replacing a
synthetic feature and updating its colocated checksum changed q/Ws without an
encoder call. The repair deliberately recomputes every cache hit from the bound
image with the verified encoder, requires exact agreement, and returns the fresh
feature. A checksum alone is not provenance. This version's cache is durable
comparison evidence, not an inference-speed optimization. The attack fixture
fails without overwrite; a real extraction-path synthetic model test and a
linked-path test cover the former test gaps. No real model is used by these tests.

Tests use synthetic vectors, synthetic CPU tensors and temporary cache fixtures
only. No CLIP weights or dataset image were loaded by these tests. The workflow
venv skips Torch-only cases because it intentionally lacks Torch; the existing
pinned WSL science venv runs them without a new install. Real same-image repeats,
fixed benign transforms and different-content comparisons are still missing.
`reports/dev/semantic-examples.json` records NOT_RUN with zero examples, never
fabricated results. Issue #16 must remain open until its real evidence exists.

No projection seed has been selected from features, no threshold has been chosen
from any split, and no result has been observed. A production development recipe
must freeze one public seed, all original 32 development identities, exact input
and config/code hashes, transformations, failures and resource limits before its
separate compute approval. Earlier engineering byte/dimension/color inspection
already occurred; do not claim a seed predates that inspection or retrospectively
label observed feature results preregistered. No held-out image is needed for C2.

Known non-mutating inspection failures this turn: nonexistent guessed method,
preprocess and runtime-helper paths; located actual `configs/method.schema.json`,
`configs/data.json` and installed `schemas/execution.schema.json` using file
inventory. No environment installation or safety bypass followed those failures.
Official run d916749c stays paused at plan-acceptance. This implementation is not
method acceptance, scientific execution permission, rights clearance or thesis
acceptance.
