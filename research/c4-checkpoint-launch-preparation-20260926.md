# New003 package preparation; no scientific execution

The user requested execution before the final new003 manifest existed. That is
not serialized as exact-manifest compute approval. Existing001/002 approvals
remain consumed. The design helper and official runner preview initially passed
commit952f3910bd6fb4b52318831a56da70216b0e32a0 / canonical9fe598a6…c4d1, but
that intermediate package must NEVER execute after subsequent source repairs.

Root's read-only inspection of installed Diffusers0.35.1 DDIMScheduler.add_noise
found a concrete prelaunch defect: its first call assigns alphas_cumprod to the
original sample device. Freezing a CPU scheduler buffer before a CUDA call would
reject this expected migration. No failed model/scientific trial occurred.
Checkpoint constructor now performs the identical device-only normalization to
the detached condition device before freezing the profile, preserving values and
dtype. An owned LazyBuffer proxy returns a new tensor identity to exercise the
ordering even on CPU; ordinary output/gradient/trajectory parity tests remain.
Actual GPU scheduler arithmetic/replay parity remains unmeasured.

New design/source changes are opt-in new003 only. The local loader accepts an
explicit bool, returns exact checkpoint class/profile and worker checks both;
config hash804cb5e28e4c3ef39e81a6aae99d4c4fdbc2d4842467a076ba69a40968960653
plus checkpoint code are mandatory inputs. Old run001/002 recipes reject. Typed
C1 receipt binds the new experiment. Original specs/runs/snapshots are unchanged.

Observed metadata only: all62 installed versions and Python3.14.4 matched;
nvidia-smi free10768/12227MiB, MemAvailable15303396KiB. Transient availability is
not fit proof and must be rechecked by the worker at execution. C4 tests before
scheduler repair:80, Windows64pass16expectedskips, WSL75pass5expectedskips;
scripts186175pass11skips. Final repaired counts/review/binding recorded separately.

No model/study/GPU kernels, scientific run, new downloads/install/paid provider,
cap/precision/source substitution, retries or lifecycle state changes occurred.
Next: repaired exact code/package review, final clean commit-bound manifest after
documentation, independent final binding, then present its exact hash for user
approval. Only official runner may execute an approved package once.
