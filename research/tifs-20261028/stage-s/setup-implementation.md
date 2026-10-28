# Deferred Stage S Linux setup

Implemented for future separately authorized Linux server use. Nothing here was
installed, downloaded or executed as setup on the laptop. Readiness remains
locked until the root's final review release. Setup does not imply permission
to rent an instance, run science or accept gated model terms.

The server operator supplies the 36 original canonical PNGs at
`ASSETS/sources/SOURCE_ID.png`. Setup verifies their frozen PNG SHA-256 values
before installing or downloading anything; it never downloads, resizes,
reencodes or substitutes sources. Runtime still verifies RGB8 hashes when it
loads them. Paths under ASSETS must have no symlink components.

Future command, following authorization and readiness release:

```bash
bash scripts/tifs_stage_s_setup.sh /workspace/assets /workspace/venv ACTUAL_INSTANCE_START_UTC
```

`TIFS_BOOTSTRAP_PYTHON` defaults to `python3`; the bootstrap creates or reuses
`VENV/bin/python`. Exact direct package pins are copied from retained
`stage2b-config.json`, including torch 2.7.1+cu128 and torchvision 0.22.1+cu128
from the CUDA 12.8 wheel index and CLIP commit
d05afc436d78f1c48dc0dbf8e5980a9d471f35f6. Setup verifies installed direct pins
and CLIP's direct_url commit, runs pip check, and records all installed package
versions without importing any scientific package. Transitive dependencies are
recorded, rather than falsely described as entirely hash-locked.

The selected asset plan preserves every retained file record under sdxl/, a6/,
vine/, wam/ and kandinsky3/ exactly: 48,597,702,199 bytes. TrustMark and VideoSeal
assets and source preparation are excluded. URLs retain pinned revisions;
licenses, file sizes and SHA-256 values are unchanged. An existing matching file
is reused after size/hash verification; mismatches fail. Partial downloads are
never appended blindly; only a completed matching partial is promoted. The
TIFS-specific `tifs-stage-s-download-ledger.json` records verified reuse,
downloads and setup failures. HTTP 401/403 stops without accepting terms,
obtaining credentials or bypassing gated access. This reuses the reviewed public
assets; it adds no approval file or license-acceptance automation.

WAM uses its verified pinned source.zip, expanded with prefix, traversal,
symlink, special-file, duplicate-path and total-size checks. Existing extracted
files must match archive bytes. VINE must remain at commit
d72f11a93f8de9bc45ef61202b9c8dda2a70cc77. Existing changes outside the two
inspected local-path patch files fail; those files must contain the exact
original or expected patch. Only `encoder_transfer_assets.patch_vine` is reused,
with bounded git-show calls. Its broader prepare function is never invoked.

The absolute rental start is required. Setup shares the 15-hour instance clock
with rehearsal, screen, idle time and retrieval. Subprocesses use the remaining
deadline, run in their own process groups, and their entire group is killed on
timeout. Downloads check time before every bounded read; an additional 30-second
network guard preserves the full one-hour retrieval reserve. Exhausted time
writes RESOURCE_STOP-setup.json and exits 3; a retained stop prevents automatic
retry. Setup failure removes any stale setup-ready receipt. Success writes
`tifs-stage-s-setup-ready.json` with source hashes, package versions, input
identities and remaining time. Setup never starts rehearsal or a screen.

Validation: seven pure-stdlib tests pass using MAIN's allowed Python with `-I`:
path traversal, exact asset filtering, requirements pins, hash/size mismatch,
absolute deadline, unavailable canonical sources and existing-file mismatch.
Both Python files pass py_compile. The shell wrapper was reviewed statically;
no bash invocation was attempted because the local Windows launcher previously
hung. Actual install availability, network throughput, disk capacity and server
science remain unmeasured and may cause an intact resource stop.
