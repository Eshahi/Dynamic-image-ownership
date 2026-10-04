# Phase residual diagnostic results (exploratory)

Retained run `20261004-0030-phase-residual` at `eca1a533a852d988b213ca47ab24f94dcda5b1f0` completed32/32 conditions in35.657s; source run JSON SHA256 `08c97137492d9807ee4ae4962eef689bb0098f21eccd0036cef1d29e96a12615`. Analysis `20261004-0031-phase-residual-analysis` SHA256 `b646ed9b7cc56802640ac82df134f7c049293704df75ff984eb93daf69d4f8a0` is complete descriptive analysis, not method acceptance. Two development sources1675/4795, four correlated owner queries per condition; no human verdict.

|Arm/profile|Clean correct matches (1675/4795)|VAE correct matches|Clean quality pass|Clean/VAE carrier gates|
|---|---|---|---|---|
|APM/full|126/127|124/126|0/2|True/True|
|APM/quality-cap|79/93|89/93|2/2|False/True|
|IPS/full|116/116|112/112|0/2|True/True|
|IPS/quality-cap|89/99|90/90|2/2|True/True|

|Source|Arm/profile|Lambda|Clean PSNR|SSIM|LPIPS|
|---:|---|---:|---:|---:|---:|
|1675|APM/full|1.000000000|25.658906|0.876752|0.110434|
|1675|APM/quality-cap|0.328313776|35.200004|0.980847|0.016240|
|1675|IPS/full|1.000000000|27.934838|0.907745|0.074046|
|1675|IPS/quality-cap|0.427460414|35.200012|0.979244|0.016822|
|4795|APM/full|1.000000000|26.623470|0.843175|0.136444|
|4795|APM/quality-cap|0.371006206|35.200007|0.969573|0.027194|
|4795|IPS/full|1.000000000|28.702192|0.878508|0.097388|
|4795|IPS/quality-cap|0.471749898|35.200001|0.965494|0.027796|

All C0 roster and marked wrong-owner queries are below82/128 in every arm/profile/dose. Reused C0 receipts and repeated queries are not independent samples or a population FPR estimate. The full residual profiles retain carriers but fail clean source quality0/2; the capped APM profile loses clean presence on one source. Frozen IPS/quality-cap meets both quality and clean/VAE carrier screens2/2 here. This licenses the prespecified remaining-ten development expansion in m1-phasemark-pilot-decision.md, without retuning the payload, blocks, threshold or cap.

The composition explicitly uses source pixels: phase-latent-residual-source-bypass. It is not pure latent decoding. Detector uses suspect RGB8, public128-bit owner payload, fixed IPS mask and pinned VAE; zero UNet but one VAE encoder. No CLIP+pHash content binding, T3 diffusion robustness, T4/T5 separation or three-state ownership result is established. VAE is a deterministic codec cycle, not diffusion regeneration. Historical pure-decoder negative quality remains retained. Neither these two sources nor a successful subsequent expansion constitutes family exhaustion or confirmatory evidence.

Verified raw JSON conditions agree with analysis counts; all controls inspected as recorded numeric metadata. No PNG, tensor or model was opened for this report.
