# C6 key-study ledger preparation

Issue #20; **software preparation only, not a scientific run or C6 acceptance**.
Applies [research-contract.md](research-contract.md), [scope-guard.md](scope-guard.md),
[method-spec.md](method-spec.md) and [acceptance.md](acceptance.md). Dependencies
#17/C3b, #11/B4 and #5/A4 are actually closed. C4's separately approved-package
question is pending; that does not prevent independent ordinary C6 software tests.
The original 38-task graph, proposal and final data commitments are unchanged.

## Implemented bounded contract

`src/signatures/key_study.py` takes explicit development sample/pair metadata and
precomputed observations. It imports no model, reads no image and uses no GPU.
`scripts/check_keys.py --plan <file> --preview` is a bounded, read-only metadata
validator. There is deliberately no scientific execution mode or extraction
adapter. A valid preview is not a frozen source frame, provenance certificate or
compute approval. Caller-supplied feature/pHash values still need image custody
and actual extraction under a separately reviewed exact scientific package.

The ledger records source/group/domain IDs for both members, relation, variants,
annotation/protocol reference and every predeclared pair, including missing or
failed observations. It checks development-only inputs, stable source domain/group
metadata, unique pair/sample IDs and owner-change isolation. A same-domain pair
is **not** labeled same-topic or unrelated by inference. `distinct_unscreened`
explicitly leaves the semantic label unresolved. Same-topic, near-instance and
unrelated annotations require independently inspected evidence before a study;
the presence of an evidence-reference string alone does not establish it.

Completed observations use existing C2 `quantize_features` and C3a
`derive_public_signatures` without changing their algorithms or projection seed.
The evaluator reports normalized-feature cosine distance, 12-bit q distance,
32-bit pHash distance, separate 256-bit Ws/Wi distances and separate exact key
agreement. The cosine uses actual widened-float32 norms; identical float32
features do not get a spurious distance from assuming their norm is exactly one.
An exact input repeat is distinct from a benign edit. Wrong-owner comparisons
hold the entire observation fixed and change only the canonical public OwnerID.
Cryptographic digest distance is not semantic similarity, and small pre-hash
distance is not a successful blind detector observation.

Missing input stays pending with null measurements; explicit extraction failure
is a failed pair with a retained error. Malformed supplied observations block,
rather than becoming measured negative/collision results. Completed-only exact
agreement denominators and planned/completed/failed/pending counts stay separate.
No missing value is converted to zero-distance, nonmatch or a favorable outcome.

All planned pairs union their source dependence groups, including failed or
missing pairs. Shared-source/transitively connected pairs remain connected.
Component counts are descriptive, **not established independent sample sizes**.
The summary deliberately emits null independent N/CI and
`UNRESOLVED_DEPENDENCE_AND_PROTOCOL`; no pair-binomial interval, AUC, practical
margin, threshold or efficacy verdict is fabricated. A group-aware inference
rule and adjudicated pair sampling still require a prospective scientific design.

## Tests and limits

Owned one-hot float32 feature fixtures and synthetic identifiers test exact
repeat/owner isolation, one-bit pHash versus hashed-distance changes, orthogonal
feature distance, visible negative exact-code collisions, missing/failure nulls,
duplicate/missing/relabel/split rejection, dependence through absent outcomes,
invalid observations and preview with model construction explicitly forbidden.
These are algorithm/ledger tests, not image robustness or collision evidence.

Initial focused Windows suite: 38 tests, 34 pass and four expected optional
environment skips (`test_key_study`, owner, instance, semantic). No scientific
pixels, model loads, new downloads, packages or original C4 manifest edits.
Independent narrow review is required before accepting this software checkpoint.

## Remaining C6 deliverables

1. Freeze reviewed real development source/variant/pair IDs with full B4 linkage,
   human/inspected same-topic/near-instance/unrelated evidence and deterministic
   A4 owner roster. Do not label an unscreened pair as a hard negative.
2. Specify transformations, endpoints, grouped uncertainty, denominators and
   criteria before new outcomes; blocked practical margins remain unresolved.
3. Implement an exact-byte approved extraction worker/package, rechecking source,
   feature/pHash/model/environment custody and retaining every planned failure.
4. Obtain exact scientific manifest approval, execute only its listed batch,
   independently analyze actual results and populate the declared CSV/summary.

`reports/dev/key-stability.csv` and `key-stability-summary.md` are not fabricated
from owned fixtures. Existing C2's 96 semantic observations do not measure Wi or
adjudicate C6's hard-negative relations. Issue #20 remains open. No C6 hypothesis,
ownership authority, validation/test result or lifecycle gate is accepted.
