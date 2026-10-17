# Registry verification development results

**Fresh primary evaluation (amended development evidence):** saved `development_pass` = **no**; completeness = **yes**; descriptor = **D1**. SD1.5/.2 source-majority F_R = **30/40**; SD2.1/.2 = **32/40**; observed false accepts = **0**. Frozen method **f5-r2** remains unchanged, with no descriptor rescue. This result takes precedence over the earlier screen pass. It uses the post-hoc calibration, pre-evaluation availability amendment `posthoc-calibration-pre-evaluation-verified-native-D1-weak-detail-abstention-v1` and frozen calibration thresholds; it is development evidence, not held-out confirmation. Expected safety-blocked negatives remain unresolved.

| Primary cell | F_R seeds | F_R source majority | Fingerprint seeds | Fingerprint source majority |
| --- | --- | --- | --- | --- |
| sd15/0.1 | 105/120 | 35/40 | 105/120 | 35/40 |
| sd15/0.2 | 89/120 | 30/40 | 89/120 | 30/40 |
| sd15/0.4 | 20/120 | 7/40 | 23/120 | 8/40 |
| sd21/0.1 | 111/120 | 37/40 | 111/120 | 37/40 |
| sd21/0.2 | 96/120 | 32/40 | 96/120 | 32/40 |
| sd21/0.4 | 23/120 | 8/40 | 26/120 | 9/40 |

At .2, the deficits to the fixed 36/40 criterion are 6 sources for SD1.5 and 4 for SD2.1. Real near-duplicate fingerprint false accepts: 4/13; pointer-plus-registry false accepts: 0/13. This panel has 11 finite cosines, 2 verified native abstentions and 0 unknown comparisons. All 13 near-pair evaluation rows have pointer_candidate=false: these are original unmarked frames in a 1:1 descriptor panel, not a fully enrolled marked 1:N near-duplicate database. Zero registry accepts therefore does not establish instance discrimination conditional on a valid pointer. These observed controls do not establish a population false-positive rate.

Screen status: **screen_pass_hypothesis**. Chosen step-1 method: **f5-r2**. Descriptor selected by the fixed D1-then-D2 rule: **D1**. Advance to fresh calibration/evaluation: **yes**.

This method adds detector side information: access to a trusted, available registry holding each published marked image’s owner, record ID, native q/h and continuous descriptor vectors. Registry trust, availability and descriptor privacy are limitations. Ownership transfer, rights management and ledgers remain outside thesis scope.

The real near-duplicate panel uses 20 fixed different-frame pairs from one licensed Tears of Steel live-action footage collection, split 7/13 for calibration/evaluation. Separate photographs define different instances here. Fixed scene-linear clipping and sRGB conversion can remove detail; verified abstentions do not demonstrate content discrimination. This narrow panel is not a representative population sample.

The semantic mark is an owner-and-record pointer. F_R requires a found/read pointer, a record within the native q radius, and correct-record identification above the descriptor threshold. Fingerprint-only search omits the pointer. The screen uses 24 consulted development sources per method (N=24), not held-out data. Thresholds are nextafter above the maximum observed primary negative and are exploratory.

Native q radius: 6. Human visual admissibility: missing.

## Descriptor thresholds and fixed screen gate

| Descriptor | Tau | Maximum negative | Observed negatives | Observed false accepts | Decision | Pass | Execution/descriptor missing | Unresolved blocked negative pairs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D1 | 0.0594367 | 0.0594367 | 43917 | 0 | pass | yes | 0 | 345 |
| D2 | 0.991147 | 0.991147 | 43917 | 0 | fail | no | 0 | 345 |
| D3 | 0.998747 | 0.998747 | 43917 | 0 | fail | no | 0 | 345 |

D1 is primary. D2 becomes primary only after a decisive D1 failure; D3 is descriptive. The chosen method must reach at least 21/24 source majorities at .2 on both SD1.5 and SD2.1, with zero observed false accepts. Safety blocks are failed positive slots, while their negative comparisons stay unresolved. Execution errors are not hidden as safety blocks. Missing descriptive PP1 results do not change the primary gate.

## Per-cell discrimination, detection and identification

Descriptor TPR and F_R entries use the fixed planned-seed denominator; known/planned exposes unavailable similarities. Source-majority F_R requires at least two successful seeds. Clean/VAE conditions use one observation per source. AUC and maximum-negative comparisons use the pooled observed primary negatives.

| Descriptor | Method/model/strength | AUC | Minimum positive | Maximum negative | Margin | Known/planned | Descriptor TPR | Correct-record F_R | Majority F_R | Fingerprint correct | Fingerprint wrong accept | Blocked | Unknown |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D1 | e3-s1/clean/None | 1 | 1 | 0.0594367 | 0.940563 | 24/24 | 24/24 | 24/24 | 24/24 | 24/24 | 0 | 0 | 0 |
| D1 | e3-s1/sd15_vae/None | 1 | 0.7317 | 0.0594367 | 0.672263 | 24/24 | 24/24 | 24/24 | 24/24 | 24/24 | 0 | 0 | 0 |
| D1 | e3-s1/sdxl_vae/None | 1 | 0.806113 | 0.0594367 | 0.746676 | 24/24 | 24/24 | 21/24 | 21/24 | 24/24 | 0 | 0 | 0 |
| D1 | e3-s1/sd15/0.1 | 1 | 0.640467 | 0.0594367 | 0.58103 | 70/72 | 70/72 | 70/72 | 23/24 | 70/72 | 0 | 2 | 0 |
| D1 | e3-s1/sd15/0.2 | 1 | 0.516615 | 0.0594367 | 0.457178 | 70/72 | 70/72 | 70/72 | 23/24 | 70/72 | 0 | 2 | 0 |
| D1 | e3-s1/sd15/0.4 | 1 | 0.328056 | 0.0594367 | 0.268619 | 72/72 | 72/72 | 71/72 | 24/24 | 72/72 | 0 | 0 | 0 |
| D1 | e3-s1/sd21/0.1 | 1 | 0.671968 | 0.0594367 | 0.612531 | 72/72 | 72/72 | 72/72 | 24/24 | 72/72 | 0 | 0 | 0 |
| D1 | e3-s1/sd21/0.2 | 1 | 0.535283 | 0.0594367 | 0.475846 | 72/72 | 72/72 | 72/72 | 24/24 | 72/72 | 0 | 0 | 0 |
| D1 | e3-s1/sd21/0.4 | 1 | 0.333257 | 0.0594367 | 0.27382 | 72/72 | 72/72 | 69/72 | 24/24 | 72/72 | 0 | 0 | 0 |
| D1 | f5-r2/clean/None | 1 | 1 | 0.0594367 | 0.940563 | 24/24 | 24/24 | 24/24 | 24/24 | 24/24 | 0 | 0 | 0 |
| D1 | f5-r2/sd15_vae/None | 1 | 0.741669 | 0.0594367 | 0.682233 | 24/24 | 24/24 | 24/24 | 24/24 | 24/24 | 0 | 0 | 0 |
| D1 | f5-r2/sdxl_vae/None | 1 | 0.811712 | 0.0594367 | 0.752275 | 24/24 | 24/24 | 14/24 | 14/24 | 24/24 | 0 | 0 | 0 |
| D1 | f5-r2/sd15/0.1 | 1 | 0.659773 | 0.0594367 | 0.600336 | 72/72 | 72/72 | 72/72 | 24/24 | 72/72 | 0 | 0 | 0 |
| D1 | f5-r2/sd15/0.2 | 1 | 0.539337 | 0.0594367 | 0.4799 | 70/72 | 70/72 | 65/72 | 22/24 | 70/72 | 0 | 2 | 0 |
| D1 | f5-r2/sd15/0.4 | 1 | 0.34554 | 0.0594367 | 0.286103 | 71/72 | 71/72 | 45/72 | 15/24 | 71/72 | 0 | 1 | 0 |
| D1 | f5-r2/sd21/0.1 | 1 | 0.694732 | 0.0594367 | 0.635295 | 72/72 | 72/72 | 72/72 | 24/24 | 72/72 | 0 | 0 | 0 |
| D1 | f5-r2/sd21/0.2 | 1 | 0.557215 | 0.0594367 | 0.497779 | 72/72 | 72/72 | 70/72 | 24/24 | 72/72 | 0 | 0 | 0 |
| D1 | f5-r2/sd21/0.4 | 1 | 0.358882 | 0.0594367 | 0.299445 | 72/72 | 72/72 | 47/72 | 15/24 | 72/72 | 0 | 0 | 0 |
| D2 | e3-s1/clean/None | 1 | 1 | 0.991147 | 0.00885275 | 24/24 | 24/24 | 24/24 | 24/24 | 24/24 | 0 | 0 | 0 |
| D2 | e3-s1/sd15_vae/None | 0.999877 | 0.875465 | 0.991147 | -0.115682 | 24/24 | 0/24 | 0/24 | 0/24 | 0/24 | 0 | 0 | 0 |
| D2 | e3-s1/sdxl_vae/None | 0.99991 | 0.962915 | 0.991147 | -0.0282321 | 24/24 | 1/24 | 1/24 | 1/24 | 1/24 | 0 | 0 | 0 |
| D2 | e3-s1/sd15/0.1 | 0.999866 | 0.824786 | 0.991147 | -0.166361 | 70/72 | 0/72 | 0/72 | 0/24 | 0/72 | 0 | 2 | 0 |
| D2 | e3-s1/sd15/0.2 | 0.999863 | 0.689447 | 0.991147 | -0.3017 | 70/72 | 0/72 | 0/72 | 0/24 | 0/72 | 0 | 2 | 0 |
| D2 | e3-s1/sd15/0.4 | 0.999845 | 0.42335 | 0.991147 | -0.567797 | 72/72 | 0/72 | 0/72 | 0/24 | 0/72 | 0 | 0 | 0 |
| D2 | e3-s1/sd21/0.1 | 0.999866 | 0.856563 | 0.991147 | -0.134584 | 72/72 | 0/72 | 0/72 | 0/24 | 0/72 | 0 | 0 | 0 |
| D2 | e3-s1/sd21/0.2 | 0.999863 | 0.723577 | 0.991147 | -0.26757 | 72/72 | 0/72 | 0/72 | 0/24 | 0/72 | 0 | 0 | 0 |
| D2 | e3-s1/sd21/0.4 | 0.999841 | 0.422215 | 0.991147 | -0.568932 | 72/72 | 0/72 | 0/72 | 0/24 | 0/72 | 0 | 0 | 0 |
| D2 | f5-r2/clean/None | 1 | 1 | 0.991147 | 0.00885273 | 24/24 | 24/24 | 24/24 | 24/24 | 24/24 | 0 | 0 | 0 |
| D2 | f5-r2/sd15_vae/None | 0.999891 | 0.929902 | 0.991147 | -0.0612456 | 24/24 | 0/24 | 0/24 | 0/24 | 0/24 | 0 | 0 | 0 |
| D2 | f5-r2/sdxl_vae/None | 0.999923 | 0.956926 | 0.991147 | -0.0342216 | 24/24 | 5/24 | 5/24 | 5/24 | 5/24 | 0 | 0 | 0 |
| D2 | f5-r2/sd15/0.1 | 0.99987 | 0.863493 | 0.991147 | -0.127654 | 72/72 | 0/72 | 0/72 | 0/24 | 0/72 | 0 | 0 | 0 |
| D2 | f5-r2/sd15/0.2 | 0.999863 | 0.732484 | 0.991147 | -0.258663 | 70/72 | 0/72 | 0/72 | 0/24 | 0/72 | 0 | 2 | 0 |
| D2 | f5-r2/sd15/0.4 | 0.999848 | 0.426952 | 0.991147 | -0.564195 | 71/72 | 0/72 | 0/72 | 0/24 | 0/72 | 0 | 1 | 0 |
| D2 | f5-r2/sd21/0.1 | 0.999871 | 0.839815 | 0.991147 | -0.151332 | 72/72 | 0/72 | 0/72 | 0/24 | 0/72 | 0 | 0 | 0 |
| D2 | f5-r2/sd21/0.2 | 0.999864 | 0.69133 | 0.991147 | -0.299817 | 72/72 | 0/72 | 0/72 | 0/24 | 0/72 | 0 | 0 | 0 |
| D2 | f5-r2/sd21/0.4 | 0.999841 | 0.422756 | 0.991147 | -0.568391 | 72/72 | 0/72 | 0/72 | 0/24 | 0/72 | 0 | 0 | 0 |
| D3 | e3-s1/clean/None | 1 | 1 | 0.998747 | 0.00125322 | 24/24 | 24/24 | 24/24 | 24/24 | 24/24 | 0 | 0 | 0 |
| D3 | e3-s1/sd15_vae/None | 0.999863 | 0.949514 | 0.998747 | -0.0492327 | 24/24 | 0/24 | 0/24 | 0/24 | 0/24 | 0 | 0 | 0 |
| D3 | e3-s1/sdxl_vae/None | 0.999863 | 0.982572 | 0.998747 | -0.016175 | 24/24 | 0/24 | 0/24 | 0/24 | 0/24 | 0 | 0 | 0 |
| D3 | e3-s1/sd15/0.1 | 0.999863 | 0.91866 | 0.998747 | -0.0800871 | 70/72 | 0/72 | 0/72 | 0/24 | 0/72 | 0 | 2 | 0 |
| D3 | e3-s1/sd15/0.2 | 0.999863 | 0.858816 | 0.998747 | -0.139931 | 70/72 | 0/72 | 0/72 | 0/24 | 0/72 | 0 | 2 | 0 |
| D3 | e3-s1/sd15/0.4 | 0.999863 | 0.778425 | 0.998747 | -0.220321 | 72/72 | 0/72 | 0/72 | 0/24 | 0/72 | 0 | 0 | 0 |
| D3 | e3-s1/sd21/0.1 | 0.999863 | 0.924168 | 0.998747 | -0.0745783 | 72/72 | 0/72 | 0/72 | 0/24 | 0/72 | 0 | 0 | 0 |
| D3 | e3-s1/sd21/0.2 | 0.999863 | 0.860455 | 0.998747 | -0.138292 | 72/72 | 0/72 | 0/72 | 0/24 | 0/72 | 0 | 0 | 0 |
| D3 | e3-s1/sd21/0.4 | 0.999857 | 0.740481 | 0.998747 | -0.258266 | 72/72 | 0/72 | 0/72 | 0/24 | 0/72 | 0 | 0 | 0 |
| D3 | f5-r2/clean/None | 1 | 1 | 0.998747 | 0.00125322 | 24/24 | 24/24 | 24/24 | 24/24 | 24/24 | 0 | 0 | 0 |
| D3 | f5-r2/sd15_vae/None | 0.999863 | 0.963821 | 0.998747 | -0.0349262 | 24/24 | 0/24 | 0/24 | 0/24 | 0/24 | 0 | 0 | 0 |
| D3 | f5-r2/sdxl_vae/None | 0.999865 | 0.977299 | 0.998747 | -0.0214481 | 24/24 | 0/24 | 0/24 | 0/24 | 0/24 | 0 | 0 | 0 |
| D3 | f5-r2/sd15/0.1 | 0.999863 | 0.936037 | 0.998747 | -0.0627099 | 72/72 | 0/72 | 0/72 | 0/24 | 0/72 | 0 | 0 | 0 |
| D3 | f5-r2/sd15/0.2 | 0.999863 | 0.914928 | 0.998747 | -0.0838186 | 70/72 | 0/72 | 0/72 | 0/24 | 0/72 | 0 | 2 | 0 |
| D3 | f5-r2/sd15/0.4 | 0.999863 | 0.797106 | 0.998747 | -0.201641 | 71/72 | 0/72 | 0/72 | 0/24 | 0/72 | 0 | 1 | 0 |
| D3 | f5-r2/sd21/0.1 | 0.999863 | 0.934367 | 0.998747 | -0.06438 | 72/72 | 0/72 | 0/72 | 0/24 | 0/72 | 0 | 0 | 0 |
| D3 | f5-r2/sd21/0.2 | 0.999863 | 0.904234 | 0.998747 | -0.0945125 | 72/72 | 0/72 | 0/72 | 0/24 | 0/72 | 0 | 0 | 0 |
| D3 | f5-r2/sd21/0.4 | 0.999863 | 0.787177 | 0.998747 | -0.21157 | 72/72 | 0/72 | 0/72 | 0/24 | 0/72 | 0 | 0 | 0 |

## Negative controls and unresolved evidence

| Descriptor | C0 planned | C0 known | C0 pointer found | C0 registry accepts | C0 fingerprint correct | C0 fingerprint wrong | Wrong-owner pointer found | Wrong-owner registry accepts |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D1 | 912 | 904 | 0 | 0 | 904 | 0 | 0 | 0 |
| D2 | 912 | 904 | 0 | 0 | 39 | 0 | 0 | 0 |
| D3 | 912 | 904 | 0 | 0 | 7 | 0 | 0 | 0 |

Unmarked C0 queries matching their own source record are expected fingerprint matches. Their pointer/registry accepts are adverse provenance controls. The alpha-only screen has no beta records, so zero beta registry accepts alone is not evidence of arbitrary-owner security. Zero observed negative accepts does not establish a population false-positive rate.

D1: true missing evidence `[]`; descriptive PP1 missing evidence `[]`. Negative scope: Zero observed primary-negative acceptances only; blocked negative comparisons are unresolved. No population FPR claim.

D1 retained PP1 (descriptive): 27 observed rows; 0 descriptor accepts; 0 pointer-plus-descriptor donor accepts. This historical 12-source panel is excluded from the primary threshold fit.

D2: true missing evidence `[]`; descriptive PP1 missing evidence `[]`. Negative scope: Zero observed primary-negative acceptances only; blocked negative comparisons are unresolved. No population FPR claim.

D2 retained PP1 (descriptive): 27 observed rows; 0 descriptor accepts; 0 pointer-plus-descriptor donor accepts. This historical 12-source panel is excluded from the primary threshold fit.

D3: true missing evidence `[]`; descriptive PP1 missing evidence `[]`. Negative scope: Zero observed primary-negative acceptances only; blocked negative comparisons are unresolved. No population FPR claim.

D3 retained PP1 (descriptive): 27 observed rows; 0 descriptor accepts; 0 pointer-plus-descriptor donor accepts. This historical 12-source panel is excluded from the primary threshold fit.

## Registry size, storage and measured lookup cost

| Descriptor | Method/model/strength | Minimum K | Median K | Maximum K |
| --- | --- | --- | --- | --- |
| D1 | e3-s1/clean/None | 1 | 2 | 7 |
| D1 | e3-s1/sd15_vae/None | 1 | 2 | 7 |
| D1 | e3-s1/sdxl_vae/None | 0 | 2 | 7 |
| D1 | e3-s1/sd15/0.1 | 0 | 2 | 7 |
| D1 | e3-s1/sd15/0.2 | 0 | 2 | 7 |
| D1 | e3-s1/sd15/0.4 | 0 | 2 | 7 |
| D1 | e3-s1/sd21/0.1 | 1 | 2 | 7 |
| D1 | e3-s1/sd21/0.2 | 1 | 2 | 7 |
| D1 | e3-s1/sd21/0.4 | 0 | 2 | 7 |
| D1 | f5-r2/clean/None | 1 | 2 | 7 |
| D1 | f5-r2/sd15_vae/None | 1 | 2 | 7 |
| D1 | f5-r2/sdxl_vae/None | 0 | 1 | 4 |
| D1 | f5-r2/sd15/0.1 | 1 | 1 | 7 |
| D1 | f5-r2/sd15/0.2 | 0 | 1 | 7 |
| D1 | f5-r2/sd15/0.4 | 0 | 1 | 7 |
| D1 | f5-r2/sd21/0.1 | 1 | 2 | 7 |
| D1 | f5-r2/sd21/0.2 | 0 | 1 | 7 |
| D1 | f5-r2/sd21/0.4 | 0 | 1 | 7 |
| D2 | e3-s1/clean/None | 1 | 2 | 7 |
| D2 | e3-s1/sd15_vae/None | 1 | 2 | 7 |
| D2 | e3-s1/sdxl_vae/None | 0 | 2 | 7 |
| D2 | e3-s1/sd15/0.1 | 0 | 2 | 7 |
| D2 | e3-s1/sd15/0.2 | 0 | 2 | 7 |
| D2 | e3-s1/sd15/0.4 | 0 | 2 | 7 |
| D2 | e3-s1/sd21/0.1 | 1 | 2 | 7 |
| D2 | e3-s1/sd21/0.2 | 1 | 2 | 7 |
| D2 | e3-s1/sd21/0.4 | 0 | 2 | 7 |
| D2 | f5-r2/clean/None | 1 | 2 | 7 |
| D2 | f5-r2/sd15_vae/None | 1 | 2 | 7 |
| D2 | f5-r2/sdxl_vae/None | 0 | 1 | 4 |
| D2 | f5-r2/sd15/0.1 | 1 | 1 | 7 |
| D2 | f5-r2/sd15/0.2 | 0 | 1 | 7 |
| D2 | f5-r2/sd15/0.4 | 0 | 1 | 7 |
| D2 | f5-r2/sd21/0.1 | 1 | 2 | 7 |
| D2 | f5-r2/sd21/0.2 | 0 | 1 | 7 |
| D2 | f5-r2/sd21/0.4 | 0 | 1 | 7 |
| D3 | e3-s1/clean/None | 1 | 2 | 7 |
| D3 | e3-s1/sd15_vae/None | 1 | 2 | 7 |
| D3 | e3-s1/sdxl_vae/None | 0 | 2 | 7 |
| D3 | e3-s1/sd15/0.1 | 0 | 2 | 7 |
| D3 | e3-s1/sd15/0.2 | 0 | 2 | 7 |
| D3 | e3-s1/sd15/0.4 | 0 | 2 | 7 |
| D3 | e3-s1/sd21/0.1 | 1 | 2 | 7 |
| D3 | e3-s1/sd21/0.2 | 1 | 2 | 7 |
| D3 | e3-s1/sd21/0.4 | 0 | 2 | 7 |
| D3 | f5-r2/clean/None | 1 | 2 | 7 |
| D3 | f5-r2/sd15_vae/None | 1 | 2 | 7 |
| D3 | f5-r2/sdxl_vae/None | 0 | 1 | 4 |
| D3 | f5-r2/sd15/0.1 | 1 | 1 | 7 |
| D3 | f5-r2/sd15/0.2 | 0 | 1 | 7 |
| D3 | f5-r2/sd15/0.4 | 0 | 1 | 7 |
| D3 | f5-r2/sd21/0.1 | 1 | 2 | 7 |
| D3 | f5-r2/sd21/0.2 | 0 | 1 | 7 |
| D3 | f5-r2/sd21/0.4 | 0 | 1 | 7 |

| Descriptor | Method | Records N | Minimum bytes/record | Maximum bytes/record | Total raw descriptor bytes | Missing vectors |
| --- | --- | --- | --- | --- | --- | --- |
| D1 | e3-s1 | 24 | 65536 | 65536 | 1572864 | 0 |
| D1 | f5-r2 | 24 | 65536 | 65536 | 1572864 | 0 |
| D2 | e3-s1 | 24 | 3072 | 3072 | 73728 | 0 |
| D2 | f5-r2 | 24 | 3072 | 3072 | 73728 | 0 |
| D3 | e3-s1 | 24 | 4096 | 4096 | 98304 | 0 |
| D3 | f5-r2 | 24 | 4096 | 4096 | 98304 | 0 |

Bytes refer to the saved normalized float64 vector only; q/h, record metadata, indexes and file/container overhead are additional. Screen scoring computes exhaustive N=24 cosine tables for impostor analysis. A prospective registry query filters owner/q and compares K candidates; fingerprint-only search compares N records.

Measured timing summary: `{"descriptor_disk_load_seconds": 0.0, "descriptor_extracted_images": 1600, "descriptor_extraction_seconds": {"D1": 258.1831375999809, "D2": 78.49097650001386, "D3": 499.24604760001785}, "descriptor_extraction_wall_seconds": 853.6247887999834, "lookup": {"cosine": {"calls": 144459, "seconds": 30.09324819997346}, "fingerprint": {"calls": 6048, "seconds": 0.01718020000407705}, "registry": {"calls": 6048, "seconds": 0.019770599999901606}}}`.

Host wall seconds. D1/D2/D3 extraction excludes model initialization; cosine scoring including cached-vector access, and owner/q filtering plus best-record selection, are measured separately. Screen scores are exhaustive for impostor analysis, not a simulated production latency. Saved per-invocation totals include resumes; cached images are not charged extraction twice.

## ROC artifacts and complete numeric evidence

[D1-roc.json](<W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/20261016-registry-step2-screen/D1-roc.json>), [D2-roc.json](<W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/20261016-registry-step2-screen/D2-roc.json>), [D3-roc.json](<W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/20261016-registry-step2-screen/D3-roc.json>). Standalone ROC SVG: missing (numeric ROC links remain available). The curves describe descriptor discrimination and omit pointer failures; F_R above includes pointer failures.

Complete native calls, all ordered impostor pairs, q-nearest flags, residual T4 and PP1 scores: [D1-scores.json](<W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/20261016-registry-step2-screen/D1-scores.json>), [D2-scores.json](<W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/20261016-registry-step2-screen/D2-scores.json>), [D3-scores.json](<W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/20261016-registry-step2-screen/D3-scores.json>).

Run provenance: [run.json](<W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/20261016-registry-step2-screen/run.json>); descriptor cache references: [descriptor-index.json](<W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/20261016-registry-step2-screen/descriptor-index.json>). Commit `764fa0d54dc4d92ff80d2bf3276cf485f8fd506e`; screen duration 1317.25 seconds; accounted step-2 duration 1317.25 seconds.

## Regenerate-and-enroll scenario

Status: **completed**. Registry size: 48 planned records. Alpha’s original publications are enrolled first; beta enrolls their seed-12 regenerated copies later, without embedding a new mark. Queries are the exact enrolled copy and its seed-13 further regeneration.

| Cell | Descriptor | Observed/planned | Pointer original owner | Wrong owner | Ambiguous | No attribution | Pointer original record | Fingerprint original record | Fingerprint both owners | Order can favor alpha |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sd15/0.2/exact_copy | D1 | 22/24 | 19 | 0 | 0 | 3 | 19 | 0 | 22 | 22 |
| sd15/0.2/exact_copy | D2 | 22/24 | 0 | 0 | 0 | 22 | 0 | 0 | 0 | 0 |
| sd15/0.2/exact_copy | D3 | 22/24 | 0 | 0 | 0 | 22 | 0 | 0 | 0 | 0 |
| sd15/0.2/further_regeneration | D1 | 22/24 | 16 | 0 | 0 | 6 | 16 | 0 | 22 | 22 |
| sd15/0.2/further_regeneration | D2 | 22/24 | 0 | 0 | 0 | 22 | 0 | 0 | 0 | 0 |
| sd15/0.2/further_regeneration | D3 | 22/24 | 0 | 0 | 0 | 22 | 0 | 0 | 0 | 0 |
| sd15/0.4/exact_copy | D1 | 23/24 | 14 | 0 | 0 | 9 | 14 | 0 | 23 | 23 |
| sd15/0.4/exact_copy | D2 | 23/24 | 0 | 0 | 0 | 23 | 0 | 0 | 0 | 0 |
| sd15/0.4/exact_copy | D3 | 23/24 | 0 | 0 | 0 | 23 | 0 | 0 | 0 | 0 |
| sd15/0.4/further_regeneration | D1 | 23/24 | 3 | 0 | 0 | 20 | 3 | 0 | 23 | 23 |
| sd15/0.4/further_regeneration | D2 | 23/24 | 0 | 0 | 0 | 23 | 0 | 0 | 0 | 0 |
| sd15/0.4/further_regeneration | D3 | 23/24 | 0 | 0 | 0 | 23 | 0 | 0 | 0 | 0 |
| sd21/0.2/exact_copy | D1 | 24/24 | 24 | 0 | 0 | 0 | 24 | 0 | 24 | 24 |
| sd21/0.2/exact_copy | D2 | 24/24 | 0 | 0 | 0 | 24 | 0 | 0 | 0 | 0 |
| sd21/0.2/exact_copy | D3 | 24/24 | 0 | 0 | 0 | 24 | 0 | 0 | 0 | 0 |
| sd21/0.2/further_regeneration | D1 | 24/24 | 17 | 0 | 0 | 7 | 17 | 0 | 23 | 23 |
| sd21/0.2/further_regeneration | D2 | 24/24 | 0 | 0 | 0 | 24 | 0 | 0 | 0 | 0 |
| sd21/0.2/further_regeneration | D3 | 24/24 | 0 | 0 | 0 | 24 | 0 | 0 | 0 | 0 |
| sd21/0.4/exact_copy | D1 | 24/24 | 15 | 0 | 0 | 9 | 15 | 0 | 24 | 24 |
| sd21/0.4/exact_copy | D2 | 24/24 | 0 | 0 | 0 | 24 | 0 | 0 | 0 | 0 |
| sd21/0.4/exact_copy | D3 | 24/24 | 0 | 0 | 0 | 24 | 0 | 0 | 0 | 0 |
| sd21/0.4/further_regeneration | D1 | 24/24 | 2 | 0 | 0 | 22 | 2 | 0 | 24 | 24 |
| sd21/0.4/further_regeneration | D2 | 24/24 | 0 | 0 | 0 | 24 | 0 | 0 | 0 | 0 |
| sd21/0.4/further_regeneration | D3 | 24/24 | 0 | 0 | 0 | 24 | 0 | 0 | 0 | 0 |

Original-owner uniqueness is distinct from selecting the original source record. Fingerprint matches to both owners are not unique owner attribution; preferring the earlier enrollment is an external registry-order rule. The native pointer is evaluated for alpha and beta here, so a zero wrong-owner rate in the alpha-only screen is not substituted for this scenario.

Native calls, all matching record IDs, cosine scores and enrollment-order choices: [rows.jsonl](<W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/20261016-registry-step2-enroll/rows.jsonl>). This scenario does not test re-embedding/T6 or arbitrary-owner security.

| Cell | Descriptor | Query observed | Query abstaining | Query unknown | Searchable/planned references | Searchable/planned beta references | Reference abstentions | Reference unknown | Beta abstentions | Beta unknown | Unique alpha with searchable own beta | Unique alpha with unsearchable own beta |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sd15/0.2/exact_copy | D1 | missing | missing | missing | missing/missing | missing/missing | missing | missing | missing | missing | missing | missing |
| sd15/0.2/exact_copy | D2 | missing | missing | missing | missing/missing | missing/missing | missing | missing | missing | missing | missing | missing |
| sd15/0.2/exact_copy | D3 | missing | missing | missing | missing/missing | missing/missing | missing | missing | missing | missing | missing | missing |
| sd15/0.2/further_regeneration | D1 | missing | missing | missing | missing/missing | missing/missing | missing | missing | missing | missing | missing | missing |
| sd15/0.2/further_regeneration | D2 | missing | missing | missing | missing/missing | missing/missing | missing | missing | missing | missing | missing | missing |
| sd15/0.2/further_regeneration | D3 | missing | missing | missing | missing/missing | missing/missing | missing | missing | missing | missing | missing | missing |
| sd15/0.4/exact_copy | D1 | missing | missing | missing | missing/missing | missing/missing | missing | missing | missing | missing | missing | missing |
| sd15/0.4/exact_copy | D2 | missing | missing | missing | missing/missing | missing/missing | missing | missing | missing | missing | missing | missing |
| sd15/0.4/exact_copy | D3 | missing | missing | missing | missing/missing | missing/missing | missing | missing | missing | missing | missing | missing |
| sd15/0.4/further_regeneration | D1 | missing | missing | missing | missing/missing | missing/missing | missing | missing | missing | missing | missing | missing |
| sd15/0.4/further_regeneration | D2 | missing | missing | missing | missing/missing | missing/missing | missing | missing | missing | missing | missing | missing |
| sd15/0.4/further_regeneration | D3 | missing | missing | missing | missing/missing | missing/missing | missing | missing | missing | missing | missing | missing |
| sd21/0.2/exact_copy | D1 | missing | missing | missing | missing/missing | missing/missing | missing | missing | missing | missing | missing | missing |
| sd21/0.2/exact_copy | D2 | missing | missing | missing | missing/missing | missing/missing | missing | missing | missing | missing | missing | missing |
| sd21/0.2/exact_copy | D3 | missing | missing | missing | missing/missing | missing/missing | missing | missing | missing | missing | missing | missing |
| sd21/0.2/further_regeneration | D1 | missing | missing | missing | missing/missing | missing/missing | missing | missing | missing | missing | missing | missing |
| sd21/0.2/further_regeneration | D2 | missing | missing | missing | missing/missing | missing/missing | missing | missing | missing | missing | missing | missing |
| sd21/0.2/further_regeneration | D3 | missing | missing | missing | missing/missing | missing/missing | missing | missing | missing | missing | missing | missing |
| sd21/0.4/exact_copy | D1 | missing | missing | missing | missing/missing | missing/missing | missing | missing | missing | missing | missing | missing |
| sd21/0.4/exact_copy | D2 | missing | missing | missing | missing/missing | missing/missing | missing | missing | missing | missing | missing | missing |
| sd21/0.4/exact_copy | D3 | missing | missing | missing | missing/missing | missing/missing | missing | missing | missing | missing | missing | missing |
| sd21/0.4/further_regeneration | D1 | missing | missing | missing | missing/missing | missing/missing | missing | missing | missing | missing | missing | missing |
| sd21/0.4/further_regeneration | D2 | missing | missing | missing | missing/missing | missing/missing | missing | missing | missing | missing | missing | missing |
| sd21/0.4/further_regeneration | D3 | missing | missing | missing | missing/missing | missing/missing | missing | missing | missing | missing | missing | missing |

A planned registry slot can lack a searchable descriptor. Unique alpha attribution with an unsearchable competing beta record is reported separately from uniqueness against a searchable competing record. Verified native weak-detail abstentions are deterministic rejections; genuine missing data remain unknown. Older runs without these availability fields display missing values, not measured zeros.

| Phase | Status | Rows |
| --- | --- | --- |
| enroll | input_unavailable | 3 |
| enroll | ok | 189 |
| evaluate | input_unavailable | 6 |
| evaluate | ok | 186 |

Available descriptor containers per observed query: minimum 46, maximum 48; planned N is not silently substituted for availability. Container availability is not D1 searchability; use the per-descriptor searchable counts above.

## Fresh construction and native-control availability

Fresh construction status: **completed**; method: **f5-r2**. Phase status: `{"embed": "completed", "sd15": "completed", "sd21": "completed"}`. These summaries use the latest complete journal event per identity, including failed or unavailable identities in the planned denominators.

| Split | Method | Clean observed/planned | Strict quality/planned | Strict quality unknown | Minimum finite PSNR dB | Infinite PSNR count | Minimum SSIM | Median LPIPS | Maximum LPIPS | Embedding time known/planned | Median embedding s | Maximum embedding s | Sum known embedding s | Clean latest status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| calibration | f5-r2 | 20/20 | 20/20 | 0 | 43.157 | 0 | 0.970594 | 0.0199532 | 0.0888606 | 20/20 | 38.453 | 38.657 | 767.998 | {"ok": 20} |
| evaluation | f5-r2 | 40/40 | 40/40 | 0 | 42.8454 | 0 | 0.947783 | 0.025829 | 0.0820028 | 40/40 | 38.5 | 38.735 | 1540.81 | {"ok": 40} |

Strict quality uses the recorded PSNR >35 dB, SSIM >.9 and LPIPS <.1 predicate. Reported extrema and embedding-time summaries use available measurements only; missing constructions are not quality successes. Clean quality is not matched to another method in this fresh chosen-method-only run. For F5, embedding_seconds is the recorded native bootstrap time; for E3 it includes the recorded supplier and writer durations. Model loading and detector/quality assessment time are included in run duration, not silently attributed to embedding.

| Split | Condition | Strength | Control | Known/planned calls | Observed A accepts | Unknown calls | Sources with observed A | Complete sources | Unresolved source clusters | Latest row status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| calibration | clean | missing | C0 native A | 20/20 | 0 | 0 | 0/20 | 20 | 0 | {"ok": 20} |
| calibration | clean | missing | C1 wrong-owner native A | 20/20 | 0 | 0 | 0/20 | 20 | 0 | {"ok": 20} |
| calibration | sd15 | 0.1 | C0 native A | 60/60 | 0 | 0 | 0/20 | 20 | 0 | {"ok": 60} |
| calibration | sd15 | 0.1 | C1 wrong-owner native A | 60/60 | 0 | 0 | 0/20 | 20 | 0 | {"ok": 60} |
| calibration | sd15 | 0.2 | C0 native A | 60/60 | 0 | 0 | 0/20 | 20 | 0 | {"ok": 60} |
| calibration | sd15 | 0.2 | C1 wrong-owner native A | 60/60 | 0 | 0 | 0/20 | 20 | 0 | {"ok": 60} |
| calibration | sd15 | 0.4 | C0 native A | 58/60 | 0 | 2 | 0/20 | 18 | 2 | {"ok": 58, "safety_blocked": 2} |
| calibration | sd15 | 0.4 | C1 wrong-owner native A | 60/60 | 0 | 0 | 0/20 | 20 | 0 | {"ok": 60} |
| calibration | sd21 | 0.1 | C0 native A | 60/60 | 0 | 0 | 0/20 | 20 | 0 | {"ok": 60} |
| calibration | sd21 | 0.1 | C1 wrong-owner native A | 60/60 | 0 | 0 | 0/20 | 20 | 0 | {"ok": 60} |
| calibration | sd21 | 0.2 | C0 native A | 60/60 | 0 | 0 | 0/20 | 20 | 0 | {"ok": 60} |
| calibration | sd21 | 0.2 | C1 wrong-owner native A | 60/60 | 0 | 0 | 0/20 | 20 | 0 | {"ok": 60} |
| calibration | sd21 | 0.4 | C0 native A | 60/60 | 0 | 0 | 0/20 | 20 | 0 | {"ok": 60} |
| calibration | sd21 | 0.4 | C1 wrong-owner native A | 60/60 | 0 | 0 | 0/20 | 20 | 0 | {"ok": 60} |
| evaluation | clean | missing | C0 native A | 40/40 | 0 | 0 | 0/40 | 40 | 0 | {"ok": 40} |
| evaluation | clean | missing | C1 wrong-owner native A | 40/40 | 0 | 0 | 0/40 | 40 | 0 | {"ok": 40} |
| evaluation | sd15 | 0.1 | C0 native A | 114/120 | 0 | 6 | 0/40 | 37 | 3 | {"ok": 114, "safety_blocked": 6} |
| evaluation | sd15 | 0.1 | C1 wrong-owner native A | 114/120 | 0 | 6 | 0/40 | 37 | 3 | {"ok": 114, "safety_blocked": 6} |
| evaluation | sd15 | 0.2 | C0 native A | 116/120 | 0 | 4 | 0/40 | 38 | 2 | {"ok": 116, "safety_blocked": 4} |
| evaluation | sd15 | 0.2 | C1 wrong-owner native A | 118/120 | 0 | 2 | 0/40 | 38 | 2 | {"ok": 118, "safety_blocked": 2} |
| evaluation | sd15 | 0.4 | C0 native A | 119/120 | 0 | 1 | 0/40 | 39 | 1 | {"ok": 119, "safety_blocked": 1} |
| evaluation | sd15 | 0.4 | C1 wrong-owner native A | 118/120 | 0 | 2 | 0/40 | 39 | 1 | {"ok": 118, "safety_blocked": 2} |
| evaluation | sd21 | 0.1 | C0 native A | 120/120 | 0 | 0 | 0/40 | 40 | 0 | {"ok": 120} |
| evaluation | sd21 | 0.1 | C1 wrong-owner native A | 120/120 | 0 | 0 | 0/40 | 40 | 0 | {"ok": 120} |
| evaluation | sd21 | 0.2 | C0 native A | 120/120 | 0 | 0 | 0/40 | 40 | 0 | {"ok": 120} |
| evaluation | sd21 | 0.2 | C1 wrong-owner native A | 120/120 | 0 | 0 | 0/40 | 40 | 0 | {"ok": 120} |
| evaluation | sd21 | 0.4 | C0 native A | 120/120 | 0 | 0 | 0/40 | 40 | 0 | {"ok": 120} |
| evaluation | sd21 | 0.4 | C1 wrong-owner native A | 120/120 | 0 | 0 | 0/40 | 40 | 0 | {"ok": 120} |

These are native detector A controls (either watermark tier found), separate from registry acceptance. A recorded call and Boolean A endpoint are both required for call availability. Safety-blocked, failed, not-yet-run and otherwise absent calls stay unknown. An unresolved source cluster has no observed A acceptance and at least one unknown call. No unavailable negative call is counted as an observed rejection. These inventories are not population false-positive estimates.

Fresh construction evidence: [run.json](<W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/20261016-registry-step2-fresh/run.json>), [rows.jsonl](<W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/20261016-registry-step2-fresh/rows.jsonl>). Commit `cf5de20abeea171b15439dcdf126f584c5830737`; duration 5237.77 seconds; accounted step-2 duration 6944.17 seconds. Human visual admissibility remains missing.

## Fresh calibration and evaluation

Fresh analysis status: **development_fail_or_incomplete**. Thresholds are fitted only on the 20 calibration sources and licensed near-duplicate calibration pairs, then frozen. Evaluation uses the disjoint 40-source development split; it remains development evidence.

Availability amendment: `posthoc-calibration-pre-evaluation-verified-native-D1-weak-detail-abstention-v1`. The original calibration failure is preserved: 415.907 seconds at commit `cf5de20`, before any threshold was frozen. The amended run uses post-hoc calibration, pre-evaluation semantics; it is not an unchanged preregistered analysis. Only D1 vectors independently verified to abstain below the existing native detail floor are deterministic rejections. D1 remains the fixed primary descriptor, with no D2 rescue and no feature, floor, threshold-selection or source-selection change. Expected safety-blocked negative comparisons remain unresolved under the original convention; they are not observed cosine scores or observed rejections. Genuine execution, image, call or descriptor errors remain unknown.

Calibration `development_pass` is diagnostic only; there is no 18/20 calibration gate. The evaluation gate remains at least 36/40 source majorities at .2 on both models with zero observed false accepts. Verified abstentions fail positive slots in the full planned denominator; negative abstentions are deterministic rejects. Finite cosine coverage, verified abstentions and unknowns are reported separately below.

### Calibration threshold drivers (descriptive)

| Descriptor | Maximum negative ID | Family | Maximum finite score | Rows tied at maximum | Maximum ID excluding real near-duplicates | Family excluding real near-duplicates | Maximum score excluding real near-duplicates | Maximum minus excluded-family maximum |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D1 | near:tos-02_3a | real_near_duplicate | 0.586548 | 1 | sd21:1180:0.4:14:f5-r2 | wrong_source | 0.0546768 | 0.531871 |
| D2 | near:tos-02_3a | real_near_duplicate | 0.989856 | 1 | sd15:1355:0.4:14:C0 | wrong_source | 0.615791 | 0.374065 |
| D3 | near:tos-02_3a | real_near_duplicate | 0.994367 | 1 | sd15:908:0.4:12:C0 | wrong_source | 0.807748 | 0.186619 |

The difference describes how far the real-near-duplicate family raises the maximum finite calibration negative. If several rows tie, the displayed ID is the first stored row; the tie count includes every row at that maximum. Absent finite scores display missing. This is a descriptive family-exclusion comparison, not an alternative threshold, gate, descriptor rescue or evaluation-based selection. The frozen threshold remains nextafter above the maximum finite calibration negative across all families.

Calibration score evidence: [calibration-D1-scores.json](<W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/20261016-registry-step2-fresh-analysis-r2/calibration-D1-scores.json>), [calibration-D2-scores.json](<W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/20261016-registry-step2-fresh-analysis-r2/calibration-D2-scores.json>), [calibration-D3-scores.json](<W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/20261016-registry-step2-fresh-analysis-r2/calibration-D3-scores.json>).

### Calibration

| Descriptor | Cell | Frozen tau | Available images | Own cosine finite | Own native abstentions | Own-descriptor TPR seed | Own-descriptor TPR majority | Seed F_R | Majority F_R | Stored TPR_seed (F_R rate) | Stored TPR_source_majority (F_R rate) | Fingerprint correct | Fingerprint majority | Old F seeds | Old F majority | Blocked | Unknown | Diagnostic pass (cal) / development pass (eval) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D1 | sd15/0.1 | 0.586548 | 60/60 | 60 | 0 | 60/60; rate 1 | 20/20; rate 1 | 60/60 | 20/20 | 1 | 1 | 60/60 | 20/20 | 0 | 0 | 0 | 0 | no |
| D1 | sd15/0.2 | 0.586548 | 60/60 | 57 | 3 | 45/60; rate 0.75 | 15/20; rate 0.75 | 45/60 | 15/20 | 0.75 | 0.75 | 45/60 | 15/20 | 0 | 0 | 0 | 0 | no |
| D1 | sd15/0.4 | 0.586548 | 60/60 | 57 | 3 | 10/60; rate 0.166667 | 3/20; rate 0.15 | 7/60 | 2/20 | 0.116667 | 0.1 | 10/60 | 3/20 | 0 | 0 | 0 | 0 | no |
| D1 | sd21/0.1 | 0.586548 | 60/60 | 59 | 1 | 59/60; rate 0.983333 | 20/20; rate 1 | 59/60 | 20/20 | 0.983333 | 1 | 59/60 | 20/20 | 0 | 0 | 0 | 0 | no |
| D1 | sd21/0.2 | 0.586548 | 60/60 | 57 | 3 | 45/60; rate 0.75 | 15/20; rate 0.75 | 45/60 | 15/20 | 0.75 | 0.75 | 45/60 | 15/20 | 0 | 0 | 0 | 0 | no |
| D1 | sd21/0.4 | 0.586548 | 60/60 | 57 | 3 | 10/60; rate 0.166667 | 3/20; rate 0.15 | 7/60 | 2/20 | 0.116667 | 0.1 | 10/60 | 3/20 | 0 | 0 | 0 | 0 | no |
| D2 | sd15/0.1 | 0.989856 | 60/60 | 60 | 0 | 0/60; rate 0 | 0/20; rate 0 | 0/60 | 0/20 | 0 | 0 | 0/60 | 0/20 | 0 | 0 | 0 | 0 | no |
| D2 | sd15/0.2 | 0.989856 | 60/60 | 60 | 0 | 0/60; rate 0 | 0/20; rate 0 | 0/60 | 0/20 | 0 | 0 | 0/60 | 0/20 | 0 | 0 | 0 | 0 | no |
| D2 | sd15/0.4 | 0.989856 | 60/60 | 60 | 0 | 0/60; rate 0 | 0/20; rate 0 | 0/60 | 0/20 | 0 | 0 | 0/60 | 0/20 | 0 | 0 | 0 | 0 | no |
| D2 | sd21/0.1 | 0.989856 | 60/60 | 60 | 0 | 0/60; rate 0 | 0/20; rate 0 | 0/60 | 0/20 | 0 | 0 | 0/60 | 0/20 | 0 | 0 | 0 | 0 | no |
| D2 | sd21/0.2 | 0.989856 | 60/60 | 60 | 0 | 0/60; rate 0 | 0/20; rate 0 | 0/60 | 0/20 | 0 | 0 | 0/60 | 0/20 | 0 | 0 | 0 | 0 | no |
| D2 | sd21/0.4 | 0.989856 | 60/60 | 60 | 0 | 0/60; rate 0 | 0/20; rate 0 | 0/60 | 0/20 | 0 | 0 | 0/60 | 0/20 | 0 | 0 | 0 | 0 | no |
| D3 | sd15/0.1 | 0.994367 | 60/60 | 60 | 0 | 0/60; rate 0 | 0/20; rate 0 | 0/60 | 0/20 | 0 | 0 | 0/60 | 0/20 | 0 | 0 | 0 | 0 | no |
| D3 | sd15/0.2 | 0.994367 | 60/60 | 60 | 0 | 0/60; rate 0 | 0/20; rate 0 | 0/60 | 0/20 | 0 | 0 | 0/60 | 0/20 | 0 | 0 | 0 | 0 | no |
| D3 | sd15/0.4 | 0.994367 | 60/60 | 60 | 0 | 0/60; rate 0 | 0/20; rate 0 | 0/60 | 0/20 | 0 | 0 | 0/60 | 0/20 | 0 | 0 | 0 | 0 | no |
| D3 | sd21/0.1 | 0.994367 | 60/60 | 60 | 0 | 0/60; rate 0 | 0/20; rate 0 | 0/60 | 0/20 | 0 | 0 | 0/60 | 0/20 | 0 | 0 | 0 | 0 | no |
| D3 | sd21/0.2 | 0.994367 | 60/60 | 60 | 0 | 0/60; rate 0 | 0/20; rate 0 | 0/60 | 0/20 | 0 | 0 | 0/60 | 0/20 | 0 | 0 | 0 | 0 | no |
| D3 | sd21/0.4 | 0.994367 | 60/60 | 60 | 0 | 0/60; rate 0 | 0/20; rate 0 | 0/60 | 0/20 | 0 | 0 | 0/60 | 0/20 | 0 | 0 | 0 | 0 | no |

| Descriptor | Negative family | Observed cosine/planned | Registry false accepts | Fingerprint false accepts | Native abstentions | Unknown | Registry cluster bounds | Fingerprint cluster bounds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D1 | wrong_source | 13927/14440 | 0 | 0 | 475 | 38 | {"completely_evaluated_sources": 18, "conservative_upper_one_sided_95": 0.2826185248858608, "independent_units": 20, "observed": 18, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.0, 0.1853019681378522], "upper_one_sided_95": 0.1533175539572782}, "planned": 20, "planned_rate_bounds": [0.0, 0.1], "positives": 0, "sources_with_unavailable_calls": 2, "unresolved": 2} | {"completely_evaluated_sources": 18, "conservative_upper_one_sided_95": 0.2826185248858608, "independent_units": 20, "observed": 18, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.0, 0.1853019681378522], "upper_one_sided_95": 0.1533175539572782}, "planned": 20, "planned_rate_bounds": [0.0, 0.1], "positives": 0, "sources_with_unavailable_calls": 2, "unresolved": 2} |
| D1 | q_nearest | 733/760 | 0 | 0 | 25 | 2 | {"completely_evaluated_sources": 18, "conservative_upper_one_sided_95": 0.2826185248858608, "independent_units": 20, "observed": 18, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.0, 0.1853019681378522], "upper_one_sided_95": 0.1533175539572782}, "planned": 20, "planned_rate_bounds": [0.0, 0.1], "positives": 0, "sources_with_unavailable_calls": 2, "unresolved": 2} | {"completely_evaluated_sources": 18, "conservative_upper_one_sided_95": 0.2826185248858608, "independent_units": 20, "observed": 18, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.0, 0.1853019681378522], "upper_one_sided_95": 0.1533175539572782}, "planned": 20, "planned_rate_bounds": [0.0, 0.1], "positives": 0, "sources_with_unavailable_calls": 2, "unresolved": 2} |
| D1 | T4 | 40/40 | 0 | 0 | 0 | 0 | {"completely_evaluated_sources": 20, "conservative_upper_one_sided_95": 0.13910834066826516, "independent_units": 20, "observed": 20, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.0, 0.1684334709830853], "upper_one_sided_95": 0.13910834066826516}, "planned": 20, "planned_rate_bounds": [0.0, 0.0], "positives": 0, "sources_with_unavailable_calls": 0, "unresolved": 0} | {"completely_evaluated_sources": 20, "conservative_upper_one_sided_95": 0.13910834066826516, "independent_units": 20, "observed": 20, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.0, 0.1684334709830853], "upper_one_sided_95": 0.13910834066826516}, "planned": 20, "planned_rate_bounds": [0.0, 0.0], "positives": 0, "sources_with_unavailable_calls": 0, "unresolved": 0} |
| D1 | real_near_duplicate | 6/7 | 0 | 0 | 1 | 0 | {"completely_evaluated_sources": 7, "conservative_upper_one_sided_95": 0.34816365513116077, "independent_units": 7, "observed": 7, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.0, 0.4096163972250034], "upper_one_sided_95": 0.34816365513116077}, "planned": 7, "planned_rate_bounds": [0.0, 0.0], "positives": 0, "sources_with_unavailable_calls": 0, "unresolved": 0} | {"completely_evaluated_sources": 7, "conservative_upper_one_sided_95": 0.34816365513116077, "independent_units": 7, "observed": 7, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.0, 0.4096163972250034], "upper_one_sided_95": 0.34816365513116077}, "planned": 7, "planned_rate_bounds": [0.0, 0.0], "positives": 0, "sources_with_unavailable_calls": 0, "unresolved": 0} |
| D2 | wrong_source | 14402/14440 | 0 | 0 | 0 | 38 | {"completely_evaluated_sources": 18, "conservative_upper_one_sided_95": 0.2826185248858608, "independent_units": 20, "observed": 18, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.0, 0.1853019681378522], "upper_one_sided_95": 0.1533175539572782}, "planned": 20, "planned_rate_bounds": [0.0, 0.1], "positives": 0, "sources_with_unavailable_calls": 2, "unresolved": 2} | {"completely_evaluated_sources": 18, "conservative_upper_one_sided_95": 0.2826185248858608, "independent_units": 20, "observed": 18, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.0, 0.1853019681378522], "upper_one_sided_95": 0.1533175539572782}, "planned": 20, "planned_rate_bounds": [0.0, 0.1], "positives": 0, "sources_with_unavailable_calls": 2, "unresolved": 2} |
| D2 | q_nearest | 758/760 | 0 | 0 | 0 | 2 | {"completely_evaluated_sources": 18, "conservative_upper_one_sided_95": 0.2826185248858608, "independent_units": 20, "observed": 18, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.0, 0.1853019681378522], "upper_one_sided_95": 0.1533175539572782}, "planned": 20, "planned_rate_bounds": [0.0, 0.1], "positives": 0, "sources_with_unavailable_calls": 2, "unresolved": 2} | {"completely_evaluated_sources": 18, "conservative_upper_one_sided_95": 0.2826185248858608, "independent_units": 20, "observed": 18, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.0, 0.1853019681378522], "upper_one_sided_95": 0.1533175539572782}, "planned": 20, "planned_rate_bounds": [0.0, 0.1], "positives": 0, "sources_with_unavailable_calls": 2, "unresolved": 2} |
| D2 | T4 | 40/40 | 0 | 0 | 0 | 0 | {"completely_evaluated_sources": 20, "conservative_upper_one_sided_95": 0.13910834066826516, "independent_units": 20, "observed": 20, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.0, 0.1684334709830853], "upper_one_sided_95": 0.13910834066826516}, "planned": 20, "planned_rate_bounds": [0.0, 0.0], "positives": 0, "sources_with_unavailable_calls": 0, "unresolved": 0} | {"completely_evaluated_sources": 20, "conservative_upper_one_sided_95": 0.13910834066826516, "independent_units": 20, "observed": 20, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.0, 0.1684334709830853], "upper_one_sided_95": 0.13910834066826516}, "planned": 20, "planned_rate_bounds": [0.0, 0.0], "positives": 0, "sources_with_unavailable_calls": 0, "unresolved": 0} |
| D2 | real_near_duplicate | 7/7 | 0 | 0 | 0 | 0 | {"completely_evaluated_sources": 7, "conservative_upper_one_sided_95": 0.34816365513116077, "independent_units": 7, "observed": 7, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.0, 0.4096163972250034], "upper_one_sided_95": 0.34816365513116077}, "planned": 7, "planned_rate_bounds": [0.0, 0.0], "positives": 0, "sources_with_unavailable_calls": 0, "unresolved": 0} | {"completely_evaluated_sources": 7, "conservative_upper_one_sided_95": 0.34816365513116077, "independent_units": 7, "observed": 7, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.0, 0.4096163972250034], "upper_one_sided_95": 0.34816365513116077}, "planned": 7, "planned_rate_bounds": [0.0, 0.0], "positives": 0, "sources_with_unavailable_calls": 0, "unresolved": 0} |
| D3 | wrong_source | 14402/14440 | 0 | 0 | 0 | 38 | {"completely_evaluated_sources": 18, "conservative_upper_one_sided_95": 0.2826185248858608, "independent_units": 20, "observed": 18, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.0, 0.1853019681378522], "upper_one_sided_95": 0.1533175539572782}, "planned": 20, "planned_rate_bounds": [0.0, 0.1], "positives": 0, "sources_with_unavailable_calls": 2, "unresolved": 2} | {"completely_evaluated_sources": 18, "conservative_upper_one_sided_95": 0.2826185248858608, "independent_units": 20, "observed": 18, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.0, 0.1853019681378522], "upper_one_sided_95": 0.1533175539572782}, "planned": 20, "planned_rate_bounds": [0.0, 0.1], "positives": 0, "sources_with_unavailable_calls": 2, "unresolved": 2} |
| D3 | q_nearest | 758/760 | 0 | 0 | 0 | 2 | {"completely_evaluated_sources": 18, "conservative_upper_one_sided_95": 0.2826185248858608, "independent_units": 20, "observed": 18, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.0, 0.1853019681378522], "upper_one_sided_95": 0.1533175539572782}, "planned": 20, "planned_rate_bounds": [0.0, 0.1], "positives": 0, "sources_with_unavailable_calls": 2, "unresolved": 2} | {"completely_evaluated_sources": 18, "conservative_upper_one_sided_95": 0.2826185248858608, "independent_units": 20, "observed": 18, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.0, 0.1853019681378522], "upper_one_sided_95": 0.1533175539572782}, "planned": 20, "planned_rate_bounds": [0.0, 0.1], "positives": 0, "sources_with_unavailable_calls": 2, "unresolved": 2} |
| D3 | T4 | 40/40 | 0 | 0 | 0 | 0 | {"completely_evaluated_sources": 20, "conservative_upper_one_sided_95": 0.13910834066826516, "independent_units": 20, "observed": 20, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.0, 0.1684334709830853], "upper_one_sided_95": 0.13910834066826516}, "planned": 20, "planned_rate_bounds": [0.0, 0.0], "positives": 0, "sources_with_unavailable_calls": 0, "unresolved": 0} | {"completely_evaluated_sources": 20, "conservative_upper_one_sided_95": 0.13910834066826516, "independent_units": 20, "observed": 20, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.0, 0.1684334709830853], "upper_one_sided_95": 0.13910834066826516}, "planned": 20, "planned_rate_bounds": [0.0, 0.0], "positives": 0, "sources_with_unavailable_calls": 0, "unresolved": 0} |
| D3 | real_near_duplicate | 7/7 | 0 | 0 | 0 | 0 | {"completely_evaluated_sources": 7, "conservative_upper_one_sided_95": 0.34816365513116077, "independent_units": 7, "observed": 7, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.0, 0.4096163972250034], "upper_one_sided_95": 0.34816365513116077}, "planned": 7, "planned_rate_bounds": [0.0, 0.0], "positives": 0, "sources_with_unavailable_calls": 0, "unresolved": 0} | {"completely_evaluated_sources": 7, "conservative_upper_one_sided_95": 0.34816365513116077, "independent_units": 7, "observed": 7, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.0, 0.4096163972250034], "upper_one_sided_95": 0.34816365513116077}, "planned": 7, "planned_rate_bounds": [0.0, 0.0], "positives": 0, "sources_with_unavailable_calls": 0, "unresolved": 0} |

TPR_seed and TPR_source_majority are the stored correct-record F_R rates on the full planned seed and source denominators, respectively; the adjacent F_R columns retain their numerator/denominator counts. Unavailable or abstaining positives do not contribute successes.

Own-descriptor TPR compares each C1 query only with its own enrolled record at the frozen descriptor tau (inclusive >=), without requiring a pointer or winning identification. It is computed from the saved score vectors in sorted source-ID record order. Missing/nonfinite own scores fail; source majority requires at least two successful seeds. Both rates retain full planned denominators; absent score files or an incomplete record ordering inventory display missing rather than a measured zero.

| Descriptor | Planned registry N | Searchable clean references/planned | Raw descriptor bytes | Lookup calls | Lookup seconds | Mean seconds/call | K observations | Minimum K | Median K | Maximum K | Extraction seconds in cache metrics |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D1 | 20 | 20/20 | 1310720 | 1520 | 0.016 | 1.05263e-05 | 360 | 0 | 1 | 7 | 0 |
| D2 | 20 | 20/20 | 61440 | 1520 | 0 | 0 | 360 | 0 | 1 | 7 | 0 |
| D3 | 20 | 20/20 | 81920 | 1520 | 0.015 | 9.86842e-06 | 360 | 0 | 1 | 7 | 0 |

Saved split extraction/cache metrics: `{"disk_hits": 812, "disk_load_seconds": 7.053264800048055, "extracted_images": 0, "extraction_seconds": {"D1": 0.0, "D2": 0.0, "D3": 0.0}, "extraction_wall_seconds": 0.0, "memory_hits": 91984}`.

N is the planned split-local registry size. Searchable clean references count unique clean C1 sources with observed own-score availability or a finite saved own cosine; abstaining reference slots remain planned but unsearchable. Raw descriptor bytes sum the available saved float64 vectors; record metadata, q/h, indexes and container overhead are additional. K summarizes the stored positive-cell candidate_counts, not all registry records or negative queries. Lookup timing covers paired registry and fingerprint identification on already computed scores; the reported mean divides their combined seconds by their combined call count, and excludes cosine extraction and scoring. Extraction/cache metrics are the latest saved invocation snapshot with memory/disk reuse, not a cumulative extraction benchmark or a cold-cache per-image cost. Split snapshots may overlap and must not be summed.

The diagnostic calibration flag does not authorize, stop or select the method; the 18/20 value used internally by that diagnostic is not a protocol gate.

### Evaluation

| Descriptor | Cell | Frozen tau | Available images | Own cosine finite | Own native abstentions | Own-descriptor TPR seed | Own-descriptor TPR majority | Seed F_R | Majority F_R | Stored TPR_seed (F_R rate) | Stored TPR_source_majority (F_R rate) | Fingerprint correct | Fingerprint majority | Old F seeds | Old F majority | Blocked | Unknown | Diagnostic pass (cal) / development pass (eval) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D1 | sd15/0.1 | 0.586548 | 114/120 | 105 | 9 | 105/120; rate 0.875 | 35/40; rate 0.875 | 105/120 | 35/40 | 0.875 | 0.875 | 105/120 | 35/40 | 0 | 0 | 6 | 0 | no |
| D1 | sd15/0.2 | 0.586548 | 118/120 | 109 | 9 | 89/120; rate 0.741667 | 30/40; rate 0.75 | 89/120 | 30/40 | 0.741667 | 0.75 | 89/120 | 30/40 | 0 | 0 | 2 | 0 | no |
| D1 | sd15/0.4 | 0.586548 | 118/120 | 108 | 10 | 23/120; rate 0.191667 | 8/40; rate 0.2 | 20/120 | 7/40 | 0.166667 | 0.175 | 23/120 | 8/40 | 0 | 0 | 2 | 0 | no |
| D1 | sd21/0.1 | 0.586548 | 120/120 | 111 | 9 | 111/120; rate 0.925 | 37/40; rate 0.925 | 111/120 | 37/40 | 0.925 | 0.925 | 111/120 | 37/40 | 0 | 0 | 0 | 0 | no |
| D1 | sd21/0.2 | 0.586548 | 120/120 | 110 | 10 | 96/120; rate 0.8 | 32/40; rate 0.8 | 96/120 | 32/40 | 0.8 | 0.8 | 96/120 | 32/40 | 0 | 0 | 0 | 0 | no |
| D1 | sd21/0.4 | 0.586548 | 120/120 | 109 | 11 | 26/120; rate 0.216667 | 9/40; rate 0.225 | 23/120 | 8/40 | 0.191667 | 0.2 | 26/120 | 9/40 | 0 | 0 | 0 | 0 | no |
| D2 | sd15/0.1 | 0.989856 | 114/120 | 114 | 0 | 1/120; rate 0.00833333 | 0/40; rate 0 | 1/120 | 0/40 | 0.00833333 | 0 | 1/120 | 0/40 | 0 | 0 | 6 | 0 | no |
| D2 | sd15/0.2 | 0.989856 | 118/120 | 118 | 0 | 0/120; rate 0 | 0/40; rate 0 | 0/120 | 0/40 | 0 | 0 | 0/120 | 0/40 | 0 | 0 | 2 | 0 | no |
| D2 | sd15/0.4 | 0.989856 | 118/120 | 118 | 0 | 0/120; rate 0 | 0/40; rate 0 | 0/120 | 0/40 | 0 | 0 | 0/120 | 0/40 | 0 | 0 | 2 | 0 | no |
| D2 | sd21/0.1 | 0.989856 | 120/120 | 120 | 0 | 0/120; rate 0 | 0/40; rate 0 | 0/120 | 0/40 | 0 | 0 | 0/120 | 0/40 | 0 | 0 | 0 | 0 | no |
| D2 | sd21/0.2 | 0.989856 | 120/120 | 120 | 0 | 0/120; rate 0 | 0/40; rate 0 | 0/120 | 0/40 | 0 | 0 | 0/120 | 0/40 | 0 | 0 | 0 | 0 | no |
| D2 | sd21/0.4 | 0.989856 | 120/120 | 120 | 0 | 0/120; rate 0 | 0/40; rate 0 | 0/120 | 0/40 | 0 | 0 | 0/120 | 0/40 | 0 | 0 | 0 | 0 | no |
| D3 | sd15/0.1 | 0.994367 | 114/120 | 114 | 0 | 0/120; rate 0 | 0/40; rate 0 | 0/120 | 0/40 | 0 | 0 | 0/120 | 0/40 | 0 | 0 | 6 | 0 | no |
| D3 | sd15/0.2 | 0.994367 | 118/120 | 118 | 0 | 0/120; rate 0 | 0/40; rate 0 | 0/120 | 0/40 | 0 | 0 | 0/120 | 0/40 | 0 | 0 | 2 | 0 | no |
| D3 | sd15/0.4 | 0.994367 | 118/120 | 118 | 0 | 0/120; rate 0 | 0/40; rate 0 | 0/120 | 0/40 | 0 | 0 | 0/120 | 0/40 | 0 | 0 | 2 | 0 | no |
| D3 | sd21/0.1 | 0.994367 | 120/120 | 120 | 0 | 0/120; rate 0 | 0/40; rate 0 | 0/120 | 0/40 | 0 | 0 | 0/120 | 0/40 | 0 | 0 | 0 | 0 | no |
| D3 | sd21/0.2 | 0.994367 | 120/120 | 120 | 0 | 0/120; rate 0 | 0/40; rate 0 | 0/120 | 0/40 | 0 | 0 | 0/120 | 0/40 | 0 | 0 | 0 | 0 | no |
| D3 | sd21/0.4 | 0.994367 | 120/120 | 120 | 0 | 0/120; rate 0 | 0/40; rate 0 | 0/120 | 0/40 | 0 | 0 | 0/120 | 0/40 | 0 | 0 | 0 | 0 | no |

| Descriptor | Negative family | Observed cosine/planned | Registry false accepts | Fingerprint false accepts | Native abstentions | Unknown | Registry cluster bounds | Fingerprint cluster bounds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D1 | wrong_source | 52630/59280 | 0 | 0 | 5831 | 819 | {"completely_evaluated_sources": 37, "conservative_upper_one_sided_95": 0.1825868500159012, "independent_units": 40, "observed": 37, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.0, 0.09489058741498986], "upper_one_sided_95": 0.0777747110051379}, "planned": 40, "planned_rate_bounds": [0.0, 0.075], "positives": 0, "sources_with_unavailable_calls": 3, "unresolved": 3} | {"completely_evaluated_sources": 37, "conservative_upper_one_sided_95": 0.1825868500159012, "independent_units": 40, "observed": 37, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.0, 0.09489058741498986], "upper_one_sided_95": 0.0777747110051379}, "planned": 40, "planned_rate_bounds": [0.0, 0.075], "positives": 0, "sources_with_unavailable_calls": 3, "unresolved": 3} |
| D1 | q_nearest | 1320/1520 | 0 | 0 | 179 | 21 | {"completely_evaluated_sources": 37, "conservative_upper_one_sided_95": 0.1825868500159012, "independent_units": 40, "observed": 37, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.0, 0.09489058741498986], "upper_one_sided_95": 0.0777747110051379}, "planned": 40, "planned_rate_bounds": [0.0, 0.075], "positives": 0, "sources_with_unavailable_calls": 3, "unresolved": 3} | {"completely_evaluated_sources": 37, "conservative_upper_one_sided_95": 0.1825868500159012, "independent_units": 40, "observed": 37, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.0, 0.09489058741498986], "upper_one_sided_95": 0.0777747110051379}, "planned": 40, "planned_rate_bounds": [0.0, 0.075], "positives": 0, "sources_with_unavailable_calls": 3, "unresolved": 3} |
| D1 | T4 | 76/80 | 0 | 0 | 4 | 0 | {"completely_evaluated_sources": 40, "conservative_upper_one_sided_95": 0.07215752450551455, "independent_units": 40, "observed": 40, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.0, 0.08809730287880237], "upper_one_sided_95": 0.07215752450551455}, "planned": 40, "planned_rate_bounds": [0.0, 0.0], "positives": 0, "sources_with_unavailable_calls": 0, "unresolved": 0} | {"completely_evaluated_sources": 40, "conservative_upper_one_sided_95": 0.07215752450551455, "independent_units": 40, "observed": 40, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.0, 0.08809730287880237], "upper_one_sided_95": 0.07215752450551455}, "planned": 40, "planned_rate_bounds": [0.0, 0.0], "positives": 0, "sources_with_unavailable_calls": 0, "unresolved": 0} |
| D1 | real_near_duplicate | 11/13 | 0 | 4 | 2 | 0 | {"completely_evaluated_sources": 13, "conservative_upper_one_sided_95": 0.20581666518655062, "independent_units": 13, "observed": 13, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.0, 0.24705263800047095], "upper_one_sided_95": 0.20581666518655062}, "planned": 13, "planned_rate_bounds": [0.0, 0.0], "positives": 0, "sources_with_unavailable_calls": 0, "unresolved": 0} | {"completely_evaluated_sources": 13, "conservative_upper_one_sided_95": 0.5726193394082124, "independent_units": 13, "observed": 13, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.09092039457209658, 0.6142616617507044], "upper_one_sided_95": 0.5726193394082124}, "planned": 13, "planned_rate_bounds": [0.3076923076923077, 0.3076923076923077], "positives": 4, "sources_with_unavailable_calls": 0, "unresolved": 0} |
| D2 | wrong_source | 58461/59280 | 0 | 0 | 0 | 819 | {"completely_evaluated_sources": 37, "conservative_upper_one_sided_95": 0.1825868500159012, "independent_units": 40, "observed": 37, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.0, 0.09489058741498986], "upper_one_sided_95": 0.0777747110051379}, "planned": 40, "planned_rate_bounds": [0.0, 0.075], "positives": 0, "sources_with_unavailable_calls": 3, "unresolved": 3} | {"completely_evaluated_sources": 37, "conservative_upper_one_sided_95": 0.1825868500159012, "independent_units": 40, "observed": 37, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.0, 0.09489058741498986], "upper_one_sided_95": 0.0777747110051379}, "planned": 40, "planned_rate_bounds": [0.0, 0.075], "positives": 0, "sources_with_unavailable_calls": 3, "unresolved": 3} |
| D2 | q_nearest | 1499/1520 | 0 | 0 | 0 | 21 | {"completely_evaluated_sources": 37, "conservative_upper_one_sided_95": 0.1825868500159012, "independent_units": 40, "observed": 37, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.0, 0.09489058741498986], "upper_one_sided_95": 0.0777747110051379}, "planned": 40, "planned_rate_bounds": [0.0, 0.075], "positives": 0, "sources_with_unavailable_calls": 3, "unresolved": 3} | {"completely_evaluated_sources": 37, "conservative_upper_one_sided_95": 0.1825868500159012, "independent_units": 40, "observed": 37, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.0, 0.09489058741498986], "upper_one_sided_95": 0.0777747110051379}, "planned": 40, "planned_rate_bounds": [0.0, 0.075], "positives": 0, "sources_with_unavailable_calls": 3, "unresolved": 3} |
| D2 | T4 | 80/80 | 0 | 0 | 0 | 0 | {"completely_evaluated_sources": 40, "conservative_upper_one_sided_95": 0.07215752450551455, "independent_units": 40, "observed": 40, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.0, 0.08809730287880237], "upper_one_sided_95": 0.07215752450551455}, "planned": 40, "planned_rate_bounds": [0.0, 0.0], "positives": 0, "sources_with_unavailable_calls": 0, "unresolved": 0} | {"completely_evaluated_sources": 40, "conservative_upper_one_sided_95": 0.07215752450551455, "independent_units": 40, "observed": 40, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.0, 0.08809730287880237], "upper_one_sided_95": 0.07215752450551455}, "planned": 40, "planned_rate_bounds": [0.0, 0.0], "positives": 0, "sources_with_unavailable_calls": 0, "unresolved": 0} |
| D2 | real_near_duplicate | 13/13 | 0 | 0 | 0 | 0 | {"completely_evaluated_sources": 13, "conservative_upper_one_sided_95": 0.20581666518655062, "independent_units": 13, "observed": 13, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.0, 0.24705263800047095], "upper_one_sided_95": 0.20581666518655062}, "planned": 13, "planned_rate_bounds": [0.0, 0.0], "positives": 0, "sources_with_unavailable_calls": 0, "unresolved": 0} | {"completely_evaluated_sources": 13, "conservative_upper_one_sided_95": 0.20581666518655062, "independent_units": 13, "observed": 13, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.0, 0.24705263800047095], "upper_one_sided_95": 0.20581666518655062}, "planned": 13, "planned_rate_bounds": [0.0, 0.0], "positives": 0, "sources_with_unavailable_calls": 0, "unresolved": 0} |
| D3 | wrong_source | 58461/59280 | 0 | 0 | 0 | 819 | {"completely_evaluated_sources": 37, "conservative_upper_one_sided_95": 0.1825868500159012, "independent_units": 40, "observed": 37, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.0, 0.09489058741498986], "upper_one_sided_95": 0.0777747110051379}, "planned": 40, "planned_rate_bounds": [0.0, 0.075], "positives": 0, "sources_with_unavailable_calls": 3, "unresolved": 3} | {"completely_evaluated_sources": 37, "conservative_upper_one_sided_95": 0.1825868500159012, "independent_units": 40, "observed": 37, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.0, 0.09489058741498986], "upper_one_sided_95": 0.0777747110051379}, "planned": 40, "planned_rate_bounds": [0.0, 0.075], "positives": 0, "sources_with_unavailable_calls": 3, "unresolved": 3} |
| D3 | q_nearest | 1499/1520 | 0 | 0 | 0 | 21 | {"completely_evaluated_sources": 37, "conservative_upper_one_sided_95": 0.1825868500159012, "independent_units": 40, "observed": 37, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.0, 0.09489058741498986], "upper_one_sided_95": 0.0777747110051379}, "planned": 40, "planned_rate_bounds": [0.0, 0.075], "positives": 0, "sources_with_unavailable_calls": 3, "unresolved": 3} | {"completely_evaluated_sources": 37, "conservative_upper_one_sided_95": 0.1825868500159012, "independent_units": 40, "observed": 37, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.0, 0.09489058741498986], "upper_one_sided_95": 0.0777747110051379}, "planned": 40, "planned_rate_bounds": [0.0, 0.075], "positives": 0, "sources_with_unavailable_calls": 3, "unresolved": 3} |
| D3 | T4 | 80/80 | 0 | 0 | 0 | 0 | {"completely_evaluated_sources": 40, "conservative_upper_one_sided_95": 0.07215752450551455, "independent_units": 40, "observed": 40, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.0, 0.08809730287880237], "upper_one_sided_95": 0.07215752450551455}, "planned": 40, "planned_rate_bounds": [0.0, 0.0], "positives": 0, "sources_with_unavailable_calls": 0, "unresolved": 0} | {"completely_evaluated_sources": 40, "conservative_upper_one_sided_95": 0.07215752450551455, "independent_units": 40, "observed": 40, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.0, 0.08809730287880237], "upper_one_sided_95": 0.07215752450551455}, "planned": 40, "planned_rate_bounds": [0.0, 0.0], "positives": 0, "sources_with_unavailable_calls": 0, "unresolved": 0} |
| D3 | real_near_duplicate | 13/13 | 0 | 3 | 0 | 0 | {"completely_evaluated_sources": 13, "conservative_upper_one_sided_95": 0.20581666518655062, "independent_units": 13, "observed": 13, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.0, 0.24705263800047095], "upper_one_sided_95": 0.20581666518655062}, "planned": 13, "planned_rate_bounds": [0.0, 0.0], "positives": 0, "sources_with_unavailable_calls": 0, "unresolved": 0} | {"completely_evaluated_sources": 13, "conservative_upper_one_sided_95": 0.4946497301513655, "independent_units": 13, "observed": 13, "observed_event_interval": {"model": "hypothetical exchangeable units", "two_sided_95": [0.050381073491151535, 0.5381315392340409], "upper_one_sided_95": 0.4946497301513655}, "planned": 13, "planned_rate_bounds": [0.23076923076923078, 0.23076923076923078], "positives": 3, "sources_with_unavailable_calls": 0, "unresolved": 0} |

TPR_seed and TPR_source_majority are the stored correct-record F_R rates on the full planned seed and source denominators, respectively; the adjacent F_R columns retain their numerator/denominator counts. Unavailable or abstaining positives do not contribute successes.

Own-descriptor TPR compares each C1 query only with its own enrolled record at the frozen descriptor tau (inclusive >=), without requiring a pointer or winning identification. It is computed from the saved score vectors in sorted source-ID record order. Missing/nonfinite own scores fail; source majority requires at least two successful seeds. Both rates retain full planned denominators; absent score files or an incomplete record ordering inventory display missing rather than a measured zero.

| Descriptor | Planned registry N | Searchable clean references/planned | Raw descriptor bytes | Lookup calls | Lookup seconds | Mean seconds/call | K observations | Minimum K | Median K | Maximum K | Extraction seconds in cache metrics |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D1 | 40 | 39/40 | 2555904 | 3040 | 0.016 | 5.26316e-06 | 720 | 0 | 4 | 24 | 56.1892 |
| D2 | 40 | 40/40 | 122880 | 3040 | 0.015 | 4.93421e-06 | 720 | 0 | 4 | 24 | 15.0596 |
| D3 | 40 | 40/40 | 163840 | 3040 | 0.016 | 5.26316e-06 | 720 | 0 | 4 | 24 | 87.6443 |

Saved split extraction/cache metrics: `{"disk_hits": 1237, "disk_load_seconds": 1.3121908999896732, "extracted_images": 368, "extraction_seconds": {"D1": 56.189224300002934, "D2": 15.059557599997333, "D3": 87.64429830000563}, "extraction_wall_seconds": 162.5977165000054, "memory_hits": 351865}`.

N is the planned split-local registry size. Searchable clean references count unique clean C1 sources with observed own-score availability or a finite saved own cosine; abstaining reference slots remain planned but unsearchable. Raw descriptor bytes sum the available saved float64 vectors; record metadata, q/h, indexes and container overhead are additional. K summarizes the stored positive-cell candidate_counts, not all registry records or negative queries. Lookup timing covers paired registry and fingerprint identification on already computed scores; the reported mean divides their combined seconds by their combined call count, and excludes cosine extraction and scoring. Extraction/cache metrics are the latest saved invocation snapshot with memory/disk reuse, not a cumulative extraction benchmark or a cold-cache per-image cost. Split snapshots may overlap and must not be summed.

Fresh numeric evidence: [run.json](<W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/20261016-registry-step2-fresh-analysis-r2/run.json>), [calibration-thresholds.json](<W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/20261016-registry-step2-fresh-analysis-r2/calibration-thresholds.json>).

Saved fresh analysis duration: 1157.42 seconds; accounted step-2 duration: 8757.5 seconds. Run duration includes journaled interrupted invocations as well as completed ones. Any separately recorded allowance for unjournaled interruption time is separate budget accounting, not measured extraction or lookup time.

## Fresh regenerate-and-enroll scenario

Status: **completed**. Registry size: 80 planned records. Alpha’s original publications are enrolled first; beta enrolls their seed-12 regenerated copies later, without embedding a new mark. Queries are the exact enrolled copy and its seed-13 further regeneration.

| Cell | Descriptor | Observed/planned | Pointer original owner | Wrong owner | Ambiguous | No attribution | Pointer original record | Fingerprint original record | Fingerprint both owners | Order can favor alpha |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sd15/0.2/exact_copy | D1 | 38/40 | 28 | 0 | 0 | 10 | 28 | 0 | 28 | 28 |
| sd15/0.2/exact_copy | D2 | 38/40 | 0 | 0 | 0 | 38 | 0 | 0 | 0 | 0 |
| sd15/0.2/exact_copy | D3 | 38/40 | 0 | 0 | 0 | 38 | 0 | 0 | 0 | 0 |
| sd15/0.2/further_regeneration | D1 | 38/40 | 20 | 0 | 0 | 18 | 20 | 0 | 21 | 21 |
| sd15/0.2/further_regeneration | D2 | 38/40 | 0 | 0 | 0 | 38 | 0 | 0 | 0 | 0 |
| sd15/0.2/further_regeneration | D3 | 38/40 | 0 | 0 | 0 | 38 | 0 | 0 | 0 | 0 |
| sd15/0.4/exact_copy | D1 | 40/40 | 7 | 0 | 0 | 33 | 7 | 0 | 8 | 8 |
| sd15/0.4/exact_copy | D2 | 40/40 | 0 | 0 | 0 | 40 | 0 | 0 | 0 | 0 |
| sd15/0.4/exact_copy | D3 | 40/40 | 0 | 0 | 0 | 40 | 0 | 0 | 0 | 0 |
| sd15/0.4/further_regeneration | D1 | 40/40 | 2 | 0 | 0 | 38 | 2 | 0 | 2 | 2 |
| sd15/0.4/further_regeneration | D2 | 40/40 | 0 | 0 | 0 | 40 | 0 | 0 | 0 | 0 |
| sd15/0.4/further_regeneration | D3 | 40/40 | 0 | 0 | 0 | 40 | 0 | 0 | 0 | 0 |
| sd21/0.2/exact_copy | D1 | 40/40 | 32 | 0 | 0 | 8 | 32 | 0 | 32 | 32 |
| sd21/0.2/exact_copy | D2 | 40/40 | 0 | 0 | 0 | 40 | 0 | 0 | 0 | 0 |
| sd21/0.2/exact_copy | D3 | 40/40 | 0 | 0 | 0 | 40 | 0 | 0 | 0 | 0 |
| sd21/0.2/further_regeneration | D1 | 40/40 | 22 | 0 | 0 | 18 | 22 | 0 | 24 | 24 |
| sd21/0.2/further_regeneration | D2 | 40/40 | 0 | 0 | 0 | 40 | 0 | 0 | 0 | 0 |
| sd21/0.2/further_regeneration | D3 | 40/40 | 0 | 0 | 0 | 40 | 0 | 0 | 0 | 0 |
| sd21/0.4/exact_copy | D1 | 40/40 | 7 | 0 | 0 | 33 | 7 | 0 | 8 | 8 |
| sd21/0.4/exact_copy | D2 | 40/40 | 0 | 0 | 0 | 40 | 0 | 0 | 0 | 0 |
| sd21/0.4/exact_copy | D3 | 40/40 | 0 | 0 | 0 | 40 | 0 | 0 | 0 | 0 |
| sd21/0.4/further_regeneration | D1 | 40/40 | 1 | 0 | 0 | 39 | 1 | 0 | 2 | 2 |
| sd21/0.4/further_regeneration | D2 | 40/40 | 0 | 0 | 0 | 40 | 0 | 0 | 0 | 0 |
| sd21/0.4/further_regeneration | D3 | 40/40 | 0 | 0 | 0 | 40 | 0 | 0 | 0 | 0 |

Original-owner uniqueness is distinct from selecting the original source record. Fingerprint matches to both owners are not unique owner attribution; preferring the earlier enrollment is an external registry-order rule. The native pointer is evaluated for alpha and beta here, so a zero wrong-owner rate in the alpha-only screen is not substituted for this scenario.

Native calls, all matching record IDs, cosine scores and enrollment-order choices: [rows.jsonl](<W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/20261017-registry-step2-fresh-enroll/rows.jsonl>). This scenario does not test re-embedding/T6 or arbitrary-owner security.

| Cell | Descriptor | Query observed | Query abstaining | Query unknown | Searchable/planned references | Searchable/planned beta references | Reference abstentions | Reference unknown | Beta abstentions | Beta unknown | Unique alpha with searchable own beta | Unique alpha with unsearchable own beta |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sd15/0.2/exact_copy | D1 | 35 | 3 | 2 | 74/80 | 35/40 | 4 | 2 | 3 | 2 | 28 | 0 |
| sd15/0.2/exact_copy | D2 | 38 | 0 | 2 | 78/80 | 38/40 | 0 | 2 | 0 | 2 | 0 | 0 |
| sd15/0.2/exact_copy | D3 | 38 | 0 | 2 | 78/80 | 38/40 | 0 | 2 | 0 | 2 | 0 | 0 |
| sd15/0.2/further_regeneration | D1 | 34 | 4 | 2 | 74/80 | 35/40 | 4 | 2 | 3 | 2 | 20 | 0 |
| sd15/0.2/further_regeneration | D2 | 38 | 0 | 2 | 78/80 | 38/40 | 0 | 2 | 0 | 2 | 0 | 0 |
| sd15/0.2/further_regeneration | D3 | 38 | 0 | 2 | 78/80 | 38/40 | 0 | 2 | 0 | 2 | 0 | 0 |
| sd15/0.4/exact_copy | D1 | 36 | 4 | 0 | 75/80 | 36/40 | 5 | 0 | 4 | 0 | 7 | 0 |
| sd15/0.4/exact_copy | D2 | 40 | 0 | 0 | 80/80 | 40/40 | 0 | 0 | 0 | 0 | 0 | 0 |
| sd15/0.4/exact_copy | D3 | 40 | 0 | 0 | 80/80 | 40/40 | 0 | 0 | 0 | 0 | 0 | 0 |
| sd15/0.4/further_regeneration | D1 | 35 | 5 | 0 | 75/80 | 36/40 | 5 | 0 | 4 | 0 | 2 | 0 |
| sd15/0.4/further_regeneration | D2 | 40 | 0 | 0 | 80/80 | 40/40 | 0 | 0 | 0 | 0 | 0 | 0 |
| sd15/0.4/further_regeneration | D3 | 40 | 0 | 0 | 80/80 | 40/40 | 0 | 0 | 0 | 0 | 0 | 0 |
| sd21/0.2/exact_copy | D1 | 37 | 3 | 0 | 76/80 | 37/40 | 4 | 0 | 3 | 0 | 32 | 0 |
| sd21/0.2/exact_copy | D2 | 40 | 0 | 0 | 80/80 | 40/40 | 0 | 0 | 0 | 0 | 0 | 0 |
| sd21/0.2/exact_copy | D3 | 40 | 0 | 0 | 80/80 | 40/40 | 0 | 0 | 0 | 0 | 0 | 0 |
| sd21/0.2/further_regeneration | D1 | 36 | 4 | 0 | 76/80 | 37/40 | 4 | 0 | 3 | 0 | 22 | 0 |
| sd21/0.2/further_regeneration | D2 | 40 | 0 | 0 | 80/80 | 40/40 | 0 | 0 | 0 | 0 | 0 | 0 |
| sd21/0.2/further_regeneration | D3 | 40 | 0 | 0 | 80/80 | 40/40 | 0 | 0 | 0 | 0 | 0 | 0 |
| sd21/0.4/exact_copy | D1 | 35 | 5 | 0 | 74/80 | 35/40 | 6 | 0 | 5 | 0 | 7 | 0 |
| sd21/0.4/exact_copy | D2 | 40 | 0 | 0 | 80/80 | 40/40 | 0 | 0 | 0 | 0 | 0 | 0 |
| sd21/0.4/exact_copy | D3 | 40 | 0 | 0 | 80/80 | 40/40 | 0 | 0 | 0 | 0 | 0 | 0 |
| sd21/0.4/further_regeneration | D1 | 35 | 5 | 0 | 74/80 | 35/40 | 6 | 0 | 5 | 0 | 1 | 0 |
| sd21/0.4/further_regeneration | D2 | 40 | 0 | 0 | 80/80 | 40/40 | 0 | 0 | 0 | 0 | 0 | 0 |
| sd21/0.4/further_regeneration | D3 | 40 | 0 | 0 | 80/80 | 40/40 | 0 | 0 | 0 | 0 | 0 | 0 |

A planned registry slot can lack a searchable descriptor. Unique alpha attribution with an unsearchable competing beta record is reported separately from uniqueness against a searchable competing record. Verified native weak-detail abstentions are deterministic rejections; genuine missing data remain unknown. Older runs without these availability fields display missing values, not measured zeros.

| Phase | Status | Rows |
| --- | --- | --- |
| enroll | input_unavailable | 2 |
| enroll | ok | 318 |
| evaluate | input_unavailable | 4 |
| evaluate | ok | 316 |

Available descriptor containers per observed query: minimum 78, maximum 80; planned N is not silently substituted for availability. Container availability is not D1 searchability; use the per-descriptor searchable counts above.

## Execution accounting and interruptions

| Component | Saved outcome | Recorded wall seconds | Scientific commit |
| --- | --- | --- | --- |
| Screen | screen_pass_hypothesis | 1317.25 | 764fa0d54dc4d92ff80d2bf3276cf485f8fd506e |
| Screen competing enrollment | completed | 389.156 | 84f16ece2c00d436cb0983962ebe2ec26fe6b72e |
| Fresh construction/grid | completed | 5237.77 | cf5de20abeea171b15439dcdf126f584c5830737 |
| Original failed calibration | incomplete | 415.907 | cf5de20abeea171b15439dcdf126f584c5830737 |
| Amended calibration/evaluation | development_fail_or_incomplete | 1157.42 | fd2566cf288a94ccce612e45065f4f01e46a5fec |
| Fresh competing enrollment | completed | 843.984 | fd2566cf288a94ccce612e45065f4f01e46a5fec |

Recorded component wall time totals 9361.48 seconds. Charged step-2 budget is 9601.48 seconds; the difference is 240 seconds of interruption allowance, not measured compute. The cap is 14400 seconds. These are conservative wall-time charges, not isolated GPU benchmarks; free acquisition time is excluded.

The original calibration failure is retained. Two app restarts interrupted evaluation before completion; their last-journaled durations remain included in the amended run. Historical invocation entries marked running are retained interruption evidence, not live children. Unchanged-code resumes reused saved native calls and lossless descriptor files. The final evaluation and competing-enrollment invocations completed. The first SD1.5 fresh-grid invocation also retained a Windows status-file-lock failure before unchanged-code resume. Download/helper failures and canonical source-release checks remain in the acquisition records and dev-log. No threshold, descriptor, source or rule changed on resume.

## Interpretation and next decision

The completed fresh primary evaluation failed the fixed development gate. The earlier screen pass does not override this failed fresh design, and no held-out confirmatory run is launched. The user decision is whether to close this route and use the bounded negative thesis result, or authorize a new research direction. Descriptor rescue, threshold retuning and a new direction are not automatic continuations of this result. No chapter finalization, submission, publication or human visual verdict is implied.
