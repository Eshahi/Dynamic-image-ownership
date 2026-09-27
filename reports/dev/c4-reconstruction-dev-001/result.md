# C4 three-arm preservation localization: retained development source

Issue #18 / draft PR #67. Exploratory, one source, seed0; no watermark/optimizer,
blind detection, population comparison or improved-method acceptance.

## Actual authority and execution

The actual authenticated user replied `من تایید میکنم.` immediately after the
assistant stated that the earlier scientific execution question remained pending.
That sole pending request was the reviewed three-arm localization package, not
the newer five-arm library. The author restated this narrow scope before execution
and serialized that actual reply in the external approval artifact. No human gate
verdict or blanket scientific permission was invented.

Official runner approval validation returned true. Actual independent reviewer
`/root/b3_intake_review` verified the dedicated clean checkout, all42 input hashes
and working/Git equivalents, in-memory builder and helper manifest/spec; no remaining
final execution-binding blocker. Then exactly one official runner execution:

- Experiment `c4-reconstruction-localization-development-v1`, run
  `c4-reconstruction-dev-001`, target local, USD0,1200s outer ceiling.
- Clean execution commit `36b4fa85942d744b7c1749947b675da784215d3a` in the isolated
  c4-localization-exec checkout. Newer author code was not substituted.
- Complete canonical manifest SHA256
  `065979dd13b7a6665c149d96baf8c9eceb7c06882321b99b15cf6445412337da`.
- Approval canonical reference
  `b18f8f79d501c89baf55662ad7be3c223ef839ea4714d26758c77cc9b7018204`;
  issued2026-09-27T11:08:00Z, expires12:08:00Z, actor user. This one-run approval
  is now **consumed**, not permission for a retry or new five-arm experiment.
- Started11:08:57.416346Z, ended11:10:00.677203Z; official status completed,
  exit0, errors empty. Worker elapsed59.819923346s; all9 render/safety/LPIPS cells
  completed,67 durable worker journal rows,6 declared output digests verified.
- Existing retained source109798, native500x333, local research only. No new
  dataset/model bytes, held-out images, RunPod or other paid service used.

## Complete unaggregated source-reference outcomes

The three arms share one encoded source and are dependent measurements, not N=3.
Strict unchanged targets are PSNR>35dB,SSIM>0.9,LPIPS<0.1.

| Fixed arm | RGB MSE | PSNR dB | SSIM | AlexNet LPIPS v0.1 | All three targets |
| --- | ---: | ---: | ---: | ---: | --- |
| VAE-only | 0.0056457428439589145 | 22.48278907271824 | 0.7429099151683972 | 0.058493178337812424 | Fail; LPIPS alone passes |
| Zero-initial-noise DDIM | 0.00719192869147502 | 21.431546273166017 | 0.6935376799565754 | 0.1362507939338684 | Fail all three |
| Unchanged fixed-base-noise DDIM | 0.009128101388585818 | 20.39619544722751 | 0.6679027647010946 | 0.11984674632549286 | Fail all three |

All saved-arm safety flags were false under the pinned checker. This is a model
flag observation, not a general safety or rights certificate. Unchanged fixed-base
control canonical pixel digest AND PNG byte digest match retained run003 exactly;
no silently altered reference or approximate replay was accepted.

## Supported interpretation and negative evidence

The planned hypothesis that VAE-only satisfies all source-quality targets is
contradicted in this source. Preservation loss is already observed in the fixed
VAE-only route without DDIM; zero noise does not repair it. This localizes loss
to at least the shared encode/decode route but does not identify VAE compression
as the unique cause separately from normalization/padding/crop/model profile.
The LPIPS ordering also differs from the zero-noise PSNR ordering; do not declare
one noise setting a general winner from this single case.

Source-conditioned inversion/replay targeting the same unrefined encoded latent
does not by itself supply evidence that the observed VAE-only source-quality gap
will disappear. A source-conditioned latent-refinement candidate through the
frozen decoder is a justified next design to investigate, with fixed objectives,
failure accounting and unchanged diffusion latent/noise embedding/detector scope;
it is **not implemented or executed by this run**, nor guaranteed to achieve targets.
No post-result parameter search, fullmethod substitution, source-assisted detector
or threshold change is authorized by the consumed localization approval.

No confidence interval, significance test, independent-seed aggregate or effect
size is reported. The generic paired-seed analysis helper is intentionally not
used to invent an aggregate over these dependent arms: the inspected design calls
for all source comparisons individually. This bounded transcription retains every
declared result and no exclusions; broader claims remain unsupported. Previous
embedding001/002 OOMs, embedding003 and saved-pair001 negative evidence remain intact.

## Resources, environment and scope limits

The model-free environment/software evidence and scientific worker evidence are
separate. Windows official runner3.12.14 dispatched the hash-bound launcher;
actual worker WSL CPython3.14.4 matched all62 pinned distributions, Torch2.12.1+cu130,
TorchVision0.27.1+cu130, Diffusers0.35.1 and Transformers4.57.6. Reviewed network
blocking/offline flags and deterministic fp32 profile remained active.

Torch allocation ceiling9,663,676,416 bytes (9GiB), not whole GPU/system memory.
Initial freeVRAM11,561,598,976 bytes, availableRAM15,190,454,272 bytes and
free disk206,797,955,072 bytes met fixed headroom checks. Peak Torch allocation
5,545,542,144 bytes (5.164688587GiB), reserved8,180,989,952 bytes (7.619140625GiB),
worker RSS8,169,795,584 bytes (7.608715057GiB). No OOM in this diagnostic. This is
not a full watermark-gradient/native2K workload fit, but no paid GPU is needed
to explain this particular completed run's quality failure. More VRAM alone
does not change the measured reconstruction outputs.

Model-runtime numerical parity and original publisher attestation remain unproved;
the loader retains its pinned-unaffiliated-mirror custody label. Source attribution/
rights limits remain, and raw PNGs are not redistributed in Git. C4 remains open,
C5 dependent; no scientific method success or official lifecycle transition.

## Retained provenance and reproducibility

Stable ignored root:
`W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/c4-runs/C4-localization-development/c4-reconstruction-dev-001/`.
Approval outside execution checkout:
`.thesis-build/c4-localization-package-20260927/user-approval-20260927.json` in stable project.

| Artifact | Actual file SHA256 |
| --- | --- |
| manifest.json | 38469352133167ecb2b36e94702e9c309c95d134d0f6d545ad001e8cd0a8124a |
| execution-manifest.json | 54c09dad87a80ca7c29d3cde95cf614a4c14175d3002ffadcd28e5ff2b4429ca |
| outputs/localization.json | b5d02f511e2da0a1931a1dfadb3053ca4e9f913a30762cf0dc4694d29fdcccf1 |
| logs/localization-progress.jsonl | b7a6f135f8c21ea123a9a670b3b89c3f97118eb86bd49b8692e64692ffe53031 |
| logs/localization-launcher.jsonl | 73d5370aca195e332fb22c3fc5b43975a2287dff24f96a65870dff47c3188a42 |
| outputs/vae_only.png | 7dd86185dd695193f81ad250f346edf72be6ecaada155fb3afa07a259b11be67 |
| outputs/ddim_zero_noise.png | 0e929c1cb3a442284ddd9ff8e26708e463c2fef6b089073135ba6db70b1842ab |
| outputs/ddim_fixed_base_noise.png | 53aceddd708642bb26c9fbd5393670282d7feb813cfab0aece824305a0b71d2c |
| external approval JSON | 2ccb9b1ed9fd60b529250b89f0a99fbdddf78a2648e5e7b07e5dcc72fb225dce |

File SHA values differ from canonical-object manifest/approval digests because
the official runner formats JSON; they are not interchangeable. Recheck declared
files with the installed official `dispatch_experiment.py collect` against retained
execution-manifest.json and source/out set to this same artifact root (read-only
hash verification, no model rerun). The author rechecked all6 SHA values and each
reported PSNR equals `-10*log10(mse_rgb01)` to1e-10. Original launcher/worker/config/
spec/design are available at the exact execution commit; report numbers are not
new metric computations on images.

Administrative check failures before execution: author initially looked for the
compute wrapper in project scripts (not installed there), then used the actual
installed skill wrapper. An unescaped alternation in a WSL pgrep command was
misinterpreted by the shell; corrected literal python inventory found no live
worker. No scientific execution occurred in either failed diagnostic. Only the
single official --execute dispatch above consumed this approval. No retry.

Actual independent `/root/b3_intake_review` reviewed exact report16c283c, verified
retained custody/time/approval/42pins/6outputs/62distributions/67journalrows/9cells,
all15 SD snapshot hashes, exact prior-control bytes and resource/metric transcription;
no narrow evidence/transcription blocker remained. No image/model/metric rerun was
performed. See audits/c4-localization-results-review-20260927/review.md for scope
and unverified claims; this is not thesis-wide or scientific method acceptance.
