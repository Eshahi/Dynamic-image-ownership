# Native projection: decoder-input precision

Precision clarification `ac-native-projection-precision-v1`, 2026-10-04, by gpt-6-astra/xhigh, frozen before the first native-projection threat outputs. This resolves step4 of [m1-terminal-continuous-expansion-design](m1-terminal-continuous-expansion-design.md) for attack `ac-native-projection-v1`. It changes no threshold, projection coefficient, quality cap, source/pair inventory or measured outcome. No GPU experiment was performed for this decision.

**Unscale in CPU float64, then cast the unscaled decoder input once to FP16.** Apply exactly the same operation to projected `z_star` and recipient-reference `z_B`. Do not cast the scaled latent to FP16 before division.

The observed primary scaled latents have already undergone the production reader's FP16 arithmetic. Convert their saved values exactly to CPU float64 for the analytic projection. With the existing float64 coefficients and templates, compute `z_star=z_B+a_s*w_s+a_i*w_i` unchanged. For each `z` in `{z_star,z_B}`, the normative conversion is:

```python
s = np.float64(0.18215)
z64 = np.asarray(z, dtype=np.float64)  # finite, flat C-order16384
u64 = np.divide(z64, s)              # actual division, not reciprocal multiply
u16 = u64.astype(np.float16)        # NumPy round-to-nearest/ties-to-even
# Validate finite values; reshape to (1,4,64,64) without reordering.
# Transfer this already-FP16 tensor to the pinned FP16 VAE.
# VAE.decode receives u16 directly, without another scale division.
```

Pin the NumPy/runtime version and verify the configured VAE scaling factor equals the expected0.18215. There is no FP32 intermediate, autocast conversion, latent clipping, renormalization or stochastic rounding. Preserve shape/dtype and actual FP16 decoder-input bytes in the receipt. A nonfinite float64 value, overflow on half conversion or mismatched scale is a failed condition, not permission to clip or change precision.

This order is faithful to the declared mathematical `decode(z_star/.18215)`: the CPU float64 projected latent is unscaled before crossing the model's dtype boundary. Casting `z_star` first would insert an additional quantization before division, including rounding of the scaled projected displacement, and can yield a different half input. It has no privileged status merely because the production VAE-cycle operator uses half arithmetic. The native projection is its own explicitly specified attack; it is not a reproduction of that VAE cycle. No comparison of attack outcomes or detector scores selects this order.

Decode both half inputs with the same pinned FP16 VAE and existing decoded-RGB clipping/operator. Continue the specified paired decoded residual, source bypass and36-iteration35.2dB quality-only cap unchanged. Do not replace the reference decode by an old RGB reconstruction produced using another conversion order. This clarification concerns the latent-to-decoder boundary; it does not amend the primary reader's scaling or the deterministic VAE threat channel.

## Conversion-error receipt

Retain `z_star`, `z_B`, each float64 `u64`, and each actual `u16` or their hash-bound arrays. For each input define the float64 diagnostics using exactly these operations:

- Unscaled error: `du = u16.astype(np.float64) - u64`.
- Represented scaled latent: `z_tilde = s * u16.astype(np.float64)`.
- Scaled error: `dz = z_tilde - z64`.

For `du` and `dz`, report L2, RMS and maximum absolute error; relative L2 uses respectively `norm(u64)` and `norm(z64)`, with null when the reference norm is zero. Do not add an arbitrary epsilon. These errors describe the actual decoder-input conversion; `z_tilde` is an evaluator representation, not a new FP16 readout or a guarantee about the decoded/re-encoded image.

For each donor channel `j`, retain the existing float64 preconversion projection residual `dot(z_star,w_j)-dot(z_A,w_j)`. Additionally record:

`postcast_absolute_residual_j = dot(z_tilde_star,w_j)-dot(z_A,w_j)`

`postcast_displacement_residual_j = dot(z_tilde_star-z_tilde_B,w_j)-a_j`.

The second includes conversion of both the projected and reference decode inputs. Neither postcast residual is forced back to zero: there is no correction iteration, threshold targeting or attack-success selection. Subsequent decoder and saved-image reader losses remain measured downstream, separately from this conversion diagnostic.

Use a nested `projection_precision` receipt with these exact fields:

```text
version: "ac-native-projection-precision-v1"
operation: "cpu_float64_divide_then_float16"
scale_float64: 0.18215
decoder_shape: [1,4,64,64]
inputs:
  projected | reference:
    scaled_latent: {path, sha256}          # existing z_star or z_B array
    unscaled_float64: {path, sha256}       # u64, flat C-order16384
    decoder_input_float16: {path, sha256}  # u16, flat C-order16384
    unscaled_conversion_error: {l2, rms, max_abs, relative_l2}
    scaled_conversion_error: {l2, rms, max_abs, relative_l2}
projection_residuals:
  s | i: {precast, postcast_absolute, postcast_displacement}
```

Here `projected | reference` and `s | i` denote two separate required dictionary entries, not literal combined keys. Existing hash-verified scaled-latent arrays may be referenced without duplication. The enclosing attack receipt already binds donor `z_A`, templates and input images. The saved half array is reshaped only for decoder invocation; its dtype and flattened bytes must equal the tensor actually submitted. An analyzer can reproduce the division, cast, errors and residuals on CPU from these receipts without new model calls.

Before execution, a bounded CPU test must compare the conversion helper to the explicit NumPy expression on fixed finite normal/subnormal values, zero and signed values; retain a fixed fixture demonstrating that the rejected cast-first/half-division order can differ. Test shape/C-order preservation, scale mismatch and overflow rejection, and direct arithmetic of both error/projection-residual definitions. These are numerical-contract tests, not evidence that either order is stronger. Record this document's hash with the attack implementation before its first run; do not edit retained outputs or retrofit a previously executed attack's provenance.
