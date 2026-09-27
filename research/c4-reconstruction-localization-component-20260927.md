# Prospective C4 reconstruction localization component

Issue #18 remains open after the reviewed saved-triplet negative quality result.
This software preparation applies research-contract.md, scope-guard.md and A5;
it does not change the proposed embedding path, thresholds, source commitments,
or detector knowledge profile. No new scientific run is authorized or performed.

The retained control/source and candidate/source both failed all quality targets.
That does not distinguish VAE roundtrip loss, DDIM/noise effects or other route
details. The prospective component records three fixed diagnostic arms on one
shared encoded source: VAE-only decoding, fixed DDIM suffix with zero initial
noise, and unchanged DDIM suffix with fixed base noise. None includes signatures,
optimization or a candidate watermark. Zero noise is not an identity operation:
the existing scheduler still scales the source latent at its initial timestep.

`src/embedding/reconstruction.py` has no CLI, loaders, discovery or network.
It enforces the existing native-grid replicate-pad64/crop rule, fp32 finite
fixed input/output profile, one source encoding, fixed arm order and explicit
failure propagation. Cloned latent/noise inputs isolate normal callback mutation
between arms; this is not a sandbox against malicious Python closures. Progress
has started/completed boundaries; a failed arm is not retried or substituted.
Future worker must retain earlier completed outputs on a later failure.

`DiffusersComponents.decode_encoded` is a diagnostic-only public wrapper over
the existing virtual `_decode` path, preserving VAE scale and checkpoint subclass
dispatch. The default proposed reconstruction/optimization path is unchanged.
This helper is not an approved alternative main method and may not be selected
post hoc as a replacement candidate to obtain favorable quality.

Author verification: five synthetic fake-backend CPU tests in the existing pinned
WSL environment, no learned models, GPU or study pixels. Tests cover fixed order,
native shape, immutable caller data, mutation isolation, invalid profiles,
no fallback/later-arm execution after failure, journal callback failure and the
VAE scale/virtual-decoder wrapper. No new dependency or installation.

Remaining before any scientific execution: reviewed exploratory design with
source/config/environment/weight pins; fully enumerated worker/launcher/resource
and safety policy; PNG roundtrip and all source-reference quality metrics; prior
control byte replay criterion; durable partial/failure evidence; final clean
manifest and actual exact user decision through the official runner. No source
discovery, strength search, scheduler modification, held-out data or more model
downloads are inferred. Do not reuse consumed embedding003/saved-pair001 approval.

Even future one-source arm differences would describe this fixed route, not prove
general VAE causality, robustness, watermark survival or scientific success.
Independent narrow software review is required; no C4 acceptance is claimed.
