# WP1: distortion, morphology and causal-attribution challenge

JUDGMENT — PROPOSED, for Gate 1. Findings 3 and 4 motivate useful tests, but neither establishes a recoverable detection count. The strongest supported priority is the interaction between carrier, finite regeneration channel, writer objective, and post-write interference. A failure class at the reader does not identify which of K4–K8 caused it. Sources: `judge/JUDGE-FINDINGS.md:61-76`; `scripts/f5_latent_codec.py:175-260`; `research/encoder-transfer-20261019/final-study-20261025/phase-a/PHASE-A-REPORT.md:89-114`.

## Scope and locator conventions

SOURCE — All repository-relative paths below refer to this worktree, except `judge/`, which abbreviates `research/f5-components-20261101/judge/`. `MAIN` means `W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5`; `S2` means `MAIN/.thesis-build/dev-runs/20261025-0128-encoder-transfer-stage2b/results/stage2b-full/rows.jsonl`; `CHANNEL` means `MAIN/.thesis-build/dev-runs/20261030-regen-channel/report.txt`; `A` means `research/encoder-transfer-20261019/final-study-20261025/phase-a/PHASE-A-REPORT.md`. These are the development sources specified in `research/f5-components-20261101/BRIEF.md:23-26`.

SOURCE — This note inspects code, committed reports and allowed development summaries. It runs only isolated standard-library scalar calculations and aggregation of saved writer/detector metadata. It generates no image, writer output, encoder pass or threshold choice. The only held-out evidence used is the frozen committed M2 report, read with `git show claude/m2-coco512-results:research/m2-coco512-results.md`, at line 97; no held-out journal or pixel is used.

## 1. Correct the K4–K8 map before attributing losses

| Component | Label and code-grounded correction | Consequence |
|---|---|---|
| K4 carrier | SOURCE — Four posterior-mode latent channels, radius `4 <= r < 32`, public weights `r/4`, disjoint keyed chip assignments and their own norm factors (`scripts/f5_latent_codec.py:44-85`). | DERIVED — These are latent DCT coordinates, not the RGB-opponent DCT bands in CHANNEL. A favorable pixel band does not directly select a favorable latent band. |
| K5 model/surrogate | SOURCE — Writer objective sees the pinned SD1.5 encoder on the current image; no decoder, noise injection or reverse diffusion occurs in `robust_pgd` (`scripts/f5_latent_codec.py:95-103,195-204`). | JUDGMENT — Split the component conceptually into reader representation and writer channel surrogate. An encoder ensemble and a noisy-codec objective address different deficiencies. |
| K6 optimizer | SOURCE — Initial write uses 150 normalized-gradient steps; one default refinement adds 50, so retained F5 uses 200 encoder-gradient steps, not 150 in total (`scripts/f5_latent_codec.py:201-212,218-220,246-250`; frozen parameters in `research/f5-r2-spec.md:8`). | DERIVED — A target margin is an objective, not a feasibility or convergence certificate. Final margins do not isolate optimization failure from subsequent corruption. |
| K7 allocation | SOURCE — The actual pixel displacement is projected into a global RGB L2 ball on each PGD call; its center is that call's input (`scripts/f5_latent_codec.py:184-186,208-214`). | DERIVED — Refinement58 is centered on the robust-plus-first-fragile RGB8 image, not the original. There is no source-centered projection after the full sequence. |
| K8 fragile/write order | SOURCE — `robust52 -> round -> fragile47 -> round -> refinement58 -> round -> fragile47 -> round`; the fragile hash and pattern are recomputed from the current image in each fragile call (`scripts/f5_latent_codec.py:230-250`). | DERIVED — Two fragile writes, not one, contribute to an interacting sequence. The final fragile write can damage robust margins after the last robust optimization. |

DERIVED — The `_activity_mask` docstring and optimizer docstring should not be read as defining a perceptual distortion constraint. The projection uses `delta.norm()`, while the mask changes the update geometry through `delta = mask * eta`; at retained `mask_power=0` it is all ones. Thus the historical H3 mask primarily reallocates the same global RGB energy, rather than enforcing a local visibility cap. Sources: `scripts/f5_latent_codec.py:164-172,185-186,193-212`; `research/f5-r2-spec.md:8`.

SOURCE — The profile's `embedding.colour="proportional"` is not what the F5 wrapper applies for its fragile writes: it adds the same luma displacement to all three RGB channels. Sources: `experiments/c4-v5-two-tier-regeneration-v1/profile.json:29-33`; `scripts/f5_latent_codec.py:234-245`.

JUDGMENT — F5 versus v5 is informative as a package comparison, but is not a clean intervention on K4 or K5 separately. It also changes writing, allocation, rounding interaction and achieved distortion. The same fragile primitive can receive different inputs and therefore write different hashes and residuals. Sources: `scripts/f5_latent_codec.py:230-250`; `research/method-amendment-v5.md:40,67-70,94`; `CHANNEL:110-120`.

## 2. Finding 3: nominal budgets are not distortion shares

DERIVED — With byte-scale RGB MSE, `MSE(P)=255^2*10^(-P/10)` and `RMS(P)=255*10^(-P/20)`. The quoted values imply:

| Quantity | Nominal MSE | Nominal RMS | Meaning |
|---|---:|---:|---|
| Final 44.96 dB | 2.075297 | 1.440589 | Conversion of the rounded cohort median PSNR, not per-source achieved tier energy |
| Fragile47 | 1.297419 | 1.139043 | Profile design target before rounding reserve and realized host-pattern cross term |
| Robust52 | 0.410280 | 0.640531 | Maximum initial floating-point RGB displacement energy in ideal arithmetic |
| Refinement58 | 0.103058 | 0.321026 | Maximum floating-point displacement relative to the intermediate input |

DERIVED — The nominal 47/44.96 and 52/44.96 ratios are 62.52% and 19.77%. Those arithmetic ratios reproduce the judge's rough percentages, but they are not an energy partition. Sources: `judge/JUDGE-FINDINGS.md:63`; `experiments/c4-v5-two-tier-regeneration-v1/profile.json:31`; `scripts/f5_latent_codec.py:186,231,249`; `CHANNEL:110`.

DERIVED — If `d_i` denotes each actual sequential stage increment, including quantization, then

`MSE_final = sum_i ||d_i||^2/N + 2 sum_{i<j} <d_i,d_j>/N`.

No inspected final-output report supplies these pairwise terms. Neither two fragile calls nor repeated attempts to restore the same fragile carrier are independent energy additions. Removing a stage changes the later starting point, hash, host rejection, rounding and gradient direction, so its counterfactual saving is not even necessarily its observed sequential squared norm. Sources: `scripts/f5_latent_codec.py:230-260`.

SOURCE — Fragile host rejection uses the *average-over-key* cost `a^2 + lambda^2*host_power`, explicitly documented that way (`scripts/revised_watermark_v4.py:762-779`). Before choosing `lambda,a`, the wrapper reserves `1/12` byte-squared for rounding (`scripts/revised_watermark_v5.py:848-852`; `research/tifs-20261028/design/r3-distortion-budget-bounds.md:21-25`).

DERIVED — For orthonormal fragile projections `h=Uy`, a sign pattern `w`, `K=320`, and `M` pixels, the realized pre-clipping target shift is `d=-lambda*h+a*w`. Its norm obeys

`||d||^2 = T*M - 2*lambda*a*<h,w>`,

where `T=1.297419-1/12=1.214086`. Hence profile47 is not a deterministic 47 dB bound on realized fragile RGB distortion. The second fragile report does not reveal `<h,w>`, and it overwrites the first report. Sources: `scripts/revised_watermark_v5.py:848-853,887`; `scripts/f5_latent_codec.py:243,260`; derivation and orthogonality conditions in `research/tifs-20261028/design/r3-distortion-budget-bounds.md:17-37`.

DERIVED — Four RGB8 conversions each allow up to 0.5 byte error per component. Independent uniform rounding with variance `1/12` is an assumption, not a deterministic guarantee, and rounding is substantial relative to a robust52 radius of only 0.641 byte RMS. Exact same-direction scaling through rounding is not available. Sources: `scripts/f5_latent_codec.py:231,245,250`; `research/tifs-20261028/design/r3-distortion-budget-bounds.md:53-72`.

DERIVED — A valid but loose ideal-arithmetic full-writer bound, accounting for three clipped passes per fragile call, is

`RMS_final <= r(52)+r(58)+2*sqrt(6*T)+4*0.5 = 8.359525`,

which implies only `PSNR_final >= 29.6872 dB`. This does not predict such poor quality; it shows that the nominal stage budgets alone cannot certify strict PSNR>35. The bound's orthonormal-row/projected-gradient argument, clipping treatment and unbounded-here numerical residual are documented in `research/tifs-20261028/design/r3-distortion-budget-bounds.md:19-72`; the same F5 calls are at `scripts/f5_latent_codec.py:230-250`.

SOURCE — The frozen M2 report says `both_match=0/90` at every regeneration strength and explains the fragile tier's intended breakage (`claude/m2-coco512-results:research/m2-coco512-results.md:97`). This is a frozen held-out observation, separate from the 60-source development calculations above.

JUDGMENT — That observation supports calling the fragile tier unhelpful for preserving *instance* acceptance through those measured regenerations. It does not establish that removing it leaves T3 semantic retention unchanged or improved, nor that its budget is wasted for clean instance detection or T4/T5. A robust-only design would need an explicitly changed full-decision interpretation; it cannot quietly preserve the old `both_match` claim. Sources: M2 report line 97; `scripts/f5_latent_codec.py:233-261`; `research/f5-encoder-amplified-latent.md:60-61`.

MEASURED — A read-only aggregation of the allowed Stage2 development detector metadata directly refutes universal extinction of the fragile channel. Keeping the last valid `ok`/`safety_blocked` record per `id`, then selecting successful F5 correct-owner calls, gives the following seed-level counts. Each cell has 180 planned calls; SD1.5 has the existing missing calls rather than assumed negatives. Source-majority numbers in parentheses use at least two positive seeds and denominator60.

| Cell | Instance found | Instance blind read | F=`both_match` | H=exact original instance code | S2 retained-row line range |
|---|---:|---:|---:|---:|---|
| SD1.5 .1 | 0 (0) | 0 (0) | 0 (0) | 0 (0) | 32711–33602 |
| SD1.5 .2 | 0 (0) | 0 (0) | 0 (0) | 0 (0) | 10606–11492 |
| SD1.5 .4 | 0 (0) | 0 (0) | 0 (0) | 0 (0) | 33607–34493 |
| SDXL .1 | 154 (52) | 108 (37) | 16 (5) | 8 (3) | 34498–35393 |
| SDXL .2 | 92 (30) | 60 (19) | 0 (0) | 1 (0) | 11496–12749 |
| SDXL .4 | 17 (5) | 5 (1) | 0 (0) | 0 (0) | 35398–36293 |
| K3 .2 | 45 (16) | 7 (2) | 25 (8) | 0 (0) | 38998–39893 |

SOURCE — Endpoint definitions are `scripts/m1b_e3_s1_analysis.py:70-83`: J is exact semantic-q plus semantic content match and has no instance requirement; H requires exact original h and blind instance read; F means the decision's `both_match`, which can use recomputed-only fallbacks. For example, `S2:10606` has J=true but H=D=F=false and instance found/read=false. This prevents interpreting the root accounting's positive J as fragile survival.

JUDGMENT — The new table shows substantial foreign-family *instance-channel detection*, some blind reading, and very little exact-original-h delivery. It does not establish useful T3 instance binding or safety: K3 has F25 despite H0, and SDXL .1 has F16 despite semantic C0 in the judge's table. Thus F and C/J are distinct endpoints, and neither F nor found is a substitute for H. Narrow the judge's Finding3 wording to the specific SD1.5/M2 setting, and retain K8 as an empirically interacting component. Sources: table above; `judge/loss-budget.json:40-60,72-83`; `scripts/m1b_e3_s1_analysis.py:75-80`.

## 3. Why the 2.2x argument cannot forecast SDXL success

DERIVED — `sqrt(MSE(44.96)/MSE(52))=2.249055`. This is a nominal initial-radius ratio under an ideal robust-only allocation with the rounded median final MSE as its target. It is not a measured amplitude gain. Counting both robust calls would instead give an illustrative ratio 2.010660 if their energies were orthogonal and fully used, or 1.498184 if their radii aligned. Neither condition is established. Sources: `scripts/f5_latent_codec.py:186,231,249`; `CHANNEL:110`.

DERIVED — Even for a single robust-only write, allocating the entire float budget to 44.96 dB does not guarantee final RGB8 PSNR44.96. The conservative single-rounding condition would require float RMS no larger than `1.440589-0.5=0.940589`, equivalent to 48.6628 dB. This is a sufficient worst-case bound, not a proposed budget or a claim that real rounding costs 0.5 RMS. Sources: `scripts/f5_latent_codec.py:231`; scalar model above.

SOURCE — The decoded reader score is a maximum over candidate patterns divided by the entire projection-vector norm; the recomputed score uses the same norm. The code performs these operations at `scripts/revised_watermark_v5.py:1178-1199`. SDXL .2's saved median decoded margin is -3.945784 (`judge/loss-budget.json:52-60`), yielding score 4.313543 at threshold 8.259327; its median recomputed score is 1.638809 at threshold 4.982033 (`S2:61`, threshold values; same judge JSON for margins).

DERIVED — For any positive `a`, scaling every chip projection `p -> a*p` leaves both normalized scores exactly unchanged. Under a hypothetically linear *signal* response `p(a)=b+a*d`, a fixed-pattern score is `w·(b+a*d)/||b+a*d||`, which is generally nonlinear in `a`. Decoding also changes the maximizing code. The decoded score includes a positive search maximum even without the intended mark, so multiplying 4.313543 by 2.249055 multiplies background and search bias as well as any signal. Sources: `scripts/revised_watermark_v5.py:1186-1199`.

JUDGMENT — Therefore the sentence “a linear reading would just clear it” needs a stronger caveat: linearity of the regeneration map would still not make this normalized maximum score linear. No SDXL source recovery forecast follows from that multiplication. This is in addition to the observed SDXL nonlinearity, not merely a restatement of it. Sources: `judge/JUDGE-FINDINGS.md:65`; `A:72-85`; preceding score identity.

## 4. K6 is unresolved, with observable final target shortfall

MEASURED — Read-only standard-library aggregation retained the last successful clean F5 writer record per `id` from S2. The 60 retained records lie at `S2:10186-10599`. Every retained report uses `(psnr_target_db,steps,target_margin,refine_rounds)=(52,150,4,1)` and verifies `both_match`. The following summarize the stored `embedding_report`, not fresh metrics:

| Stored field | Minimum | Median | Maximum |
|---|---:|---:|---:|
| `rgb_psnr_db` | 42.157332 | 44.961968 | 45.396696 |
| `margin_median` | 0.515033 | 1.036284 | 1.764448 |
| `margin_min` | -1.983745 | -0.703407 | 0.451894 |
| `negative_chips` | 0 | 17 | 72 |

MEASURED — All 60 final median margins are below target4; 56/60 final images contain negative chips. These are final post-fragile RGB8 measurements, as defined in `scripts/f5_latent_codec.py:251-260`. Reproducible reduction: stream S2 with `json.loads`; select `arm=='f5-r2'`, `channel=='clean'`, `status=='ok'`, and `embedding_report`; replace a dictionary entry by `id` on each matching row; take `statistics.median`, `min`, `max` and counts over the retained fields. The scan used `MAIN/.thesis-build/venv/Scripts/python.exe -I -`, completed in seconds and wrote nothing.

JUDGMENT — This is evidence that the final writer does not achieve its chipwise objective; it is not evidence that another optimizer would improve T3. Four explanations remain compatible: an infeasible target within robust52, insufficient 150/50-step convergence, RGB8 loss, and final fragile interference. Per-step loss and achieved radius, and pre-/post-rounding and pre-/post-fragile margins are absent from `embedding_report`. K6 should be ranked “unknown contribution, diagnostic evidence of shortfall”, not “shown adequate”. Sources: `scripts/f5_latent_codec.py:201-215,230-260`; measured table above.

## 5. Finding 4: what the saved channel measurements actually estimate

SOURCE — CHANNEL uses an orthonormal opponent transform with first axis `(R+G+B)/sqrt(3)`, then red-green and blue-yellow. It is not perceptual Y=`.299R+.587G+.114B`, which F5's mask uses. Sources: `research/coarse-lattice-20261030/measure_channel.py:37-42`; `scripts/f5_latent_codec.py:169`; `research/tifs-20261028/design/r3-distortion-budget-bounds.md:17`.

DERIVED — For a band-restricted mark residual `w=x_marked-x` and paired regenerated change `d=G(x_marked)-G(x)`, reported mark gain is the pooled projection slope

`g = sum <w,d> / sum ||w||^2`.

It is not `||d||/||w||`, a retained-energy fraction, a median over sources, a bit SNR, or F5's latent chip score. The script separately computes coherence `sum<w,d>^2/(sum||w||^2 * sum||d||^2)` but does not print it. Sources: `research/coarse-lattice-20261030/measure_channel.py:108-124`; `research/coarse-lattice-20261030/channel_report.py:81-94`.

SOURCE — In band64–96 the reported F5 slopes are 1.76 for SD1.5 .2, .35 for SDXL .2 and .60 for K3 .2, versus v5 .29/.33/.48 and VINE-R .44/.62/.74 (`CHANNEL:113,116,118,122,125,127,131,134,136`; band order at `CHANNEL:146`). These reproduce the proposal's selected-band numbers (`research/coarse-lattice-20261030/PROPOSAL.md:26-34`).

DERIVED — The *host* gain uses `sum<x,G(x)>/sum||x||^2`, not the differential mark-response experiment (`research/coarse-lattice-20261030/channel_report.py:55-57`). Comparing this slope to residual gain does not isolate “looking natural”: host magnitude, orientation, color, spatial distribution and nonlinear finite displacement differ simultaneously. At reported median quality, v5's MSE is about 6.47 times F5's, and VINE-R's about 9.59 times F5's, so the mark comparisons are not equal-distortion interventions either (`CHANNEL:110,119,128`; ratio formula `10^((44.96-P)/10)`).

SOURCE — The displayed F5 residual-energy shares in the equal-RGB axis are .13/.30/.26/.13/.03 for bands128–192/192–256/256–384/384–512/512–2048 (`CHANNEL:111`). These displayed rounded shares sum to .85 of total RGB residual energy; each is computed relative to total energy across all colors and bands (`research/coarse-lattice-20261030/channel_report.py:75-80`).

JUDGMENT — This concentration is consistent with a high-frequency fragile contribution, but cannot attribute .85 to K8: the robust optimizer, its refinement and RGB8 rounding can occupy the same pixel bands. The representative band64–96 is not where the displayed table places most final F5 pixel distortion, and pixel-band gain is not the carrier's detection endpoint. Sources: `CHANNEL:111-118`; `scripts/f5_latent_codec.py:230-250`.

SOURCE — For band32–48, unmarked total regeneration-residual RMS is 132.11/32.97/42.57 for SD1.5 .2, 98.20/28.32/37.63 for SDXL .2, and 78.07/24.80/31.67 for K3 .2, in equal-RGB/red-green/blue-yellow order (`CHANNEL:4,15,79,99`).

DERIVED — The equal-RGB/chroma RMS ratios span 2.47–4.01 in these three cells, not uniformly 3–4. They concern all unmarked regeneration change `(G(x)-x)`, which includes content-dependent systematic change, rather than independently sampled additive noise. Seed variance is a separate saved statistic. Sources: `research/coarse-lattice-20261030/measure_channel.py:96-105`; preceding table locators.

JUDGMENT — Lower chroma residual RMS is useful motivation, but alone does not imply greater usable information at equal visual quality. Candidate chroma gain, spatial correlations, host interference, flat-region visibility, and joint T4/T5 decisions remain required. Existing F4 already illustrates this distinction: its predeclared quality-matched r4 selection failed, while the stronger post-hoc r5 passed the written small-development gate with a larger perceptual cost (`research/f4-chroma-carrier.md:27-39,57-61`). The coarse-lattice report separately acknowledges actual T3 is unmeasured and visible flat-region blotches remain (`research/coarse-lattice-20261030/PROPOSAL.md:55,76-87`).

SOURCE — An additional diagnostic discrepancy: the channel report describes its water-filling capacity as using “gain from the best available mark response”, but the implementation uses clipped *host* gain, `gain[c]`, rather than `resp_gain` (`research/coarse-lattice-20261030/channel_report.py:97-111`).

JUDGMENT — Those capacities must remain conditional scalar-channel illustrations, not measured achievable bits or rigorous upper bounds for arbitrary marks under nonlinear regeneration. They cannot supply K4–K8 source-recovery ceilings. Sources: the implementation discrepancy above; `research/coarse-lattice-20261030/PROPOSAL.md:76`.

## 6. Surrogate mismatch: the strongest prior evidence is more specific than encoder mismatch

SOURCE — In Phase A's 12-source mechanism module, F5 residual encoder norm gain is 15.0 for SD1.5, 392 for SDXL and 43.3 for K3, larger than their norm-matched Gaussian/Fourier controls. These norms use different encoders and preprocessing, so cross-encoder absolute magnitudes are not common score units. The report explicitly states encoder amplification transfers while survival does not (`A:89-97`).

SOURCE — Stagewise target-chip retention at .2, each a median relative to clean, is:

| Stage | SD1.5 | SDXL | K3 |
|---|---:|---:|---:|
| Mode codec | .98 | .66 | .72 |
| Noise-only decoded latent | .92 | .08 | .34 |
| Native output | .74 | .08 | .17 |

SOURCE — Table locators are `A:99-107`. The same report explicitly calls these paired descriptive comparisons “not causal evidence” (`A:114`).

DERIVED — Ratios of these *reported medians* are .08/.66=.121 for SDXL noise-only versus mode-codec, .92/.98=.939 for SD1.5, and .34/.72=.472 for K3. They are not medians of per-source ratios. This descriptive contrast puts much of the SDXL decline after its codec stage, whereas K3 has additional native-stage decline. Sources: `A:103-107`.

SOURCE — The finite-change SDXL chip response and tangent are nearly orthogonal: cos .047/.016/.013 and tangent-to-change norm ratio 7.7/14.8/14.2 at .1/.2/.4; SD1.5 is substantially more linear (`A:72-85`).

JUDGMENT — Keep K4/K5 highly ranked as a *joint channel problem*, but reject “foreign encoders fail to amplify this residual” as the established mechanism. Plausible alternatives are noise-dependent decoder response, loss of alignment with the fixed SD1.5 reader, native processing beyond the codec, and normalization/host contamination. The stored observables do not distinguish these fully. Sources: `A:89-114`; `scripts/revised_watermark_v5.py:1186-1199`.

SOURCE — Approved F6 addresses a different surrogate: finite noisy codecs or predicted-clean latents, with unchanged F5 reader. The latter is not the full native regeneration attack and changes timestep exposure as well (`research/tifs-20261028/FINAL-REPORT.md:34-38`). Stage P has robust52/46/42/38 with fixed refinement58 and two fragile writes (`research/tifs-20261028/stage-p/PROTOCOL.md:21-30`); nominal budget equality does not guarantee achieved quality equality (`research/tifs-20261028/FINAL-REPORT.md:61`).

JUDGMENT — No result here justifies editing that approved package or replacing it with coarse lattice. Budget and write-order diagnostics can inform a later complementary test; current evidence does not predict which surrogate or carrier wins. Sources: `research/tifs-20261028/FINAL-REPORT.md:83`; `research/coarse-lattice-20261030/PROPOSAL.md:55,76`.

## 7. Honest ceilings and the proposed Gate 1 disagreements

DERIVED — For a new writer change in any of K4–K8, the only unconditional source-count ceiling from these 60-source results is 60/60. The *available headroom above current C* is shown below. This is not a predicted gain, does not erase missing rows, and is not a component-specific causal ceiling. Baselines come from `judge/loss-budget.json:2-83`.

| Development cell | Current F5 C /60 | Arithmetic maximum additional sources | Identifiable gain for K4, K5, K6, K7 or K8 separately |
|---|---:|---:|---|
| SD1.5 .1 | 60 | 0 | UNKNOWN (no positive count headroom) |
| SD1.5 .2 | 57 | 3 | UNKNOWN |
| SD1.5 .4 | 39 | 21 | UNKNOWN |
| SDXL .1 | 0 | 60 | UNKNOWN |
| SDXL .2 | 0 | 60 | UNKNOWN |
| SDXL .4 | 0 | 60 | UNKNOWN |
| K3 .2 | 5 | 55 | UNKNOWN |

DERIVED — “Lost” means neither existing reader test passed; it does not prove that all mark information is absent. Conversely, a present readable but wrong code can originate from upstream signal corruption, not only a faulty content check. These classes are valid operational partitions but are not mutually exclusive causal ownership assignments to components. Sources: `judge/loss_budget.py:35-49`; `scripts/revised_watermark_v5.py:1232-1257`.

SOURCE — Prior narrow failures must stay in the map: H1's alternate band8–28 pilot gave .4 counts13/17 versus13/18, and its informed weighting benefit was only1.1 dB; H3 mask0.5 improved mean LPIPS24% but reduced .4 counts from49/58 to38/58 and .5 from37/58 to23/59. These were SD1.5 stress experiments, not a universal rejection of new carrier geometries or visibility constraints (`research/f5-plateau-20261005.md:3,7-8`).

JUDGMENT — Requested Gate 1 rulings:

1. **Reject distortion-share attribution and universal fragile extinction as established.** Retain the nominal budget arithmetic, but label actual K7/K8 marginal savings UNKNOWN until intermediates and cross terms exist. The foreign-family instance found/read/H measurements require narrowing the claimed extinction to the measured SD1.5/M2 setting. Sources: sections 2–3; `scripts/f5_latent_codec.py:230-260`.
2. **Reject the decoded-score scaling forecast.** The 2.249 radius ratio may motivate a budget test, but yields no guaranteed or expected SDXL count. Sources: section 3; `scripts/revised_watermark_v5.py:1178-1199`.
3. **Correct the map and causal wording.** Add the second fragile write, refinement's new center, four rounding operations, and separate reader encoder from writer channel surrogate. Rank K4/K5 jointly; do not claim their individual losses are measured. Sources: sections 1 and 6.
4. **Do not dismiss K6.** Final chip margins miss target on all60 and are negative on56; attribution among solver, budget and postprocessing is unresolved. The cheapest informative later writer test should preserve identical settings while saving each intermediate and a loss/radius trace, before searching additional variants. Source: section 4.
5. **Treat morphology/chroma as conditional evidence.** Use exact opponent-axis and projection-gain definitions, report coherence and source dispersion, and keep true lattice T3 plus human flat-region quality MISSING. Sources: section 5; `research/coarse-lattice-20261030/PROPOSAL.md:55,76-87`.

JUDGMENT — Minimal evidence needed to discriminate the principal explanations on a later authorized server: save initial robust float/RGB8, first fragile RGB8, refinement float/RGB8 and final fragile RGB8; save actual per-stage RMS, pairwise inner products, saturation fraction and chip margins; compare retained, reduced-fragile and robust-only writers at measured final quality with separate endpoint labels; carry the same saved outputs through native cells, and retain clean/T4/T5 checks. No such writer or regeneration test is authorized or executed in this WP1 note. The current CPU restrictions are `research/f5-components-20261101/BRIEF.md:18-26`; the missing metadata follows from `scripts/f5_latent_codec.py:256-261`.
