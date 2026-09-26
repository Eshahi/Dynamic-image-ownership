# Independent review: retained C4 run002 failure

Actual delegated actor: `/root/b3_intake_review`, distinct from author `/root`.
Reviewed analysis commit: `3a949dae9ef5e9779ec54bdf062fac15693c9aac`.
Executed scientific commit: `4db4f96453ddaba81ab5ec7b1978b354ed215066`.
Canonical manifest: `a43ccae7b11a857fd213b79f9eaf1707cc8388151d58f5338fbe48e8157ab052`.

The reviewer independently checked the genuine approval's run/time/budget binding,
45 historical input pins, three declared output digests, retained source identity,
and all 35 trajectory rows. Its in-memory analysis exactly matched retained-v2
SHA256 `058dffe1054b06e8847911fa4251e2fa7bc4122eb5a35c729c565b1c19f63f7c`.
Eleven owned tests passed independently on Windows and WSL.

No blocking discrepancy was found in the actual evidence: matched-control render
completed; iteration-0 optimization render and VAE decode remained unfinished;
allocated tensors reduced by 1,708,905,984 bytes while reserved memory was unchanged
at those boundaries; OutOfMemoryError occurred at 59.054950409 worker seconds;
no gradient/update/PNG was recorded, and gradient remains null.

Nonblocking warning: the journal parser accepts balanced unknown operations or
deletion of some balanced operations. The actual hash-pinned ledger was inspected
and is correct. Do not claim a generic complete-operation-inventory validation
from parser checks alone; harden it before future reuse or qualify that claim.
The result documentation now explicitly qualifies it.

Accepted scope is honest retained-failure provenance only. This is not C4
completion, successful numerical memory-transfer parity, minimum GPU capacity,
human lifecycle approval, retry permission or paid RunPod authorization. No models,
pixels, GPU, scientific rerun, downloads or evidence changes were made by reviewer.
