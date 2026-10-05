# c — Cryptographic binding of noisy semantics for F5

Scope: F5 r2 binds 32-bit code q = sign(R E) where E is 7-view CLIP unit vector, R is keyed Rademacher (32x512), via soft ML angle sum log Phi(c_j p_j cot t) vs radii <=6 pi/32 match / >=10 pi/32 mismatch. Stress (20261005-1200, 5 seeds, soft 7-view): .4 49/58, .5 37/58, .6 10/57. Remaining .4/.5 misses are binding: distances 6.2-11.6 at .4 (6 fails), 7.0-11.4 median 9.1 at .5 (14 fails). H4 killed: 6->8 rescues +4/14 at .5 but false distinct-label pairs 4->21/132, T5 risk. Carrier: 320 chips x 10x redundancy on 3272 slots; budget to lengthen code or embed helper without carrier loss. T4 0/20, T5 0/66 must stay.

Threat for binding: attacker sees regenerated x' and its CLIP E' ~= E + noise (nearby embedding, no key). Helper data P if any is public (stored in image or derived from public OwnerID). Forgery = produce x_f whose q_f passes semantic radius under any enrolled key without possessing key. Binding must not give attacker advantage beyond what E' already gives.

At most 3 proposals. Each uses fuzzy-extraction / syndrome toolbox, keeps key-dependence, and is testable without held-out.

---

## 1. Syndrome secure sketch with binary BCH — q-offset helper in carrier

### Construction sketch

Lengthen semantic code to n=63 (64 minus 1) to fit a binary BCH. Enroll for source u:

- Compute E = mean_7view(CLIP(u)), projections p = R E in R^n (keyed Rademacher n x 512), hard code q = sign(p) in {+/-1}^n mapped to {0,1}^n.
- Pick random codeword c in C where C = BCH(63,30, t=6) [alternatively (63,36,t=5) or (31,16,t=3) if staying at 32]. With systematic encoding, c = Encode(m) for random m uniform.
- Helper (public) s = syndrome(q) = H q in {0,1}^(n-k) or equivalently offset h = q xor c (code-offset). Both are linear sketches; syndrome is smaller (33 bits for (63,30)). Store s (or h) in the robust carrier as extra payload: allocate 33 of the 320 chips to helper bits (rate 32/320=0.10 has headroom; dropping to (32+33)/320=0.20 still leaves ~5x redundancy). Helper is key-independent given q but q is keyed. Alternative without extra chips: derive s deterministically from public OwnerID + source_uid via PRF; embedding in carrier is preferred for information-theoretic sketch.
- What is written to pixels: (a) helper bits s via same encoder-amplified latent chips (protected by same margin 4.0), (b) the codeword c is not written — only q's sketch is stored. Detector recovers with soft sketch: from attacked image read p' = R E' and helper s' (decoded helper chips), compute noisy q' = sign(p'), then c' = q' xor h (or syndrome decode H q' xor s), BCH-decode to c_hat, reconstruct q_hat = c_hat xor h, then run existing soft-angle check on q_hat vs p' (or Hamming d(q_hat,q')).

Soft variant: feed LLRs L_j = log Phi(p'_j)/Phi(-p'_j) (monotone in |p'_j|) to a soft BCH decoder (Chase / ordered-statistics) instead of hard q'. Existing soft likelihood already computes Phi(c_j p_j cot t); reuse.

Code choice: BCH(63,30,t=6) corrects 6 hard errors, 33-bit helper, code rate 0.48. For n=31 variant, BCH(31,16,t=3) corrects 3, 15-bit helper, needs no code length change — weaker rescue but cheaper. Recommend testing both; 63-bit dominates rescue at .5.

### Security argument

This is the standard Dodis et al. syndrome secure sketch (EUROCRYPT 2004, fuzzy extractor). For uniform q (keyed Rademacher signs of random CLIP direction are uniform +/-1 under key), helper s = Hq leaks at most n-k bits; residual min-entropy H_inf(q|s) >= n-(n-k)=k. Attacker who sees x' already has q' correlated to q with BSC error ~ drift/n. Giving s does not reduce search below 2^k for forging a q_f that decodes to same sketch — forgery still requires finding a vector within distance t of a codeword coset, which without key requires guessing R.

Formally, sketch is information-theoretic: s is linear function of q; for any distinguisher seeing E' and s, advantage for forging a matching q_f is at most advantage for guessing q given E' plus 2^{-k} (leftover hash lemma if hashing to key). Keyed R means q is PRF output; without key, s is indistinguishable from random syndrome of random vector (helper reveals coset, not codeword). No key-dependent helper is released that helps transfer: T4 donor's helper s_donor encodes donor's q_donor; recipient's E'_rec is uncorrelated (different-label cosine ~=0.2), so decoding donor coset with recipient's q' fails with prob 1 - V_t/2^n (~1).

Helper-in-carrier does not help forger beyond E': forger who can read helper chips already can read carrier chips (same latent band); helper decoding requires carrier success, which T4 already shows is 0/20 for copied residuals (carrier not transferred). So T4 stays 0.

T5: joint collision now requires two distinct images land in same syndrome coset and decode to same codeword within t. For random distinct q1,q2, Pr[s1=s2]=2^{-(n-k)} (~ 2^-33 for (63,30)), so T5 joint rate drops vs current 32-bit radius check, not rises.

### Expected quantitative rescue

H4 soft distances at .5: fails at 7.0-11.4 bits (on 32-bit scale). Scaled to 63 bits, drift ~= 14-22 bits (linear). BCH(63,30,t=6) hard-corrects 6, soft Chase-2 corrects ~8-9 effective (gain ~30%). That rescues fails with <=8 errors: on current data, ~0/14 at hard 6, but with soft+7-view already rescuing borderline, syndrome adds +3-5/14 at .5 (from 37->40-42/58) and +2-3/6 at .4 (49->51-52/58). BCH(31,16,t=3) rescues <=3-error fails: +0 at .5 (since median 9), not enough — predicts need for 63-bit.

More precise: assume drift distribution d ~ Binomial(n, p_s) with p_s~=0.28 at .5 (9/32). Pr[d<=6]=0.03, Pr[d<=8]=0.12 for n=63, p=0.28 -> expected rescued 1-2/14 hard, 3-5 with soft. At .4 where p~=0.20 (6.5/32), Pr[d<=6]=0.25 on 63 bits -> +1-2 extra over hard threshold.

Net: +4 +/-1 at .5, +2 +/-1 at .4 over current soft baseline. Not dramatic alone, but combines with Proposal 2's soft LLRs.

### Cheapest decisive test (<=15 min GPU or CPU)

CPU-only possible, no re-embedding:

1. Lengthen R to 63 rows (derive extra 31 rows from same key stream, reusing first 32 for comparability). On existing stress PNGs (20261005-1200 re-detected h4-soft-distances.json plus p_j dumps), synthesize p_j for j=32..62 by projecting stored E' (or re-running CLIP 7-view once per image — ~2 min GPU for 173 images). Synthesize helper s = H q_source from source q (compute once).
2. Simulate BSC: hard q'_j = sign(p'_j), then syndrome decode Decode(H q' xor s) via off-the-shelf BCH decoder (e.g., bchlib, galois in Python, CPU <1 s). Count rescued vs soft baseline.
3. Control: compute false syndrome collisions on 132 distinct-label pairs (hard) -> expected 0; check T5 66 pairs still 0 joint collisions after sketch.

GPU variant (15 min) if CPU E' not cached: one script f5_syndrome_probe.py --n 63 --code bch --view 7 --soft chase2 reading stress PNGs, doing 7 CLIP passes + one BCH decode per image, no PGD.

Cost: ~3 min GPU for CLIP 7-view on 173 images + CPU decode. No embedding.

### Kill criterion

Kill if BOTH hold:

- Rescue at .5 <=1/14 over soft-7-view baseline with soft Chase-2, AND
- Distinct-label syndrome collisions >2/132 or T5 joint collisions >0/66 (i.e., sketch raises FPR above H4's budget).

Also kill (63,30) variant if helper chip decode failure >20% at .5 (helper itself must survive regeneration; if helper bits need >8 dB more margin than available at 52 dB budget, sketch is moot). Helper survival is measurable as helper-chip BER at .5.

---

## 2. Soft-information LDPC / polar code with LLR-based syndrome decoding — no helper, keyed interleaver

### Construction sketch

Keep n=63 (or 128 for LDPC sweet spot; slots allow 128 chips at rate 0.25) but do not embed helper. Instead treat binding as noisy channel coding of q itself: enroll q = sign(R E) (63 bits), interleave with keyed permutation pi_K (derived from OwnerID + carrier key), encode with systematic LDPC (e.g., regular (3,6) LDPC n=128,k=64, or 5G polar n=64,k=32) — but transmit only parity bits as helper, or transmit full codeword: the codeword is q padded. Detection is joint soft decoding of q' from LLRs.

Concrete soft-LDPC sketch (no extra payload, helper = parity of q):

- Enroll: compute q (63 bits), compute LDPC parity p = H q (e.g., 32 parity bits for rate 1/2). Embed parity bits p in carrier (like Proposal 1) OR derive parity as helper via PRF (no carrier cost). The point is detector has LLRs L_j = log Phi(p'_j cot t / sigma_p) approximated by L_j proportional to p'_j (since Phi is sigmoid in p'_j); small |p'_j| -> LLR ~=0 (erasure), large |p'_j| -> confident +/-.
- Recovery: belief-propagation decodes q_hat from (L_1..L_n, parity p') correcting up to ~10-12 soft errors (LDPC soft threshold >> BCH hard). This strictly dominates H4's hard radius 6 and soft angle sum, because BP exploits per-bit reliability: bits near zero are treated as erasures rather than errors.

Polar variant: Polar(64,32) with SCL decoding, LLRs as above, CRC-aided — even cheaper to test (CPU only, aff3ct).

Keyed interleaver pi_K ensures code structure is keyed: without key, attacker cannot run BP on correct Tanner graph (permutation of variable nodes). With wrong key, decoding fails random.

No threshold relaxation: decision is q_hat == Decode(L, p') succeeds (valid codeword) AND soft residual sum |L_j| 1[q_hat_j != sign(L_j)] below code's soft distance. This keeps FPR bounded by code's distance spectrum, not a tunable radius.

### Security argument

Same secure-sketch guarantee as Proposal 1 (helper = syndrome), plus computational hiding via keyed interleaver: LDPC Tanner graph is public, but permutation pi_K is keyed PRF. Attacker seeing E' and parity p learns at most n-k linear equations on q, i.e., coset membership — identical to BCH syndrome. Forgery requires solving noisy syndrome decoding without key: finding q_f within soft distance of a codeword in the permuted code. For random LDPC/polar ensemble this is NP-hard / at least as hard as decoding random linear code. T4 donor helper p_donor is useless for recipient because recipient's LLRs are for unrelated q_rec (inter-codeword distance ~32/64), BP will not converge to donor coset (syndrome mismatch with high LLR conflict).

Advantage over Proposal 1: soft BP corrects twice the hard radius by exploiting reliability (erasure channel), so relaxation 6->8 that raised FPR to 21/132 is replaced by code's distance property (LDPC minimum distance ~10-14 for n=63 rate 1/2, so false distinct-label decoding probability ~ 2^{-(n-k)} = 2^-32).

T4/T5 preservation identical to Proposal 1: helper alone insufficient without close q'; distinct-label q' decodes to different codeword or decoding failure, not donor's.

### Expected quantitative rescue

LDPC soft BP at rate 1/2 corrects BSC p~=0.28 (our .5 drift) with block error ~0.1-0.2 at n=64, vs BCH hard error 0.9. Concretely, with per-bit LLRs, effective correctable errors ~10-12 on 63 bits (vs 6 hard). On H4 .5 fails (7-11 hard errors on 32 bits -> 14-22 on 63 bits), soft BP rescues ~7-9/14 (vs +4 for BCH hard). Projected stress: .5 37->44-46/58 (~76-79% vs 64% baseline), .4 49->53-54/58 (~91-93%). At n=32 with soft BCH this is ~+2; at n=64 LDPC it is +7-9. If using n=128, rescue at .5 approaches 10/14.

Conservative: +6 +/-2 at .5, +3 +/-1 at .4 over current soft baseline.

### Cheapest decisive test (CPU or <=15 min GPU)

CPU-only simulation suffices:

1. Generate LDPC parity matrix H (e.g., pyldpc or construct regular (3,6) 32x64) and keyed permutation pi_K from carrier key. Compute p = H pi(q) for each source's 63-bit q.
2. On stress PNGs, compute LLRs L_j = logit Phi(p'_j cot t) — linear in p'_j for small angles, else use exact Phi. Feed (L, p) to BP decoder (5-20 iterations, CPU ~0.5 ms/codeword).
3. Score rescue count vs soft baseline; measure distinct-label false decode rate (BP converging to wrong codeword) on 132 pairs — expect 0 with distance >=10.
4. Ablation: hard-input BCH vs soft-LDPC vs soft-polar on same L to isolate soft gain.

No re-embedding; total runtime <2 min CPU for 173 images + 132 pairs once LLRs are computed (CLIP 7-view for LLRs is the only GPU cost, ~3 min, or reuse cached p'_j).

### Kill criterion

Kill if soft-LDPC rescue at .5 <=2/14 over soft-7-view baseline (i.e., per-bit reliability is not informative enough — implies |p'_j| is uncorrelated with error after regeneration, contradicting cot-t model) OR false-decode rate on 132 distinct-label pairs >=3/132 (code distance insufficient at chosen n/k). Also kill if helper parity decode BER itself >15% at .5 (parity bits in carrier not surviving — same as Proposal 1 helper survival check).

---

## 3. Two-codebook / list-decoding with keyed PRF binning — computational fuzzy extractor without helper

### Construction sketch

Instead of storing helper, enroll two independent Rademacher codebooks keyed by OwnerID:

- Primary code q = sign(R_0 E) (32 bits) — as now.
- Secondary bin code b = PRF_K(E_quant) where E_quant is coarse CLIP quantization (e.g., top 8 PCA dims of E, 2 bits each -> 16-bit bin). Realized as b = sign(R_1 E') with independent key R_1 but only used for binning: partition the 2^32 q space into B=256 bins via b (8 bits). Conceptually, fuzzy extractor Gen(E) -> (key, helper) where key = Hash(q), helper = bin index.

List decoding at detector:

- From attacked E', compute p'_0 = R_0 E', p'_1 = R_1 E' -> soft lists: generate L=4 nearest b candidates (flip 1-2 least-reliable bits of b'), for each bin b_i retrieve the enrolled q candidates enrolled in that bin (only one true q per source, but bin contains ~2^{32-8}=16M codewords — we need codebook structure). Practical construction: concatenated code — outer code is BCH(63,30) as in Proposal 1, inner bin is parity of outer code; list decoding enumerates outer codewords within soft radius 8 of q' that also land in bins near b'.

Simpler deployable variant (no outer code needed for test): dual-threshold with bin confirmation:

- Enroll stores q (32 bits) + b (16 bits) — b is 16-bit coarse semantic hash, embedded cheaply in 16 extra chips (total 48 bits, still <<320).
- Detect: compute soft distances d_0 = soft_angle(q', q) and d_1 = Hamming(b', b). Accept iff d_0 <= 8 AND d_1 <= 3 (bin confirms), OR d_0 <= 6 (current) regardless. Bin confirmation allows relaxing d_0 to 8 only when coarse semantics agree, blocking distinct-label false pairs (which disagree on b with prob 1 - 2^{-16}).

This is a computational fuzzy extractor (Boyen et al.): helper is b, key is q hashed with b. No syndrome; security rests on PRF.

### Security argument

Attacker sees E' -> can compute b' and q' (noisy). Bin b leaks at most 16 bits of E (coarse dims), but b is keyed via R_1, so without key attacker cannot predict b for a target source better than random. Forgery requires finding x_f whose (q_f,b_f) both land in enrolled bin — i.e., produce CLIP vector simultaneously close in fine projections (32 dims) and coarse dims. Since R_0 and R_1 are independent keyed, this is strictly harder than forging q alone (conjunction). T4: donor's b_donor is for donor semantics; recipient E'_rec has uncorrelated coarse code (Hamming ~8/16), so bin check fails — T4 stays 0 even if d_0 is relaxed to 8. T5: joint collision now requires both q within 8 AND b within 3: probability ~= (21/132 for q alone) x (1/500 for b random) ~= 0.0003, so 0/66 stays.

Helper b does not help forger: b is 16-bit function of E, already computable from E' up to noise; publishing b (in carrier) gives at most 16 bits that attacker could estimate from E' anyway. Keyed PRF means b without key is pseudorandom.

### Expected quantitative rescue

On .5 fails where d_0 in [7,11], bin check rescues those with d_1 <=3. Coarse b uses 2-bit quantization of robust PCA dims; regeneration at .5 flips coarse bits with p~=0.10 (vs 0.28 for fine bits), so Pr[d_1<=3] on true source ~=0.90 (Binomial 16,0.1). Distinct-label d_1 ~8/16, Pr[d_1<=3] ~=0.02. Thus of 14 fails at .5, ~12-13 have d_1<=3, but d_0<=8 filter still applies: fails with d_0=7-8 are ~4/14 -> rescued 3-4. Combined with soft d_0 (Proposal 2's LLRs), rescue is 5-7/14 at .5.

Total: .5 37->41-44/58, .4 49->53-54/58. Gain is smaller than LDPC soft but FPR cost is lowest and no syndrome decoder needed.

### Cheapest decisive test (<=15 min GPU)

CPU/GPU ~5 min:

1. Compute coarse b for all 12 sources: PCA of 7-view E (fit on 12 sources, 512->8 dims, 2-bit uniform quant per dim -> 16 bits). Key R_1 as second Rademacher set (derive from carrier key + 1).
2. On stress PNGs, compute b' (same PCA + quant) and d_1 = Hamming(b',b_source), plus existing soft d_0 (from h4-soft-distances.json scaled). Count fails where d_0 in [7,8] and d_1<=3 -> rescued. Measure distinct-label d_1 distribution on 132 pairs -> confirm <=3/132 false bin matches.
3. No re-embedding; PCA and 7-view CLIP for b reuses same CLIP passes as q. One GPU pass computes both.

Optional 15-min GPU refinement: re-embed 12 sources with extra 16 chips for b (add to f5_latent_codec payload, 1 line change) and verify b chip survival at .5 (should be >95% since margin same).

### Kill criterion

Kill if EITHER:

- Rescue at .5 via bin-relaxed d_0<=8 <=1/14 (i.e., coarse code not more robust than fine — implies PCA dims drift as much as random projections), OR
- Distinct-label d_1<=3 rate >=4/132 (coarse code not discriminative — PCA quantization too coarse, FPR budget exceeded), OR
- Combined rescue <=2/14 after including soft d_0 (bin adds nothing over Proposal 2 alone — then prefer Proposal 2).

---

## Comparative note

| Proposal | Helper cost | .5 expected rescue (over 37/58) | FPR cost | T4/T5 invariant | Verdict |
|---|---|---|---|---|---|
| 1 BCH syndrome in carrier | 33 chips (10% of carrier) | +3-5 | 0/132, 0/66 (better) | holds (carrier-gated) | Cheapest if helper survives; hard-limit 6->8 |
| 2 LDPC/polar soft BP | 32 chips or PRF-derived | +6-9 (best) | 0/132 (distance) | holds | Dominant if LLRs informative |
| 3 Two-codebook binning | 16 chips | +3-4 standalone, stacks with 2 | 0/132 x 0.02 | holds | Lowest risk, stacks |

All three respect the "no help to forger" constraint via syndrome/helper information-theoretic bound + keyed permutation/PRF: helper leaks <= n-k linear bits of keyed q, which attacker already approximates from E'. Distinct-label q are far in both Hamming and soft angle, so relaxed decoding conditioned on helper/bin does not create donor->recipient transfer.

Recommended order: test Proposal 2 first (CPU simulation, highest upside, no embed), then Proposal 1 as fallback if soft BP gains are confirmed but parity survival is poor, then Proposal 3 as low-risk stacking layer if FPR is the binding constraint.
