# A6 deterministic base-noise and carrier byte vectors (model-free)

Issue [#7](https://github.com/Eshahi/Dynamic-image-ownership/issues/7),
2026-09-24 UTC. Status: **bounded CPU unit-test evidence, not a scientific
environment lock or experiment**. The source rule is
[`method-spec.md`](method-spec.md), which applies
[`research-contract.md`](research-contract.md) and
[`scope-guard.md`](scope-guard.md). No image, checkpoint, dataset, Stage-2
package, network model call or GPU method run was used.

`scripts/base_noise_reference.py` implements the specified `pack` rule (each
field prefixed by uint32 big-endian byte length), domain `a5-base-noise-v1`,
uint64 big-endian seed, raw 32-byte source SHA-256 digest and three uint32
big-endian latent dimensions. SHAKE256 output is consumed as pairs of uint64
big-endian words; `(x+0.5)/2^64` and Box-Muller yield two values per pair.
Values are rounded into little-endian float32 bytes in channel/row/column
order. This **reference** caps output at one million elements to keep ordinary
tests bounded. The cap is not a proposed research input-size limit.

Synthetic known-answer vector: seed `7`, source digest 32 zero bytes, shape
`C=1, h=2, w=3` produces six float32 values:

```text
(0.17093929648399353, 0.9753754734992981,
 -1.220534324645996, -0.574219286441803,
 0.6080271005630493, 0.3844108581542969)
```

The SHA-256 of the resulting 24 little-endian bytes is
`1180bb2e44603d3f0db122e8cd0024ec25762ab5df5ad36255df48ebae8a94cd`.
Tests also cover an odd element count, seed/source/shape separation and
invalid-input rejection. This frozen vector detects accidental byte-order,
field-framing or output-order changes; it does not prove a distributional
claim or end-to-end watermark behavior.

Verified from the A6 worktree with the `AGENTS.md` Python interpreter:

```powershell
& 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/venv/Scripts/python.exe' -m unittest discover -s scripts -p 'test_*.py' -q
```

Result: 41 tests discovered, 40 passed and one optional Torch test skipped because that CPU
workflow venv does not contain Torch. The already-authorized isolated Stage-1
science venv then ran only the four base-noise unit tests, including a separate
PyTorch `float64` CPU Box-Muller calculation rounded to float32:

```powershell
& 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/a6-science-venv/Scripts/python.exe' -m unittest discover -s scripts -p 'test_base_noise*.py' -v
```

Result: four passed. Each of the six Torch-versus-Python scalar differences
was at most `2e-6`; the test does not assert byte identity across math
libraries. The selected tolerance is a local smoke-test threshold, **not** a
validated production parity bound. Both implementations share the same
SHAKE256/word interpretation, so this comparison does not constitute an
independent cryptographic or cross-runtime audit. A6 still needs the actual
component implementations, full dependency lock, model/weight receipts,
larger representative shape checks, numerical-drift policy and local/remote
environment receipts before scientific execution. The official plan gate and
compute approval are unchanged.

## Separate semantic/instance carrier vector

The same standard-library module now covers the `a5-carrier-v1` stream from
`method-spec.md`: length-prefixed domain; one ASCII component byte `s` or `i`;
raw 32-byte public-derived signature; uint64 big-endian per-image seed; uint32
big-endian C/h/w; and raw 32-byte detector configuration ID. It consumes
SHAKE256 bits **low-to-high within each byte** in channel/row/column order;
zero maps to `-1/sqrt(C*h*w)`, one to positive. The output is rounded to
little-endian float32 bytes. Its float32 norm may differ slightly from exact
one. The one-million-element cap is again only a reference-test bound.

Synthetic known-answer input: component `s`, signature hex `01` repeated 32
times, seed `7`, shape `C=2,h=2,w=3`, detector config ID hex `ab` repeated 32
times. The 12 output signs, with positive represented by `1`, are
`000100110011`; each magnitude rounds to `0.28867512941360474` in float32.
SHA-256 of the 48 output bytes is
`39c035801126715dbc0cd021b60ff6406b2ae6254cf6d140be099415a90ecb32`.
Tests check component, signature, seed, shape and config-ID separation as
well as malformed-input rejection; they do not claim collision resistance
from these few synthetic cases or test a real watermark. This carrier never
enters the blind detector as an oracle source key.

After this addition, the complete workflow-venv script suite discovered 44
tests, with 43 passing and the one expected Torch skip. The isolated Stage-1
science venv passed all three targeted `test_carrier_reference.py` tests.
No Stage-2 package, checkpoint, dataset or scientific compute was used.
