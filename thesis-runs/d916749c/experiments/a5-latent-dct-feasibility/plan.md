# A4 draft for A5-dependent latent-to-DCT feasibility

Status: **BLOCKED DESIGN DRAFT**. This is neither a completed preregistration nor execution approval.

The supported prospective question is whether the proposal-faithful latent/noise path can create an image-domain 8x8-DCT signal that the core detector can recompute for an existing image and claimed public OwnerID, while separating marked outputs from the declared controls. The draft preserves the proposal's semantic-plus-perceptual signature, existing-image route, latent/noise embedding and inversion-free image-DCT detector. It does not substitute image-space embedding, inversion or a neural decoder into the proposed method.

The machine-readable draft is `experiment-spec.yaml`. It fixes the falsifiability and negative-result boundaries that are already supported. It deliberately leaves datasets, seeds, score equation, threshold/FPR, practical margin, sample size and comparator revisions unresolved because the corresponding artifacts do not exist.

Before this can become a preregistration, A5 must supply the reviewed end-to-end algorithm and final config schema, including the stable key recomputation and Pattern -> Noise/Latent -> Image -> DCT bridge. A4 must then freeze endpoints, independent units, margins, uncertainty, multiplicity, sample sizes and stop rules. Dataset release identities, licenses, item IDs, splits and deduplication must be recorded without reducing the proposal commitments by inference.

No scientific execution, data acquisition, paid service, GPU purchase or external mutation is authorized by this package.
