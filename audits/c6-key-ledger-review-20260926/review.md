# C6 bounded software review

Date: 2026-09-26. Actual independent actor `/root/b3_intake_review`; author `/root`.
Authority: AGENTS.md and research/approval-policy.md delegated independent
technical review. This is not a human verdict, lifecycle gate decision or full
scientific evidence acceptance.

Exact initial code/docs: `f3729db8b164fb3ebd0c8843094227addd9ec0cd`.
Exact repaired code: `0078f8b9987abd19ebbf48405f46c7a2ac94df5e`.
Reviewed: key_study.py, check_keys.py, test_key_study.py and the preparation note.

## Blocking finding and repair

At the initial commit, one-shot pair iterators silently erased all result rows;
empty iterators bypassed the nonempty check. The reviewer independently obtained
`evaluate(samples, iter(pairs), observations, seed) == []` for four declared
owned pairs, and `validate_plan(iter([]), iter([])) == {}`. This was a real
fail-closed inventory defect, not a scientific outcome.

The repaired validator rejects non-list/tuple inputs before truthiness or
iteration. The independent adversarial recheck confirms original erasure probes
now reject and tuple inventories retain four planned rows. All 11 owned C6 tests
passed independently in Windows and WSL. The reviewer independently checked
non-one-hot widened-float32 scalar cosine/projection, NFC public-owner SHA256,
integer XOR Hamming and packed dependence-group identity arithmetic. No model,
study pixels, GPU or scientific extraction was used.

Disposition: **no remaining blocker to this narrow software checkpoint**.

## Warning / unaccepted claims

`summarize` assumes direct in-memory evaluate rows. A future saved scientific
results reader must validate and bind each row to the frozen plan; the current
helper must not authenticate an arbitrary persisted result table by inference.
The preparation documentation records this warning as a remaining boundary.

Software arithmetic/inventory checks are supported by owned tests. Actual image
stability, semantic/instance hard-negative labels, extraction provenance,
collision rates, independent sample count, CI, scientific acceptance and compute
permission remain unsupported/unresolved. Required C6 scientific CSV/summary
are absent intentionally, not reconstructed from fixtures. #20 remains open.

Author broader checks: combined Windows39/35pass4skips and WSL39pass; scripts
185/174pass11skips. Expanded root discovery failed on existing Windows NumPy
imports and WSL Windows-only launcher/jsonschema constraints. Neither a full
discovery pass nor a dependency repair is claimed. All failures are retained in
the preparation note.

No reviewer source edits, C4 artifact changes, study execution, installs,
downloads, approval artifact or official lifecycle transition occurred.
