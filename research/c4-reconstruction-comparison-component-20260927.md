# C4 shared-source reconstruction comparison component

Issue #18 / PR #67; ordinary implementation, **not a scientific execution package**.
Apply research-contract.md, scope-guard.md and the actual reconstruction-path
amendment. The owned CPU fixture's numerical policy values are software-test inputs,
not selected experiment parameters or evidence of improvement on the retained source.
No new model, scientific worker, manifest or user approval is generated here.

## Fixed composition

`src/embedding/reconstruction_comparison.py` shares one source encode and exactly
five ordered arms: VAE-only, unchanged zero-initial-noise DDIM ablation, unchanged
fixed-base-noise DDIM control, fixed-point inversion/replay, and safeguarded
coordinate inversion/replay with an explicit L2 effective-transition prior.
No carrier, watermark optimization, candidate search, new source or held-out image.
The existing SD1.5 fp32/empty-condition scheduler and VAE scaling/pad/crop/native-grid
interfaces remain. Returned metadata explicitly says PNG/safety/quality and blind
detection are not performed; passing a latent residual does not establish source
PSNR/SSIM/LPIPS or watermark success.

The prior extension to inversion_path.py uses each current inverse boundary target:
`r=alpha/alpha_previous`, `beta_effective=1-r`, `mu=sqrt(r)*target`, prior term
`weight*L2(x-mu)/beta_effective`. Each per-pair beta/mean scale/profile is journaled.
This uses the Gaussian-transition structure discussed in the inspected
[GNRI v5](https://arxiv.org/html/2312.12540v5), but replaces the dense one-step
transition with the **effective skipped DDIM pair**. The norm choice, safeguards,
stopping and candidate conditioning still differ; this is GNRI-inspired, not a
verified author implementation or transferable paper performance. The zero-beta
degenerate profile is refused before prediction. Positive prior weight is explicit;
static means cannot be mixed with this mode; a nonneutral static-beta policy is
refused rather than silently ignored. Weight/iteration/tolerances must be frozen
and justified in the next exact scientific configuration, not chosen from outputs.

## Failure, custody and resources

Both inversion candidates must pass their whole latent replay tolerance before a
decoded image is produced. A normally nonconverged arm persists its intermediate
states/failed metadata and produces **no** fallback decoded image. The next listed
independent arm may still run so a reference failure is not used to suppress another
declared outcome. This is not an undocumented retry or best-of-many selection.
Exceptions (model/profile/journal/persistence/nonfinite/time limit) stop the component;
earlier saves remain intact and later outcomes remain absent, never marked complete.

UNet and VAE identities/mutation versions/eval/dtype/device are guarded. VAE scaling
is checked; original module/tensor references remain alive across callbacks. Native
outputs and metadata passed to callbacks are isolated copies, and successful state
persistence is required before arm-saved records. The component retains metadata
only, not all generated GPU images. Caller must durably save partial latents/PNG
and file hashes and preserve incomplete reports. The existing accidental-drift
guard's private `_version`, raw-storage/method-tamper and weight-authentication
limitations still apply; loader/manifests are not replaced.

The exact concrete loader profiles `DiffusersComponents` and
`CheckpointedComponents` are accepted; arbitrary subclasses are refused. The
path delegates prediction through the bound backend `_predict` function, preserving
the already-reviewed nonreentrant activation checkpoint profile instead of making
direct UNet calls that silently discard it. Changing that function after binding
is refused. This is software compatibility, not measured learned-model parity.

Per-inverse-arm mathematical NFE ceiling includes forward replay, with separate backward counts.
Checkpoint backward recomputation is additional model work, not free NFE. A temporary
root-UNet forward pre-hook journals all forward starts and counts backward-context
recomputations separately. Actual starts are capped at twice the declared NFE
ceiling, refusing before an additional root call; the hook is removed on success
and on model/journal/persistence failure. A start record is not a completed-forward
claim. Normal results include both counts; exceptions retain incremental journal
evidence and do not invent a terminal count or completed arm. These root-call counts
do not measure internal module operations or FLOPs. The checkpoint profile's tensor
guards and the external runner resource limits still apply.

Legacy control predictor count is its fixed suffix length, VAE-only zero scheduler
calls. This is operation accounting, not a FLOP/time/memory equivalence. The component
cooperative whole-comparison duration may be at most1100 seconds to permit a future
20-minute worker to reserve load/safety/metrics time; it cannot stop a stuck call.
External runner timeout, measured free resources and Torch allocation guard remain
mandatory. No actual VRAM fit, additional allocation permission or RunPod need follows.

## Next complete package, not another tiny approval

Integrate this comparison once into a reviewed real-asset worker with versioned
parameter rationale, exact source/model/config/code/environment hashes, durable
cell and file inventory, old-control pixel replay, native saved-PNG source metrics,
actual safety and q/h diagnostics if declared. Retain nonconverged, flagged, failed
and interrupted arms and full negative/OOM history. Then finalize the exact manifest,
design-helper/official-runner preview and independent binding before one necessary
actual user compute question. Do not execute this library with pretrained models
merely because ordinary fake CPU tests pass. The old three-arm exact localization
question stays pending and unchanged; no duplicate prompt, consumed approval reuse
or execution from a newer mismatched checkout. C4 remains open; C5 dependent.
