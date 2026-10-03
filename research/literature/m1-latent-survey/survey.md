# M1 latent watermark survey (2026-10-03)

Seven primary full texts were locally downloaded and inspected in method and experiment sections. Cards distinguish reported evidence from local reproduction. The strict literature response validates and synthesizes without warnings. No held-out data were accessed. Bibliographic DOIs remain null rather than guessed; versioned canonical URLs identify the inspected sources.

## Design implications (agent inference)

Every surveyed initial-noise or intermediate-state method reconstructs diffusion latents using the diffusion model. None demonstrates extraction of its initial-noise signature by image-domain DCT alone. A Fourier ring in initial noise is not an image Fourier ring: nonlinear denoising and VAE decoding intervene. Proposal acceptance must therefore measure a lightweight decoder directly; robust inversion baselines do not establish that claim.

Gaussian Shading is the smallest feasible published latent baseline for pinned local SD1.5: sample independent half-normal magnitudes with signs supplied by encrypted, tiled payload bits, then generate with the existing pipeline. Its official MIT codec, run script and inversion implementation were inspected at commit `09c678fadc7545acf7be12647ddf2a5e66f6a9dc`; artifact checksums are in download-records.md. Main paper tests SD1.4 rather than SD1.5, so an SD1.5 result is an explicit adaptation. Native current diffusers inversion should be verified against the model prediction type and scheduler configuration. Fifty inverse U-Net evaluations are material detector cost and must be reported.

PRC is a distinct, stronger coding family; it uses exact DPM inversion and distinguishes detection from message decoding. Its statistical false-positive theorem conditions on key-independent images and random key generation, and its finite experimental parameters do not establish the asymptotic cryptographic guarantees. WIND uses an initial-noise identity bank, giving excellent published regeneration correlation but requiring substantial side information. RingID shows why high binary presence detection cannot establish multi-owner identification. ROBIN offers partial inversion at the expense of optimized hiding prompts and watermark preparation.

The newer Gaussian Shannon preprint combines LDPC and repetition. It supports a three-outcome architecture: exact decoded message, verification without reliable decoding, and failure. It does not prove that LDPC parity acceptance authenticates ownership: an attacker can construct valid codewords, so an authenticated payload or registered signed record is still necessary.

## Threat alignment

T3 must distinguish image-to-image strength, training noise timestep, repeated regeneration count, latent sign flip rate, and VAE compression. In particular, Gaussian Shading's reported flip-rate 0.4 does not support survival of local img2img strength 0.4. Published tables mix ROC-AUC, bit accuracy, exact decode and nearest-key identification; preserve these distinctions.

T4 requires transplantation tests with a different host image; the surveyed ordinary crop/drop transformations are not a copy-paste attribution test. T5 requires semantically similar wrong-content negatives, owner changes and forged payloads. Public OwnerID and public CLIP/DCT descriptors are reproducible identifiers rather than authentication secrets. Content registration/signature verification must be separated from mark-presence detection. Gaussian Shading explicitly documents a prompt-change framing attack, making content binding an experimental requirement.

## Prioritized development comparison

1. Native Gaussian Shading on four synthetic prompt generations: clean, VAE, local SD1.5 img2img sweep; score native inverted-latent bits and original-reference paired quality.
2. Measure the same images with lightweight image-DCT extraction, preserving failures rather than treating native inversion as proof of lightweight success.
3. Use coded repetition/PRC or an intermediate-state decoder as substantially different follow-up designs when the proposed decoder fails; amend the method explicitly if inversion becomes necessary.

Download inventory totals approximately 2.6MB of primary HTML and MIT source. The search was targeted and incomplete; this survey makes no claim that an unsearched architecture cannot exist.
