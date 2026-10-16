# Unseen-regenerator development results

Run status: **completed**. Frozen method choice: **f5-r2**. SD2.1-base at strength .2 gives E3-S1 24/24 and F5 r2 24/24; E3 minus F5 = 0 sources, against the fixed threshold of 3.

This is exploratory evidence on 24 development sources. Clean quality is unmatched across methods. No held-out execution or human visual admissibility judgment is supplied. These are image-domain comparators, not a demonstrated proposal latent method.

Retain E3 only at fixed-denominator E3-minus-F5 >= 3/24; otherwise choose F5. Completed safety-policy blocks are non-successes. Genuine missing/error execution leaves the method choice unresolved.

Primary source majority and paired tests use all 24 attempted sources: at least two observed True seeds pass; unavailable/safety-blocked/missing positive slots are non-successes. This does not assert observed detector rejection. Seed availability and optimistic source bounds remain supplemental; negative calls retain unresolved status.

A nonsignificant paired sign test does not establish equality or equivalence. No formal equivalence test or margin was preregistered.

## Clean construction and quality

| Method | Observed | Strict quality | Minimum PSNR dB | Minimum SSIM | Median LPIPS | Maximum LPIPS | Median embedding s |
| --- | --- | --- | --- | --- | --- | --- | --- |
| e3-s1 | 24/24 | 24/24 | 39.6952 | 0.955932 | 0.0392575 | 0.0926664 | 130.133 |
| f5-r2 | 24/24 | 24/24 | 42.1568 | 0.977085 | 0.0144277 | 0.0638407 | 52.4685 |
| v5-r3 | 24/24 | 24/24 | 35.193 | 0.962602 | 0.0159371 | 0.0497669 | 2.578 |

Strict quality means PSNR >35 dB, SSIM >.9 and LPIPS <.1. Embedding times retain each source’s recorded construction basis; retained E3/F5 times are not fresh timing reruns.

## Seed endpoints

Entries are successes/planned calls followed by unavailable calls. Planned denominator is 72 per cell. Frozen predicates: S = semantic found and content match; C = semantic read and content match; Q = read q exactly equals the target; J = Q and semantic content match; H = read h exactly equals the target; F = both_match; A = either tier found.

| Cell | Method | S | C | Q | J | H | F | A |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sd15/0.1 | e3-s1 | 70/72; unresolved 2 | 70/72; unresolved 2 | 70/72; unresolved 2 | 70/72; unresolved 2 | 0/72; unresolved 2 | 0/72; unresolved 2 | 70/72; unresolved 2 |
| sd15/0.1 | f5-r2 | 72/72; unresolved 0 | 72/72; unresolved 0 | 41/72; unresolved 0 | 41/72; unresolved 0 | 0/72; unresolved 0 | 0/72; unresolved 0 | 72/72; unresolved 0 |
| sd15/0.1 | v5-r3 | 68/72; unresolved 0 | 49/72; unresolved 0 | 15/72; unresolved 0 | 15/72; unresolved 0 | 0/72; unresolved 0 | 0/72; unresolved 0 | 71/72; unresolved 0 |
| sd15/0.2 | e3-s1 | 70/72; unresolved 2 | 70/72; unresolved 2 | 70/72; unresolved 2 | 70/72; unresolved 2 | 0/72; unresolved 2 | 0/72; unresolved 2 | 70/72; unresolved 2 |
| sd15/0.2 | f5-r2 | 69/72; unresolved 2 | 66/72; unresolved 2 | 32/72; unresolved 2 | 31/72; unresolved 2 | 0/72; unresolved 2 | 0/72; unresolved 2 | 70/72; unresolved 2 |
| sd15/0.2 | v5-r3 | 43/72; unresolved 1 | 17/72; unresolved 1 | 0/72; unresolved 1 | 0/72; unresolved 1 | 0/72; unresolved 1 | 0/72; unresolved 1 | 47/72; unresolved 1 |
| sd15/0.4 | e3-s1 | 59/72; unresolved 0 | 59/72; unresolved 0 | 71/72; unresolved 0 | 59/72; unresolved 0 | 0/72; unresolved 0 | 0/72; unresolved 0 | 71/72; unresolved 0 |
| sd15/0.4 | f5-r2 | 51/72; unresolved 1 | 37/72; unresolved 1 | 14/72; unresolved 1 | 11/72; unresolved 1 | 0/72; unresolved 1 | 0/72; unresolved 1 | 62/72; unresolved 1 |
| sd15/0.4 | v5-r3 | 3/72; unresolved 1 | 0/72; unresolved 1 | 0/72; unresolved 1 | 0/72; unresolved 1 | 0/72; unresolved 1 | 0/72; unresolved 1 | 3/72; unresolved 1 |
| sd21/0.1 | e3-s1 | 72/72; unresolved 0 | 72/72; unresolved 0 | 72/72; unresolved 0 | 72/72; unresolved 0 | 0/72; unresolved 0 | 0/72; unresolved 0 | 72/72; unresolved 0 |
| sd21/0.1 | f5-r2 | 72/72; unresolved 0 | 72/72; unresolved 0 | 41/72; unresolved 0 | 41/72; unresolved 0 | 0/72; unresolved 0 | 0/72; unresolved 0 | 72/72; unresolved 0 |
| sd21/0.1 | v5-r3 | 69/72; unresolved 0 | 53/72; unresolved 0 | 20/72; unresolved 0 | 20/72; unresolved 0 | 0/72; unresolved 0 | 0/72; unresolved 0 | 71/72; unresolved 0 |
| sd21/0.2 | e3-s1 | 71/72; unresolved 0 | 71/72; unresolved 0 | 72/72; unresolved 0 | 71/72; unresolved 0 | 0/72; unresolved 0 | 0/72; unresolved 0 | 72/72; unresolved 0 |
| sd21/0.2 | f5-r2 | 71/72; unresolved 0 | 70/72; unresolved 0 | 37/72; unresolved 0 | 37/72; unresolved 0 | 0/72; unresolved 0 | 0/72; unresolved 0 | 72/72; unresolved 0 |
| sd21/0.2 | v5-r3 | 43/72; unresolved 0 | 17/72; unresolved 0 | 1/72; unresolved 0 | 1/72; unresolved 0 | 0/72; unresolved 0 | 0/72; unresolved 0 | 48/72; unresolved 0 |
| sd21/0.4 | e3-s1 | 60/72; unresolved 0 | 59/72; unresolved 0 | 69/72; unresolved 0 | 59/72; unresolved 0 | 0/72; unresolved 0 | 0/72; unresolved 0 | 70/72; unresolved 0 |
| sd21/0.4 | f5-r2 | 51/72; unresolved 0 | 37/72; unresolved 0 | 12/72; unresolved 0 | 11/72; unresolved 0 | 0/72; unresolved 0 | 0/72; unresolved 0 | 62/72; unresolved 0 |
| sd21/0.4 | v5-r3 | 3/72; unresolved 0 | 0/72; unresolved 0 | 0/72; unresolved 0 | 0/72; unresolved 0 | 0/72; unresolved 0 | 0/72; unresolved 0 | 3/72; unresolved 0 |

## Source-majority endpoints

Success requires at least two observed True seeds; unavailable slots do not contribute successes. Every main endpoint uses all 24 sources.

| Cell | Method | S | C | Q | J | H | F | A |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sd15/0.1 | e3-s1 | 23/24 | 23/24 | 23/24 | 23/24 | 0/24 | 0/24 | 23/24 |
| sd15/0.1 | f5-r2 | 24/24 | 24/24 | 13/24 | 13/24 | 0/24 | 0/24 | 24/24 |
| sd15/0.1 | v5-r3 | 23/24 | 16/24 | 4/24 | 4/24 | 0/24 | 0/24 | 24/24 |
| sd15/0.2 | e3-s1 | 23/24 | 23/24 | 23/24 | 23/24 | 0/24 | 0/24 | 23/24 |
| sd15/0.2 | f5-r2 | 23/24 | 22/24 | 10/24 | 9/24 | 0/24 | 0/24 | 24/24 |
| sd15/0.2 | v5-r3 | 14/24 | 5/24 | 0/24 | 0/24 | 0/24 | 0/24 | 15/24 |
| sd15/0.4 | e3-s1 | 19/24 | 19/24 | 24/24 | 19/24 | 0/24 | 0/24 | 24/24 |
| sd15/0.4 | f5-r2 | 17/24 | 12/24 | 5/24 | 4/24 | 0/24 | 0/24 | 21/24 |
| sd15/0.4 | v5-r3 | 1/24 | 0/24 | 0/24 | 0/24 | 0/24 | 0/24 | 1/24 |
| sd21/0.1 | e3-s1 | 24/24 | 24/24 | 24/24 | 24/24 | 0/24 | 0/24 | 24/24 |
| sd21/0.1 | f5-r2 | 24/24 | 24/24 | 13/24 | 13/24 | 0/24 | 0/24 | 24/24 |
| sd21/0.1 | v5-r3 | 24/24 | 19/24 | 7/24 | 7/24 | 0/24 | 0/24 | 24/24 |
| sd21/0.2 | e3-s1 | 24/24 | 24/24 | 24/24 | 24/24 | 0/24 | 0/24 | 24/24 |
| sd21/0.2 | f5-r2 | 24/24 | 24/24 | 12/24 | 12/24 | 0/24 | 0/24 | 24/24 |
| sd21/0.2 | v5-r3 | 15/24 | 5/24 | 0/24 | 0/24 | 0/24 | 0/24 | 17/24 |
| sd21/0.4 | e3-s1 | 22/24 | 22/24 | 24/24 | 22/24 | 0/24 | 0/24 | 24/24 |
| sd21/0.4 | f5-r2 | 18/24 | 12/24 | 4/24 | 4/24 | 0/24 | 0/24 | 22/24 |
| sd21/0.4 | v5-r3 | 0/24 | 0/24 | 0/24 | 0/24 | 0/24 | 0/24 | 0/24 |

## Supplemental unavailable-seed bounds

These tri-state summaries preserve unresolved seed majorities. They do not replace the fixed-denominator primary counts.

| Cell | Method | S | C | Q | J | H | F | A |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sd15/0.1 | e3-s1 | 23/24; unresolved 1 | 23/24; unresolved 1 | 23/24; unresolved 1 | 23/24; unresolved 1 | 0/24; unresolved 1 | 0/24; unresolved 1 | 23/24; unresolved 1 |
| sd15/0.1 | f5-r2 | 24/24; unresolved 0 | 24/24; unresolved 0 | 13/24; unresolved 0 | 13/24; unresolved 0 | 0/24; unresolved 0 | 0/24; unresolved 0 | 24/24; unresolved 0 |
| sd15/0.1 | v5-r3 | 23/24; unresolved 0 | 16/24; unresolved 0 | 4/24; unresolved 0 | 4/24; unresolved 0 | 0/24; unresolved 0 | 0/24; unresolved 0 | 24/24; unresolved 0 |
| sd15/0.2 | e3-s1 | 23/24; unresolved 1 | 23/24; unresolved 1 | 23/24; unresolved 1 | 23/24; unresolved 1 | 0/24; unresolved 1 | 0/24; unresolved 1 | 23/24; unresolved 1 |
| sd15/0.2 | f5-r2 | 23/24; unresolved 1 | 22/24; unresolved 1 | 10/24; unresolved 0 | 9/24; unresolved 1 | 0/24; unresolved 0 | 0/24; unresolved 0 | 24/24; unresolved 0 |
| sd15/0.2 | v5-r3 | 14/24; unresolved 0 | 5/24; unresolved 1 | 0/24; unresolved 0 | 0/24; unresolved 0 | 0/24; unresolved 0 | 0/24; unresolved 0 | 15/24; unresolved 0 |
| sd15/0.4 | e3-s1 | 19/24; unresolved 0 | 19/24; unresolved 0 | 24/24; unresolved 0 | 19/24; unresolved 0 | 0/24; unresolved 0 | 0/24; unresolved 0 | 24/24; unresolved 0 |
| sd15/0.4 | f5-r2 | 17/24; unresolved 0 | 12/24; unresolved 0 | 5/24; unresolved 1 | 4/24; unresolved 0 | 0/24; unresolved 0 | 0/24; unresolved 0 | 21/24; unresolved 0 |
| sd15/0.4 | v5-r3 | 1/24; unresolved 0 | 0/24; unresolved 0 | 0/24; unresolved 0 | 0/24; unresolved 0 | 0/24; unresolved 0 | 0/24; unresolved 0 | 1/24; unresolved 0 |
| sd21/0.1 | e3-s1 | 24/24; unresolved 0 | 24/24; unresolved 0 | 24/24; unresolved 0 | 24/24; unresolved 0 | 0/24; unresolved 0 | 0/24; unresolved 0 | 24/24; unresolved 0 |
| sd21/0.1 | f5-r2 | 24/24; unresolved 0 | 24/24; unresolved 0 | 13/24; unresolved 0 | 13/24; unresolved 0 | 0/24; unresolved 0 | 0/24; unresolved 0 | 24/24; unresolved 0 |
| sd21/0.1 | v5-r3 | 24/24; unresolved 0 | 19/24; unresolved 0 | 7/24; unresolved 0 | 7/24; unresolved 0 | 0/24; unresolved 0 | 0/24; unresolved 0 | 24/24; unresolved 0 |
| sd21/0.2 | e3-s1 | 24/24; unresolved 0 | 24/24; unresolved 0 | 24/24; unresolved 0 | 24/24; unresolved 0 | 0/24; unresolved 0 | 0/24; unresolved 0 | 24/24; unresolved 0 |
| sd21/0.2 | f5-r2 | 24/24; unresolved 0 | 24/24; unresolved 0 | 12/24; unresolved 0 | 12/24; unresolved 0 | 0/24; unresolved 0 | 0/24; unresolved 0 | 24/24; unresolved 0 |
| sd21/0.2 | v5-r3 | 15/24; unresolved 0 | 5/24; unresolved 0 | 0/24; unresolved 0 | 0/24; unresolved 0 | 0/24; unresolved 0 | 0/24; unresolved 0 | 17/24; unresolved 0 |
| sd21/0.4 | e3-s1 | 22/24; unresolved 0 | 22/24; unresolved 0 | 24/24; unresolved 0 | 22/24; unresolved 0 | 0/24; unresolved 0 | 0/24; unresolved 0 | 24/24; unresolved 0 |
| sd21/0.4 | f5-r2 | 18/24; unresolved 0 | 12/24; unresolved 0 | 4/24; unresolved 0 | 4/24; unresolved 0 | 0/24; unresolved 0 | 0/24; unresolved 0 | 22/24; unresolved 0 |
| sd21/0.4 | v5-r3 | 0/24; unresolved 0 | 0/24; unresolved 0 | 0/24; unresolved 0 | 0/24; unresolved 0 | 0/24; unresolved 0 | 0/24; unresolved 0 | 0/24; unresolved 0 |

## Paired checked-semantic C tests

| Cell and comparison | Left successes | Right successes | Left only | Right only | Difference pp | One-sided exact p | Holm p (18 tests) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| sd15/0.1/e3-s1:f5-r2 | 23/24 | 24/24 | 0 | 1 | -4.16667 | 1 | 1 |
| sd15/0.1/e3-s1:v5-r3 | 23/24 | 16/24 | 8 | 1 | 29.1667 | 0.0195312 | 0.15625 |
| sd15/0.1/f5-r2:v5-r3 | 24/24 | 16/24 | 8 | 0 | 33.3333 | 0.00390625 | 0.0351562 |
| sd15/0.2/e3-s1:f5-r2 | 23/24 | 22/24 | 1 | 0 | 4.16667 | 0.5 | 1 |
| sd15/0.2/e3-s1:v5-r3 | 23/24 | 5/24 | 18 | 0 | 75 | 3.8147e-06 | 5.34058e-05 |
| sd15/0.2/f5-r2:v5-r3 | 22/24 | 5/24 | 17 | 0 | 70.8333 | 7.62939e-06 | 9.91821e-05 |
| sd15/0.4/e3-s1:f5-r2 | 19/24 | 12/24 | 8 | 1 | 29.1667 | 0.0195312 | 0.15625 |
| sd15/0.4/e3-s1:v5-r3 | 19/24 | 0/24 | 19 | 0 | 79.1667 | 1.90735e-06 | 3.24249e-05 |
| sd15/0.4/f5-r2:v5-r3 | 12/24 | 0/24 | 12 | 0 | 50 | 0.000244141 | 0.00292969 |
| sd21/0.1/e3-s1:f5-r2 | 24/24 | 24/24 | 0 | 0 | 0 | 1 | 1 |
| sd21/0.1/e3-s1:v5-r3 | 24/24 | 19/24 | 5 | 0 | 20.8333 | 0.03125 | 0.1875 |
| sd21/0.1/f5-r2:v5-r3 | 24/24 | 19/24 | 5 | 0 | 20.8333 | 0.03125 | 0.1875 |
| sd21/0.2/e3-s1:f5-r2 | 24/24 | 24/24 | 0 | 0 | 0 | 1 | 1 |
| sd21/0.2/e3-s1:v5-r3 | 24/24 | 5/24 | 19 | 0 | 79.1667 | 1.90735e-06 | 3.24249e-05 |
| sd21/0.2/f5-r2:v5-r3 | 24/24 | 5/24 | 19 | 0 | 79.1667 | 1.90735e-06 | 3.24249e-05 |
| sd21/0.4/e3-s1:f5-r2 | 22/24 | 12/24 | 10 | 0 | 41.6667 | 0.000976562 | 0.00976562 |
| sd21/0.4/e3-s1:v5-r3 | 22/24 | 0/24 | 22 | 0 | 91.6667 | 2.38419e-07 | 4.29153e-06 |
| sd21/0.4/f5-r2:v5-r3 | 12/24 | 0/24 | 12 | 0 | 50 | 0.000244141 | 0.00292969 |

The test direction is left > right. A nonsignificant result does not establish equality or equivalence.

## Transfer drop: SD1.5 minus SD2.1 source-majority C

| Strength and method | Sources | Rate | Supplemental unknown bounds |
| --- | --- | --- | --- |
| 0.1/e3-s1 | -1 | -0.0416667 | [-1, 0] |
| 0.1/f5-r2 | 0 | 0 | [0, 0] |
| 0.1/v5-r3 | -3 | -0.125 | [-3, -3] |
| 0.2/e3-s1 | -1 | -0.0416667 | [-1, 0] |
| 0.2/f5-r2 | -2 | -0.0833333 | [-2, -1] |
| 0.2/v5-r3 | 0 | 0 | [0, 1] |
| 0.4/e3-s1 | -3 | -0.125 | [-3, -3] |
| 0.4/f5-r2 | 0 | 0 | [0, 0] |
| 0.4/v5-r3 | 0 | 0 | [0, 0] |

## Negative controls clustered by source

A cluster is adverse if any observed A call accepts. Unavailable negatives remain unresolved; conservative bounds include them as potentially adverse.

| Cell | Method | Panel | Adverse sources | Complete sources | Unavailable sources | Rate bounds | Conservative 95% upper |
| --- | --- | --- | --- | --- | --- | --- | --- |
| sd15/0.1 | e3-s1 | c0_A_clustered | 0/24 | 23 | 1 | [0.0, 0.041666666666666664] | 0.182892 |
| sd15/0.1 | e3-s1 | wrong_owner_A_clustered | 0/24 | 23 | 1 | [0.0, 0.041666666666666664] | 0.182892 |
| sd15/0.1 | f5-r2 | c0_A_clustered | 0/24 | 23 | 1 | [0.0, 0.041666666666666664] | 0.182892 |
| sd15/0.1 | f5-r2 | wrong_owner_A_clustered | 0/24 | 24 | 0 | [0.0, 0.0] | 0.117346 |
| sd15/0.1 | v5-r3 | c0_A_clustered | 0/24 | 23 | 1 | [0.0, 0.041666666666666664] | 0.182892 |
| sd15/0.1 | v5-r3 | wrong_owner_A_clustered | 0/24 | 24 | 0 | [0.0, 0.0] | 0.117346 |
| sd15/0.2 | e3-s1 | c0_A_clustered | 0/24 | 22 | 2 | [0.0, 0.08333333333333333] | 0.239801 |
| sd15/0.2 | e3-s1 | wrong_owner_A_clustered | 0/24 | 23 | 1 | [0.0, 0.041666666666666664] | 0.182892 |
| sd15/0.2 | f5-r2 | c0_A_clustered | 0/24 | 22 | 2 | [0.0, 0.08333333333333333] | 0.239801 |
| sd15/0.2 | f5-r2 | wrong_owner_A_clustered | 0/24 | 22 | 2 | [0.0, 0.08333333333333333] | 0.239801 |
| sd15/0.2 | v5-r3 | c0_A_clustered | 0/24 | 22 | 2 | [0.0, 0.08333333333333333] | 0.239801 |
| sd15/0.2 | v5-r3 | wrong_owner_A_clustered | 0/24 | 23 | 1 | [0.0, 0.041666666666666664] | 0.182892 |
| sd15/0.4 | e3-s1 | c0_A_clustered | 0/24 | 23 | 1 | [0.0, 0.041666666666666664] | 0.182892 |
| sd15/0.4 | e3-s1 | wrong_owner_A_clustered | 0/24 | 24 | 0 | [0.0, 0.0] | 0.117346 |
| sd15/0.4 | f5-r2 | c0_A_clustered | 0/24 | 23 | 1 | [0.0, 0.041666666666666664] | 0.182892 |
| sd15/0.4 | f5-r2 | wrong_owner_A_clustered | 0/24 | 23 | 1 | [0.0, 0.041666666666666664] | 0.182892 |
| sd15/0.4 | v5-r3 | c0_A_clustered | 0/24 | 23 | 1 | [0.0, 0.041666666666666664] | 0.182892 |
| sd15/0.4 | v5-r3 | wrong_owner_A_clustered | 0/24 | 23 | 1 | [0.0, 0.041666666666666664] | 0.182892 |
| sd21/0.1 | e3-s1 | c0_A_clustered | 0/24 | 24 | 0 | [0.0, 0.0] | 0.117346 |
| sd21/0.1 | e3-s1 | wrong_owner_A_clustered | 0/24 | 24 | 0 | [0.0, 0.0] | 0.117346 |
| sd21/0.1 | f5-r2 | c0_A_clustered | 0/24 | 24 | 0 | [0.0, 0.0] | 0.117346 |
| sd21/0.1 | f5-r2 | wrong_owner_A_clustered | 0/24 | 24 | 0 | [0.0, 0.0] | 0.117346 |
| sd21/0.1 | v5-r3 | c0_A_clustered | 0/24 | 24 | 0 | [0.0, 0.0] | 0.117346 |
| sd21/0.1 | v5-r3 | wrong_owner_A_clustered | 0/24 | 24 | 0 | [0.0, 0.0] | 0.117346 |
| sd21/0.2 | e3-s1 | c0_A_clustered | 0/24 | 24 | 0 | [0.0, 0.0] | 0.117346 |
| sd21/0.2 | e3-s1 | wrong_owner_A_clustered | 0/24 | 24 | 0 | [0.0, 0.0] | 0.117346 |
| sd21/0.2 | f5-r2 | c0_A_clustered | 0/24 | 24 | 0 | [0.0, 0.0] | 0.117346 |
| sd21/0.2 | f5-r2 | wrong_owner_A_clustered | 0/24 | 24 | 0 | [0.0, 0.0] | 0.117346 |
| sd21/0.2 | v5-r3 | c0_A_clustered | 0/24 | 24 | 0 | [0.0, 0.0] | 0.117346 |
| sd21/0.2 | v5-r3 | wrong_owner_A_clustered | 0/24 | 24 | 0 | [0.0, 0.0] | 0.117346 |
| sd21/0.4 | e3-s1 | c0_A_clustered | 0/24 | 24 | 0 | [0.0, 0.0] | 0.117346 |
| sd21/0.4 | e3-s1 | wrong_owner_A_clustered | 0/24 | 24 | 0 | [0.0, 0.0] | 0.117346 |
| sd21/0.4 | f5-r2 | c0_A_clustered | 0/24 | 24 | 0 | [0.0, 0.0] | 0.117346 |
| sd21/0.4 | f5-r2 | wrong_owner_A_clustered | 0/24 | 24 | 0 | [0.0, 0.0] | 0.117346 |
| sd21/0.4 | v5-r3 | c0_A_clustered | 0/24 | 24 | 0 | [0.0, 0.0] | 0.117346 |
| sd21/0.4 | v5-r3 | wrong_owner_A_clustered | 0/24 | 24 | 0 | [0.0, 0.0] | 0.117346 |

## Safety policy, execution inventory and VAE comparison

| Phase | Arm or method | Latest status | Rows |
| --- | --- | --- | --- |
| prepare | e3-s1 | ok | 48 |
| prepare | f5-r2 | ok | 48 |
| prepare | v5-r3 | ok | 48 |
| sd15 | C0 | ok | 212 |
| sd15 | C0 | safety_blocked | 4 |
| sd15 | e3-s1 | ok | 212 |
| sd15 | e3-s1 | safety_blocked | 4 |
| sd15 | f5-r2 | ok | 213 |
| sd15 | f5-r2 | safety_blocked | 3 |
| sd15 | v5-r3 | ok | 214 |
| sd15 | v5-r3 | safety_blocked | 2 |
| sd21 | C0 | ok | 216 |
| sd21 | e3-s1 | ok | 216 |
| sd21 | f5-r2 | ok | 216 |
| sd21 | v5-r3 | ok | 216 |

SD2.1 VAE comparison: `{"equal_after_cast_to_regenerator_dtype": false, "meaning": "full state comparison at fp16 precision; equality can expose shared weights, inequality does not prove unrelated ancestry"}`.

Regenerator configuration and safety-checker presence: `{"sd15": {"assets": "W:\\Prrojects\\image ownership\\THESIS_GUIDE_OFFLINE_v5\\.thesis-build\\assets\\a6\\sd15-fp16", "safety_checker": true, "scheduler": {"_use_default_values": ["sample_max_value", "dynamic_thresholding_ratio", "clip_sample_range"], "beta_end": 0.012, "beta_schedule": "scaled_linear", "beta_start": 0.00085, "clip_sample": false, "clip_sample_range": 1.0, "dynamic_thresholding_ratio": 0.995, "num_train_timesteps": 1000, "prediction_type": "epsilon", "rescale_betas_zero_snr": false, "sample_max_value": 1.0, "set_alpha_to_one": false, "steps_offset": 1, "thresholding": false, "timestep_spacing": "leading", "trained_betas": null}}, "sd21": {"assets": "W:\\Prrojects\\image ownership\\THESIS_GUIDE_OFFLINE_v5\\.thesis-build\\assets\\registry-sd21-4e63672c", "safety_checker": false, "scheduler": {"_class_name": "DDIMScheduler", "_diffusers_version": "0.10.0.dev0", "_use_default_values": ["timestep_spacing", "rescale_betas_zero_snr", "clip_sample_range", "sample_max_value", "thresholding", "dynamic_thresholding_ratio"], "beta_end": 0.012, "beta_schedule": "scaled_linear", "beta_start": 0.00085, "clip_sample": false, "clip_sample_range": 1.0, "dynamic_thresholding_ratio": 0.995, "num_train_timesteps": 1000, "prediction_type": "epsilon", "rescale_betas_zero_snr": false, "sample_max_value": 1.0, "set_alpha_to_one": false, "skip_prk_steps": true, "steps_offset": 1, "thresholding": false, "timestep_spacing": "leading", "trained_betas": null}}}`. SD1.5 retains its frozen safety checker; SD2.1 has none. Missing or blocked outputs are not silently rerun without safety checks.

SDXL full generation was omitted prospectively in unseen-regenerator-protocol.md because safe fit was not established on the shared 12 GB desktop GPU. This is a conservative feasibility decision, not a measured out-of-memory result. The SDXL VAE control remains in step 2. No absent SDXL arm is represented as a measured result.

## Limits and numeric evidence

F5 h uses operational bootstrap decoded h, E3 uses its supplied h, v5 uses native intended h; these exact-H targets differ.

The detector uses the claimed owner, public profile and pinned VAE/CLIP models, without an enrolled reference image in this step. The .2 transfer comparison is development evidence; it does not establish generalization to every regenerator. Source selection, safety policy and unmatched quality constrain interpretation.

Numeric sources: [run.json](<W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/20261016-registry-step1-transfer/run.json>), [summary.json](<W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/20261016-registry-step1-transfer/summary.json>), [rows.jsonl](<W:/Prrojects/image ownership/THESIS_GUIDE_OFFLINE_v5/.thesis-build/dev-runs/20261016-registry-step1-transfer/rows.jsonl>).

Commit: `a7443c8e1a79e91432170362086036da67433c47`. Duration: 3251.02 seconds. Incomplete primary choice executions: `[]`.
