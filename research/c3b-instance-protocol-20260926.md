# C3b instance signature and common-q fusion

Implements issue#17 / source method-2 under research/method-spec.md,
research/research-contract.md and research/scope-guard.md. C2#16 actually closed
with PR#65 merge `ef9d483ccbdb3607ca9c678ac331e832992d452a`; its one exact approved
development run is consumed and has not been repeated. No method/seed/threshold
change is made in response to C2's three JPEG drifts or two collisions.

`src/signatures/instance.py` accepts immutable, already-canonical native RGB8
bytes, width/height at least32 and withinuint32, no file discovery or decoder.
Its pinned arithmetic profile is
`a5-phash32-rgb8-f32-channels-f64-bilinear-fsum-dct-v1`: eachbyte/255 rounds once
to IEEEbinary32 as required by the A5 pixel interface, then widens to binary64;
Y uses0.299R+0.587G+0.114B without gamma linearization. Fixed32x32 pixel-center
bilinear resampling clamps neighbor coordinates. Separable orthonormal DCT-II
uses Pythonmathcos/mathsqrt and fsum, horizontal before vertical. The median uses
all63 top-left8x8 AC values; the first32 positions ordered(u+v,u,v) use strict>
comparison, little-bit-first packing. Coefficients, median and selected minimum
margin remain inspectable. True constant RGB has analytic zeroAC and all-zero
code; differently colored constants are an explicit known collision.

This specifies numerical behavior, not empirical invariance. The earlier B2
scalar reference computes binary64 weighted bytes/255 rather than the A5
binary32-channel snapshot. It is not asserted bit-equivalent near ties. The C3b
test independently constructs binary32-channel luminance, pixel-center samples
and direct full2D DCT on an owned non-square fixture, checking every coefficient
and packed code. Platform trig libraries can still affect near-median signs;
runtime/code identities and owned-vector parity are required before scientific
use. This does not certify every image or a future vectorized implementation.

Wi reuses the reviewed C3a exact domain-separated pack/SHA256/NFC rules.
Changing h under fixed q/owner leaves Ws unchanged but changes Wi in the supplied
tests; changing owner affects both. `bind_canonical_image` uses supplied C2 q,
not an implicit CLIP extraction; callers must verify/bind its image origin and
the full C1 static config. No secret-key or authenticated ownership mode exists.

`fuse_candidates` validates one owner's complete13semantic/429instance score
inventory for the already-fixed radius-one q/h search. Missing/extra/duplicate/
nonfinite candidates are errors, not negative matches. Ordering is original
code then low-to-high single-bit flips, independent of caller ordering; tied
maxima retain the first candidate. Supplied thresholds/version/config digest
are explicit labels, not evidence of calibration. Strictscore>threshold and
zero-variance veto apply. `both_match` requires the **same q** for semantic and
instance hits. Cross-q component hits remain two flags plus `cross_q_only`, not
an invented joint match or forgery diagnosis. Full C5 DetectionResult labeling,
DCT extraction, validation calibration and multi-owner any-of-K evaluation are
not claimed implemented by this one-owner fusion primitive.

Declared `reports/dev/instance-examples.json` contains owned synthetic arithmetic/
byte-protocol examples and supplied-score controls, clearly labeled **not a
scientific study run**. It is not a replacement for future measured pHash or
marked-image stability. No study image, model, held-out set, new package/download,
GPU, paid compute or RunPod is used. This CPU task's acceptance is implementation,
shape safety, domain separation and deterministic correct/wrong/changed-input
controls after independent review, not experimental efficacy. Any new scientific
execution still needs its own exact-manifest user approval.

Ordinary commands (verified Windows workflow interpreter):

```powershell
& 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/venv/Scripts/python.exe' -m unittest tests.test_instance
& 'W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/venv/Scripts/python.exe' scripts/instance_protocol_examples.py --output '<unused-owned-protocol-report>.json'
```

Nine focused tests pass in WindowsPython3.12.14 and WSLPython3.14.4. The owned
37x43 fixture yields pHash`1cbe0da9`, changed43x37 fixture`1cbf0ac5`, both constants
`00000000`, identically on both platforms; their Ws/Wi byte fields and complete
supplied-score fusion reports match. **Full floating reports are not equal**:
the first selected margin is0.005912209101639299 on Windows versus
0.005912209101639327 on WSL; the second0.0026520015416608145 versus
0.0026520015416609047. Near-tie universal pHash parity is not established.
The initial whole-example equality check failed honestly; inspection isolated
these margin differences without changing arithmetic, tests or output bytes.
A PowerShell diagnostic syntax error was repaired without source/artifact changes.
Both initial reports remain: committed Windows report and stableignored
`.thesis-build/c3b-owned-protocol-wsl-20260926.json`. The chosen known-answer byte
assertions freeze these owned fixtures, not a study-selected projection seed.
Full185script tests174pass11expectedskips; focused owner/semantic/C2/instance
Windows37tests33pass4expectedskips. No new scientific result is asserted.

Independent technical review and GitHub acceptance are pending. The official
Spec Kit controller remains paused atplan-acceptance with nullchoice; no human
or lifecycle verdict is fabricated and existing evidence remains immutable.
