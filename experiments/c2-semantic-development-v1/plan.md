# C2 development-only feature probe

Status: prospective exploratory engineering experiment, not executed or approved.
Applies research/research-contract.md, research/scope-guard.md and A5 method-spec.
The design and compute-runner skills preserve exact-manifest review/approval; the
plan does not self-authorize a run or advance Spec Kit's paused plan gate.

Use only the original 32 development reservations (10 COCO, 10 DIV2K train,
12 DiffusionDB). Pinned B4 manifest/split/canonical digests are checked before a
model is loaded. Every external raw source byte and the existing local CLIP
checkpoint are verified again; no dataset discovery, download or new dependency.
No raw source/transform image or upstream prompt/user metadata is published.
All data remain local-only with disclosed rights/content/intake limitations.

All96 image/transform/pair cases are predeclared with pending status in the
exclusively created report before raw-byte preflight or model load. Every terminal
case gets an explicit completed/failed status and phase/error, fsynced append-only
progress journal, and atomic report checkpoint. A timeout/crash leaves pending
cases honest and retains completed work plus journal evidence; partial failures
cannot disappear or change the fixed pair order. Both report and progress journal
are declared hashed runner outputs. Configuration corruption can prevent trusted
inventory initialization; that is a failed launch with retained runner logs, not
an invented scientific case inventory.

Three cases per input: two uncached same-image extractions, fixed JPEG95
subsampling0 comparison, and the next sorted same-domain source as different
content. Planned 96 records are not 96 independent images. No threshold is fitted.
Record cosine distance, q Hamming distance, Ws digest Hamming distance, projection
margins, failures and model/config identity. Whole-digest distance is not semantic
similarity; the original code distance is reported separately. Different-content
pairing is fixed before features, including pairs with failed members.

The public projection seed is the all-zero 32-byte constant, not data-selected.
It is frozen before any study-image feature outcome, but after engineering
byte/dimension/color inspection. This is explicitly development/exploratory, not
retrospective confirmatory preregistration or evidence that all A5 claims hold.

Local RTX5070Ti/WSL, batch one, one existing pinned CLIP load. Estimated runtime
3–10 minutes, bounded at20 minutes; estimated peak RAM6GiB, Torch VRAM4GiB ceiling,
disk256MiB. These are estimates, not measured outcomes. The official runner must
check available GPU headroom; no RunPod, API, storage/egress spending or new
download is requested. A Linux timeout owns the worker process group and kills
at1160+10 seconds before the outer1200-second runner ceiling. Launcher uses fixed
argument arrays and a clean environment; offline socket connections fail.

The4GiB ceiling covers Torch allocator memory, not all GPU allocations. RAM/disk
are planning estimates, not OS-enforced caps; the duration and zero-paid-spending
boundaries are explicit. Any materially higher observed demand stops expansion
and is reported rather than silently broadening resources.

The existing 62-distribution WSL science environment remains unchanged. No new
package installation is part of this plan. Scientific execution still requires
the user's exact manifest/run/target approval through the official runner. The
implementation and launcher need independent review before asking for execution.
