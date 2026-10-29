# Interpreting the VINE-B payload screen

Date: 2026-10-29. Explanatory analysis of the frozen Round 2 design, not a new method, threshold or experiment. The calculations below use only exact binomial formulas and standard-library arithmetic. No observed error rate is assumed, fitted or measured. The operational protocol remains [R2 binding design](r2-binding-design.md) and the reviewed Stage S configuration.

## Known-message presence and blind recovery answer different questions

The retained VINE-R test accepts at least 69 matches to a supplied 100-bit message. It can therefore tolerate 31 errors because it tests one known hypothesis. VINE-B instead must recover q without the original message, donor, candidate-source list or registry. Its semantic field has 32 data bits and 36 redundancy bits; it accepts a unique word within four errors in those 68 bits. The last 32 bits carry uncorrected masked h and cannot influence semantic decoding.

Consequently, high historical VINE-R presence does not predict high VINE-B C, Q or J. Nor would low VINE-B recovery establish that the published carrier failed the original known-message task. A very small average raw bit error can still damage full-message equality, and a large average accuracy does not identify which field contains the errors. The frozen raw q/tag/masked-h delivery records are necessary to interpret this difference.

For illustration only, suppose each bit flips independently with the same probability p. Define

```
B(n,k,p) = sum(comb(n,j) * p**j * (1-p)**(n-j), j=0..k).
```

Known-message presence then has probability B(100,31,p). The true semantic codeword lies inside the radius-four search ball with probability B(68,4,p). This is an upper bound on exact q recovery by this decoder under the illustration: another qualifying word causes rejection. It is not a lower bound, and it is not the probability of C or J. Even exact q recovery still needs the suspect's content-consistency predicate to pass. Raw h equality, conditional on the true q being selected, has probability (1-p)^32 under this independent model.

| Assumed independent bit error p | Known-message presence | True q/tag word inside radius 4 | Raw h exact, conditional on true q |
|---:|---:|---:|---:|
| .01 | >.999999 | .999382 | .724980 |
| .03 | >.999999 | .946468 | .377308 |
| .05 | >.999999 | .747124 | .193711 |
| .10 | >.999999 | .177570 | .034337 |
| .15 | .999985 | .018233 | .005513 |
| .20 | .996870 | .001060 | .000792 |
| .30 | .633108 | .000000933 | .0000110 |

These are analytical examples, not predictions for VINE. Correlated errors, unequal bit reliability, image-dependent biases and changes to the suspect descriptors can change every relationship. The examples do not justify changing the radius, threshold, payload or article rule after outputs.

VINE-B is one prospectively specified content-bound instantiation of the published carrier, not a proof of the best achievable coding scheme for its 100-bit output. A gain over this arm supports the stated comparator claim, not architecture-wide superiority over VINE or an information-theoretic capacity limit. Any later coding alternative must be named and frozen before new data; it cannot silently replace this baseline after its outcomes are known.

## What the ideal null bound does and does not say

There are 2^32 possible semantic codewords in 68 bits. Each radius-four ball contains

```
sum(comb(68,j), j=0..4) = 866848
```

points. By a union bound, a uniformly random 68-bit string lies in any ball with probability at most 866848 / 2^36 = 0.000012614298611879349. Overlapping balls only reduce the union volume, and rejecting ambiguity can reduce acceptance further. This bound holds for a fixed codebook under that uniform input law; it does not require independence between the balls. It does not establish that neural outputs on unmarked photographs have that law.

It also does not apply to an adaptive attacker who knows the public-derived profile and can generate a valid word. Neither the owner-conditioned tag nor the h mask authenticates a claimant. Reporting many queries does not create independent negative sources. Even zero events on 16 independent sources has a one-sided 95% binomial upper bound of about .17075; the actual fixed cohort is a development screen, not a representative population sample.

## Reading later outcomes without changing the experiment

| Observed pattern | Permitted interpretation | Unsupported inference |
|---|---|---|
| VINE-R presence high; VINE-B Q low | Known-message testing survived while the frozen blind payload did not; inspect field errors and no-codeword/ambiguity counts | VINE is generally ineffective, or its known-message score equals blind recovery |
| VINE-B Q high; C/J lower | Delivery survived but suspect semantic consistency changed | All losses are carrier failures |
| VINE-B q recovery high; H low | The raw conditional h field or its original reference did not survive | Semantic recovery failed, or h was error-corrected |
| VINE-B D high on a quality-eligible transplant; F false | Donor code arrived but the fixed content rule rejected that recipient | No donor signal was delivered |
| No false accepts with little or no donor Q delivery | End-to-end screen has no observed accept; binding evidence is limited by delivery | The content-consistency rule alone defeated transplantation |
| F6 numeric gates pass; VINE-B evidence missing | F6 numeric status is retained, package/article remain incomplete | The original numerical result vanished, or a partial package is article GO |
| F6 and VINE-B are within both directed practical margins with no strict edge | Numerical parity under the frozen development rule | Statistical equivalence, or novelty of the generic bound-carrier idea |

The original-h reference of VINE-B and retained clean-decoded-h basis of F5/F6 are already disclosed in the design. Primary article retention uses C and J; H/D/F interpretation must retain those reference conventions. Human judgments and fresh confirmation remain separate requirements. These explanations add no winning dimension, arm, compute request or new gate.
