# C4 explicit residency pilot: retained memory failure

Actual direct user instruction to start the same pending local test approved
`c4-embedding-dev-002`, canonical manifest
`a43ccae7b11a857fd213b79f9eaf1707cc8388151d58f5338fbe48e8157ab052`,
clean executed commit `4db4f96453ddaba81ab5ec7b1978b354ed215066`,
1200 seconds/USD0/Torch8192MiB. Separate exact approval was serialized from that
actual message outside the checkout; official validate-approval passed. This is
not a human lifecycle verdict, remote budget or another attempt's authorization.
Approval is consumed; one execution, no retry.

Runner started 2026-09-26T21:41:32.775327Z, ended 21:42:36.940625Z, exit2/failed.
Worker terminal OutOfMemoryError elapsed 59.054950409 seconds. All45 input pins,
unchanged source109798/native500x333/pad512x384/seed0/config/model assets and
environment checks passed; model loading completed at56.612435293 seconds.
Original run001 failure remains preserved separately.

## Observed improvement, still insufficient

Idle transfer completed at57.231969705 seconds. Measured current Torch allocation
fell from5,541,969,408 to3,833,063,424 bytes: **1,708,905,984 bytes released from
allocated tensors**. Reserved bytes stayed5,639,241,728 across these boundaries;
do not describe allocation reduction as equal physical/free/reserved memory gain.
The module device/dtype/profile guards passed that transition; this does not
independently establish numerical transfer fidelity or safety parity.

Source VAE encoding and matched-control rendering completed. The optimization
iteration0 journal records both UNet forwards and scheduler steps completed,
then `vae_decode` started without completion. Its enclosing optimization-render
operation also remains unfinished. The error was **observed during that operation
boundary**; asynchronous CUDA errors prevent proving the precise faulty kernel.
No objective/backward/update/final measurement, PNG save or safety phase is
recorded. Zero recorded gradient/update observations is not a zero-valued gradient
or proof that all unrecorded internal progress was absent. Gradient remains null.

Peak allocated8,323,352,064 bytes (below approved8,589,934,592); reserved
8,545,894,400 bytes; peak worker RSS7,673,032,704 bytes. The allocation ceiling
was not the whole-system/GPU ceiling. Initial free VRAM11,561,598,976 bytes and
available RAM15,179,149,312 passed headroom checks. These results refute completion
of **this exact8GiB profile**, not prove the physical12GiB GPU cannot support a
different method-preserving memory implementation. Minimal successful VRAM and
backward-phase demand are unmeasured; do not infer an exact larger-GPU requirement.

## Retained provenance and analysis

Immutable run root: stable project's ignored
`.thesis-build/c4-runs/C4-development/c4-embedding-dev-002/`.
Runner record SHA256 `318124de7189a36dceb156699fe374cdac203b0c451b63459e05c007deaacb4b`.
Declared report/progress/launcher SHA256 respectively
`431a401cbebd4ad9928d78c90ef59d18fe950b0ed1d6f3c46422d557f2892011`,
`21e315bb148ecf0cef3f5599f5f45d2d700134522e353ff1786d01eeaab5da42`,
`5fe50a9f8eef231bd7e73f03aa936ce3eb765427fab7d26fa7f091e06c3b9489`.
35 trajectory rows and source/private model snapshot are retained locally,
without raw images/weights/prompts in Git.

Read-only `python -m scripts.summarize_c4_residency_failure` resolves45 inputs
against the executed Git blobs, with only the two exact-hash Windows requirements
CRLF reconstructions, checks declared output/source identity and ordered phases,
nested operation boundaries and absence of outputs. Exclusive analysis outputs
stay outside the checkout. Initial retained-residency-failure-v1 analysis SHA
`aefa21d478381f44251ecbf6a73318d044b10cd7950f690e3ae7cec8692e347b`
is preserved; later provenance hardening adds analyzer SHA/input-inventory/bool
context checks without changing observations. Official v1 helper already reports
expected1/observed1/failed1/missing0, gradient n0/all summary scalars null, no
CI/significance/superiority. Its generic few-seeds warning is not a population
power analysis for this engineering trial. Updated reviewed analysis provenance
will be recorded after independent review; never replace original run artifacts.

Owned parser/original-failure tests: 11 passed in Windows/WSL before additional
bool-context regression. No study rerun or new install/download. Loader warnings
about clip_text_model-versus-clip and torch_dtype deprecation remain in process
logs. Quality, q/h drift, blind verification and saved-pixel safety remain NOT_RUN.
#18/PR67 stay open/draft; this is not scientific method success or C4 closure.

## Next decision boundary

Do not repeat002 or raise the cap by inference. Ordinary inspection can assess
graph-memory/checkpointing alternatives preserving source, dtype and method.
A larger GPU is a plausible resource alternative, not yet an empirically proven
minimum. Any local cap/profile change or remote experiment needs a new reviewed
exact manifest/user approval. Paid RunPod setup/creation is not authorized here;
the current live provider also refuses creation until genuine bounded termination
is established. Do not bypass that safeguard with a manual/direct API run. Prepare
a supported environment/transport/deadline/budget package before asking the user
to create a billable Pod. Continue independent C6 software work while that branch
waits; its PR69 is already published, not a new scientific permission.
