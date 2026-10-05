# e -- 2025-2026 literature: transferable mechanisms for F5

Scope: F5 r2 pinned SD1.5 VAE encoder, DCT band 4-32, 320 chips, PSNR 52 dB, 7-view soft binding (32-bit q). Stress grid 12x{.4,.5,.6}x5 seeds, CFG1 20 DDIM: .4 49/58, .5 37/58, .6 10/57. Remaining .4/.5 binding, .6 carrier. Papers opened 2026-10-05 as cards in research/literature/; primary sources only, at least abstract+method inspected. Card files: fu2025-diffusion-adversary.md, lu2025-vine.md, optmark2025.md, freqmark-2410.20824.md, seal-2503.12172.md, shallow-diffuse-2410.21088.md, vae-diffusion-attackers-2025.md, zhao-regeneration-2306.01953.md.

At most 3 transferable mechanisms. Each states derivation, expected quantitative gain on stress grid, cheapest decisive test (CPU or <=15 min GPU), and kill criterion. Threat scope T3/T4/T5 only; T4 0/20, T5 0/66 must stay, clean LPIPS mean <=.0173 max <=.050.

---

## E1 -- Blur-surrogate augmentation inside PGD (from VINE, Lu et al. 2025)

Source: Lu-Shilin et al., VINE (arXiv:2410.18775, ICLR 2025) -- SDXL-Turbo one-step encoder, distortion layer uses Gaussian/motion blur as cheap surrogate for diffusion editing because blur and regeneration share low-frequency distortion profile. Trained end-to-end with surrogates; best-of-class on W-Bench yet still falls at high strength (Fu 2025: VINE-R 100%->24.5% unguided->1.6% guided). Card lu2025-vine.md.

Derivation for F5. F5 PGD maximizes margin via VAE encoder J_E only. Regeneration applies Denoise(Noisy(E(x+delta))). Optimizing only J_E ignores J_Denoise. VINE insight ports as: augment PGD objective with J_{Blur o E} where Blur is differentiable Gaussian (sigma=1.0-2.0 px, kernel 9x9) applied to RGB before encoding. Blur J is low-pass, so J_{Blur o E} penalizes high-frequency PGD components the denoiser erases, steering delta toward frequencies the denoiser preserves. Effective L*Delta/sigma in Zhao Thm 4.3 becomes L_eff*Delta/sigma where L_eff=||P*J_E|| with P ~ blur transfer H(f).

Expected gain. Bridging ~30-50% of VAE-only to full-regeneration gap. F5 already spends ~37s/image on 150 VAE steps; Blur adds one convolution per step (~5% cost). Header: H1 per-chip variance 0.12-0.35 was 1.1 dB detector-side; embed-side shaping via surrogate could add 1.5-2.5 dB. Stress: .4 +1-3 (49->50-52/58), .5 +2-4 (37->39-41/58), .6 +1-3 (10->11-13/57). Stacks with binding fixes (A-P2/C-2), orthogonal.

Cheapest decisive test (<=10 min GPU). 4 sources x2 strengths (.4,.5) x2 conditions (plain PGD vs Blur-PGD, sigma=1.5 px before encode, same L2 52 dB, same 150 steps) =16 embeddings ~10 min GPU. Add Blur as F.conv2d(x, gaussian_kernel) differentiable. Measure post-attack chip SNR and semantic rescue. Also CPU re-read sanity on H(f) vs H1 a_i.

Kill criterion. Post-attack SNR gain <0.5 dB at .4 or paired T3 delta<=0 at .5 (n=20) or any LPIPS regression >5% at equal PSNR or visible blur-ring on 147498. Also kill if T4 donor copy leakage >0/20.

T4/T5 risk. Low. Blur is public, key-independent; donor copy still donor-pixel-specific.

---

## E2 -- Dual-locus / structure-vs-detail split (from OptMark, 2025; echoes VINE frequency insight)

Source: OptMark (arXiv:2508.21727, 2025-08-29) -- inference-time optimized multi-bit watermark via adjoint gradients, dual watermark (structural early-denoising latents + detail late latents), adjoint memory O(N)->O(1). Also VINE frequency analysis (edit ~ blur). Cards optmark2025.md, lu2025-vine.md.

Derivation for F5. F5 320 chips uniform over DCT ring radius 4-32 with weight (r/4)^1. OptMark ports as unequal error protection across frequency: reserve k_s~80 chips in low sub-band (r=4-12, structure, survives Noisy->Denoise best) with higher margin target m_s=5.0, and k_d=240 chips in high sub-band (r=12-32, detail) with m_d=3.0, or dual-decoder OR: detection succeeds if either locus exceeds threshold. Low-band a_s~0.7 vs high-band a_d~0.35 at .4 (lower DCT radii survive better), so partitioning isolates reliable signal.

Expected gain. .4 +2-3 (49->51-52), .5 +3-5 (37->40-42), .6 +2-4 (10->12-14). Stacks with UEP over |p_j|.

Cheapest decisive test (CPU + <=10 min GPU). CPU: split H1 probe chips into low/high by radius and simulate weighted OR detector on stored stress images. If CPU predicts <+2 at .5, kill without GPU. If promising: re-embed 4 sources with split layout at PSNR 52, 5 seeds .4/.5.

Kill criterion. CPU OR-rescue <+2 at .5 at joint FPR=1e-6 or required per-locus FPR >5e-7 or no low-band a_s advantage (<1 dB over uniform) or LPIPS low-freq blotches.

T4/T5 risk. Low-medium. Joint FPR via OR thresholding; T4 structure copy not pixel-aligned so <1/20.

---

## E3 -- Guidance-aware bound: decoder-in-the-loop ceiling (from Fu et al. 2025)

Source: Fu-Wenkai et al. (arXiv:2511.05598) -- formal I(x_w;m)->0 under diffusion regeneration as strength/steps grows, via unguided vs guided (decoder-steered) attacks. Even VINE-R collapses 24.5%->1.6% with guidance while preserving quality. Card fu2025-diffusion-adversary.md. Complements Zhao 2306.01953 Thm 4.3.

Transfer -- negative result / ceiling. No watermark survives beyond strength threshold if decoder guides denoising by steering away from decoding region. For F5 threat (unguided T3, pinned SD1.5 img2img), unguided numbers are correct comparator (12-24% survival for prior SOTA at medium-high strength, consistent with F5 18-36% at .6). Once s exceeds s* where sigma(s)/L*Delta > Phi^{-1}(1-e1), TPR->chance. Using F5 measured L*Delta~15.9*B at 52 dB, sigma(.6)~1.8*sigma(.4), predicts s*~0.6-0.7 where .6 10/57 matches theory.

Implication. No carrier-geometry variant wt equal PSNR whose .6 exceeds bound+10 pts should be claimed without larger Delta or full denoise trajectory (H2, >=2x cost, T4 risk). Justifies hard stop at .5 knee (as in f5-plateau-20261005) and focus on .4/.5 binding.

Cheapest decisive test (CPU, 0 GPU). Compute L*Delta/sigma curve from probe: L*Delta from 52 dB encoder gain (15.9), sigma(s) from H1 a(s): a .05->1.0, .4->0.57, .5->0.42 est, .6->0.28 est. Plot predicted TPR(s)=Phi(Phi^{-1}(1-FPR)-L*Delta/sigma(s)) vs observed counts. If theory TPR(.6) <25% and observed ~18%, calibrated. Flag any .6 claim >10 pts above bound.

Kill criterion. Kill any B1-B3/D2 variant at equal PSNR whose .6 claim exceeds f(e1) bound+10 pts, or whose .6 gain costs >2x GPU without approaching bound. Declare .6 a limitation.

T4/T5 risk. None -- theory-only.
