# Stage transport is not unique causal attribution

Author supplement, 2026-10-25, outside the completed WP6/E3 independent-review scope. Original algebra only; no experiment or computation ran. This note adds no measurement, intervention, hypothesis or protocol amendment. [07-final-experiment.md](../07-final-experiment.md) and H1–H6 remain controlling.

## What the retained contrasts identify

[04-mechanism.md](../04-mechanism.md) records F5 semantic C on 55/60 sources after each foreign autoencoder round trip, versus 0/60 under full SDXL regeneration and 5/60 under full Kandinsky 3 regeneration. These observations contradict universal destruction by those complete round-trip programs. They do not locate the additional loss uniquely in an encoder, reverse denoiser or decoder: historical paths also differ in posterior, numeric convention, noising and trajectory. C additionally combines reading with content binding. The round trip itself measures encoder-plus-decoder-plus-reader behavior, not an isolated encoder.

The future compatible-path contrasts specified in [mechanism-server-spec.md](mechanism-server-spec.md) have narrower computational interpretations: adding the specified reverse program at fixed inputs/draws, or changing the posterior convention under shared downstream noise. They are pipeline-specific contrasts, not an intervention on independent training, and do not provide a universal causal decomposition. Their measurements remain unperformed.

## A valid product, and its coordinate boundary

For a fixed clean trajectory and declared smooth surrogate, write the differential chain as

\[
v=RDFE\delta,
\]

where E is the input-encoder derivative, F includes noising and reverse transport, D is decoder/output transport, and R is reader/chip transport. Intermediate Jacobians are evaluated at their respective native states. The main forecast instead starts with the exact finite encoder displacement d and uses downstream transport of a*d; these are distinct constructions ([theory-design.md](theory-design.md), [finite-transport-boundary.md](finite-transport-boundary.md)).

For propagated nonzero directions h_i=A_i h_(i-1), define g_i=||h_i||/||h_(i-1)||. Then

\[
\prod_i g_i=\frac{\|v\|}{\|\delta\|}.
\]

This telescoping identity is valid directional transport, not a product of independent retention probabilities. A zero intermediate direction makes subsequent ratios undefined; compute the full product directly. Multiplying operator norms instead supplies only an upper bound, generally not equality. Neither norm expression determines signed reader alignment or compound C.

For invertible latent coordinate changes S,T, replace

\[
E'=SE,\quad F'=TFS^{-1},\quad D'=DT^{-1}.
\]

The observable derivative remains R D' F' E'=RDFE. Individual factor ranks are invariant, but Euclidean norms and singular values generally change. In one dimension, E=1,F=1/2,D=R=1 yields output gain 1/2. Taking S=c,T=c gives gains c,1/2,1/c; taking S=1,T=c gives 1,c/2,1/c. Thus a small reported encoder or denoiser gain can arise solely from units. These are reexpressions of one pipeline, not different physical models. Noise covariances must transform too: under S, (d,Sigma) becomes (Sd,S Sigma S^T), preserving nonsingular Mahalanobis separation. Keeping isotropic noise unchanged after a nonorthogonal rescaling changes the experiment.

Native coordinate conventions fix useful reproducible measurements; this invariance argument does not invalidate them. It prevents treating their magnitudes as coordinate-free causal shares. [conditional-information-bound.md](conditional-information-bound.md) likewise requires explicit latent units and side information.

## Ordered allocation is a convention

Even exact scalar systems exhibit interactions. Let output Y(e,d)=de for input one, with baseline (e,d)=(1,1) and comparison (2,3). The total difference is 5. Replacing the encoder first gives

\[
[Y(2,1)-Y(1,1)]+[Y(2,3)-Y(2,1)]=1+4;
\]

replacing the decoder first gives 2+3, assigning decoder 2 and encoder 3. Both telescope exactly. Neither is the unique allocation of the difference: the interaction (2−1)(3−1)=2 is assigned to whichever component changes second. Explicitly defined, compatible interventions can have well-defined conditional effects; ordering alone does not identify independent contributions. The native computational order does uniquely define its tangent propagation, but does not turn stage gains into causal percentages. Actual finite endpoint differences further include the remainder and numeric discrepancies already described in the finite-transport note.

## Why swapping components does not repair identification

Consider E_A(x)=(x,0) and D_A(z)=z_1+k z_2. Every k gives the same native round trip D_A E_A(x)=x. Another encoder E_B(x)=(0,x), with native decoder D_B(z)=z_2, also reconstructs x exactly. Yet the swapped output D_A E_B(x)=kx is arbitrary despite identical observed native behavior in both pipelines. Native observations constrain the decoder on its supported inputs, not this off-support extension. Equal latent dimensions do not establish compatible coordinates, distributions or training support. The algebra is a counterexample, not a proposed experiment.

Future stage measurements can therefore describe where a specified perturbation contracts, rotates or disappears along a specified native computation, and test full-chain prediction. They require privileged clean sources, marked inputs, target-model internals, explicit noise and C0 trajectories; they are not an operational lightweight detector. No such transport has been measured here. Even successful forecasting would establish neither encoder-training independence as the cause nor unique encoder/denoiser/decoder responsibility.
