# B3 independent acquisition pre-launch review, 2026-09-26

Author/controller `/root`; independent read-focused reviewer `/root/b3_intake_review`. Exact reviewed commit `f91ca43b2e85c7004e27c9bdff954aeff1996d00`. Authority: AGENTS.md and `research/approval-policy.md` delegation. Actual user reply «دانلود کن» is recorded by the parent task, not invented by the reviewer.

Verdict: **no blocking technical finding for one bounded acquisition writer**, subject to that actual user authority. Scope accepted is acquisition/byte-integrity workflow only; not item-level rights, scientific execution, paid budget, final source IDs, B3 completion or Spec Kit transition.

Reviewer independently passed ten selection tests and strictly replayed the local pinned Parquet. Complete result equals committed production receipt: 6,219 groups, 14,000 rows, 7,206 score/size exclusions and three empty-text exclusions. Checked all fourteen candidate cardinalities before prefix acceptance and malformed text even in otherwise excluded rows. Authorization/proposal/selection working and Git-blob digests matched; production receipt SHA-256 `50e0df5e3935ba458cbaad96221c33590dd33cb04216ed2f866494e78fa6fb46`. The newline defect is resolved. `-ListOnly` independently admitted exactly fourteen pinned files totaling 8,493,745,129 final archive bytes.

Downloader review covered linked-path/contract/scope checks, exclusive parent lock, storage preflight, serial resume, checking existing full files and partial sizes, exact-size/full-SHA-256 finalization and preserving rather than overwriting wrong/oversized files. No extraction/scientific action occurs.

Operational warning retained: the lock belongs to parent PowerShell. If that process dies while curl survives, the lock may release before the child stops. Recovery must inspect **both parent PowerShell and curl writers**, existing partial bytes and logs before resuming; a persistent lock filename alone is not proof of active/inactive ownership. Reviewer made no file writes, downloads or external mutations.
