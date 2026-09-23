# SEAL targeted revision comparison

Inspected 2026-09-23 UTC by /root.
Earlier revision: https://arxiv.org/html/2503.12172v1 (2025-03-15).
Later revision: https://arxiv.org/html/2503.12172v4 (2026-05-18), previously inspected in seal-v4.md.

In v1 section 3.2, Algorithm 1 uses a secret salt; Algorithm 2 generates a proxy image, captions and embeds it, then generates from derived noise. Algorithm 3 performs inverse diffusion for detection. These core features therefore predate v4. This narrow comparison resolves the concern that the observed inversion pipeline was introduced only in the later revision.

Limits: not a full revision diff, parameter/result equivalence claim, or evidence that the proposal author read v1. The proposal's exact consulted revision remains unknown. Existing v4 card is unchanged; this supplemental comparison is not a second counted publication or a silent version merge. No empirical results verified. Local notes checksum identifies this record, not remote paper bytes.
