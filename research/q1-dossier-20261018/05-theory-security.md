# Theory, attribution games and security limits

Prepared 2026-10-18 by Codex. Research-only WP5: source text and retained summaries inspected; no image, feature, detector, model, attack or experiment executed. The [evidence ledger](01-evidence-ledger.md) and [M2 review](01b-heldout-registry-m2-review.md) govern empirical numbers. The claims below support framing C, empirical attribution boundaries, with framing A, passive competing enrollment, as a narrower fallback. They do not make the current manuscript submission-ready.

## 1. Objects, roles and trust

Let `x` be a canonical source photograph, `a` a public owner identifier, and `w = W(x,a)` its published F5 r2 marked image. F5 optimizes RGB pixels through a pinned encoder. It is an image-domain writer with an encoder-space objective; neither latent insertion into the photograph's original generation process nor lightweight DCT-only extraction has been established.

The roles are a publishing/enrolling party, a registry service, a verifier, and a competing claimant. A record is

`r = (record_id, owner=a, q_r, D1(w), B1(w), profile/version metadata)`.

The registry preserves this association and supplies the reference descriptors to the verifier. **Registry integrity is assumed; truthful ownership is not inferred from an enrollment.** The competing-enrollment game deliberately allows beta to submit a derived image under beta's own identifier without modifying alpha's record. Assuming instead that a trusted authority refuses every dishonest ownership claim would remove the attack by assumption. Identity authentication, enrollment authorization, ordering policy, and evidence of first creation have not been evaluated as security mechanisms. Dynamic ownership, transfers and ledgers remain outside thesis scope.

OwnerID and the study's pattern derivation are public. The source threat model specifies no cryptographic secret in the baseline public-derived profile. “Keyed” describes pattern construction here, not secret-key authentication. The verifier also needs the pinned model/profile information, native owner-specific calls, and trusted enrolled descriptors. This side information must accompany every attribution claim.

The carried 32-bit content-derived code `q` is inherited from the semantic coding path; it is not a fresh uniformly random registry identifier. Native owner-specific detection yields `found`, `read`, and a decoded code `qhat_a`, or abstains. A record passes the pointer stage exactly when

`P_r(y) = found_a(y) AND read_a(y) AND [d_H(qhat_a(y),q_r) <= 6]`.

Thus “owner-and-record pointer” means an owner-conditioned candidate lookup. It need not identify a unique record. The actual code retains every matching record and every matching owner; a displayed `best_record` does not replace that accepted set. Source: `scripts/m1b_registry_analysis.py`, `native_q`, `qmatch`, `attribution`, read as text only.

### The frozen descriptor decision

D1 is the native fine-detail vector. B1 is the unit-normalized, mean-centered, 32 × 32 gray-layout vector made using BOX resizing. D1 is not CLIP, and B1 is not pHash. Let `d_r` and `b_r` be their cosine similarities to record `r`. For an available comparison, the frozen record check is

\[
F_r(y)=
\begin{cases}
\mathbf1[d_r\ge .0594367\ \land\ b_r\ge .90],&\text{D1 similarity available},\\
\mathbf1[b_r\ge .99],&\text{valid native D1 abstention},\\
0\text{ operationally, with outcome unknown},&\text{required query/record data absent}.
\end{cases}
\]

The final line is not an observed negative. A missing descriptor artifact is not permission to invoke the plain-image fallback. The reviewed E3 loader distinguishes an explicitly recorded D1 abstention from an absent/invalid cache. Conversely, the valid fallback really is a one-descriptor branch and must be included in every soundness statement; calling the entire rule “two factors always required” is incorrect (EV-72; `claude_round3_two_factor.py:rule`, `claude_two_factor_instance.py:Features`, `m1b_registry_analysis.py:vector`).

For a fixed available bank `R`, define accepted records and owners as

\[
\mathcal M(y;R)=\{r\in R:P_r(y)\land F_r(y)\},\qquad
\mathcal A(y;R)=\{\operatorname{owner}(r):r\in\mathcal M(y;R)\}.
\]

Fingerprint-only uses the identical descriptor rule and records, but omits `P_r`. This is a within-system ablation of candidate gating, not an externally matched fingerprint baseline.

## 2. Identity and channel definitions

For the real/synthetic look-alike endpoint, the frozen operational negative predicate is

\[
\operatorname{Different}(u,v)
 =\mathbf1[\operatorname{grayPSNR}(u,v)<18.126065828471827\text{ dB}].
\]

Gray PSNR uses the canonical gray images and `10 log10(255^2/MSE)`; equality or a higher PSNR is ambiguous for this endpoint. The cutoff is the fifth percentile of strength-.2 development regeneration PSNR, frozen before this confirmation (EV-72; approved plan §2 and frozen JSON). It is an operational separation criterion, not human-validated identity, a legal test, or an equivalence relation. A development percentile is not a population guarantee. It does not establish that exactly 95% of future legitimate regenerations lie above the cutoff, or that every below-cutoff image has a different semantic identity.

Regeneration provenance and negative eligibility are distinct. In the measured positive channel, `y = T_theta(w;s)` means the specified checkpoint, DDIM20 img2img configuration, empty prompt, guidance 1, and scheduled seed. Strength .2 is the primary E1 channel, with SD1.5 and SD2.1-base separately reported; stronger/settings-specific results are not replacements for it. “Admissible” here denotes membership in that protocol-defined channel, not a new held-out quality filter. Unavailable primary outputs count as misses. No post-hoc PSNR cutoff is imposed on E1 to discard difficult regenerations. Broader security would require a separate attacker-output fidelity/content condition; the current counts do not establish one for arbitrary transformations.

## 3. Attribution games and attacker access

These games formalize the reported events. They are not newly executed protocols or cryptographic security definitions with a proven negligible advantage.

| Game | Input and allowed action in the measured setting | Event and limitation |
|---|---|---|
| T3, regeneration recovery | Published `w`; specified nonadaptive regenerator, strength and seeds; no detector-feedback optimization | Recovery checks acceptance of alpha's enrolled record after regeneration. Removal/loss of alpha is distinct from acceptance of beta. E1 uses a majority of the three scheduled seeds per source. |
| T4, residual copy transfer | Marked donor, **clean donor**, and recipient; transfer the donor residual at scales .5 or 1 to fixed cyclic recipients | False binding is acceptance against the donor's record. This is a clean-donor-assisted residual test, stronger access than a marked-image-only extraction attack but narrower than every adaptive copy attack. Report carrier delivery separately where available. |
| T5, distinct-content confusion | Fixed unrelated and real look-alike pairs; look-alike eligibility uses the frozen PSNR predicate | E2 tests the descriptor predicate `F_r`, including its fallback. An accepted negative is a failed record-specificity endpoint. It does not by itself establish `P_r AND F_r`, hence is not a demonstrated whole-pipeline forgery. |
| Passive regenerate-and-enroll | Beta derives `z=T_theta(w;15)`, submits a beta record of `z`, then queries `z` or its scheduled further regeneration | Beta's q is the beta native **recomputed semantic_code** on `z`; no beta watermark is inserted. Compare accepted owner sets with and without the pointer, under the same record bank and descriptor rule. |

T4 access is verified in `scripts/m1b_registry_runtime.py`, lines 241–246: the transfer consumes recipient canonical pixels, embedded donor pixels and donor canonical pixels. Reading this code does not execute it. The passive E3 construction is specified in `scripts/m1b_registry_analysis.py:scenario`; its source comment and output metadata explicitly state no reembedding.

For the two labels alpha and beta, outcomes are:

- original-only: `A={alpha}`;
- unique competing owner: `A={beta}`;
- ambiguity: `A={alpha,beta}`;
- abstention: `A` is empty.

The declared E3 error is **`beta in A`**, including ambiguity and acceptance of a cross-source beta record. It is not merely `A={beta}`. Selection by first enrollment or highest score is not the evaluated attribution rule. A source-level record-correctness claim is also stricter than owner-only correctness when an owner has many records.

The measured passive adversary lacks beta re-marking and adaptive optimization, despite public method information. An **active re-marking** adversary could run the public writer on `z` for beta before enrollment, target alpha's identifier, search inputs/codes, or optimize against the verifier. None of those capabilities is measured by E3. Public derivation prevents interpreting owner detection as possession of a secret; however, it is not evidence that a specific full registry attack has already succeeded. An active attack's success still depends on the frozen descriptor check and enrollment policy. This distinction is essential before using “secure ownership” in a title.

Competing evidence has historical antecedents: Craver et al., §§IV–VIII, analyze invertibility/quasi-invertibility and ownership ambiguity. Passive regeneration/enrollment is a different construction within that broad problem, not a new discovery that conflicting claims can exist. [Primary paper](https://web.cs.ucla.edu/~miodrag/cs259-security/craver98resolving.pdf), `craver1998ownership`.

## 4. What correctness and soundness can mean

Fix the bank, enrollment procedure, channel distribution, owner candidate set, availability policy and negative relation before assigning a probability.

**Record correctness:** `Pr[r_alpha in M(T(w);R)]`. **Unique-owner correctness:** `Pr[A(T(w);R)={alpha}]`. These are different estimands: accepting alpha can coexist with an erroneous beta acceptance. The E1 source event is majority acceptance of the intended alpha record over the scheduled seeds, with gaps as misses. E1 does not alone estimate exclusive attribution or arbitrary per-query success. Without an independent identical-seed model, the majority rate is not the single-seed rate transformed by `3p^2-2p^3`.

**False record acceptance:** `Pr[P_r(Y) AND F_r(Y) | Y is an eligible negative for r]`. **Competing-owner soundness:** `Pr[beta in A(Y;R)]` in the stated competing-enrollment game. A corresponding correctness requirement is necessary: an always-abstaining verifier has zero competing-owner errors but no attribution utility.

The observed fixed-cohort frequencies estimate only these protocol-specific events, with the following evidence mapping:

| Endpoint | Supported reading | Unsupported reading |
|---|---|---|
| E1 | Joint pointer/record majority acceptance on the fixed strength-.2 channel, 277/300 and 280/300 (EV-50/51) | All-seed recovery, exclusive-owner accuracy, universal diffusion robustness, or independent-encoder transfer |
| E2 | Record-check specificity stress test: zero available unrelated/transfer accepts but 3/45 eligible real-pair accepts, in 2/16 shots (EV-53–55/71) | Three measured full-pipeline forgeries; a universal false-accept rate; successful overall confirmation |
| E3 | Zero any-beta acceptance in the observed complete-case pointer cells; comparison to a pointer-disabled arm under passive enrollment (EV-58–66/75) | Authenticated enrollment, active public-writer security, full-bank zero error, or cryptographic unforgeability |

A mathematical soundness claim would need a quantified adversary class and bounds for its induced negative distribution, including adaptive selection and enrollment. None is supplied by a finite zero count. A cryptographic guarantee additionally needs a security parameter, access model, secret or authentication assumption where relevant, and proof/reduction. This dossier supplies conditional empirical statements and elementary probability bounds, not that guarantee.

## 5. Uncertainty, clustering and missingness

For `k` successes in `n` independent identically distributed Bernoulli units, the one-sided Clopper–Pearson limits at error level `eta` are

`L = BetaQuantile(eta; k,n-k+1)` for `k>0`, otherwise 0;

`U = BetaQuantile(1-eta; k+1,n-k)` for `k<n`, otherwise 1.

For zero events, `U=1-eta^(1/n)`. Exact binomial coverage is conditional on the binomial model, not an assurance about selected, dependent or missing observations. The frozen convention is retained; no replacement interval is used to improve the result. Brown, Cai and DasGupta, §4.2.1, discuss Clopper–Pearson coverage/conservatism; see the session's [V2 card](02-literature/C8-theory/cards/brown2001binomial.md). Cluster dependence and few-cluster issues are explained by Cameron and Miller, §§II, IV–VI; their regression formulas are not automatically rare-event registry bounds. [Primary author manuscript](https://faculty.econ.ucdavis.edu/faculty/cameron/research/Cameron_Miller_JHR_2015_February.pdf), `cameron2015cluster`.

### Existing count bounds

These values come from WP1. E1/E2 acceptance numerators were cross-checked between retained summaries, not independently rescored from pixels or descriptors. WP1 independently recounted availability and E3 saved owner sets; this package does not upgrade that verification depth.

| Evidence | Unit and bound | Qualification |
|---|---|---|
| E1 SD1.5 / SD2.1 | Source, one-sided 95% lower .89313049 / .90459802 | 277/300 / 280/300; all attempted sources retained. Simultaneous two-model Bonferroni lower bounds .88718188 / .89891435 also exceed .85. Sources are shared across models; the adjustment does not require model independence. EV-50–52; review recount. |
| E2 real look-alikes | Shot incidence 2/16, upper .34382520; descriptive pair 3/45, upper .16338838 | The pair interval is not a cluster correction. Shots come from one film; even independent-shot sampling is an assumption, not demonstrated film-level generality. EV-55. |
| E2 T4 | 0/594 observed transfers, 297 donor clusters; conditional source upper .01003594 | 600 planned, six absent. Cyclic donor/recipient reuse can couple clusters. This is not an unconditional guarantee for all planned transfers. EV-54. |
| E2 unrelated | 0/3,343,081 scored; 3,408,600 planned; 65,519 missing | All 300 query banks have unknown comparisons. The 0/300 observed-cluster upper .00993608 is only a conditional sensitivity under independent sources and the tested observed bank. It is not a complete-bank guarantee or a million-independent-trial bound. EV-53. |
| E3 pointer | Zero any-beta per cell, `n=294,294,294,293,297,297,297,297` | Per-cell upper 1.0036%–1.0172%; eight-cell Bonferroni upper 1.6943%–1.7172%, conditional on evaluability and the observed bank. Do not pool cells. EV-58–66. |

E3 cell order throughout is SD1.5 .2 exact/.2 further/.4 exact/.4 further, then the same four SD2.1 cells. Fingerprint-only any-beta counts are **294, 293, 294, 263, 297, 296, 297, 265** in those cells (EV-75). “Up to 75 wrong” counts unique-beta outcomes alone and understates the declared error predicate. Ambiguity is still not a unique attacker assignment. Pointer utility declines: at .4 further regeneration only 81/293 and 81/297 receive alpha, with 212 and 216 abstentions (EV-62/66).

The strict frozen E3 completeness gate remains false: all 2,400 scheduled rows are unknown under full-bank requirements (EV-70; review recount). The pre-result approved complete-case reading requires the query, native calls and its own alpha/beta records, yielding the displayed denominators. It cannot certify absent cross-source beta records. Adding an available record can only add to the accepted-owner set under the fixed per-record rule; deleting an unavailable beta can suppress precisely the error being measured. Therefore missing beta records are not harmless merely because own-pair checks exist or original-record E2 comparisons showed zero.

The all-pairs design has two-way reuse: sources supply queries and references, transformations share sources, and every query uses essentially the same bank. Conditioning on a bank can define a useful risk for that bank; it does not create independent draws when the queries themselves helped form it. A source/shot incidence table is more honest than a pair-level CP claim, but does not remove all dependence or establish random population sampling. Safety blocks and failed markings are structured missingness, not demonstrated missing-at-random exclusions (EV-67/68).

The eight-cell Bonferroni calculation is a transparent desk-analysis sensitivity, not a new preregistered gate or a correction for every claim in the article. It addresses those eight marginal intervals only. Repeated seeds, two E1 models, E2 families, several strengths, bank candidates and exploratory method selection are distinct multiplicity issues. No familywise claim covering all of them is made. Missingness and target-population uncertainty remain after an interval adjustment.

## 6. Pointer capacity: calculations under explicit assumptions

The following are **analytic reference calculations, not measured properties of q**. Suppose stored codes and a fresh query code are independent uniform 32-bit strings. Write `M=2^32` and let `N` be the number of stored records in one owner-conditioned lookup domain.

The probability that some two of `N` stored codes are exactly equal is

\[
1-\prod_{j=0}^{N-1}(1-j/M)
\approx 1-\exp[-N(N-1)/(2M)].
\]

For one fresh code, exact-match probability against that bank is `1-(1-1/M)^N`. This is a different question from the birthday event. The actual radius-six lookup has ball volume

\[
V(32,6)=\sum_{j=0}^{6}{32\choose j}=1{,}149{,}017,
\qquad p_6=V/M=0.0002675263676792383.
\]

Under the independent uniform reference model, a fresh query has expected `N p_6` candidates and probability `1-(1-p_6)^N` of at least one. These numbers condition on having a decoded query code; they are not native owner-detection false-positive probabilities.

| N stored records | Any exact stored-code collision, birthday approximation | Fresh exact query hit | Fresh radius-six query hit | Expected radius-six candidates |
|---:|---:|---:|---:|---:|
| 100 | .00000115251 | .0000000232831 | .0264014 | .02675 |
| 300 | .0000104424 | .0000000698492 | .0771316 | .08026 |
| 1,000 | .000116292 | .000000232831 | .234757 | .26753 |
| 10,000 | .0115729 | .00000232830 | .931136 | 2.67526 |
| 100,000 | .687809 | .0000232828 | >.99999999999 | 26.75264 |
| 1,000,000 | approximately 1 | .000232804 | approximately 1 | 267.52637 |

Radius-six random matching provides about `-log2(p_6)=11.868` bits of rejection against one uniformly random code, not 32-bit exact matching and not cryptographic security. Even an intentionally designed binary code with disjoint radius-six decoding balls has sphere-packing upper bound `floor(2^32/V)=3,737` codewords; the content-derived q dictionary is not such a code. This is an elementary capacity upper bound, not an attainable design claim or a recommendation to change the method.

Actual q values derive from content and owner-conditioned projections. Similar content and repeated versions can have correlated, biased codes; a single fixed projection bank is not fresh randomness per query. For iid codes with distribution `p(q)`, exact pair collision probability is `sum_q p(q)^2`, and radius-six probability is `sum_{u,v} p(u)p(v) 1[d_H(u,v)<=6]`. Conditional/adaptive queries need their joint distribution instead. Without measured or proved entropy/separation assumptions, the uniform table does not bound the actual registry. Public code generation also permits adversarial search; it does not provide unpredictable identifiers.

Neither owner multiplicity nor repeated record/query attempts comes free. Separate owner-specific native calls create additional hypotheses; multiple records within an owner create additional content checks. No present result establishes a registry-size-independent false attribution rate.

## 7. The correct conjunction bound

For one false record, write `P` for pointer eligibility and `F` for the full frozen descriptor rule, including fallback. With no independence assumption,

\[
\Pr(P\cap F)\le\min\{\Pr(P),\Pr(F)\},
\qquad
\Pr(P\cap F)=\Pr(P)\Pr(F\mid P).
\]

Thus a record check is a genuine extra acceptance condition even when pointer codes collide. It never turns a rejected descriptor comparison into an accepted one. **This logical intersection is the valid sense in which the check protects against collisions; it does not mean the two errors are statistically independent.** Do not substitute `Pr(P)Pr(F)` or multiply D1 and B1 marginal false-accept rates. Shared content, thresholds and adaptive selection can strongly correlate them.

For `N` false records,

\[
\Pr(\exists r:P_r\cap F_r)
\le\min\left\{1,\sum_{r=1}^N\Pr(P_r\cap F_r)\right\}
\le\min\left\{1,\sum_{r=1}^N\min[\Pr(P_r),\Pr(F_r)]\right\}.
\]

A sharper conditional statement is possible only if justified: if for every realized selected-candidate set `C` and each `r in C`, `Pr(F_r | C) <= epsilon_r(C)` under the actual negative/enrollment process, then the query risk is at most `E[min(1,sum_{r in C} epsilon_r(C))]`. A bound measured on unrelated pairs is not automatically valid after q-based selection, among same-shot neighbors, for arbitrary records or after an attacker searches outputs. No such uniform conditional bound has been proved here.

Let `H` denote valid D1 abstention, `D` its passing threshold when present, and `B_t` a B1 pass at threshold `t`. Then

`F = (not H AND D AND B_.90) OR (H AND B_.99)`

is a union of disjoint branches. Consequently

`Pr(F) = Pr(not H,D,B_.90) + Pr(H,B_.99)`.

The fallback contribution cannot be discarded, and `H` can depend on content or attacker choices. A small joint-branch error does not bound the fallback. Missing-artifact uncertainty is separate from `H`. Future correctness/soundness statements must cover both valid branches and missingness; the empirical E2 rule does so only for its observed test distribution.

## 8. Encoder amplification: hypothesis, not proof

For a small pixel perturbation `delta`, a first-order approximation is `E(x+delta)-E(x) approximately J_E(x) delta`. Optimizing RGB pixels against encoder-space chip margins can align `delta` with directions that have substantial gain through the known encoder. This makes a carrier hypothesis plausible while preserving F5's image-domain status. The approximation alone does not show that denoising retains the particular pattern, that the detector recovers it, or that a registry verifies the correct instance.

Zhao et al., Theorem 4.3, bound false-negative error for an attack of the form `A(phi(x)+N(0,sigma^2 I))` by

\[
\epsilon_2\ge\Phi\left(\Phi^{-1}(1-\epsilon_1)-L_{x,w}\Delta/\sigma\right).
\]

Increasing the watermark-direction encoder gain can weaken this removal lower bound. A weak or vacuous bound is **not a lower bound on watermark survival**, and does not prove an attack fails. For the scaled diffusion noising step, the separation ratio becomes `L Delta sqrt(alpha/(1-alpha))`; matching an actual attack to the theorem's observation/noise assumptions matters. Appendix C.6 explicitly cautions that input-dependent VAE variance prevents direct application of the fixed-noise theorem to arbitrary VAE sampling. [Primary v3, §§4.1–4.2 and Appendix C](https://arxiv.org/html/2306.01953v3), `zhao2024provablyremovable`.

The theorem concerns distinguishing attacked marked from attacked unmarked distributions. Registered-image matching can succeed on content even when those distributions are indistinguishable. Conversely, a registry does not automatically evade a theorem merely because it is extra information: applying the theorem would require a matched model of what auxiliary registry information is fixed or revealed in the two hypotheses. Neither the theorem nor E1 proves ownership soundness of the hybrid.

Failure modes remain hypotheses requiring later evidence:

- A separately trained encoder may not amplify the same direction, or may move energy into coordinates the denoiser suppresses.
- A robustified encoder or an adaptive encoder-aware regeneration strategy may reduce mark-specific gain while retaining useful content; its quality/security trade-off is unknown here.
- Larger noise, repeated regeneration or content drift can preserve enough image meaning while losing pointer recovery or record specificity. E3's stronger-regeneration abstention demonstrates an operating-point limit, not its unique cause (EV-62/66).
- Known writer/detector access can support active re-marking or optimization of acceptance. Passive E3 does not address that access.
- Carrier recovery may survive while descriptor separation fails, as the distinct E1/E2 endpoints already show; repairing one does not prove the other.

SD2.1-base does not settle the first failure mode. The [Q-VAE analysis](02-literature/Q-VAE.md) documents shared encoder ancestry: the SDXL authors describe SD2.x's autoencoder change as decoder fine-tuning, whereas SDXL's autoencoder was trained from scratch. Unequal serialized local full-VAE hashes do not prove different encoder tensors after dtype conversion. The supported wording is **unseen diffusion checkpoint with shared encoder ancestry**. [SDXL §2.4, Table 3](https://arxiv.org/html/2307.01952#S2.SS4). An independently trained encoder, robustified/adaptive channel and active re-marking are future questions, **NOT RUN**, without an implementation or execution plan here.

## 9. Cryptographic tools do not supply the missing identity relation

Secure sketches and fuzzy extractors address noisy recovery and residual entropy. Their correctness region and secrecy assumptions do not establish that legitimate regenerations and different same-shot images occupy separable feature neighborhoods. Public images, public helper data and adversary knowledge must enter any entropy model; hashing a publicly reproducible descriptor does not create secret entropy. Dodis et al., §§3.1–3.2 and Theorem 5.1, give the relevant definitions and Hamming construction. [Primary author manuscript](https://www.cs.bu.edu/~reyzin/papers/fuzzy.pdf), `dodis2008fuzzy`.

A signature on a registry statement could authenticate its issuer and content under a separate key/trust model. It would not make a false statement true, prove image creation, establish legal title, or resolve D1+B1's look-alike acceptance. These are conceptual distinctions only; no cryptographic replacement, registry policy, key infrastructure or ownership-transfer mechanism is proposed as completed work.

## 10. Defensible theory statement for the article

“The system combines an owner-conditioned watermark candidate gate with a trusted enrolled-record check. Its acceptance event is their intersection, so candidate-code collisions need not cause attribution; no independence or multiplicative error reduction is assumed. The measured evidence is conditional on the fixed registry, regeneration channel, availability rule and operational negative definition. Pointer gating disambiguated passive competing enrollment in the observed cases, while the frozen descriptor check failed on some eligible same-shot negatives and stronger regeneration increased abstention. These results bound an empirical operating point and do not establish authenticated ownership or active-forgery security.”

### Audit trail for this package

Read once: authoritative MAIN STATE, then WP5 brief; ledger, review/recount and counts artifact; WP3; Q-VAE; C8 cards and relevant C2/C3 cards; frozen confirmation plan/JSON; method/threat text and the named source functions. No protected or shared file was edited. Primary-source opens on 2026-10-18 succeeded for Zhao v3, Dodis's author PDF, SDXL HTML, Cameron–Miller's author PDF and Craver's published PDF. Brown's mirrored full-text open returned an error; its statement above relies on the existing session V2 card and exact locator, not a claimed fresh successful inspection. No new literature search was performed, and no V-level was upgraded.

Numeric work used only MAIN `.thesis-build/venv/Scripts/python.exe` with Python `math`, for analytic 32-bit collision/Hamming-ball expressions and zero-count CP formulas. The zero-count bounds reproduce the existing review artifact; nonzero-count bounds are imported from WP1. No outcome was newly scored. Hypothetical registry-size table entries are explicitly separate from EV empirical evidence. All future tests in this file are **NOT RUN**.
