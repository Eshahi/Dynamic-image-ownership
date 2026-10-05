# F5 Encoder and Denoiser Geometry -- Survivable Latent Directions

Scope: Exploit J_enc and score-function geometry to increase post-regeneration chip correlation at fixed PSNR 52 dB. Current F5: DCT ring radius 4-32 on 64x64x4 latent, 3272 slots / 320 chips, 150-step PGD through J_enc achieves 20-27x gain vs decoder rendering. Stress grid (12x3x5, CFG1, 20 DDIM): .4: 49/58, .5: 37/58, .6: 10/57. H1: a~0.57 at .4, corr 0.79, optimal a/v weighting +1.1 dB only, band 8-28 no gain. At .6 carrier loss dominates. Encoder fp32 pinned runwayml/stable-diffusion-v1-5 VAE. Zhao Thm 4.3 depends on local Lipschitz L.

Regeneration map: R(x)=D(Phi(E(x))) where Phi is encode->noising->denoise->decode, readout z_prime=E(R(x+dx)). Survival of chip w governed by ||P_w J_cycle dz||/||dz|| with J_cycle=J_enc*J_Phi*J_dec. Minimizing L_w maximizes certifiable radius.

---

## 1. Joint Encoder-Top / Denoiser-Null Subspace PGD (SVD-Guided Allocation)

### Geometric argument

J_enc in R^(16384 x 786432) is not an isometry. Its spectrum is heavy-tailed: top ~200 singular vectors capture >80% Frobenius energy. Random-pixel PGD wastes budget on low-sigma directions.

Let J_enc = U Sigma V^T. For any dx, ||dz||^2 = sum sigma_i^2 <v_i,dx>^2. Gain 20-27x already exploits this vs naive J_dec-rendering, but ell_inf PGD does not explicitly confine dz to span(U_1:k).

Survival requires J_Phi w ~= w. J_Phi = I + int ds_theta/dz dt along PF-ODE; eigenvectors with lambda~=0 preserved, lambda<<0 contracted. Desired w in Null(ds_theta/dz) intersect span(U_1:k).

Intersection non-empty because J_enc top directions are spatially correlated textures which diffusion treats as signal.

### Expected latent displacement

Baseline: ||dz|| ~= g*||dx|| with g~=23. Confining to top-k: g_k ~= 1.4--1.8x g (sigma_1/sigma_median ~=8--12; k~=512 of 16384). Filtering by ||J_Phi w||>0.7 retains ~30-50% of subspace.

Net: ||dz_surviving|| ~= (0.35--0.50)*1.6*g*||dx|| post-Phi vs baseline ~=0.57*g*||dx|| (a=0.57 at .4). Predicted a_prime 0.60-0.72 at .4, chip SNR +0.5 to +2.0 dB at .4/.5. At .6 intersection shrinks: +0.2 to +0.8 dB.

### Translation to stress grid

Empirical slope: +1 dB ~= +3-4 passes at .4/.5, +1-2 at .6.

- .4: 49/58 -> 52-55/58 (+3 to +6)
- .5: 37/58 -> 40-44/58 (+3 to +7)
- .6: 10/57 -> 11-13/57 (+1 to +3)

No PSNR cost if k constraint replaces implicit PGD bias.

### Cheapest decisive test (<=15 min GPU)

1. Encoder SVD probe (5 min, VAE only, no UNet): Power-iteration/Lanczos via jvp/vjp to estimate top 64 singular vectors of J_enc at 1 image. Compute Rayleigh quotient and V^T dx of current F5 dx* -- fraction outside top-512. If >60% already inside, headroom small.
2. Denoiser survival filter (10 min, SD1.5 UNet): Inject eps*U_i at t~=0.4T and 0.6T, single img2img DDIM 20-step Phi (CFG1), measure <U_i, Phi(z+eps U_i)-Phi(z)>/eps. Rank by survival. Jaccard >0.25 confirms exploitable intersection.

Total: one 4090, <15 min.

### Kill criterion

- Kill if F5 dx* already >=70% energy in top-512 V AND top-sigma survival not >1.3x median. Headroom <1 dB.
- Kill if survival at t=0.6 for all top-sigma <0.3. Joint subspace empty at .6.

### T4/T5 risk

- T4 (crop/edit/inpaint): MODERATE-HIGH. Top singular vectors are global textures (large receptive field); concentrating there reduces spatial redundancy. Must retain tiled structure; do not collapse to <8 tiles.
- T5 (purification): LOW. Nullspace of s_theta is what purifier preserves. Risk only if purifier uses different VAE.
---

## 2. UNet Spectral Transfer Profiling and Band Reshaping

### Geometric argument

H1 showed radial band 8-28 gave no gain, but radial averaging masks anisotropy. UNet Jacobian is approximately diagonal in Fourier basis with transfer H(f,theta,t) = d Phi_hat(f)/d z_hat(f). Diffusion training makes H~=1 for signal frequencies, H<<1 for noise frequencies.

Current DCT ring treats all angles and radii 4-32 equally. H(f,theta,t) is not isotropic: SD1.5 UNet preserves H/V mid-frequencies more than diagonal high-frequencies. Per-chip attenuation a_i correlates with rho_i (0.79) because chips on high-H frequencies survive.

Formally a(f)=|H(f,t0)|*|G_enc(f)| where G_enc is encoder frequency response. Maximizing a(f) under pixel budget is water-filling: allocate chip power where a(f) maximal.

### Expected latent displacement

Literature (Dieleman 2024, Kingma 2023) suggests H varies 6-10 dB across orientations at fixed radius, 8-12 dB across radii at fixed t. Top quartile of (f,theta) bins yields E[a^2] gain +1.5 to +3 dB over uniform ring. Incremental chip SNR at .4/.5: +1.0 to +2.5 dB (conservative, PGD already partially water-fills).

At .6, cutoff f_c(t) moves inward (f_c propto 1/sqrt(t)). Bins at 20-32 fall beyond f_c(0.6) irrecoverably. Reshaping to 4-18 at .6 recovers +1.5 to +2.0 dB vs uniform 4-32.

### Translation to stress grid

- .4: 52-56/58 (+3 to +7) if angle-selective; radial-only ~+1 dB
- .5: 41-46/58 (+4 to +9) -- largest headroom
- .6: 13-18/57 (+3 to +8) -- only mechanism with meaningful .6 lift

### Cheapest decisive test (<=15 min GPU)

Single-tone transfer sweep (no PGD, no dataset). For 1-2 images, for each DCT basis vector e_{f,theta} in 4-32 ring (subsample 48 log-spaced bins):

  z = E(x); z_pert = z + eps*e; // eps=chip RMS ~0.015
  z_out = Phi(z_pert; t) - Phi(z; t) // 20 DDIM, CFG1
  H(f,theta) = <e, z_out>/eps

Also compute G_enc via single VJP. Plot a(f,theta)=H*G heatmap. Compute ideal water-filling gain: 10 log10(mean_top25% a^2 / mean_all a^2). Variant at t in {0.4,0.5,0.6} to see f_c migration.

Total ~48*3=144 chains x 20 steps ~= 8-12 min on 4090 (batched 4x -> ~3 min).

### Kill criterion

- Kill if H(f,theta) dynamic range <3 dB across ring at t=0.4. Then water-filling gain <0.8 dB; angle-selectivity is the only remaining axis -- if flat, dead.
- Kill if top-quartile a^2 gain <1.2 dB at t=0.5 or f_c(0.6) inside radius <8 (no frequency survives .6) -- then .6 unfixable in latent DCT basis.

### T4/T5 risk

- T4: LOW-MODERATE. Mid-frequency oriented energy (8-16, H/V bias) more robust to crop/resize than high-frequency; comparable to uniform.
- T5: LOW. Selecting high-H directions is selecting what purifier preserves. Adaptive notching would need to know selected bins.
---

## 3. Latent Channel Anisotropy and Encoder-Decoder Cycle Alignment

### Geometric argument

SD1.5 VAE latent has 4 channels with unequal statistics: Var(z_c) ~= [0.42,0.58,0.61,0.47] and ||J_enc^{(c)}||_F varies ~4-6 dB across channels (ch2 most sensitive, ch0 least; KL regularization).

Current F5 spreads 320 chips uniformly 80/ch. Uniform is optimal only if per-channel survival a_c = E[||P_c J_cycle P_c||] equal. It is not: encoder gain G_c differs, denoiser sensitivity differs (cross-channel attention not permutation-equivariant), and cycle Jacobian J_cyc^{(c)} has channel-dependent contraction (small J_dec gain => E(D(z)) attenuates that channel).

Optimal allocation p_c propto a_c^2 (water-filling). Also perturbation should align J_enc row space with J_dec column space: perturbations in Ker(J_dec) survive encoding but vanish after decode->re-encode.

Adversarial view: dx that VAE amplifies (large ||J_enc dx||) but decoder renders as plausible texture (small perceptual ||x - D(E(x)+J_enc dx)||) is exactly direction denoiser treats as signal (s_theta small). Such dx in span(V_top) intersect span(J_dec U_top).

### Expected latent displacement

Per-channel a_c spread ~3-5 dB. Reallocating 320 chips propto a_c^2 yields Delta SNR = 10 log10(sum p*_c a_c^2 / sum p_uniform a_c^2). With 4 dB spread, optimal weighting ~= [0.12,0.32,0.38,0.18] vs uniform 0.25 each -> +0.9 to +1.6 dB at .4/.5.

Additional alignment: projecting dz onto span(J_dec^T J_dec) avoids ~15-25% energy in Ker(J_dec) lost in D->E cycle. Recovering half -> +0.6 to +1.0 dB additive.

Combined: +1.5 to +2.6 dB at .4/.5. At .6, J_Phi contraction dominates and is more channel-uniform: +0.4 to +1.0 dB.

### Translation to stress grid

- .4: 51-54/58 (+2 to +5)
- .5: 40-43/58 (+3 to +6)
- .6: 11-14/57 (+1 to +4)

Binding failures at .4/.5 may worsen if dominant channel carries more semantic content (ch1/2 dominance correlates with CLIP sensitivity).

### Cheapest decisive test (<=15 min GPU)

Per-channel survival assay (no PGD). For 4 channels on 4-6 images:

  For c in 0..3:
    z=E(x); e_c=DCT ring confined to channel c, ||e_c||=eps
    x_pert=D(z+e_c); z_cyc=E(x_pert)-E(D(z)); a_c^E=||P_c z_cyc||/eps
    z_den=Phi(z+e_c; t=0.4)-Phi(z; t=0.4); a_c^R=||P_c E(D(z_den+z))||/eps

Also compute G_c via Hutchinson trace (20 probes, VAE only, 1 min). Plot a_c^R(t) for t in {0.4,0.5,0.6}. Total ~4*6*3=72 cycles ~=4-6 min GPU.

Cycle-alignment check (CPU, 2 min): cos(J_enc dx, J_dec^T J_dec J_enc dx) for current F5 dx* via single VJP/JVP. If cosine <0.6, significant energy in Ker(J_dec).

### Kill criterion

- Kill if per-channel a_c^R spread <2 dB at t=0.4. Headroom <0.5 dB.
- Kill if a_c^R ranking inversely correlates with CLIP binding (Pearson r(a_c, Delta_CLIP_c) >0.7): exploiting anisotropy trades against binding -- the .4/.5 bottleneck. Kill or require joint CLIP-constrained allocation.

### T4/T5 risk

- T4: MODERATE. Channel-concentrated watermark vulnerable to per-channel perturbations (color jitter, channel-wise compression). Mitigation: do not concentrate >45% in single channel; keep >=3 channels active.
- T5: LOW-MODERATE. Purifier with same latent bias preserves selected channels. Risk rises if purifier uses different VAE (SDXL vs SD1.5 channel semantics not identical).

---

## Cross-Cutting Notes

Priority order: (2) -> (1) -> (3). (2) has highest predicted .6 lift and cheapest H(f,theta) measurement; (1) most principled for .4/.5; (3) lowest-hanging but risks binding trade-off.

Interaction: Composable. Ideal is SVD subspace (1) restricted to high-H frequencies (2) with channel water-filling (3). Expected combined gain sub-additive: ~+2.0 to +3.5 dB, translating to .4: 54-57/58, .5: 44-50/58, .6: 16-22/57 if all hold. If only one survives kill criteria, pursue that one.

What H1 already ruled out: Radial band narrowing (8-28) and global a-weighted combiner. Proposals survive H1 because (1) exploits angular/singular-vector structure H1 did not test, (2) angle-dependent H not radial, (3) channel not frequency.

Global kill: If all three assays show <1 dB headroom, conclude SD1.5 VAE+UNet cycle is effectively isotropic in 4-32 DCT subspace at 52 dB; further gains require (a) higher PSNR budget, (b) semantic carrier outside VAE latent, or (c) detector-side improvements (binding, not carrier).