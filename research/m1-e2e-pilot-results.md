# Fresh original200 + A-C100 pilot

Exploratory two-source development gate completed2026-10-04. The original fixed pilot passed; this triggers the ten remaining fixed development sources and their common threat assessment, not M1 completion or held-out authorization.

MAIN `.thesis-build/dev-runs/20261004-1102-e2e-1675` and `20261004-1122-e2e-4795` ran681.672 and681.313 seconds, respectively. Each used a fresh deterministic original200 initializer, followed by fresh independent100-update embedding Adam and saved-PNG blind readout. Sources/config/initializer full states, residual stages, quality cap, saved-image hashes and continuous score algebra were independently checked by `m1_terminal_e2e.merge_pilot`. Recorded CLIP and LPIPS observations were checked for consistency but not re-inferred by this CPU audit.

The merged receipt is MAIN `.thesis-build/dev-runs/20261004-1134-e2e-pilot-analysis/run.json`, SHA256 `286558cf970a8a317fb3d5de40a429b6389f065dee82c1fbd9b5de9c72ca7c0c`. All8 conditions and32 owner queries completed; both clean quality conjunctions, both clean dual matches, both VAE semantic matches and all28 negative queries passed the frozen gate.

| Source | Clean PSNR | SSIM | LPIPS | Clean semantic / instance | VAE semantic / instance |
|---|---:|---:|---:|---|---|
|1675|36.387705|0.980183|0.010275|5.899147 /7.326778|5.725767 /6.402508|
|4795|36.394559|0.977687|0.012986|5.869005 /7.429226|5.878863 /4.809296|

Both VAE outputs also return dual matches, although only semantic retention was the VAE promotion condition. Their source-referenced quality does not meet the clean image-quality conjunction; codec retention is not a claim of imperceptible regeneration. Human visual verdicts remain missing. Two development sources cannot establish population detection or false-positive bounds, and no diffusion outcome has been inferred.

## Descriptive legacy-initializer component contrast

Compare the identical source/arm/dose rows with MAIN `20261004-1021-terminal-deterministic`, whose old initializer made it component-only evidence. Every new C1 PNG differs from that component run. New minus old score differences are:

| Source/dose | Semantic delta | Instance delta | PSNR delta |
|---|---:|---:|---:|
|1675 clean|0.009388|-0.034225|0.005843|
|1675 VAE|-0.017096|0.058933|0.002023|
|4795 clean|-0.027324|0.044487|-0.009886|
|4795 VAE|-0.031241|0.059233|0.001770|

These are paired recorded differences, not a tolerance-based equivalence claim or a test of superiority. Unmarked canonical C0 source identity is unchanged. Initializer differences and missing new initializer LPIPS remain documented in `m1-e2e-initializer-observations.md`. The complete original200+100 path is used for every subsequent source; no retained legacy initializer substitutes for it.
