# L1 decoder-tangent screen results

Exploratory local study at `019031ada4d2a869dc02e559c061354be6297776`. The fixed L1 construction fails its clean exact-message screen; neither source supplies a qualifying latent-arm image. L-arm T3 was not executed.

| Source | Arm | Fraction | Strict quality | Clean exact q | SD1.5 VAE exact q | SDXL VAE exact q |
|---|---|---:|---:|---:|---:|---:|
| 1675 | L | 0.25 | 1 | 0 | 0 | 0 |
| 1675 | L | 0.5 | 1 | 0 | 0 | 0 |
| 1675 | L | 0.75 | 1 | 0 | 0 | 0 |
| 1675 | L | 1.0 | 1 | 0 | 0 | 0 |
| 1675 | P | 0.25 | 1 | 0 | 0 | 0 |
| 1675 | P | 0.5 | 1 | 0 | 1 | 0 |
| 1675 | P | 0.75 | 1 | 1 | 1 | 0 |
| 1675 | P | 1.0 | 1 | 1 | 1 | 1 |
| 468505 | L | 0.25 | 1 | 0 | 0 | 0 |
| 468505 | L | 0.5 | 1 | 0 | 0 | 0 |
| 468505 | L | 0.75 | 1 | 0 | 0 | 0 |
| 468505 | L | 1.0 | 1 | 0 | 0 | 0 |
| 468505 | P | 0.25 | 1 | 0 | 1 | 1 |
| 468505 | P | 0.5 | 1 | 1 | 0 | 0 |
| 468505 | P | 0.75 | 1 | 1 | 1 | 1 |
| 468505 | P | 1.0 | 0 | 1 | 1 | 1 |

Exact q requires readable original intended bits, semantic found and content match. The two sources and four fractions per arm are repeated development measurements, not sixteen independent images.

| Arm | Strength | Completed / planned | Exact checked q | Semantic found + content |
|---|---:|---:|---:|---:|
| L | 0.1 | 0/6 | 0 | 0 |
| L | 0.2 | 0/6 | 0 | 0 |
| P | 0.1 | 6/6 | 4 | 6 |
| P | 0.2 | 6/6 | 1 | 6 |

The L-arm zero completed counts mean not selected, not twelve measured regeneration failures. P is a descriptive pixel control and cannot rescue L.

Observed negative detections: 0/18 C0 calls and 0/60 wrong-owner calls. These calls reuse two sources; no population rare-event bound follows.

Original duration 107.438 s; total with technical completion 130.407 s, USD 0. The original twelve strength-.1 calls failed before generation due to an imported whitelist omitting .1. Their original errors remain retained; the completion changes no image, fraction, target, threshold or selection.

This stops one fixed direction construction, not every terminal-latent method, and adds no independent design family. Native suspect-image DCT replaces the VAE watermark reader, while seven-view CLIP remains. There is no instance payload, full dual-tier candidate, cryptographic authorization, held-out result or new M1a passage.

Source: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\dev-runs\20261010-1309-latent-tangent`.
Completion: `W:\Prrojects\image ownership\THESIS_GUIDE_OFFLINE_v5\.thesis-build\dev-runs\20261010-1321-l1-t3-completion`.
