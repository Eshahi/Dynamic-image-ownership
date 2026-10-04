# A: completed two-source enrollment pilots

Exploratory development evidence only. Sources 1675 and 4795 were declared; ten of the twelve reserved development sources were not enrolled here. Two completed routes on the same two sources are not four independent sources, and these results do not exhaust family A. No image was opened for this report; values come from retained JSON analysis and terminal run records.

Both routes optimized an unscaled terminal VAE latent from reconstruction step200, with 60 robust and40 joint steps. The image-DCT/CLIP verifier re-extracted suspect features; no diffusion inversion was used. `pure-decoder` emits VAE.decode(z). `hybrid-source-bypass` adds decoder displacement to the source image. The latter's source bypass is a material method amendment, not initial-noise generation.

| Route / source | Clean C1 PSNR / SSIM / LPIPS vs source | Semantic / instance content match | After VAE cycle PSNR / SSIM / LPIPS vs source | After-cycle semantic / instance |
| --- | --- | --- | --- | --- |
| Pure /1675 |31.214 /0.8915 /0.0718|yes /absent|28.623 /0.8637 /0.0875|yes /absent|
| Pure /4795 |28.231 /0.7166 /0.1788|yes /absent|27.318 /0.6932 /0.1928|yes /absent|
| Hybrid /1675 |38.629 /0.9852 /0.00762|yes /yes|26.606 /0.8113 /0.0571|yes /yes|
| Hybrid /4795 |38.255 /0.9829 /0.00920|yes /yes|25.067 /0.5862 /0.0905|yes /absent|

The clean hybrid images satisfy PSNR>35, SSIM>0.9 and LPIPS<0.1 on2/2; pure-decoder images satisfy the conjunction on0/2. The matched unmarked pure-decoder controls already have PSNR31.003/28.059 and SSIM0.8904/0.7113, while matched hybrid controls equal their source. This supports a source-fidelity limitation of this pure-decoder configuration, without proving a universal decoder ceiling. Hybrid clean C1 returns operational `authentic` on2/2; pure C1 returns `regenerated` on2/2 because its instance tier is absent. These labels describe channel/content states, not verified causal history.

After one saved-RGB8 VAE cycle, semantic content match remains2/2 for each route; instance match is0/2 pure and1/2 hybrid. Hybrid states are authentic for1675 and regenerated for4795. All cycled C1 images fail the source-quality conjunction. Across each route's source, matched and cycled unmarked controls, correct-owner false findings are0/6; wrong-owner findings are0/10 across its five cells ×two sources. These dependent descriptive controls do not establish population FPR. No actual diffusion-regeneration T3, copy-paste T4 or semantic-collision T5 result is supplied here. Human quality assessment remains missing; paired C1/C0 distortion was not recorded and is not inferred from source-quality values.

Optimization took224.016/222.921 seconds per pure source and222.844/221.593 seconds per hybrid source. Internal detector total times were210.253–391.146ms over all cells; these timers exclude the CLIP feature call performed before the detector and are not end-to-end lightweight latency. Final hybrid semantic/instance surrogate scores were8.860/8.493 and8.849/9.205; pure scores8.634/4.528 and7.959/3.490. Continuous surrogate values do not replace saved-image decisions.

## Retained launch inventory and provenance

All runs are under MAIN `.thesis-build/dev-runs/`. Failed launches were infrastructure failures before either source was attempted, not scientific negative results; both remain retained.

| Run directory | Commit | Outcome /duration | run.json SHA256 |
| --- | --- | --- | --- |
|20261003-2333-A-pure-pilot|d619addb032cbaca0879bb06b86b1370abe0e06b|failed /6.031s; missing CLIP path|908217b92feec5924eba0b8c5d521c6c1d8d47fe19e2c8bb20f37e91cdd88c31|
|20261003-2336-A-pure-pilot-retry|482d1dd9ab23068d5b10bca4a678e0173c59b1e0|failed /7.109s; module lookup `'a6_clip_visual'`|09f2c368addec60e527682b38b1d3fbb515caf5ee2259f87a199dbd362a045e1|
|20261003-2337-A-pure-pilot-retry2|92705c288b8bfb54def37016bae541a181e6b0fc|completed /467.485s|854a23ebc4eac433d6cfe213837ae24789deba82e4047445704962cc4eafcc2d|
|20261003-2347-A-hybrid-pilot|421787d14cfaceaa41c94141f517e1730da0390a|completed /466.016s|0e56178cbdf483ac790bef3c2b575ca9e072b3a4ca0f65a93a4a20f93848a677|

Analysis `20261003-2355-A-pilot-analysis` at commit `c4f722e5ae0512e872ebaef0bd4b71228ea95f29` is `completed_descriptive_analysis`; `run.json` SHA256 `e79451b3aba5303faa0d333597e6fc689346cac3554a1cad12d3852a9f946608`, `analysis.json` SHA256 `498ff42babb1469692e9678afd7bfad87d2ca92e411c6a3811360fa9b30501e6`. Its source manifests/journals/cohort hashes are retained in `run.json`. This report does not adopt an amendment, assert M1 acceptance or replace independent review.
