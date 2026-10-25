# LDPC-PRC concrete security — V2 primary-source card

Inspected 2026-10-25. Tianrui Wang, Anyu Wang, Tianshuo Cong, Delong Ran, Jinyuan Liu and Xiaoyun Wang, *Cryptanalysis of LDPC-Based Pseudorandom Error-Correcting Codes*. Final USENIX Security 2026 proceedings version, pp. 4287–4306; PDF includes a proceedings cover (21 PDF pages). No revision identifier is printed. V2 means methods/security analysis and experiments were inspected, not independently verified.

Primary URLs: [official record](https://www.usenix.org/conference/usenixsecurity26/presentation/wang-tianrui), [proceedings PDF](https://www.usenix.org/system/files/usenixsecurity26-wang-tianrui.pdf).

## Compact source paraphrase (under 200 words)

Public-key attacks know (G,z). I recovers partial parity checks; overwhelming distinguishing needs Θ(n) independent vectors (Theorem 1). II searches multiple public keys for implementation-induced weak keys, then samples that key's oracle (Theorem 2; Algorithm 9). Neither requires decoder queries. III recovers encoding noise before structured removal (§4.3).

Config2: n=2^14, g=λ=log2(binomial(n,t)), t=3…7, 512 message bits, target FPR=10^-5 (§5.1.2). Table7 gives I log2-cost 21.88 at t=3 versus 45.14 at t=7; concrete III costs 56.56…49.22. The ~2^22 headline is distinguishing complexity, excluding image inversion (§5), not universal removal timing.

SD2.1-base/50-step DDIM inversion uses 128 keys×16 images (§6.1). Table4 t=3: I/II image TPR 93%/96%, FPR 0%; t=4 II's 100% conditional TPR accompanies only 2.3% weak-key success. Removal: 100 images, t=3, 67%/89%/96% at l∞=8/12/16 over255 (§6.3). AppendixD tests SD1.5/2.0 proxy autoencoders, not SDXL/FLUX.

Defenses: larger n/t with robustness tradeoffs; revised KeyGen; more noise; avoid explicit message decoding (§7). Soundness quantifies fixed content over random keys and is explicitly untargeted (§3.1.1). These concrete/implementation findings do not refute the abstract primitive's conditional asymptotic theorem.

## Original interpretation for this study

Keep three questions separate: accidental acceptance with independently sampled keys; whether an outsider can identify marked outputs; and whether an adversary can create an accepted ownership claim after adapting to one fixed key. None is interchangeable with another. In particular, an outsider's successful distinguisher is not by itself a successful owner forgery. A low accidental FPR cannot supply a bound for repeated adaptive attempts without a separate security argument.

For F5, this is a security-claim caution, not evidence that F5 inherits LDPC weaknesses or that PRC fails the planned T3 regeneration grid. Our encoder-directed image-domain writer has a different mechanism and access model. Conversely, adding a cryptographic code would not establish independent-encoder signal transport. The retained F5 SDXL failure remains an empirical transfer result; this paper does not explain that result causally. Preserve all current baseline and protocol choices. Any later PRC comparator would need its exact code parameters, key disclosure, number of same-key samples, inversion resources and measured regeneration results reported separately.

The paper's structured image perturbation is distinct from the proposed detector-free T3 regeneration attacks. Proxy extraction from SD-family autoencoders does not isolate independently trained encoder transfer. No 128-bit deployment claim should be inferred from a nominal parameter called λ or extrapolated from the paper's finite regime to all possible PRCs.

## Inspection and locator log

- Direct open, no search query: official record URL above; followed its “Wang PDF” link to the exact PDF URL above. No PDF, code, data, model or image was downloaded to the workspace.
- Read Definitions 1/4 and Construction1 (§3, printed pp.4289–4291); public-key/soundness and stronger-robustness distinctions.
- Read §§4.1–4.3/Theorems1–3 (pp.4291–4295), §§5.1–5.3/Table2/Figure4 (pp.4295–4297), §§6.1–6.3/Tables3–4 (pp.4297–4299), and §§7.1–7.3/Algorithm2 (pp.4299–4300).
- Read AppendixC/Tables6–7 and AppendixD–E/Table8 (pp.4304–4306). PDF text was opened around extracted lines 440, 500, 523, 650, 795, 870, 1090, 1170, 1180, 1300, 1320, 1450, 1508, 1534, 1550, 1610, 1630, 1780, 1790, 1810, 1840, 1863, 1880, 1910, 1957, 2310, 2347 and 2531; in-document finds: “22”, “5.1”, “6.2”, “7.1”. Screenshot requests were made for zero-based pages19/13/14; tool returned references only, so conclusions use readable PDF text, not a claimed visual inspection.
- Read existing local `literature/watermarks/09-prc.md` under this dossier. It concerns Gunn–Zhao–Song's image construction; this supplementary card does not replace that source or import its results as independent evidence.
- No operational attack code, experiment, benchmark, package installation or protocol amendment was produced.
