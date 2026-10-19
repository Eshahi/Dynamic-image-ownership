# dodis2008fuzzy — V2

Accessed 2026-10-18. Verification denotes primary method and evaluation/proof inspection, not reproduction.

**Metadata.** Yevgeniy Dodis, Rafail Ostrovsky, Leonid Reyzin and Adam Smith. *Fuzzy Extractors: How to Generate Strong Keys from Biometrics and Other Noisy Data*. SIAM Journal on Computing 38(1):97–139 (2008). [Author record](https://www.cs.bu.edu/~reyzin/fuzzy.html), [author manuscript dated 2008-01-20](https://www.cs.bu.edu/~reyzin/papers/fuzzy.pdf); arXiv cs/0602007. DOI left unverified here. Locators: §§3.1–3.2, Lemma 4.3, Theorems 5.1–5.2 and Appendix C.

**Setting/mechanism.** A secure sketch permits recovery from a nearby input while bounding entropy loss. A fuzzy extractor produces a nearly uniform secret despite public helper data, assuming sufficient input min-entropy. Hamming constructions combine error-correcting codes and extraction.

**Evaluation/payload.** Theoretical construction, not an image benchmark. For a binary [n,k,2t+1] code, the displayed extractor output length is m+k−n−2log2(1/epsilon)+2. Correctness is guaranteed within distance t; behavior beyond t has no generic rejection guarantee.

**Limit/relevance.** No theorem establishes that D1/B1 features satisfy the required entropy or separation assumptions. Public images and attacker side information matter. Fuzzy extraction does not by itself distinguish same-shot negatives, authenticate enrollment, or turn a perceptual feature into a copyright proof. It is a possible future construction only after those assumptions are justified.

