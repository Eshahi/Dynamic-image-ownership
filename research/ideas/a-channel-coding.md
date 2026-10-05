# A — Channel coding over the regeneration channel for F5

Scope: F5 r2 pinned SD1.5 VAE encoder, DCT band radius 4-32 (3272 coeffs -> 320 chips, repetition ~10.2x, weight radius/4), PSNR 52 dB, 7-view soft binding (32-bit q). Stress grid 12 sources x {.4,.5,.6} x 5 seeds, CFG1 20 steps: F5 r2 .4 49/58 .5 37/58 .6 10/57. H1 measured per-chip attenuation a~0.57 at .4 (corr 0.79, variance hetero 0.12-0.35), optimal a/v weighting +1.1 dB only, band 8-28 no gain. At .4/.5 bottleneck is binding drift; at .6 carrier loss. T4 0/20, T5 0/66 must stay 0. No re-embedding beyond cheapest test without kill review.

Channel model shared by proposals: after img2img, de-whitened chip observation r_i = a_i c_i + n_i, c_i in {+/- sqrt(Ec_i)}, n_i ~ N(0, sigma_i^2) approximately independent after keyed sign de-spreading but empirically colored (H1 variance spread). Repetition within a chip averages ~10 DCT bins, so chip SNR_i = a_i^2 Ec_i / sigma_i^2. Threshold set for FPR 1e-6 (decoded 8.26). Current operating point: median latent score ~10.4 at .4 (barely above recomputed 4.98 on tails), 37 at clean — headroom ~8-10 dB before threshold.

Capacity estimate: AWGN per chip C_i = 0.5 log2(1+SNR_i). At .4, median chip BER from probe approx Phi(- a sqrt(Ec)/sigma). With 52 dB budget Ec ~ 15-26x natural probe gain (F5 gain 15.9 at 52 dB), effective chip Eb/N0 roughly 2-4 dB at .4, ~0-1.5 dB at .5, <0 dB at .6. Total capacity over 320 chips at .4 approx 320*0.5*log2(1+1.5) ~ 210 bits; at .5 ~ 100 bits; at .6 ~ 40 bits. Payload is only 32 b of q plus implicit detection preamble (~5-6 b of threshold margin). So channel is not capacity-limited at .4/.5 for 32 b — it is code-limited: repetition is ~4-5 dB from capacity at rate 0.1. A modern code at same rate can deliver 2-4 dB coding gain, and UEP/list decoding can trade that gain for binding robustness without touching embedding energy.

---

## P1 — Concatenated code with interleaving: replace repetition by rate-~0.1 soft code

**Idea:** Keep 3272-slot geometry and L2 budget, but replace the 10x repetition over 320 chips by an outer binary code + inner spreading with interleaver. Baseline is repetition (rate 0.1, hard minority) — the worst code on AWGN. A concatenated construction — e.g. outer BCH(63,36) t=5 or LDPC(320,32) rate 0.1, or rate-1/3 tail-biting convolutional + random interleaver across radial bins — gives 2-3 dB coding gain at BER 1e-3/1e-4 on AWGN and decorrelates the colored burst errors H1 observed (variance 0.12-0.35 correlated by radius).

**Derivation.**

- Inner channel: r = a c + n, c = sqrt(Ec) * (2b-1). Repetition distance d_rep=10, soft combining SNR_rep = 10 * a^2 Ec / sigma^2. Coded system: same Ec per slot, but 320 coded bits carry 32 info bits via code distance d_code >> d_rep effective. For rate 1/10, Shannon limit Eb/N0 = (2^{2R}-1)/(2R) ~ -0.9 dB; repetition needs ~4-5 dB for BER 1e-4, LDPC/TBCC needs ~1-2 dB — gap 2.5-3.5 dB (standard AWGN coding tables). Water-filling across a_i/sigma_i is folded into bit-to-slot mapper: assign coded bits to slots with weight sqrt(Ec_i) proportional to a_i/sigma_i^2 already approximates, but interleaver ensures each codeword sees average a/sigma.
- Capacity check: at .5 where probe extrapolates a~0.42 (from 0.57 at .4, ~ -2.7 dB), repetition SNR ~ -1 to +1 dB chip-level -> BER ~ 0.15-0.25, above threshold. 2.5 dB gain moves operating point to BER ~0.07-0.12 — enough to keep chip-level soft score above 8.26 on ~60% of current .5 carrier tails.

**Expected quantitative gain (stress grid):**

- .4: carrier failures are ~3/58 now; coding gain rescues at most those 3 plus turns marginal binding-adjacent carriers (scores 5-7) solid — estimate +2 to +4 at .4 (49->51-53/58).
- .5: 21/58 fail now, ~38% carrier among .6 fails suggests at .5 ~8-10 carrier + 11 binding. Coding gain rescues ~6-9 carrier tails -> 37->43-46/58.
- .6: 47/57 fail, ~38 carrier. Even 2.5 dB rescues only ~8-12 of the best carrier tails (scores 5-8) -> 10->18-22/57. No claim to close .6.

**Cheapest decisive test (<=15 min GPU, mostly CPU):**

1. CPU-only simulation: take H1 probe per-chip (a_i, sigma_i) + empirical covariance; synthesize r_i for 10k random codewords at .4/.5/.6 SNR. Simulate repetition decoder (current sign vote, threshold 8.26) vs. soft Viterbi for TBCC(1/3, K=7) punctured to 1/10 or LDPC(320,32) belief propagation (off-the-shelf, 20 iterations). No re-embedding. Measure BER and block error vs threshold.
2. If sim shows >=2 dB gain at BLER 1e-2: one GPU re-embedding pilot (4 sources x 3 strengths x 2 seeds = 24 images, PSNR 52, same PGD but loss = code-aware margin — sum over coded bits instead of repetition margin; keep steps 150). Decode with new decoder, compare paired both_match.

**Kill criterion:** Simulated coding gain <1.5 dB at BLER 0.05 or pilot paired gain <+2 at .5 (n=12-24, p~0.5 threshold from research plan) or LPIPS regression >5% at equal PSNR. Also kill if decoder complexity requires >2x detection time without >+4 at .5.

**T4/T5 risk:** Explicit. Stronger code lowers undetected-error rate, so T5 joint collisions stay 0 if threshold kept. But lower required SNR could make copied residual (T4) more likely to cross threshold if donor energy leaks — risk is decoder sensitivity, not energy. Must re-run T4 on pilot: kill if semantic delivered >1/20 (same as H2 kill). T5 must stay 0/66; any new collision kills proposal even with T3 gain.

---

## P2 — Unequal error protection (UEP) + water-filling across q bits

**Idea:** Not all 32 q bits are equal under soft binding: phi(c_j | p_j, t)=Phi(c_j p_j cot t) — bits with |p_j| near zero dominate error. Current repetition treats all bits equally (equal Ec). UEP allocates more chips / more energy to fragile bits (small |p| and large tan t). Water-filling across DCT radius already does power allocation across frequency; UEP does it across information bits.

**Derivation.**

- Let t = soft distance * pi/32. Bit error p_e,j = Phi(-|p_j| cot t / sigma_eff). For the 32 projections, |p_j| distribution is half-normal with median ~0.67 sigma_p. At t~0.45 rad (typical drift at .4), cot t ~2, so p_e ranges 0.05 for large |p| to ~0.35 for small |p| — 7x spread. Equal Ec wastes power on already-reliable bits.
- Channel with UEP: assign n_j chips to bit j, sum n_j=320, or weight Ec_j. Effective SNR_j = n_j * a^2 Ec_0 / sigma^2 (if repetition per bit). Optimize n_j to equalize p_e,j or minimize max soft-distance contribution. Water-filling solution: n_j proportional to 1/|p_j| in first order, capped. Approx gain: moving 20% of chips from 8 strongest bits to 8 weakest bits cuts worst-bit p_e from 0.35 to 0.18, reducing expected Hamming drift by ~1.2 bits and soft distance by ~0.12 rad — comparable to 1.0-1.5 dB overall. This directly attacks the .4/.5 binding cluster (soft distances 6.2-7.2 at .4, median 9.1 at .5) where 1 bit is the margin.
- Capacity view: feedback-free UEP does not change total capacity (same sum power), but for a fixed code rate it reduces required Eb/N0 for the worst bits by ~1.5 dB, which at .4 is the difference between 49/58 and 53-54/58 seen in H4 threshold 7 analysis (4 rescued at .4).

**Expected quantitative gain:**

- .4: H4 showed thr 7 rescues 4/6 fails. UEP achieves similar without raising threshold — estimate +3 to +5 at .4 (49->52-54/58).
- .5: thr 7 rescues 0/14, thr 8 rescues 4/14 — drift too large for threshold alone. UEP rescues ~2-4 of the 14 .5 fails where 1-2 fragile bits dominate -> 37->39-41/58.
- .6: dominated by carrier, UEP gain ~0 to +1.

**Cheapest decisive test (CPU only):**

Re-read only. On existing stress baseline attacked images (58+58 rows), compute per-bit p_j magnitudes from stored 7-view projections (or recompute CLIP on CPU for 12 sources — ~2 min). Simulate UEP mapper: re-weight chip LLRs by n_j (or Ec_j) and recompute soft distance without re-embedding (post-hoc LLR scaling). Measure rescued binding failures vs current soft at radii 6,7,8. No GPU.

**Kill criterion:** Simulated rescue <+2 at .4 at FPR-equal threshold (different-label matches must stay <=2/114 as in H4), or UEP weights increase T5 pairwise matches beyond 4/132 at thr 6-equivalent. If CPU sim passes, one-shot GPU pilot (4 sources, 5 seeds, .4/.5) with UEP-aware PGD loss (weight bit margins by 1/|p_j|) — kill if pilot delta <+2 at .4 or any LPIPS/T4 regression.

**T4/T5 risk:** UEP keeps total power and threshold, so T5 at matched FPR is neutral — but reallocating power to fragile bits makes random-image q collisions slightly more likely on those bits (they become more detectable). Empirically H4 showed thr 7 -> 2.5x false pairs (4->10/132). UEP at thr 6 must not exceed that FPR; explicit check on 132 ordered clean pairs required. T4 risk low (total energy unchanged), but donor copy-paste that happens to align with weak-bit pattern could gain ~0.5 dB — monitor T4 pilot, kill if >0/20 semantic delivered.

---

## P3 — List / soft-binding decoding with outer CRC (bind without lowering threshold)

**Idea:** Keep carrier and threshold at 6, but decode q to a short list and disambiguate with an outer check — i.e., list decoding of the semantic code. Current soft binding makes a hard decision at radius 6 (3.8 bits expected under drift vs 16 random). At .5, fail distances median 9.1 (range 7-11) — many fails are only 1-3 bits beyond 6. A list decoder that returns L=4-8 candidates within radius 8-10 and picks the one consistent with an 8-bit CRC (or with CLIP prior |p|) achieves thr-8 coverage at thr-6 FPR.

**Derivation.**

- Channel for q: 32-bit vector through AWGN + CLIP drift, modeled as BSC with crossover p ~ 0.15 at .4 (distance 4.8/32), p~0.28 at .5 (9/32). Capacity of BSC(p) is 1 - H(p): ~0.39 bits/channel at .4, ~0.13 at .5 — so 32*bC = 12.5 bits at .4, 4.2 bits at .5 of mutual info, insufficient for 32 bits uncoded but sufficient for 24+8 CRC with list size 8.
- Block error for bounded-distance decoder radius 6: P_e = sum_{i>6} C(32,i) p^i (1-p)^{32-i}. At p=0.15 -> P_e~0.06; at p=0.28 -> P_e~0.55. List radius 8: P_e(8) at p=0.28 -> ~0.27 — halving the error. But naive radius 8 raises FPR 5x (H4: 4->21/132). With 8-bit CRC, false-accept among L=8 random candidates is L * 2^{-8} = 0.031 per image; times 1e-6 carrier FPR -> joint FPR ~3e-8, still below 1e-6 target. So list+CRC buys radius 8 at radius 6 FPR.
- Practical: CLIP provides per-bit reliability |p_j| — use Chase-like list: flip the 3-4 least reliable bits, enumerate 8-16 candidates, check CRC that was embedded as part of q (requires re-embedding 8 CRC bits — 32->24 info + 8 CRC, same 32-chip budget, or 40 chips if extended to 40). Even without CRC, picking candidate with maximal phi(c|p,t) (ML) among list is already soft+list gain of ~0.5-1.0 bits.

**Expected quantitative gain:**

- .4: fails at 6.2-7.2 — list radius 8 with CRC rescues 5/6 (H4: thr 8 rescued 5/6) -> 49->54/58.
- .5: thr 8 rescued 4/14 -> 37->41/58 (same as H4 thr 8 but at thr 6 FPR). With |p|-ordered list, expect 3-5 rescues (not 0 as thr 7) because ordering exploits soft info.
- .6: carrier failures dominate, no gain beyond P1's carrier fix — expect +0-2.

**Cheapest decisive test (CPU only):**

On existing attacked images, assume transmitted q known (from clean image 7-view code). Run list decoder post-hoc: generate candidates within Hamming 8 of hard q_hat (or Chase over 4 least reliable |p|), count how many fails would be rescued if an 8-bit CRC had been present (i.e., assume CRC would select correct candidate when it is in list and no other candidate accidentally matches CRC). Compute rescue rate vs FPR estimate from 132 clean ordered pairs (count pairs where any list candidate collides and CRC would falsely match). No re-embedding.

**Kill criterion:** CPU rescue <+3 at .4 or <+2 at .5 after CRC-adjusted FPR, or required list size to rescue >16 (implies latency/cost), or FPR-adjusted rescue is no better than H4 thr 7 (already killed). If CPU passes, pilot re-embedding needed to actually embed CRC bits (4 sources x 5 seeds x .4/.5, 20 images, ~8 min GPU) — kill pilot if paired gain <+2 at .5 or T5 list collisions >0/66 or different-label matches >2/114.

**T4/T5 risk:** Highest among the three if done naively — raising radius to 8 without CRC multiplies T5 collisions (H4: 0->multiple). CRC restores FPR only if CRC bits are themselves protected at least as well as q bits; otherwise attacker can forge CRC. T4 risk: donor patch that carries wrong q but happens to be within list distance + CRC collision (prob 1/256) could be falsely attributed — joint probability still ~ 0.004 per donor, so 0/20 must hold in pilot. Explicit T5 re-evaluation mandatory; any joint collision at list+CRC kills. Also T5 CRC must be evaluated on 66 distinct-image pairs with same profile — must stay 0/66.

---

### Ranking and next step

P2 and P3 are CPU-re-readable today and attack the actual .4/.5 binding bottleneck; P1 attacks the .6 carrier tail and is prerequisite if .6 matters for thesis. Cheapest order: P2 sim -> P3 sim -> P1 sim; any pilot that needs re-embedding does 4-source subset first. All three keep PSNR 52 dB and T3 gate (.1 29/29, .2 28/28) as non-regression; none changes VAE/CLIP pins.
